from typing import Any, Dict
from uuid import UUID
from nutrisense_agents.config.settings import settings
from supabase import create_client, Client
import uuid

class SupabaseClient:
    """
    Cliente para interactuar con la base de datos Supabase
    """
    def __init__(self):
        """
        Inicializa el cliente de Supabase
        """
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )

    def _update_health_profile(self, user_id: UUID, **fields) -> Dict[str, Any]:
        update = (
            self.supabase
            .table("user_health_profile")
            .update(fields)
            .eq("user_id", str(user_id))
            .execute()
        )
        return {"message": "Actualizado"} if update.data else {"message": "Perfil no encontrado"}

    def add_summary_to_user_health_profile(self, user_id: UUID, summary: str) -> Dict[str, Any]:
        return self._update_health_profile(user_id, summary=summary)

    def add_nutritional_plan_to_user_health_profile(self, user_id: UUID, plan: str) -> Dict[str, Any]:
        return self._update_health_profile(user_id, nutritional_plan=plan)
    
    def add_food_diary(self, user_id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        food_diary_data = {
            "id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "date": data.get("date", ""),
            "meal_type": data.get("meal_type", ""),
            "recipe_id": str(data.get("recipe_id", "")),
            "food_name": data.get("food_name", ""),
            "quantity": data.get("quantity", 0),
            "unit": data.get("unit", ""),
            "calories": data.get("calories", 0),
            "protein": data.get("protein", 0),
            "carbs": data.get("carbs", 0),
            "fat": data.get("fat", 0),
            "fiber": data.get("fiber", 0),
            "notes": data.get("notes", ""),
            "sugar": data.get("sugar", 0),
            "consumed_at": data.get("consumed_at", ""),
            "location_type": data.get("location_type", ""),
            "time_since_last_meal": data.get("time_since_last_meal", 0),
            "day_type": data.get("day_type", ""),
            "eating_context": data.get("eating_context", ""),
            "mood_emoji": data.get("mood_emoji", ""),
            "created_at": data.get("created_at", ""),
        }
        return self.supabase.table("food_diary").insert(food_diary_data).execute()
    
