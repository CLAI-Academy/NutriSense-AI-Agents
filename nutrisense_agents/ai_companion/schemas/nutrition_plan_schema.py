from pydantic import BaseModel, Field
from typing import Optional

class NutritionPlanSchema(BaseModel):
    markdown: str = Field(description="Markdown formatted nutrition plan content")
    name: Optional[str] = Field(default=None, description="Título opcional del plan")
