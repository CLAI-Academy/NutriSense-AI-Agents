from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from nutrisense_agents.ai_companion.graphs.text_analyzer.state import TextRecipeState
from nutrisense_agents.ai_companion.graphs.text_analyzer.nodes import (
    text_extract, 
    human_ingredients_validation,
    calc_macros, 
    human_consumption_validation, 
    insert_food_diary
)

g = StateGraph(TextRecipeState)

# Agregar todos los nodos
g.add_node("text_extract", text_extract)
g.add_node("human_ingredients_validation", human_ingredients_validation)
g.add_node("calc_macros", calc_macros)
g.add_node("human_consumption_validation", human_consumption_validation)
g.add_node("insert_food_diary", insert_food_diary)

# Conexiones del grafo
g.add_edge(START, "text_extract")
g.add_edge("text_extract", "human_ingredients_validation")
g.add_edge("human_ingredients_validation", "calc_macros")
g.add_edge("calc_macros", "human_consumption_validation")
g.add_edge("human_consumption_validation", "insert_food_diary")
g.add_edge("insert_food_diary", END)

# Compilar con checkpointer
text_graph = g.compile(checkpointer=MemorySaver())