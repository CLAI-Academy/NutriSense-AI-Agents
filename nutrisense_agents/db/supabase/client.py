from typing import Any, Dict
from uuid import UUID
from nutrisense_agents.config.settings import settings
from supabase import create_client, Client
import uuid
import logging

logger = logging.getLogger(__name__)

def get_supabase_client():
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        print("Warning: Supabase URL or Service Role Key not configured")
        return None

    try:
        client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
        return client
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None

class SupabaseClient:
    def __init__(self):
        try:
            self.supabase: Client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    def refresh_schema_cache(self):
        try:
            self.supabase.table("food_diary").select("id").limit(1).execute()
            logger.info("✅ Schema cache refrescado exitosamente")
            return True
        except Exception as e:
            logger.error(f"❌ Error refrescando schema cache: {e}")
            return False

    def verify_food_diary_schema(self):
        try:
            result = self.supabase.rpc('get_table_columns', {
                'table_name': 'food_diary'
            }).execute()
            logger.info(f"🔍 Columnas disponibles en food_diary: {result.data}")
            return result.data
        except Exception as e:
            logger.warning(f"⚠️ No se pudo verificar esquema (esto es normal): {e}")
            return None

    def _update_health_profile(self, user_id: UUID, **fields) -> Dict[str, Any]:
        try:
            # First, check if the profile exists
            existing_profile = (
                self.supabase
                .table("user_health_profile")
                .select("user_id")
                .eq("user_id", str(user_id))
                .execute()
            )
            
            if existing_profile.data and len(existing_profile.data) > 0:
                # Profile exists, update it
                update = (
                    self.supabase
                    .table("user_health_profile")
                    .update(fields)
                    .eq("user_id", str(user_id))
                    .execute()
                )
                logger.info(f"Health profile updated for user {user_id}")
                return {"message": "Actualizado", "operation": "update"}
            else:
                # Profile doesn't exist, create it
                fields["user_id"] = str(user_id)
                insert = (
                    self.supabase
                    .table("user_health_profile")
                    .insert(fields)
                    .execute()
                )
                logger.info(f"Health profile created for user {user_id}")
                return {"message": "Creado", "operation": "insert"}
                
        except Exception as e:
            logger.error(f"Error in _update_health_profile: {str(e)}")
            return {"error": str(e)}

    def add_summary_to_user_health_profile(self, user_id: UUID, summary: str) -> Dict[str, Any]:
        return self._update_health_profile(user_id, summary=summary)

    def add_nutritional_plan_to_user_health_profile(self, user_id: str, markdown: str, recipes: list) -> Dict[str, Any]:
        return self._update_health_profile(user_id, nutritional_plan=markdown, recommended_recipes=recipes)
    
    def update_complete_health_profile(self, user_id: str, health_profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza el perfil completo de salud del usuario con todos los campos
        """
        return self._update_health_profile(UUID(user_id), **health_profile_data)

    def add_food_diary(self, user_id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        food_diary_data = {
            "id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "date": data.get("date", ""),
            "meal_type": data.get("meal_type", ""),
            "recipe_id": data.get("recipe_id"),
            "food_name": data.get("food_name", ""),
            "quantity": data.get("quantity", 0),
            "unit": data.get("unit", ""),
            "calories": data.get("calories", 0),
            "protein": data.get("protein", 0),
            "carbs": data.get("carbs", 0),
            "fat": data.get("fat", 0),
            "fiber": data.get("fiber", 0),
            "notes": data.get("notes", ""),
            "consumed_at": data.get("consumed_at", ""),
            "location_type": data.get("location_type", "unknown"),
            "time_since_last_meal": data.get("time_since_last_meal"),
            "day_type": data.get("day_type", "weekday"),
            "eating_context": data.get("eating_context"),
            "image_url": data.get("image_url"),
            "mood_emoji": data.get("mood_emoji"),
            "created_at": data.get("created_at", ""),
        }

        food_diary_data = {k: v for k, v in food_diary_data.items() if v is not None}
        logger.info(f"🔍 Insertando en food_diary: {list(food_diary_data.keys())}")

        try:
            result = self.supabase.table("food_diary").insert(food_diary_data).execute()
            logger.info("✅ Inserción exitosa en food_diary")
            return result
        except Exception as e:
            logger.error(f"❌ Error insertando en food_diary: {e}")
            logger.info("🔄 Intentando refresh de schema y reintento...")
            self.refresh_schema_cache()

            try:
                result = self.supabase.table("food_diary").insert(food_diary_data).execute()
                logger.info("✅ Inserción exitosa después de refresh")
                return result
            except Exception as retry_error:
                logger.error(f"❌ Error persiste después de refresh: {retry_error}")
                raise retry_error
