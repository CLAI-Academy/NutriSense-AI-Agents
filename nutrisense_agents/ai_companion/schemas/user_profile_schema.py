from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class FoodPreference(BaseModel):
    food_name: str
    food_image: str
    liked: bool

class UserProfileInputSchema(BaseModel):
    user_id: str
    age: int
    gender: str = Field(..., description="Options: male|female|other")
    weight: float
    height: float
    activity_level: str = Field(..., description="Options: sedentary|light|moderate|active|very-active")
    goal: str = Field(..., description="Options: lose-weight|gain-weight|maintain|muscle-gain|health")
    preferences: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    medical_conditions: List[str] = Field(default_factory=list)

    breakfast: str = Field(default="")
    lunch: str = Field(default="")
    snack: str = Field(default="")
    dinner: str = Field(default="")

    work_mode: str = Field(..., description="Options: home|office|hybrid")
    shift_type: str = Field(..., description="Options: fixed|rotating")
    lunch_place: str = Field(..., description="Options: home|work|packed")

    who_cooks: str = Field(..., description="Options: me|partner|family|shared|none")
    who_shops: str = Field(..., description="Options: me|partner|family|shared|delivery")
    cook_for_others: str = Field(..., description="Options: myself|couple|family|varies")

    weekend_diff: str = Field(..., description="Options: maintain|flexible|different|disorganized")

    cooking_frequency: str = Field(..., description="Options: daily|weekly|rarely|never")
    cooking_time: str = Field(..., description="Options: very-little|some|enough")
    cooking_likes: str = Field(..., description="Options: love|like|neutral|dislike")
    ultraprocessed_frequency: str = Field(..., description="Options: never|rarely|weekly|frequent|daily")

    weight_history: str = Field(default="")
    weight_changes: str = Field(default="")
    weight_events: str = Field(default="")

    current_difficulties: str = Field(default="")
    emotional_eating: str = Field(..., description="Options: por_hambre|por_emocion")
    snacking: str = Field(..., description="Options: nunca|raramente|algunas_veces|frecuentemente|constantemente")
    alcohol_intake: str = Field(..., description="Options: never|rarely|weekly|regular|daily")

    weight_target: str = Field(default="")
    food_preferences: List[FoodPreference] = Field(default_factory=list)


class   NutritionTargetSchema(BaseModel):
    """Objetivos nutricionales calculados"""
    calories: int = Field(description="Objetivo diario de calorías")
    protein: int = Field(description="Objetivo diario de proteínas en gramos")
    carbs: int = Field(description="Objetivo diario de carbohidratos en gramos")
    grasas: int = Field(description="Objetivo diario de grasas en gramos")

    def dict(self, *args, **kwargs):
        return {
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "grasas": self.grasas
        }
        
    def __json__(self):
        return self.dict()

class UserProfileSheet(BaseModel):
    """Schema para la ficha informativa del usuario"""
    profile_name: str = Field(..., description="Nombre del perfil nutricional")
    user_summary : str = Field(..., description="Resumen conversacional del perfil nutricional en formato de guión")
    nombre: str = Field(..., description="Nombre del usuario")
    edad: int = Field(..., description="Edad del usuario")
    peso: float = Field(..., description="Peso actual en kg")
    altura: int = Field(..., description="Altura en cm")
    imc: float = Field(..., description="Índice de masa corporal")
    nivel_actividad: str = Field(..., description="Nivel de actividad física")
    objetivo_principal: str = Field(..., description="Objetivo principal del usuario")
    
    # Preferencias y restricciones unificadas
    preferencias_y_restricciones: str = Field(..., description="Descripción informativa de las preferencias alimentarias, alergias, intolerancias y condiciones médicas del usuario")
    
    # Hábitos y contexto de vida unificados
    habitos_y_contexto: str = Field(..., description="Descripción de los hábitos alimentarios del usuario, incluyendo comidas típicas, contexto laboral, organización de comidas y estilo de vida")
    
    # Objetivos nutricionales calculados
    objetivos_nutricionales: NutritionTargetSchema = Field(..., description="Objetivos nutricionales calculados")
    
    # Dificultades y observaciones generales
    dificultades_y_observaciones: str = Field(default="", description="Dificultades actuales reportadas y observaciones adicionales del análisis nutricional")


class ProfileSummarySchema(BaseModel):
    """Schema para el resumen conversacional del perfil"""
    summary: str = Field(description="Resumen conversacional del perfil nutricional en formato de guión")