from typing import List, Dict, Any, Tuple
import yaml
import json
import aiohttp
from pydantic import BaseModel
from asktheapi_team_builder.prompts.agents_apispec_prompt import CLASSIFY_SPEC_SYSTEM, CLASSIFY_SPEC_USER, GENERATE_AGENT_FOR_SPEC_SYSTEM, GENERATE_AGENT_FOR_SPEC_USER
from asktheapi_team_builder.services.llm_service import LLMService
from asktheapi_team_builder.services.open_ai_service import OpenAIService

class APISpecClassification(BaseModel):
    name: str
    description: str
    paths: List[str]

class APISpecClassificationResult(BaseModel):
    specs: List[APISpecClassification]

class APISpecAgentToolResult(BaseModel):
    name: str
    description: str
    jsonschema: dict
    path: str
    method: str
    
class APISpecAgentResult(BaseModel):
    name: str
    description: str
    system_prompt: str
    user_prompt: str
    tools: List[APISpecAgentToolResult]

class APISpecHandler:
    def __init__(self, headers: dict = {}):
        self.llm_service = LLMService(openai_service=OpenAIService(), llm_headers=headers)

    async def download_url_spec(self, url: str) -> dict:
        """Download and parse OpenAPI spec from URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                
                    try:
                        # Try parsing as YAML first
                        spec = yaml.safe_load(response_text)
                    except yaml.YAMLError:
                        # If YAML fails, try JSON
                        spec = json.loads(response_text)
                        
                    return spec
                
        except Exception as e:
            raise Exception(f"Failed to download or parse spec: {str(e)}")

    def get_components_for_paths(self, paths: List[str], content: dict) -> Tuple[List[dict], dict]:
        """Extract components and paths from OpenAPI spec."""
        components = {}
        
        filtered_paths = [p for p in paths if p in content['paths']]
        
        for path in filtered_paths:
            path_obj = content['paths'][path]
            
            for method in path_obj:
                method_obj = path_obj[method]
                
                # Check request body refs
                if 'requestBody' in method_obj:
                    request_body = method_obj['requestBody']
                    if 'content' in request_body:
                        for content_type in request_body['content']:
                            schema = request_body['content'][content_type].get('schema', {})
                            if '$ref' in schema:
                                ref_name = schema['$ref'].split('/')[-1]
                                if ref_name in content['components']['schemas']:
                                    components[ref_name] = content['components']['schemas'][ref_name]
                
                # Check response refs
                if 'responses' in method_obj:
                    for response_code in method_obj['responses']:
                        response = method_obj['responses'][response_code]
                        if 'content' in response:
                            for content_type in response['content']:
                                schema = response['content'][content_type].get('schema', {})
                                if '$ref' in schema:
                                    ref_name = schema['$ref'].split('/')[-1]
                                    if ref_name in content['components']['schemas']:
                                        components[ref_name] = content['components']['schemas'][ref_name]
                
                # Check parameters refs
                if 'parameters' in method_obj:
                    for param in method_obj['parameters']:
                        if 'schema' in param and '$ref' in param['schema']:
                            ref_name = param['schema']['$ref'].split('/')[-1]
                            if ref_name in content['components']['schemas']:
                                components[ref_name] = content['components']['schemas'][ref_name]
                                
        path_content = [{"path": p, "content": content['paths'][p]} for p in filtered_paths]
        return path_content, components

    async def classify_spec(self, content: dict) -> APISpecClassificationResult:
        """Classify API endpoints into logical groups."""
        if not self.llm_service:
            raise ValueError("LLM service is required for classification")

        messages = [{
            "role": "system",
            "content": CLASSIFY_SPEC_SYSTEM.format(current_groups="")
        }, {
            "role": "user",
            "content": CLASSIFY_SPEC_USER.format(spec_info=json.dumps(content['paths']))
        }]
        
        llm_response = await self.llm_service.chat_completion("gpt-4o-mini", messages, False)
        response = llm_response.choices[0].message.content
        return APISpecClassificationResult.model_validate_json(response)

    async def generate_agent_for_group(self, 
                                     group_spec: APISpecClassification, 
                                     content: dict) -> APISpecAgentResult:
        """Generate an agent for a group of related endpoints."""
        if not self.llm_service:
            raise ValueError("LLM service is required for agent generation")

        paths, components = self.get_components_for_paths(group_spec.paths, content)
        messages = [{
            "role": "system",
            "content": GENERATE_AGENT_FOR_SPEC_SYSTEM
        }, {
            "role": "user",
            "content": GENERATE_AGENT_FOR_SPEC_USER.format(
                paths=paths, 
                components=components, 
                security=content.get('securitySchemes', {})
            )
        }]
        
        llm_response = await self.llm_service.chat_completion("gpt-4o-mini", messages, False)
        response = llm_response.choices[0].message.content
        return APISpecAgentResult.model_validate_json(response) 