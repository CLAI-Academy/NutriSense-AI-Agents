from nutrisense_agents.ai_companion.agents.nutrition_plan_agent import get_nutrition_plan_agent_chain
from nutrisense_agents.db.supabase.client import SupabaseClient

supabase = SupabaseClient()

chain = get_nutrition_plan_agent_chain()

def generate_nutrition_plan_service(user_data: dict,user_id:str):
    """Recibe un diccionario con los datos del usuario y su user_id.
    Genera un plan nutricional en formato markdown y lo guarda en Supabase."""
    try:
            
        result = chain.invoke(user_data)
        markdown = result.markdown

        response = supabase.add_nutritional_plan_to_user_health_profile(user_id, markdown)


        if response.get("error"):
            return {
                "success": False,
                "message": f"Error updating nutrition plan: {response['error']}",
                "error": response["error"]
            }
        return {
            "success": True,
            "message": "Nutrition plan updated successfully",
            "markdown": markdown
        }
    except Exception as e:
            return {
                "success": False,
                "message": f"An error occurred while generating the nutrition plan: {str(e)}",
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

    markdown = generate_nutrition_plan_service(user_data)

    # Guardar el resultado en un archivo Markdown
    # Crear la carpeta 'outputs' si no existe
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # Definir ruta de salida
    output_path = os.path.join(output_dir, "plan_nutricional.md")
    with open("plan_nutricional.md", "w", encoding="utf-8") as f:
        f.write(markdown)

    print(markdown)