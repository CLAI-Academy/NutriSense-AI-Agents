"""
Prueba LOCAL del servicio de extracción de macronutrientes.
Este script NO requiere conexión a Supabase ni configuración de base de datos.
Solo necesita las API keys de OpenAI o Anthropic configuradas en .env
"""

from nutrisense_agents.ai_companion.agents.macronutrient_agent import get_macronutrient_extraction_chain

def test_local_macronutrient_extraction():
    """
    Prueba simple y local del extractor de macronutrientes.
    Solo usa la IA, no guarda nada en base de datos.
    """
    
    print("🥗 NUTRISENSE AI - PRUEBA LOCAL SIMPLE")
    print("=" * 50)
    print("📝 Analizando ingredientes con IA (sin base de datos)")
    print("=" * 50)
    print()
    
    # Inicializar la cadena de IA
    try:
        extraction_chain = get_macronutrient_extraction_chain()
        print("✅ Agente de IA inicializado correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar IA: {str(e)}")
        print("💡 Verifica que tengas configuradas las API keys en .env")
        return
    
    # Ingredientes de prueba
    test_ingredients = [
        "100g de pechuga de pollo a la plancha",
        "150g de arroz integral cocido", 
        "80g de brócoli al vapor"
    ]
    
    print(f"🔍 Analizando {len(test_ingredients)} ingredientes:")
    for i, ingredient in enumerate(test_ingredients, 1):
        print(f"   {i}. {ingredient}")
    print()
    
    # Procesar cada ingrediente
    results = []
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    for i, ingredient in enumerate(test_ingredients, 1):
        print(f"🧠 Analizando ingrediente {i}/{len(test_ingredients)}...")
        
        try:
            # Llamar a la IA
            result = extraction_chain.invoke({
                "ingredients": [ingredient],
                "meal_type": "almuerzo",
                "preparation_method": "saludable",
                "portion_size": "porción estándar",
                "additional_notes": "Comida balanceada"
            })
            
            results.append(result)
            
            # Mostrar resultado
            print(f"   ✅ {result.name}")
            print(f"   📊 {result.total_calories:.1f} kcal | "
                  f"P: {result.total_protein:.1f}g | "
                  f"C: {result.total_carbs:.1f}g | "
                  f"G: {result.total_fat:.1f}g")
            print(f"   🎯 Confianza: {result.confidence_score*100:.0f}%")
            print()
            
            # Acumular totales
            total_calories += result.total_calories
            total_protein += result.total_protein
            total_carbs += result.total_carbs
            total_fat += result.total_fat
            
        except Exception as e:
            print(f"   ❌ Error procesando '{ingredient}': {str(e)}")
            print()
            continue
    
    # Mostrar resumen final
    if results:
        print("=" * 50)
        print("📊 RESUMEN NUTRICIONAL TOTAL:")
        print(f"🔥 Calorías totales: {total_calories:.1f} kcal")
        print(f"🥩 Proteínas totales: {total_protein:.1f}g")
        print(f"🌾 Carbohidratos totales: {total_carbs:.1f}g")
        print(f"🥑 Grasas totales: {total_fat:.1f}g")
        print("=" * 50)
        print(f"✅ Análisis completado: {len(results)}/{len(test_ingredients)} ingredientes procesados")
    else:
        print("❌ No se pudieron procesar los ingredientes")
    
    print()
    print("🎉 ¡Prueba local completada!")
    print("💡 Esta prueba solo usa IA, no guarda datos en base de datos")


if __name__ == "__main__":
    test_local_macronutrient_extraction()
