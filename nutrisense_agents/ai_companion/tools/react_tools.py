# tools_wrappers.py
from typing import List, Optional, Dict
import logging
import sys
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from nutrisense_agents.ai_companion.schemas.tools_schemas.react_input_schemas import (
    RecipeList, MealPlanInput, PlannedMealInput, OptimizeMealPlanInput, 
    MealPlanSummaryInput, UserDataInput,ShoppingListInput
)
from nutrisense_agents.db.supabase.supabasetool import SupabaseTools   # tu clase original

logging.basicConfig(level=logging.ERROR, handlers=[logging.StreamHandler(sys.stderr)])
log = logging.getLogger(__name__)

st = SupabaseTools()   # instancia compartida (o crea una nueva dentro)


@tool
def add_planned_meal_tool(data: RecipeList, *, config: RunnableConfig):
    """
    Añade una lista de comidas planificadas para el usuario.
    Tras crear la lista de comidas, se debe mostrar al usuario, qué días debe cocinar, 
    que recetas debe preparar y como guardarlas para que sea lo más óptimo posible.
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")   # ← inyección segura
    if not user_uuid:
        raise KeyError("user_uuid")
    return st.add_planned_meal(data, user_uuid)

@tool
def create_meal_plan_tool(data: MealPlanInput, *, config: RunnableConfig):
    """
    Crea un plan de comidas semanal base para el usuario.
    Genera un plan personalizado considerando fecha de inicio, objetivos calóricos, 
    preferencias dietéticas y número de comidas por día.
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")
    if not user_uuid:
        raise KeyError("user_uuid")
    return st.create_meal_plan(data, user_uuid)

@tool
def add_planned_meal_to_schedule_tool(data: PlannedMealInput, *, config: RunnableConfig):
    """
    Crea recetas y las programa automáticamente en un plan de comidas existente.
    Combina la creación de recetas con la programación automática en la semana, 
    distribuyendo las comidas de forma equilibrada.
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")
    if not user_uuid:
        raise KeyError("user_uuid")
    return st.add_planned_meal_to_schedule(data, user_uuid)

@tool
def optimize_meal_plan_tool(data: OptimizeMealPlanInput, *, config: RunnableConfig):
    """
    Analiza y optimiza un plan de comidas existente.
    Proporciona análisis nutricional completo, recomendaciones de mejora, 
    lista de ingredientes necesarios y sugerencias de meal prep.
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")
    if not user_uuid:
        raise KeyError("user_uuid")
    return st.optimize_meal_plan(data.meal_plan_id, user_uuid)

@tool
def get_meal_plan_summary_tool(data: MealPlanSummaryInput, *, config: RunnableConfig):
    """
    Obtiene un resumen completo del plan de comidas con información práctica.
    Incluye horarios de comidas, días optimizados para cocinar, recetas a preparar 
    y tiempo total de cocina estimado.
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")
    if not user_uuid:
        raise KeyError("user_uuid")
    return st.get_meal_plan_summary(data.meal_plan_id, user_uuid)

@tool
def get_user_data_tool(data: UserDataInput, *, config: RunnableConfig):
    """
    Obtiene datos del usuario de tablas específicas con filtros opcionales.
    
    INFORMACIÓN DISPONIBLE POR TABLA:
    
    PLANIFICACIÓN:
    • meal_plans: Planes de comida semanales (week_start_date, is_active)
    • planned_meals: Comidas planificadas específicas (day_of_week, meal_type, recipe_id, 
      start_time, servings_planned)
    
    REGISTRO Y SEGUIMIENTO:
    • food_diary: Diario nutricional diario con alimentos consumidos, cantidades, información 
      nutricional, hora de consumo, ubicación, contexto, estado de ánimo ocasional
    • daily_nutrition_summary: Resúmenes nutricionales diarios agregados con totales vs objetivos 
      y puntuación de adherencia
    
    INVENTARIO Y COMPRAS:
    • user_inventory: Inventario personal de ingredientes (quantity, unit, expiry_date, location)
    • shopping_lists: Listas de compra (name, status, meal_plan_id, total_estimated_cost)
    • shopping_list_items: Items específicos de listas de compra con cantidades necesarias, 
      disponibles y a comprar
    
    GAMIFICACIÓN:
    • user_streak: Rachas de cumplimiento de objetivos (current_streak, best_streak, 
      last_target_date)
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")
    if not user_uuid:
        raise KeyError("user_uuid")
    return st.get_user_data(data.table_name, user_uuid, data.extra_filters, data.limit)

@tool
def get_user_inventory_tool(*, config: RunnableConfig):
    """
    Devuelve el inventario actual del usuario desde Supabase.

    Incluye nombre del ingrediente, cantidad, unidad y fecha de vencimiento.
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")
    if not user_uuid:
        raise KeyError("user_uuid")
    return st.get_user_inventory(user_uuid)

@tool
def check_expiring_ingredients_tool(*, days_ahead: int = 0, days_behind: int = 0, config: RunnableConfig):
    """
    Consulta el inventario del usuario y devuelve ingredientes según su fecha de vencimiento.

    - expired: vencidos en los últimos `days_behind` días.
    - expiring_today: vencen exactamente hoy.
    - expiring_soon: vencen en los próximos `days_ahead` días.

    Ejemplos:
    - "Qué alimentos vencen hoy?" → days_ahead=0, days_behind=0
    - "Qué alimentos ya vencieron?" → days_ahead=0, days_behind=30
    - "Qué alimentos vencen en 2 días?" → days_ahead=2, days_behind=0
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")
    if not user_uuid:
        raise KeyError("user_uuid")

    return st.get_ingredients_expiry_range(user_uuid, days_ahead, days_behind)

@tool
def suggest_recipes_from_stock_tool(*, config: RunnableConfig):
    """
    Sugiere recetas que el usuario puede preparar con su inventario actual.
    Devuelve recetas ordenadas según cuántos ingredientes ya tiene disponibles.
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")
    if not user_uuid:
        raise KeyError("user_uuid")
    return st.get_suggested_recipes_by_inventory(user_uuid)

@tool
def generate_shopping_list_tool(*, recipe_ids: list[int], config: RunnableConfig):
    """
    Genera una lista de compras basada en recetas seleccionadas y el inventario actual del usuario.
    Devuelve solo los ingredientes faltantes con cantidades.
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")
    if not user_uuid:
        raise KeyError("user_uuid")
    return st.generate_shopping_list(user_uuid, recipe_ids)

@tool
def suggest_recipes_for_expiring_tool(*, days_ahead: int = 3, config: RunnableConfig):
    """
    Sugiere recetas priorizando los ingredientes que están por vencer en los próximos `days_ahead` días.
    Ordena las recetas de forma que primero aparezcan las que usan ingredientes con fecha más próxima
    y mayor porcentaje de coincidencia.

    Args:
        days_ahead (int): rango de días hacia adelante para considerar "por vencer".
    """
    user_uuid = config.get("configurable", {}).get("user_uuid")
    if not user_uuid:
        raise KeyError("user_uuid")

    return st.get_suggested_recipes_by_expiring_ingredients(user_uuid, days_ahead)


TOOLS = [
    add_planned_meal_tool,
    create_meal_plan_tool,
    add_planned_meal_to_schedule_tool,
    get_meal_plan_summary_tool,
    get_user_data_tool,
    get_user_inventory_tool,
    check_expiring_ingredients_tool,
    suggest_recipes_from_stock_tool,
    generate_shopping_list_tool,
    suggest_recipes_for_expiring_tool
]

