# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for use_foundry_tools builder function."""
import pytest
from typing import List


from azure.ai.agentserver.langgraph.tools._builder import use_foundry_tools
from azure.ai.agentserver.langgraph.tools._chat_model import FoundryToolLateBindingChatModel
from azure.ai.agentserver.langgraph.tools._middleware import FoundryToolBindingMiddleware
from azure.ai.agentserver.langgraph.tools._resolver import get_registry

from .conftest import FakeChatModel


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the global registry before and after each test."""
    registry = get_registry()
    registry.clear()
    yield
    registry.clear()


@pytest.mark.unit
class TestUseFoundryTools:
    """Tests for use_foundry_tools function."""

    def test_use_foundry_tools_with_tools_only_returns_middleware(self):
        """Test that passing only tools returns FoundryToolBindingMiddleware."""
        tools = [{"type": "code_interpreter"}]

        result = use_foundry_tools(tools)

        assert isinstance(result, FoundryToolBindingMiddleware)

    def test_use_foundry_tools_with_model_and_tools_returns_chat_model(self):
        """Test that passing model and tools returns FoundryToolLateBindingChatModel."""
        model = FakeChatModel()
        tools = [{"type": "code_interpreter"}]

        result = use_foundry_tools(model, tools)  # type: ignore

        assert isinstance(result, FoundryToolLateBindingChatModel)

    def test_use_foundry_tools_with_model_but_no_tools_raises_error(self):
        """Test that passing model without tools raises ValueError."""
        model = FakeChatModel()

        with pytest.raises(ValueError, match="Tools must be provided"):
            use_foundry_tools(model, None)  # type: ignore

    def test_use_foundry_tools_registers_tools_in_global_registry(self):
        """Test that tools are registered in the global registry."""
        tools = [
            {"type": "code_interpreter"},
            {"type": "mcp", "project_connection_id": "test"},
        ]

        use_foundry_tools(tools)

        registry = get_registry()
        assert len(registry) == 2

    def test_use_foundry_tools_with_model_registers_tools(self):
        """Test that tools are registered when using with model."""
        model = FakeChatModel()
        tools = [{"type": "code_interpreter"}]

        use_foundry_tools(model, tools)  # type: ignore

        registry = get_registry()
        assert len(registry) == 1

    def test_use_foundry_tools_with_empty_tools_list(self):
        """Test using with empty tools list."""
        tools: List = []

        result = use_foundry_tools(tools)

        assert isinstance(result, FoundryToolBindingMiddleware)
        assert len(get_registry()) == 0

    def test_use_foundry_tools_with_mcp_tools(self):
        """Test using with MCP connected tools."""
        tools = [
            {
                "type": "mcp",
                "project_connection_id": "MicrosoftLearn",
            },
        ]

        result = use_foundry_tools(tools)

        assert isinstance(result, FoundryToolBindingMiddleware)

    def test_use_foundry_tools_with_mixed_tool_types(self):
        """Test using with a mix of different tool types."""
        tools = [
            {"type": "code_interpreter"},
            {"type": "mcp", "project_connection_id": "MicrosoftLearn"},
        ]

        result = use_foundry_tools(tools)

        assert isinstance(result, FoundryToolBindingMiddleware)
        assert len(get_registry()) == 2

