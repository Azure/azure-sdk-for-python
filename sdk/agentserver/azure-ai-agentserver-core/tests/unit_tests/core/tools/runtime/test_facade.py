# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for _facade.py - testing public function ensure_foundry_tool."""
import pytest

from azure.ai.agentserver.core.tools.runtime._facade import ensure_foundry_tool
from azure.ai.agentserver.core.tools.client._models import (
    FoundryConnectedTool,
    FoundryHostedMcpTool,
    FoundryToolProtocol,
    FoundryToolSource,
)
from azure.ai.agentserver.core.tools._exceptions import InvalidToolFacadeError


class TestEnsureFoundryTool:
    """Tests for ensure_foundry_tool public function."""

    def test_returns_same_instance_when_given_foundry_tool(self, sample_hosted_mcp_tool):
        """Test that passing a FoundryTool returns the same instance."""
        result = ensure_foundry_tool(sample_hosted_mcp_tool)

        assert result is sample_hosted_mcp_tool

    def test_returns_same_instance_for_connected_tool(self, sample_connected_tool):
        """Test that passing a FoundryConnectedTool returns the same instance."""
        result = ensure_foundry_tool(sample_connected_tool)

        assert result is sample_connected_tool

    def test_converts_facade_with_mcp_protocol_to_connected_tool(self):
        """Test that a facade with 'mcp' protocol is converted to FoundryConnectedTool."""
        facade = {
            "type": "mcp",
            "project_connection_id": "my-connection"
        }

        result = ensure_foundry_tool(facade)

        assert isinstance(result, FoundryConnectedTool)
        assert result.protocol == FoundryToolProtocol.MCP
        assert result.project_connection_id == "my-connection"
        assert result.source == FoundryToolSource.CONNECTED

    def test_converts_facade_with_a2a_protocol_to_connected_tool(self):
        """Test that a facade with 'a2a' protocol is converted to FoundryConnectedTool."""
        facade = {
            "type": "a2a",
            "project_connection_id": "my-a2a-connection"
        }

        result = ensure_foundry_tool(facade)

        assert isinstance(result, FoundryConnectedTool)
        assert result.protocol == FoundryToolProtocol.A2A
        assert result.project_connection_id == "my-a2a-connection"

    def test_converts_facade_with_unknown_type_to_hosted_mcp_tool(self):
        """Test that a facade with unknown type is converted to FoundryHostedMcpTool."""
        facade = {
            "type": "my_custom_tool",
            "some_config": "value123",
            "another_config": True
        }

        result = ensure_foundry_tool(facade)

        assert isinstance(result, FoundryHostedMcpTool)
        assert result.name == "my_custom_tool"
        assert result.configuration == {"some_config": "value123", "another_config": True}
        assert result.source == FoundryToolSource.HOSTED_MCP

    def test_raises_error_when_type_is_missing(self):
        """Test that InvalidToolFacadeError is raised when 'type' is missing."""
        facade = {"project_connection_id": "my-connection"}

        with pytest.raises(InvalidToolFacadeError) as exc_info:
            ensure_foundry_tool(facade)

        assert "type" in str(exc_info.value).lower()

    def test_raises_error_when_type_is_empty_string(self):
        """Test that InvalidToolFacadeError is raised when 'type' is empty string."""
        facade = {"type": "", "project_connection_id": "my-connection"}

        with pytest.raises(InvalidToolFacadeError) as exc_info:
            ensure_foundry_tool(facade)

        assert "type" in str(exc_info.value).lower()

    def test_raises_error_when_type_is_not_string(self):
        """Test that InvalidToolFacadeError is raised when 'type' is not a string."""
        facade = {"type": 123, "project_connection_id": "my-connection"}

        with pytest.raises(InvalidToolFacadeError) as exc_info:
            ensure_foundry_tool(facade)

        assert "type" in str(exc_info.value).lower()

    def test_raises_error_when_mcp_protocol_missing_connection_id(self):
        """Test that InvalidToolFacadeError is raised when mcp protocol is missing project_connection_id."""
        facade = {"type": "mcp"}

        with pytest.raises(InvalidToolFacadeError) as exc_info:
            ensure_foundry_tool(facade)

        assert "project_connection_id" in str(exc_info.value)

    def test_raises_error_when_a2a_protocol_has_empty_connection_id(self):
        """Test that InvalidToolFacadeError is raised when a2a protocol has empty project_connection_id."""
        facade = {"type": "a2a", "project_connection_id": ""}

        with pytest.raises(InvalidToolFacadeError) as exc_info:
            ensure_foundry_tool(facade)

        assert "project_connection_id" in str(exc_info.value)

    def test_parses_resource_id_format_connection_id(self):
        """Test that resource ID format project_connection_id is parsed correctly."""
        resource_id = (
            "/subscriptions/sub-123/resourceGroups/rg-test/providers/"
            "Microsoft.CognitiveServices/accounts/acc-test/projects/proj-test/connections/my-conn-name"
        )
        facade = {
            "type": "mcp",
            "project_connection_id": resource_id
        }

        result = ensure_foundry_tool(facade)

        assert isinstance(result, FoundryConnectedTool)
        assert result.project_connection_id == "my-conn-name"

    def test_raises_error_for_invalid_resource_id_format(self):
        """Test that InvalidToolFacadeError is raised for invalid resource ID format."""
        invalid_resource_id = "/subscriptions/sub-123/invalid/path"
        facade = {
            "type": "mcp",
            "project_connection_id": invalid_resource_id
        }

        with pytest.raises(InvalidToolFacadeError) as exc_info:
            ensure_foundry_tool(facade)

        assert "Invalid resource ID format" in str(exc_info.value)

    def test_uses_simple_connection_name_as_is(self):
        """Test that simple connection name is used as-is without parsing."""
        facade = {
            "type": "mcp",
            "project_connection_id": "simple-connection-name"
        }

        result = ensure_foundry_tool(facade)

        assert isinstance(result, FoundryConnectedTool)
        assert result.project_connection_id == "simple-connection-name"

    def test_original_facade_not_modified(self):
        """Test that the original facade dictionary is not modified."""
        facade = {
            "type": "my_tool",
            "config_key": "config_value"
        }
        original_facade = facade.copy()

        ensure_foundry_tool(facade)

        assert facade == original_facade

    def test_hosted_mcp_tool_with_no_extra_configuration(self):
        """Test that hosted MCP tool works with no extra configuration."""
        facade = {"type": "simple_tool"}

        result = ensure_foundry_tool(facade)

        assert isinstance(result, FoundryHostedMcpTool)
        assert result.name == "simple_tool"
        assert result.configuration == {}
