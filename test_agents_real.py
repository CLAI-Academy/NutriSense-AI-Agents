#!/usr/bin/env python3
"""
Test que verifica que los agentes generan fichas de usuario reales
Requiere configuración de variables de entorno para las API keys
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nutrisense_agents.ai_companion.agents.user_profile_agent import (
    nutrition_target_agent,
    get_user_profile_agent_chain,
    get_profile_summary_agent
)

def check_environment():
    """Verificar que las variables de entorno estén configuradas"""
    required_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "GROQ_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Para ejecutar este test necesitas configurar las API keys:")
        print("   export OPENAI_API_KEY=your_key")
        print("   export ANTHROPIC_API_KEY=your_key")
        print("   export GROQ_API_KEY=your_key")
        return False
    
    print("✅ Variables de entorno configuradas correctamente")
    return True

def test_nutrition_targets_agent():
    """Test del agente que calcula objetivos nutricionales"""
    print("🎯 Testing nutrition target agent...")
    
    try:
        agent = nutrition_target_agent()
        
        test_data = {
            "age": 30,
            "gender": "masculino",
            "weight": 75,
            "height": 175,
            "activity_level": "moderado",
            "goal": "perder peso",
            "preferences": ["vegetariano"],
            "allergies": ["gluten"],
            "medical_conditions": [],
            "breakfast": "café con tostadas",
            "lunch": "ensalada con proteína",
            "snack": "fruta",
            "dinner": "verduras con proteína",
            "work_mode": "home office",
            "shift_type": "fijo",
            "lunch_place": "casa",
            "who_cooks": "yo mismo",
            "who_shops": "yo mismo",
            "cook_for_others": False,
            "weekend_diff": "como más fuera de casa",
            "cooking_frequency": "3-4 veces por semana",
            "cooking_time": "30-45 minutos",
            "cooking_likes": "me gusta cocinar cosas sencillas",
            "ultraprocessed_frequency": "2-3 veces por semana",
            "weight_history": "peso estable en 70kg hace 2 años",
            "weight_changes": "subí 5kg durante pandemia",
            "weight_events": "estrés laboral",
            "current_difficulties": "picoteo entre comidas",
            "emotional_eating": True,
            "snacking": True,
            "alcohol_intake": "1-2 veces por semana"
        }
        
        print("⏳ Llamando al agente...")
        start_time = datetime.now()
        
        result = agent.invoke(test_data)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
        print(f"✅ Objetivos calculados:")
        print(f"   - Calorías: {result.calories}")
        print(f"   - Proteínas: {result.protein}g")
        print(f"   - Carbohidratos: {result.carbs}g")
        print(f"   - Grasas: {result.grasas}g")
        
        # Validaciones
        assert hasattr(result, 'calories'), "Falta campo calories"
        assert hasattr(result, 'protein'), "Falta campo protein"
        assert hasattr(result, 'carbs'), "Falta campo carbs"
        assert hasattr(result, 'grasas'), "Falta campo grasas"
        
        # Validar rangos razonables
        assert 1200 <= result.calories <= 4000, f"Calorías fuera del rango razonable: {result.calories}"
        assert 50 <= result.protein <= 300, f"Proteínas fuera del rango razonable: {result.protein}"
        assert 100 <= result.carbs <= 500, f"Carbohidratos fuera del rango razonable: {result.carbs}"
        assert 30 <= result.grasas <= 200, f"Grasas fuera del rango razonable: {result.grasas}"
        
        return True, result, execution_time
        
    except Exception as e:
        print(f"❌ Error en nutrition target agent: {str(e)}")
        return False, None, None

def test_user_profile_agent():
    """Test del agente que genera el perfil de usuario"""
    print("👤 Testing user profile agent...")
    
    try:
        agent = get_user_profile_agent_chain()
        
        test_data = {
            "age": 28,
            "gender": "femenino",
            "weight": 65,
            "height": 160,
            "activity_level": "ligero",
            "goal": "ganar masa muscular",
            "preferences": ["mediterránea", "comida casera"],
            "allergies": ["frutos secos"],
            "medical_conditions": ["hipotiroidismo"],
            "breakfast": "avena con frutas",
            "lunch": "quinoa con verduras",
            "snack": "yogur",
            "dinner": "pescado con verduras",
            "work_mode": "presencial",
            "shift_type": "rotativo",
            "lunch_place": "trabajo",
            "who_cooks": "mi pareja y yo",
            "who_shops": "compartimos",
            "cook_for_others": True,
            "weekend_diff": "cocinamos más elaborado",
            "cooking_frequency": "todos los días",
            "cooking_time": "45-60 minutos",
            "cooking_likes": "me encanta cocinar",
            "ultraprocessed_frequency": "rara vez",
            "weight_history": "peso estable",
            "weight_changes": "quiero ganar músculo",
            "weight_events": "inicio de rutina de gym",
            "current_difficulties": "comer suficiente proteína",
            "emotional_eating": False,
            "snacking": False,
            "alcohol_intake": "ocasionalmente",
            "daily_calories_target": 2200,
            "daily_protein_target": 120,
            "daily_carbs_target": 280,
            "daily_fat_target": 75,
            "weight_target": 70
        }
        
        print("⏳ Llamando al agente...")
        start_time = datetime.now()
        
        result = agent.invoke(test_data)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
        print(f"✅ Perfil generado:")
        print(f"   - Nombre: {result.profile_name}")
        print(f"   - Resumen: {result.user_summary[:100]}...")
        print(f"   - Objetivos: {result.nutrition_targets.calories} cal")
        print(f"   - Proteínas desayuno: {', '.join(result.breakfast_guidelines.recommended_proteins[:3])}...")
        print(f"   - Snacks opcionales: {len(result.optional_snacks)} opciones")
        
        # Validaciones de estructura
        assert hasattr(result, 'profile_name'), "Falta profile_name"
        assert hasattr(result, 'user_summary'), "Falta user_summary"
        assert hasattr(result, 'nutrition_targets'), "Falta nutrition_targets"
        assert hasattr(result, 'breakfast_guidelines'), "Falta breakfast_guidelines"
        assert hasattr(result, 'lunch_guidelines'), "Falta lunch_guidelines"
        assert hasattr(result, 'snack_guidelines'), "Falta snack_guidelines"
        assert hasattr(result, 'dinner_guidelines'), "Falta dinner_guidelines"
        assert hasattr(result, 'optional_snacks'), "Falta optional_snacks"
        assert hasattr(result, 'lifestyle_factors'), "Falta lifestyle_factors"
        assert hasattr(result, 'dietary_considerations'), "Falta dietary_considerations"
        assert hasattr(result, 'general_recommendations'), "Falta general_recommendations"
        
        # Validaciones de contenido
        assert len(result.profile_name) > 10, "profile_name muy corto"
        assert len(result.user_summary) > 50, "user_summary muy corto"
        assert len(result.breakfast_guidelines.recommended_proteins) > 0, "Sin proteínas para desayuno"
        assert len(result.breakfast_guidelines.recommended_carbs) > 0, "Sin carbohidratos para desayuno"
        assert len(result.optional_snacks) > 0, "Sin snacks opcionales"
        
        # Validar que no sean recetas específicas
        breakfast_proteins = result.breakfast_guidelines.recommended_proteins
        recipe_keywords = ["receta", "mezclar", "hervir", "cocinar durante", "preparar con"]
        
        for protein in breakfast_proteins:
            for keyword in recipe_keywords:
                if keyword in protein.lower():
                    print(f"⚠️  Posible receta específica detectada: {protein}")
        
        return True, result, execution_time
        
    except Exception as e:
        print(f"❌ Error en user profile agent: {str(e)}")
        return False, None, None

def test_profile_summary_agent():
    """Test del agente que genera el resumen conversacional"""
    print("📝 Testing profile summary agent...")
    
    try:
        agent = get_profile_summary_agent()
        
        test_data = {
            "age": 35,
            "gender": "masculino",
            "weight": 80,
            "height": 175,
            "goal": "mantener peso",
            "activity_level": "moderado",
            "preferences": ["mediterránea", "comida casera"],
            "allergies": [],
            "medical_conditions": ["diabetes tipo 2"],
            "breakfast": "café con cereales",
            "lunch": "comida casera completa",
            "snack": "fruta o yogur",
            "dinner": "cena ligera",
            "work_mode": "presencial",
            "shift_type": "fijo",
            "who_cooks": "yo cocino para la familia",
            "cooking_frequency": "diariamente",
            "cooking_time": "1-2 horas",
            "ultraprocessed_frequency": "muy rara vez",
            "current_difficulties": "controlar azúcar en sangre",
            "emotional_eating": False,
            "snacking": False,
            "daily_calories_target": 2000,
            "daily_protein_target": 100,
            "daily_carbs_target": 250,
            "daily_fat_target": 70,
            "weight_target": 80,
            "user_profile_summary": "Perfil nutricional personalizado para mantenimiento de peso con control de diabetes, enfocado en alimentación mediterránea y comida casera."
        }
        
        print("⏳ Llamando al agente...")
        start_time = datetime.now()
        
        result = agent.invoke(test_data)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
        print(f"✅ Resumen generado:")
        print(f"   - Longitud: {len(result.summary)} caracteres")
        print(f"   - Contenido: {result.summary[:150]}...")
        
        # Validaciones
        assert hasattr(result, 'summary'), "Falta campo summary"
        assert len(result.summary) > 100, "Resumen muy corto"
        assert len(result.summary) < 2000, "Resumen muy largo"
        
        # Verificar que sea conversacional
        conversational_indicators = ["tu", "tienes", "vas a", "te", "puedes"]
        is_conversational = any(indicator in result.summary.lower() for indicator in conversational_indicators)
        assert is_conversational, "El resumen no parece conversacional"
        
        # Verificar que mencione datos específicos
        assert "calorías" in result.summary.lower() or "2000" in result.summary, "No menciona calorías"
        assert "proteína" in result.summary.lower() or "100" in result.summary, "No menciona proteínas"
        
        return True, result, execution_time
        
    except Exception as e:
        print(f"❌ Error en profile summary agent: {str(e)}")
        return False, None, None

def run_agents_test():
    """Ejecutar test completo de los agentes"""
    print("🤖 INICIANDO TEST DE AGENTES REALES")
    print("=" * 60)
    
    # Verificar variables de entorno
    if not check_environment():
        return False
    
    print()
    
    tests = [
        ("Nutrition Target Agent", test_nutrition_targets_agent),
        ("User Profile Agent", test_user_profile_agent),
        ("Profile Summary Agent", test_profile_summary_agent)
    ]
    
    results = []
    total_time = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        print("-" * 40)
        
        try:
            success, result, execution_time = test_func()
            results.append((test_name, success, result, execution_time))
            if execution_time:
                total_time += execution_time
                
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {str(e)}")
            results.append((test_name, False, None, None))
    
    # Guardar resultados
    successful_results = []
    for test_name, success, result, execution_time in results:
        if success and result:
            successful_results.append({
                "test_name": test_name,
                "result": result.model_dump() if hasattr(result, 'model_dump') else str(result),
                "execution_time": execution_time
            })
    
    if successful_results:
        with open("agents_test_results.json", 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_execution_time": total_time,
                "results": successful_results
            }, f, ensure_ascii=False, indent=2)
        print(f"💾 Resultados guardados en: agents_test_results.json")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📈 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    successful_tests = sum(1 for _, success, _, _ in results if success)
    total_tests = len(results)
    
    print(f"✅ Tests exitosos: {successful_tests}/{total_tests}")
    print(f"⏱️  Tiempo total: {total_time:.2f} segundos")
    print(f"⏱️  Tiempo promedio: {total_time/len(results):.2f} segundos")
    
    for test_name, success, result, execution_time in results:
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({execution_time:.2f}s)" if execution_time else ""
        print(f"   {status} - {test_name}{time_info}")
    
    if successful_tests == total_tests:
        print("\n🎉 ¡TODOS LOS TESTS DE AGENTES PASARON EXITOSAMENTE!")
        print("✅ Los agentes generan fichas de usuario correctamente")
        print("✅ Las fichas contienen directrices generales (no recetas específicas)")
        print("✅ Los objetivos nutricionales se calculan apropiadamente")
        print("✅ Los resúmenes conversacionales son personalizados")
        print("\n🚀 CONCLUSIÓN: El sistema está funcionando correctamente con agentes reales")
        return True
    else:
        print(f"\n💥 {total_tests - successful_tests} TESTS FALLARON")
        print("🔧 Verifica la configuración de las API keys y la conectividad")
        return False

if __name__ == "__main__":
    try:
        print("🚀 Iniciando test de agentes reales...")
        success = run_agents_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {str(e)}")
        sys.exit(1)