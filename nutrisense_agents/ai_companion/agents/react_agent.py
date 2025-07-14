"""
Módulo para la construcción del React Agent de NutriSense.

Este módulo se limita a:
1. Recuperar el modelo de chat
2. Obtener las tools protegidas
3. Construir el grafo React Agent con LangGraph
"""

from typing import Dict, Any

from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from nutrisense_agents.config.agent_config import get_chat_model
from nutrisense_agents.ai_companion.MCPs.mcp_tools import get_mcp_tools
from nutrisense_agents.ai_companion.prompts.react_prompt import REACT_PROMPT

async def create_nutrisense_react_agent(user_uid: str, user_sheet: str, user_plan: str):
    """
    Compila y devuelve el React Agent ya preparado para el usuario.
    
    Args:
        user_uid: ID del usuario
        user_sheet: Ficha del usuario
        user_plan: Plan nutricional del usuario
    """
    model = get_chat_model("gpt")
    tools = await get_mcp_tools(user_uid=user_uid)

    # Construimos el prompt con el contexto del usuario y placeholder para mensajes
    template = ChatPromptTemplate.from_messages([
        ("system", f"{REACT_PROMPT}\n\nContexto del usuario:\nFicha: {user_sheet}\nPlan Nutricional: {user_plan}"),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    return create_react_agent(model, tools, prompt=template)