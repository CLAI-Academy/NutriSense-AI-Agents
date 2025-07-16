from typing import Dict, Any
from nutrisense_agents.ai_companion.graphs.nutrition_plan_graph.state import UserProfileState
from nutrisense_agents.ai_companion.agents.user_profile_agent import nutrition_target_agent, get_user_profile_agent_chain, get_profile_summary_agent
from nutrisense_agents.ai_companion.schemas.user_profile_schema import NutritionTargetSchema, UserProfileSheet
from nutrisense_agents.db.supabase.client import SupabaseClient
import logging

logger = logging.getLogger(__name__)

def calculate_nutrition_targets(state: UserProfileState) -> Dict[str, Any]:
    """
    Primer nodo: Calcula objetivos nutricionales usando nutrition_target_agent
    """
    try:
        # Crear el agente para calcular objetivos nutricionales
        nutrition_target_chain = nutrition_target_agent()
        
        # Preparar datos de entrada para el agente
        user_data = {
            "age": state["age"],
            "gender": state["gender"],
            "weight": state["weight"],
            "height": state["height"],
            "activity_level": state["activity_level"],
            "goal": state["goal"],
            "preferences": state.get("preferences", []),
            "allergies": state.get("allergies", []),
            "medical_conditions": state.get("medical_conditions", []),
            "breakfast": state.get("breakfast"),
            "lunch": state.get("lunch"),
            "snack": state.get("snack"),
            "dinner": state.get("dinner"),
            "work_mode": state.get("work_mode"),
            "shift_type": state.get("shift_type"),
            "lunch_place": state.get("lunch_place"),
            "who_cooks": state.get("who_cooks"),
            "who_shops": state.get("who_shops"),
            "cook_for_others": state.get("cook_for_others"),
            "weekend_diff": state.get("weekend_diff"),
            "cooking_frequency": state.get("cooking_frequency"),
            "cooking_time": state.get("cooking_time"),
            "cooking_likes": state.get("cooking_likes"),
            "ultraprocessed_frequency": state.get("ultraprocessed_frequency"),
            "weight_history": state.get("weight_history"),
            "weight_changes": state.get("weight_changes"),
            "weight_events": state.get("weight_events"),
            "current_difficulties": state.get("current_difficulties"),
            "emotional_eating": state.get("emotional_eating"),
            "snacking": state.get("snacking"),
            "alcohol_intake": state.get("alcohol_intake")
        }
        
        # Invocar el agente para calcular objetivos
        result = nutrition_target_chain.invoke(user_data)
        
        # Extraer los objetivos nutricionales calculados o usar valores por defecto
        targets = NutritionTargetSchema(
            calories=getattr(result, 'calories', 2000),
            protein=getattr(result, 'protein', 150),
            carbs=getattr(result, 'carbs', 200),
            grasas=getattr(result, 'grasas', 70)
        )
        
        logger.info(f"Objetivos nutricionales calculados: {targets}")
        
        return {
            "nutrition_targets": targets
        }
        
    except Exception as e:
        logger.error(f"Error calculando objetivos nutricionales: {str(e)}")
        return {
            "error": f"Error calculando objetivos nutricionales: {str(e)}"
        }

def calculate_basic_targets(user_data: Dict[str, Any]) -> NutritionTargetSchema:
    """
    Función auxiliar para calcular objetivos nutricionales básicos
    basados en datos del usuario cuando el agente no los proporciona directamente
    """
    # Cálculos básicos de TMB y necesidades calóricas
    age = user_data["age"]
    weight = user_data["weight"]
    height = user_data["height"]
    gender = user_data["gender"].lower()
    activity_level = user_data["activity_level"].lower()
    goal = user_data["goal"].lower()
    
    # Calcular TMB usando fórmula de Harris-Benedict
    if gender == "male" or gender == "masculino" or gender == "hombre":
        tmb = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        tmb = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    # Factor de actividad
    activity_factors = {
        "sedentario": 1.2,
        "ligero": 1.375,
        "moderado": 1.55,
        "intenso": 1.725,
        "muy intenso": 1.9
    }
    
    activity_factor = activity_factors.get(activity_level, 1.55)
    maintenance_calories = int(tmb * activity_factor)
    
    # Ajustar calorías según objetivo
    if "perder" in goal or "bajar" in goal:
        target_calories = int(maintenance_calories * 0.8)  # Déficit del 20%
    elif "ganar" in goal or "subir" in goal:
        target_calories = int(maintenance_calories * 1.1)  # Superávit del 10%
    else:
        target_calories = maintenance_calories
    
    # Calcular macronutrientes
    protein = int(weight * 1.6)  # 1.6g por kg de peso corporal
    fat = int(target_calories * 0.25 / 9)  # 25% de calorías de grasa
    carbs = int((target_calories - (protein * 4) - (fat * 9)) / 4)  # Resto en carbohidratos
    
    return NutritionTargetSchema(
        calories=target_calories,
        protein=protein,
        carbs=carbs,
        grasas=fat
    )

