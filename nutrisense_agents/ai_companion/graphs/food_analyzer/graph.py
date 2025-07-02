from langgraph.graph import StateGraph, END
from nutrisense_agents.ai_companion.graphs.food_analyzer.state import FoodAnalysisState
from nutrisense_agents.ai_companion.graphs.food_analyzer.nodes import (
    extract_food_info,
    human_ingredients_validation,
    calc_macros,
    human_consumption_validation,
    update_user_streak,
    insert_food_diary,
    handle_user_cancellation
)
from langgraph.checkpoint.memory import MemorySaver
import logging

logger = logging.getLogger(__name__)

def should_cancel(state: FoodAnalysisState) -> str:
    """Determina si el proceso debe cancelarse"""
    if state.get("action") == "cancel":
        return "handle_cancellation"
    return "calc_macros"

def should_cancel_after_consumption(state: FoodAnalysisState) -> str:
    """Determina si el proceso debe cancelarse después de la validación de consumo"""
    if state.get("action") == "cancel":
        return "handle_cancellation"
    return "update_streak"

# Crear el grafo
workflow = StateGraph(FoodAnalysisState)

# Agregar nodos
workflow.add_node("extract_food_info", extract_food_info)
workflow.add_node("human_ingredients_validation", human_ingredients_validation)
workflow.add_node("calc_macros", calc_macros)
workflow.add_node("human_consumption_validation", human_consumption_validation)
workflow.add_node("update_streak", update_user_streak)
workflow.add_node("insert_food_diary", insert_food_diary)
workflow.add_node("handle_cancellation", handle_user_cancellation)

# Definir el flujo
workflow.set_entry_point("extract_food_info")

# Flujo principal
workflow.add_edge("extract_food_info", "human_ingredients_validation")

# Condicional después de validación de ingredientes
workflow.add_conditional_edges(
    "human_ingredients_validation",
    should_cancel,
    {
        "calc_macros": "calc_macros", 
        "handle_cancellation": "handle_cancellation"
    }
)

workflow.add_edge("calc_macros", "human_consumption_validation")

# Condicional después de validación de consumo
workflow.add_conditional_edges(
    "human_consumption_validation",
    should_cancel_after_consumption,
    {
        "update_streak": "update_streak",
        "handle_cancellation": "handle_cancellation"
    }
)

workflow.add_edge("update_streak", "insert_food_diary")

# Finales
workflow.add_edge("insert_food_diary", END)
workflow.add_edge("handle_cancellation", END)

# Crear checkpointer para persistir estado
checkpointer = MemorySaver()

# Compilar el grafo
food_analysis_graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_ingredients_validation", "human_consumption_validation"]
)

# Exportar para uso en rutas
graph = food_analysis_graph