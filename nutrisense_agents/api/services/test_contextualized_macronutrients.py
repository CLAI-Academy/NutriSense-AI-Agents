#!/usr/bin/env python3
"""
Script de prueba para el análisis contextualizado de macronutrientes.
Este script demuestra cómo usar el nuevo servicio contextualizado tanto en modo local como completo.

Autor: NutriSense AI Team
Fecha: 2024
"""

import sys
import os
from typing import List, Dict, Any

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nutrisense_agents.ai_companion.schemas.macronutrient_schema import (
    UserNutritionalProfile,
    Gender,
    ActivityLevel,
    Goal
)
from nutrisense_agents.api.services.macronutrient_service import (
    extract_macronutrients_contextualized_local_test,
    extract_macronutrients_with_context_service
)

def create_sample_user_profiles() -> List[UserNutritionalProfile]:
    """Crear perfiles de usuario de ejemplo para las pruebas"""
    
    profiles = [
        UserNutritionalProfile(
            age=25,
            gender=Gender.FEMALE,
            weight_kg=60.0,
            height_cm=165,
            activity_level=ActivityLevel.LIGHTLY_ACTIVE,
            goal=Goal.WEIGHT_LOSS,
            dietary_restrictions=["vegetariana"],
            medical_conditions=None
        ),
        UserNutritionalProfile(
            age=30,
            gender=Gender.MALE,
            weight_kg=80.0,
            height_cm=180,
            activity_level=ActivityLevel.VERY_ACTIVE,
            goal=Goal.MUSCLE_GAIN,
            dietary_restrictions=None,
            medical_conditions=None
        ),
        UserNutritionalProfile(
            age=45,
            gender=Gender.MALE,
            weight_kg=85.0,
            height_cm=175,
            activity_level=ActivityLevel.MODERATELY_ACTIVE,
            goal=Goal.MAINTENANCE,
            dietary_restrictions=["sin gluten"],
            medical_conditions=["diabetes tipo 2"]
        ),
        UserNutritionalProfile(
            age=28,
            gender=Gender.FEMALE,
            weight_kg=55.0,
            height_cm=160,
            activity_level=ActivityLevel.EXTRA_ACTIVE,
            goal=Goal.ENDURANCE,
            dietary_restrictions=None,
            medical_conditions=None
        )
    ]
    
    return profiles

def get_sample_meals() -> List[Dict[str, Any]]:
    """Crear comidas de ejemplo para las pruebas"""
    
    meals = [
        {
            "name": "Desayuno Equilibrado",
            "ingredients": ["2 huevos revueltos con 1 tostada integral y 1 aguacate mediano"],
            "meal_type": "desayuno",
            "preparation_method": "revuelto y tostado",
            "portion_size": "porción estándar",
            "notes": "Desayuno rico en proteínas y grasas saludables"
        },
        {
            "name": "Almuerzo Post-Entreno",
            "ingredients": ["150g de salmón a la plancha con 200g de quinoa y ensalada mixta"],
            "meal_type": "almuerzo",
            "preparation_method": "plancha y hervido",
            "portion_size": "porción grande",
            "notes": "Comida para recuperación post-entreno"
        },
        {
            "name": "Cena Ligera",
            "ingredients": ["100g de pechuga de pollo con 150g de verduras al vapor"],
            "meal_type": "cena",
            "preparation_method": "plancha y vapor",
            "portion_size": "porción pequeña",
            "notes": "Cena baja en carbohidratos"
        },
        {
            "name": "Snack Saludable",
            "ingredients": ["1 batido de proteína con plátano y mantequilla de almendras"],
            "meal_type": "snack",
            "preparation_method": "batido",
            "portion_size": "porción mediana",
            "notes": "Snack pre-entreno"
        }
    ]
    
    return meals

def run_single_test(profile: UserNutritionalProfile, meal: Dict[str, Any], test_num: int):
    """Ejecutar una prueba individual con un perfil y comida específicos"""
    
    print(f"\n{'='*80}")
    print(f"🧪 PRUEBA {test_num}: {meal['name']}")
    print(f"👤 Perfil: {profile.age} años, {profile.gender.value}, objetivo: {profile.goal.value}")
    print(f"🍽️ Comida: {meal['ingredients'][0]}")
    print(f"{'='*80}")
    
    try:
        result = extract_macronutrients_contextualized_local_test(
            ingredients=meal["ingredients"],
            user_profile=profile,
            user_id=f"test_user_{test_num}",
            meal_type=meal["meal_type"],
            preparation_method=meal["preparation_method"],
            portion_size=meal["portion_size"],
            additional_notes=meal["notes"]
        )
        
        if result["success"]:
            print(f"\n✅ {result['message']}")
            
            # Extraer datos clave para mostrar
            ctx_analysis = result["contextualized_analysis"]
            food_extraction = ctx_analysis["food_extraction"]
            nutritional_calc = ctx_analysis["nutritional_calculations"]
            analysis = ctx_analysis["contextualized_analysis"]
            
            print(f"\n📊 RESUMEN:")
            print(f"   🔥 Calorías: {food_extraction['total_calories']:.0f} kcal (Target diario: {nutritional_calc['vct_calories']:.0f})")
            print(f"   🥩 Proteína: {food_extraction['total_protein']:.1f}g ({analysis['protein_vs_target_percent']:.1f}% del objetivo)")
            print(f"   🌾 Carbohidratos: {food_extraction['total_carbs']:.1f}g ({analysis['carbs_vs_target_percent']:.1f}% del objetivo)")
            print(f"   🥑 Grasas: {food_extraction['total_fat']:.1f}g ({analysis['fat_vs_target_percent']:.1f}% del objetivo)")
            print(f"   🎯 Alineación con objetivo: {analysis['alignment_score']:.1f}/10")
            
        else:
            print(f"\n❌ {result['message']}")
            print(f"🔍 Error: {result.get('error', 'Desconocido')}")
            
    except Exception as e:
        print(f"\n❌ Error inesperado en la prueba: {str(e)}")

