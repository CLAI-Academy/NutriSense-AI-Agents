# nutrisense_agents/api/routes/img_analysis_route.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from nutrisense_agents.ai_companion.graphs.img_analtzer.graph import graph
from langgraph.types import Command
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router en lugar de app
router = APIRouter(prefix="/recipe-analysis", tags=["recipe-analysis"])

@router.websocket("/ws/{thread_id}")
async def recipe_analysis_websocket(ws: WebSocket, thread_id: str):
    """
    WebSocket para análisis de recetas con imágenes.
    
    Args:
        ws: Conexión WebSocket
        thread_id: ID único del thread para mantener estado
    
    Flujo:
    1. Cliente envía imagen URL
    2. Servidor extrae ingredientes
    3. Servidor genera nombre de receta
    4. Servidor pide validación humana (interrupt)
    5. Cliente envía correcciones
    6. Servidor calcula macros
    7. Servidor guarda en BD
    """
    await ws.accept()
    logger.info(f"WebSocket conectado para thread_id: {thread_id}")
    
    try:
        # Primer mensaje debe traer la imagen URL
        init_msg = await ws.receive_json()
        image_url = init_msg.get("image_url")
        
        if not image_url:
            await ws.send_json({
                "type": "error",
                "message": "Se requiere image_url en el mensaje inicial"
            })
            await ws.close()
            return
        
        # Estado inicial para el grafo
        init_state = {
            "image_url": image_url,
            "user_id": init_msg.get("user_id"),
            "current_step": "starting",
            "success": False,
            "error_message": None
        }
        
        logger.info(f"Iniciando análisis para thread_id: {thread_id}")
        
        # Ejecutar el grafo de análisis
        async for event in graph.astream(
            init_state,
            config={"configurable": {"thread_id": thread_id}}
        ):
            if "interrupt" in event:
                # 🚨 Punto de interrupción para validación humana
                logger.info(f"Interrupción en thread_id: {thread_id} - esperando validación")
                await ws.send_json({
                    "type": "need_input",
                    "payload": event["interrupt"]["value"],
                    "step": "human_validation"
                })
                
                # Esperar correcciones del usuario
                edited = await ws.receive_json()
                logger.info(f"Recibidas correcciones para thread_id: {thread_id}")
                
                # Continuar el flujo con las correcciones
                await graph.ainvoke(
                    Command(resume=edited),
                    config={"configurable": {"thread_id": thread_id}}
                )
                
            elif event.get("__end__"):
                # ✅ Flujo terminado exitosamente
                logger.info(f"Análisis completado para thread_id: {thread_id}")
                await ws.send_json({
                    "type": "done",
                    "message": "Análisis de receta completado exitosamente"
                })
                await ws.close()
                break
                
            else:
                # 📊 Progreso del flujo
                current_step = event.get("current_step", "processing")
                logger.info(f"Progreso en thread_id: {thread_id} - paso: {current_step}")
                
                await ws.send_json({
                    "type": "update",
                    "payload": event,
                    "step": current_step
                })

    except WebSocketDisconnect:
        # El usuario cerró la conexión
        logger.info(f"WebSocket desconectado para thread_id: {thread_id}")
        # El checkpointer mantiene el estado para reconexión futura
        
    except Exception as e:
        # Error inesperado
        logger.error(f"Error en WebSocket thread_id {thread_id}: {str(e)}")
        try:
            await ws.send_json({
                "type": "error",
                "message": f"Error interno del servidor: {str(e)}"
            })
            await ws.close()
        except:
            pass


