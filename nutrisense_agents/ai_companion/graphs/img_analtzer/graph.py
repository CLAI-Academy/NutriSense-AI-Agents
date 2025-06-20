# graph.py
from langgraph.graph import StateGraph, START, END

from langgraph.checkpoint.memory import MemorySaver
from nutrisense_agents.ai_companion.graphs.img_analtzer.state import RecipeState
from nutrisense_agents.ai_companion.graphs.img_analtzer.nodes import vision_extract, human_ingredients_validation, calc_macros, human_consumption_validation, insert_food_diary

g = StateGraph(RecipeState)


g.add_node("vision", vision_extract)
g.add_node("human_ingredients_validation", human_ingredients_validation)
g.add_node("calc_macros", calc_macros)
g.add_node("human_consumption_validation", human_consumption_validation)
g.add_node("insert_food_diary", insert_food_diary)

g.add_edge(START, "vision")
g.add_edge("vision", "human_ingredients_validation")
g.add_edge("human_ingredients_validation", "calc_macros")
g.add_edge("calc_macros", "human_consumption_validation")
g.add_edge("human_consumption_validation", "insert_food_diary")
g.add_edge("insert_food_diary", END)

# Usar MemorySaver que maneja thread_id como string correctamente
graph = g.compile(checkpointer=MemorySaver())
