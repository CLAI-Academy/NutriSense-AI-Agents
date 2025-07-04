# nutrisense_agents/api/routes/food_analysis_route.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from nutrisense_agents.ai_companion.graphs.food_analyzer.graph import graph
from langgraph.types import Command
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router unificado
router = APIRouter(prefix="/food-analysis", tags=["food-analysis"])

@router.websocket("/ws/{thread_id}")
async def food_analysis_websocket(ws: WebSocket, thread_id: str):
    """WebSocket unificado para análisis de alimentos (imagen y texto) - manejo de múltiples interrupciones."""
    await ws.accept()
    logger.info(f"WebSocket conectado para thread_id: {thread_id}")
    
    try:
        # Primer mensaje debe traer el tipo de análisis y los datos correspondientes
        init_msg = await ws.receive_json()
        extraction_type = init_msg.get("extraction_type")
        
        if not extraction_type or extraction_type not in ["image", "text"]:
            await ws.send_json({
                "type": "error",
                "message": "Se requiere extraction_type válido ('image' o 'text') en el mensaje inicial"
            })
            await ws.close()
            return
        
        # Validar datos según el tipo de extracción
        if extraction_type == "image":
            image_url = init_msg.get("image_url")
            if not image_url:
                await ws.send_json({
                    "type": "error",
                    "message": "Se requiere image_url para análisis de imagen"
                })
                await ws.close()
                return
            
            # Estado inicial para análisis de imagen
            init_state = {
                "extraction_type": "image",
                "image_url": image_url,
                "user_notes": init_msg.get("user_notes", ""),
                "user_id": init_msg.get("user_id"),
                "current_step": "starting",
                "success": False,
                "error_message": None
            }
            
        elif extraction_type == "text":
            text_description = init_msg.get("text_description")
            if not text_description:
                await ws.send_json({
                    "type": "error",
                    "message": "Se requiere text_description para análisis de texto"
                })
                await ws.close()
                return
            
            # Estado inicial para análisis de texto
            init_state = {
                "extraction_type": "text",
                "text_description": text_description,
                "user_notes": init_msg.get("user_notes", ""),
                "user_id": init_msg.get("user_id"),
                "current_step": "starting",
                "success": False,
                "error_message": None
            }
        
        logger.info(f"Iniciando análisis de {extraction_type} para thread_id: {thread_id}")
        config = {"configurable": {"thread_id": thread_id}}
        
        # Manejar el flujo completo con múltiples interrupciones
        await handle_graph_execution(ws, init_state, config, thread_id)

    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado para thread_id: {thread_id}")
        
    except Exception as e:
        logger.error(f"Error en WebSocket thread_id {thread_id}: {str(e)}")
        logger.error(f"Traceback completo: ", exc_info=True)
        try:
            await ws.send_json({
                "type": "error",
                "message": f"Error interno del servidor: {str(e)}"
            })
            await ws.close()
        except:
            pass

async def handle_graph_execution(ws: WebSocket, initial_state: dict, config: dict, thread_id: str):
    """
    Maneja la ejecución completa del grafo incluyendo múltiples interrupciones
    """
    current_input = initial_state
    
    while True:
        logger.info(f"🔄 Ejecutando grafo con input: {current_input}")
        
        try:
            # Ejecutar el grafo desde el estado actual
            async for event in graph.astream(current_input, config=config):
                logger.info(f"📨 Evento recibido: {list(event.keys()) if isinstance(event, dict) else event}")
                
                # MANEJO DE INTERRUPCIÓN
                if "__interrupt__" in event:
                    interrupt_data = await handle_interrupt(ws, event, thread_id)
                    if interrupt_data is None:
                        # Usuario se desconectó o error
                        return
                    
                    # Usar Command(resume=...) y continuar el bucle
                    current_input = Command(resume=interrupt_data)
                    logger.info(f"🔄 Reanudando con datos del usuario: {interrupt_data}")
                    break  # Salir del astream actual y reiniciar con el nuevo input
                
                # FLUJO TERMINADO
                elif event.get("__end__"):
                    logger.info(f"✅ Análisis completado para thread_id: {thread_id}")
                    final_state = event.get("__end__", {})
                    extraction_type = final_state.get("extraction_type", "unknown")
                    
                    await ws.send_json({
                        "type": "done", 
                        "message": f"Análisis de {extraction_type} completado exitosamente",
                        "final_state": final_state
                    })
                    await ws.close()
                    return  # Terminar completamente
                
                # PROGRESO NORMAL
                else:
                    current_step = event.get("current_step", "processing")
                    logger.info(f"📊 Progreso en thread_id: {thread_id} - paso: {current_step}")
                    
                    await ws.send_json({
                        "type": "update",
                        "payload": event,
                        "step": current_step
                    })
            
            # Si llegamos aquí sin interrupt ni __end__, algo está mal
            else:
                logger.warning(f"⚠️ Flujo terminó sin __end__ para thread_id: {thread_id}")
                await ws.send_json({
                    "type": "done",
                    "message": "Análisis completado (flujo inesperado)"
                })
                await ws.close()
                return
                
        except Exception as e:
            logger.error(f"❌ Error en ejecución del grafo: {e}")
            await ws.send_json({
                "type": "error",
                "message": f"Error en procesamiento: {str(e)}"
            })
            await ws.close()
            return

async def handle_interrupt(ws: WebSocket, event: dict, thread_id: str) -> dict:
    """
    Maneja una interrupción individual de forma robusta
    """
    try:
        # Extraer datos de la interrupción
        interrupt_obj = event["__interrupt__"]
        
        # Determinar cómo acceder a los datos según el tipo
        if hasattr(interrupt_obj, 'value'):
            interrupt_data = interrupt_obj.value
        elif isinstance(interrupt_obj, list) and len(interrupt_obj) > 0:
            first_interrupt = interrupt_obj[0]
            if hasattr(first_interrupt, 'value'):
                interrupt_data = first_interrupt.value
            else:
                interrupt_data = str(first_interrupt)
        else:
            interrupt_data = str(interrupt_obj)
        
        logger.info(f"🛑 Interrupción en thread_id: {thread_id}")
        logger.info(f"🛑 Datos de interrupción: {interrupt_data}")
        
        # Enviar datos al usuario
        await ws.send_json({
            "type": "need_input",
            "payload": interrupt_data,
            "step": interrupt_data.get("current_step", "awaiting_input") if isinstance(interrupt_data, dict) else "awaiting_input"
        })
        
        # Esperar respuesta del usuario
        logger.info(f"⏳ Esperando input del usuario para thread_id: {thread_id}")
        user_input = await ws.receive_json()
        logger.info(f"📥 Input recibido del usuario: {user_input}")
        
        return user_input
        
    except WebSocketDisconnect:
        logger.info(f"🔌 Usuario desconectado durante interrupción en thread_id: {thread_id}")
        return None
    except Exception as e:
        logger.error(f"❌ Error manejando interrupción: {e}")
        await ws.send_json({
            "type": "error",
            "message": f"Error procesando interrupción: {str(e)}"
        })
        return None