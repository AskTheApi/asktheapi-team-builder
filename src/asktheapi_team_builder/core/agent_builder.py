from typing import Dict, List, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from .models import Agent, Message
from .tool_builder import build_tool_function

class AgentBuilder:
    """Handles the creation and management of AutoGen agents"""
    
    def __init__(self, model: str = "gpt-4", model_config: Optional[Dict] = None):
        """
        Initialize the agent builder
        
        Args:
            model: The OpenAI model to use
            model_config: Additional configuration for the model client
        """
        self.model_config = model_config or {}
        self.model_client = OpenAIChatCompletionClient(
            model=model,
            **self.model_config
        )
    
    async def build_agent(
        self,
        agent_spec: Agent,
        headers: Optional[Dict[str, str]] = None
    ) -> AssistantAgent:
        """
        Build an AutoGen agent from specifications
        
        Args:
            agent_spec: The agent specification
            headers: Optional headers to include in tool requests
            
        Returns:
            An AutoGen AssistantAgent instance
        """
        tools = []
        for tool in agent_spec.tools:
            fn = await build_tool_function(agent_spec, tool, headers)
            tools.append(fn)
            
        return AssistantAgent(
            name=agent_spec.name.replace(' ', ''),
            description=agent_spec.description,
            model_client=self.model_client,
            tools=tools,
            system_message=agent_spec.system_prompt,
            reflect_on_tool_use=True
        )
        
    async def run_agent(
        self,
        agent: AssistantAgent,
        messages: List[Message]
    ):
        """
        Run an agent with a list of messages
        
        Args:
            agent: The AutoGen agent to run
            messages: List of messages to process
        """
        formatted_msgs = [
            TextMessage(source=msg.role, content=msg.content)
            for msg in messages
        ]
        await agent.run(task=formatted_msgs) 