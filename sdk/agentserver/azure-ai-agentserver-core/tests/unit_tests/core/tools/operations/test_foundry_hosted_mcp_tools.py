# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryMcpToolsOperations - testing only public methods."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from azure.ai.agentserver.core.tools.client._models import (
    FoundryHostedMcpTool,
    FoundryToolDetails,
    ResolvedFoundryTool,
    SchemaDefinition,
    SchemaProperty,
    SchemaType,
)
from azure.ai.agentserver.core.tools.client.operations._foundry_hosted_mcp_tools import (
    FoundryMcpToolsOperations,
)
from azure.ai.agentserver.core.tools._exceptions import ToolInvocationError

from ..conftest import create_mock_http_response


class TestFoundryMcpToolsOperationsListTools:
    """Tests for FoundryMcpToolsOperations.list_tools public method."""

    @pytest.mark.asyncio
    async def test_list_tools_with_empty_list_returns_empty(self):
        """Test list_tools returns empty when allowed_tools is empty."""
        mock_client = AsyncMock()
        ops = FoundryMcpToolsOperations(mock_client)

        result = await ops.list_tools([])

        assert result == []
        # Should not make any HTTP request
        mock_client.send_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_tools_returns_matching_tools(self, sample_hosted_mcp_tool):
        """Test list_tools returns tools that match the allowed list."""
        mock_client = AsyncMock()

        response_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": sample_hosted_mcp_tool.name,
                        "description": "Test MCP tool",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"}
                            }
                        }
                    }
                ]
            }
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryMcpToolsOperations(mock_client)
        result = list(await ops.list_tools([sample_hosted_mcp_tool]))

        assert len(result) == 1
        definition, details = result[0]
        assert definition == sample_hosted_mcp_tool
        assert isinstance(details, FoundryToolDetails)
        assert details.name == sample_hosted_mcp_tool.name
        assert details.description == "Test MCP tool"

    @pytest.mark.asyncio
    async def test_list_tools_filters_out_non_allowed_tools(self, sample_hosted_mcp_tool):
        """Test list_tools only returns tools in the allowed list."""
        mock_client = AsyncMock()

        # Server returns multiple tools but only one is allowed
        response_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": sample_hosted_mcp_tool.name,
                        "description": "Allowed tool",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "other_tool_not_in_list",
                        "description": "Not allowed tool",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "another_unlisted_tool",
                        "description": "Also not allowed",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryMcpToolsOperations(mock_client)
        result = list(await ops.list_tools([sample_hosted_mcp_tool]))

        assert len(result) == 1
        assert result[0][1].name == sample_hosted_mcp_tool.name

    @pytest.mark.asyncio
    async def test_list_tools_with_multiple_allowed_tools(self):
        """Test list_tools with multiple tools in allowed list."""
        mock_client = AsyncMock()

        tool1 = FoundryHostedMcpTool(name="tool_one")
        tool2 = FoundryHostedMcpTool(name="tool_two")

        response_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": "tool_one",
                        "description": "First tool",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "tool_two",
                        "description": "Second tool",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryMcpToolsOperations(mock_client)
        result = list(await ops.list_tools([tool1, tool2]))

        assert len(result) == 2
        names = {r[1].name for r in result}
        assert names == {"tool_one", "tool_two"}

    @pytest.mark.asyncio
    async def test_list_tools_preserves_tool_metadata(self):
        """Test list_tools preserves metadata from server response."""
        mock_client = AsyncMock()

        tool = FoundryHostedMcpTool(name="tool_with_meta")

        response_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": "tool_with_meta",
                        "description": "Tool with metadata",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "param1": {"type": "string"}
                            },
                            "required": ["param1"]
                        },
                        "_meta": {
                            "type": "object",
                            "properties": {
                                "model": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryMcpToolsOperations(mock_client)
        result = list(await ops.list_tools([tool]))

        assert len(result) == 1
        details = result[0][1]
        assert details.metadata is not None


class TestFoundryMcpToolsOperationsInvokeTool:
    """Tests for FoundryMcpToolsOperations.invoke_tool public method."""

    @pytest.mark.asyncio
    async def test_invoke_tool_returns_server_response(self, sample_resolved_mcp_tool):
        """Test invoke_tool returns the response from server."""
        mock_client = AsyncMock()

        expected_response = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "content": [{"type": "text", "text": "Hello World"}]
            }
        }
        mock_response = create_mock_http_response(200, expected_response)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryMcpToolsOperations(mock_client)
        result = await ops.invoke_tool(sample_resolved_mcp_tool, {"query": "test"})

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_invoke_tool_with_empty_arguments(self, sample_resolved_mcp_tool):
        """Test invoke_tool works with empty arguments."""
        mock_client = AsyncMock()

        expected_response = {"result": "success"}
        mock_response = create_mock_http_response(200, expected_response)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryMcpToolsOperations(mock_client)
        result = await ops.invoke_tool(sample_resolved_mcp_tool, {})

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_invoke_tool_with_complex_arguments(self, sample_resolved_mcp_tool):
        """Test invoke_tool handles complex nested arguments."""
        mock_client = AsyncMock()

        mock_response = create_mock_http_response(200, {"result": "ok"})
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryMcpToolsOperations(mock_client)
        complex_args = {
            "text": "sample text",
            "options": {
                "temperature": 0.7,
                "max_tokens": 100
            },
            "tags": ["tag1", "tag2"]
        }

        result = await ops.invoke_tool(sample_resolved_mcp_tool, complex_args)

        assert result == {"result": "ok"}
        mock_client.send_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_invoke_tool_with_connected_tool_raises_error(
        self,
        sample_resolved_connected_tool
    ):
        """Test invoke_tool raises ToolInvocationError for non-MCP tool."""
        mock_client = AsyncMock()
        ops = FoundryMcpToolsOperations(mock_client)

        with pytest.raises(ToolInvocationError) as exc_info:
            await ops.invoke_tool(sample_resolved_connected_tool, {})

        assert "not a Foundry-hosted MCP tool" in str(exc_info.value)
        # Should not make any HTTP request
        mock_client.send_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_invoke_tool_with_configuration_and_metadata(self):
        """Test invoke_tool handles tool with configuration and metadata."""
        mock_client = AsyncMock()

        # Create tool with configuration
        tool_def = FoundryHostedMcpTool(
            name="image_generation",
            configuration={"model_deployment_name": "dall-e-3"}
        )

        # Create tool details with metadata schema
        meta_schema = SchemaDefinition(
            type=SchemaType.OBJECT,
            properties={
                "model": SchemaProperty(type=SchemaType.STRING)
            }
        )
        details = FoundryToolDetails(
            name="image_generation",
            description="Generate images",
            input_schema=SchemaDefinition(type=SchemaType.OBJECT, properties={}),
            metadata=meta_schema
        )
        resolved_tool = ResolvedFoundryTool(definition=tool_def, details=details)

        mock_response = create_mock_http_response(200, {"result": "image_url"})
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryMcpToolsOperations(mock_client)
        result = await ops.invoke_tool(resolved_tool, {"prompt": "a cat"})

        assert result == {"result": "image_url"}

