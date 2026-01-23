# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Integration-style unit tests for langgraph agents with foundry tools.

These tests demonstrate the usage patterns similar to the tool_client_example samples,
but use mocked models and tools to avoid calling real services.
"""
import pytest

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from typing_extensions import Literal

from azure.ai.agentserver.core.tools import (
    FoundryHostedMcpTool,
    FoundryToolDetails,
    ResolvedFoundryTool,
    SchemaDefinition,
    SchemaProperty,
    SchemaType,
)
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext
from azure.ai.agentserver.langgraph._context import LanggraphRunContext
from azure.ai.agentserver.langgraph.tools import use_foundry_tools
from azure.ai.agentserver.langgraph.tools._context import FoundryToolContext
from azure.ai.agentserver.langgraph.tools._chat_model import FoundryToolLateBindingChatModel
from azure.ai.agentserver.langgraph.tools._middleware import FoundryToolBindingMiddleware
from azure.ai.agentserver.langgraph.tools._resolver import ResolvedTools, get_registry

from .conftest import FakeChatModel


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the global registry before and after each test."""
    registry = get_registry()
    registry.clear()
    yield
    registry.clear()


@pytest.mark.unit
class TestGraphAgentWithFoundryTools:
    """Tests demonstrating graph agent usage patterns similar to graph_agent_tool.py sample."""

    def _create_mock_langgraph_context(
        self,
        foundry_tool: FoundryHostedMcpTool,
        langchain_tool: BaseTool,
    ) -> LanggraphRunContext:
        """Create a mock LanggraphRunContext with resolved tools."""
        # Create resolved foundry tool
        resolved_foundry_tool = ResolvedFoundryTool(
            definition=foundry_tool,
            details=FoundryToolDetails(
                name=langchain_tool.name,
                description=langchain_tool.description or "Mock tool",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={
                        "query": SchemaProperty(type=SchemaType.STRING, description="Query"),
                    },
                    required={"query"},
                ),
            ),
        )

        # Create resolved tools
        resolved_tools = ResolvedTools(tools=[(resolved_foundry_tool, langchain_tool)])

        # Create context
        payload = {"input": [{"role": "user", "content": "test"}], "stream": False}
        agent_run_context = AgentRunContext(payload=payload)
        tool_context = FoundryToolContext(resolved_tools=resolved_tools)

        return LanggraphRunContext(agent_run=agent_run_context, tools=tool_context)

    @pytest.mark.asyncio
    async def test_graph_agent_with_foundry_tools_no_tool_call(self):
        """Test a graph agent that uses foundry tools but doesn't make a tool call."""
        # Create a mock tool
        @tool
        def calculate(expression: str) -> str:
            """Calculate a mathematical expression.

            :param expression: The expression to calculate.
            :return: The result.
            """
            return "42"

        # Create foundry tool definition
        foundry_tool = FoundryHostedMcpTool(name="code_interpreter", configuration={})
        foundry_tools = [{"type": "code_interpreter"}]

        # Create mock model that returns simple response (no tool call)
        mock_model = FakeChatModel(
            responses=[AIMessage(content="The answer is 42.")],
        )

        # Create the foundry tool binding chat model
        llm_with_foundry_tools = FoundryToolLateBindingChatModel(
            delegate=mock_model,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        # Create context and attach
        context = self._create_mock_langgraph_context(foundry_tool, calculate)
        config: RunnableConfig = {"configurable": {}}
        context.attach_to_config(config)

        # Define the LLM call node
        async def llm_call(state: MessagesState, config: RunnableConfig):
            return {
                "messages": [
                    await llm_with_foundry_tools.ainvoke(
                        [SystemMessage(content="You are a helpful assistant.")]
                        + state["messages"],
                        config=config,
                    )
                ]
            }

        # Define routing function
        def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            return END

        # Build the graph
        builder = StateGraph(MessagesState)
        builder.add_node("llm_call", llm_call)
        builder.add_node("tools", llm_with_foundry_tools.tool_node)
        builder.add_edge(START, "llm_call")
        builder.add_conditional_edges("llm_call", should_continue, {"tools": "tools", END: END})
        builder.add_edge("tools", "llm_call")

        graph = builder.compile()

        # Run the graph
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content="What is 6 * 7?")]},
            config=config,
        )

        # Verify result
        assert len(result["messages"]) == 2  # HumanMessage + AIMessage
        assert result["messages"][-1].content == "The answer is 42."

    @pytest.mark.asyncio
    async def test_graph_agent_with_tool_call(self):
        """Test a graph agent that makes a tool call."""
        # Create a mock tool
        @tool
        def calculate(expression: str) -> str:
            """Calculate a mathematical expression.

            :param expression: The expression to calculate.
            :return: The result.
            """
            return "42"

        # Create foundry tool definition
        foundry_tool = FoundryHostedMcpTool(name="code_interpreter", configuration={})
        foundry_tools = [{"type": "code_interpreter"}]

        # Create mock model that makes a tool call, then returns final answer
        mock_model = FakeChatModel(
            responses=[
                AIMessage(
                    content="",
                    tool_calls=[{"id": "call_1", "name": "calculate", "args": {"expression": "6 * 7"}}],
                ),
                AIMessage(content="The answer is 42."),
            ],
        )

        # Create the foundry tool binding chat model
        llm_with_foundry_tools = FoundryToolLateBindingChatModel(
            delegate=mock_model,  # type: ignore
            runtime=None,
            foundry_tools=foundry_tools,
        )

        # Create context with the calculate tool
        context = self._create_mock_langgraph_context(foundry_tool, calculate)
        config: RunnableConfig = {"configurable": {}}
        context.attach_to_config(config)

        # Define the LLM call node
        async def llm_call(state: MessagesState, config: RunnableConfig):
            return {
                "messages": [
                    await llm_with_foundry_tools.ainvoke(
                        [SystemMessage(content="You are a helpful assistant.")]
                        + state["messages"],
                        config=config,
                    )
                ]
            }

        # Define routing function
        def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            return END

        # Build the graph with a regular ToolNode (using the local tool directly for testing)
        builder = StateGraph(MessagesState)
        builder.add_node("llm_call", llm_call)
        builder.add_node("tools", ToolNode([calculate]))
        builder.add_edge(START, "llm_call")
        builder.add_conditional_edges("llm_call", should_continue, {"tools": "tools", END: END})
        builder.add_edge("tools", "llm_call")

        graph = builder.compile()

        # Run the graph
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content="What is 6 * 7?")]},
            config=config,
        )

        # Verify result - should have: HumanMessage, AIMessage (with tool call), ToolMessage, AIMessage (final)
        assert len(result["messages"]) == 4
        assert result["messages"][-1].content == "The answer is 42."

        # Verify tool was called
        tool_message = result["messages"][2]
        assert isinstance(tool_message, ToolMessage)
        assert tool_message.content == "42"


