# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryConnectedToolsOperations - testing only public methods."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from azure.ai.agentserver.core.tools.client._models import (
    FoundryConnectedTool,
    FoundryToolDetails,
)
from azure.ai.agentserver.core.tools.client.operations._foundry_connected_tools import (
    FoundryConnectedToolsOperations,
)
from azure.ai.agentserver.core.tools._exceptions import OAuthConsentRequiredError, ToolInvocationError

from ...conftest import create_mock_http_response


class TestFoundryConnectedToolsOperationsListTools:
    """Tests for FoundryConnectedToolsOperations.list_tools public method."""

    @pytest.mark.asyncio
    async def test_list_tools_with_empty_list_returns_empty(self):
        """Test list_tools returns empty when tools list is empty."""
        mock_client = AsyncMock()
        ops = FoundryConnectedToolsOperations(mock_client)

        result = await ops.list_tools([], None, "test-agent")

        assert result == []
        # Should not make any HTTP request
        mock_client.send_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_tools_returns_tools_from_server(
        self,
        sample_connected_tool,
        sample_user_info
    ):
        """Test list_tools returns tools from server response."""
        mock_client = AsyncMock()

        response_data = {
            "tools": [
                {
                    "remoteServer": {
                        "protocol": sample_connected_tool.protocol,
                        "projectConnectionId": sample_connected_tool.project_connection_id
                    },
                    "manifest": [
                        {
                            "name": "remote_tool",
                            "description": "A remote connected tool",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "input": {"type": "string"}
                                }
                            }
                        }
                    ]
                }
            ]
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)
        result = list(await ops.list_tools([sample_connected_tool], sample_user_info, "test-agent"))

        assert len(result) == 1
        definition, details = result[0]
        assert definition == sample_connected_tool
        assert isinstance(details, FoundryToolDetails)
        assert details.name == "remote_tool"
        assert details.description == "A remote connected tool"

    @pytest.mark.asyncio
    async def test_list_tools_without_user_info(self, sample_connected_tool):
        """Test list_tools works without user info (local execution)."""
        mock_client = AsyncMock()

        response_data = {
            "tools": [
                {
                    "remoteServer": {
                        "protocol": sample_connected_tool.protocol,
                        "projectConnectionId": sample_connected_tool.project_connection_id
                    },
                    "manifest": [
                        {
                            "name": "tool_no_user",
                            "description": "Tool without user",
                            "parameters": {"type": "object", "properties": {}}
                        }
                    ]
                }
            ]
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)
        result = list(await ops.list_tools([sample_connected_tool], None, "test-agent"))

        assert len(result) == 1
        assert result[0][1].name == "tool_no_user"

    @pytest.mark.asyncio
    async def test_list_tools_with_multiple_connections(self, sample_user_info):
        """Test list_tools with multiple connected tool definitions."""
        mock_client = AsyncMock()

        tool1 = FoundryConnectedTool(protocol="mcp", project_connection_id="conn-1")
        tool2 = FoundryConnectedTool(protocol="a2a", project_connection_id="conn-2")

        response_data = {
            "tools": [
                {
                    "remoteServer": {
                        "protocol": "mcp",
                        "projectConnectionId": "conn-1"
                    },
                    "manifest": [
                        {
                            "name": "tool_from_conn1",
                            "description": "From connection 1",
                            "parameters": {"type": "object", "properties": {}}
                        }
                    ]
                },
                {
                    "remoteServer": {
                        "protocol": "a2a",
                        "projectConnectionId": "conn-2"
                    },
                    "manifest": [
                        {
                            "name": "tool_from_conn2",
                            "description": "From connection 2",
                            "parameters": {"type": "object", "properties": {}}
                        }
                    ]
                }
            ]
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)
        result = list(await ops.list_tools([tool1, tool2], sample_user_info, "test-agent"))

        assert len(result) == 2
        names = {r[1].name for r in result}
        assert names == {"tool_from_conn1", "tool_from_conn2"}

    @pytest.mark.asyncio
    async def test_list_tools_filters_by_connection_id(self, sample_user_info):
        """Test list_tools only returns tools from requested connections."""
        mock_client = AsyncMock()

        requested_tool = FoundryConnectedTool(protocol="mcp", project_connection_id="requested-conn")

        # Server returns tools from multiple connections, but we only requested one
        response_data = {
            "tools": [
                {
                    "remoteServer": {
                        "protocol": "mcp",
                        "projectConnectionId": "requested-conn"
                    },
                    "manifest": [
                        {
                            "name": "requested_tool",
                            "description": "Requested",
                            "parameters": {"type": "object", "properties": {}}
                        }
                    ]
                },
                {
                    "remoteServer": {
                        "protocol": "mcp",
                        "projectConnectionId": "unrequested-conn"
                    },
                    "manifest": [
                        {
                            "name": "unrequested_tool",
                            "description": "Not requested",
                            "parameters": {"type": "object", "properties": {}}
                        }
                    ]
                }
            ]
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)
        result = list(await ops.list_tools([requested_tool], sample_user_info, "test-agent"))

        # Should only return tools from requested connection
        assert len(result) == 1
        assert result[0][1].name == "requested_tool"

    @pytest.mark.asyncio
    async def test_list_tools_multiple_tools_per_connection(
        self,
        sample_connected_tool,
        sample_user_info
    ):
        """Test list_tools returns multiple tools from same connection."""
        mock_client = AsyncMock()

        response_data = {
            "tools": [
                {
                    "remoteServer": {
                        "protocol": sample_connected_tool.protocol,
                        "projectConnectionId": sample_connected_tool.project_connection_id
                    },
                    "manifest": [
                        {
                            "name": "tool_one",
                            "description": "First tool",
                            "parameters": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "tool_two",
                            "description": "Second tool",
                            "parameters": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "tool_three",
                            "description": "Third tool",
                            "parameters": {"type": "object", "properties": {}}
                        }
                    ]
                }
            ]
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)
        result = list(await ops.list_tools([sample_connected_tool], sample_user_info, "test-agent"))

        assert len(result) == 3
        names = {r[1].name for r in result}
        assert names == {"tool_one", "tool_two", "tool_three"}

    @pytest.mark.asyncio
    async def test_list_tools_raises_oauth_consent_error(
        self,
        sample_connected_tool,
        sample_user_info
    ):
        """Test list_tools raises OAuthConsentRequiredError when consent needed."""
        mock_client = AsyncMock()

        response_data = {
            "type": "OAuthConsentRequired",
            "toolResult": {
                "consentUrl": "https://login.microsoftonline.com/consent",
                "message": "User consent is required to access this resource",
                "projectConnectionId": sample_connected_tool.project_connection_id
            }
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)

        with pytest.raises(OAuthConsentRequiredError) as exc_info:
            list(await ops.list_tools([sample_connected_tool], sample_user_info, "test-agent"))

        assert exc_info.value.consent_url == "https://login.microsoftonline.com/consent"
        assert "consent" in exc_info.value.message.lower()


