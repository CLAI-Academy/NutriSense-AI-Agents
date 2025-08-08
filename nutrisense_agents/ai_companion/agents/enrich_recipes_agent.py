from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional, Union
import json
from nutrisense_agents.config.settings import settings

def get_openai_client():
    """Get OpenAI client with proper configuration"""
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=settings.OPENAI_API_KEY)

# Modelos para el input
class Ingredient(BaseModel):
    id: Optional[int]
    name: str
    default_unit: str

class IngredientsInput(BaseModel):
    ingredients: List[Ingredient]

# Modelos para el output
class NutritionUpdate(BaseModel):
    id: Optional[int]
    name: str
    category: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: float

class NutritionError(BaseModel):
    name: str
    reason: str

class NutritionResponse(BaseModel):
    updates: List[NutritionUpdate]
    errors: List[NutritionError]

def enrich_ingredients_nutrition(ingredients_json: dict) -> dict:
    """
    Función que recibe un JSON con ingredientes y devuelve información nutricional enriquecida.
    
    Args:
        ingredients_json: Dict con formato {"ingredients": [{"id": int, "name": str, "default_unit": str}]}
    
    Returns:
        Dict con formato {"updates": [...], "errors": [...]}
    """
    
    # Validar input
    try:
        input_data = IngredientsInput(**ingredients_json)
    except Exception as e:
        return {"updates": [], "errors": [{"name": "input_validation", "reason": f"Invalid input format: {str(e)}"}]}
    
    # Crear el prompt para el LLM
    ingredients_list = []
    for ing in input_data.ingredients:
        ingredients_list.append({
            "id": ing.id,
            "name": ing.name,
            "default_unit": ing.default_unit
        })
    
    system_prompt = """Eres un experto en nutrición. Te daré una lista de ingredientes y necesitas devolver información nutricional completa para cada uno.

Para cada ingrediente, proporciona:
- category: categoría del alimento en español (ej: "semillas", "leche vegetal", "frutas", etc.)
- calories_per_100g: calorías por 100g
- protein_per_100g: proteínas en g por 100g
- carbs_per_100g: carbohidratos en g por 100g  
- fat_per_100g: grasas en g por 100g
- fiber_per_100g: fibra en g por 100g
- nutrition_status: "verified" si tienes datos confiables, "pending" si no estás seguro

Si no puedes encontrar información nutricional confiable para un ingrediente, inclúyelo en la lista de errores con la razón.

Responde SOLO con el JSON en el formato especificado, sin texto adicional."""

    user_prompt = f"Ingredientes a procesar: {json.dumps(ingredients_list, indent=2)}"

    try:
        # Hacer la llamada al LLM
        client = get_openai_client()
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=NutritionResponse,
        )
        
        # Extraer la respuesta parseada
        nutrition_data = response.choices[0].message.parsed
        
        # Asegurar que los IDs se mantengan del input original
        for update in nutrition_data.updates:
            # Buscar el ingrediente original por nombre para mantener el ID
            for original_ing in input_data.ingredients:
                if original_ing.name.lower() == update.name.lower():
                    update.id = original_ing.id
                    break
        
        return nutrition_data.model_dump()
        
    except Exception as e:
        return {
            "updates": [],
            "errors": [{"name": "llm_error", "reason": f"Error calling LLM: {str(e)}"}]
        }

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de test para enrich_ingredients_nutrition
    test_input = {
        "ingredients": [
            {
                "id": 123,
                "name": "chia seeds",
                "default_unit": "g"
            },
            {
                "id": 124,
                "name": "almond milk",
                "default_unit": "ml"
            }
        ]
    }
    
    result = enrich_ingredients_nutrition(test_input)
    print("Nutrition enrichment result:")
    print(json.dumps(result, indent=2))