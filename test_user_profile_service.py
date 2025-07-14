#!/usr/bin/env python3
"""
Test para verificar el funcionamiento del servicio de generación de fichas de usuario
"""

import json
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nutrisense_agents.api.services.user_profile_service import generate_user_profile_service

def create_test_data():
    """Crear datos de prueba realistas para diferentes escenarios"""
    
    # Escenario 1: Usuario que quiere perder peso, trabajo desde casa
    test_case_1 = {
        "name": "Usuario que quiere perder peso - Trabajo desde casa",
        "data": {
            "age": 32,
            "gender": "femenino",
            "weight": 75,
            "height": 165,
            "activity_level": "ligero",
            "goal": "perder peso",
            "preferences": ["vegetariano", "comida mediterránea"],
            "allergies": ["frutos secos"],
            "medical_conditions": ["hipotiroidismo"],
            "breakfast": "café con tostadas",
            "lunch": "ensalada o sandwich",
            "snack": "yogurt o fruta",
            "dinner": "pasta o arroz con verduras",
            "work_mode": "home office",
            "shift_type": "horario fijo",
            "lunch_place": "en casa",
            "who_cooks": "yo mismo",
            "who_shops": "yo mismo",
            "cook_for_others": True,
            "weekend_diff": "como más fuera de casa",
            "cooking_frequency": "cocino 4-5 veces por semana",
            "cooking_time": "30-45 minutos disponibles",
            "cooking_likes": "me gusta cocinar cosas sencillas",
            "ultraprocessed_frequency": "2-3 veces por semana",
            "weight_history": "peso estable en 68kg hace 3 años",
            "weight_changes": "subí 7kg durante pandemia",
            "weight_events": "estrés laboral y menos ejercicio",
            "current_difficulties": "picoteo entre comidas y porciones grandes",
            "emotional_eating": True,
            "snacking": True,
            "alcohol_intake": "1-2 veces por semana",
            "weight_target": 68
        }
    }
    
    # Escenario 2: Usuario que quiere ganar masa muscular, trabajo presencial
    test_case_2 = {
        "name": "Usuario que quiere ganar masa muscular - Trabajo presencial",
        "data": {
            "age": 28,
            "gender": "masculino",
            "weight": 65,
            "height": 175,
            "activity_level": "intenso",
            "goal": "ganar masa muscular",
            "preferences": ["sin restricciones"],
            "allergies": ["lactosa"],
            "medical_conditions": [],
            "breakfast": "avena con proteína",
            "lunch": "pollo con arroz",
            "snack": "batido de proteína",
            "dinner": "pescado con verduras",
            "work_mode": "presencial",
            "shift_type": "rotativo",
            "lunch_place": "restaurante cerca del trabajo",
            "who_cooks": "mi pareja",
            "who_shops": "compartimos las compras",
            "cook_for_others": True,
            "weekend_diff": "entreno más tiempo",
            "cooking_frequency": "poco, prefiero que cocine mi pareja",
            "cooking_time": "poco tiempo entre semana",
            "cooking_likes": "no me gusta cocinar",
            "ultraprocessed_frequency": "rara vez",
            "weight_history": "siempre he sido delgado",
            "weight_changes": "peso estable últimos años",
            "weight_events": "inicio de rutina de gym",
            "current_difficulties": "comer suficiente proteína",
            "emotional_eating": False,
            "snacking": False,
            "alcohol_intake": "ocasionalmente",
            "weight_target": 75
        }
    }
    
    # Escenario 3: Usuario que quiere mantener peso, edad madura
    test_case_3 = {
        "name": "Usuario que quiere mantener peso - Edad madura",
        "data": {
            "age": 45,
            "gender": "femenino",
            "weight": 62,
            "height": 160,
            "activity_level": "moderado",
            "goal": "mantener peso",
            "preferences": ["comida casera", "platos tradicionales"],
            "allergies": [],
            "medical_conditions": ["diabetes tipo 2"],
            "breakfast": "café con cereales",
            "lunch": "comida completa casera",
            "snack": "infusión con galletas",
            "dinner": "cena ligera",
            "work_mode": "presencial",
            "shift_type": "horario fijo",
            "lunch_place": "en casa",
            "who_cooks": "yo cocino para la familia",
            "who_shops": "yo hago las compras",
            "cook_for_others": True,
            "weekend_diff": "comidas familiares más elaboradas",
            "cooking_frequency": "cocino todos los días",
            "cooking_time": "1-2 horas disponibles",
            "cooking_likes": "me encanta cocinar",
            "ultraprocessed_frequency": "muy rara vez",
            "weight_history": "peso estable durante años",
            "weight_changes": "pequeñas fluctuaciones",
            "weight_events": "menopausia",
            "current_difficulties": "controlar el azúcar en sangre",
            "emotional_eating": False,
            "snacking": False,
            "alcohol_intake": "muy ocasionalmente",
            "weight_target": 62
        }
    }
    
    return [test_case_1, test_case_2, test_case_3]

