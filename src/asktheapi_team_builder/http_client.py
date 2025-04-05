import aiohttp
from typing import Optional, Dict, Any

async def perform_call(
    method: str,
    url: str,
    path_params: Optional[Dict[str, Any]] = None,
    query_params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Performs an HTTP call with the given parameters
    
    Args:
        method: HTTP method to use
        url: Base URL for the request
        path_params: Parameters to replace in the URL path
        query_params: Query string parameters
        body: Request body
        headers: Request headers
        
    Returns:
        JSON response from the server
    """
    if not headers:
        headers = {}
        
    if path_params:
        for param, value in path_params.items():
            url = url.replace(f"{{{param}}}", str(value))
        
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=method,
            url=url,
            params=query_params,
            json=body,
            headers=headers
        ) as response:
            return await response.json() 