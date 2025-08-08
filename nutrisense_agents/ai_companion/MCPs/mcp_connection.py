"""
Simple MCP Connection Manager with schema preprocessing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool


@dataclass
class MCPServerConfig:
    """Configuration for a remote MCP server"""
    name: str
    url: str
    transport: str = "sse"
    enabled: bool = True


class CustomMCPClient(MultiServerMCPClient):
    """Cliente MCP personalizado que intercepta y modifica schemas"""
    
    def __init__(self, config, user_uid: Optional[str] = None):
        super().__init__(config)
        self.user_uid = user_uid
        self.logger = logging.getLogger(__name__)
        self.tools_requiring_uid = {
            "add_planned_meal",
            "create_meal_plan", 
            "add_planned_meal_to_schedule",
            "optimize_meal_plan",
            "get_meal_plan_summary",
            "add_food_diary",
            "add_daily_summary",
            "get_user_data",
        }
    
    def _preprocess_tool_schema(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocessa el schema de la tool antes de crear BaseTool"""
        tool_name = tool_data.get("name", "")
        
        self.logger.debug(f"🔄 Preprocesando schema para tool: {tool_name}")
        self.logger.debug(f"📥 Schema original: {tool_data}")
        
        if tool_name not in self.tools_requiring_uid:
            self.logger.debug("⏩ Tool no requiere UID, devolviendo sin cambios")
            return tool_data
            
        if "input_schema" in tool_data:
            schema = tool_data["input_schema"]
            self.logger.debug(f"📋 Schema input original: {schema}")
            
            if "properties" in schema:
                original_props = list(schema["properties"].keys())
                self.logger.debug(f"🔑 Properties originales: {original_props}")
                
                filtered_properties = {
                    k: v for k, v in schema["properties"].items()
                    if k != "user_uuid"
                }
                schema["properties"] = filtered_properties
                
                self.logger.debug(f"🔑 Properties filtradas: {list(filtered_properties.keys())}")
                
            if "required" in schema:
                original_required = schema["required"]
                self.logger.debug(f"📌 Required original: {original_required}")
                
                schema["required"] = [
                    field for field in schema["required"]
                    if field != "user_uuid"
                ]
                
                self.logger.debug(f"📌 Required filtrado: {schema['required']}")
                
            self.logger.debug(f"📤 Schema final para {tool_name}: {schema}")
            
        return tool_data
    
    async def get_tools(self) -> List[BaseTool]:
        """Obtiene tools con schemas preprocessados"""
        raw_tools = await super().get_tools()
        
        if not self.user_uid:
            return raw_tools
            
        secured_tools = []
        for tool in raw_tools:
            if tool.name in self.tools_requiring_uid:
                secured_tools.append(self._wrap_tool_with_uid(tool))
            else:
                secured_tools.append(tool)
                
        return secured_tools
    
    def _wrap_tool_with_uid(self, raw_tool: BaseTool) -> BaseTool:
        """Wrapper simple que solo inyecta user_uuid sin modificar schema"""
        user_uid = self.user_uid  # Capture user_uid in closure
        
        class WrappedTool(BaseTool):
            name: str = raw_tool.name
            description: str = raw_tool.description
            
            def get_input_schema(self) -> dict:
                return raw_tool.get_input_schema()
                
            def _run(self, **kwargs) -> Any:
                full_payload = {**kwargs, "user_uuid": user_uid}
                return raw_tool.invoke(full_payload)
                
            async def _arun(self, **kwargs) -> Any:
                full_payload = {**kwargs, "user_uuid": user_uid}
                if hasattr(raw_tool, 'ainvoke'):
                    return await raw_tool.ainvoke(full_payload)
                else:
                    return raw_tool.invoke(full_payload)
        
        return WrappedTool()


class MCPConnectionManager:
    """Manager actualizado que usa CustomMCPClient"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client: Optional[CustomMCPClient] = None
        self.tools: List[BaseTool] = []
        self.is_connected = False
        self.user_uid: Optional[str] = None
        
        # Default server configurations
        self.server_configs = {
            "nutrisense_server": MCPServerConfig(
                name="nutrisense_server", 
                url="http://localhost:8000/mcp",
                transport="streamable_http"
            )
        }
    
    def configure_servers(self, servers: Dict[str, MCPServerConfig]) -> None:
        """Configure MCP servers"""
        self.server_configs.update(servers)
        self.logger.info(f"Configured {len(servers)} MCP servers")
    
    async def connect(self, user_uid: Optional[str] = None) -> None:
        """Connect to MCP servers with optional user_uid"""
        if self.is_connected and self.user_uid == user_uid:
            return
            
        self.user_uid = user_uid
        
        # Build client configuration
        client_config = {}
        for name, config in self.server_configs.items():
            if config.enabled:
                client_config[name] = {
                    "url": config.url,
                    "transport": config.transport
                }
        
        if not client_config:
            self.logger.warning("No MCP servers configured")
            return
        
        try:
            # Usar nuestro cliente personalizado
            self.client = CustomMCPClient(client_config, user_uid)
            self.tools = await self.client.get_tools()
            self.is_connected = True
            
            self.logger.info(f"Connected to MCP servers: {len(self.tools)} tools available")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP servers: {e}")
            raise
    
    def get_tools(self) -> List[BaseTool]:
        """Get all available tools from connected servers"""
        if not self.is_connected:
            self.logger.warning("Not connected to MCP servers")
            return []
        
        return self.tools
    
    async def disconnect(self) -> None:
        """Disconnect from MCP servers"""
        if self.client and self.is_connected:
            try:
                self.logger.info("Disconnected from MCP servers")
            except Exception as e:
                self.logger.error(f"Error disconnecting from MCP servers: {e}")
            finally:
                self.client = None
                self.tools = []
                self.is_connected = False
                self.user_uid = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get connection status"""
        return {
            "connected": self.is_connected,
            "configured_servers": list(self.server_configs.keys()),
            "tools_count": len(self.tools),
            "user_uid": self.user_uid
        }


# Global instance
mcp_connection = MCPConnectionManager()