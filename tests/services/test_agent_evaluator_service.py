import pytest
from asktheapi_team_builder.services.agent_evaluator_service import AgentEvaluatorService
from asktheapi_team_builder.types import TextMessage, ToolCallExecutionEvent
from autogen_core.models import FunctionExecutionResult
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_needs_evaluation_task_result_no_errors(agent_evaluator_service, sample_task_result):
    # Act
    result = agent_evaluator_service.needs_evaluation_task_result(sample_task_result)
    
    # Assert
    assert result is False

@pytest.mark.asyncio
async def test_needs_evaluation_task_result_with_text_error(agent_evaluator_service, sample_task_result):
    # Arrange
    task_result = sample_task_result
    task_result.messages.append(TextMessage(content="An error occurred", source="test_agent"))
    
    # Act
    result = agent_evaluator_service.needs_evaluation_task_result(task_result)
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_needs_evaluation_task_result_with_tool_error(agent_evaluator_service, sample_task_result):
    # Arrange
    task_result = sample_task_result
    task_result.messages.append(ToolCallExecutionEvent(content=[
                FunctionExecutionResult(call_id="call1", is_error=True, content="Error ocurred", name="test_function")
            ], source="test_agent"))
    
    # Act
    result = agent_evaluator_service.needs_evaluation_task_result(task_result)
    
    # Assert
    assert result is True

@pytest.mark.asyncio
async def test_evaluate_task_result(agent_evaluator_service, sample_agent, sample_task_result, mock_llm_service):
    # Arrange
    mock_llm_service.chat_completion.return_value = AsyncMock(
        choices=[MagicMock(message=MagicMock(content='{"evaluation": []}'))]
    )
    
    # Act
    result = await agent_evaluator_service.evaluate_task_result([sample_agent], sample_task_result)
    
    # Assert
    assert result is not None
    mock_llm_service.chat_completion.assert_called_once()
    assert "test_agent" in str(mock_llm_service.chat_completion.call_args)

@pytest.mark.asyncio
async def test_evaluate_task_result_error_handling(agent_evaluator_service, sample_agent, sample_task_result, mock_llm_service):
    # Arrange
    mock_llm_service.chat_completion.side_effect = Exception("Evaluation error")
    
    # Act & Assert
    await agent_evaluator_service.evaluate_task_result([sample_agent], sample_task_result)