def generate_user_profile(state: UserProfileState) -> Dict[str, Any]:
    """
    Segundo nodo: Genera el perfil nutricional con directrices generales usando los objetivos calculados
    """
    try:
        # Obtener el agente para generar el perfil
        user_profile_chain = get_user_profile_agent_chain()
        
        # Preparar datos incluyendo los objetivos calculados
        user_data = {
            "age": state["age"],
            "gender": state["gender"],
            "weight": state["weight"],
            "height": state["height"],
            "activity_level": state["activity_level"],
            "goal": state["goal"],
            "preferences": state.get("preferences", []),
            "allergies": state.get("allergies", []),
            "medical_conditions": state.get("medical_conditions", []),
            "breakfast": state.get("breakfast"),
            "lunch": state.get("lunch"),
            "snack": state.get("snack"),
            "dinner": state.get("dinner"),
            "work_mode": state.get("work_mode"),
            "shift_type": state.get("shift_type"),
            "lunch_place": state.get("lunch_place"),
            "who_cooks": state.get("who_cooks"),
            "who_shops": state.get("who_shops"),
            "cook_for_others": state.get("cook_for_others"),
            "weekend_diff": state.get("weekend_diff"),
            "cooking_frequency": state.get("cooking_frequency"),
            "cooking_time": state.get("cooking_time"),
            "cooking_likes": state.get("cooking_likes"),
            "ultraprocessed_frequency": state.get("ultraprocessed_frequency"),
            "weight_history": state.get("weight_history"),
            "weight_changes": state.get("weight_changes"),
            "weight_events": state.get("weight_events"),
            "current_difficulties": state.get("current_difficulties"),
            "emotional_eating": state.get("emotional_eating"),
            "snacking": state.get("snacking"),
            "alcohol_intake": state.get("alcohol_intake"),
            # Incluir los objetivos calculados en el paso anterior
            "daily_calories_target": state["nutrition_targets"].calories,
            "daily_protein_target": state["nutrition_targets"].protein,
            "daily_carbs_target": state["nutrition_targets"].carbs,
            "daily_fat_target": state["nutrition_targets"].grasas,
            "weight_target": state.get("weight_target")
        }
        
        # Generar el perfil nutricional
        result = user_profile_chain.invoke(user_data)
        
        logger.info(f"Perfil nutricional generado: {result.profile_name}")
        
        return {
            "user_profile": result
        }
        
    except Exception as e:
        logger.error(f"Error generando perfil nutricional: {str(e)}")
        return {
            "error": f"Error generando perfil nutricional: {str(e)}"
        }

    
def generate_summary(state: UserProfileState) -> Dict[str, Any]:
    """
    Tercer nodo: Genera resumen conversacional del perfil nutricional
    """
    try:
        # Obtener el agente de resumen
        summary_agent = get_profile_summary_agent()
        
        # Preparar datos para el agente de resumen
        summary_data = {
            "age": state["age"],
            "gender": state["gender"],
            "weight": state["weight"],
            "height": state["height"],
            "goal": state["goal"],
            "activity_level": state["activity_level"],
            "preferences": state.get("preferences", []),
            "allergies": state.get("allergies", []),
            "medical_conditions": state.get("medical_conditions", []),
            "breakfast": state.get("breakfast"),
            "lunch": state.get("lunch"),
            "snack": state.get("snack"),
            "dinner": state.get("dinner"),
            "work_mode": state.get("work_mode"),
            "shift_type": state.get("shift_type"),
            "who_cooks": state.get("who_cooks"),
            "cooking_frequency": state.get("cooking_frequency"),
            "cooking_time": state.get("cooking_time"),
            "ultraprocessed_frequency": state.get("ultraprocessed_frequency"),
            "current_difficulties": state.get("current_difficulties"),
            "emotional_eating": state.get("emotional_eating"),
            "snacking": state.get("snacking"),
            "daily_calories_target": state["nutrition_targets"].calories,
            "daily_protein_target": state["nutrition_targets"].protein,
            "daily_carbs_target": state["nutrition_targets"].carbs,
            "daily_fat_target": state["nutrition_targets"].grasas,
            "weight_target": state.get("weight_target"),
            "user_profile_summary": state["user_profile"].user_summary if state["user_profile"] else ""
        }
        
        # Generar el resumen conversacional
        result = summary_agent.invoke(summary_data)
        
        logger.info(f"Resumen conversacional generado exitosamente")
        
        return {
            "summary": result.summary
        }
        
    except Exception as e:
        logger.error(f"Error generando resumen: {str(e)}")
        return {
            "error": f"Error generando resumen: {str(e)}"
        }

