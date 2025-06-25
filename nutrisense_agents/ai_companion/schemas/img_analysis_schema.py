# nutrisense_agents/ai_companion/schemas/img_analysis_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DetectedIngredient(BaseModel):
    """Ingrediente detectado en la imagen"""
    name: str = Field(description="Nombre del ingrediente detectado y cantidad aproximada<example>1 taza de arroz</example><example>100g de pollo</example><example>2 Hot Dogs</example>")

class ImageAnalysisResult(BaseModel):
    """Resultado del análisis de imagen para extracción de ingredientes y nombrado de receta""" 
    # Información principal
    recipe_name: str = Field(description="Nombre descriptivo de la receta basado en los ingredientes detectados")
    ingredients: List[DetectedIngredient] = Field(description="Lista de ingredientes detectados en la imagen")
    
   