from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from nutrisense_agents.ai_companion.agents.macronutrient_agent import get_macronutrient_extraction_chain, process_multiple_ingredients
from nutrisense_agents.ai_companion.schemas.macronutrient_schema import MacronutrientExtraction, FoodDiaryEntry, FoodPhotoAnalysis
from nutrisense_agents.db.supabase.client import get_supabase_client

# Inicializar la cadena de procesamiento
extraction_chain = get_macronutrient_extraction_chain()

def extract_macronutrients_service(
    ingredients: List[str],
    user_id: str,
    meal_type: str = "unknown",
    preparation_method: str = "unknown",
    portion_size: str = "porción estándar",
    photo_url: Optional[str] = None,
    additional_notes: str = ""
) -> Dict[str, Any]:
    """
    Servicio principal para extraer macronutrientes de ingredientes y guardar en la base de datos.
    
    Args:
        ingredients: Lista de ingredientes verificados por el usuario
        user_id: ID del usuario
        meal_type: Tipo de comida (desayuno, almuerzo, cena, snack)
        preparation_method: Método de preparación
        portion_size: Tamaño de la porción
        photo_url: URL de la foto analizada (opcional)
        additional_notes: Notas adicionales
        
    Returns:
        Dict con los resultados del procesamiento y IDs de los registros creados
    """
    
    try:
        # 1. Procesar ingredientes y extraer macronutrientes
        macronutrient_extractions = []
        
        for ingredient in ingredients:
            extraction_result = extraction_chain.invoke({
                "ingredients": [ingredient],
                "meal_type": meal_type,
                "preparation_method": preparation_method,
                "portion_size": portion_size,
                "additional_notes": additional_notes
            })
            macronutrient_extractions.append(extraction_result)
        
        # 2. Calcular totales de la comida
        total_calories = sum(extraction.total_calories for extraction in macronutrient_extractions)
        total_protein = sum(extraction.total_protein for extraction in macronutrient_extractions)
        total_carbs = sum(extraction.total_carbs for extraction in macronutrient_extractions)
        total_fat = sum(extraction.total_fat for extraction in macronutrient_extractions)
        total_fiber = sum(extraction.total_fiber or 0 for extraction in macronutrient_extractions)
        total_sugar = sum(extraction.total_sugar or 0 for extraction in macronutrient_extractions)
        total_sodium = sum(extraction.total_sodium or 0 for extraction in macronutrient_extractions)
        
        # 3. Conectar a Supabase
        supabase = get_supabase_client()
        
        # 4. Insertar ingredientes en la tabla ingredients
        ingredient_ids = []
        for extraction in macronutrient_extractions:
            ingredient_data = {
                "name": extraction.name,
                "description": extraction.description,
                "brand": extraction.brand,
                "calories_per_100g": extraction.calories_per_100g,
                "protein_per_100g": extraction.protein_per_100g,
                "carbs_per_100g": extraction.carbs_per_100g,
                "fat_per_100g": extraction.fat_per_100g,
                "fiber_per_100g": extraction.fiber_per_100g,
                "sugar_per_100g": extraction.sugar_per_100g,
                "sodium_per_100g": extraction.sodium_per_100g,
                "category": extraction.category,
                "preparation_method": extraction.preparation_method,
                "confidence_score": extraction.confidence_score,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Verificar si el ingrediente ya existe
            existing_ingredient = supabase.table("ingredients").select("id").eq("name", extraction.name).execute()
            
            if existing_ingredient.data:
                ingredient_id = existing_ingredient.data[0]["id"]
            else:
                ingredient_result = supabase.table("ingredients").insert(ingredient_data).execute()
                ingredient_id = ingredient_result.data[0]["id"]
            
            ingredient_ids.append(ingredient_id)
        
        # 5. Insertar entrada en food_diary
        food_diary_entry = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "meal_type": meal_type,
            "consumed_at": datetime.utcnow().isoformat(),
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat,
            "total_fiber": total_fiber if total_fiber > 0 else None,
            "total_sugar": total_sugar if total_sugar > 0 else None,
            "total_sodium": total_sodium if total_sodium > 0 else None,
            "notes": additional_notes if additional_notes else None,
            "created_at": datetime.utcnow().isoformat()
        }
        
        food_diary_result = supabase.table("food_diary").insert(food_diary_entry).execute()
        food_diary_id = food_diary_result.data[0]["id"]
        
        # 6. Insertar relaciones food_diary_ingredients
        for i, ingredient_id in enumerate(ingredient_ids):
            relation_data = {
                "food_diary_id": food_diary_id,
                "ingredient_id": ingredient_id,
                "quantity_grams": macronutrient_extractions[i].estimated_quantity_grams,
                "calories_consumed": macronutrient_extractions[i].total_calories,
                "protein_consumed": macronutrient_extractions[i].total_protein,
                "carbs_consumed": macronutrient_extractions[i].total_carbs,
                "fat_consumed": macronutrient_extractions[i].total_fat,
                "created_at": datetime.utcnow().isoformat()
            }
            
            supabase.table("food_diary_ingredients").insert(relation_data).execute()
        
        # 7. Si hay foto, insertar en food_photo_analysis
        photo_analysis_id = None
        if photo_url:
            detected_foods = [extraction.name for extraction in macronutrient_extractions]
            avg_confidence = sum(extraction.confidence_score for extraction in macronutrient_extractions) / len(macronutrient_extractions)
            
            photo_analysis_data = {
                "id": str(uuid.uuid4()),
                "food_diary_id": food_diary_id,
                "photo_url": photo_url,
                "analysis_confidence": avg_confidence,
                "detected_foods": detected_foods,
                "analysis_notes": f"Análisis automático de {len(detected_foods)} ingredientes",
                "created_at": datetime.utcnow().isoformat()
            }
            
            photo_analysis_result = supabase.table("food_photo_analysis").insert(photo_analysis_data).execute()
            photo_analysis_id = photo_analysis_result.data[0]["id"]
        
        # 8. Retornar resultado exitoso
        return {
            "success": True,
            "food_diary_id": food_diary_id,
            "photo_analysis_id": photo_analysis_id,
            "ingredient_ids": ingredient_ids,
            "extracted_macronutrients": [extraction.dict() for extraction in macronutrient_extractions],
            "total_nutrition": {
                "calories": total_calories,
                "protein": total_protein,
                "carbs": total_carbs,
                "fat": total_fat,
                "fiber": total_fiber,
                "sugar": total_sugar,
                "sodium": total_sodium
            },
            "message": f"Se procesaron exitosamente {len(ingredients)} ingredientes"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al procesar los macronutrientes"
        }


