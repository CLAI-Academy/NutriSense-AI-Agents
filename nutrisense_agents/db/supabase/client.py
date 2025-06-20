from typing import Any, Dict
from uuid import UUID
from nutrisense_agents.config.settings import settings
from supabase import create_client, Client
import uuid
import logging

logger = logging.getLogger(__name__)

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
    
    def refresh_schema_cache(self):
        """
        Refresca el cache de esquema de Supabase
        """
        try:
            # Forzar refresh del esquema haciendo una query simple
            self.supabase.table("food_diary").select("id").limit(1).execute()
            logger.info("✅ Schema cache refrescado exitosamente")
            return True
        except Exception as e:
            logger.error(f"❌ Error refrescando schema cache: {e}")
            return False
    
    def verify_food_diary_schema(self):
        """
        Verifica las columnas disponibles en food_diary para debug
        """
        try:
            # Obtener información de la tabla
            result = self.supabase.rpc('get_table_columns', {
                'table_name': 'food_diary'
            }).execute()
            
            logger.info(f"🔍 Columnas disponibles en food_diary: {result.data}")
            return result.data
        except Exception as e:
            logger.warning(f"⚠️ No se pudo verificar esquema (esto es normal): {e}")
            return None
    
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
        """
        Añade entrada al food_diary usando SOLO los campos que existen en el esquema actual
        """
        
        # 🔧 SOLO CAMPOS QUE EXISTEN EN TU ESQUEMA ACTUAL
        food_diary_data = {
            "id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "date": data.get("date", ""),
            "meal_type": data.get("meal_type", ""),
            "recipe_id": data.get("recipe_id"),  # Puede ser None
            "food_name": data.get("food_name", ""),
            "quantity": data.get("quantity", 0),
            "unit": data.get("unit", ""),
            "calories": data.get("calories", 0),
            "protein": data.get("protein", 0),
            "carbs": data.get("carbs", 0),
            "fat": data.get("fat", 0),
            "fiber": data.get("fiber", 0),
            "notes": data.get("notes", ""),
            # ❌ ELIMINADO: "sugar": data.get("sugar", 0),  # <- ESTA LÍNEA CAUSABA EL ERROR
            "consumed_at": data.get("consumed_at", ""),
            "location_type": data.get("location_type", "unknown"),
            "time_since_last_meal": data.get("time_since_last_meal"),  # Puede ser None
            "day_type": data.get("day_type", "weekday"),
            "eating_context": data.get("eating_context"),  # Puede ser None
            "mood_emoji": data.get("mood_emoji"),  # Puede ser None
            "created_at": data.get("created_at", ""),
        }
        
        # Remover campos None para evitar problemas
        food_diary_data = {k: v for k, v in food_diary_data.items() if v is not None}
        
        logger.info(f"🔍 Insertando en food_diary: {list(food_diary_data.keys())}")
        
        try:
            result = self.supabase.table("food_diary").insert(food_diary_data).execute()
            logger.info("✅ Inserción exitosa en food_diary")
            return result
        except Exception as e:
            logger.error(f"❌ Error insertando en food_diary: {e}")
            
            # 🔄 Fallback: Intentar refrescar schema y reintentar
            logger.info("🔄 Intentando refresh de schema y reintento...")
            self.refresh_schema_cache()
            
            try:
                result = self.supabase.table("food_diary").insert(food_diary_data).execute()
                logger.info("✅ Inserción exitosa después de refresh")
                return result
            except Exception as retry_error:
                logger.error(f"❌ Error persiste después de refresh: {retry_error}")
                raise retry_error