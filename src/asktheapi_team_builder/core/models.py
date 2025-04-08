from pydantic import BaseModel
from typing import List, Optional

class Tool(BaseModel):
    """Represents a tool that can be used by an agent"""
    name: str
    description: str
    method: str
    path: str
    jsonschema: dict

class Agent(BaseModel):
    """Represents an agent with its configuration"""
    name: str
    description: str
    system_prompt: str
    base_url: Optional[str] = None
    tools: List[Tool] = []

class Message(BaseModel):
    """Represents a chat message"""
    role: str
    content: str 