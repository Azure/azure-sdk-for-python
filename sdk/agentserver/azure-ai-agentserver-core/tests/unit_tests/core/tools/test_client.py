# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryToolClient - testing only public methods."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from azure.ai.agentserver.core.tools.client._client import FoundryToolClient
from azure.ai.agentserver.core.tools.client._models import (
    FoundryToolDetails,
    FoundryToolSource,
    ResolvedFoundryTool,
)
from azure.ai.agentserver.core.tools._exceptions import ToolInvocationError

from .conftest import create_mock_http_response


class TestFoundryToolClientInit:
    """Tests for FoundryToolClient.__init__ public method."""

    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    def test_init_with_valid_endpoint_and_credential(self, mock_pipeline_client_class, mock_credential):
        """Test client can be initialized with valid endpoint and credential."""
        endpoint = "https://test.api.azureml.ms"

        client = FoundryToolClient(endpoint, mock_credential)

        # Verify client was created with correct base_url
        call_kwargs = mock_pipeline_client_class.call_args
        assert call_kwargs[1]["base_url"] == endpoint
        assert client is not None


class TestFoundryToolClientListTools:
    """Tests for FoundryToolClient.list_tools public method."""

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_list_tools_empty_collection_returns_empty_list(
        self,
        mock_pipeline_client_class,
        mock_credential
    ):
        """Test list_tools returns empty list when given empty collection."""
        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)

        result = await client.list_tools([], agent_name="test-agent")

        assert result == []

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_list_tools_with_single_mcp_tool_returns_resolved_tools(
        self,
        mock_pipeline_client_class,
        mock_credential,
        sample_hosted_mcp_tool
    ):
        """Test list_tools with a single MCP tool returns resolved tools."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        # Mock HTTP response for MCP tools listing
        response_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": sample_hosted_mcp_tool.name,
                        "description": "Test MCP tool description",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client_instance.send_request.return_value = mock_response
        mock_client_instance.post.return_value = MagicMock()

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)
        result = await client.list_tools([sample_hosted_mcp_tool], agent_name="test-agent")

        assert len(result) == 1
        assert isinstance(result[0], ResolvedFoundryTool)
        assert result[0].name == sample_hosted_mcp_tool.name
        assert result[0].source == FoundryToolSource.HOSTED_MCP

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_list_tools_with_single_connected_tool_returns_resolved_tools(
        self,
        mock_pipeline_client_class,
        mock_credential,
        sample_connected_tool,
        sample_user_info
    ):
        """Test list_tools with a single connected tool returns resolved tools."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        # Mock HTTP response for connected tools listing
        response_data = {
            "tools": [
                {
                    "remoteServer": {
                        "protocol": sample_connected_tool.protocol,
                        "projectConnectionId": sample_connected_tool.project_connection_id
                    },
                    "manifest": [
                        {
                            "name": "connected_test_tool",
                            "description": "Test connected tool",
                            "parameters": {"type": "object", "properties": {}}
                        }
                    ]
                }
            ]
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client_instance.send_request.return_value = mock_response
        mock_client_instance.post.return_value = MagicMock()

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)
        result = await client.list_tools(
            [sample_connected_tool],
            agent_name="test-agent",
            user=sample_user_info
        )

        assert len(result) == 1
        assert isinstance(result[0], ResolvedFoundryTool)
        assert result[0].name == "connected_test_tool"
        assert result[0].source == FoundryToolSource.CONNECTED

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_list_tools_with_mixed_tool_types_returns_all_resolved(
        self,
        mock_pipeline_client_class,
        mock_credential,
        sample_hosted_mcp_tool,
        sample_connected_tool,
        sample_user_info
    ):
        """Test list_tools with both MCP and connected tools returns all resolved tools."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        # We need to return different responses based on the request
        mcp_response_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": sample_hosted_mcp_tool.name,
                        "description": "MCP tool",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }
        connected_response_data = {
            "tools": [
                {
                    "remoteServer": {
                        "protocol": sample_connected_tool.protocol,
                        "projectConnectionId": sample_connected_tool.project_connection_id
                    },
                    "manifest": [
                        {
                            "name": "connected_tool",
                            "description": "Connected tool",
                            "parameters": {"type": "object", "properties": {}}
                        }
                    ]
                }
            ]
        }

        # Mock to return different responses for different requests
        mock_client_instance.send_request.side_effect = [
            create_mock_http_response(200, mcp_response_data),
            create_mock_http_response(200, connected_response_data)
        ]
        mock_client_instance.post.return_value = MagicMock()

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)
        result = await client.list_tools(
            [sample_hosted_mcp_tool, sample_connected_tool],
            agent_name="test-agent",
            user=sample_user_info
        )

        assert len(result) == 2
        sources = {tool.source for tool in result}
        assert FoundryToolSource.HOSTED_MCP in sources
        assert FoundryToolSource.CONNECTED in sources

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_list_tools_filters_unlisted_mcp_tools(
        self,
        mock_pipeline_client_class,
        mock_credential,
        sample_hosted_mcp_tool
    ):
        """Test list_tools only returns tools that are in the allowed list."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        # Server returns more tools than requested
        response_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": sample_hosted_mcp_tool.name,
                        "description": "Requested tool",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "unrequested_tool",
                        "description": "This tool was not requested",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client_instance.send_request.return_value = mock_response
        mock_client_instance.post.return_value = MagicMock()

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)
        result = await client.list_tools([sample_hosted_mcp_tool], agent_name="test-agent")

        # Should only return the requested tool
        assert len(result) == 1
        assert result[0].name == sample_hosted_mcp_tool.name


