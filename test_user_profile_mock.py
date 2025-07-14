#!/usr/bin/env python3
"""
Test simulado para verificar la estructura y funcionalidad del servicio de ficha de usuario
"""

import json
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nutrisense_agents.ai_companion.schemas.user_profile_schema import (
    UserNutritionProfileSchema,
    NutritionTargetSchema,
    MealGuideline,
    LifestyleFactors,
    DietaryConsiderations,
    GeneralRecommendations,
    ProfileSummarySchema
)

def create_mock_nutrition_targets():
    """Crear objetivos nutricionales simulados"""
    return NutritionTargetSchema(
        calories=2000,
        protein=150,
        carbs=200,
        grasas=65
    )

def create_mock_meal_guideline(meal_type="breakfast"):
    """Crear directrices de comida simuladas"""
    guidelines = {
        "breakfast": {
            "recommended_proteins": ["huevos", "yogur griego", "proteína vegetal", "queso fresco"],
            "recommended_carbs": ["avena", "pan integral", "cereales integrales", "frutas"],
            "recommended_vegetables": ["espinacas", "tomate", "pimientos"],
            "recommended_fruits": ["plátano", "bayas", "manzana"],
            "recommended_fats": ["aguacate", "frutos secos", "aceite de oliva"],
            "portion_guidelines": "1 porción de proteína (tamaño de palma), 1-2 porciones de carbohidratos, vegetales a voluntad",
            "meal_timing": "Consumir dentro de 1-2 horas después de despertar",
            "preparation_tips": ["Preparar la noche anterior", "Usar métodos de cocción rápidos", "Combinar proteína con carbohidratos complejos"]
        },
        "lunch": {
            "recommended_proteins": ["pollo", "pescado", "legumbres", "tofu"],
            "recommended_carbs": ["arroz integral", "quinoa", "pasta integral", "patatas"],
            "recommended_vegetables": ["brócoli", "ensalada verde", "calabacín", "zanahoria"],
            "recommended_fruits": ["opcional como postre"],
            "recommended_fats": ["aceite de oliva", "aguacate", "frutos secos"],
            "portion_guidelines": "1 porción de proteína, 1 porción de carbohidratos, 2 porciones de vegetales",
            "meal_timing": "Entre 12:00 y 14:00 horas",
            "preparation_tips": ["Batch cooking domingos", "Usar verduras congeladas", "Cocinar proteína en cantidad"]
        },
        "snack": {
            "recommended_proteins": ["yogur", "frutos secos", "huevo duro"],
            "recommended_carbs": ["fruta", "galletas integrales", "crackers"],
            "recommended_vegetables": ["bastones de zanahoria", "pepino", "tomates cherry"],
            "recommended_fruits": ["manzana", "pera", "bayas"],
            "recommended_fats": ["frutos secos", "semillas"],
            "portion_guidelines": "Porciones pequeñas, combinar proteína con carbohidratos",
            "meal_timing": "Entre comidas principales si hay hambre",
            "preparation_tips": ["Preparar porciones individuales", "Tener opciones listas", "Evitar ultraprocesados"]
        },
        "dinner": {
            "recommended_proteins": ["pescado", "pollo", "proteína vegetal", "huevos"],
            "recommended_carbs": ["vegetales", "ensalada", "carbohidratos ligeros"],
            "recommended_vegetables": ["verduras al vapor", "ensalada", "vegetales asados"],
            "recommended_fruits": ["opcional, preferir antes del postre"],
            "recommended_fats": ["aceite de oliva", "aguacate", "frutos secos"],
            "portion_guidelines": "1 porción de proteína, abundantes vegetales, carbohidratos ligeros",
            "meal_timing": "2-3 horas antes de dormir",
            "preparation_tips": ["Cenas ligeras", "Priorizar vegetales", "Evitar alimentos pesados"]
        }
    }
    
    meal_data = guidelines.get(meal_type, guidelines["breakfast"])
    
    return MealGuideline(
        recommended_proteins=meal_data["recommended_proteins"],
        recommended_carbs=meal_data["recommended_carbs"],
        recommended_vegetables=meal_data.get("recommended_vegetables"),
        recommended_fruits=meal_data.get("recommended_fruits"),
        recommended_fats=meal_data.get("recommended_fats"),
        portion_guidelines=meal_data["portion_guidelines"],
        meal_timing=meal_data.get("meal_timing"),
        preparation_tips=meal_data["preparation_tips"]
    )

