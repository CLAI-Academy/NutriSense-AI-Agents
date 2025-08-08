# nutrisense_agents/api/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Importar routers
from nutrisense_agents.api.routes.food_analysis_route import router as food_analysis_router
from nutrisense_agents.api.routes.react_agent_route import router as react_agent_router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI principal
app = FastAPI(
    title="NutriSense AI API",
    description="API para análisis nutricional con IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raíz para verificar que el servidor está funcionando"""
    return {
        "message": "NutriSense AI API está funcionando",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Endpoint de salud para monitoreo"""
    return {
        "status": "healthy",
        "service": "NutriSense AI API"
    }

# Incluir routers
app.include_router(food_analysis_router)
app.include_router(react_agent_router)

if __name__ == "__main__":
    # Configuración del servidor
    uvicorn.run(
        "nutrisense_agents.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
