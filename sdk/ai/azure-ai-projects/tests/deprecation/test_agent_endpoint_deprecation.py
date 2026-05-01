# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Tests for AgentEndpoint deprecation warning."""

import warnings

class TestAgentEndpointDeprecation:
    """Test that AgentEndpoint is deprecated but still functional (PEP 562 __getattr__)."""

    def test_agent_endpoint_emits_deprecation_warning_on_access(self):
        """Test that accessing AgentEndpoint emits a DeprecationWarning (PEP 562)."""
        import azure.ai.projects.models as models

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Warning is emitted on attribute access, not instantiation
            _ = models.AgentEndpoint  # type: ignore[attr-defined]

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "AgentEndpoint" in str(w[0].message)
            assert "AgentEndpointConfig" in str(w[0].message)

    def test_agent_endpoint_config_no_warning(self):
        """Test that using AgentEndpointConfig does not emit a warning."""
        import azure.ai.projects.models as models

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = models.AgentEndpointConfig
            config = models.AgentEndpointConfig()

            # Filter only DeprecationWarnings related to AgentEndpoint
            deprecation_warnings = [
                warning for warning in w
                if issubclass(warning.category, DeprecationWarning)
                and "AgentEndpoint" in str(warning.message)
            ]
            assert len(deprecation_warnings) == 0

    def test_agent_endpoint_is_same_class_as_config(self):
        """Test that AgentEndpoint returns the same class as AgentEndpointConfig (PEP 562)."""
        import azure.ai.projects.models as models

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            # With PEP 562 __getattr__, AgentEndpoint IS AgentEndpointConfig
            assert models.AgentEndpoint is models.AgentEndpointConfig  # type: ignore[attr-defined]

    def test_agent_endpoint_instance_is_config_instance(self):
        """Test that AgentEndpoint instance is also an AgentEndpointConfig instance."""
        import azure.ai.projects.models as models

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            endpoint = models.AgentEndpoint()  # type: ignore[attr-defined]

        assert isinstance(endpoint, models.AgentEndpointConfig)

    def test_agent_endpoint_functionality_preserved(self):
        """Test that AgentEndpoint still works with all its parameters."""
        import azure.ai.projects.models as models

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            endpoint = models.AgentEndpoint(  # type: ignore[attr-defined]
                protocols=[models.AgentEndpointProtocol.A2A],
            )

        assert endpoint.protocols == [models.AgentEndpointProtocol.A2A]
