"""
MCP Tools Helper - versión simplificada sin wrappers complejos
"""

from typing import List, Dict, Any, Optional
import logging
import sys

from langchain_core.tools import BaseTool

from .mcp_connection import mcp_connection

logger = logging.getLogger(__name__)

async def get_mcp_tools(user_uid: Optional[str] = None) -> List[BaseTool]:
    """Devuelve tools MCP con schemas ya procesados"""
    
    # Conectar con user_uid para preprocessar schemas
    await mcp_connection.connect(user_uid)
    
    # Tools ya vienen con schemas limpios y wrappers aplicados
    return mcp_connection.get_tools()


async def initialize_mcp_tools(
    server_configs: Optional[Dict[str, Any]] = None,
    user_uid: Optional[str] = None,
) -> List[BaseTool]:
    """Inicializa MCP tools con configuración opcional"""
    
    if server_configs:
        from .mcp_connection import MCPServerConfig
        configs = {name: MCPServerConfig(**cfg) for name, cfg in server_configs.items()}
        mcp_connection.configure_servers(configs)
    
    return await get_mcp_tools(user_uid)


def get_mcp_status() -> Dict[str, Any]:
    """Estado de conexión MCP"""
    return mcp_connection.get_status()


async def cleanup_mcp_connections() -> None:
    """Limpia conexiones MCP"""
    await mcp_connection.disconnect()
