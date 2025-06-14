"""
Ejemplo de uso del servicio de extracción de macronutrientes.
Este script demuestra cómo usar el servicio de manera independiente.

MODO LOCAL: Para pruebas sin base de datos, usa las funciones que terminan en "_local"
MODO COMPLETO: Para producción con base de datos, usa las funciones normales
"""

from nutrisense_agents.api.services.macronutrient_service import extract_macronutrients_service, extract_macronutrients_local_test

def ejemplo_desayuno_local():
    """Ejemplo LOCAL de análisis de un desayuno (sin BD)"""
    ingredientes_desayuno = [
        "2 huevos revueltos",
        "2 rebanadas de pan integral tostado", 
        "1 aguacate mediano",
        "1 vaso de leche desnatada"
    ]
    
    resultado = extract_macronutrients_local_test(
        ingredients=ingredientes_desayuno,
        user_id="usuario_ejemplo_001",
        meal_type="desayuno",
        preparation_method="revuelto y tostado",
        portion_size="desayuno estándar",
        additional_notes="Desayuno balanceado con proteína y grasas saludables"
    )
    
    return resultado

def ejemplo_desayuno():
    """Ejemplo de análisis de un desayuno"""
    ingredientes_desayuno = [
        "2 huevos revueltos",
        "2 rebanadas de pan integral tostado",
        "1 aguacate mediano",
        "1 vaso de leche desnatada"
    ]
    
    resultado = extract_macronutrients_service(
        ingredients=ingredientes_desayuno,
        user_id="usuario_ejemplo_001",
        meal_type="desayuno",
        preparation_method="revuelto y tostado",
        portion_size="desayuno estándar",
        additional_notes="Desayuno balanceado con proteína y grasas saludables"
    )
    
    return resultado

def ejemplo_almuerzo_con_foto():
    """Ejemplo de análisis de un almuerzo con foto"""
    ingredientes_almuerzo = [
        "150g de salmón a la plancha",
        "200g de quinoa cocida",
        "100g de espárragos verdes",
        "1 cucharada de aceite de oliva"
    ]
    
    resultado = extract_macronutrients_service(
        ingredients=ingredientes_almuerzo,
        user_id="usuario_ejemplo_002", 
        meal_type="almuerzo",
        preparation_method="a la plancha",
        portion_size="almuerzo abundante",
        photo_url="https://ejemplo.com/mi-almuerzo.jpg",
        additional_notes="Almuerzo rico en omega-3 y proteína"
    )
    
    return resultado

def ejemplo_snack_simple():
    """Ejemplo de análisis de un snack simple"""
    ingredientes_snack = [
        "1 manzana mediana",
        "30g de almendras"
    ]
    
    resultado = extract_macronutrients_service(
        ingredients=ingredientes_snack,
        user_id="usuario_ejemplo_003",
        meal_type="snack",
        preparation_method="crudo",
        portion_size="snack pequeño",
        additional_notes="Snack saludable de media tarde"
    )
    
    return resultado

def mostrar_resultado(resultado, titulo):
    """Función helper para mostrar resultados de manera legible"""
    print(f"\n{'='*50}")
    print(f"📊 {titulo}")
    print(f"{'='*50}")
    
    if resultado["success"]:
        print(f"✅ Estado: {resultado['message']}")
        print(f"📝 ID Diario: {resultado['food_diary_id']}")
        
        if resultado.get('photo_analysis_id'):
            print(f"📸 ID Análisis Foto: {resultado['photo_analysis_id']}")
        
        print(f"\n🍽️ RESUMEN NUTRICIONAL TOTAL:")
        totales = resultado["total_nutrition"]
        print(f"   Calorías: {totales['calories']:.1f} kcal")
        print(f"   Proteínas: {totales['protein']:.1f}g")
        print(f"   Carbohidratos: {totales['carbs']:.1f}g")
        print(f"   Grasas: {totales['fat']:.1f}g")
        if totales['fiber'] > 0:
            print(f"   Fibra: {totales['fiber']:.1f}g")
        if totales['sodium'] > 0:
            print(f"   Sodio: {totales['sodium']:.1f}mg")
        
        print(f"\n🥘 INGREDIENTES ANALIZADOS:")
        for i, ingrediente in enumerate(resultado["extracted_macronutrients"], 1):
            print(f"   {i}. {ingrediente['name']}")
            print(f"      └ {ingrediente['total_calories']:.1f} kcal | "
                  f"P: {ingrediente['total_protein']:.1f}g | "
                  f"C: {ingrediente['total_carbs']:.1f}g | "
                  f"G: {ingrediente['total_fat']:.1f}g")
            print(f"      └ Confianza: {ingrediente['confidence_score']*100:.0f}%")
    else:
        print(f"❌ Error: {resultado['message']}")
        print(f"   Detalles: {resultado.get('error', 'Sin detalles')}")

