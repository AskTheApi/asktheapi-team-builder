import pytest
from asktheapi_team_builder.services.llm_service import LLMService
from unittest.mock import AsyncMock

@pytest.fixture
def llm_service(mock_openai_service):
    return LLMService(mock_openai_service)

@pytest.mark.asyncio
async def test_chat_completion(llm_service, mock_openai_service):
    # Arrange
    model = "gpt-4"
    messages = [{"role": "user", "content": "test"}]
    stream = False
    
    # Act
    result = await llm_service.chat_completion(model, messages, stream)
    
    # Assert
    mock_openai_service.completion_with_headers.assert_called_once_with(
        model=model,
        messages=messages,
        stream=stream,
        headers={}
    )
    assert result is not None

@pytest.mark.asyncio
async def test_chat_completion_with_custom_headers():
    # Arrange
    custom_headers = {"custom-header": "value"}
    mock_openai = AsyncMock()
    service = LLMService(mock_openai, custom_headers)
    
    # Act
    await service.chat_completion("gpt-4", [], False)
    
    # Assert
    mock_openai.completion_with_headers.assert_called_once_with(
        model="gpt-4",
        messages=[],
        stream=False,
        headers=custom_headers
    ) 