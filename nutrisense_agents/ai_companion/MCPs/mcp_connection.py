"""
Simple MCP Connection Manager for remote HTTP streameable servers
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
    transport: str = "sse"  # Server-Sent Events for HTTP streaming
    enabled: bool = True


class MCPConnectionManager:
    """Simple manager for MCP server connections"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client: Optional[MultiServerMCPClient] = None
        self.tools: List[BaseTool] = []
        self.is_connected = False
        
        # Default server configurations - adjust URLs as needed
        self.server_configs = {
            "reddit_MCP": MCPServerConfig(
                name="nutrisense_server", 
                url="http://localhost:8000/mcp",
                transport="streamable_http"
            )
        }
    
    def configure_servers(self, servers: Dict[str, MCPServerConfig]) -> None:
        """Configure MCP servers"""
        self.server_configs.update(servers)
        self.logger.info(f"Configured {len(servers)} MCP servers")
    
    async def connect(self) -> None:
        """Connect to all configured MCP servers"""
        if self.is_connected:
            self.logger.info("Already connected to MCP servers")
            return
        
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
            self.client = MultiServerMCPClient(client_config)
            
            # Get all available tools using the new API
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
                # No need for __aexit__ in new API
                self.logger.info("Disconnected from MCP servers")
            except Exception as e:
                self.logger.error(f"Error disconnecting from MCP servers: {e}")
            finally:
                self.client = None
                self.tools = []
                self.is_connected = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get connection status"""
        return {
            "connected": self.is_connected,
            "configured_servers": list(self.server_configs.keys()),
            "tools_count": len(self.tools)
        }


# Global instance
mcp_connection = MCPConnectionManager()