#!/usr/bin/env python3
"""
Test simple para verificar el funcionamiento del servicio de generación de fichas de usuario
(sin depender de la base de datos)
"""

import json
import os
import sys
from datetime import datetime
import uuid

# Agregar el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nutrisense_agents.ai_companion.agents.user_profile_agent import (
    nutrition_target_agent,
    get_user_profile_agent_chain,
    get_profile_summary_agent
)

def test_nutrition_targets():
    """Test para verificar el cálculo de objetivos nutricionales"""
    print("🎯 Probando cálculo de objetivos nutricionales...")
    
    try:
        agent = nutrition_target_agent()
        
        test_data = {
            "age": 30,
            "gender": "masculino",
            "weight": 75,
            "height": 175,
            "activity_level": "moderado",
            "goal": "perder peso",
            "preferences": [],
            "allergies": [],
            "medical_conditions": [],
            "breakfast": "café con tostadas",
            "lunch": "pollo con ensalada",
            "snack": "fruta",
            "dinner": "pescado con verduras",
            "work_mode": "office",
            "shift_type": "fijo",
            "lunch_place": "trabajo",
            "who_cooks": "yo",
            "who_shops": "yo",
            "cook_for_others": False,
            "weekend_diff": "como más fuera",
            "cooking_frequency": "3 veces por semana",
            "cooking_time": "30 minutos",
            "cooking_likes": "me gusta cocinar",
            "ultraprocessed_frequency": "ocasionalmente",
            "weight_history": "peso estable",
            "weight_changes": "subí 5kg",
            "weight_events": "estrés",
            "current_difficulties": "picoteo",
            "emotional_eating": True,
            "snacking": True,
            "alcohol_intake": "1 vez por semana"
        }
        
        result = agent.invoke(test_data)
        
        print(f"✅ Objetivos calculados: {result.calories} cal, {result.protein}g prot, {result.carbs}g carbs, {result.grasas}g grasas")
        
        # Validar que los valores sean razonables
        assert result.calories > 1000 and result.calories < 4000, "Calorías fuera del rango razonable"
        assert result.protein > 50 and result.protein < 300, "Proteínas fuera del rango razonable"
        assert result.carbs > 50 and result.carbs < 500, "Carbohidratos fuera del rango razonable"
        assert result.grasas > 20 and result.grasas < 200, "Grasas fuera del rango razonable"
        
        return True, result
        
    except Exception as e:
        print(f"❌ Error en test de objetivos nutricionales: {str(e)}")
        return False, None

def test_user_profile_generation():
    """Test para verificar la generación del perfil de usuario"""
    print("👤 Probando generación de perfil de usuario...")
    
    try:
        agent = get_user_profile_agent_chain()
        
        test_data = {
            "age": 28,
            "gender": "femenino",
            "weight": 65,
            "height": 160,
            "activity_level": "ligero",
            "goal": "ganar masa muscular",
            "preferences": ["vegetariano"],
            "allergies": ["frutos secos"],
            "medical_conditions": [],
            "breakfast": "avena con frutas",
            "lunch": "quinoa con verduras",
            "snack": "yogur",
            "dinner": "tofu con arroz",
            "work_mode": "home office",
            "shift_type": "flexible",
            "lunch_place": "casa",
            "who_cooks": "yo",
            "who_shops": "pareja",
            "cook_for_others": True,
            "weekend_diff": "cocino más elaborado",
            "cooking_frequency": "todos los días",
            "cooking_time": "45 minutos",
            "cooking_likes": "me encanta cocinar",
            "ultraprocessed_frequency": "rara vez",
            "weight_history": "peso estable",
            "weight_changes": "quiero ganar músculo",
            "weight_events": "inicio de gym",
            "current_difficulties": "comer suficiente proteína",
            "emotional_eating": False,
            "snacking": False,
            "alcohol_intake": "nunca",
            "daily_calories_target": 2200,
            "daily_protein_target": 120,
            "daily_carbs_target": 280,
            "daily_fat_target": 75,
            "weight_target": 70
        }
        
        result = agent.invoke(test_data)
        
        print(f"✅ Perfil generado: {result.profile_name}")
        
        # Validar estructura del perfil
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
        
        # Validar que las directrices no sean recetas específicas
        breakfast_proteins = result.breakfast_guidelines.recommended_proteins
        assert isinstance(breakfast_proteins, list), "recommended_proteins debe ser lista"
        assert len(breakfast_proteins) > 0, "Debe haber proteínas recomendadas"
        
        print(f"📊 Directrices de desayuno - Proteínas: {breakfast_proteins}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Error en test de perfil de usuario: {str(e)}")
        return False, None