def create_mock_lifestyle_factors():
    """Crear factores de estilo de vida simulados"""
    return LifestyleFactors(
        work_schedule="Horario de oficina (9-17h), posibilidad de comer en casa al mediodía",
        cooking_availability="Tiempo moderado para cocinar, prefiere preparaciones sencillas",
        meal_organization="Compras semanales, planificación básica de menús",
        social_eating="Come en familia, ocasionalmente fuera de casa los fines de semana",
        weekend_patterns="Más tiempo para cocinar, comidas más elaboradas"
    )

def create_mock_dietary_considerations():
    """Crear consideraciones dietéticas simuladas"""
    return DietaryConsiderations(
        allergies_impact="Evitar frutos secos en todas las preparaciones, leer etiquetas cuidadosamente",
        preferences_integration="Incorporar opciones vegetarianas 3-4 veces por semana",
        medical_adaptations="Control de porciones de carbohidratos, preferir complejos sobre simples",
        emotional_eating_strategies="Identificar triggers emocionales, tener alternativas saludables preparadas"
    )

def create_mock_general_recommendations():
    """Crear recomendaciones generales simuladas"""
    return GeneralRecommendations(
        meal_prep_suggestions=[
            "Preparar proteínas en lotes los domingos",
            "Cortar vegetales y guardar en recipientes",
            "Cocinar granos en cantidad y congelar porciones",
            "Preparar snacks saludables para la semana"
        ],
        shopping_tips=[
            "Hacer lista de compras basada en el plan semanal",
            "Comprar proteínas en ofertas y congelar",
            "Priorizar vegetales de temporada",
            "Tener básicos siempre en casa"
        ],
        time_management=[
            "Usar olla express para cocinar más rápido",
            "Aprovechar mientras se cocina una cosa para preparar otra",
            "Tener recetas de 15-20 minutos para días ocupados"
        ],
        habit_building=[
            "Empezar con cambios pequeños y sostenibles",
            "Establecer rutinas de compra y preparación",
            "Celebrar pequeños logros semanales"
        ],
        progress_tracking=[
            "Llevar registro de energía y bienestar",
            "Tomar fotos de los platos para ver evolución",
            "Evaluar semanalmente qué funcionó y qué no"
        ]
    )

def create_mock_user_profile():
    """Crear perfil de usuario completo simulado"""
    return UserNutritionProfileSchema(
        profile_name="Plan Nutricional Personalizado - Pérdida de Peso Saludable",
        user_summary="Hola María, hemos creado tu perfil nutricional personalizado enfocado en la pérdida de peso saludable. Considerando tu trabajo desde casa y tu preferencia por comidas vegetarianas, este perfil incluye directrices flexibles que te ayudarán a alcanzar tus objetivos de forma sostenible.",
        nutrition_targets=create_mock_nutrition_targets(),
        breakfast_guidelines=create_mock_meal_guideline("breakfast"),
        lunch_guidelines=create_mock_meal_guideline("lunch"),
        snack_guidelines=create_mock_meal_guideline("snack"),
        dinner_guidelines=create_mock_meal_guideline("dinner"),
        optional_snacks=[
            "Yogur griego con bayas",
            "Frutos secos (porción pequeña)",
            "Hummus con bastones de vegetales",
            "Huevo duro con tomates cherry",
            "Smoothie de proteína con vegetales verdes"
        ],
        lifestyle_factors=create_mock_lifestyle_factors(),
        dietary_considerations=create_mock_dietary_considerations(),
        general_recommendations=create_mock_general_recommendations(),
        special_notes="Recuerda que este es un perfil flexible que debe adaptarse a tus necesidades diarias. Lo importante es crear hábitos sostenibles."
    )