class TestFoundryConnectedToolsOperationsInvokeTool:
    """Tests for FoundryConnectedToolsOperations.invoke_tool public method."""

    @pytest.mark.asyncio
    async def test_invoke_tool_returns_result_value(
        self,
        sample_resolved_connected_tool,
        sample_user_info
    ):
        """Test invoke_tool returns the result value from server."""
        mock_client = AsyncMock()

        expected_result = {"data": "some output", "status": "success"}
        response_data = {"toolResult": expected_result}
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)
        result = await ops.invoke_tool(
            sample_resolved_connected_tool,
            {"input": "test"},
            sample_user_info,
            "test-agent"
        )

        assert result == expected_result

    @pytest.mark.asyncio
    async def test_invoke_tool_without_user_info(self, sample_resolved_connected_tool):
        """Test invoke_tool works without user info (local execution)."""
        mock_client = AsyncMock()

        response_data = {"toolResult": "local result"}
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)
        result = await ops.invoke_tool(
            sample_resolved_connected_tool,
            {},
            None,  # No user info
            "test-agent"
        )

        assert result == "local result"

    @pytest.mark.asyncio
    async def test_invoke_tool_with_complex_arguments(
        self,
        sample_resolved_connected_tool,
        sample_user_info
    ):
        """Test invoke_tool handles complex nested arguments."""
        mock_client = AsyncMock()

        response_data = {"toolResult": "processed"}
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)
        complex_args = {
            "query": "search term",
            "filters": {
                "date_range": {"start": "2025-01-01", "end": "2025-12-31"},
                "categories": ["A", "B", "C"]
            },
            "limit": 50
        }

        result = await ops.invoke_tool(
            sample_resolved_connected_tool,
            complex_args,
            sample_user_info,
            "test-agent"
        )

        assert result == "processed"
        mock_client.send_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_invoke_tool_returns_none_for_empty_result(
        self,
        sample_resolved_connected_tool,
        sample_user_info
    ):
        """Test invoke_tool returns None when server returns no result."""
        mock_client = AsyncMock()

        # Server returns empty response (no toolResult)
        response_data = {
            "toolResult": None
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)
        result = await ops.invoke_tool(
            sample_resolved_connected_tool,
            {},
            sample_user_info,
            "test-agent"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_invoke_tool_with_mcp_tool_raises_error(
        self,
        sample_resolved_mcp_tool,
        sample_user_info
    ):
        """Test invoke_tool raises ToolInvocationError for non-connected tool."""
        mock_client = AsyncMock()
        ops = FoundryConnectedToolsOperations(mock_client)

        with pytest.raises(ToolInvocationError) as exc_info:
            await ops.invoke_tool(
                sample_resolved_mcp_tool,
                {},
                sample_user_info,
                "test-agent"
            )

        assert "not a Foundry connected tool" in str(exc_info.value)
        # Should not make any HTTP request
        mock_client.send_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_invoke_tool_raises_oauth_consent_error(
        self,
        sample_resolved_connected_tool,
        sample_user_info
    ):
        """Test invoke_tool raises OAuthConsentRequiredError when consent needed."""
        mock_client = AsyncMock()

        response_data = {
            "type": "OAuthConsentRequired",
            "toolResult": {
                "consentUrl": "https://login.microsoftonline.com/oauth/consent",
                "message": "Please provide consent to continue",
                "projectConnectionId": "test-connection-id"
            }
        }
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)

        with pytest.raises(OAuthConsentRequiredError) as exc_info:
            await ops.invoke_tool(
                sample_resolved_connected_tool,
                {"input": "test"},
                sample_user_info,
                "test-agent"
            )

        assert "https://login.microsoftonline.com/oauth/consent" in exc_info.value.consent_url

    @pytest.mark.asyncio
    async def test_invoke_tool_with_different_agent_names(
        self,
        sample_resolved_connected_tool,
        sample_user_info
    ):
        """Test invoke_tool uses correct agent name in request."""
        mock_client = AsyncMock()

        response_data = {"toolResult": "result"}
        mock_response = create_mock_http_response(200, response_data)
        mock_client.send_request.return_value = mock_response
        mock_client.post.return_value = MagicMock()

        ops = FoundryConnectedToolsOperations(mock_client)

        # Invoke with different agent names
        for agent_name in ["agent-1", "my-custom-agent", "production-agent"]:
            await ops.invoke_tool(
                sample_resolved_connected_tool,
                {},
                sample_user_info,
                agent_name
            )

            # Verify the correct path was used
            call_args = mock_client.post.call_args
            assert agent_name in call_args[0][0]

