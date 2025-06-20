from typing import Dict, Any
from datetime import datetime
from nutrisense_agents.ai_companion.graphs.img_analtzer.state import RecipeState
from langgraph.types import interrupt
from nutrisense_agents.ai_companion.agents.image_extraction_agent import get_image_extraction_agent_chain
from nutrisense_agents.ai_companion.agents.macronutrient_agent import get_macronutrient_extraction_chain
from nutrisense_agents.utils.get_meal_type import get_type_meal
from nutrisense_agents.db.supabase.client import SupabaseClient
import uuid

def vision_extract(state: RecipeState) -> Dict[str, Any]:
    """
    Extrae ingredientes de la imagen usando visión por computadora y genera un nombre de receta
    """
    try:
        image_extraction_agent_chain = get_image_extraction_agent_chain()
        result = image_extraction_agent_chain.invoke({"image_url": state["image_url"]})
    except Exception as e:
        return {
            "extracted_ingredients": [],
            "recipe_name": "Error en análisis",
            "current_step": "vision_error",
            "error": f"Error en extracción de imagen: {str(e)}"
        }
    
    # Convertir objetos DetectedIngredient a lista de strings para compatibilidad JSON
    extracted_ingredients = [ingredient.name for ingredient in result.ingredients]
    
    # También guardamos los detalles completos como diccionarios serializables
    ingredients_with_details = [ingredient.model_dump() for ingredient in result.ingredients]
    
    return {
        "extracted_ingredients": extracted_ingredients,
        "recipe_name": result.recipe_name,  # También guardamos el nombre de receta
        "ingredients_with_details": ingredients_with_details,  # Detalles completos JSON serializables
        "current_step": "ingredients_extracted"
    }

    
def human_ingredients_validation(state: RecipeState) -> Dict[str, Any]:
    """
    Punto de interrupción para validación humana
    """
    # ✅ Correcto: asignar el resultado de interrupt a una variable
    validation_result = interrupt({
        "extracted_ingredients": state["extracted_ingredients"],
        "recipe_name": state["recipe_name"],
        "current_step": "awaiting_validation"
    })
    
    # ✅ Correcto: retornar un diccionario que actualice el estado
    # El validation_result contendrá los datos enviados cuando se reanude
    return {
        "extracted_ingredients": validation_result.get("extracted_ingredients", state["extracted_ingredients"]),
        "recipe_name": validation_result.get("recipe_name", state["recipe_name"]),
        "current_step": "ingredients_validated"
    }

def calc_macros(state: RecipeState) -> Dict[str, Any]:
    """
    Calcula macros nutricionales para toda la lista de ingredientes usando la chain de macronutrientes
    """
    total_macros = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "fiber": 0
    }
    
    # Obtener la lista de ingredientes como strings
    ingredients_list = state.get("extracted_ingredients", [])
    
    if not ingredients_list:
        return {
            "calculated_macros": total_macros,
            "current_step": "macros_calculated",
            "error": "No hay ingredientes para calcular macros"
        }
    
    # Inicializar la chain dentro del contexto del nodo para evitar problemas de contexto runnable
    try:
        chain = get_macronutrient_extraction_chain()
        result = chain.invoke({"ingredients": ingredients_list})
    except Exception as e:
        return {
            "calculated_macros": total_macros,
            "current_step": "macros_calculated",
            "error": f"Error calculando macros: {str(e)}"
        }
    
    total_macros["calories"] = result.total_calories
    total_macros["protein"] = result.total_protein
    total_macros["carbs"] = result.total_carbs
    total_macros["fat"] = result.total_fat
    total_macros["fiber"] = result.total_fiber or 0
    
    return {
        "calculated_macros": total_macros,
        "current_step": "macros_calculated"
    }

    

def human_consumption_validation(state: RecipeState) -> Dict[str, Any]:
    """
    Punto de interrupción para validación humana del consumo de la comida
    """
    # ✅ Correcto: asignar el resultado de interrupt a una variable
    consumption_result = interrupt({
        "calculated_macros": state["calculated_macros"],
        "current_step": "awaiting_consumption_validation"
    })
    
    # ✅ Correcto: retornar un diccionario que actualice el estado
    return {
        "calculated_macros": consumption_result.get("calculated_macros", state["calculated_macros"]),
        "current_step": "consumption_validated"
    }

def insert_food_diary(state: RecipeState) -> Dict[str, Any]:
    """
    Inserta una entrada en la tabla food_diary con los datos calculados
    """
    try:
        supabase_client = SupabaseClient()
        # Obtener datos del estado
        extracted_ingredients = state.get("extracted_ingredients", [])
        calculated_macros = state.get("calculated_macros", {})
        recipe_name = state.get("recipe_name", "Receta analizada")
        
        # Si no hay ingredientes extraídos, usar valores por defecto
        if not extracted_ingredients:
            return {
                "success": False,
                "error": "No hay ingredientes extraídos para insertar",
                "current_step": "food_diary_insert_failed"
            }
        
        # Calculamos el tipo de comida en base a la fecha y hora actual
        meal_type = get_type_meal()
        
        # Preparar datos para food_diary usando el formato esperado por add_food_diary
        food_diary_data = {
            "date": datetime.now().date().isoformat(),
            "meal_type": meal_type,
            "food_name": recipe_name,  # Usar el nombre de la receta
            "quantity": 1.0,  # Una porción de la receta completa
            "unit": "serving",
            "calories": calculated_macros.get("calories", 0),
            "protein": calculated_macros.get("protein", 0),
            "carbs": calculated_macros.get("carbs", 0),
            "fat": calculated_macros.get("fat", 0),
            "fiber": calculated_macros.get("fiber", 0),
            "notes": f"Comida analizada automáticamente: {', '.join(extracted_ingredients)}",
            "consumed_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
         # Usar la función add_food_diary del cliente Supabase
        user_id = state.get("user_id", "default_user")

        
        
        result = supabase_client.add_food_diary(
            user_id=uuid.UUID(user_id) if user_id != "default_user" else uuid.uuid4(),
            data=food_diary_data
        )
        
        if result.data:
            food_diary_id = result.data[0]["id"]
            return {
                "saved_food_diary_id": food_diary_id,
                "food_diary_data": food_diary_data,
                "current_step": "food_diary_inserted",
                "success": True
            }
        else:
            return {
                "success": False,
                "error": "No se pudo insertar en food_diary",
                "current_step": "food_diary_insert_failed"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error insertando en food_diary: {str(e)}",
            "current_step": "food_diary_insert_failed"
        }
    
