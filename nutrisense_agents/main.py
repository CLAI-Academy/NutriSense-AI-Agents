from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from nutrisense_agents.api.routes import router as api_router
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NutriSense AI API",
    description="API para análisis nutricional con IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "NutriSense AI API está funcionando",
        "version": "1.0.0",
        "status": "active",
        "protocols": ["HTTP", "WebSocket"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "NutriSense AI API"
    }

app.include_router(api_router)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Cliente WebSocket conectado. Total conexiones: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Cliente WebSocket desconectado. Total conexiones: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Mensaje WebSocket recibido: {data}")
            try:
                message = json.loads(data)
                response = {
                    "type": "response",
                    "message": f"Mensaje recibido: {message.get('message', 'Sin mensaje')}",
                    "timestamp": str(datetime.now())
                }
                await manager.send_personal_message(json.dumps(response), websocket)
            except json.JSONDecodeError:
                await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/analysis")
async def websocket_analysis_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Análisis WebSocket recibido: {data}")
            try:
                message = json.loads(data)
                response = {
                    "type": "analysis_result",
                    "data": message,
                    "status": "processed",
                    "timestamp": str(datetime.now())
                }
                await manager.send_personal_message(json.dumps(response), websocket)
            except Exception as e:
                error_response = {
                    "type": "error",
                    "message": str(e),
                    "timestamp": str(datetime.now())
                }
                await manager.send_personal_message(json.dumps(error_response), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    import os
    
    # CRÍTICO: Leer puerto de variable de entorno
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"Iniciando servidor en puerto {port}...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,  # NO hardcodeado!
        log_level="info"
    )
