from typing import Dict, Any
from datetime import datetime
from nutrisense_agents.ai_companion.graphs.food_analyzer.state import FoodAnalysisState
from langgraph.types import interrupt
from nutrisense_agents.ai_companion.agents.food_extraction_agent import get_image_extraction_agent_chain, get_text_extraction_agent_chain
from nutrisense_agents.ai_companion.agents.macronutrient_agent import get_macronutrient_extraction_chain
from nutrisense_agents.utils.get_meal_type import get_type_meal
from nutrisense_agents.db.supabase.client import SupabaseClient
import uuid
import logging
logger = logging.getLogger(__name__)

def extract_food_info(state: FoodAnalysisState) -> Dict[str, Any]:
    """Extrae información de alimentos según el tipo de entrada (imagen o texto)"""
    extraction_type = state.get("extraction_type")
    
    if extraction_type == "image":
        return _extract_from_image(state)
    elif extraction_type == "text":
        return _extract_from_text(state)
    else:
        return {
            "extracted_ingredients": [],
            "recipe_name": "Error en análisis",
            "current_step": "extraction_error",
            "error": f"Tipo de extracción no válido: {extraction_type}"
        }

def _extract_from_image(state: FoodAnalysisState) -> Dict[str, Any]:
    """Extrae ingredientes de la imagen usando visión por computadora"""
    try:
        image_extraction_agent_chain = get_image_extraction_agent_chain()
        result = image_extraction_agent_chain.invoke({
            "image_url": state["image_url"], 
            "notes": state.get("user_notes", "")
        })
    except Exception as e:
        return {
            "extracted_ingredients": [],
            "recipe_name": "Error en análisis de imagen",
            "current_step": "vision_error",
            "error": f"Error en extracción de imagen: {str(e)}"
        }
    
    extracted_ingredients = [ingredient.name for ingredient in result.ingredients]
    ingredients_with_details = [ingredient.model_dump() for ingredient in result.ingredients]
    
    return {
        "extracted_ingredients": extracted_ingredients,
        "recipe_name": result.recipe_name,
        "ingredients_with_details": ingredients_with_details,
        "current_step": "ingredients_extracted"
    }

def _extract_from_text(state: FoodAnalysisState) -> Dict[str, Any]:
    """Extrae ingredientes del texto usando análisis de texto"""
    try:
        text_extraction_agent_chain = get_text_extraction_agent_chain()
        result = text_extraction_agent_chain.invoke({
            "text_description": state["text_description"]
        })
    except Exception as e:
        return {
            "extracted_ingredients": [],
            "recipe_name": "Error en análisis de texto",
            "current_step": "text_error",
            "error": f"Error en extracción de texto: {str(e)}"
        }
    
    extracted_ingredients = [ingredient.name for ingredient in result.ingredients]
    ingredients_with_details = [ingredient.model_dump() for ingredient in result.ingredients]
    
    return {
        "extracted_ingredients": extracted_ingredients,
        "recipe_name": result.recipe_name,
        "ingredients_with_details": ingredients_with_details,
        "current_step": "ingredients_extracted"
    }

