from nutrisense_agents.ai_companion.agents.nutrition_plan_agent import get_nutrition_plan_agent_chain
import json
import os

def test_local_generation():
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

    chain = get_nutrition_plan_agent_chain()
    result = chain.invoke(user_data)
    markdown = result.markdown

    # Guardar localmente (opcional)
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "plan_nutricional.md"), "w", encoding="utf-8") as f:
        f.write(markdown)

    print("\n🧠 Plan Nutricional Generado:\n")
    print(markdown)

if __name__ == "__main__":
    test_local_generation()
