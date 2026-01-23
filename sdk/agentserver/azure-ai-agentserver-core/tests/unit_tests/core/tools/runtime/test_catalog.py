# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for _catalog.py - testing public methods of DefaultFoundryToolCatalog."""
import asyncio
import pytest
from unittest.mock import AsyncMock

from azure.ai.agentserver.core.tools.runtime._catalog import (
    DefaultFoundryToolCatalog,
)
from azure.ai.agentserver.core.tools.client._models import (
    FoundryToolDetails,
    ResolvedFoundryTool,
    UserInfo,
)


class TestFoundryToolCatalogGet:
    """Tests for FoundryToolCatalog.get method."""

    @pytest.mark.asyncio
    async def test_get_returns_resolved_tool_when_found(
        self,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_hosted_mcp_tool,
        sample_tool_details,
        sample_user_info
    ):
        """Test get returns a resolved tool when the tool is found."""
        mock_foundry_tool_client.list_tools_details = AsyncMock(
            return_value={sample_hosted_mcp_tool.id: [sample_tool_details]}
        )

        catalog = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        result = await catalog.get(sample_hosted_mcp_tool)

        assert result is not None
        assert isinstance(result, ResolvedFoundryTool)
        assert result.details == sample_tool_details

    @pytest.mark.asyncio
    async def test_get_returns_none_when_not_found(
        self,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_hosted_mcp_tool
    ):
        """Test get returns None when the tool is not found."""
        mock_foundry_tool_client.list_tools_details = AsyncMock(return_value={})

        catalog = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        result = await catalog.get(sample_hosted_mcp_tool)

        assert result is None


