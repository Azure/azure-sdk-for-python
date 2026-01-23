# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for ResolvedTools and FoundryLangChainToolResolver."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.tools import BaseTool, StructuredTool, tool
from pydantic import BaseModel

from azure.ai.agentserver.core.tools import (FoundryConnectedTool, FoundryHostedMcpTool, FoundryToolDetails,
                                             ResolvedFoundryTool, SchemaDefinition, SchemaProperty, SchemaType)
from azure.ai.agentserver.langgraph.tools._resolver import (
    ResolvedTools,
    FoundryLangChainToolResolver,
    get_registry,
)


@pytest.mark.unit
class TestResolvedTools:
    """Tests for ResolvedTools class."""

    def test_create_empty_resolved_tools(self):
        """Test creating an empty ResolvedTools."""
        resolved = ResolvedTools(tools=[])

        tools_list = list(resolved)
        assert len(tools_list) == 0

    def test_create_with_single_tool(
        self,
        sample_code_interpreter_tool: FoundryHostedMcpTool,
        mock_langchain_tool: BaseTool,
    ):
        """Test creating ResolvedTools with a single tool."""
        resolved_foundry_tool = ResolvedFoundryTool(
            definition=sample_code_interpreter_tool,
            details=FoundryToolDetails(
                name="test_tool",
                description="A test tool",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={
                        "input": SchemaProperty(type=SchemaType.STRING, description="Input"),
                    },
                    required={"input"},
                ),
            ),
        )
        resolved = ResolvedTools(tools=[(resolved_foundry_tool, mock_langchain_tool)])

        tools_list = list(resolved)
        assert len(tools_list) == 1
        assert tools_list[0] is mock_langchain_tool

    def test_create_with_multiple_tools(
        self,
        sample_code_interpreter_tool: FoundryHostedMcpTool,
        sample_mcp_connected_tool: FoundryConnectedTool,
    ):
        """Test creating ResolvedTools with multiple tools."""
        @tool
        def tool1(query: str) -> str:
            """Tool 1."""
            return "result1"

        @tool
        def tool2(query: str) -> str:
            """Tool 2."""
            return "result2"

        resolved_tool1 = ResolvedFoundryTool(
            definition=sample_code_interpreter_tool,
            details=FoundryToolDetails(
                name="tool1",
                description="Tool 1",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={"query": SchemaProperty(type=SchemaType.STRING, description="Query")},
                    required={"query"},
                ),
            ),
        )
        resolved_tool2 = ResolvedFoundryTool(
            definition=sample_mcp_connected_tool,
            details=FoundryToolDetails(
                name="tool2",
                description="Tool 2",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={"query": SchemaProperty(type=SchemaType.STRING, description="Query")},
                    required={"query"},
                ),
            ),
        )

        resolved = ResolvedTools(tools=[
            (resolved_tool1, tool1),
            (resolved_tool2, tool2),
        ])

        tools_list = list(resolved)
        assert len(tools_list) == 2

    def test_get_tool_by_foundry_tool_like(
        self,
        sample_code_interpreter_tool: FoundryHostedMcpTool,
        mock_langchain_tool: BaseTool,
    ):
        """Test getting tools by FoundryToolLike."""
        resolved_foundry_tool = ResolvedFoundryTool(
            definition=sample_code_interpreter_tool,
            details=FoundryToolDetails(
                name="test_tool",
                description="A test tool",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={
                        "input": SchemaProperty(type=SchemaType.STRING, description="Input"),
                    },
                    required={"input"},
                ),
            ),
        )
        resolved = ResolvedTools(tools=[(resolved_foundry_tool, mock_langchain_tool)])

        # Get by the original foundry tool definition
        tools = list(resolved.get(sample_code_interpreter_tool))
        assert len(tools) == 1
        assert tools[0] is mock_langchain_tool

    def test_get_tools_by_list_of_foundry_tools(
        self,
        sample_code_interpreter_tool: FoundryHostedMcpTool,
        sample_mcp_connected_tool: FoundryConnectedTool,
    ):
        """Test getting tools by a list of FoundryToolLike."""
        @tool
        def tool1(query: str) -> str:
            """Tool 1."""
            return "result1"

        @tool
        def tool2(query: str) -> str:
            """Tool 2."""
            return "result2"

        resolved_tool1 = ResolvedFoundryTool(
            definition=sample_code_interpreter_tool,
            details=FoundryToolDetails(
                name="tool1",
                description="Tool 1",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={"query": SchemaProperty(type=SchemaType.STRING, description="Query")},
                    required={"query"},
                ),
            ),
        )
        resolved_tool2 = ResolvedFoundryTool(
            definition=sample_mcp_connected_tool,
            details=FoundryToolDetails(
                name="tool2",
                description="Tool 2",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={"query": SchemaProperty(type=SchemaType.STRING, description="Query")},
                    required={"query"},
                ),
            ),
        )

        resolved = ResolvedTools(tools=[
            (resolved_tool1, tool1),
            (resolved_tool2, tool2),
        ])

        # Get by list of foundry tools
        tools = list(resolved.get([sample_code_interpreter_tool, sample_mcp_connected_tool]))
        assert len(tools) == 2

    def test_get_all_tools_when_no_filter(
        self,
        sample_code_interpreter_tool: FoundryHostedMcpTool,
        mock_langchain_tool: BaseTool,
    ):
        """Test getting all tools when no filter is provided."""
        resolved_foundry_tool = ResolvedFoundryTool(
            definition=sample_code_interpreter_tool,
            details=FoundryToolDetails(
                name="test_tool",
                description="A test tool",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={
                        "input": SchemaProperty(type=SchemaType.STRING, description="Input"),
                    },
                    required={"input"},
                ),
            ),
        )
        resolved = ResolvedTools(tools=[(resolved_foundry_tool, mock_langchain_tool)])

        # Get all tools (no filter)
        tools = list(resolved.get())
        assert len(tools) == 1

    def test_get_returns_empty_for_unknown_tool(
        self,
        sample_code_interpreter_tool: FoundryHostedMcpTool,
        sample_mcp_connected_tool: FoundryConnectedTool,
        mock_langchain_tool: BaseTool,
    ):
        """Test that get returns empty when requesting unknown tool."""
        resolved_foundry_tool = ResolvedFoundryTool(
            definition=sample_code_interpreter_tool,
            details=FoundryToolDetails(
                name="test_tool",
                description="A test tool",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={
                        "input": SchemaProperty(type=SchemaType.STRING, description="Input"),
                    },
                    required={"input"},
                ),
            ),
        )
        resolved = ResolvedTools(tools=[(resolved_foundry_tool, mock_langchain_tool)])

        # Get by a different foundry tool (not in resolved)
        tools = list(resolved.get(sample_mcp_connected_tool))
        assert len(tools) == 0

    def test_iteration_over_resolved_tools(
        self,
        sample_code_interpreter_tool: FoundryHostedMcpTool,
        mock_langchain_tool: BaseTool,
    ):
        """Test iterating over ResolvedTools."""
        resolved_foundry_tool = ResolvedFoundryTool(
            definition=sample_code_interpreter_tool,
            details=FoundryToolDetails(
                name="test_tool",
                description="A test tool",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={
                        "input": SchemaProperty(type=SchemaType.STRING, description="Input"),
                    },
                    required={"input"},
                ),
            ),
        )
        resolved = ResolvedTools(tools=[(resolved_foundry_tool, mock_langchain_tool)])

        # Iterate using for loop
        count = 0
        for t in resolved:
            assert t is mock_langchain_tool
            count += 1
        assert count == 1


