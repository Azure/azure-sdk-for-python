# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryToolContext."""
import pytest

from azure.ai.agentserver.langgraph.tools._context import FoundryToolContext
from azure.ai.agentserver.langgraph.tools._resolver import ResolvedTools


@pytest.mark.unit
class TestFoundryToolContext:
    """Tests for FoundryToolContext class."""

    def test_create_with_resolved_tools(self, sample_resolved_tools: ResolvedTools):
        """Test creating FoundryToolContext with resolved tools."""
        context = FoundryToolContext(resolved_tools=sample_resolved_tools)

        assert context.resolved_tools is sample_resolved_tools

    def test_create_with_default_resolved_tools(self):
        """Test creating FoundryToolContext with default empty resolved tools."""
        context = FoundryToolContext()

        # Default should be empty ResolvedTools
        assert context.resolved_tools is not None
        tools_list = list(context.resolved_tools)
        assert len(tools_list) == 0

    def test_resolved_tools_is_iterable(self, sample_resolved_tools: ResolvedTools):
        """Test that resolved_tools can be iterated."""
        context = FoundryToolContext(resolved_tools=sample_resolved_tools)

        tools_list = list(context.resolved_tools)
        assert len(tools_list) == 1

