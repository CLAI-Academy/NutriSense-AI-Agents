from typing import TypedDict, List, Optional, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass



@dataclass
class FoodDiaryEntry:
    """Entrada del diario de comidas"""
    id: Optional[str] = None
    user_id: str = ""
    date: str = ""
    meal_type: str = ""
    food_name: str = ""
    quantity: float = 0.0
    unit: str = ""
    calories: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0
    fiber: float = 0.0
    notes: Optional[str] = None
    consumed_at: Optional[str] = None
    created_at: Optional[str] = None


class RecipeState(TypedDict):
    """Estado principal del flujo de análisis de imagen y extracción de receta"""
    
    # Datos de entrada
    image_url: str
    user_id: Optional[str]
    user_notes: Optional[str]
    # Datos extraídos de la imagen
    extracted_ingredients: Optional[List[str]]
    recipe_name: Optional[str]
    ingredients_with_details: Optional[List[Dict[str, Any]]]  # Para almacenar detalles completos si es necesario
    
    # Datos de macronutrientes
    calculated_macros: Optional[Dict[str, float]]
    
    # Control de flujo
    current_step: Optional[str]
    
    # Resultados finales
    saved_food_diary_id: Optional[str]
    food_diary_data: Optional[Dict[str, Any]]
    
    # Control de errores
    success: Optional[bool]
    error: Optional[str]
    
    # Datos adicionales para procesamiento
    food_diary_entry: Optional[FoodDiaryEntry]
