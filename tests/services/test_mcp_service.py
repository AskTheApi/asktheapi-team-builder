import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from asktheapi_team_builder.services.mcp_service import MCPService, MCPConfig
from asktheapi_team_builder.core.api_spec_handler import APISpecHandler

@pytest.fixture
def mock_api_spec_handler():
    handler = AsyncMock(spec=APISpecHandler)
    handler.download_url_spec.return_value = "mock_spec_content"
    handler.classify_spec.return_value = MagicMock(
        specs=[
            MagicMock(
                group_name="test_group",
                endpoints=["/test"]
            )
        ]
    )
    handler.generate_agent_for_group.return_value = MagicMock(
        tools=[
            MagicMock(
                name="test_tool",
                description="A test tool",
                method="GET",
                path="/test",
                jsonschema={}
            )
        ]
    )
    return handler

@pytest.fixture
def mock_fast_mcp():
    with patch("asktheapi_team_builder.services.mcp_service.FastMCP") as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance

@pytest.fixture
def mcp_service(mock_fast_mcp, mock_api_spec_handler):
    with patch("asktheapi_team_builder.services.mcp_service.APISpecHandler", return_value=mock_api_spec_handler):
        config = MCPConfig(transport="sse", port=8000, name="test_mcp")
        service = MCPService(config)
        return service

@pytest.mark.asyncio
async def test_mcp_service_initialization(mcp_service, mock_fast_mcp):
    # Assert
    assert mcp_service.mcp_config.name == "test_mcp"
    assert mcp_service.mcp_config.port == 8000
    assert mcp_service.mcp_config.transport == "sse"

@pytest.mark.asyncio
async def test_create_from_spec(mcp_service, mock_api_spec_handler, mock_fast_mcp):
    # Arrange
    url_spec = "http://example.com/spec"
    headers = {"Authorization": "Bearer token"}
    
    # Act
    result = await mcp_service._create_from_spec(url_spec, headers)
    
    # Assert
    mock_api_spec_handler.download_url_spec.assert_called_once_with(url_spec)
    mock_api_spec_handler.classify_spec.assert_called_once_with("mock_spec_content")
    mock_api_spec_handler.generate_agent_for_group.assert_called_once()
    assert result == mock_fast_mcp
    # Verify that add_tool was called
    assert mock_fast_mcp.add_tool.called

@pytest.mark.asyncio
async def test_run_mcp(mcp_service, mock_fast_mcp):
    # Act
    await mcp_service._run_mcp()
    
    # Assert
    mock_fast_mcp.run.assert_called_once_with("sse")

@pytest.mark.asyncio
async def test_start_from_spec(mcp_service, mock_api_spec_handler):
    # Arrange
    url_spec = "http://example.com/spec"
    headers = {"Authorization": "Bearer token"}
    
    # Act
    await mcp_service.start_from_spec(url_spec, headers)
    
    # Assert
    mock_api_spec_handler.download_url_spec.assert_called_once_with(url_spec)
    mcp_service.mcp.run.assert_called_once_with("sse")

@pytest.mark.asyncio
async def test_mcp_config_defaults():
    # Act
    config = MCPConfig()
    
    # Assert
    assert config.transport == "sse"
    assert config.port == 8000
    assert config.name == "asktheapi_mcp" 