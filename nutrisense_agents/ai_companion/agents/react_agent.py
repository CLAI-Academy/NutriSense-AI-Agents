"""
Servicio de creación e invocación del React Agent de NutriSense.

Este módulo se limita a:
1. Recuperar el modelo de chat.
2. Obtener las tools protegidas que devuelve `mcp_tools`.
3. Construir el grafo React Agent con LangGraph.
4. Exponer funciones auxiliares para invocación normal y streaming.
"""

from typing import Dict, Any, List

from langgraph.prebuilt import create_react_agent

from nutrisense_agents.config.agent_config import get_chat_model
from nutrisense_agents.ai_companion.MCPs.mcp_tools import get_mcp_tools
from nutrisense_agents.ai_companion.prompts.react_prompt import REACT_PROMPT

# ---------------------------------------------------------------------------
# Construcción del agente
# ---------------------------------------------------------------------------

async def create_nutrisense_react_agent(user_uid: str):
    """Compila y devuelve el React Agent ya preparado para el usuario."""

    model = get_chat_model("gpt")
    tools = await get_mcp_tools(user_uid=user_uid)
    return create_react_agent(model, tools, prompt=REACT_PROMPT)

# ---------------------------------------------------------------------------
# Invocación estándar
# ---------------------------------------------------------------------------

async def invoke_nutrisense_react_agent(
    user_uid: str, messages: List[Dict[str, Any]]
):
    """Invoca el agente con una lista de mensajes y devuelve la respuesta."""

    agent = await create_nutrisense_react_agent(user_uid)
    return await agent.ainvoke({"messages": messages})

# ---------------------------------------------------------------------------
# Invocación en streaming
# ---------------------------------------------------------------------------

async def stream_nutrisense_react_agent(
    user_uid: str, messages: List[Dict[str, Any]]
):
    """Generador asíncrono que produce los chunks de respuesta en tiempo real."""

    agent = await create_nutrisense_react_agent(user_uid)
    async for chunk in agent.astream({"messages": messages}):
        yield chunk