@pytest.mark.unit
class TestReactAgentWithFoundryTools:
    """Tests demonstrating react agent usage patterns similar to react_agent_tool.py sample."""

    @pytest.mark.asyncio
    async def test_middleware_integration_with_foundry_tools(self):
        """Test that FoundryToolBindingMiddleware correctly integrates with agents."""
        # Define foundry tools configuration
        foundry_tools_config = [
            {"type": "code_interpreter"},
            {"type": "mcp", "project_connection_id": "MicrosoftLearn"},
        ]

        # Create middleware using use_foundry_tools
        middleware = use_foundry_tools(foundry_tools_config)

        # Verify middleware is created correctly
        assert isinstance(middleware, FoundryToolBindingMiddleware)

        # Verify dummy tool is created for the agent
        assert len(middleware.tools) == 1
        assert middleware.tools[0].name == "__dummy_tool_by_foundry_middleware__"

        # Verify foundry tools are recorded
        assert len(middleware._foundry_tools_to_bind) == 2

    def test_use_foundry_tools_with_model(self):
        """Test use_foundry_tools when used with a model directly."""
        foundry_tools = [{"type": "code_interpreter"}]
        mock_model = FakeChatModel()

        result = use_foundry_tools(mock_model, foundry_tools)  # type: ignore

        assert isinstance(result, FoundryToolLateBindingChatModel)
        assert len(result._foundry_tools_to_bind) == 1
        assert isinstance(result._foundry_tools_to_bind[0], FoundryHostedMcpTool)
        assert result._foundry_tools_to_bind[0].name == "code_interpreter"


