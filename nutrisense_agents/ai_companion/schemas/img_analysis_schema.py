# nutrisense_agents/ai_companion/schemas/img_analysis_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DetectedIngredient(BaseModel):
    """Ingrediente detectado en la imagen"""
    name: str = Field(description="Nombre del ingrediente detectado")
    quantity_estimate: Optional[str] = Field(description="Estimación de cantidad (ej: '1 taza', '200g')", default=None)

class ImageAnalysisResult(BaseModel):
    """Resultado del análisis de imagen para extracción de ingredientes y nombrado de receta""" 
    # Información principal
    recipe_name: str = Field(description="Nombre descriptivo de la receta basado en los ingredientes detectados")
    ingredients: List[DetectedIngredient] = Field(description="Lista de ingredientes detectados en la imagen")
    
   