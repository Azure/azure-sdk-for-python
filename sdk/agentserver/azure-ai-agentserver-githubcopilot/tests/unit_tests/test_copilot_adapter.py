# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# ---------------------------------------------------------
"""Unit tests for GitHubCopilotAdapter methods.

Tests cover get_model() and clear_default_model() functionality.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

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
        """get_model() returns None when no model is configured."""
        adapter = GitHubCopilotAdapter(session_config={})
        assert adapter.get_model() is None

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

    def test_clear_model_from_session_config(self):
        """clear_default_model() removes model from session config."""
        adapter = GitHubCopilotAdapter(session_config={"model": "gpt-4o"})
        assert adapter.get_model() == "gpt-4o"

        adapter.clear_default_model()

        assert adapter.get_model() is None

    def test_clear_model_without_foundry_resource(self):
        """clear_default_model() works when no Foundry resource is configured."""
        adapter = GitHubCopilotAdapter(session_config={"model": "gpt-4o"})

        # Should not raise an error
        adapter.clear_default_model()

        assert adapter.get_model() is None

    @patch('azure.ai.agentserver.githubcopilot._copilot_adapter.ModelCache')
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

    @patch('azure.ai.agentserver.githubcopilot._copilot_adapter.ModelCache')
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

    def test_clear_model_idempotent(self):
        """clear_default_model() can be called multiple times safely."""
        adapter = GitHubCopilotAdapter(session_config={"model": "gpt-4o"})

        adapter.clear_default_model()
        adapter.clear_default_model()  # Should not raise

        assert adapter.get_model() is None


# ---------------------------------------------------------------------------
# Integration test: clear and re-initialize workflow
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestClearAndReinitialize:
    """Test the workflow of clearing model and re-initializing."""

    @pytest.mark.asyncio
    @patch('azure.ai.agentserver.githubcopilot._copilot_adapter.ModelCache')
    async def test_clear_forces_rediscovery(self, mock_cache_class):
        """Clearing model should force re-discovery on next initialize()."""
        mock_cache_instance = MagicMock()
        mock_cache_class.return_value = mock_cache_instance

        # Set up a cached model
        mock_cache_instance.get_cache_info.return_value = {
            "selected_model": "gpt-4o",
            "age_hours": 1.0,
        }

        resource_url = "https://test.cognitiveservices.azure.com"
        adapter = GitHubCopilotAdapter(session_config={
            "_foundry_resource_url": resource_url,
        })

        # Mock credential
        mock_credential = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test_token"
        mock_credential.get_token.return_value = mock_token
        adapter._credential = mock_credential

        # First initialize should use cache
        with patch('azure.ai.agentserver.githubcopilot._copilot_adapter.discover_foundry_deployments') as mock_discover:
            await adapter.initialize()
            assert adapter.get_model() == "gpt-4o"
            mock_discover.assert_not_called()  # Should use cache

        # Clear model
        adapter.clear_default_model()
        assert adapter.get_model() is None

        # Verify cache was invalidated
        mock_cache_instance.invalidate.assert_called_once_with(resource_url)
