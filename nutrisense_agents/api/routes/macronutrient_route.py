from fastapi import APIRouter
from nutrisense_agents.api.services.macronutrient_service import (
    extract_macronutrients_service,
    extract_macronutrients_local_test
)
from nutrisense_agents.ai_companion.schemas.macronutrient_request_schema import (
    MacronutrientInputSchema,
    MacronutrientResponseSchema,
)

router = APIRouter()

@router.post("/macronutrients")
async def extract_macronutrients(input_data: MacronutrientInputSchema):
    """
    Extrae macronutrientes de ingredientes y los guarda en Supabase.
    """
    result = extract_macronutrients_service(
        ingredients=input_data.ingredients,
        user_id=input_data.user_id,
        meal_type=input_data.meal_type,
        preparation_method=input_data.preparation_method,
        portion_size=input_data.portion_size,
        photo_url=input_data.photo_url,
        additional_notes=input_data.additional_notes
    )
    return result

@router.post("/macronutrients/local")
async def extract_macronutrients_local(input_data: MacronutrientInputSchema):
    """
    Extrae macronutrientes de ingredientes (modo local, sin guardar en BD).
    """
    result = extract_macronutrients_local_test(
        ingredients=input_data.ingredients,
        user_id=input_data.user_id,
        meal_type=input_data.meal_type,
        preparation_method=input_data.preparation_method,
        portion_size=input_data.portion_size,
        additional_notes=input_data.additional_notes
    )
    return result

@router.post("/macronutrients/production")
async def extract_macronutrients_production(input_data: MacronutrientInputSchema):
    """
    Extrae macronutrientes y los guarda en Supabase con estructura simplificada.
    Funciona con la estructura actual de la base de datos.
    """
    from nutrisense_agents.db.supabase.client import get_supabase_client
    from nutrisense_agents.ai_companion.agents.macronutrient_agent import process_multiple_ingredients
    from datetime import datetime
    
    try:
        # 1. Verificar conexión a Supabase
        supabase = get_supabase_client()
        if not supabase:
            return {
                "success": False,
                "error": "Supabase not configured",
                "message": "Base de datos no disponible. Use el modo local para pruebas."
            }
        
        # 2. Procesar ingredientes con IA
        extractions = process_multiple_ingredients(
            ingredients=input_data.ingredients,
            meal_type=input_data.meal_type,
            preparation_method=input_data.preparation_method,
            portion_size=input_data.portion_size,
            additional_notes=input_data.additional_notes
        )
        
        # 3. Calcular totales
        total_calories = sum(e.total_calories for e in extractions)
        total_protein = sum(e.total_protein for e in extractions)
        total_carbs = sum(e.total_carbs for e in extractions)
        total_fat = sum(e.total_fat for e in extractions)
        
        # 4. Insertar en food_diary con estructura compatible
        food_diary_data = {
            "user_id": input_data.user_id,
            "date": datetime.now().date().isoformat(),
            "meal_type": input_data.meal_type,
            "recipe_id": 1,  # Requerido por la estructura
            "food_name": ", ".join([e.name for e in extractions]),
            "quantity": sum(e.estimated_quantity_grams for e in extractions),
            "unit": "gramos",
            "calories": total_calories,
            "protein": total_protein,
            "carbs": total_carbs,
            "fat": total_fat,
            "notes": f"API: {input_data.additional_notes or 'Sin notas'}",
            "consumed_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table("food_diary").insert(food_diary_data).execute()
        
        if result.data:
            return {
                "success": True,
                "mode": "PRODUCTION",
                "food_diary_id": result.data[0].get('id'),
                "extracted_macronutrients": [
                    {
                        "name": e.name,
                        "description": e.description,
                        "calories_per_100g": e.calories_per_100g,
                        "protein_per_100g": e.protein_per_100g,
                        "carbs_per_100g": e.carbs_per_100g,
                        "fat_per_100g": e.fat_per_100g,
                        "estimated_quantity_grams": e.estimated_quantity_grams,
                        "total_calories": e.total_calories,
                        "total_protein": e.total_protein,
                        "total_carbs": e.total_carbs,
                        "total_fat": e.total_fat,
                        "confidence_score": e.confidence_score
                    } for e in extractions
                ],
                "total_nutrition": {
                    "calories": total_calories,
                    "protein": total_protein,
                    "carbs": total_carbs,
                    "fat": total_fat
                },
                "message": f"✅ PRODUCCIÓN: Datos guardados en Supabase exitosamente (ID: {result.data[0].get('id')})"
            }
        else:
            return {
                "success": False,
                "error": "Failed to insert data",
                "message": "No se pudieron guardar los datos en la base de datos"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al procesar los macronutrientes"
        }
