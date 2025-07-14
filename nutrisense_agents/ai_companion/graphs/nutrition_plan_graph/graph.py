from langgraph.graph import StateGraph, START, END
from nutrisense_agents.ai_companion.graphs.nutrition_plan_graph.state import UserProfileState
from nutrisense_agents.ai_companion.graphs.nutrition_plan_graph.nodes import (
    calculate_nutrition_targets,
    generate_user_profile,
    generate_summary,
    save_to_database
)

def user_profile_graph():
    # Crear el grafo con el estado de perfil nutricional
    workflow = StateGraph(UserProfileState)
    
    # Agregar todos los nodos al grafo
    workflow.add_node("calculate_nutrition_targets", calculate_nutrition_targets)
    workflow.add_node("generate_user_profile", generate_user_profile)
    workflow.add_node("generate_summary", generate_summary)
    workflow.add_node("save_to_database", save_to_database)
    
    # Definir las conexiones del grafo
    workflow.add_edge(START, "calculate_nutrition_targets")
    workflow.add_edge("calculate_nutrition_targets", "generate_user_profile")
    workflow.add_edge("generate_user_profile", "generate_summary")
    workflow.add_edge("generate_summary", "save_to_database")
    workflow.add_edge("save_to_database", END)
    
    # Compilar el grafo
    return workflow

compiled_user_profile_graph = user_profile_graph().compile()