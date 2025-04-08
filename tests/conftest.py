import os
from autogen_core import FunctionCall
from autogen_core.models import FunctionExecutionResult
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from asktheapi_team_builder.services.open_ai_service import OpenAIService
from asktheapi_team_builder.services.llm_service import LLMService
from asktheapi_team_builder.services.agent_evaluator_service import AgentEvaluatorService, AgentDTO, AgentToolDTO, TaskResult, TextMessage, ToolCallExecutionEvent, ToolCallRequestEvent

@pytest.fixture(autouse=True)
def setenvvar(monkeypatch):
    with patch.dict(os.environ, clear=True):
        envvars = {
            "OPENAI_API_KEY": "mock-api-key",
            "OPENAI_BASE_URL": "mock-base-url"
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield 
        
@pytest.fixture
def mock_openai_service():
    service = AsyncMock(spec=OpenAIService)
    service.completion_with_headers.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=['{"evaluation": []}']))]
    )
    return service

@pytest.fixture
def mock_llm_service():
    return AsyncMock(spec=LLMService)

@pytest.fixture
def agent_evaluator_service(mock_llm_service):
    service = AgentEvaluatorService()
    service.llm_service = mock_llm_service
    return service

@pytest.fixture
def sample_agent_tool():
    return AgentToolDTO(
        id="tool1",
        name="test_tool",
        description="A test tool",
        method="GET",
        path="/test",
        jsonschema={},
        auto_updated=False
    )

@pytest.fixture
def sample_agent(sample_agent_tool):
    return AgentDTO(
        id="agent1",
        name="test_agent",
        system_prompt="You are a test agent",
        description="A test agent",
        base_url="http://test.com",
        tools=[sample_agent_tool],
        apispec_id="spec1",
        auto_updated=False
    )

@pytest.fixture
def sample_task_result():
    return TaskResult(
        messages=[
            TextMessage(content="Test message", source="test_agent"),
            ToolCallRequestEvent(content=[FunctionCall(
                name="test_function", arguments="{}", id="call1")
            ], source="test_agent"),
            ToolCallExecutionEvent(content=[
                FunctionExecutionResult(call_id="call1", is_error=False, content="Success", name="test_function")
            ], source="test_agent")
        ]
    ) 