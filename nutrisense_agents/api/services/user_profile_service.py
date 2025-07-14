from nutrisense_agents.ai_companion.graphs.nutrition_plan_graph.graph import compiled_user_profile_graph
from nutrisense_agents.ai_companion.schemas.user_profile_schema import UserProfileInputSchema

def generate_user_profile_service(user_data: dict, user_id: str):
    """Recibe un diccionario con los datos del usuario y su user_id.
    Genera un perfil nutricional usando el grafo de LangGraph y lo guarda en Supabase."""
    try:
        # Preparar el estado inicial con los datos del usuario
        initial_state = {
            "user_id": user_id,
            "age": user_data.get("age"),
            "gender": user_data.get("gender"),
            "weight": user_data.get("weight"),
            "height": user_data.get("height"),
            "activity_level": user_data.get("activity_level"),
            "goal": user_data.get("goal"),
            "preferences": user_data.get("preferences", []),
            "allergies": user_data.get("allergies", []),
            "medical_conditions": user_data.get("medical_conditions", []),
            "breakfast": user_data.get("breakfast"),
            "lunch": user_data.get("lunch"),
            "snack": user_data.get("snack"),
            "dinner": user_data.get("dinner"),
            "work_mode": user_data.get("work_mode"),
            "shift_type": user_data.get("shift_type"),
            "lunch_place": user_data.get("lunch_place"),
            "who_cooks": user_data.get("who_cooks"),
            "who_shops": user_data.get("who_shops"),
            "cook_for_others": user_data.get("cook_for_others"),
            "weekend_diff": user_data.get("weekend_diff"),
            "cooking_frequency": user_data.get("cooking_frequency"),
            "cooking_time": user_data.get("cooking_time"),
            "cooking_likes": user_data.get("cooking_likes"),
            "ultraprocessed_frequency": user_data.get("ultraprocessed_frequency"),
            "weight_history": user_data.get("weight_history"),
            "weight_changes": user_data.get("weight_changes"),
            "weight_events": user_data.get("weight_events"),
            "current_difficulties": user_data.get("current_difficulties"),
            "emotional_eating": user_data.get("emotional_eating"),
            "snacking": user_data.get("snacking"),
            "alcohol_intake": user_data.get("alcohol_intake"),
            "weight_target": user_data.get("weight_target")
        }
        
        # Ejecutar el grafo completo
        result = compiled_user_profile_graph.invoke(initial_state)
        
        # Verificar si el proceso fue exitoso
        if not result.get("success"):
            return {
                "success": False,
                "message": f"Error generating user profile: {result.get('error', 'Unknown error')}",
                "error": result.get("error", "Unknown error")
            }
        
        # Retornar resultado exitoso
        return {
            "success": True,
            "message": "User profile generated and saved successfully",
            "user_profile": result.get("user_profile_json"),
            "nutrition_targets": result.get("nutrition_targets"),
            "summary": result.get("summary"),
            "db_response": result.get("db_response")
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred while generating the user profile: {str(e)}",
            "error": str(e)
        } 


if __name__ == "__main__":
    import json
    import os
    
    raw_json = '''{
        "age": 30,
        "gender": "male",
        "weight": 100,
        "height": 186,
        "activity_level": "moderado",
        "goal": "perder peso",
        "preferences": "ninguna",
        "allergies": "gluten",
        "medical_conditions": "ninguna",
        "breakfast": "chocolate y helado",
        "lunch": "hamburguesa de mcdonalds",
        "snack": "nada",
        "dinner": "papas fritas con helado y jamon y queso",
        "work_mode": "home office",
        "shift_type": "fijo",
        "lunch_place": "en casa",
        "who_cooks": "nadie, compro comida",
        "who_shops": "generalmente mi pareja",
        "cook_for_others": "sí",
        "weekend_diff": "sí, suelo tomar mucho mas alcohol",
        "cooking_frequency": "me cuesta mucho cocinar, pero quiero aprender",
        "cooking_time": "sí, tengo tiempo",
        "cooking_likes": "no me gusta",
        "ultraprocessed_frequency": "todos los dias",
        "weight_history": "peso estable 85kg hace unos años",
        "weight_changes": "subí mucho este año",
        "weight_events": "estrés laboral",
        "current_difficulties": "picoteo y desorganización",
        "emotional_eating": "sí",
        "snacking": "sí",
        "alcohol_intake": "1 vez por semana",
        "daily_calories_target": 2689,
        "daily_protein_target": 172,
        "daily_carbs_target": 327,
        "daily_fat_target": 77,
        "weight_target": 86
    }'''
    user_data = json.loads(raw_json)

    result = generate_user_profile_service(user_data, "test-user-id")
    profile = result.get("user_profile", {})

    # Guardar el resultado en un archivo JSON
    # Crear la carpeta 'outputs' si no existe
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # Definir ruta de salida
    output_path = os.path.join(output_dir, "user_profile.json")
    with open("user_profile.json", "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    print(json.dumps(profile, ensure_ascii=False, indent=2))