from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class MacronutrientExtraction(BaseModel):
    """Schema para la extracción de macronutrientes de ingredientes"""
    
    # Información básica del alimento
    name: str = Field(description="Nombre del alimento/ingrediente principal")
    description: Optional[str] = Field(description="Descripción del alimento", default=None)
    brand: Optional[str] = Field(description="Marca del producto si aplica", default=None)
    
    # Macronutrientes por 100g
    calories_per_100g: float = Field(description="Calorías por 100 gramos")
    protein_per_100g: float = Field(description="Proteínas en gramos por 100g")
    carbs_per_100g: float = Field(description="Carbohidratos en gramos por 100g")
    fat_per_100g: float = Field(description="Grasas en gramos por 100g")
    fiber_per_100g: Optional[float] = Field(description="Fibra en gramos por 100g", default=None)
    sugar_per_100g: Optional[float] = Field(description="Azúcares en gramos por 100g", default=None)
    sodium_per_100g: Optional[float] = Field(description="Sodio en miligramos por 100g", default=None)
    
    # Cantidad estimada consumida
    estimated_quantity_grams: float = Field(description="Cantidad estimada consumida en gramos")
    
    # Macronutrientes totales consumidos
    total_calories: float = Field(description="Calorías totales consumidas")
    total_protein: float = Field(description="Proteínas totales consumidas en gramos")
    total_carbs: float = Field(description="Carbohidratos totales consumidos en gramos")
    total_fat: float = Field(description="Grasas totales consumidas en gramos")
    total_fiber: Optional[float] = Field(description="Fibra total consumida en gramos", default=None)
    total_sugar: Optional[float] = Field(description="Azúcares totales consumidos en gramos", default=None)
    total_sodium: Optional[float] = Field(description="Sodio total consumido en miligramos", default=None)
    
    # Información adicional
    category: Optional[str] = Field(description="Categoría del alimento (fruta, verdura, proteína, etc.)", default=None)
    preparation_method: Optional[str] = Field(description="Método de preparación si es relevante", default=None)
    confidence_score: float = Field(description="Nivel de confianza en la extracción (0.0 a 1.0)", default=0.8)

class FoodDiaryEntry(BaseModel):
    """Schema para entrada en el diario alimentario"""
    
    user_id: str = Field(description="ID del usuario")
    meal_type: str = Field(description="Tipo de comida (desayuno, almuerzo, cena, snack)")
    consumed_at: datetime = Field(description="Fecha y hora de consumo")
    
    # Totales de la comida completa
    total_calories: float = Field(description="Calorías totales de la comida")
    total_protein: float = Field(description="Proteínas totales en gramos")
    total_carbs: float = Field(description="Carbohidratos totales en gramos")
    total_fat: float = Field(description="Grasas totales en gramos")
    total_fiber: Optional[float] = Field(description="Fibra total en gramos", default=None)
    total_sugar: Optional[float] = Field(description="Azúcares totales en gramos", default=None)
    total_sodium: Optional[float] = Field(description="Sodio total en miligramos", default=None)
    
    notes: Optional[str] = Field(description="Notas adicionales", default=None)

class FoodPhotoAnalysis(BaseModel):
    """Schema para análisis de foto de comida"""
    
    food_diary_id: str = Field(description="ID de la entrada del diario alimentario")
    photo_url: str = Field(description="URL de la foto analizada")
    analysis_confidence: float = Field(description="Confianza en el análisis de la foto")
    detected_foods: List[str] = Field(description="Lista de alimentos detectados en la foto")
    analysis_notes: Optional[str] = Field(description="Notas del análisis", default=None)
