# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Tests for AgentEndpoint deprecation warning."""

import warnings
import pytest


class TestAgentEndpointDeprecation:
    """Test that AgentEndpoint is deprecated but still functional."""

    def test_agent_endpoint_emits_deprecation_warning(self):
        """Test that using AgentEndpoint emits a DeprecationWarning."""
        from azure.ai.projects.models import AgentEndpoint

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            endpoint = AgentEndpoint()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "AgentEndpoint" in str(w[0].message)
            assert "AgentEndpointConfig" in str(w[0].message)

    def test_agent_endpoint_config_no_warning(self):
        """Test that using AgentEndpointConfig does not emit a warning."""
        from azure.ai.projects.models import AgentEndpointConfig

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = AgentEndpointConfig()

            # Filter only DeprecationWarnings related to AgentEndpoint
            deprecation_warnings = [
                warning for warning in w
                if issubclass(warning.category, DeprecationWarning)
                and "AgentEndpoint" in str(warning.message)
            ]
            assert len(deprecation_warnings) == 0

    def test_agent_endpoint_is_subclass_of_config(self):
        """Test that AgentEndpoint is a subclass of AgentEndpointConfig."""
        from azure.ai.projects.models import AgentEndpoint, AgentEndpointConfig

        assert issubclass(AgentEndpoint, AgentEndpointConfig)

    def test_agent_endpoint_instance_is_config_instance(self):
        """Test that AgentEndpoint instance is also an AgentEndpointConfig instance."""
        from azure.ai.projects.models import AgentEndpoint, AgentEndpointConfig

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            endpoint = AgentEndpoint()

        assert isinstance(endpoint, AgentEndpointConfig)

    def test_agent_endpoint_functionality_preserved(self):
        """Test that AgentEndpoint still works with all its parameters."""
        from azure.ai.projects.models import AgentEndpoint, AgentEndpointProtocol

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            endpoint = AgentEndpoint(
                protocols=[AgentEndpointProtocol.A2A],
            )

        assert endpoint.protocols == [AgentEndpointProtocol.A2A]
