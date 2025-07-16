from typing import Any, Dict
from uuid import UUID
from nutrisense_agents.config.settings import settings
from supabase import create_client, Client
import uuid
import logging
from datetime import date, datetime

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
        print("🔍 DEBUG: ===== INICIO _update_health_profile =====", list(fields.keys()))
        try:
            logger.info(f"🔍 DEBUG: Iniciando _update_health_profile para user_id: {user_id}")
            logger.info(f"🔍 DEBUG: Campos recibidos: {list(fields.keys())}")

            # First, check if the profile exists
            existing_profile = (
                self.supabase
                .table("user_health_profile")
                .select("user_id")
                .eq("user_id", str(user_id))
                .execute()
            )
            logger.info(f"🔍 DEBUG: Perfil existente encontrado: {len(existing_profile.data) if existing_profile.data else 0}")
        
            if existing_profile.data and len(existing_profile.data) > 0:
                # Profile exists, update it
                logger.info(f"🔍 DEBUG: Actualizando perfil existente para user_id: {user_id}")
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
            "compatibility": data.get("compatibility"),
            "agent_observation": data.get("agent_observation"),
            "audio_url": data.get("audio_url"),
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

    def check_and_update_user_streak(self, user_id: str) -> Dict[str, Any]:
        """
        Extrae datos de user_streak. Si updated_at es igual a la fecha de hoy, no hace nada.
        Si no, incrementa current_streak en 1 y actualiza best_streak si es necesario.
        
        Args:
            user_id: UUID del usuario
            
        Returns:
            Dict con updated_streak (bool) y streak (int)
        """
        try:
            # Obtener la fecha actual
            today = date.today().isoformat()
            
            # Obtener el registro de streak del usuario
            streak_result = (
                self.supabase
                .table("user_streak")
                .select("current_streak, best_streak, updated_at")
                .eq("user_id", user_id)
                .execute()
            )
            
            if not streak_result.data or len(streak_result.data) == 0:
                # Usuario no existe, crear registro con streak = 1
                logger.info(f"Usuario {user_id} no tiene registro de streak, creando nuevo")
                return self._increment_user_streak(user_id)
            
            user_streak_data = streak_result.data[0]
            updated_at = user_streak_data.get("updated_at")
            
            # Extraer solo la fecha de updated_at (sin hora)
            if updated_at:
                updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00')).date().isoformat()
            else:
                updated_date = None
            
            # Si updated_at es igual a la fecha de hoy, no hacer nada
            if updated_date == today:
                logger.info(f"Usuario {user_id} ya fue actualizado hoy, no actualizando streak")
                return {
                    "updated_streak": False,
                    "streak": user_streak_data.get("current_streak"),
                    "message": "Usuario ya fue actualizado hoy"
                }
            
            # Si no, incrementar el streak
            logger.info(f"Usuario {user_id} no fue actualizado hoy, incrementando streak")
            return self._increment_user_streak(user_id)
            
        except Exception as e:
            logger.error(f"Error checking user streak: {e}")
            return {
                "updated_streak": False,
                "streak": None,
                "error": str(e)
            }

    def _increment_user_streak(self, user_id: str) -> Dict[str, Any]:
        """
        Incrementa el streak del usuario en la tabla user_streak.
        También actualiza best_streak si current_streak supera el récord.
        
        Args:
            user_id: UUID del usuario
            
        Returns:
            Dict con updated_streak (bool) y streak (int)
        """
        try:
            # Verificar si el usuario ya tiene un registro de streak
            existing_streak = (
                self.supabase
                .table("user_streak")
                .select("current_streak, best_streak")
                .eq("user_id", user_id)
                .execute()
            )
            
            if existing_streak.data and len(existing_streak.data) > 0:
                # Usuario existe, incrementar streak
                current_streak = existing_streak.data[0]["current_streak"]
                best_streak = existing_streak.data[0]["best_streak"] or 0
                new_streak = current_streak + 1
                
                # Actualizar best_streak si el nuevo streak es mayor
                new_best_streak = max(new_streak, best_streak)
                
                update_data = {
                    "current_streak": new_streak,
                    "best_streak": new_best_streak,
                    "updated_at": datetime.now().isoformat()
                }
                
                update_result = (
                    self.supabase
                    .table("user_streak")
                    .update(update_data)
                    .eq("user_id", user_id)
                    .execute()
                )
                
                logger.info(f"Streak actualizado para usuario {user_id}: {current_streak} -> {new_streak}, best: {new_best_streak}")
                return {
                    "updated_streak": True,
                    "streak": new_streak,
                    "best_streak": new_best_streak,
                    "previous_streak": current_streak
                }
                
            else:
                # Usuario no existe, crear registro con streak = 1
                insert_data = {
                    "user_id": user_id,
                    "current_streak": 1,
                    "best_streak": 1,
                    "updated_at": datetime.now().isoformat()
                }
                
                insert_result = (
                    self.supabase
                    .table("user_streak")
                    .insert(insert_data)
                    .execute()
                )
                
                logger.info(f"Nuevo streak creado para usuario {user_id}: 1")
                return {
                    "updated_streak": True,
                    "streak": 1,
                    "best_streak": 1,
                    "previous_streak": 0
                }
                
        except Exception as e:
            logger.error(f"Error incrementing user streak: {e}")
            return {
                "updated_streak": False,
                "streak": None,
                "error": str(e)
            }

    def get_user_streak(self, user_id: str) -> Dict[str, Any]:
        """
        Obtiene el streak actual del usuario.
        
        Args:
            user_id: UUID del usuario
            
        Returns:
            Dict con el streak actual
        """
        try:
            result = (
                self.supabase
                .table("user_streak")
                .select("current_streak")
                .eq("user_id", user_id)
                .execute()
            )
            
            if result.data and len(result.data) > 0:
                return {
                    "streak": result.data[0]["current_streak"],
                    "exists": True
                }
            else:
                return {
                    "streak": 0,
                    "exists": False
                }
                
        except Exception as e:
            logger.error(f"Error getting user streak: {e}")
            return {
                "streak": 0,
                "exists": False,
                "error": str(e)
            }
