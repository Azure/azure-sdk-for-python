# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for _invoker.py - testing public methods of DefaultFoundryToolInvoker."""
import pytest
from unittest.mock import AsyncMock

from azure.ai.agentserver.core.tools.runtime._invoker import DefaultFoundryToolInvoker


class TestDefaultFoundryToolInvokerResolvedTool:
    """Tests for DefaultFoundryToolInvoker.resolved_tool property."""

    def test_resolved_tool_returns_tool_passed_at_init(
        self,
        sample_resolved_mcp_tool,
        mock_foundry_tool_client,
        mock_user_provider
    ):
        """Test resolved_tool property returns the tool passed during initialization."""
        invoker = DefaultFoundryToolInvoker(
            resolved_tool=sample_resolved_mcp_tool,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        assert invoker.resolved_tool is sample_resolved_mcp_tool

    def test_resolved_tool_returns_connected_tool(
        self,
        sample_resolved_connected_tool,
        mock_foundry_tool_client,
        mock_user_provider
    ):
        """Test resolved_tool property returns connected tool."""
        invoker = DefaultFoundryToolInvoker(
            resolved_tool=sample_resolved_connected_tool,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        assert invoker.resolved_tool is sample_resolved_connected_tool


class TestDefaultFoundryToolInvokerInvoke:
    """Tests for DefaultFoundryToolInvoker.invoke method."""

    @pytest.mark.asyncio
    async def test_invoke_calls_client_with_correct_arguments(
        self,
        sample_resolved_mcp_tool,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_user_info
    ):
        """Test invoke calls client.invoke_tool with correct arguments."""
        invoker = DefaultFoundryToolInvoker(
            resolved_tool=sample_resolved_mcp_tool,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )
        arguments = {"input": "test value", "count": 5}

        await invoker.invoke(arguments)

        mock_foundry_tool_client.invoke_tool.assert_called_once_with(
            sample_resolved_mcp_tool,
            arguments,
            "test-agent",
            sample_user_info
        )

    @pytest.mark.asyncio
    async def test_invoke_returns_result_from_client(
        self,
        sample_resolved_mcp_tool,
        mock_foundry_tool_client,
        mock_user_provider
    ):
        """Test invoke returns the result from client.invoke_tool."""
        expected_result = {"output": "test result", "status": "completed"}
        mock_foundry_tool_client.invoke_tool = AsyncMock(return_value=expected_result)

        invoker = DefaultFoundryToolInvoker(
            resolved_tool=sample_resolved_mcp_tool,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        result = await invoker.invoke({"input": "test"})

        assert result == expected_result

    @pytest.mark.asyncio
    async def test_invoke_with_empty_arguments(
        self,
        sample_resolved_mcp_tool,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_user_info
    ):
        """Test invoke works with empty arguments dictionary."""
        invoker = DefaultFoundryToolInvoker(
            resolved_tool=sample_resolved_mcp_tool,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        await invoker.invoke({})

        mock_foundry_tool_client.invoke_tool.assert_called_once_with(
            sample_resolved_mcp_tool,
            {},
            "test-agent",
            sample_user_info
        )

    @pytest.mark.asyncio
    async def test_invoke_with_none_user(
        self,
        sample_resolved_mcp_tool,
        mock_foundry_tool_client,
        mock_user_provider_none
    ):
        """Test invoke works when user provider returns None."""
        invoker = DefaultFoundryToolInvoker(
            resolved_tool=sample_resolved_mcp_tool,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider_none,
            agent_name="test-agent"
        )

        await invoker.invoke({"input": "test"})

        mock_foundry_tool_client.invoke_tool.assert_called_once_with(
            sample_resolved_mcp_tool,
            {"input": "test"},
            "test-agent",
            None
        )

    @pytest.mark.asyncio
    async def test_invoke_propagates_client_exception(
        self,
        sample_resolved_mcp_tool,
        mock_foundry_tool_client,
        mock_user_provider
    ):
        """Test invoke propagates exceptions from client.invoke_tool."""
        mock_foundry_tool_client.invoke_tool = AsyncMock(
            side_effect=RuntimeError("Client error")
        )

        invoker = DefaultFoundryToolInvoker(
            resolved_tool=sample_resolved_mcp_tool,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        with pytest.raises(RuntimeError, match="Client error"):
            await invoker.invoke({"input": "test"})

    @pytest.mark.asyncio
    async def test_invoke_with_complex_nested_arguments(
        self,
        sample_resolved_mcp_tool,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_user_info
    ):
        """Test invoke with complex nested argument structure."""
        complex_args = {
            "nested": {"key1": "value1", "key2": 123},
            "list": [1, 2, 3],
            "mixed": [{"a": 1}, {"b": 2}]
        }

        invoker = DefaultFoundryToolInvoker(
            resolved_tool=sample_resolved_mcp_tool,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        await invoker.invoke(complex_args)

        mock_foundry_tool_client.invoke_tool.assert_called_once_with(
            sample_resolved_mcp_tool,
            complex_args,
            "test-agent",
            sample_user_info
        )
