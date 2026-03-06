#!/usr/bin/env python3
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for get_agent_name function."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from azure.ai.agentserver.core.server.base import get_agent_name
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext


class TestGetAgentName:
    """Test suite for get_agent_name function."""

    def test_get_agent_name_with_valid_agent_object(self):
        """Test get_agent_name with valid agent object."""
        # Create a mock agent object
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"
        mock_agent.version = "1.0.0"

        # Create a mock AgentRunContext
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.get_agent_id_object.return_value = mock_agent

        # Call get_agent_name
        agent_name, agent_id = get_agent_name(mock_context)

        # Assert results
        assert agent_name == "TestAgent"
        assert agent_id == "TestAgent:1.0.0"

    def test_get_agent_name_with_no_version(self):
        """Test get_agent_name when agent has no version."""
        # Create a mock agent object with no version
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"
        mock_agent.version = ""

        # Create a mock AgentRunContext
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.get_agent_id_object.return_value = mock_agent

        # Call get_agent_name
        agent_name, agent_id = get_agent_name(mock_context)

        # Assert results
        assert agent_name == "TestAgent"
        assert agent_id == "TestAgent:"

    def test_get_agent_name_with_none_agent_object(self):
        """Test get_agent_name when agent object is None."""
        # Create a mock AgentRunContext that returns None
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.get_agent_id_object.return_value = None

        # Call get_agent_name
        agent_name, agent_id = get_agent_name(mock_context)

        # Assert results
        assert agent_name is None
        assert agent_id == ""

    def test_get_agent_name_with_none_context(self):
        """Test get_agent_name with None context."""
        # Call get_agent_name with None
        agent_name, agent_id = get_agent_name(None)

        # Assert results
        assert agent_name is None
        assert agent_id == ""

    def test_get_agent_name_with_missing_name_attribute(self):
        """Test get_agent_name when agent object has no name attribute."""
        # Create a mock agent object without name
        mock_agent = MagicMock()
        mock_agent.name = None
        mock_agent.version = "1.0.0"

        # Create a mock AgentRunContext
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.get_agent_id_object.return_value = mock_agent

        # Call get_agent_name
        agent_name, agent_id = get_agent_name(mock_context)

        # Assert results - agent_id should not be set if name is None
        assert agent_name is None
        assert agent_id == ""

    def test_get_agent_name_with_empty_name(self):
        """Test get_agent_name when agent name is empty string."""
        # Create a mock agent object with empty name
        mock_agent = MagicMock()
        mock_agent.name = ""
        mock_agent.version = "1.0.0"

        # Create a mock AgentRunContext
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.get_agent_id_object.return_value = mock_agent

        # Call get_agent_name
        agent_name, agent_id = get_agent_name(mock_context)

        # Assert results - agent_id should not be set if name is empty
        assert agent_name == ""
        assert agent_id == ""

    def test_get_agent_name_return_type(self):
        """Test that get_agent_name returns a tuple."""
        # Create a mock agent object
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"
        mock_agent.version = "2.0.0"

        # Create a mock AgentRunContext
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.get_agent_id_object.return_value = mock_agent

        # Call get_agent_name
        result = get_agent_name(mock_context)

        # Assert result is a tuple of length 2
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_get_agent_name_with_special_characters(self):
        """Test get_agent_name with special characters in agent name and version."""
        # Create a mock agent object with special characters
        mock_agent = MagicMock()
        mock_agent.name = "Test-Agent_v2"
        mock_agent.version = "2.0.0-beta.1"

        # Create a mock AgentRunContext
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.get_agent_id_object.return_value = mock_agent

        # Call get_agent_name
        agent_name, agent_id = get_agent_name(mock_context)

        # Assert results
        assert agent_name == "Test-Agent_v2"
        assert agent_id == "Test-Agent_v2:2.0.0-beta.1"