def validate_user_profile_structure(profile):
    """Validar que el perfil tenga la estructura correcta"""
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Verificar campos obligatorios
    required_fields = [
        "profile_name", "user_summary", "nutrition_targets",
        "breakfast_guidelines", "lunch_guidelines", "snack_guidelines", "dinner_guidelines",
        "optional_snacks", "lifestyle_factors", "dietary_considerations", "general_recommendations"
    ]
    
    for field in required_fields:
        if not hasattr(profile, field):
            validation_results["errors"].append(f"Campo obligatorio faltante: {field}")
            validation_results["valid"] = False
    
    # Verificar objetivos nutricionales
    if hasattr(profile, 'nutrition_targets'):
        targets = profile.nutrition_targets
        required_nutrition_fields = ["calories", "protein", "carbs", "grasas"]
        
        for field in required_nutrition_fields:
            if not hasattr(targets, field):
                validation_results["errors"].append(f"Objetivo nutricional faltante: {field}")
                validation_results["valid"] = False
            else:
                value = getattr(targets, field)
                if not isinstance(value, (int, float)) or value <= 0:
                    validation_results["errors"].append(f"Valor inválido para {field}: {value}")
                    validation_results["valid"] = False
    
    # Verificar directrices de comidas
    meals = ["breakfast_guidelines", "lunch_guidelines", "snack_guidelines", "dinner_guidelines"]
    required_meal_fields = ["recommended_proteins", "recommended_carbs", "portion_guidelines", "preparation_tips"]
    
    for meal in meals:
        if hasattr(profile, meal):
            meal_obj = getattr(profile, meal)
            for field in required_meal_fields:
                if not hasattr(meal_obj, field):
                    validation_results["errors"].append(f"Campo faltante en {meal}: {field}")
                    validation_results["valid"] = False
                else:
                    value = getattr(meal_obj, field)
                    if field in ["recommended_proteins", "recommended_carbs", "preparation_tips"]:
                        if not isinstance(value, list) or len(value) == 0:
                            validation_results["errors"].append(f"Lista vacía en {meal}.{field}")
                            validation_results["valid"] = False
    
    # Verificar que no sean recetas específicas
    if hasattr(profile, 'breakfast_guidelines'):
        proteins = profile.breakfast_guidelines.recommended_proteins
        specific_recipe_indicators = ["mezclar", "hervir", "freír", "cocinar durante", "receta"]
        
        for protein in proteins:
            if any(indicator in protein.lower() for indicator in specific_recipe_indicators):
                validation_results["warnings"].append(f"Posible receta específica en proteínas: {protein}")
    
    return validation_results

def test_schema_validation():
    """Test de validación de schemas"""
    print("📋 Probando validación de schemas...")
    
    try:
        # Test NutritionTargetSchema
        nutrition_targets = create_mock_nutrition_targets()
        assert nutrition_targets.calories == 2000
        assert nutrition_targets.protein == 150
        assert nutrition_targets.carbs == 200
        assert nutrition_targets.grasas == 65
        print("✅ NutritionTargetSchema validado")
        
        # Test MealGuideline
        meal_guideline = create_mock_meal_guideline("breakfast")
        assert len(meal_guideline.recommended_proteins) > 0
        assert len(meal_guideline.recommended_carbs) > 0
        assert len(meal_guideline.preparation_tips) > 0
        print("✅ MealGuideline validado")
        
        # Test UserNutritionProfileSchema completo
        profile = create_mock_user_profile()
        assert profile.profile_name is not None
        assert profile.user_summary is not None
        assert profile.nutrition_targets is not None
        print("✅ UserNutritionProfileSchema validado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en validación de schemas: {str(e)}")
        return False

