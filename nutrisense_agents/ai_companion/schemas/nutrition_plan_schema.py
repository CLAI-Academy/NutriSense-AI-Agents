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


class NutritionPlanSchema(BaseModel):
    markdown: str = Field(description="Markdown formatted nutrition plan content")
    name: Optional[str] = Field(default=None, description="Título opcional del plan")