def human_ingredients_validation(state: FoodAnalysisState) -> Dict[str, Any]:
    """
    PRIMER INTERRUPT: Validación de ingredientes y nombre de receta
    
    El usuario puede:
    1. Aprobar todo sin cambios
    2. Modificar solo ingredientes
    3. Modificar solo el nombre
    4. Modificar ambos
    5. Agregar metadatos adicionales
    6. Cancelar el proceso
    """
    
    # Datos que se envían al usuario para validación
    validation_payload = {
        "extracted_ingredients": state["extracted_ingredients"],
        "recipe_name": state["recipe_name"],
        "extraction_type": state["extraction_type"],
        "current_step": "awaiting_validation",
        
        # Opciones disponibles para el usuario
        "options": {
            "can_modify_ingredients": True,
            "can_modify_recipe_name": True,
            "can_add_notes": True,
            "can_cancel": True,
            "example_responses": {
                "approve_all": {
                    "extracted_ingredients": state["extracted_ingredients"],
                    "recipe_name": state["recipe_name"]
                },
                "modify_ingredients": {
                    "extracted_ingredients": ["tomate", "nuevo_ingrediente"],
                    "recipe_name": state["recipe_name"]
                },
                "cancel": {
                    "action": "cancel",
                    "reason": "No quiero continuar"
                }
            }
        }
    }
    
    # Pausar y obtener respuesta del usuario
    user_response = interrupt(validation_payload)
    
    # Procesar la respuesta del usuario y actualizar el estado
    if user_response.get("action") == "cancel":
        return {
            "current_step": "cancelled_by_user",
            "action": "cancel",
            "cancellation_reason": user_response.get("reason", "Proceso cancelado por el usuario")
        }
    
    # Actualizar el estado con los datos del usuario
    updated_state = {
        "current_step": "ingredients_validated",
        "validation_completed": True
    }
    
    # Actualizar ingredientes si el usuario los modificó
    if "extracted_ingredients" in user_response:
        updated_state["extracted_ingredients"] = user_response["extracted_ingredients"]
        logger.info(f"🔄 Ingredientes actualizados por usuario: {user_response['extracted_ingredients']}")
    
    # Actualizar nombre de receta si el usuario lo modificó
    if "recipe_name" in user_response:
        updated_state["recipe_name"] = user_response["recipe_name"]
        logger.info(f"🔄 Nombre de receta actualizado por usuario: {user_response['recipe_name']}")
    
    # Agregar metadatos adicionales del usuario
    if "user_notes" in user_response:
        updated_state["user_notes"] = user_response["user_notes"]
    
    if "portion_size" in user_response:
        updated_state["portion_size"] = user_response["portion_size"]
    
    return updated_state

def handle_user_cancellation(state: FoodAnalysisState) -> Dict[str, Any]:
    """Maneja la cancelación del usuario en cualquier punto"""
    return {
        "success": False,
        "current_step": "cancelled_by_user",
        "error": state.get("cancellation_reason", "Proceso cancelado por el usuario")
    }

def calc_macros(state: FoodAnalysisState) -> Dict[str, Any]:
    """
    Calcula macros nutricionales considerando todas las modificaciones del usuario
    """
    
    # Verificar si el usuario canceló
    if state.get("action") == "cancel":
        return handle_user_cancellation(state)
    
    # Obtener ingredientes actualizados (pueden haber sido modificados por el usuario)
    ingredients_list = state.get("extracted_ingredients", [])
    
    # DEBUG: Verificar qué ingredientes se están usando
    logger.info(f"🔍 DEBUG - Ingredientes para calcular macros: {ingredients_list}")
    logger.info(f"🔍 DEBUG - Nombre de receta actual: {state.get('recipe_name')}")
    
    total_macros = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "fiber": 0
    }
    
    if not ingredients_list:
        return {
            "calculated_macros": total_macros,
            "current_step": "macros_calculated",
            "error": "No hay ingredientes para calcular macros"
        }
    
    try:
        chain = get_macronutrient_extraction_chain()
        result = chain.invoke({"ingredients": ingredients_list})
        
        total_macros.update({
            "calories": result.total_calories,
            "protein": result.total_protein,
            "carbs": result.total_carbs,
            "fat": result.total_fat,
            "fiber": result.total_fiber or 0
        })
        
        # Preservar metadatos adicionales del usuario
        response = {
            "calculated_macros": total_macros,
            "current_step": "macros_calculated"
        }
        
        # Mantener notas del usuario si las hay
        if state.get("user_notes"):
            response["user_notes"] = state["user_notes"]
        if state.get("portion_size"):
            response["portion_size"] = state["portion_size"]
            
        return response
        
    except Exception as e:
        return {
            "calculated_macros": total_macros,
            "current_step": "macros_calculated",
            "error": f"Error calculando macros: {str(e)}"
        }

