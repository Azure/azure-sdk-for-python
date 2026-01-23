# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryToolBindingMiddleware."""
import pytest
from typing import Any, List
from unittest.mock import AsyncMock, MagicMock

from langchain.agents.middleware.types import ModelRequest
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt.tool_node import ToolCallRequest

from azure.ai.agentserver.langgraph.tools._middleware import FoundryToolBindingMiddleware

from .conftest import FakeChatModel


@pytest.mark.unit
class TestFoundryToolBindingMiddleware:
    """Tests for FoundryToolBindingMiddleware class."""

    def test_init_with_foundry_tools_creates_dummy_tool(self):
        """Test that initialization with foundry tools creates a dummy tool."""
        foundry_tools = [{"type": "code_interpreter"}]

        middleware = FoundryToolBindingMiddleware(foundry_tools)

        # Should have one dummy tool
        assert len(middleware.tools) == 1
        assert middleware.tools[0].name == "__dummy_tool_by_foundry_middleware__"

    def test_init_without_foundry_tools_no_dummy_tool(self):
        """Test that initialization without foundry tools creates no dummy tool."""
        foundry_tools: List[Any] = []

        middleware = FoundryToolBindingMiddleware(foundry_tools)

        assert len(middleware.tools) == 0

    def test_wrap_model_call_wraps_model_with_foundry_binding(self):
        """Test that wrap_model_call wraps the model correctly."""
        foundry_tools = [{"type": "code_interpreter"}]
        middleware = FoundryToolBindingMiddleware(foundry_tools)

        # Create mock model and request
        mock_model = FakeChatModel()
        mock_runtime = MagicMock()
        mock_request = MagicMock(spec=ModelRequest)
        mock_request.model = mock_model
        mock_request.runtime = mock_runtime
        mock_request.tools = []

        # Create a modified request to return
        modified_request = MagicMock(spec=ModelRequest)
        mock_request.override = MagicMock(return_value=modified_request)

        # Mock handler
        expected_result = AIMessage(content="Result")
        mock_handler = MagicMock(return_value=expected_result)

        result = middleware.wrap_model_call(mock_request, mock_handler)

        # Handler should be called with modified request
        mock_handler.assert_called_once()
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_awrap_model_call_wraps_model_async(self):
        """Test that awrap_model_call wraps the model correctly in async."""
        foundry_tools = [{"type": "code_interpreter"}]
        middleware = FoundryToolBindingMiddleware(foundry_tools)

        # Create mock model and request
        mock_model = FakeChatModel()
        mock_runtime = MagicMock()
        mock_request = MagicMock(spec=ModelRequest)
        mock_request.model = mock_model
        mock_request.runtime = mock_runtime
        mock_request.tools = []

        # Create a modified request to return
        modified_request = MagicMock(spec=ModelRequest)
        mock_request.override = MagicMock(return_value=modified_request)

        # Mock async handler
        expected_result = AIMessage(content="Async Result")
        mock_handler = AsyncMock(return_value=expected_result)

        result = await middleware.awrap_model_call(mock_request, mock_handler)

        # Handler should be called
        mock_handler.assert_awaited_once()
        assert result == expected_result

    def test_wrap_model_without_foundry_tools_returns_unchanged(self):
        """Test that wrap_model returns unchanged request when no foundry tools."""
        foundry_tools: List[Any] = []
        middleware = FoundryToolBindingMiddleware(foundry_tools)

        mock_model = FakeChatModel()
        mock_request = MagicMock(spec=ModelRequest)
        mock_request.model = mock_model
        mock_request.tools = []

        # Should not call override
        mock_request.override = MagicMock()

        mock_handler = MagicMock(return_value=AIMessage(content="Result"))

        middleware.wrap_model_call(mock_request, mock_handler)

        # Handler should be called with original request
        mock_handler.assert_called_once_with(mock_request)

    def test_remove_dummy_tool_from_request(self):
        """Test that dummy tool is removed from the request tools."""
        foundry_tools = [{"type": "code_interpreter"}]
        middleware = FoundryToolBindingMiddleware(foundry_tools)

        # Create request with dummy tool
        dummy = middleware._dummy_tool()

        @tool
        def real_tool(x: str) -> str:
            """Real tool."""
            return x

        mock_request = MagicMock(spec=ModelRequest)
        mock_request.tools = [dummy, real_tool]

        # Call internal method
        result = middleware._remove_dummy_tool(mock_request)

        # Should only have real_tool
        assert len(result) == 1
        assert result[0] is real_tool

    def test_wrap_tool_call_delegates_to_wrapper(self):
        """Test that wrap_tool_call delegates to FoundryToolCallWrapper."""
        foundry_tools = [{"type": "code_interpreter"}]
        middleware = FoundryToolBindingMiddleware(foundry_tools)

        # Create mock tool call request
        mock_request = MagicMock(spec=ToolCallRequest)
        mock_request.tool = None
        mock_request.tool_call = {"name": "test_tool", "id": "call_1"}
        mock_request.state = {}
        mock_request.runtime = None

        # Mock handler
        expected_result = ToolMessage(content="Result", tool_call_id="call_1")
        mock_handler = MagicMock(return_value=expected_result)

        result = middleware.wrap_tool_call(mock_request, mock_handler)

        # Handler should be called
        mock_handler.assert_called_once()
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_awrap_tool_call_delegates_to_wrapper_async(self):
        """Test that awrap_tool_call delegates to FoundryToolCallWrapper async."""
        foundry_tools = [{"type": "code_interpreter"}]
        middleware = FoundryToolBindingMiddleware(foundry_tools)

        # Create mock tool call request
        mock_request = MagicMock(spec=ToolCallRequest)
        mock_request.tool = None
        mock_request.tool_call = {"name": "test_tool", "id": "call_1"}
        mock_request.state = {}
        mock_request.runtime = None

        # Mock async handler
        expected_result = ToolMessage(content="Async Result", tool_call_id="call_1")
        mock_handler = AsyncMock(return_value=expected_result)

        result = await middleware.awrap_tool_call(mock_request, mock_handler)

        # Handler should be awaited
        mock_handler.assert_awaited_once()
        assert result == expected_result

    def test_middleware_with_multiple_foundry_tools(self):
        """Test middleware initialization with multiple foundry tools."""
        foundry_tools = [
            {"type": "code_interpreter"},
            {"type": "mcp", "project_connection_id": "test"},
        ]

        middleware = FoundryToolBindingMiddleware(foundry_tools)

        # Should still only have one dummy tool
        assert len(middleware.tools) == 1
        # But should have all foundry tools registered
        assert len(middleware._foundry_tools_to_bind) == 2

