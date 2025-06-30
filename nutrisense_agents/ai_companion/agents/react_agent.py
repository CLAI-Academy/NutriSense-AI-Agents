import asyncio
from nutrisense_agents.api.services.react_agent_service import create_nutrisense_react_agent_service

# Para mantener compatibilidad con código existente
# UID obtenido desde tu sesión, frontend, JWT, etc.
USER_UID = "user_abc123"

# Crear el grafo usando el servicio
graph = asyncio.run(create_nutrisense_react_agent_service(USER_UID))