def human_consumption_validation(state: FoodAnalysisState) -> Dict[str, Any]:
    """
    SEGUNDO INTERRUPT: Validación de consumo real
    
    El usuario puede:
    1. Confirmar que comió todo (100%)
    2. Ajustar el porcentaje consumido
    3. Hacer ajustes manuales específicos
    4. Agregar comidas adicionales
    5. Cancelar el guardado
    """
    
    calculated_macros = state.get("calculated_macros", {})
    
    current_recipe_name = state.get("recipe_name")
    current_ingredients = state.get("extracted_ingredients", [])
    
    consumption_payload = {
        "calculated_macros": calculated_macros,
        "recipe_name": current_recipe_name,
        "extracted_ingredients": current_ingredients,
        "extraction_type": state["extraction_type"],
        "current_step": "awaiting_consumption_validation",
        
        # Opciones de consumo
        "consumption_options": {
            "percentage_options": [25, 50, 75, 100, 125, 150],
            "manual_adjustment": True,
            "can_add_extras": True,
            "can_cancel": True,
            
            "example_responses": {
                "consumed_all": {
                    "calculated_macros": calculated_macros
                },
                "consumed_half": {
                    "calculated_macros": {
                        "calories": calculated_macros.get("calories", 0) * 0.5,
                        "protein": calculated_macros.get("protein", 0) * 0.5,
                        "carbs": calculated_macros.get("carbs", 0) * 0.5,
                        "fat": calculated_macros.get("fat", 0) * 0.5,
                        "fiber": calculated_macros.get("fiber", 0) * 0.5
                    }
                },
                "manual_adjustment": {
                    "calculated_macros": {
                        "calories": 400,
                        "protein": 25,
                        "carbs": 30,
                        "fat": 15,
                        "fiber": 3
                    },
                    "adjustment_reason": "No comí todo el arroz"
                },
                "added_extras": {
                    "calculated_macros": {
                        "calories": calculated_macros.get("calories", 0) + 100,
                        "protein": calculated_macros.get("protein", 0) + 5,
                        "carbs": calculated_macros.get("carbs", 0) + 10,
                        "fat": calculated_macros.get("fat", 0) + 5,
                        "fiber": calculated_macros.get("fiber", 0) + 1
                    },
                    "additional_foods": ["pan", "postre"]
                }
            }
        }
    }
    
    user_response = interrupt(consumption_payload)
    
    if user_response.get("action") == "cancel":
        return {
            "current_step": "cancelled_by_user",
            "action": "cancel",
            "cancellation_reason": user_response.get("reason", "Proceso cancelado por el usuario")
        }
    
    # Actualizar macros con los datos del usuario
    updated_state = {
        "current_step": "consumption_validated",
        "consumption_validation_completed": True
    }
    
    # Actualizar macros si el usuario los modificó
    if "calculated_macros" in user_response:
        updated_state["calculated_macros"] = user_response["calculated_macros"]
        logger.info(f"🔄 Macros actualizados por usuario: {user_response['calculated_macros']}")
    
    # Agregar información adicional del usuario
    if "adjustment_reason" in user_response:
        updated_state["adjustment_reason"] = user_response["adjustment_reason"]
    
    if "additional_foods" in user_response:
        updated_state["additional_foods"] = user_response["additional_foods"]
    
    return updated_state