class TestDefaultFoundryToolCatalogList:
    """Tests for DefaultFoundryToolCatalog.list method."""

    @pytest.mark.asyncio
    async def test_list_returns_empty_list_when_no_tools(
        self,
        mock_foundry_tool_client,
        mock_user_provider
    ):
        """Test list returns empty list when no tools are provided."""
        catalog = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        result = await catalog.list([])

        assert result == []

    @pytest.mark.asyncio
    async def test_list_returns_resolved_tools(
        self,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_hosted_mcp_tool,
        sample_tool_details
    ):
        """Test list returns resolved tools."""
        mock_foundry_tool_client.list_tools_details = AsyncMock(
            return_value={sample_hosted_mcp_tool.id: [sample_tool_details]}
        )

        catalog = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        result = await catalog.list([sample_hosted_mcp_tool])

        assert len(result) == 1
        assert isinstance(result[0], ResolvedFoundryTool)
        assert result[0].definition == sample_hosted_mcp_tool
        assert result[0].details == sample_tool_details

    @pytest.mark.asyncio
    async def test_list_multiple_tools_with_multiple_details(
        self,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_hosted_mcp_tool,
        sample_connected_tool,
        sample_schema_definition
    ):
        """Test list returns all resolved tools when tools have multiple details."""
        details1 = FoundryToolDetails(
            name="tool1",
            description="First tool",
            input_schema=sample_schema_definition
        )
        details2 = FoundryToolDetails(
            name="tool2",
            description="Second tool",
            input_schema=sample_schema_definition
        )

        mock_foundry_tool_client.list_tools_details = AsyncMock(
            return_value={
                sample_hosted_mcp_tool.id: [details1],
                sample_connected_tool.id: [details2]
            }
        )

        catalog = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        result = await catalog.list([sample_hosted_mcp_tool, sample_connected_tool])

        assert len(result) == 2
        names = {r.details.name for r in result}
        assert names == {"tool1", "tool2"}

    @pytest.mark.asyncio
    async def test_list_caches_results_for_hosted_mcp_tools(
        self,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_hosted_mcp_tool,
        sample_tool_details
    ):
        """Test that list caches results for hosted MCP tools."""
        mock_foundry_tool_client.list_tools_details = AsyncMock(
            return_value={sample_hosted_mcp_tool.id: [sample_tool_details]}
        )

        catalog = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        # First call
        result1 = await catalog.list([sample_hosted_mcp_tool])
        # Second call should use cache
        result2 = await catalog.list([sample_hosted_mcp_tool])

        # Client should only be called once
        assert mock_foundry_tool_client.list_tools_details.call_count == 1
        assert len(result1) == len(result2) == 1

    @pytest.mark.asyncio
    async def test_list_with_facade_dict(
        self,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_tool_details
    ):
        """Test list works with facade dictionaries."""
        facade = {"type": "custom_tool", "config": "value"}
        expected_id = "hosted_mcp:custom_tool"

        mock_foundry_tool_client.list_tools_details = AsyncMock(
            return_value={expected_id: [sample_tool_details]}
        )

        catalog = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        result = await catalog.list([facade])

        assert len(result) == 1
        assert result[0].details == sample_tool_details

    @pytest.mark.asyncio
    async def test_list_returns_multiple_details_per_tool(
        self,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_hosted_mcp_tool,
        sample_schema_definition
    ):
        """Test list returns multiple resolved tools when a tool has multiple details."""
        details1 = FoundryToolDetails(
            name="function1",
            description="First function",
            input_schema=sample_schema_definition
        )
        details2 = FoundryToolDetails(
            name="function2",
            description="Second function",
            input_schema=sample_schema_definition
        )

        mock_foundry_tool_client.list_tools_details = AsyncMock(
            return_value={sample_hosted_mcp_tool.id: [details1, details2]}
        )

        catalog = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        result = await catalog.list([sample_hosted_mcp_tool])

        assert len(result) == 2
        names = {r.details.name for r in result}
        assert names == {"function1", "function2"}

    @pytest.mark.asyncio
    async def test_list_handles_exception_from_client(
        self,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_hosted_mcp_tool
    ):
        """Test list propagates exception from client and clears cache."""
        mock_foundry_tool_client.list_tools_details = AsyncMock(
            side_effect=RuntimeError("Network error")
        )

        catalog = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        with pytest.raises(RuntimeError, match="Network error"):
            await catalog.list([sample_hosted_mcp_tool])

    @pytest.mark.asyncio
    async def test_list_connected_tool_cache_key_includes_user(
        self,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_connected_tool,
        sample_tool_details,
        sample_user_info
    ):
        """Test that connected tool cache key includes user info."""
        mock_foundry_tool_client.list_tools_details = AsyncMock(
            return_value={sample_connected_tool.id: [sample_tool_details]}
        )

        # Create a new user provider returning a different user
        other_user = UserInfo(object_id="other-oid", tenant_id="other-tid")
        mock_user_provider2 = AsyncMock()
        mock_user_provider2.get_user = AsyncMock(return_value=other_user)

        catalog1 = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        catalog2 = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider2,
            agent_name="test-agent"
        )

        # Both catalogs should be able to list tools
        result1 = await catalog1.list([sample_connected_tool])
        result2 = await catalog2.list([sample_connected_tool])

        assert len(result1) == 1
        assert len(result2) == 1


class TestCachedFoundryToolCatalogConcurrency:
    """Tests for CachedFoundryToolCatalog concurrency handling."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_share_single_fetch(
        self,
        mock_foundry_tool_client,
        mock_user_provider,
        sample_hosted_mcp_tool,
        sample_tool_details
    ):
        """Test that concurrent requests for the same tool share a single fetch."""
        call_count = 0
        fetch_event = asyncio.Event()

        async def slow_fetch(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            await fetch_event.wait()
            return {sample_hosted_mcp_tool.id: [sample_tool_details]}

        mock_foundry_tool_client.list_tools_details = slow_fetch

        catalog = DefaultFoundryToolCatalog(
            client=mock_foundry_tool_client,
            user_provider=mock_user_provider,
            agent_name="test-agent"
        )

        # Start two concurrent requests
        task1 = asyncio.create_task(catalog.list([sample_hosted_mcp_tool]))
        task2 = asyncio.create_task(catalog.list([sample_hosted_mcp_tool]))

        # Allow tasks to start
        await asyncio.sleep(0.01)

        # Release the fetch
        fetch_event.set()

        results = await asyncio.gather(task1, task2)

        # Both should get results, but fetch should only be called once
        assert len(results[0]) == 1
        assert len(results[1]) == 1
        assert call_count == 1
