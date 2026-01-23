# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryToolCallWrapper and FoundryToolNodeWrappers."""
import pytest
from typing import Any, List
from unittest.mock import AsyncMock, MagicMock

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

from azure.ai.agentserver.langgraph.tools._tool_node import (
    FoundryToolCallWrapper,
    FoundryToolNodeWrappers,
)


@pytest.mark.unit
class TestFoundryToolCallWrapper:
    """Tests for FoundryToolCallWrapper class."""

    def test_as_wrappers_returns_typed_dict(self):
        """Test that as_wrappers returns a FoundryToolNodeWrappers TypedDict."""
        foundry_tools = [{"type": "code_interpreter"}]
        wrapper = FoundryToolCallWrapper(foundry_tools)

        result = wrapper.as_wrappers()

        assert isinstance(result, dict)
        assert "wrap_tool_call" in result
        assert "awrap_tool_call" in result
        assert callable(result["wrap_tool_call"])
        assert callable(result["awrap_tool_call"])

    def test_call_tool_with_already_resolved_tool(self):
        """Test that call_tool passes through when tool is already resolved."""
        foundry_tools = [{"type": "code_interpreter"}]
        wrapper = FoundryToolCallWrapper(foundry_tools)

        # Create request with tool already set
        @tool
        def existing_tool(x: str) -> str:
            """Existing tool."""
            return f"Result: {x}"

        mock_request = MagicMock(spec=ToolCallRequest)
        mock_request.tool = existing_tool
        mock_request.tool_call = {"name": "existing_tool", "id": "call_1"}

        expected_result = ToolMessage(content="Result: test", tool_call_id="call_1")
        mock_invocation = MagicMock(return_value=expected_result)

        result = wrapper.call_tool(mock_request, mock_invocation)

        # Should pass through original request
        mock_invocation.assert_called_once_with(mock_request)
        assert result == expected_result

    def test_call_tool_with_no_foundry_tools(self):
        """Test that call_tool passes through when no foundry tools configured."""
        foundry_tools: List[Any] = []
        wrapper = FoundryToolCallWrapper(foundry_tools)

        mock_request = MagicMock(spec=ToolCallRequest)
        mock_request.tool = None
        mock_request.tool_call = {"name": "some_tool", "id": "call_1"}

        expected_result = ToolMessage(content="Result", tool_call_id="call_1")
        mock_invocation = MagicMock(return_value=expected_result)

        result = wrapper.call_tool(mock_request, mock_invocation)

        mock_invocation.assert_called_once_with(mock_request)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_call_tool_async_with_already_resolved_tool(self):
        """Test that call_tool_async passes through when tool is already resolved."""
        foundry_tools = [{"type": "code_interpreter"}]
        wrapper = FoundryToolCallWrapper(foundry_tools)

        @tool
        def existing_tool(x: str) -> str:
            """Existing tool."""
            return f"Result: {x}"

        mock_request = MagicMock(spec=ToolCallRequest)
        mock_request.tool = existing_tool
        mock_request.tool_call = {"name": "existing_tool", "id": "call_1"}

        expected_result = ToolMessage(content="Async Result", tool_call_id="call_1")
        mock_invocation = AsyncMock(return_value=expected_result)

        result = await wrapper.call_tool_async(mock_request, mock_invocation)

        mock_invocation.assert_awaited_once_with(mock_request)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_call_tool_async_with_no_foundry_tools(self):
        """Test that call_tool_async passes through when no foundry tools configured."""
        foundry_tools: List[Any] = []
        wrapper = FoundryToolCallWrapper(foundry_tools)

        mock_request = MagicMock(spec=ToolCallRequest)
        mock_request.tool = None
        mock_request.tool_call = {"name": "some_tool", "id": "call_1"}

        expected_result = ToolMessage(content="Result", tool_call_id="call_1")
        mock_invocation = AsyncMock(return_value=expected_result)

        result = await wrapper.call_tool_async(mock_request, mock_invocation)

        mock_invocation.assert_awaited_once_with(mock_request)
        assert result == expected_result

    def test_call_tool_returns_command_result(self):
        """Test that call_tool can return Command objects."""
        foundry_tools: List[Any] = []
        wrapper = FoundryToolCallWrapper(foundry_tools)

        mock_request = MagicMock(spec=ToolCallRequest)
        mock_request.tool = None
        mock_request.tool_call = {"name": "some_tool", "id": "call_1"}

        # Return a Command instead of ToolMessage
        expected_result = Command(goto="next_node")
        mock_invocation = MagicMock(return_value=expected_result)

        result = wrapper.call_tool(mock_request, mock_invocation)

        assert result == expected_result
        assert isinstance(result, Command)


@pytest.mark.unit
class TestFoundryToolNodeWrappers:
    """Tests for FoundryToolNodeWrappers TypedDict."""

    def test_foundry_tool_node_wrappers_structure(self):
        """Test that FoundryToolNodeWrappers has the expected structure."""
        foundry_tools = [{"type": "code_interpreter"}]
        wrapper = FoundryToolCallWrapper(foundry_tools)

        wrappers: FoundryToolNodeWrappers = wrapper.as_wrappers()

        # Should have both sync and async wrappers
        assert "wrap_tool_call" in wrappers
        assert "awrap_tool_call" in wrappers

        # Should be the wrapper methods
        assert wrappers["wrap_tool_call"] == wrapper.call_tool
        assert wrappers["awrap_tool_call"] == wrapper.call_tool_async

    def test_wrappers_can_be_unpacked_to_tool_node(self):
        """Test that wrappers can be unpacked as kwargs to ToolNode."""
        foundry_tools = [{"type": "code_interpreter"}]
        wrapper = FoundryToolCallWrapper(foundry_tools)

        wrappers = wrapper.as_wrappers()

        # Should be usable as kwargs
        assert len(wrappers) == 2

        # This pattern is used: ToolNode([], **wrappers)
        def mock_tool_node_init(tools, wrap_tool_call=None, awrap_tool_call=None):
            return {
                "tools": tools,
                "wrap_tool_call": wrap_tool_call,
                "awrap_tool_call": awrap_tool_call,
            }

        result = mock_tool_node_init([], **wrappers)

        assert result["wrap_tool_call"] is not None
        assert result["awrap_tool_call"] is not None