def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("🚀 Iniciando ejemplos del servicio de extracción de macronutrientes...")
    
    try:
        # Ejemplo 1: Desayuno
        resultado_desayuno = ejemplo_desayuno()
        mostrar_resultado(resultado_desayuno, "EJEMPLO 1: Desayuno Balanceado")
        
        # Ejemplo 2: Almuerzo con foto
        resultado_almuerzo = ejemplo_almuerzo_con_foto()
        mostrar_resultado(resultado_almuerzo, "EJEMPLO 2: Almuerzo con Foto")
        
        # Ejemplo 3: Snack
        resultado_snack = ejemplo_snack_simple()
        mostrar_resultado(resultado_snack, "EJEMPLO 3: Snack Saludable")
        
        print(f"\n{'='*50}")
        print("✨ Todos los ejemplos completados exitosamente!")
        print("📋 Revisa la base de datos para ver los registros creados.")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"\n❌ Error ejecutando ejemplos: {str(e)}")
def main_local():
    """Función principal que ejecuta todos los ejemplos en MODO LOCAL (sin BD)"""
    print("🚀 Iniciando ejemplos del servicio de extracción de macronutrientes...")
    print("🧪 MODO LOCAL: Solo análisis de IA, sin guardar en base de datos")
    print("=" * 60)
    
    try:
        # Ejemplo 1: Desayuno LOCAL
        resultado_desayuno = ejemplo_desayuno_local()
        mostrar_resultado(resultado_desayuno, "EJEMPLO 1: Desayuno Balanceado (LOCAL)")
        
        print(f"\n{'='*60}")
        print("✨ Ejemplo local completado exitosamente!")
        print("💡 Este modo solo analiza con IA, no guarda en base de datos.")
        print("🔄 Para usar con base de datos, ejecuta con el flag --full")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Error ejecutando ejemplo local: {str(e)}")
        print("💡 Verifica que tengas configuradas las API keys en .env")

def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("🚀 Iniciando ejemplos del servicio de extracción de macronutrientes...")
    
    try:
        # Ejemplo 1: Desayuno
        resultado_desayuno = ejemplo_desayuno()
        mostrar_resultado(resultado_desayuno, "EJEMPLO 1: Desayuno Balanceado")
        
        # Ejemplo 2: Almuerzo con foto
        resultado_almuerzo = ejemplo_almuerzo_con_foto()
        mostrar_resultado(resultado_almuerzo, "EJEMPLO 2: Almuerzo con Foto")
        
        # Ejemplo 3: Snack
        resultado_snack = ejemplo_snack_simple()
        mostrar_resultado(resultado_snack, "EJEMPLO 3: Snack Saludable")
        
        print(f"\n{'='*50}")
        print("✨ Todos los ejemplos completados exitosamente!")
        print("📋 Revisa la base de datos para ver los registros creados.")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"\n❌ Error ejecutando ejemplos: {str(e)}")
        print("💡 Asegúrate de que:")
        print("   - Las variables de entorno están configuradas")
        print("   - La base de datos Supabase está accesible")
        print("   - Las tablas requeridas existen")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        print("🔗 Modo COMPLETO: Con conexión a base de datos")
        main()
    else:
        print("🧪 Modo LOCAL por defecto: Solo análisis de IA")
        print("💡 Para modo completo con BD usa: python ejemplo_macronutrientes.py --full")
        print()
        main_local()
