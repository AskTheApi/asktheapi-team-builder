from openai import AsyncOpenAI
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from asktheapi_team_builder.services.open_ai_service import OpenAIService

@pytest.fixture()
def openai_service():
    service = OpenAIService()
    service.client = AsyncOpenAI()
    service.client.chat.completions = AsyncMock()
    return service

@pytest.mark.asyncio
async def test_completion_with_headers(openai_service):
    # Arrange
    model = "gpt-4"
    messages = [{"role": "user", "content": "test"}]
    stream = False
    headers = {"test-header": "value"}
    
    # Act
    result = await openai_service.completion_with_headers(model, messages, stream, headers)
    
    # Assert
    openai_service.client.chat.completions.create.assert_called_once_with(
        model=model,
        messages=messages,
        stream=stream,
        extra_headers=headers,
        response_format={'type': 'json_object'}
    )
    assert result is not None

@pytest.mark.asyncio
async def test_completion_with_headers_error_handling(openai_service):
    # Arrange
    openai_service.client.chat.completions.create.side_effect = Exception("API Error")
    
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await openai_service.completion_with_headers("gpt-4", [], False, {})
    assert str(exc_info.value) == "API Error" 