def save_to_database(state: UserProfileState) -> Dict[str, Any]:
    """
    Cuarto nodo: Prepara los datos y guarda el perfil nutricional completo en user_health_profile
    """
    print("🔍 DEBUG: ===== INICIO save_to_database =====")
    try:
        supabase_client = SupabaseClient()
        
        # Preparar datos del perfil
        user_profile = state["user_profile"]
        
        # Convertir el perfil completo a JSON para preservar toda la estructura del schema
        user_profile_json = user_profile.model_dump() if user_profile else {}
        
        logger.info(f"Datos del perfil preparados - {user_profile.profile_name}")
        logger.info(f"�� DEBUG: user_id del estado: {state['user_id']}")
        
        # Preparar datos completos para user_health_profile (sin user_id en el dict)
        health_profile_data = {
            "dietary_preferences": state.get("preferences", []),
            "health_goals": [state["goal"]] if state.get("goal") else [],
            "allergies": state.get("allergies", []),
            "medical_conditions": state.get("medical_conditions", []),
            "daily_calories_target": state["nutrition_targets"].calories,
            "daily_protein_target": state["nutrition_targets"].protein,
            "daily_carbs_target": state["nutrition_targets"].carbs,
            "daily_fat_target": state["nutrition_targets"].grasas,
            "weight_target": state.get("weight_target"),
            "cooking_lifestyle": generate_cooking_lifestyle_summary(state),
            "summary": state["summary"],  # Usar el resumen conversacional generado
            "user_nutrition_profile": user_profile_json  # Guardar como JSON completo
        }
        logger.info(f"🔍 DEBUG: Datos de health_profile preparados: {list(health_profile_data.keys())}")
        
        # Guardar el perfil completo en la base de datos
        response = supabase_client.update_complete_health_profile(
            user_id=state["user_id"],
            health_profile_data=health_profile_data
        )
        
        if response.get("error"):
            return {
                "success": False,
                "error": f"Error guardando en base de datos: {response['error']}",
                "db_response": response
            }
        
        logger.info(f"Perfil nutricional y perfil de salud guardado exitosamente para usuario {state['user_id']}")
        
        return {
            "success": True,
            "db_response": response,
            "health_profile_data": health_profile_data,
            "user_profile_json": user_profile_json
        }
        
    except Exception as e:
        logger.error(f"Error guardando en base de datos: {str(e)}")
        return {
            "success": False,
            "error": f"Error guardando en base de datos: {str(e)}"
        }


def generate_cooking_lifestyle_summary(state: UserProfileState) -> str:
    """
    Genera un resumen del estilo de vida culinario del usuario
    """
    lifestyle_parts = []
    
    if state.get("work_mode"):
        lifestyle_parts.append(f"Modalidad laboral: {state['work_mode']}")
    
    if state.get("who_cooks"):
        lifestyle_parts.append(f"Cocina: {state['who_cooks']}")
    
    if state.get("cooking_frequency"):
        lifestyle_parts.append(f"Frecuencia de cocina: {state['cooking_frequency']}")
    
    if state.get("cooking_time"):
        lifestyle_parts.append(f"Tiempo disponible: {state['cooking_time']}")
    
    if state.get("ultraprocessed_frequency"):
        lifestyle_parts.append(f"Ultraprocesados: {state['ultraprocessed_frequency']}")
    
    return " | ".join(lifestyle_parts) if lifestyle_parts else "No especificado"