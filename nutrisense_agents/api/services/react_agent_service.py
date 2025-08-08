"""
Servicio de creación e invocación del React Agent de NutriSense.

Este módulo se encarga de:
1. Obtener los datos del perfil de salud del usuario
2. Crear e invocar el React Agent con el contexto del usuario
3. Exponer funciones para invocación normal y streaming
"""

from typing import Dict, Any, List, AsyncGenerator

from langchain_core.messages import BaseMessage
from nutrisense_agents.ai_companion.agents.react_agent import create_nutrisense_react_agent
from nutrisense_agents.db.supabase.client import SupabaseClient

# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def convert_langchain_messages_to_dict(messages: List[BaseMessage]) -> List[Dict[str, Any]]:
    """
    Convierte mensajes de LangChain a formato diccionario para la API.
    
    Args:
        messages: Lista de mensajes de LangChain (HumanMessage, AIMessage, etc.)
        
    Returns:
        Lista de diccionarios con formato {role: str, content: str}
    """
    result = []
    for msg in messages:
        if hasattr(msg, 'type') and hasattr(msg, 'content'):
            # Mapear tipos de LangChain a roles de API
            role_mapping = {
                'human': 'user',
                'ai': 'assistant',
                'system': 'system'
            }
            role = role_mapping.get(msg.type, 'user')
            result.append({
                'role': role,
                'content': str(msg.content)
            })
    return result

async def get_user_health_data(user_uid: str) -> Dict[str, Any]:
    """Obtiene los datos de salud del usuario."""
    supabase = SupabaseClient()
    return supabase.get_user_health_profile_data(user_uid)

async def create_react_agent_service(user_uid: str) -> Any:
    """Prepara el React Agent con los datos del usuario."""
    # Obtener datos del perfil de salud
    user_data = await get_user_health_data(user_uid)
    
    return await create_nutrisense_react_agent(
        user_uid=user_uid,
        user_sheet=user_data.get("summary", "No hay ficha disponible"),
        user_plan=user_data.get("user_nutrition_profile", "No hay plan nutricional disponible")
    )

# ---------------------------------------------------------------------------
# API pública del servicio
# ---------------------------------------------------------------------------

async def invoke_nutrisense_react_agent(
    user_uid: str, 
    messages: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Invoca el agente de forma síncrona y devuelve la respuesta completa.
    
    Args:
        user_uid: ID del usuario
        messages: Lista de mensajes en formato [{role: str, content: str}]
    """
    agent = await create_react_agent_service(user_uid)
    response = await agent.ainvoke({"messages": messages}, config={"configurable": {"user_uuid": user_uid}})
    
    # Convertir mensajes de LangChain a formato dict
    if "messages" in response and isinstance(response["messages"], list):
        response["messages"] = convert_langchain_messages_to_dict(response["messages"])
    
    return response

async def stream_nutrisense_react_agent(
    user_uid: str, 
    messages: List[Dict[str, Any]]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Invoca el agente de forma asíncrona y devuelve un generador de chunks.
    
    Args:
        user_uid: ID del usuario
        messages: Lista de mensajes en formato [{role: str, content: str}]
    """
    agent = await create_react_agent_service(user_uid)
    async for chunk in agent.astream({"messages": messages}, config={"configurable": {"user_uuid": user_uid}}):
        # Convertir mensajes de LangChain a formato dict en cada chunk
        if "messages" in chunk and isinstance(chunk["messages"], list):
            chunk["messages"] = convert_langchain_messages_to_dict(chunk["messages"])
        yield chunk