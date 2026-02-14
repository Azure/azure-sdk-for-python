# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures for langgraph tools unit tests."""
from typing import Any, Dict, List, Optional

import pytest
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool

from azure.ai.agentserver.core.tools import (
    FoundryHostedMcpTool,
    FoundryConnectedTool,
    FoundryToolDetails,
    ResolvedFoundryTool,
    SchemaDefinition,
    SchemaProperty,
    SchemaType,
)
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext
from azure.ai.agentserver.langgraph._context import LanggraphRunContext
from azure.ai.agentserver.langgraph.tools._context import FoundryToolContext
from azure.ai.agentserver.langgraph.tools._resolver import ResolvedTools


class FakeChatModel(BaseChatModel):
    """A fake chat model for testing purposes that returns pre-configured responses."""

    responses: List[AIMessage] = []
    tool_calls_list: List[List[Dict[str, Any]]] = []
    _call_count: int = 0
    _bound_tools: List[Any] = []
    _bound_kwargs: Dict[str, Any] = {}

    def __init__(
        self,
        responses: Optional[List[AIMessage]] = None,
        tool_calls: Optional[List[List[Dict[str, Any]]]] = None,
        **kwargs: Any,
    ):
        """Initialize the fake chat model.

        :param responses: List of AIMessage responses to return in sequence.
        :param tool_calls: List of tool_calls lists corresponding to each response.
        """
        super().__init__(**kwargs)
        self.responses = responses or []
        self.tool_calls_list = tool_calls or []
        self._call_count = 0
        self._bound_tools = []
        self._bound_kwargs = {}

    @property
    def _llm_type(self) -> str:
        return "fake_chat_model"

    def _generate(
        self,
        messages: List[Any],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response."""
        response = self._get_next_response()
        return ChatResult(generations=[ChatGeneration(message=response)])

    def bind_tools(
        self,
        tools: List[Any],
        **kwargs: Any,
    ) -> "FakeChatModel":
        """Bind tools to this model."""
        self._bound_tools = list(tools)
        self._bound_kwargs.update(kwargs)
        return self

    def invoke(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any) -> AIMessage:
        """Synchronously invoke the model."""
        return self._get_next_response()

    async def ainvoke(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any) -> AIMessage:
        """Asynchronously invoke the model."""
        return self._get_next_response()

    def stream(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any):
        """Stream the response."""
        yield self._get_next_response()

    async def astream(self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any):
        """Async stream the response."""
        yield self._get_next_response()

    def _get_next_response(self) -> AIMessage:
        """Get the next response in sequence."""
        if self._call_count < len(self.responses):
            response = self.responses[self._call_count]
        else:
            # Default response if no more configured
            response = AIMessage(content="Default response")

        # Apply tool calls if configured
        if self._call_count < len(self.tool_calls_list):
            response = AIMessage(
                content=response.content,
                tool_calls=self.tool_calls_list[self._call_count],
            )

        self._call_count += 1
        return response


@pytest.fixture
def sample_schema_definition() -> SchemaDefinition:
    """Create a sample SchemaDefinition."""
    return SchemaDefinition(
        type=SchemaType.OBJECT,
        properties={
            "query": SchemaProperty(type=SchemaType.STRING, description="Search query"),
        },
        required={"query"},
    )


@pytest.fixture
def sample_code_interpreter_tool() -> FoundryHostedMcpTool:
    """Create a sample code interpreter tool definition."""
    return FoundryHostedMcpTool(
        name="code_interpreter",
        configuration={},
    )


@pytest.fixture
def sample_mcp_connected_tool() -> FoundryConnectedTool:
    """Create a sample MCP connected tool definition."""
    return FoundryConnectedTool(
        protocol="mcp",
        project_connection_id="MicrosoftLearn",
    )


@pytest.fixture
def sample_tool_details(sample_schema_definition: SchemaDefinition) -> FoundryToolDetails:
    """Create a sample FoundryToolDetails."""
    return FoundryToolDetails(
        name="search",
        description="Search for documents",
        input_schema=sample_schema_definition,
    )


@pytest.fixture
def sample_resolved_tool(
    sample_code_interpreter_tool: FoundryHostedMcpTool,
    sample_tool_details: FoundryToolDetails,
) -> ResolvedFoundryTool:
    """Create a sample resolved foundry tool."""
    return ResolvedFoundryTool(
        definition=sample_code_interpreter_tool,
        details=sample_tool_details,
    )


@pytest.fixture
def mock_langchain_tool() -> BaseTool:
    """Create a mock LangChain BaseTool."""
    @tool
    def mock_tool(query: str) -> str:
        """Mock tool for testing.

        :param query: The search query.
        :return: Mock result.
        """
        return f"Mock result for: {query}"

    return mock_tool


@pytest.fixture
def mock_async_langchain_tool() -> BaseTool:
    """Create a mock async LangChain BaseTool."""
    @tool
    async def mock_async_tool(query: str) -> str:
        """Mock async tool for testing.

        :param query: The search query.
        :return: Mock result.
        """
        return f"Async mock result for: {query}"

    return mock_async_tool


@pytest.fixture
def sample_resolved_tools(
    sample_code_interpreter_tool: FoundryHostedMcpTool,
    mock_langchain_tool: BaseTool,
) -> ResolvedTools:
    """Create a sample ResolvedTools instance."""
    resolved_foundry_tool = ResolvedFoundryTool(
        definition=sample_code_interpreter_tool,
        details=FoundryToolDetails(
            name="mock_tool",
            description="Mock tool for testing",
            input_schema=SchemaDefinition(
                type=SchemaType.OBJECT,
                properties={
                    "query": SchemaProperty(type=SchemaType.STRING, description="Query"),
                },
                required={"query"},
            ),
        ),
    )
    return ResolvedTools(tools=[(resolved_foundry_tool, mock_langchain_tool)])


@pytest.fixture
def mock_agent_run_context() -> AgentRunContext:
    """Create a mock AgentRunContext."""
    payload = {
        "input": [{"role": "user", "content": "Hello"}],
        "stream": False,
    }
    return AgentRunContext(payload=payload)


@pytest.fixture
def mock_foundry_tool_context(sample_resolved_tools: ResolvedTools) -> FoundryToolContext:
    """Create a mock FoundryToolContext."""
    return FoundryToolContext(resolved_tools=sample_resolved_tools)


@pytest.fixture
def mock_langgraph_run_context(
    mock_agent_run_context: AgentRunContext,
    mock_foundry_tool_context: FoundryToolContext,
) -> LanggraphRunContext:
    """Create a mock LanggraphRunContext."""
    return LanggraphRunContext(
        agent_run=mock_agent_run_context,
        tools=mock_foundry_tool_context,
    )


@pytest.fixture
def fake_chat_model_simple() -> FakeChatModel:
    """Create a simple fake chat model."""
    return FakeChatModel(
        responses=[AIMessage(content="Hello! How can I help you?")],
    )


@pytest.fixture
def fake_chat_model_with_tool_call() -> FakeChatModel:
    """Create a fake chat model that makes a tool call."""
    return FakeChatModel(
        responses=[
            AIMessage(content=""),  # First response: tool call
            AIMessage(content="The answer is 42."),  # Second response: final answer
        ],
        tool_calls=[
            [{"id": "call_1", "name": "mock_tool", "args": {"query": "test query"}}],
            [],  # No tool calls in final response
        ],
    )

