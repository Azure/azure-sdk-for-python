# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for AgentConfig."""
import pytest

from azure.ai.agentserver.core._config import AgentConfig


class TestAgentConfigIsHosted:
    """Tests for AgentConfig.is_hosted snapshotting behavior."""

    def test_is_hosted_false_when_env_var_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """is_hosted is False when FOUNDRY_HOSTING_ENVIRONMENT is not set."""
        monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
        config = AgentConfig.from_env()
        assert config.is_hosted is False

    def test_is_hosted_false_when_env_var_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """is_hosted is False when FOUNDRY_HOSTING_ENVIRONMENT is set to an empty string."""
        monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "")
        config = AgentConfig.from_env()
        assert config.is_hosted is False

    def test_is_hosted_true_when_env_var_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """is_hosted is True when FOUNDRY_HOSTING_ENVIRONMENT is set to a non-empty value."""
        monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "production")
        config = AgentConfig.from_env()
        assert config.is_hosted is True

    def test_is_hosted_snapshotted_at_creation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """is_hosted reflects the env var value at creation time, not at access time."""
        monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "production")
        config = AgentConfig.from_env()
        assert config.is_hosted is True

        # Changing the env var after creation must not affect the already-created config.
        monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT")
        assert config.is_hosted is True
