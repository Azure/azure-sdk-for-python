# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# ---------------------------------------------------------
"""Unit tests for GitHubCopilotAdapter methods.

Tests cover get_model() and clear_default_model() functionality.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from azure.ai.agentserver.githubcopilot._copilot_adapter import GitHubCopilotAdapter


# ---------------------------------------------------------------------------
# get_model() tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetModel:
    """Tests for GitHubCopilotAdapter.get_model()."""

    def test_get_model_when_configured(self):
        """get_model() returns the configured model name."""
        adapter = GitHubCopilotAdapter(session_config={"model": "gpt-4o"})
        assert adapter.get_model() == "gpt-4o"

    def test_get_model_when_not_configured(self):
        """get_model() returns default when no model is explicitly configured."""
        with patch.dict(os.environ, {}, clear=True):
            adapter = GitHubCopilotAdapter(session_config={})
            # _build_session_config() sets a default model (gpt-5)
            assert adapter.get_model() == "gpt-5"

    def test_get_model_with_default_config(self):
        """get_model() works with default session config."""
        with patch.dict(os.environ, {}, clear=True):
            adapter = GitHubCopilotAdapter()
            # Should return default model from _build_session_config()
            model = adapter.get_model()
            assert model is not None  # Default config sets a model


# ---------------------------------------------------------------------------
# clear_default_model() tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestClearDefaultModel:
    """Tests for GitHubCopilotAdapter.clear_default_model()."""

    def test_clear_model_without_foundry_resource(self):
        """clear_default_model() resets to environment default when no Foundry resource."""
        with patch.dict(os.environ, {"COPILOT_MODEL": "gpt-4"}, clear=True):
            adapter = GitHubCopilotAdapter(session_config={"model": "gpt-4o"})
            assert adapter.get_model() == "gpt-4o"

            adapter.clear_default_model()

            # Should reset to environment default (COPILOT_MODEL)
            assert adapter.get_model() == "gpt-4"

    def test_clear_model_without_foundry_uses_fallback(self):
        """clear_default_model() uses gpt-5 fallback when no env vars set."""
        with patch.dict(os.environ, {}, clear=True):
            adapter = GitHubCopilotAdapter(session_config={"model": "gpt-4o"})
            assert adapter.get_model() == "gpt-4o"

            adapter.clear_default_model()

            # Should reset to fallback default (gpt-5)
            assert adapter.get_model() == "gpt-5"

    @patch('azure.ai.agentserver.githubcopilot._model_cache.ModelCache')
    def test_clear_model_with_foundry_resource(self, mock_cache_class):
        """clear_default_model() invalidates cache when Foundry resource is configured."""
        mock_cache_instance = MagicMock()
        mock_cache_class.return_value = mock_cache_instance

        resource_url = "https://test.cognitiveservices.azure.com"
        adapter = GitHubCopilotAdapter(session_config={
            "model": "gpt-4o",
            "_foundry_resource_url": resource_url,
        })

        adapter.clear_default_model()

        # Verify model was removed from config
        assert adapter.get_model() is None

        # Verify cache was invalidated
        mock_cache_instance.invalidate.assert_called_once_with(resource_url)

    @patch('azure.ai.agentserver.githubcopilot._model_cache.ModelCache')
    def test_clear_model_handles_cache_errors(self, mock_cache_class):
        """clear_default_model() handles cache errors gracefully."""
        mock_cache_class.side_effect = Exception("Cache error")

        adapter = GitHubCopilotAdapter(session_config={
            "model": "gpt-4o",
            "_foundry_resource_url": "https://test.cognitiveservices.azure.com",
        })

        # Should not raise an exception
        adapter.clear_default_model()

        # Model should still be cleared from session config
        assert adapter.get_model() is None

    def test_clear_model_idempotent_non_foundry(self):
        """clear_default_model() can be called multiple times safely (non-Foundry)."""
        with patch.dict(os.environ, {"COPILOT_MODEL": "gpt-4"}, clear=True):
            adapter = GitHubCopilotAdapter(session_config={"model": "gpt-4o"})

            adapter.clear_default_model()
            adapter.clear_default_model()  # Should not raise

            # Should remain at environment default
            assert adapter.get_model() == "gpt-4"

    @patch('azure.ai.agentserver.githubcopilot._model_cache.ModelCache')
    def test_clear_model_idempotent_foundry(self, mock_cache_class):
        """clear_default_model() can be called multiple times safely (Foundry mode)."""
        mock_cache_instance = MagicMock()
        mock_cache_class.return_value = mock_cache_instance

        adapter = GitHubCopilotAdapter(session_config={
            "model": "gpt-4o",
            "_foundry_resource_url": "https://test.cognitiveservices.azure.com",
        })

        adapter.clear_default_model()
        adapter.clear_default_model()  # Should not raise

        # Should remain None in Foundry mode
        assert adapter.get_model() is None


# ---------------------------------------------------------------------------
# Integration test: clear and re-initialize workflow
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestClearAndReinitialize:
    """Test the workflow of clearing model and re-initializing."""

    @pytest.mark.asyncio
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.get_default_model')
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.discover_foundry_deployments')
    @patch('azure.ai.agentserver.githubcopilot._model_cache.ModelCache')
    async def test_clear_forces_rediscovery(self, mock_cache_class, mock_discover, mock_get_default):
        """Clearing model should force re-discovery on next initialize()."""
        mock_cache_instance = MagicMock()
        mock_cache_class.return_value = mock_cache_instance

        # Set up a cached model for first initialize
        mock_cache_instance.get_cache_info.return_value = {
            "selected_model": "gpt-4o",
            "age_hours": 1.0,
        }

        resource_url = "https://test.cognitiveservices.azure.com"
        adapter = GitHubCopilotAdapter(session_config={
            "_foundry_resource_url": resource_url,
        })

        # Remove default model so initialize() will check cache
        adapter._session_config.pop("model", None)

        # Mock credential
        mock_credential = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test_token"
        mock_credential.get_token.return_value = mock_token
        adapter._credential = mock_credential

        # First initialize should use cache
        await adapter.initialize()
        assert adapter.get_model() == "gpt-4o"
        mock_discover.assert_not_called()  # Should use cache

        # Clear model
        adapter.clear_default_model()
        assert adapter.get_model() is None

        # Verify cache was invalidated
        mock_cache_instance.invalidate.assert_called_once_with(resource_url)

        # After clearing, cache returns None (simulating cleared cache)
        mock_cache_instance.get_cache_info.return_value = None

        # Mock discovery to return a new model
        mock_deployment = MagicMock()
        mock_deployment.name = "gpt-4-turbo"
        mock_deployment.model_name = "gpt-4"
        mock_deployment.model_version = "turbo-2024-04-09"
        mock_deployment.model_format = "OpenAI"
        mock_deployment.token_rate_limit = 1000000
        mock_discover.return_value = [mock_deployment]
        mock_get_default.return_value = "gpt-4-turbo"

        # Second initialize should trigger discovery
        await adapter.initialize()
        assert adapter.get_model() == "gpt-4-turbo"
        mock_discover.assert_called_once()  # Discovery should be invoked
        mock_get_default.assert_called_once()


# ---------------------------------------------------------------------------
# wire_api selection tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestWireApiSelection:
    """Tests for dynamic wire_api selection based on model capabilities."""

    @pytest.mark.asyncio
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.get_default_model')
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.discover_foundry_deployments')
    @patch('azure.ai.agentserver.githubcopilot._model_cache.ModelCache')
    async def test_responses_capable_model_sets_responses_wire_api(
        self, mock_cache_class, mock_discover, mock_get_default
    ):
        """Model with responses=true should set wire_api to 'responses'."""
        from azure.ai.agentserver.githubcopilot._foundry_model_discovery import FoundryDeployment

        mock_cache_instance = MagicMock()
        mock_cache_class.return_value = mock_cache_instance
        mock_cache_instance.get_cache_info.return_value = None

        deployment = FoundryDeployment(
            name="gpt-5.3-codex",
            model_name="gpt-5.3-codex",
            model_version="2026-02-24",
            model_format="OpenAI",
            token_rate_limit=5000000,
            capabilities={"chatCompletion": "false", "responses": "true"},
        )
        mock_discover.return_value = [deployment]
        mock_get_default.return_value = "gpt-5.3-codex"

        from azure.ai.agentserver.githubcopilot._copilot_adapter import ProviderConfig
        adapter = GitHubCopilotAdapter(session_config={
            "_foundry_resource_url": "https://test.openai.azure.com",
            "provider": ProviderConfig(
                type="openai",
                base_url="https://test.openai.azure.com/openai/v1/",
                bearer_token="placeholder",
                wire_api="completions",
            ),
        })
        adapter._session_config.pop("model", None)

        mock_credential = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test_token"
        mock_credential.get_token.return_value = mock_token
        adapter._credential = mock_credential

        await adapter.initialize()

        assert adapter.get_model() == "gpt-5.3-codex"
        assert adapter._session_config["provider"]["wire_api"] == "responses"

    @pytest.mark.asyncio
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.get_default_model')
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.discover_foundry_deployments')
    @patch('azure.ai.agentserver.githubcopilot._model_cache.ModelCache')
    async def test_chat_only_model_sets_completions_wire_api(
        self, mock_cache_class, mock_discover, mock_get_default
    ):
        """Model with only chatCompletion=true should set wire_api to 'completions'."""
        from azure.ai.agentserver.githubcopilot._foundry_model_discovery import FoundryDeployment

        mock_cache_instance = MagicMock()
        mock_cache_class.return_value = mock_cache_instance
        mock_cache_instance.get_cache_info.return_value = None

        deployment = FoundryDeployment(
            name="gpt-4.1",
            model_name="gpt-4.1",
            model_version="2025-04-14",
            model_format="OpenAI",
            token_rate_limit=100000,
            capabilities={"chatCompletion": "true", "responses": "false"},
        )
        mock_discover.return_value = [deployment]
        mock_get_default.return_value = "gpt-4.1"

        from azure.ai.agentserver.githubcopilot._copilot_adapter import ProviderConfig
        adapter = GitHubCopilotAdapter(session_config={
            "_foundry_resource_url": "https://test.openai.azure.com",
            "provider": ProviderConfig(
                type="openai",
                base_url="https://test.openai.azure.com/openai/v1/",
                bearer_token="placeholder",
                wire_api="completions",
            ),
        })
        adapter._session_config.pop("model", None)

        mock_credential = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test_token"
        mock_credential.get_token.return_value = mock_token
        adapter._credential = mock_credential

        await adapter.initialize()

        assert adapter.get_model() == "gpt-4.1"
        assert adapter._session_config["provider"]["wire_api"] == "completions"

    @pytest.mark.asyncio
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.get_default_model')
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.discover_foundry_deployments')
    @patch('azure.ai.agentserver.githubcopilot._model_cache.ModelCache')
    async def test_both_capabilities_prefers_responses(
        self, mock_cache_class, mock_discover, mock_get_default
    ):
        """Model with both chatCompletion=true and responses=true should prefer responses."""
        from azure.ai.agentserver.githubcopilot._foundry_model_discovery import FoundryDeployment

        mock_cache_instance = MagicMock()
        mock_cache_class.return_value = mock_cache_instance
        mock_cache_instance.get_cache_info.return_value = None

        deployment = FoundryDeployment(
            name="gpt-4o",
            model_name="gpt-4o",
            model_version="2024-11-20",
            model_format="OpenAI",
            token_rate_limit=40000,
            capabilities={"chatCompletion": "true", "responses": "true"},
        )
        mock_discover.return_value = [deployment]
        mock_get_default.return_value = "gpt-4o"

        from azure.ai.agentserver.githubcopilot._copilot_adapter import ProviderConfig
        adapter = GitHubCopilotAdapter(session_config={
            "_foundry_resource_url": "https://test.openai.azure.com",
            "provider": ProviderConfig(
                type="openai",
                base_url="https://test.openai.azure.com/openai/v1/",
                bearer_token="placeholder",
                wire_api="completions",
            ),
        })
        adapter._session_config.pop("model", None)

        mock_credential = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test_token"
        mock_credential.get_token.return_value = mock_token
        adapter._credential = mock_credential

        await adapter.initialize()

        assert adapter.get_model() == "gpt-4o"
        assert adapter._session_config["provider"]["wire_api"] == "responses"


# ---------------------------------------------------------------------------
# Configured model matching tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConfiguredModelMatching:
    """Tests for validating configured model against discovered deployments."""

    @pytest.mark.asyncio
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.get_default_model')
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.discover_foundry_deployments')
    @patch('azure.ai.agentserver.githubcopilot._model_cache.ModelCache')
    async def test_configured_model_matched(
        self, mock_cache_class, mock_discover, mock_get_default
    ):
        """Configured model found in deployments keeps that model."""
        from azure.ai.agentserver.githubcopilot._foundry_model_discovery import FoundryDeployment

        mock_cache_instance = MagicMock()
        mock_cache_class.return_value = mock_cache_instance
        mock_cache_instance.get_cache_info.return_value = None

        deployments = [
            FoundryDeployment(
                name="gpt-5.3-codex", model_name="gpt-5.3-codex",
                model_version="2026-02-24", token_rate_limit=5000000,
                capabilities={"responses": "true"},
            ),
            FoundryDeployment(
                name="gpt-4o", model_name="gpt-4o",
                model_version="2024-11-20", token_rate_limit=40000,
                capabilities={"chatCompletion": "true", "responses": "true"},
            ),
        ]
        mock_discover.return_value = deployments

        from azure.ai.agentserver.githubcopilot._copilot_adapter import ProviderConfig
        adapter = GitHubCopilotAdapter(session_config={
            "model": "gpt-4o",
            "_foundry_resource_url": "https://test.openai.azure.com",
            "provider": ProviderConfig(
                type="openai",
                base_url="https://test.openai.azure.com/openai/v1/",
                bearer_token="placeholder",
                wire_api="completions",
            ),
        })

        mock_credential = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test_token"
        mock_credential.get_token.return_value = mock_token
        adapter._credential = mock_credential

        await adapter.initialize()

        assert adapter.get_model() == "gpt-4o"
        assert adapter._session_config["provider"]["wire_api"] == "responses"
        mock_get_default.assert_not_called()  # Should not auto-select

    @pytest.mark.asyncio
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.get_default_model')
    @patch('azure.ai.agentserver.githubcopilot._foundry_model_discovery.discover_foundry_deployments')
    @patch('azure.ai.agentserver.githubcopilot._model_cache.ModelCache')
    async def test_configured_model_not_found_auto_selects(
        self, mock_cache_class, mock_discover, mock_get_default
    ):
        """Configured model not in deployments triggers auto-selection."""
        from azure.ai.agentserver.githubcopilot._foundry_model_discovery import FoundryDeployment

        mock_cache_instance = MagicMock()
        mock_cache_class.return_value = mock_cache_instance
        mock_cache_instance.get_cache_info.return_value = None

        deployment = FoundryDeployment(
            name="gpt-5.3-codex", model_name="gpt-5.3-codex",
            model_version="2026-02-24", token_rate_limit=5000000,
            capabilities={"responses": "true"},
        )
        mock_discover.return_value = [deployment]
        mock_get_default.return_value = "gpt-5.3-codex"

        from azure.ai.agentserver.githubcopilot._copilot_adapter import ProviderConfig
        adapter = GitHubCopilotAdapter(session_config={
            "model": "nonexistent-model",
            "_foundry_resource_url": "https://test.openai.azure.com",
            "provider": ProviderConfig(
                type="openai",
                base_url="https://test.openai.azure.com/openai/v1/",
                bearer_token="placeholder",
                wire_api="completions",
            ),
        })

        mock_credential = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test_token"
        mock_credential.get_token.return_value = mock_token
        adapter._credential = mock_credential

        await adapter.initialize()

        assert adapter.get_model() == "gpt-5.3-codex"
        assert adapter._session_config["provider"]["wire_api"] == "responses"
        mock_get_default.assert_called_once()