def test_profile_summary():
    """Test para verificar la generación del resumen conversacional"""
    print("📝 Probando generación de resumen conversacional...")
    
    try:
        agent = get_profile_summary_agent()
        
        test_data = {
            "age": 35,
            "gender": "masculino",
            "weight": 80,
            "height": 175,
            "goal": "mantener peso",
            "activity_level": "moderado",
            "preferences": ["mediterránea"],
            "allergies": [],
            "medical_conditions": ["diabetes"],
            "breakfast": "café con cereales",
            "lunch": "comida casera",
            "snack": "fruta",
            "dinner": "cena ligera",
            "work_mode": "presencial",
            "shift_type": "fijo",
            "who_cooks": "yo",
            "cooking_frequency": "diariamente",
            "cooking_time": "1 hora",
            "ultraprocessed_frequency": "rara vez",
            "current_difficulties": "controlar azúcar",
            "emotional_eating": False,
            "snacking": False,
            "daily_calories_target": 2000,
            "daily_protein_target": 100,
            "daily_carbs_target": 250,
            "daily_fat_target": 70,
            "weight_target": 80,
            "user_profile_summary": "Perfil para mantenimiento con control de diabetes"
        }
        
        result = agent.invoke(test_data)
        
        print(f"✅ Resumen generado: {result.summary[:100]}...")
        
        # Validar que el resumen sea conversacional
        assert hasattr(result, 'summary'), "Falta summary"
        assert len(result.summary) > 50, "Resumen muy corto"
        assert "tu" in result.summary.lower() or "tienes" in result.summary.lower(), "Debe ser conversacional"
        
        return True, result
        
    except Exception as e:
        print(f"❌ Error en test de resumen: {str(e)}")
        return False, None

def run_full_test():
    """Ejecutar test completo sin base de datos"""
    print("🚀 INICIANDO TEST COMPLETO DEL SERVICIO DE FICHA DE USUARIO")
    print("=" * 60)
    
    results = []
    
    # Test 1: Objetivos nutricionales
    print("\n1️⃣ TEST: Cálculo de objetivos nutricionales")
    print("-" * 40)
    success1, result1 = test_nutrition_targets()
    results.append(("Objetivos nutricionales", success1))
    
    # Test 2: Generación de perfil
    print("\n2️⃣ TEST: Generación de perfil de usuario")
    print("-" * 40)
    success2, result2 = test_user_profile_generation()
    results.append(("Perfil de usuario", success2))
    
    # Test 3: Resumen conversacional
    print("\n3️⃣ TEST: Resumen conversacional")
    print("-" * 40)
    success3, result3 = test_profile_summary()
    results.append(("Resumen conversacional", success3))
    
    # Guardar resultados de ejemplo
    if success2 and result2:
        with open("example_user_profile.json", 'w', encoding='utf-8') as f:
            json.dump(result2.model_dump(), f, ensure_ascii=False, indent=2)
        print(f"💾 Ejemplo de perfil guardado en: example_user_profile.json")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📈 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    successful_tests = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"✅ Tests exitosos: {successful_tests}/{total_tests}")
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    if successful_tests == total_tests:
        print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("✅ El servicio de ficha de usuario está funcionando correctamente")
        return True
    else:
        print(f"\n💥 {total_tests - successful_tests} TESTS FALLARON")
        return False

if __name__ == "__main__":
    try:
        success = run_full_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {str(e)}")
        sys.exit(1)