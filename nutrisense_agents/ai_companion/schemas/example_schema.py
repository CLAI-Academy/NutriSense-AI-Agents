from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class ExampleAgent(BaseModel):
    recipe: str = Field(description="Una receta")
    ingredients: List[str] = Field(description="Los ingredientes de la receta")
    instructions: str = Field(description="Las instrucciones de la receta")
    nutrition_info: str = Field(description="La información nutricional de la receta")
    calories: int = Field(description="Las calorías de la receta")
    protein: int = Field(description="La proteína de la receta")
    carbs: int = Field(description="Los carbohidratos de la receta")
    fat: int = Field(description="La grasa de la receta")

