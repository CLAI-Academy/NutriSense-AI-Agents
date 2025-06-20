# nutrisense_agents/api/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Importar el router de análisis de imágenes
from nutrisense_agents.api.routes.img_analysis_route import router as img_analysis_router

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

# Incluir el router de análisis de imágenes
app.include_router(img_analysis_router)

if __name__ == "__main__":
    # Configuración del servidor
    uvicorn.run(
        "nutrisense_agents.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
