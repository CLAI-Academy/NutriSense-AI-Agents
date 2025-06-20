#!/usr/bin/env python3
"""
Punto de entrada principal para NutriSense AI.
Ejecuta directamente el servidor desde server.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz del proyecto al path de Python
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Función principal que ejecuta server.py"""
    try:
        print("🚀 Ejecutando NutriSense AI Server...")
        print(f"📁 Directorio del proyecto: {project_root}")
        
        # Importar uvicorn para ejecutar el servidor
        import uvicorn
        
        # Ejecutar el servidor usando uvicorn
        uvicorn.run(
            "nutrisense_agents.api.server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que todas las dependencias estén instaladas:")
        print("   pip install fastapi uvicorn langgraph")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()