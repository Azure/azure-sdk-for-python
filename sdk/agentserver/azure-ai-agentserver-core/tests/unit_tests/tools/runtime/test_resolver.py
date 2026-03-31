# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for _resolver.py - testing public methods of DefaultFoundryToolInvocationResolver."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from azure.ai.agentserver.core.tools.runtime._resolver import DefaultFoundryToolInvocationResolver
from azure.ai.agentserver.core.tools.runtime._invoker import DefaultFoundryToolInvoker
from azure.ai.agentserver.core.tools._exceptions import UnableToResolveToolInvocationError
from azure.ai.agentserver.core.tools.client._models import (
    FoundryConnectedTool,
    FoundryHostedMcpTool,
)


class TestDefaultFoundryToolInvocationResolverResolve:
    """Tests for DefaultFoundryToolInvocationResolver.resolve method."""

    @pytest.fixture
    def mock_catalog(self, sample_resolved_mcp_tool):
        """Create a mock FoundryToolCatalog."""
        catalog = AsyncMock()
        catalog.get = AsyncMock(return_value=sample_resolved_mcp_tool)
        catalog.list = AsyncMock(return_value=[sample_resolved_mcp_tool])
        return catalog

    @pytest.mark.asyncio
    async def test_resolve_with_resolved_tool_returns_invoker_directly(
        self,
        mock_catalog,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_resolved_mcp_tool
    ):
        """Test resolve returns invoker directly when given ResolvedFoundryTool."""
        resolver = DefaultFoundryToolInvocationResolver(
            catalog=mock_catalog,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        invoker = await resolver.resolve(sample_resolved_mcp_tool)

        assert isinstance(invoker, DefaultFoundryToolInvoker)
        assert invoker.resolved_tool is sample_resolved_mcp_tool
        # Catalog should not be called when ResolvedFoundryTool is passed
        mock_catalog.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolve_with_foundry_tool_uses_catalog(
        self,
        mock_catalog,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_hosted_mcp_tool,
        sample_resolved_mcp_tool
    ):
        """Test resolve uses catalog to resolve FoundryTool."""
        mock_catalog.get = AsyncMock(return_value=sample_resolved_mcp_tool)

        resolver = DefaultFoundryToolInvocationResolver(
            catalog=mock_catalog,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        invoker = await resolver.resolve(sample_hosted_mcp_tool)

        assert isinstance(invoker, DefaultFoundryToolInvoker)
        mock_catalog.get.assert_called_once_with(sample_hosted_mcp_tool)

    @pytest.mark.asyncio
    async def test_resolve_with_facade_dict_uses_catalog(
        self,
        mock_catalog,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_resolved_connected_tool
    ):
        """Test resolve converts facade dict and uses catalog."""
        mock_catalog.get = AsyncMock(return_value=sample_resolved_connected_tool)
        facade = {
            "type": "mcp",
            "project_connection_id": "test-connection"
        }

        resolver = DefaultFoundryToolInvocationResolver(
            catalog=mock_catalog,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        invoker = await resolver.resolve(facade)

        assert isinstance(invoker, DefaultFoundryToolInvoker)
        mock_catalog.get.assert_called_once()
        # Verify the facade was converted to FoundryConnectedTool
        call_arg = mock_catalog.get.call_args[0][0]
        assert isinstance(call_arg, FoundryConnectedTool)

    @pytest.mark.asyncio
    async def test_resolve_raises_error_when_tool_not_found_in_catalog(
        self,
        mock_catalog,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_hosted_mcp_tool
    ):
        """Test resolve raises UnableToResolveToolInvocationError when catalog returns None."""
        mock_catalog.get = AsyncMock(return_value=None)

        resolver = DefaultFoundryToolInvocationResolver(
            catalog=mock_catalog,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        with pytest.raises(UnableToResolveToolInvocationError) as exc_info:
            await resolver.resolve(sample_hosted_mcp_tool)

        assert exc_info.value.tool is sample_hosted_mcp_tool
        assert "Unable to resolve tool" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_resolve_with_hosted_mcp_facade(
        self,
        mock_catalog,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_resolved_mcp_tool
    ):
        """Test resolve with hosted MCP facade (unknown type becomes FoundryHostedMcpTool)."""
        mock_catalog.get = AsyncMock(return_value=sample_resolved_mcp_tool)
        facade = {
            "type": "custom_mcp_tool",
            "config_key": "config_value"
        }

        resolver = DefaultFoundryToolInvocationResolver(
            catalog=mock_catalog,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        invoker = await resolver.resolve(facade)

        assert isinstance(invoker, DefaultFoundryToolInvoker)
        # Verify the facade was converted to FoundryHostedMcpTool
        call_arg = mock_catalog.get.call_args[0][0]
        assert isinstance(call_arg, FoundryHostedMcpTool)
        assert call_arg.name == "custom_mcp_tool"

    @pytest.mark.asyncio
    async def test_resolve_returns_invoker_with_correct_agent_name(
        self,
        mock_catalog,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_resolved_mcp_tool
    ):
        """Test resolve creates invoker with the correct agent name."""
        resolver = DefaultFoundryToolInvocationResolver(
            catalog=mock_catalog,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="custom-agent-name"
        )

        invoker = await resolver.resolve(sample_resolved_mcp_tool)

        # Verify invoker was created with correct agent name by checking internal state
        assert invoker._agent_name == "custom-agent-name"

    @pytest.mark.asyncio
    async def test_resolve_with_connected_tool_directly(
        self,
        mock_catalog,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_connected_tool,
        sample_resolved_connected_tool
    ):
        """Test resolve with FoundryConnectedTool directly."""
        mock_catalog.get = AsyncMock(return_value=sample_resolved_connected_tool)

        resolver = DefaultFoundryToolInvocationResolver(
            catalog=mock_catalog,
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        invoker = await resolver.resolve(sample_connected_tool)

        assert isinstance(invoker, DefaultFoundryToolInvoker)
        mock_catalog.get.assert_called_once_with(sample_connected_tool)
