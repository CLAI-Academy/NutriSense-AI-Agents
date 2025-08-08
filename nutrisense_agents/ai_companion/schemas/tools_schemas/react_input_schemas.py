from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class RecipeIngredient(BaseModel):
    name: str
    quantity: float
    unit: str

class RecipeInput(BaseModel):
    name: str
    description: str
    instructions: str
    meal_type: str
    ingredients: List[RecipeIngredient]

class RecipeList(BaseModel):
    recipes: List[RecipeInput]

class MealPlanInput(BaseModel):
    week_start_date: date = Field(description="Fecha de inicio de la semana (lunes)")
    target_calories_per_day: Optional[int] = Field(default=2000, description="Calorías objetivo por día")
    dietary_preferences: Optional[List[str]] = Field(default=[], description="Preferencias dietéticas")
    meals_per_day: Optional[int] = Field(default=3, description="Número de comidas por día")

class PlannedMealInput(BaseModel):
    meal_plan_id: str = Field(description="ID del plan de comidas")
    recipes: List[RecipeInput] = Field(description="Lista de recetas a planificar")
    auto_schedule: Optional[bool] = Field(default=True, description="Programar automáticamente en la semana")

class OptimizeMealPlanInput(BaseModel):
    meal_plan_id: str = Field(description="ID del plan de comidas a optimizar")

class MealPlanSummaryInput(BaseModel):
    meal_plan_id: str = Field(description="ID del plan de comidas para obtener resumen")

class UserDataInput(BaseModel):
    table_name: str = Field(description="Nombre de la tabla a consultar")
    extra_filters: Optional[dict] = Field(default=None, description="Filtros adicionales a aplicar")
    limit: Optional[int] = Field(default=None, description="Límite de resultados a retornar")

class ShoppingListInput(BaseModel):
    recipe_ids: list[int]