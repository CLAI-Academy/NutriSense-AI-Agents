"""
MCP Tools Helper – utilidades para trabajar con MCP tools en LangGraph.

Soluciona fallo: `tool() got an unexpected keyword argument 'name'` usando la
forma correcta de envolver la función (`tool(name=..., description=...)(fn)`).
"""

from typing import List, Dict, Any, Optional
import logging

from langchain_core.tools import BaseTool, tool

from .mcp_connection import mcp_connection

# Configurar logging
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tools que necesitan inyección de UID
# ---------------------------------------------------------------------------
TOOLS_REQUIRING_UID = {
    "add_planned_meal",
    "create_meal_plan",
    "add_planned_meal_to_schedule",
    "optimize_meal_plan",
    "get_meal_plan_summary",
    "add_food_diary",
    "add_daily_summary",
    "get_user_data",
}

# ---------------------------------------------------------------------------
# Wrapping helper (forma compatible con decorator factory)
# ---------------------------------------------------------------------------

def _wrap_tool_with_uid(raw_tool: BaseTool, user_uid: str) -> BaseTool:
    """Crea un wrapper seguro que inyecta `user_uuid` sin exponerlo al LLM."""

    # Crear una nueva clase que herede de BaseTool
    class WrappedTool(BaseTool):
        name: str = raw_tool.name
        description: str = raw_tool.description
        
        def _run(self, **kwargs) -> Any:
            """Método síncrono - no usado pero requerido por BaseTool"""
            # Debug: Mostrar qué argumentos recibimos
            logger.error(f"🔧 DEBUG {self.name}: Argumentos recibidos en _run: {kwargs}")
            
            # Crear el payload completo con user_uuid
            full_payload = {**kwargs, "user_uuid": user_uid}
            logger.error(f"🔧 DEBUG {self.name}: Payload completo en _run: {full_payload}")
            
            try:
                result = raw_tool.invoke(full_payload)
                logger.error(f"🔧 DEBUG {self.name}: Resultado exitoso en _run: {result}")
                return result
            except Exception as e:
                logger.error(f"🔧 DEBUG {self.name}: Error en _run: {e}")
                raise
                
        async def _arun(self, **kwargs) -> Any:
            """Método asíncrono principal"""
            # Debug: Mostrar qué argumentos recibimos
            logger.error(f"🔧 DEBUG {self.name}: Argumentos recibidos en _arun: {kwargs}")
            
            # Crear el payload completo con user_uuid
            full_payload = {**kwargs, "user_uuid": user_uid}
            logger.error(f"🔧 DEBUG {self.name}: Payload completo en _arun: {full_payload}")
            
            try:
                # Intentar usar ainvoke primero
                if hasattr(raw_tool, 'ainvoke'):
                    result = await raw_tool.ainvoke(full_payload)
                else:
                    result = raw_tool.invoke(full_payload)
                logger.error(f"🔧 DEBUG {self.name}: Resultado exitoso en _arun: {result}")
                return result
            except Exception as e:
                logger.error(f"🔧 DEBUG {self.name}: Error en _arun: {e}")
                raise
    
    return WrappedTool()

# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

async def get_mcp_tools(user_uid: Optional[str] = None) -> List[BaseTool]:
    """Devuelve la lista de tools MCP, envolviendo las que requieren UID."""

    if not mcp_connection.is_connected:
        await mcp_connection.connect()

    raw_tools = mcp_connection.get_tools()

    # Si no vamos a inyectar UID, devolvemos tal cual
    if user_uid is None:
        return raw_tools

    secured: List[BaseTool] = []
    for raw in raw_tools:
        if raw.name in TOOLS_REQUIRING_UID:
            secured.append(_wrap_tool_with_uid(raw, user_uid))
        else:
            secured.append(raw)
    return secured


async def initialize_mcp_tools(
    server_configs: Optional[Dict[str, Any]] = None,
    user_uid: Optional[str] = None,
) -> List[BaseTool]:
    """Conecta a los servidores MCP indicados y devuelve las tools protegidas."""

    if server_configs:
        from .mcp_connection import MCPServerConfig

        configs = {name: MCPServerConfig(**cfg) for name, cfg in server_configs.items()}
        mcp_connection.configure_servers(configs)

    await mcp_connection.connect()
    return await get_mcp_tools(user_uid)


# ---------------------------------------------------------------------------
# Utilidades de estado
# ---------------------------------------------------------------------------

def get_mcp_status() -> Dict[str, Any]:
    """Devuelve el estado actual de la conexión MCP."""
    return mcp_connection.get_status()


async def cleanup_mcp_connections() -> None:
    """Cierra todas las conexiones MCP activas."""
    await mcp_connection.disconnect()
