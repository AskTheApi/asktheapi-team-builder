from typing import List, Optional, Sequence, Union, AsyncGenerator
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage
from autogen_agentchat.teams import SelectorGroupChat

from .models import Agent, Message
from .agent_builder import AgentBuilder

class TeamBuilder:
    """Handles the creation and management of AutoGen agent teams"""
    
    def __init__(self, model: str = "gpt-4", model_config: Optional[dict] = None):
        """
        Initialize the team builder
        
        Args:
            model: The OpenAI model to use
            model_config: Additional configuration for the model client
        """
        self.agent_builder = AgentBuilder(model, model_config)
        
    def _get_team_members_description(self, agents: List[Agent]) -> str:
        """Generate a description of team members for the planning agent"""
        return "\n".join([
            f"{agent.name}: {agent.description}"
            for agent in agents
        ])
        
    async def _get_planning_agent(self, agents: List[Agent]) -> AssistantAgent:
        """Create the planning agent that coordinates the team"""
        system_message = f"""You are a task planning agent that coordinates a team of specialized agents.
Your role is to:
1. Analyze the user's request
2. Break down complex tasks into smaller subtasks
3. Delegate subtasks to appropriate team members
4. Monitor progress and ensure task completion

Available team members:
{self._get_team_members_description(agents)}

When delegating tasks:
- Consider each agent's specialization
- Provide clear instructions
- Include any necessary context
- Specify expected outputs

You must be the first to engage when given a new task.
Type 'TERMINATE' when the overall task is complete."""
        
        return AssistantAgent(
            "PlanningAgent",
            description="An agent for planning tasks and coordinating team members",
            model_client=self.agent_builder.model_client,
            system_message=system_message,
            reflect_on_tool_use=True
        )
        
    def _selector_func(self, messages: Sequence[AgentEvent | ChatMessage]) -> str | None:
        """Determine which agent should speak next"""
        if messages[-1].source != "PlanningAgent":
            return "PlanningAgent"
        return None
        
    async def build_team(
        self,
        agents: List[Agent],
        headers: Optional[dict] = None
    ) -> SelectorGroupChat:
        """
        Build a team of agents that can work together
        
        Args:
            agents: List of agent specifications
            headers: Optional headers to include in tool requests
            
        Returns:
            A SelectorGroupChat instance representing the team
        """
        autogen_agents = []
        for agent in agents:
            autogen_agents.append(
                await self.agent_builder.build_agent(agent, headers)
            )
            
        planning_agent = await self._get_planning_agent(agents)
        text_termination = TextMentionTermination("TERMINATE")
        
        return SelectorGroupChat(
            [planning_agent] + autogen_agents,
            model_client=self.agent_builder.model_client,
            termination_condition=text_termination,
            selector_func=self._selector_func,
            max_turns=10
        )
        
    async def run_team(
        self,
        team: SelectorGroupChat,
        messages: List[Message],
        stream: bool = False
    ) -> Union[AsyncGenerator[AgentEvent | ChatMessage | TaskResult, None], TaskResult]:
        """
        Run a team of agents with a list of messages
        
        Args:
            team: The team to run
            messages: List of messages to process
            stream: Whether to stream the results
            
        Returns:
            Either a generator of events or the final result
        """
        formatted_msgs = [
            TextMessage(source=msg.role, content=msg.content)
            for msg in messages
        ]
        
        if stream:
            return team.run_stream(task=formatted_msgs)
        else:
            return await team.run(task=formatted_msgs) 