def run_comprehensive_test():
    """Ejecutar pruebas completas con diferentes perfiles y comidas"""
    
    print("🚀 INICIANDO PRUEBAS COMPREHENSIVAS DEL ANÁLISIS CONTEXTUALIZADO")
    print("📝 Nota: Estas pruebas usan el modo LOCAL (sin base de datos)")
    print("🎯 Se probarán 4 perfiles de usuario con 4 tipos de comidas diferentes\n")
    
    profiles = create_sample_user_profiles()
    meals = get_sample_meals()
    
    total_tests = len(profiles) * len(meals)
    current_test = 0
    successful_tests = 0
    
    for i, profile in enumerate(profiles):
        print(f"\n🔄 PROBANDO PERFIL {i+1}/{len(profiles)}")
        print(f"   👤 {profile.age} años, {profile.gender.value}, {profile.weight_kg}kg, {profile.height_cm}cm")
        print(f"   🏃‍♂️ Actividad: {profile.activity_level.value}")
        print(f"   🎯 Objetivo: {profile.goal.value}")
        if profile.dietary_restrictions:
            print(f"   🚫 Restricciones: {', '.join(profile.dietary_restrictions)}")
        if profile.medical_conditions:
            print(f"   🏥 Condiciones: {', '.join(profile.medical_conditions)}")
        
        for j, meal in enumerate(meals):
            current_test += 1
            try:
                run_single_test(profile, meal, current_test)
                successful_tests += 1
            except KeyboardInterrupt:
                print(f"\n\n👋 Pruebas interrumpidas por el usuario")
                print(f"📊 Pruebas completadas: {current_test-1}/{total_tests}")
                print(f"✅ Pruebas exitosas: {successful_tests}/{current_test-1}")
                return
            except Exception as e:
                print(f"\n❌ Error en prueba {current_test}: {str(e)}")
    
    print(f"\n\n🎉 ¡PRUEBAS COMPREHENSIVAS COMPLETADAS!")
    print(f"📊 Total de pruebas: {total_tests}")
    print(f"✅ Pruebas exitosas: {successful_tests}")
    print(f"❌ Pruebas fallidas: {total_tests - successful_tests}")
    print(f"📈 Tasa de éxito: {(successful_tests/total_tests)*100:.1f}%")

def run_quick_demo():
    """Ejecutar una demostración rápida con un ejemplo"""
    
    print("🚀 DEMO RÁPIDA DEL ANÁLISIS CONTEXTUALIZADO")
    print("=" * 60)
    
    # Perfil de ejemplo: mujer joven que quiere perder peso
    demo_profile = UserNutritionalProfile(
        age=28,
        gender=Gender.FEMALE,
        weight_kg=70.0,
        height_cm=165,
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        goal=Goal.WEIGHT_LOSS,
        dietary_restrictions=None,
        medical_conditions=None
    )
    
    # Comida de ejemplo
    demo_meal = {
        "name": "Ensalada de Pollo",
        "ingredients": ["150g de pechuga de pollo a la plancha con ensalada verde mixta y aceite de oliva"],
        "meal_type": "almuerzo",
        "preparation_method": "plancha",
        "portion_size": "porción mediana",
        "notes": "Almuerzo saludable para pérdida de peso"
    }
    
    run_single_test(demo_profile, demo_meal, 1)

def main():
    """Función principal del script de pruebas"""
    
    print("🥗 NUTRISENSE AI - ANÁLISIS CONTEXTUALIZADO DE MACRONUTRIENTES")
    print("=" * 70)
    print("Este script prueba el nuevo servicio de análisis contextualizado")
    print("=" * 70)
    
    while True:
        print("\n🔧 OPCIONES DE PRUEBA:")
        print("1. 🚀 Demo rápida (1 prueba)")
        print("2. 🧪 Pruebas comprehensivas (16 pruebas)")
        print("3. 🔧 Prueba personalizada")
        print("4. ❌ Salir")
        
        try:
            choice = input("\n👉 Selecciona una opción (1-4): ").strip()
            
            if choice == "1":
                run_quick_demo()
            elif choice == "2":
                run_comprehensive_test()
            elif choice == "3":
                print("🔧 Funcionalidad de prueba personalizada próximamente...")
            elif choice == "4":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Por favor selecciona 1, 2, 3 o 4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()