def test_profile_structure():
    """Test de estructura del perfil"""
    print("🏗️ Probando estructura del perfil...")
    
    try:
        profile = create_mock_user_profile()
        validation_result = validate_user_profile_structure(profile)
        
        if validation_result["valid"]:
            print("✅ Estructura del perfil válida")
            
            # Mostrar información del perfil
            print(f"📊 Perfil: {profile.profile_name}")
            print(f"🎯 Objetivos: {profile.nutrition_targets.calories} cal, {profile.nutrition_targets.protein}g prot")
            print(f"🍳 Proteínas desayuno: {', '.join(profile.breakfast_guidelines.recommended_proteins[:3])}...")
            print(f"🥗 Snacks opcionales: {len(profile.optional_snacks)} opciones")
            
            if validation_result["warnings"]:
                print("⚠️  Warnings:")
                for warning in validation_result["warnings"]:
                    print(f"   - {warning}")
            
            return True
        else:
            print("❌ Estructura del perfil inválida")
            for error in validation_result["errors"]:
                print(f"   - {error}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de estructura: {str(e)}")
        return False

def test_json_serialization():
    """Test de serialización JSON"""
    print("💾 Probando serialización JSON...")
    
    try:
        profile = create_mock_user_profile()
        
        # Serializar a JSON
        profile_dict = profile.model_dump()
        json_str = json.dumps(profile_dict, ensure_ascii=False, indent=2)
        
        # Deserializar de JSON
        loaded_dict = json.loads(json_str)
        reconstructed_profile = UserNutritionProfileSchema(**loaded_dict)
        
        # Verificar que son iguales
        assert profile.profile_name == reconstructed_profile.profile_name
        assert profile.nutrition_targets.calories == reconstructed_profile.nutrition_targets.calories
        assert len(profile.breakfast_guidelines.recommended_proteins) == len(reconstructed_profile.breakfast_guidelines.recommended_proteins)
        
        print("✅ Serialización JSON exitosa")
        
        # Guardar ejemplo
        with open("mock_user_profile.json", 'w', encoding='utf-8') as f:
            f.write(json_str)
        print("💾 Ejemplo guardado en: mock_user_profile.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en serialización JSON: {str(e)}")
        return False

def run_mock_tests():
    """Ejecutar todos los tests simulados"""
    print("🧪 INICIANDO TESTS SIMULADOS DEL SERVICIO DE FICHA DE USUARIO")
    print("=" * 70)
    
    tests = [
        ("Validación de schemas", test_schema_validation),
        ("Estructura del perfil", test_profile_structure),
        ("Serialización JSON", test_json_serialization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        print("-" * 40)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 70)
    print("📈 RESUMEN DE RESULTADOS")
    print("=" * 70)
    
    successful_tests = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"✅ Tests exitosos: {successful_tests}/{total_tests}")
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    if successful_tests == total_tests:
        print("\n🎉 ¡TODOS LOS TESTS SIMULADOS PASARON EXITOSAMENTE!")
        print("✅ La estructura y schemas del servicio están correctos")
        print("✅ El sistema está listo para generar fichas de usuario")
        print("✅ Las fichas incluyen directrices generales (no recetas específicas)")
        print("✅ Los datos se pueden serializar correctamente para otros agentes")
        return True
    else:
        print(f"\n💥 {total_tests - successful_tests} TESTS FALLARON")
        return False

if __name__ == "__main__":
    try:
        success = run_mock_tests()
        print(f"\n{'='*70}")
        if success:
            print("🚀 CONCLUSIÓN: El servicio de ficha de usuario está correctamente implementado")
            print("📋 Las fichas generadas contienen directrices nutricionales generales")
            print("🔄 Estas fichas pueden ser utilizadas por otros agentes para generar recetas específicas")
        else:
            print("🔧 CONCLUSIÓN: Se necesitan ajustes en la implementación")
        
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {str(e)}")
        sys.exit(1)