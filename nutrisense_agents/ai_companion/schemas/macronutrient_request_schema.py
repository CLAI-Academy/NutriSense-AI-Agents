from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class MacronutrientInputSchema(BaseModel):
    """Schema de entrada para la extracción de macronutrientes"""
    user_id: str
    ingredients: List[str] = Field(description="Lista de ingredientes a analizar")
    meal_type: str = Field(default="unknown", description="Tipo de comida (desayuno, almuerzo, cena, snack)")
    preparation_method: str = Field(default="unknown", description="Método de preparación")
    portion_size: str = Field(default="porción estándar", description="Tamaño de la porción")
    photo_url: Optional[str] = Field(default=None, description="URL de la foto de la comida (opcional)")
    additional_notes: str = Field(default="", description="Notas adicionales")

class MacronutrientResponseSchema(BaseModel):
    """Schema de respuesta para la extracción de macronutrientes"""
    success: bool
    message: str
    food_diary_id: Optional[str] = None
    photo_analysis_id: Optional[str] = None
    ingredient_ids: Optional[List[str]] = None
    extracted_macronutrients: Optional[List[Dict[str, Any]]] = None
    total_nutrition: Optional[Dict[str, float]] = None
    error: Optional[str] = None
