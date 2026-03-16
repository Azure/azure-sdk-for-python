# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for _name_resolver.py - testing public methods of ToolNameResolver."""
from azure.ai.agentserver.core.tools.utils import ToolNameResolver
from azure.ai.agentserver.core.tools.client._models import (
    FoundryConnectedTool,
    FoundryHostedMcpTool,
    FoundryToolDetails,
    ResolvedFoundryTool,
)

from .conftest import create_resolved_tool_with_name


class TestToolNameResolverResolve:
    """Tests for ToolNameResolver.resolve method."""

    def test_resolve_returns_tool_name_for_first_occurrence(
        self,
        sample_resolved_mcp_tool
    ):
        """Test resolve returns the original tool name for first occurrence."""
        resolver = ToolNameResolver()

        result = resolver.resolve(sample_resolved_mcp_tool)

        assert result == sample_resolved_mcp_tool.details.name

    def test_resolve_returns_same_name_for_same_tool(
        self,
        sample_resolved_mcp_tool
    ):
        """Test resolve returns the same name when called multiple times for same tool."""
        resolver = ToolNameResolver()

        result1 = resolver.resolve(sample_resolved_mcp_tool)
        result2 = resolver.resolve(sample_resolved_mcp_tool)
        result3 = resolver.resolve(sample_resolved_mcp_tool)

        assert result1 == result2 == result3
        assert result1 == sample_resolved_mcp_tool.details.name

    def test_resolve_appends_count_for_duplicate_names(self):
        """Test resolve appends count for tools with duplicate names."""
        resolver = ToolNameResolver()

        tool1 = create_resolved_tool_with_name("my_tool", connection_id="conn-1")
        tool2 = create_resolved_tool_with_name("my_tool", connection_id="conn-2")
        tool3 = create_resolved_tool_with_name("my_tool", connection_id="conn-3")

        result1 = resolver.resolve(tool1)
        result2 = resolver.resolve(tool2)
        result3 = resolver.resolve(tool3)

        assert result1 == "my_tool"
        assert result2 == "my_tool_1"
        assert result3 == "my_tool_2"

    def test_resolve_handles_multiple_unique_names(self):
        """Test resolve handles multiple tools with unique names."""
        resolver = ToolNameResolver()

        tool1 = create_resolved_tool_with_name("tool_alpha")
        tool2 = create_resolved_tool_with_name("tool_beta")
        tool3 = create_resolved_tool_with_name("tool_gamma")

        result1 = resolver.resolve(tool1)
        result2 = resolver.resolve(tool2)
        result3 = resolver.resolve(tool3)

        assert result1 == "tool_alpha"
        assert result2 == "tool_beta"
        assert result3 == "tool_gamma"

    def test_resolve_mixed_unique_and_duplicate_names(self):
        """Test resolve handles a mix of unique and duplicate names."""
        resolver = ToolNameResolver()

        tool1 = create_resolved_tool_with_name("shared_name", connection_id="conn-1")
        tool2 = create_resolved_tool_with_name("unique_name")
        tool3 = create_resolved_tool_with_name("shared_name", connection_id="conn-2")
        tool4 = create_resolved_tool_with_name("another_unique")
        tool5 = create_resolved_tool_with_name("shared_name", connection_id="conn-3")

        assert resolver.resolve(tool1) == "shared_name"
        assert resolver.resolve(tool2) == "unique_name"
        assert resolver.resolve(tool3) == "shared_name_1"
        assert resolver.resolve(tool4) == "another_unique"
        assert resolver.resolve(tool5) == "shared_name_2"

    def test_resolve_returns_cached_name_after_duplicate_added(self):
        """Test that resolving a tool again returns cached name even after duplicates are added."""
        resolver = ToolNameResolver()

        tool1 = create_resolved_tool_with_name("my_tool", connection_id="conn-1")
        tool2 = create_resolved_tool_with_name("my_tool", connection_id="conn-2")

        # First resolution
        first_result = resolver.resolve(tool1)
        assert first_result == "my_tool"

        # Add duplicate
        dup_result = resolver.resolve(tool2)
        assert dup_result == "my_tool_1"

        # Resolve original again - should return cached value
        second_result = resolver.resolve(tool1)
        assert second_result == "my_tool"

    def test_resolve_with_connected_tool(
        self,
        sample_resolved_connected_tool
    ):
        """Test resolve works with connected tools."""
        resolver = ToolNameResolver()

        result = resolver.resolve(sample_resolved_connected_tool)

        assert result == sample_resolved_connected_tool.details.name

    def test_resolve_different_tools_same_details_name(self, sample_schema_definition):
        """Test resolve handles different tool definitions with same details name."""
        resolver = ToolNameResolver()

        details = FoundryToolDetails(
            name="shared_function",
            description="A shared function",
            input_schema=sample_schema_definition
        )

        mcp_def = FoundryHostedMcpTool(name="mcp_server", configuration={})
        connected_def = FoundryConnectedTool(protocol="mcp", project_connection_id="my-conn")

        tool1 = ResolvedFoundryTool(definition=mcp_def, details=details)
        tool2 = ResolvedFoundryTool(definition=connected_def, details=details)

        result1 = resolver.resolve(tool1)
        result2 = resolver.resolve(tool2)

        assert result1 == "shared_function"
        assert result2 == "shared_function_1"

    def test_resolve_empty_name(self):
        """Test resolve handles tools with empty name."""
        resolver = ToolNameResolver()

        tool = create_resolved_tool_with_name("")

        result = resolver.resolve(tool)

        assert result == ""

    def test_resolve_special_characters_in_name(self):
        """Test resolve handles tools with special characters in name."""
        resolver = ToolNameResolver()

        tool1 = create_resolved_tool_with_name("my-tool_v1.0", connection_id="conn-1")
        tool2 = create_resolved_tool_with_name("my-tool_v1.0", connection_id="conn-2")

        result1 = resolver.resolve(tool1)
        result2 = resolver.resolve(tool2)

        assert result1 == "my-tool_v1.0"
        assert result2 == "my-tool_v1.0_1"

    def test_independent_resolver_instances(self):
        """Test that different resolver instances maintain independent state."""
        resolver1 = ToolNameResolver()
        resolver2 = ToolNameResolver()

        tool1 = create_resolved_tool_with_name("tool_name", connection_id="conn-1")
        tool2 = create_resolved_tool_with_name("tool_name", connection_id="conn-2")

        # Both resolvers resolve tool1 first
        assert resolver1.resolve(tool1) == "tool_name"
        assert resolver2.resolve(tool1) == "tool_name"

        # resolver1 resolves tool2 as duplicate
        assert resolver1.resolve(tool2) == "tool_name_1"

        # resolver2 has not seen tool2 yet in its context
        # but tool2 has same name, so it should be duplicate
        assert resolver2.resolve(tool2) == "tool_name_1"

    def test_resolve_many_duplicates(self):
        """Test resolve handles many tools with the same name."""
        resolver = ToolNameResolver()

        tools = [
            create_resolved_tool_with_name("common_name", connection_id=f"conn-{i}")
            for i in range(10)
        ]

        results = [resolver.resolve(tool) for tool in tools]

        expected = ["common_name"] + [f"common_name_{i}" for i in range(1, 10)]
        assert results == expected

    def test_resolve_uses_tool_id_for_caching(self, sample_schema_definition):
        """Test that resolve uses tool.id for caching, not just name."""
        resolver = ToolNameResolver()

        # Create two tools with same definition but different details names
        definition = FoundryHostedMcpTool(name="same_definition", configuration={})

        details1 = FoundryToolDetails(
            name="function_a",
            description="Function A",
            input_schema=sample_schema_definition
        )
        details2 = FoundryToolDetails(
            name="function_b",
            description="Function B",
            input_schema=sample_schema_definition
        )

        tool1 = ResolvedFoundryTool(definition=definition, details=details1)
        tool2 = ResolvedFoundryTool(definition=definition, details=details2)

        result1 = resolver.resolve(tool1)
        result2 = resolver.resolve(tool2)

        # Both should get their respective names since they have different tool.id
        assert result1 == "function_a"
        assert result2 == "function_b"

    def test_resolve_idempotent_for_same_tool_id(self, sample_schema_definition):
        """Test that resolve is idempotent for the same tool id."""
        resolver = ToolNameResolver()

        definition = FoundryHostedMcpTool(name="my_mcp", configuration={})
        details = FoundryToolDetails(
            name="my_function",
            description="My function",
            input_schema=sample_schema_definition
        )
        tool = ResolvedFoundryTool(definition=definition, details=details)

        # Call resolve many times
        results = [resolver.resolve(tool) for _ in range(5)]

        # All should return the same name
        assert all(r == "my_function" for r in results)

    def test_resolve_interleaved_tool_resolutions(self):
        """Test resolve with interleaved resolutions of different tools."""
        resolver = ToolNameResolver()

        toolA_1 = create_resolved_tool_with_name("A", connection_id="A-1")
        toolA_2 = create_resolved_tool_with_name("A", connection_id="A-2")
        toolB_1 = create_resolved_tool_with_name("B", connection_id="B-1")
        toolA_3 = create_resolved_tool_with_name("A", connection_id="A-3")
        toolB_2 = create_resolved_tool_with_name("B", connection_id="B-2")

        assert resolver.resolve(toolA_1) == "A"
        assert resolver.resolve(toolB_1) == "B"
        assert resolver.resolve(toolA_2) == "A_1"
        assert resolver.resolve(toolA_3) == "A_2"
        assert resolver.resolve(toolB_2) == "B_1"
