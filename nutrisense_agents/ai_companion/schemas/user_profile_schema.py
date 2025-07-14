from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserProfileInputSchema(BaseModel):
    user_id: str
    age: int
    gender: str
    weight: float
    height: int
    activity_level: str
    goal: str
    preferences: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    medical_conditions: Optional[List[str]] = []

    breakfast: Optional[str] = None
    lunch: Optional[str] = None
    snack: Optional[str] = None
    dinner: Optional[str] = None

    work_mode: Optional[str] = None
    shift_type: Optional[str] = None
    lunch_place: Optional[str] = None

    who_cooks: Optional[str] = None
    who_shops: Optional[str] = None
    cook_for_others: Optional[bool] = None

    weekend_diff: Optional[str] = None

    cooking_frequency: Optional[str] = None
    cooking_time: Optional[str] = None
    cooking_likes: Optional[str] = None
    ultraprocessed_frequency: Optional[str] = None

    weight_history: Optional[str] = None
    weight_changes: Optional[str] = None
    weight_events: Optional[str] = None

    current_difficulties: Optional[str] = None
    emotional_eating: Optional[bool] = None
    snacking: Optional[bool] = None
    alcohol_intake: Optional[bool] = None

    daily_calories_target: Optional[int] = None
    daily_protein_target: Optional[float] = None
    daily_carbs_target: Optional[float] = None
    daily_fat_target: Optional[float] = None
    weight_target: Optional[float] = None


class MealGuideline(BaseModel):
    """Directrices generales para cada comida"""
    recommended_proteins: List[str] = Field(..., description="Tipos de proteínas recomendadas (categorías generales)")
    recommended_carbs: List[str] = Field(..., description="Tipos de carbohidratos recomendados (categorías generales)")
    recommended_vegetables: Optional[List[str]] = Field(default=None, description="Tipos de vegetales recomendados")
    recommended_fruits: Optional[List[str]] = Field(default=None, description="Tipos de frutas recomendadas")
    recommended_fats: Optional[List[str]] = Field(default=None, description="Tipos de grasas saludables recomendadas")
    portion_guidelines: str = Field(..., description="Guías generales de porciones para esta comida")
    meal_timing: Optional[str] = Field(default=None, description="Recomendaciones sobre horarios para esta comida")
    preparation_tips: List[str] = Field(..., description="Tips generales de preparación para esta comida")


class LifestyleFactors(BaseModel):
    """Factores del estilo de vida que influyen en la alimentación"""
    work_schedule: Optional[str] = Field(default=None, description="Horarios de trabajo y su impacto")
    cooking_availability: Optional[str] = Field(default=None, description="Disponibilidad y habilidad para cocinar")
    meal_organization: Optional[str] = Field(default=None, description="Organización de comidas y compras")
    social_eating: Optional[str] = Field(default=None, description="Contexto social de las comidas")
    weekend_patterns: Optional[str] = Field(default=None, description="Diferencias en patrones de fin de semana")


class DietaryConsiderations(BaseModel):
    """Consideraciones dietéticas específicas"""
    allergies_impact: Optional[str] = Field(default=None, description="Cómo las alergias afectan las elecciones alimentarias")
    preferences_integration: Optional[str] = Field(default=None, description="Cómo integrar las preferencias en el plan")
    medical_adaptations: Optional[str] = Field(default=None, description="Adaptaciones necesarias por condiciones médicas")
    emotional_eating_strategies: Optional[str] = Field(default=None, description="Estrategias para el manejo del comer emocional")


class GeneralRecommendations(BaseModel):
    """Recomendaciones generales para organización y éxito"""
    meal_prep_suggestions: List[str] = Field(..., description="Sugerencias para preparación de comidas")
    shopping_tips: List[str] = Field(..., description="Tips para hacer compras eficientes")
    time_management: List[str] = Field(..., description="Manejo del tiempo en la cocina")
    habit_building: List[str] = Field(..., description="Estrategias para crear hábitos sostenibles")
    progress_tracking: List[str] = Field(..., description="Cómo monitorear el progreso")


class NutritionTargetSchema(BaseModel):
    """Objetivos nutricionales calculados"""
    calories: int = Field(description="Objetivo diario de calorías")
    protein: int = Field(description="Objetivo diario de proteínas en gramos")
    carbs: int = Field(description="Objetivo diario de carbohidratos en gramos")
    grasas: int = Field(description="Objetivo diario de grasas en gramos")


class UserNutritionProfileSchema(BaseModel):
    """Schema principal de la ficha de usuario"""
    profile_name: str = Field(..., description="Nombre descriptivo del perfil")
    user_summary: str = Field(..., description="Resumen personalizado del usuario y sus objetivos")
    
    # Objetivos nutricionales
    nutrition_targets: NutritionTargetSchema = Field(..., description="Objetivos nutricionales calculados")
    
    # Directrices por comidas
    breakfast_guidelines: MealGuideline = Field(..., description="Directrices para el desayuno")
    lunch_guidelines: MealGuideline = Field(..., description="Directrices para el almuerzo")
    snack_guidelines: MealGuideline = Field(..., description="Directrices para la merienda")
    dinner_guidelines: MealGuideline = Field(..., description="Directrices para la cena")
    
    # Colaciones opcionales
    optional_snacks: List[str] = Field(..., description="Opciones de colaciones saludables entre comidas")
    
    # Contexto del estilo de vida
    lifestyle_factors: LifestyleFactors = Field(..., description="Factores del estilo de vida")
    
    # Consideraciones dietéticas
    dietary_considerations: DietaryConsiderations = Field(..., description="Consideraciones dietéticas específicas")
    
    # Recomendaciones generales
    general_recommendations: GeneralRecommendations = Field(..., description="Recomendaciones generales")
    
    # Notas adicionales
    special_notes: Optional[str] = Field(default=None, description="Notas especiales o consideraciones adicionales")


class ProfileSummarySchema(BaseModel):
    """Schema para el resumen conversacional del perfil"""
    summary: str = Field(description="Resumen conversacional del perfil nutricional en formato de guión")