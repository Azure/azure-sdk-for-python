#!/usr/bin/env python3
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for OTEL context attributes in AgentRunContextMiddleware."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from azure.ai.agentserver.core.server.base import AgentRunContextMiddleware
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext


class TestAgentRunContextMiddlewareOtelAttributes:
    """Test suite for OTEL attributes in AgentRunContextMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create a middleware instance for testing."""
        mock_app = MagicMock()
        return AgentRunContextMiddleware(mock_app)

    def test_set_run_context_with_valid_agent(self, middleware):
        """Test that context is set with correct OTEL attributes for valid agent."""
        # Create a mock agent object
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"
        mock_agent.version = "1.0.0"

        # Create a mock AgentRunContext
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.response_id = "resp-123"
        mock_context.conversation_id = "conv-456"
        mock_context.stream = False
        mock_context.get_agent_id_object.return_value = mock_agent

        # Mock request_context
        with patch("azure.ai.agentserver.core.server.base.request_context") as mock_req_context:
            mock_req_context.get.return_value = {}

            # Call the method
            middleware.set_run_context_to_context_var(mock_context)

            # Verify request_context.set was called
            mock_req_context.set.assert_called_once()

            # Get the context dict that was set
            call_args = mock_req_context.set.call_args
            ctx = call_args[0][0]

            # Assert OTEL attributes are set correctly
            assert ctx["gen_ai.operation.name"] == "invoke_agent"
            assert ctx["gen_ai.agent.id"] == "TestAgent:1.0.0"
            assert ctx["gen_ai.agent.name"] == "TestAgent"
            assert ctx["gen_ai.provider.name"] == "AzureAI Hosted Agents"

    def test_set_run_context_with_no_agent(self, middleware):
        """Test that context is set with empty values when agent is None."""
        # Create a mock AgentRunContext with no agent
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.response_id = "resp-123"
        mock_context.conversation_id = "conv-456"
        mock_context.stream = False
        mock_context.get_agent_id_object.return_value = None

        # Mock request_context
        with patch("azure.ai.agentserver.core.server.base.request_context") as mock_req_context:
            mock_req_context.get.return_value = {}

            # Call the method
            middleware.set_run_context_to_context_var(mock_context)

            # Get the context dict that was set
            call_args = mock_req_context.set.call_args
            ctx = call_args[0][0]

            # Assert OTEL attributes are set with empty values
            assert ctx["gen_ai.operation.name"] == "invoke_agent"
            assert ctx["gen_ai.agent.id"] == ""
            assert ctx["gen_ai.agent.name"] == ""
            assert ctx["gen_ai.provider.name"] == "AzureAI Hosted Agents"

    def test_set_run_context_preserves_existing_context(self, middleware):
        """Test that existing context values are preserved."""
        # Create a mock agent object
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"
        mock_agent.version = "1.0.0"

        # Create a mock AgentRunContext
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.response_id = "resp-123"
        mock_context.conversation_id = "conv-456"
        mock_context.stream = True
        mock_context.get_agent_id_object.return_value = mock_agent

        # Mock request_context with existing values
        existing_ctx = {"existing_key": "existing_value"}
        with patch("azure.ai.agentserver.core.server.base.request_context") as mock_req_context:
            mock_req_context.get.return_value = existing_ctx.copy()

            # Call the method
            middleware.set_run_context_to_context_var(mock_context)

            # Get the context dict that was set
            call_args = mock_req_context.set.call_args
            ctx = call_args[0][0]

            # Assert existing key is preserved
            assert ctx["existing_key"] == "existing_value"
            # Assert new keys are added
            assert ctx["gen_ai.operation.name"] == "invoke_agent"
            assert ctx["gen_ai.agent.name"] == "TestAgent"

    def test_set_run_context_with_streaming(self, middleware):
        """Test that streaming flag is correctly set in context."""
        # Create a mock agent object
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"
        mock_agent.version = "1.0.0"

        # Create a mock AgentRunContext with streaming enabled
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.response_id = "resp-123"
        mock_context.conversation_id = "conv-456"
        mock_context.stream = True
        mock_context.get_agent_id_object.return_value = mock_agent

        # Mock request_context
        with patch("azure.ai.agentserver.core.server.base.request_context") as mock_req_context:
            mock_req_context.get.return_value = {}

            # Call the method
            middleware.set_run_context_to_context_var(mock_context)

            # Get the context dict that was set
            call_args = mock_req_context.set.call_args
            ctx = call_args[0][0]

            # Assert streaming flag is set
            assert ctx["azure.ai.agentserver.streaming"] == "True"

    def test_set_run_context_with_none_values(self, middleware):
        """Test that None response/conversation IDs are converted to empty strings."""
        # Create a mock agent object
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"
        mock_agent.version = "1.0.0"

        # Create a mock AgentRunContext with None IDs
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.response_id = None
        mock_context.conversation_id = None
        mock_context.stream = False
        mock_context.get_agent_id_object.return_value = mock_agent

        # Mock request_context
        with patch("azure.ai.agentserver.core.server.base.request_context") as mock_req_context:
            mock_req_context.get.return_value = {}

            # Call the method
            middleware.set_run_context_to_context_var(mock_context)

            # Get the context dict that was set
            call_args = mock_req_context.set.call_args
            ctx = call_args[0][0]

            # Assert None values are converted to empty strings
            assert ctx["azure.ai.agentserver.response_id"] == ""
            assert ctx["azure.ai.agentserver.conversation_id"] == ""
            assert ctx["gen_ai.response.id"] == ""
            assert ctx["gen_ai.conversation.id"] == ""

    def test_set_run_context_otel_attributes_completeness(self, middleware):
        """Test that all required OTEL attributes are present in context."""
        # Create a mock agent object
        mock_agent = MagicMock()
        mock_agent.name = "TestAgent"
        mock_agent.version = "1.0.0"

        # Create a mock AgentRunContext
        mock_context = MagicMock(spec=AgentRunContext)
        mock_context.response_id = "resp-123"
        mock_context.conversation_id = "conv-456"
        mock_context.stream = False
        mock_context.get_agent_id_object.return_value = mock_agent

        # Mock request_context
        with patch("azure.ai.agentserver.core.server.base.request_context") as mock_req_context:
            mock_req_context.get.return_value = {}

            # Call the method
            middleware.set_run_context_to_context_var(mock_context)

            # Get the context dict that was set
            call_args = mock_req_context.set.call_args
            ctx = call_args[0][0]

            # Assert all required attributes are present
            required_attributes = [
                "azure.ai.agentserver.response_id",
                "azure.ai.agentserver.conversation_id",
                "azure.ai.agentserver.streaming",
                "gen_ai.operation.name",
                "gen_ai.agent.id",
                "gen_ai.agent.name",
                "gen_ai.provider.name",
                "gen_ai.response.id",
                "gen_ai.conversation.id",
            ]
            for attr in required_attributes:
                assert attr in ctx, f"Missing required attribute: {attr}"

    def test_set_run_context_agent_id_format(self, middleware):
        """Test that agent ID is formatted correctly as 'name:version'."""
        # Test cases with different version values
        test_cases = [
            ("Agent1", "1.0.0", "Agent1:1.0.0"),
            ("Agent2", "2.1.0-beta", "Agent2:2.1.0-beta"),
            ("Agent3", "", "Agent3:"),
        ]

        for agent_name, agent_version, expected_id in test_cases:
            # Create a mock agent object
            mock_agent = MagicMock()
            mock_agent.name = agent_name
            mock_agent.version = agent_version

            # Create a mock AgentRunContext
            mock_context = MagicMock(spec=AgentRunContext)
            mock_context.response_id = "resp-123"
            mock_context.conversation_id = "conv-456"
            mock_context.stream = False
            mock_context.get_agent_id_object.return_value = mock_agent

            # Mock request_context
            with patch("azure.ai.agentserver.core.server.base.request_context") as mock_req_context:
                mock_req_context.get.return_value = {}

                # Call the method
                middleware.set_run_context_to_context_var(mock_context)

                # Get the context dict that was set
                call_args = mock_req_context.set.call_args
                ctx = call_args[0][0]

                # Assert agent ID format
                assert ctx["gen_ai.agent.id"] == expected_id
