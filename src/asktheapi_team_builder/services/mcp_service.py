from fastmcp import FastMCP
from pydantic import BaseModel

from asktheapi_team_builder.core.api_spec_handler import APISpecHandler
from asktheapi_team_builder.core.tool_builder import build_tool_function

class MCPConfig(BaseModel):
    transport: str = "sse"
    port: int = 8000
    name: str = "asktheapi_mcp"
    
class MCPService():
    def __init__(self, mcp_config: MCPConfig):
        self.mcp = FastMCP(name=mcp_config.name, port=mcp_config.port)
        self.mcp_config = mcp_config
        self.api_spec_handler = APISpecHandler()
        
    async def _create_from_spec(self, url_spec: str, headers: dict = {}):
        spec_content = await self.api_spec_handler.download_url_spec(url_spec)
        classification_result = await self.api_spec_handler.classify_spec(spec_content)
        for group_spec in classification_result.specs:
            agent_result = await self.api_spec_handler.generate_agent_for_group(
                group_spec,
                spec_content
            )
            for tool in agent_result.tools:
                self.mcp.add_tool(build_tool_function(agent_result, tool, headers))
        
        return self.mcp
        
    async def _run_mcp(self):
        self.mcp.run(self.mcp_config.transport)
        
    async def start_from_spec(self, url_spec: str, headers: dict = {}):
        await self._create_from_spec(url_spec, headers)
        await self._run_mcp()