from typing import TypedDict, List, Optional, Dict, Any
from nutrisense_agents.ai_companion.schemas.user_profile_schema import NutritionTargetSchema, UserProfileSheet


class UserProfileState(TypedDict):
    """Estado principal del flujo de generación de perfil nutricional"""
    
    # Datos de entrada del usuario
    user_id: str
    age: int
    gender: str
    weight: float
    height: int
    activity_level: str
    goal: str
    preferences: Optional[List[str]]
    allergies: Optional[List[str]]
    medical_conditions: Optional[List[str]]
    
    # Comidas actuales
    breakfast: Optional[str]
    lunch: Optional[str]
    snack: Optional[str]
    dinner: Optional[str]
    
    # Contexto laboral
    work_mode: Optional[str]
    shift_type: Optional[str]
    lunch_place: Optional[str]
    
    # Organización alimentaria
    who_cooks: Optional[str]
    who_shops: Optional[str]
    cook_for_others: Optional[bool]
    
    # Rutinas
    weekend_diff: Optional[str]
    
    # Habilidades culinarias
    cooking_frequency: Optional[str]
    cooking_time: Optional[str]
    cooking_likes: Optional[str]
    ultraprocessed_frequency: Optional[str]
    
    # Historia del peso
    weight_history: Optional[str]
    weight_changes: Optional[str]
    weight_events: Optional[str]
    
    # Hábitos alimentarios
    current_difficulties: Optional[str]
    emotional_eating: Optional[bool]
    snacking: Optional[bool]
    alcohol_intake: Optional[str]
    
    # Objetivos nutricionales calculados por el primer agente
    nutrition_targets: Optional[NutritionTargetSchema]
    
    # Perfil nutricional generado
    user_profile: Optional[UserProfileSheet]
    
    # Resumen conversacional generado
    summary: Optional[str]
    
    # Control de flujo
    success: Optional[bool]
    error: Optional[str]
    
    # Respuesta de la base de datos
    db_response: Optional[Dict[str, Any]]