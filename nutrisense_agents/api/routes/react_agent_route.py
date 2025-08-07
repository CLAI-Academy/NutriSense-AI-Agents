# nutrisense_agents/api/routes/react_agent_route.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import logging

from nutrisense_agents.api.services.react_agent_service import (
    invoke_nutrisense_react_agent,
    stream_nutrisense_react_agent
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/react-agent", tags=["react-agent"])

# Esquemas de request/response
class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str

class ReactAgentRequest(BaseModel):
    user_uid: str
    messages: List[ChatMessage]

class ReactAgentResponse(BaseModel):
    success: bool
    messages: List[Dict[str, Any]]
    error: str = None

@router.post("/chat", response_model=ReactAgentResponse)
async def chat_with_react_agent(request: ReactAgentRequest):
    """
    Endpoint síncrono para interactuar con el React Agent.
    
    Args:
        request: Contiene user_uid y lista de mensajes
        
    Returns:
        Respuesta completa del agente
    """
    try:
        logger.info(f"Iniciando chat con React Agent para usuario: {request.user_uid}")
        
        # Convertir mensajes a formato dict
        messages_dict = [msg.dict() for msg in request.messages]
        
        # Invocar el agente
        response = await invoke_nutrisense_react_agent(
            user_uid=request.user_uid,
            messages=messages_dict
        )
        
        logger.info(f"Chat completado exitosamente para usuario: {request.user_uid}")
        
        return ReactAgentResponse(
            success=True,
            messages=response.get("messages", [])
        )
        
    except Exception as e:
        logger.error(f"Error en chat con React Agent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/chat/stream")
async def stream_chat_with_react_agent(request: ReactAgentRequest):
    """
    Endpoint de streaming para interactuar con el React Agent.
    
    Args:
        request: Contiene user_uid y lista de mensajes
        
    Returns:
        Stream de respuestas del agente en formato Server-Sent Events
    """
    try:
        logger.info(f"Iniciando stream con React Agent para usuario: {request.user_uid}")
        
        # Convertir mensajes a formato dict
        messages_dict = [msg.dict() for msg in request.messages]
        
        async def generate_stream():
            try:
                async for chunk in stream_nutrisense_react_agent(
                    user_uid=request.user_uid,
                    messages=messages_dict
                ):
                    # Formatear chunk para SSE
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                # Enviar evento de finalización
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                logger.error(f"Error en streaming: {str(e)}")
                error_chunk = {
                    "type": "error",
                    "message": f"Error en streaming: {str(e)}"
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"Error configurando stream: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error configurando stream: {str(e)}"
        )

@router.get("/health")
async def react_agent_health():
    """Endpoint de salud para el React Agent."""
    return {
        "status": "healthy",
        "service": "React Agent",
        "endpoints": ["/chat", "/chat/stream"]
    }