@pytest.mark.unit
class TestFoundryLangChainToolResolver:
    """Tests for FoundryLangChainToolResolver class."""

    def test_init_with_default_name_resolver(self):
        """Test initialization with default name resolver."""
        resolver = FoundryLangChainToolResolver()

        assert resolver._name_resolver is not None

    def test_init_with_custom_name_resolver(self):
        """Test initialization with custom name resolver."""
        from azure.ai.agentserver.core.tools.utils import ToolNameResolver

        custom_resolver = ToolNameResolver()
        resolver = FoundryLangChainToolResolver(name_resolver=custom_resolver)

        assert resolver._name_resolver is custom_resolver

    def test_create_pydantic_model_with_required_fields(self):
        """Test creating a Pydantic model with required fields."""
        input_schema = SchemaDefinition(
            type=SchemaType.OBJECT,
            properties={
                "query": SchemaProperty(type=SchemaType.STRING, description="Search query"),
                "limit": SchemaProperty(type=SchemaType.INTEGER, description="Max results"),
            },
            required={"query"},
        )

        model = FoundryLangChainToolResolver._create_pydantic_model("test_tool", input_schema)

        assert issubclass(model, BaseModel)
        # Check that the model has the expected fields
        assert "query" in model.model_fields
        assert "limit" in model.model_fields

    def test_create_pydantic_model_with_no_required_fields(self):
        """Test creating a Pydantic model with no required fields."""
        input_schema = SchemaDefinition(
            type=SchemaType.OBJECT,
            properties={
                "query": SchemaProperty(type=SchemaType.STRING, description="Search query"),
            },
            required=set(),
        )

        model = FoundryLangChainToolResolver._create_pydantic_model("optional_tool", input_schema)

        assert issubclass(model, BaseModel)
        assert "query" in model.model_fields
        # Optional field should have None as default
        assert model.model_fields["query"].default is None

    def test_create_pydantic_model_with_special_characters_in_name(self):
        """Test creating a Pydantic model with special characters in tool name."""
        input_schema = SchemaDefinition(
            type=SchemaType.OBJECT,
            properties={
                "input": SchemaProperty(type=SchemaType.STRING, description="Input"),
            },
            required={"input"},
        )

        model = FoundryLangChainToolResolver._create_pydantic_model("my-tool name", input_schema)

        assert issubclass(model, BaseModel)
        # Name should be sanitized
        assert "-Input" in model.__name__ or "Input" in model.__name__

    def test_create_structured_tool(self):
        """Test creating a StructuredTool from a resolved foundry tool."""
        resolver = FoundryLangChainToolResolver()

        foundry_tool = FoundryHostedMcpTool(name="test_tool", configuration={})
        resolved_tool = ResolvedFoundryTool(
            definition=foundry_tool,
            details=FoundryToolDetails(
                name="search",
                description="Search for documents",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={
                        "query": SchemaProperty(type=SchemaType.STRING, description="Search query"),
                    },
                    required={"query"},
                ),
            ),
        )

        structured_tool = resolver._create_structured_tool(resolved_tool)

        assert isinstance(structured_tool, StructuredTool)
        assert structured_tool.description == "Search for documents"
        assert structured_tool.coroutine is not None  # Should have async function

    @pytest.mark.asyncio
    async def test_resolve_from_registry(self):
        """Test resolving tools from the global registry."""
        resolver = FoundryLangChainToolResolver()

        # Mock the AgentServerContext
        mock_context = MagicMock()
        mock_catalog = AsyncMock()
        mock_context.tools.catalog.list = mock_catalog

        foundry_tool = FoundryHostedMcpTool(name="test_tool", configuration={})
        resolved_foundry_tool = ResolvedFoundryTool(
            definition=foundry_tool,
            details=FoundryToolDetails(
                name="search",
                description="Search tool",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={
                        "query": SchemaProperty(type=SchemaType.STRING, description="Query"),
                    },
                    required={"query"},
                ),
            ),
        )
        mock_catalog.return_value = [resolved_foundry_tool]

        # Add tool to registry
        registry = get_registry()
        registry.clear()
        registry.append({"type": "code_interpreter"})

        with patch("azure.ai.agentserver.langgraph.tools._resolver.AgentServerContext.get", return_value=mock_context):
            result = await resolver.resolve_from_registry()

        assert isinstance(result, ResolvedTools)
        mock_catalog.assert_called_once()

        # Clean up registry
        registry.clear()

    @pytest.mark.asyncio
    async def test_resolve_with_foundry_tools_list(self):
        """Test resolving a list of foundry tools."""
        resolver = FoundryLangChainToolResolver()

        # Mock the AgentServerContext
        mock_context = MagicMock()
        mock_catalog = AsyncMock()
        mock_context.tools.catalog.list = mock_catalog

        foundry_tool = FoundryHostedMcpTool(name="code_interpreter", configuration={})
        resolved_foundry_tool = ResolvedFoundryTool(
            definition=foundry_tool,
            details=FoundryToolDetails(
                name="execute_code",
                description="Execute code",
                input_schema=SchemaDefinition(
                    type=SchemaType.OBJECT,
                    properties={
                        "code": SchemaProperty(type=SchemaType.STRING, description="Code to execute"),
                    },
                    required={"code"},
                ),
            ),
        )
        mock_catalog.return_value = [resolved_foundry_tool]

        foundry_tools = [{"type": "code_interpreter"}]

        with patch("azure.ai.agentserver.langgraph.tools._resolver.AgentServerContext.get", return_value=mock_context):
            result = await resolver.resolve(foundry_tools)

        assert isinstance(result, ResolvedTools)
        tools_list = list(result)
        assert len(tools_list) == 1
        assert isinstance(tools_list[0], StructuredTool)

    @pytest.mark.asyncio
    async def test_resolve_empty_list(self):
        """Test resolving an empty list of foundry tools."""
        resolver = FoundryLangChainToolResolver()

        # Mock the AgentServerContext
        mock_context = MagicMock()
        mock_catalog = AsyncMock()
        mock_context.tools.catalog.list = mock_catalog
        mock_catalog.return_value = []

        with patch("azure.ai.agentserver.langgraph.tools._resolver.AgentServerContext.get", return_value=mock_context):
            result = await resolver.resolve([])

        assert isinstance(result, ResolvedTools)
        tools_list = list(result)
        assert len(tools_list) == 0


@pytest.mark.unit
class TestGetRegistry:
    """Tests for the get_registry function."""

    def test_get_registry_returns_list(self):
        """Test that get_registry returns a list."""
        registry = get_registry()

        assert isinstance(registry, list)

    def test_registry_is_singleton(self):
        """Test that get_registry returns the same list instance."""
        registry1 = get_registry()
        registry2 = get_registry()

        assert registry1 is registry2

    def test_registry_can_be_modified(self):
        """Test that the registry can be modified."""
        registry = get_registry()
        original_length = len(registry)

        registry.append({"type": "test_tool"})

        assert len(registry) == original_length + 1

        # Clean up
        registry.pop()

    def test_registry_extend(self):
        """Test extending the registry with multiple tools."""
        registry = get_registry()
        registry.clear()

        tools = [
            {"type": "code_interpreter"},
            {"type": "mcp", "project_connection_id": "test"},
        ]
        registry.extend(tools)

        assert len(registry) == 2

        # Clean up
        registry.clear()
