from typing import TypedDict, List, Optional, Dict, Any, Union, Literal
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


class FoodAnalysisState(TypedDict):
    """Estado unificado para análisis de alimentos (imagen y texto)"""
    
    # Tipo de extracción (diferenciador principal)
    extraction_type: Literal["image", "text"]
    
    # Datos de entrada (condicionales según tipo)
    image_url: Optional[str]        # Solo para tipo "image"
    text_description: Optional[str] # Solo para tipo "text"
    user_notes: Optional[str]       # Para ambos tipos
    user_id: Optional[str]
    
    # Datos extraídos (comunes para ambos tipos)
    extracted_ingredients: Optional[List[str]]
    recipe_name: Optional[str]
    ingredients_with_details: Optional[List[Dict[str, Any]]]
    
    # Datos de macronutrientes
    calculated_macros: Optional[Dict[str, float]]
    
    # Datos de compatibilidad nutricional
    compatibility_result: Optional[Dict[str, Any]]
    user_targets: Optional[Dict[str, float]]
    daily_consumption: Optional[Dict[str, float]]
    
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
    
    # Datos de streak
    streak_updated: Optional[bool]
    current_streak: Optional[int]