@pytest.mark.unit
class TestLanggraphRunContextIntegration:
    """Tests for LanggraphRunContext integration with langgraph."""

    def test_context_attachment_to_config(self):
        """Test that context is correctly attached to RunnableConfig."""
        # Create a mock context
        payload = {"input": [{"role": "user", "content": "test"}], "stream": False}
        agent_run_context = AgentRunContext(payload=payload)
        tool_context = FoundryToolContext()

        context = LanggraphRunContext(agent_run=agent_run_context, tools=tool_context)

        # Create config and attach context
        config: RunnableConfig = {"configurable": {}}
        context.attach_to_config(config)

        # Verify context is attached
        assert "__foundry_hosted_agent_langgraph_run_context__" in config["configurable"]
        assert config["configurable"]["__foundry_hosted_agent_langgraph_run_context__"] is context

    def test_context_resolution_from_config(self):
        """Test that context can be resolved from RunnableConfig."""
        # Create and attach context
        payload = {"input": [{"role": "user", "content": "test"}], "stream": False}
        agent_run_context = AgentRunContext(payload=payload)
        tool_context = FoundryToolContext()

        context = LanggraphRunContext(agent_run=agent_run_context, tools=tool_context)

        config: RunnableConfig = {"configurable": {}}
        context.attach_to_config(config)

        # Resolve context
        resolved = LanggraphRunContext.resolve(config=config)

        assert resolved is context

    def test_context_resolution_returns_none_when_not_attached(self):
        """Test that context resolution returns None when not attached.

        For Python < 3.11, LanggraphRunContext.resolve will return None.
        For Python >= 3.11, it will try get_runtime() from langgraph which depends on
        context propagation. Since we don't run inside langgraph in unit tests,
        no one propagates the context for us, so RuntimeError is raised.
        """
        import sys
        config: RunnableConfig = {"configurable": {}}

        if sys.version_info >= (3, 11):
            with pytest.raises(RuntimeError, match="outside of a runnable context"):
                LanggraphRunContext.resolve(config=config)
        else:
            resolved = LanggraphRunContext.resolve(config=config)
            assert resolved is None

    def test_from_config_returns_context(self):
        """Test LanggraphRunContext.from_config method."""
        payload = {"input": [{"role": "user", "content": "test"}], "stream": False}
        agent_run_context = AgentRunContext(payload=payload)
        tool_context = FoundryToolContext()

        context = LanggraphRunContext(agent_run=agent_run_context, tools=tool_context)

        config: RunnableConfig = {"configurable": {}}
        context.attach_to_config(config)

        result = LanggraphRunContext.from_config(config)

        assert result is context

    def test_from_config_returns_none_for_non_context_value(self):
        """Test that from_config returns None when value is not LanggraphRunContext."""
        config: RunnableConfig = {
            "configurable": {
                "__foundry_hosted_agent_langgraph_run_context__": "not a context"
            }
        }

        result = LanggraphRunContext.from_config(config)

        assert result is None


@pytest.mark.unit
class TestToolsResolutionInGraph:
    """Tests for tool resolution within langgraph execution."""

    @pytest.mark.asyncio
    async def test_foundry_tools_resolved_from_context_in_graph_node(self):
        """Test that foundry tools are correctly resolved from context during graph execution."""
        # Create mock tool
        @tool
        def search(query: str) -> str:
            """Search for information.

            :param query: The search query.
            :return: Search results.
            """
            return f"Results for: {query}"

        # Create foundry tool and context
        foundry_tool = FoundryHostedMcpTool(name="code_interpreter", configuration={})
        resolved_foundry_tool = ResolvedFoundryTool(
            definition=foundry_tool,
            details=FoundryToolDetails(
                name="search",
                description="Search tool",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={"query": SchemaProperty(type=SchemaType.STRING, description="Query")},
                    required={"query"},
                ),
            ),
        )

        resolved_tools = ResolvedTools(tools=[(resolved_foundry_tool, search)])

        # Create context
        payload = {"input": [{"role": "user", "content": "test"}], "stream": False}
        agent_run_context = AgentRunContext(payload=payload)
        tool_context = FoundryToolContext(resolved_tools=resolved_tools)
        lg_context = LanggraphRunContext(agent_run=agent_run_context, tools=tool_context)

        # Create config and attach context
        config: RunnableConfig = {"configurable": {}}
        lg_context.attach_to_config(config)

        # Verify tools can be resolved
        resolved = LanggraphRunContext.resolve(config=config)
        assert resolved is not None

        tools = list(resolved.tools.resolved_tools.get(foundry_tool))
        assert len(tools) == 1
        assert tools[0].name == "search"

