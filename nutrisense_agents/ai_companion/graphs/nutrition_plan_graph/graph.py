from langgraph.graph import StateGraph, START, END
from nutrisense_agents.ai_companion.graphs.nutrition_plan_graph.state import NutritionPlanState
from nutrisense_agents.ai_companion.graphs.nutrition_plan_graph.nodes import (
    calculate_nutrition_targets,
    generate_nutrition_plan,
    generate_summary,
    save_to_database
)

def nutrition_plan_graph():
    # Crear el grafo con el estado de plan nutricional
    workflow = StateGraph(NutritionPlanState)
    
    # Agregar todos los nodos al grafo
    workflow.add_node("calculate_nutrition_targets", calculate_nutrition_targets)
    workflow.add_node("generate_nutrition_plan", generate_nutrition_plan)
    workflow.add_node("generate_summary", generate_summary)
    workflow.add_node("save_to_database", save_to_database)
    
    # Definir las conexiones del grafo
    workflow.add_edge(START, "calculate_nutrition_targets")
    workflow.add_edge("calculate_nutrition_targets", "generate_nutrition_plan")
    workflow.add_edge("generate_nutrition_plan", "generate_summary")
    workflow.add_edge("generate_summary", "save_to_database")
    workflow.add_edge("save_to_database", END)
    
    # Compilar el grafo
    return workflow

compiled_nutrition_plan_graph = nutrition_plan_graph().compile()