def validate_user_profile(profile_data):
    """Validar que el perfil generado tenga la estructura correcta"""
    
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Verificar campos obligatorios
    required_fields = [
        "profile_name",
        "user_summary", 
        "nutrition_targets",
        "breakfast_guidelines",
        "lunch_guidelines", 
        "snack_guidelines",
        "dinner_guidelines",
        "optional_snacks",
        "lifestyle_factors",
        "dietary_considerations",
        "general_recommendations"
    ]
    
    for field in required_fields:
        if field not in profile_data:
            validation_results["errors"].append(f"Campo obligatorio faltante: {field}")
            validation_results["valid"] = False
    
    # Verificar objetivos nutricionales
    if "nutrition_targets" in profile_data:
        nutrition_targets = profile_data["nutrition_targets"]
        required_nutrition_fields = ["calories", "protein", "carbs", "grasas"]
        
        for field in required_nutrition_fields:
            if field not in nutrition_targets:
                validation_results["errors"].append(f"Objetivo nutricional faltante: {field}")
                validation_results["valid"] = False
            elif not isinstance(nutrition_targets[field], (int, float)):
                validation_results["errors"].append(f"Objetivo nutricional debe ser numérico: {field}")
                validation_results["valid"] = False
    
    # Verificar directrices de comidas
    meal_guidelines = ["breakfast_guidelines", "lunch_guidelines", "snack_guidelines", "dinner_guidelines"]
    required_meal_fields = ["recommended_proteins", "recommended_carbs", "portion_guidelines", "preparation_tips"]
    
    for meal in meal_guidelines:
        if meal in profile_data:
            meal_data = profile_data[meal]
            for field in required_meal_fields:
                if field not in meal_data:
                    validation_results["errors"].append(f"Campo faltante en {meal}: {field}")
                    validation_results["valid"] = False
    
    # Verificar que las recomendaciones no sean recetas específicas
    if "breakfast_guidelines" in profile_data:
        breakfast = profile_data["breakfast_guidelines"]
        if "recommended_proteins" in breakfast:
            proteins = breakfast["recommended_proteins"]
            # Verificar que sean categorías generales, no recetas específicas
            specific_recipes_keywords = ["receta", "preparación", "mezclar", "hervir", "freír"]
            for protein in proteins:
                if any(keyword in protein.lower() for keyword in specific_recipes_keywords):
                    validation_results["warnings"].append(f"Posible receta específica detectada en proteínas: {protein}")
    
    return validation_results

def run_test():
    """Ejecutar test completo del servicio"""
    
    print("🧪 INICIANDO TEST DEL SERVICIO DE FICHA DE USUARIO")
    print("=" * 60)
    
    test_cases = create_test_data()
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        test_result = {
            "case_name": test_case["name"],
            "success": False,
            "profile_generated": False,
            "validation_passed": False,
            "errors": [],
            "warnings": [],
            "execution_time": None
        }
        
        try:
            # Ejecutar el servicio
            start_time = datetime.now()
            
            print("⏳ Generando perfil de usuario...")
            service_result = generate_user_profile_service(test_case["data"], f"test-user-{i}")
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            test_result["execution_time"] = execution_time
            
            print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
            
            # Verificar resultado del servicio
            if service_result.get("success"):
                print("✅ Servicio ejecutado exitosamente")
                test_result["success"] = True
                
                # Verificar que se generó el perfil
                if service_result.get("user_profile"):
                    print("✅ Perfil de usuario generado")
                    test_result["profile_generated"] = True
                    
                    # Validar estructura del perfil
                    profile_data = service_result["user_profile"]
                    validation_result = validate_user_profile(profile_data)
                    
                    if validation_result["valid"]:
                        print("✅ Validación del perfil exitosa")
                        test_result["validation_passed"] = True
                    else:
                        print("❌ Validación del perfil falló")
                        test_result["errors"].extend(validation_result["errors"])
                    
                    test_result["warnings"].extend(validation_result["warnings"])
                    
                    # Mostrar información del perfil generado
                    print(f"📊 Perfil generado: {profile_data.get('profile_name', 'N/A')}")
                    if 'nutrition_targets' in profile_data:
                        targets = profile_data['nutrition_targets']
                        print(f"🎯 Objetivos: {targets.get('calories', 'N/A')} cal, {targets.get('protein', 'N/A')}g prot")
                    
                    # Guardar resultado para inspección
                    output_file = f"test_result_{i}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "test_case": test_case["name"],
                            "service_result": service_result,
                            "validation": validation_result
                        }, f, ensure_ascii=False, indent=2)
                    print(f"💾 Resultado guardado en: {output_file}")
                    
                else:
                    print("❌ No se generó el perfil de usuario")
                    test_result["errors"].append("No se generó el perfil de usuario")
                    
            else:
                print("❌ Error en el servicio")
                error_msg = service_result.get("error", "Error desconocido")
                test_result["errors"].append(f"Error del servicio: {error_msg}")
                print(f"Error: {error_msg}")
                
        except Exception as e:
            print(f"❌ Excepción durante la ejecución: {str(e)}")
            test_result["errors"].append(f"Excepción: {str(e)}")
            
        results.append(test_result)
        
        # Mostrar warnings si los hay
        if test_result["warnings"]:
            print("\n⚠️  Warnings:")
            for warning in test_result["warnings"]:
                print(f"   - {warning}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📈 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results if r["success"] and r["validation_passed"])
    total_tests = len(results)
    
    print(f"✅ Tests exitosos: {successful_tests}/{total_tests}")
    print(f"⏱️  Tiempo promedio: {sum(r['execution_time'] or 0 for r in results)/len(results):.2f}s")
    
    for result in results:
        status = "✅ PASS" if result["success"] and result["validation_passed"] else "❌ FAIL"
        print(f"   {status} - {result['case_name']}")
        
        if result["errors"]:
            for error in result["errors"]:
                print(f"      ❌ {error}")
    
    # Guardar resumen completo
    with open("test_summary.json", 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Resumen completo guardado en: test_summary.json")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    print("🚀 Iniciando test del servicio de ficha de usuario...")
    
    try:
        success = run_test()
        if success:
            print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
            sys.exit(0)
        else:
            print("\n💥 ALGUNOS TESTS FALLARON")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO DURANTE EL TEST: {str(e)}")
        sys.exit(1)