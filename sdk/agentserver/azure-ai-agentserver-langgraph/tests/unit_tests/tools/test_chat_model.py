# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryToolLateBindingChatModel."""
import pytest
from typing import Any, List, Optional
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool

from azure.ai.agentserver.core.tools import (
    FoundryHostedMcpTool,
    FoundryToolDetails,
    ResolvedFoundryTool,
    SchemaDefinition,
    SchemaProperty,
    SchemaType,
)
from azure.ai.agentserver.langgraph._context import LanggraphRunContext
from azure.ai.agentserver.langgraph.tools._chat_model import FoundryToolLateBindingChatModel
from azure.ai.agentserver.langgraph.tools._context import FoundryToolContext
from azure.ai.agentserver.langgraph.tools._resolver import ResolvedTools

from .conftest import FakeChatModel


@pytest.mark.unit
class TestFoundryToolLateBindingChatModel:
    """Tests for FoundryToolLateBindingChatModel class."""

    def test_llm_type_property(self):
        """Test the _llm_type property returns correct value."""
        delegate = FakeChatModel()
        foundry_tools = [{"type": "code_interpreter"}]

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        assert "foundry_tool_binding_model" in model._llm_type
        assert "fake_chat_model" in model._llm_type

    def test_bind_tools_records_tools(self):
        """Test that bind_tools records tools for later use."""
        delegate = FakeChatModel()
        foundry_tools = [{"type": "code_interpreter"}]

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        @tool
        def my_tool(x: str) -> str:
            """My tool."""
            return x

        result = model.bind_tools([my_tool], tool_choice="auto")

        # Should return self for chaining
        assert result is model
        # Tools should be recorded
        assert len(model._bound_tools) == 1
        assert model._bound_kwargs.get("tool_choice") == "auto"

    def test_bind_tools_multiple_times(self):
        """Test binding tools multiple times accumulates them."""
        delegate = FakeChatModel()
        foundry_tools = [{"type": "code_interpreter"}]

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        @tool
        def tool1(x: str) -> str:
            """Tool 1."""
            return x

        @tool
        def tool2(x: str) -> str:
            """Tool 2."""
            return x

        model.bind_tools([tool1])
        model.bind_tools([tool2])

        assert len(model._bound_tools) == 2

    def test_tool_node_property(self):
        """Test that tool_node property returns a ToolNode."""
        delegate = FakeChatModel()
        foundry_tools = [{"type": "code_interpreter"}]

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        tool_node = model.tool_node

        # Should return a ToolNode
        assert tool_node is not None

    def test_tool_node_wrapper_property(self):
        """Test that tool_node_wrapper returns correct wrappers."""
        delegate = FakeChatModel()
        foundry_tools = [{"type": "code_interpreter"}]

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        wrappers = model.tool_node_wrapper

        assert "wrap_tool_call" in wrappers
        assert "awrap_tool_call" in wrappers
        assert callable(wrappers["wrap_tool_call"])
        assert callable(wrappers["awrap_tool_call"])

    def test_invoke_with_context(
        self,
        mock_langgraph_run_context: LanggraphRunContext,
        sample_code_interpreter_tool: FoundryHostedMcpTool,
    ):
        """Test invoking model with context attached."""
        delegate = FakeChatModel(
            responses=[AIMessage(content="Hello from model!")],
        )
        foundry_tools = [{"type": "code_interpreter"}]

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        # Attach context to config
        config: RunnableConfig = {"configurable": {}}
        mock_langgraph_run_context.attach_to_config(config)

        input_messages = [HumanMessage(content="Hello")]
        result = model.invoke(input_messages, config=config)

        assert result.content == "Hello from model!"

    @pytest.mark.asyncio
    async def test_ainvoke_with_context(
        self,
        mock_langgraph_run_context: LanggraphRunContext,
    ):
        """Test async invoking model with context attached."""
        delegate = FakeChatModel(
            responses=[AIMessage(content="Async hello from model!")],
        )
        foundry_tools = [{"type": "code_interpreter"}]

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        # Attach context to config
        config: RunnableConfig = {"configurable": {}}
        mock_langgraph_run_context.attach_to_config(config)

        input_messages = [HumanMessage(content="Hello")]
        result = await model.ainvoke(input_messages, config=config)

        assert result.content == "Async hello from model!"

    def test_invoke_without_context_and_no_foundry_tools(self):
        """Test invoking model without context and no foundry tools."""
        delegate = FakeChatModel(
            responses=[AIMessage(content="Hello!")],
        )
        # No foundry tools
        foundry_tools: List[Any] = []

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        config: RunnableConfig = {"configurable": {}}
        input_messages = [HumanMessage(content="Hello")]
        result = model.invoke(input_messages, config=config)

        # Should work since no foundry tools need resolution
        assert result.content == "Hello!"

    def test_invoke_without_context_raises_error_when_foundry_tools_present(self):
        """Test that invoking without context raises error when foundry tools are set."""
        delegate = FakeChatModel(
            responses=[AIMessage(content="Hello!")],
        )
        foundry_tools = [{"type": "code_interpreter"}]

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        config: RunnableConfig = {"configurable": {}}
        input_messages = [HumanMessage(content="Hello")]

        with pytest.raises(RuntimeError, match="Unable to resolve foundry tools from context"):
            model.invoke(input_messages, config=config)

    def test_stream_with_context(
        self,
        mock_langgraph_run_context: LanggraphRunContext,
    ):
        """Test streaming model with context attached."""
        delegate = FakeChatModel(
            responses=[AIMessage(content="Streamed response!")],
        )
        foundry_tools = [{"type": "code_interpreter"}]

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        # Attach context to config
        config: RunnableConfig = {"configurable": {}}
        mock_langgraph_run_context.attach_to_config(config)

        input_messages = [HumanMessage(content="Hello")]
        results = list(model.stream(input_messages, config=config))

        assert len(results) == 1
        assert results[0].content == "Streamed response!"

    @pytest.mark.asyncio
    async def test_astream_with_context(
        self,
        mock_langgraph_run_context: LanggraphRunContext,
    ):
        """Test async streaming model with context attached."""
        delegate = FakeChatModel(
            responses=[AIMessage(content="Async streamed response!")],
        )
        foundry_tools = [{"type": "code_interpreter"}]

        model = FoundryToolLateBindingChatModel(
            delegate=delegate,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        # Attach context to config
        config: RunnableConfig = {"configurable": {}}
        mock_langgraph_run_context.attach_to_config(config)

        input_messages = [HumanMessage(content="Hello")]
        results = []
        async for chunk in model.astream(input_messages, config=config):
            results.append(chunk)

        assert len(results) == 1
        assert results[0].content == "Async streamed response!"

