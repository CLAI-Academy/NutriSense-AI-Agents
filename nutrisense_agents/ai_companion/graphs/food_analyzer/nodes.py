from typing import Dict, Any
from datetime import datetime, date
from nutrisense_agents.ai_companion.graphs.food_analyzer.state import FoodAnalysisState
from langgraph.types import interrupt
from nutrisense_agents.ai_companion.agents.food_extraction_agent import get_image_extraction_agent_chain, get_text_extraction_agent_chain, get_compatibility_agent_chain
from nutrisense_agents.ai_companion.agents.macronutrient_agent import get_macronutrient_extraction_chain
from nutrisense_agents.utils.get_meal_type import get_type_meal
from nutrisense_agents.db.supabase.client import SupabaseClient
from openai import OpenAI
from nutrisense_agents.config.agent_config import get_openai_api_key
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
    Validación de consumo automática - asume que el usuario consumió todo
    """
    
    calculated_macros = state.get("calculated_macros", {})
    
    # Asumir que el usuario consumió toda la comida (100%)
    updated_state = {
        "current_step": "consumption_validated",
        "consumption_validation_completed": True,
        "calculated_macros": calculated_macros
    }
    
    logger.info(f"✅ Consumo validado automáticamente: {calculated_macros}")
    
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
        
        # Obtener datos de compatibilidad nutricional
        compatibility_result = state.get("compatibility_result", {})
        compatibility = compatibility_result.get("compatibility")
        agent_observation = compatibility_result.get("agent_observation")
        audio_url = state.get("audio_url")
        
        logger.info(f"🔍 DEBUG - Macros filtrados: {filtered_macros}")
        logger.info(f"🔍 DEBUG - Image URL: {image_url}")
        logger.info(f"🔍 DEBUG - Compatibilidad: {compatibility}")
        logger.info(f"🔍 DEBUG - Observación del agente: {agent_observation}")
        logger.info(f"🔍 DEBUG - Audio URL: {audio_url}")
        
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
            "image_url": image_url,
            "compatibility": compatibility,
            "agent_observation": agent_observation,
            "audio_url": audio_url
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
                    "extraction_type": state.get("extraction_type"),
                    "audio_url": state.get("audio_url")
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

def analyze_nutritional_compatibility(state: FoodAnalysisState) -> Dict[str, Any]:
    """
    Analiza la compatibilidad nutricional de la comida con los objetivos del usuario.
    Se ejecuta en paralelo al cálculo de macronutrientes.
    """
    
    # Verificar si el usuario canceló
    if state.get("action") == "cancel":
        return {
            "compatibility_result": None,
            "current_step": "compatibility_cancelled",
            "error": "Análisis de compatibilidad cancelado por el usuario"
        }
    
    try:
        supabase_client = SupabaseClient()
        user_id = state.get("user_id", "default_user")
        
        # Si no hay user_id válido, no analizar compatibilidad
        if user_id == "default_user" or not user_id:
            logger.warning("No se analiza compatibilidad porque no hay user_id válido")
            return {
                "compatibility_result": {
                    "compatibility": "5", 
                    "agent_observation": "No se pudo evaluar compatibilidad sin perfil de usuario."
                },
                "current_step": "compatibility_analyzed"
            }
        
        # 1. Obtener targets del usuario desde user_health_profile
        user_targets = {}
        user_name = {}
        recent_foods = {}
        try:
            profile_result = supabase_client.supabase.table("user_health_profile").select(
                "daily_calories_target, daily_protein_target, daily_carbs_target, daily_fat_target"
            ).eq("user_id", user_id).execute()
            
            user_name = supabase_client.supabase.table("profiles").select(
                "full_name"
            ).eq("id", user_id).execute()
            
            recent_foods = supabase_client.supabase.table("food_diary").select(
                "food_name, calories, protein, carbs, fat"
            ).eq("user_id", user_id).eq("date", date.today().isoformat()).execute()
            
            if profile_result.data and len(profile_result.data) > 0:
                profile = profile_result.data[0]
                user_targets = {
                    "calories": float(profile.get("daily_calories_target", 2000) or 2000),
                    "protein": float(profile.get("daily_protein_target", 150) or 150),
                    "carbs": float(profile.get("daily_carbs_target", 250) or 250),
                    "fat": float(profile.get("daily_fat_target", 70) or 70)
                }
            else:
                # Valores por defecto si no hay perfil
                user_targets = {"calories": 2000, "protein": 150, "carbs": 250, "fat": 70}
        except Exception as e:
            logger.warning(f"Error obteniendo perfil del usuario: {e}")
            user_targets = {"calories": 2000, "protein": 150, "carbs": 250, "fat": 70}
        
        # 2. Obtener consumo del día actual desde food_diary
        today = date.today().isoformat()
        daily_consumption = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        
        try:
            diary_result = supabase_client.supabase.table("food_diary").select(
                "calories, protein, carbs, fat"
            ).eq("user_id", user_id).eq("date", today).execute()
            
            if diary_result.data:
                for entry in diary_result.data:
                    daily_consumption["calories"] += float(entry.get("calories", 0) or 0)
                    daily_consumption["protein"] += float(entry.get("protein", 0) or 0)
                    daily_consumption["carbs"] += float(entry.get("carbs", 0) or 0)
                    daily_consumption["fat"] += float(entry.get("fat", 0) or 0)
        except Exception as e:
            logger.warning(f"Error obteniendo consumo diario: {e}")
        
        # 3. Obtener macros de la comida actual
        current_meal_macros = state.get("calculated_macros", {})
        if not current_meal_macros:
            # Si no hay macros calculados aún, usar valores por defecto
            current_meal_macros = {"calories": 500, "protein": 25, "carbs": 60, "fat": 20}
        
        # 4. Obtener ingredientes de la comida actual
        ingredients = state.get("extracted_ingredients", [])
        
        # 5. Llamar al agente de compatibilidad
        compatibility_chain = get_compatibility_agent_chain()
        compatibility_result = compatibility_chain.invoke({
            "user_targets": user_targets,
            "daily_consumption": daily_consumption,
            "current_meal_macros": current_meal_macros,
            "ingredients": ingredients,
            "user_name": user_name,
            "recent_foods": recent_foods
        })
        
        # 6. Generar audio TTS si está habilitado para el usuario
        audio_url = None
        try:
            # Verificar si el usuario tiene habilitado el audio
            profiles_result = supabase_client.supabase.table("profiles").select(
                "audios"
            ).eq("id", user_id).execute()
            
            if profiles_result.data and len(profiles_result.data) > 0:
                audios_enabled = profiles_result.data[0].get("audios", False)
                
                if audios_enabled:
                    audio_url = generate_tts_audio(compatibility_result.agent_observation, user_id)
                    logger.info(f"Audio TTS generado: {audio_url}")
                else:
                    logger.info("Usuario no tiene habilitado el audio TTS")
            else:
                logger.info("No se encontró perfil del usuario para verificar configuración de audio")
        except Exception as e:
            logger.error(f"Error generando audio TTS: {e}")
        
        # Guardar datos en el estado para usar en el nodo de inserción
        return {
            "compatibility_result": {
                "compatibility": compatibility_result.compatibility,
                "agent_observation": compatibility_result.agent_observation
            },
            "user_targets": user_targets,
            "daily_consumption": daily_consumption,
            "audio_url": audio_url,
            "current_step": "compatibility_analyzed"
        }
        
    except Exception as e:
        logger.error(f"Error analizando compatibilidad nutricional: {e}")
        return {
            "compatibility_result": {
                "compatibility": "5",
                "agent_observation": "No se pudo evaluar la compatibilidad debido a un error técnico."
            },
            "current_step": "compatibility_error",
            "error": f"Error en análisis de compatibilidad: {str(e)}"
        }

def generate_tts_audio(text: str, user_id: str) -> str:
    """Genera audio TTS usando OpenAI y lo sube a Supabase"""
    try:
        client = OpenAI(api_key=get_openai_api_key())
        
        # Generar audio
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        
        # Crear nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compatibility_audio_{user_id}_{timestamp}.mp3"
        
        # Subir a Supabase Storage
        supabase_client = SupabaseClient()
        
        # Subir archivo al bucket
        upload_result = supabase_client.supabase.storage.from_("audios").upload(
            filename, 
            response.content,
            file_options={"content-type": "audio/mpeg"}
        )
        
        logger.info(f"Upload result: {upload_result}")
        
        # Obtener URL pública del archivo (asumimos que se subió correctamente si no hay excepción)
        public_url = supabase_client.supabase.storage.from_("audios").get_public_url(filename)
        
        logger.info(f"Audio TTS generado y subido exitosamente: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Error generando audio TTS: {e}")
        return None