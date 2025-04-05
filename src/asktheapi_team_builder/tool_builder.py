from typing import Callable, Dict, Optional
from urllib.parse import urljoin
from .models import Agent, Tool
from .http_client import perform_call

async def build_tool_function(
    agent: Agent,
    tool: Tool,
    headers: Optional[Dict[str, str]] = None
) -> Callable:
    """
    Builds a dynamic function from a tool specification
    
    Args:
        agent: Agent configuration
        tool: Tool specification
        headers: Optional headers to include in all requests
        
    Returns:
        A callable function that implements the tool
    """
    namespace = {}
    agent_name = tool.name.replace(' ', '')
    
    if agent.base_url:
        full_url = urljoin(f"{agent.base_url.rstrip('/')}/", tool.path.lstrip('/'))
    else:
        full_url = tool.path
        
    exec(f"""
async def {agent_name}(path_params: dict | None = None, query_params: dict | None = None, body: dict | None = None):
    '''
        {tool.description}
        
        The input schema is:
        {str(tool.jsonschema)}
    '''
    return await perform_call(
        "{tool.method}",
        "{full_url}",
        path_params,
        query_params,
        body,
        {str(headers) if headers else "None"}
    )
    """, globals(), namespace)
    
    return namespace[agent_name] 