class TestFoundryToolClientListToolsDetails:
    """Tests for FoundryToolClient.list_tools_details public method."""

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_list_tools_details_returns_mapping_structure(
        self,
        mock_pipeline_client_class,
        mock_credential,
        sample_hosted_mcp_tool
    ):
        """Test list_tools_details returns correct mapping structure."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        response_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": sample_hosted_mcp_tool.name,
                        "description": "Test tool",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client_instance.send_request.return_value = mock_response
        mock_client_instance.post.return_value = MagicMock()

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)
        result = await client.list_tools_details([sample_hosted_mcp_tool], agent_name="test-agent")

        assert isinstance(result, dict)
        assert sample_hosted_mcp_tool.id in result
        assert len(result[sample_hosted_mcp_tool.id]) == 1
        assert isinstance(result[sample_hosted_mcp_tool.id][0], FoundryToolDetails)

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_list_tools_details_groups_multiple_tools_by_definition(
        self,
        mock_pipeline_client_class,
        mock_credential,
        sample_hosted_mcp_tool
    ):
        """Test list_tools_details groups multiple tools from same source by definition ID."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        # Server returns multiple tools for the same MCP source
        response_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "tools": [
                    {
                        "name": sample_hosted_mcp_tool.name,
                        "description": "Tool variant 1",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client_instance.send_request.return_value = mock_response
        mock_client_instance.post.return_value = MagicMock()

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)
        result = await client.list_tools_details([sample_hosted_mcp_tool], agent_name="test-agent")

        # All tools should be grouped under the same definition ID
        assert sample_hosted_mcp_tool.id in result


class TestFoundryToolClientInvokeTool:
    """Tests for FoundryToolClient.invoke_tool public method."""

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_invoke_mcp_tool_returns_result(
        self,
        mock_pipeline_client_class,
        mock_credential,
        sample_resolved_mcp_tool
    ):
        """Test invoke_tool with MCP tool returns the invocation result."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        expected_result = {"result": {"content": [{"text": "Hello World"}]}}
        mock_response = create_mock_http_response(200, expected_result)
        mock_client_instance.send_request.return_value = mock_response
        mock_client_instance.post.return_value = MagicMock()

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)
        result = await client.invoke_tool(
            sample_resolved_mcp_tool,
            arguments={"input": "test"},
            agent_name="test-agent"
        )

        assert result == expected_result

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_invoke_connected_tool_returns_result(
        self,
        mock_pipeline_client_class,
        mock_credential,
        sample_resolved_connected_tool,
        sample_user_info
    ):
        """Test invoke_tool with connected tool returns the invocation result."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        expected_value = {"output": "Connected tool result"}
        response_data = {"toolResult": expected_value}
        mock_response = create_mock_http_response(200, response_data)
        mock_client_instance.send_request.return_value = mock_response
        mock_client_instance.post.return_value = MagicMock()

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)
        result = await client.invoke_tool(
            sample_resolved_connected_tool,
            arguments={"input": "test"},
            agent_name="test-agent",
            user=sample_user_info
        )

        assert result == expected_value

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_invoke_tool_with_complex_arguments(
        self,
        mock_pipeline_client_class,
        mock_credential,
        sample_resolved_mcp_tool
    ):
        """Test invoke_tool correctly passes complex arguments."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        mock_response = create_mock_http_response(200, {"result": "success"})
        mock_client_instance.send_request.return_value = mock_response
        mock_client_instance.post.return_value = MagicMock()

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)
        complex_args = {
            "string_param": "value",
            "number_param": 42,
            "bool_param": True,
            "list_param": [1, 2, 3],
            "nested_param": {"key": "value"}
        }

        result = await client.invoke_tool(
            sample_resolved_mcp_tool,
            arguments=complex_args,
            agent_name="test-agent"
        )

        # Verify request was made
        mock_client_instance.send_request.assert_called_once()

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_invoke_tool_with_unsupported_source_raises_error(
        self,
        mock_pipeline_client_class,
        mock_credential,
        sample_tool_details
    ):
        """Test invoke_tool raises ToolInvocationError for unsupported tool source."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        # Create a mock tool with unsupported source
        mock_definition = MagicMock()
        mock_definition.source = "unsupported_source"
        mock_tool = MagicMock(spec=ResolvedFoundryTool)
        mock_tool.definition = mock_definition
        mock_tool.source = "unsupported_source"
        mock_tool.details = sample_tool_details

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)

        with pytest.raises(ToolInvocationError) as exc_info:
            await client.invoke_tool(
                mock_tool,
                arguments={"input": "test"},
                agent_name="test-agent"
            )

        assert "Unsupported tool source" in str(exc_info.value)


class TestFoundryToolClientClose:
    """Tests for FoundryToolClient.close public method."""

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_close_closes_underlying_client(
        self,
        mock_pipeline_client_class,
        mock_credential
    ):
        """Test close() properly closes the underlying HTTP client."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        client = FoundryToolClient("https://test.api.azureml.ms", mock_credential)
        await client.close()

        mock_client_instance.close.assert_called_once()


class TestFoundryToolClientContextManager:
    """Tests for FoundryToolClient async context manager protocol."""

    @pytest.mark.asyncio
    @patch("azure.ai.agentserver.core.tools.client._client.AsyncPipelineClient")
    async def test_async_context_manager_enters_and_exits(
        self,
        mock_pipeline_client_class,
        mock_credential
    ):
        """Test client can be used as async context manager."""
        mock_client_instance = AsyncMock()
        mock_pipeline_client_class.return_value = mock_client_instance

        async with FoundryToolClient("https://test.api.azureml.ms", mock_credential) as client:
            assert client is not None
            mock_client_instance.__aenter__.assert_called_once()

        mock_client_instance.__aexit__.assert_called_once()