def insert_food_diary(state: FoodAnalysisState) -> Dict[str, Any]:
    """
    Inserta en la base de datos considerando TODAS las modificaciones del usuario
    """
    
    # Verificar cancelación final
    if state.get("action") == "cancel":
        return handle_user_cancellation(state)
    
    try:
        supabase_client = SupabaseClient()
        
        # Usar datos finales actualizados
        extracted_ingredients = state.get("extracted_ingredients", [])
        calculated_macros = state.get("calculated_macros", {})
        recipe_name = state.get("recipe_name", "Receta analizada")
        
        logger.info(f"🔍 DEBUG - Datos finales para insertar:")
        logger.info(f"🔍 DEBUG - Ingredientes: {extracted_ingredients}")
        logger.info(f"🔍 DEBUG - Nombre receta: {recipe_name}")
        logger.info(f"🔍 DEBUG - Macros: {calculated_macros}")

        
        if not extracted_ingredients:
            return {
                "success": False,
                "error": "No hay ingredientes para guardar",
                "current_step": "food_diary_insert_failed"
            }
        
        meal_type = get_type_meal()
        
        # Construir notas completas incluyendo todas las modificaciones
        notes_parts = [f"Ingredientes: {', '.join(extracted_ingredients)}"]
        
        if state.get("user_notes"):
            notes_parts.append(f"Notas del usuario: {state['user_notes']}")
        
        if state.get("adjustment_reason"):
            notes_parts.append(f"Ajuste de consumo: {state['adjustment_reason']}")
            
        if state.get("additional_foods"):
            notes_parts.append(f"Comidas adicionales: {', '.join(state['additional_foods'])}")
        
        if state.get("portion_size"):
            notes_parts.append(f"Tamaño de porción: {state['portion_size']}")
        
        # Obtener hora actual para cálculos
        now = datetime.now()
        current_date = now.date()
        
        # Determinar day_type
        day_type = "weekend" if current_date.weekday() >= 5 else "weekday"
        
        # Filtrar solo los macros que existen en el esquema
        allowed_macros = ["calories", "protein", "carbs", "fat", "fiber"]
        filtered_macros = {}
        
        for macro in allowed_macros:
            filtered_macros[macro] = calculated_macros.get(macro, 0)
        
        # Obtener image_url solo si es análisis de imagen
        image_url = state.get("image_url") if state.get("extraction_type") == "image" else None
        
        logger.info(f"🔍 DEBUG - Macros filtrados: {filtered_macros}")
        logger.info(f"🔍 DEBUG - Image URL: {image_url}")
        
        # Preparar datos para food_diary según el esquema
        food_diary_data = {
            "date": current_date.isoformat(),
            "meal_type": meal_type,
            "recipe_id": None,
            "food_name": recipe_name,
            "quantity": 1.0,
            "unit": "gramos",
            **filtered_macros,
            "notes": " | ".join(notes_parts),
            "consumed_at": now.isoformat(),
            "location_type": None,
            "time_since_last_meal": None,
            "day_type": day_type,
            "eating_context": None,
            "mood_emoji": None,
            "created_at": now.isoformat(),
            "image_url": image_url
        }
        
        user_id = state.get("user_id", "default_user")
        
        result = supabase_client.add_food_diary(
            user_id=uuid.UUID(user_id) if user_id != "default_user" else uuid.uuid4(),
            data=food_diary_data
        )
        
        if result.data:
            return {
                "saved_food_diary_id": result.data[0]["id"],
                "food_diary_data": food_diary_data,
                "current_step": "food_diary_inserted",
                "success": True,
                "final_summary": {
                    "recipe_name": recipe_name,
                    "ingredients_count": len(extracted_ingredients),
                    "total_calories": filtered_macros.get("calories", 0),
                    "modifications_made": bool(state.get("user_notes") or state.get("adjustment_reason")),
                    "additional_foods": state.get("additional_foods", []),
                    "extraction_type": state.get("extraction_type")
                }
            }
        else:
            return {
                "success": False,
                "error": f"No se pudo insertar en food_diary. Result: {result}",
                "current_step": "food_diary_insert_failed"
            }
            
    except Exception as e:
        logger.error(f"🔍 DEBUG - Excepción completa: {e}")
        logger.error(f"🔍 DEBUG - Traceback: ", exc_info=True)
        return {
            "success": False,
            "error": f"Error insertando en food_diary: {str(e)}",
            "current_step": "food_diary_insert_failed"
        }

def update_user_streak(state: FoodAnalysisState) -> Dict[str, Any]:
    """
    Actualiza el streak del usuario.
    Verifica si ya ha añadido recetas hoy y actualiza el streak si no lo ha hecho.
    """
    
    # Verificar si el proceso anterior fue exitoso
    if state.get("action") == "cancel":
        logger.warning("No se actualiza streak porque el usuario canceló el proceso")
        return {
            "streak_updated": False,
            "current_streak": None,
            "current_step": "streak_update_skipped",
            "error": "No se actualiza streak porque el usuario canceló"
        }
    
    try:
        supabase_client = SupabaseClient()
        user_id = state.get("user_id", "default_user")
        
        # Si no hay user_id válido, no actualizar streak
        if user_id == "default_user" or not user_id:
            logger.warning("No se actualiza streak porque no hay user_id válido")
            return {
                "streak_updated": False,
                "current_streak": None,
                "current_step": "streak_update_skipped",
                "error": "No hay user_id válido para actualizar streak"
            }
        
        # Verificar y actualizar streak
        streak_result = supabase_client.check_and_update_user_streak(user_id)
        
        logger.info(f"Resultado de actualización de streak: {streak_result}")
        
        return {
            "streak_updated": streak_result.get("updated_streak", False),
            "current_streak": streak_result.get("streak"),
            "current_step": "streak_updated",
            "streak_message": streak_result.get("message", "")
        }
        
    except Exception as e:
        logger.error(f"Error actualizando streak del usuario: {e}")
        return {
            "streak_updated": False,
            "current_streak": None,
            "current_step": "streak_update_failed",
            "error": f"Error actualizando streak: {str(e)}"
        }