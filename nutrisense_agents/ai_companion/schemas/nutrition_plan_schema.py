from pydantic import BaseModel, Field
from typing import Optional, List

class NutritionPlanInputSchema(BaseModel):

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


class MealGroup(BaseModel):
    proteinas: List[str] = Field(..., description="Opciones de alimentos ricos en proteínas")
    hidratos: List[str] = Field(..., description="Opciones de alimentos con carbohidratos")
    vegetales: Optional[List[str]] = Field(default=None, description="Opciones de vegetales (cuando aplique)")
    frutas_opcional: Optional[List[str]] = Field(default=None, description="Frutas para agregar opcionalmente")
    grasas_opcional: Optional[List[str]] = Field(default=None, description="Grasas saludables que se pueden incluir")
    ejemplos: List[str] = Field(..., description="Ejemplos de combinaciones prácticas para esta comida")


class DailyMeals(BaseModel):
    desayuno: MealGroup = Field(..., description="Opciones y combinaciones para el desayuno")
    almuerzo: MealGroup = Field(..., description="Opciones y combinaciones para el almuerzo")
    merienda: MealGroup = Field(..., description="Opciones y combinaciones para la merienda")
    cena: MealGroup = Field(..., description="Opciones y combinaciones para la cena")
    colaciones_opcionales: List[str] = Field(..., description="Snacks recomendados entre comidas o post entrenamiento")


class RecomendedRecipes(BaseModel):
    name: str = Field(..., description="Nombre de la receta")
    ingredients: List[str] = Field(..., description="Lista de ingredientes necesarios")
    instructions: str = Field(..., description="Pasos para preparar la receta")
    calories_per_serving: int = Field(..., description="Calorías por porción")
    protein_per_serving: float = Field(..., description="Proteínas por porción (en gramos)")
    carbs_per_serving: float = Field(..., description="Hidratos por porción (en gramos)")
    fat_per_serving: float = Field(..., description="Grasas por porción (en gramos)")
    prep_time: int = Field(..., description="Tiempo de preparación (en minutos)")
    cook_time: int = Field(..., description="Tiempo de cocción (en minutos)")
    servings: int = Field(..., description="Cantidad de porciones que rinde la receta")


class NutritionPlanSchema(BaseModel):
    name: str = Field(default=None, description="Título opcional del plan")
    description: str = Field(default=None, description="Descripción opcional del plan, hablando con el nombre del usuario, y siempre con una frase personalizada que describa el objetivo del plan, por Ej:(Bienvenido a tu plan nutricional de Nutrisense, Alejandro, tu objetivo es perder peso, por lo que hemos diseñado un plan para que puedas alcanzarlo)")
    plan: DailyMeals = Field(..., description="Plan de alimentación organizado por momentos del día")
    recipes: List[RecomendedRecipes] = Field(..., description="Lista de recetas recomendadas incluidas en el plan")

class NutritionTargetSchema(BaseModel):
    calories: int = Field(description="Objetivo diario de calorias, ej: 2000")
    protein: int = Field(description="Objetivo diario de proteinas, ej: 140")
    carbs: int = Field(description="Objetivo diario de carbohidratos, ej: 170")
    grasas: int = Field(description="Objetivo diario de grasas, ej: 50")

class SummarySchema(BaseModel):
    summary: str = Field(description="Resumen conversacional del plan nutricional en formato de guión, sin markdown ni formato especial")