# Función de prueba LOCAL (sin Supabase)
def extract_macronutrients_local_test(
    ingredients: List[str],
    user_id: str = "test_user",
    meal_type: str = "almuerzo",
    preparation_method: str = "mixto",
    portion_size: str = "porción estándar",
    additional_notes: str = ""
) -> Dict[str, Any]:
    """
    Versión local del servicio para pruebas sin conexión a Supabase.
    Solo ejecuta la extracción de IA sin guardar en base de datos.
    """
    
    try:
        print(f"🧪 MODO PRUEBA LOCAL - Sin conexión a Base de Datos")
        print(f"👤 Usuario: {user_id}")
        print(f"🍽️ Tipo de comida: {meal_type}")
        print(f"📝 Ingredientes a analizar: {len(ingredients)}")
        print("-" * 50)
        
        # 1. Procesar ingredientes y extraer macronutrientes
        macronutrient_extractions = []
        
        for i, ingredient in enumerate(ingredients, 1):
            print(f"🔍 Analizando ingrediente {i}/{len(ingredients)}: {ingredient}")
            
            extraction_result = extraction_chain.invoke({
                "ingredients": [ingredient],
                "meal_type": meal_type,
                "preparation_method": preparation_method,
                "portion_size": portion_size,
                "additional_notes": additional_notes
            })
            macronutrient_extractions.append(extraction_result)
            
            # Mostrar resultado por ingrediente
            print(f"   ✅ {extraction_result.name}")
            print(f"   📊 {extraction_result.total_calories:.1f} kcal | "
                  f"P: {extraction_result.total_protein:.1f}g | "
                  f"C: {extraction_result.total_carbs:.1f}g | "
                  f"G: {extraction_result.total_fat:.1f}g")
            print(f"   🎯 Confianza: {extraction_result.confidence_score*100:.0f}%")
            print()
        
        # 2. Calcular totales de la comida
        total_calories = sum(extraction.total_calories for extraction in macronutrient_extractions)
        total_protein = sum(extraction.total_protein for extraction in macronutrient_extractions)
        total_carbs = sum(extraction.total_carbs for extraction in macronutrient_extractions)
        total_fat = sum(extraction.total_fat for extraction in macronutrient_extractions)
        total_fiber = sum(extraction.total_fiber or 0 for extraction in macronutrient_extractions)
        total_sugar = sum(extraction.total_sugar or 0 for extraction in macronutrient_extractions)
        total_sodium = sum(extraction.total_sodium or 0 for extraction in macronutrient_extractions)
        
        print("=" * 50)
        print("📊 RESUMEN NUTRICIONAL TOTAL:")
        print(f"🔥 Calorías: {total_calories:.1f} kcal")
        print(f"🥩 Proteínas: {total_protein:.1f}g")
        print(f"🌾 Carbohidratos: {total_carbs:.1f}g")
        print(f"🥑 Grasas: {total_fat:.1f}g")
        if total_fiber > 0:
            print(f"🌿 Fibra: {total_fiber:.1f}g")
        if total_sugar > 0:
            print(f"🍯 Azúcares: {total_sugar:.1f}g")
        if total_sodium > 0:
            print(f"🧂 Sodio: {total_sodium:.1f}mg")
        print("=" * 50)
        
        # 3. Retornar resultado exitoso (simulado)
        return {
            "success": True,
            "mode": "LOCAL_TEST",
            "food_diary_id": f"local_test_{user_id}_{meal_type}",
            "photo_analysis_id": None,
            "ingredient_ids": [f"local_ingredient_{i}" for i in range(len(ingredients))],
            "extracted_macronutrients": [extraction.dict() for extraction in macronutrient_extractions],
            "total_nutrition": {
                "calories": total_calories,
                "protein": total_protein,
                "carbs": total_carbs,
                "fat": total_fat,
                "fiber": total_fiber,
                "sugar": total_sugar,
                "sodium": total_sodium
            },
            "message": f"✅ PRUEBA LOCAL: Se procesaron exitosamente {len(ingredients)} ingredientes (sin guardar en BD)",
            "note": "Esta es una prueba local. Los datos NO se guardaron en la base de datos."
        }
        
    except Exception as e:
        print(f"❌ Error en prueba local: {str(e)}")
        return {
            "success": False,
            "mode": "LOCAL_TEST",
            "error": str(e),
            "message": "Error al procesar los macronutrientes en modo local"
        }


