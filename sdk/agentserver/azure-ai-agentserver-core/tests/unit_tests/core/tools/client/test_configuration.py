# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryToolClientConfiguration."""

from azure.core.pipeline import policies

from azure.ai.agentserver.core.tools.client._configuration import FoundryToolClientConfiguration


class TestFoundryToolClientConfiguration:
    """Tests for FoundryToolClientConfiguration class."""

    def test_init_creates_all_required_policies(self, mock_credential):
        """Test that initialization creates all required pipeline policies."""
        config = FoundryToolClientConfiguration(mock_credential)

        assert isinstance(config.retry_policy, policies.AsyncRetryPolicy)
        assert isinstance(config.logging_policy, policies.NetworkTraceLoggingPolicy)
        assert isinstance(config.request_id_policy, policies.RequestIdPolicy)
        assert isinstance(config.http_logging_policy, policies.HttpLoggingPolicy)
        assert isinstance(config.user_agent_policy, policies.UserAgentPolicy)
        assert isinstance(config.authentication_policy, policies.AsyncBearerTokenCredentialPolicy)
        assert isinstance(config.redirect_policy, policies.AsyncRedirectPolicy)