# Función de prueba para desarrollo
def test_macronutrient_extraction():
    """Función de prueba LOCAL para el servicio de extracción de macronutrientes (sin BD)"""
    
    print("🚀 Iniciando prueba LOCAL del extractor de macronutrientes...")
    print("📝 Nota: Esta prueba NO requiere conexión a Supabase\n")
    
    test_ingredients = [
        "100g de pechuga de pollo a la plancha",
        "150g de arroz integral cocido",
        "80g de brócoli al vapor"
    ]
    
    # Usar la función LOCAL que no necesita Supabase
    result = extract_macronutrients_local_test(
        ingredients=test_ingredients,
        user_id="test_user_123",
        meal_type="almuerzo",
        preparation_method="a la plancha y al vapor",
        portion_size="porción mediana",
        additional_notes="Comida saludable post-entreno"
    )
    
    return result


if __name__ == "__main__":
    print("🥗 NUTRISENSE AI - PRUEBA LOCAL DE MACRONUTRIENTES")
    print("=" * 60)
    print("Esta prueba analiza ingredientes usando IA sin necesidad de base de datos")
    print("=" * 60)
    print()
    
    # Ejecutar prueba local
    test_result = test_macronutrient_extraction()
    
    print("\n🎉 ¡Prueba completada!")
    if test_result["success"]:
        print(f"✅ {test_result['message']}")
        print(f"📊 Modo: {test_result['mode']}")
    else:
        print(f"❌ {test_result['message']}")
        print(f"🔍 Error: {test_result.get('error', 'Desconocido')}")
    print("\n" + "=" * 60)
