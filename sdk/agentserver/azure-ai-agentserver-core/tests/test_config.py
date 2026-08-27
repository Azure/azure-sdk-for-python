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


class TestAgentConfigAgentGuid:
    """Tests for the FOUNDRY_AGENT_ID (agent_guid) resolution."""

    def test_agent_guid_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FOUNDRY_AGENT_ID", "11111111-2222-3333-4444-555555555555")
        config = AgentConfig.from_env()
        assert config.agent_guid == "11111111-2222-3333-4444-555555555555"

    def test_agent_guid_empty_when_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("FOUNDRY_AGENT_ID", raising=False)
        config = AgentConfig.from_env()
        assert config.agent_guid == ""

    def test_agent_guid_distinct_from_composite_agent_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """agent_guid (GUID) is independent of the name:version composite agent_id."""
        monkeypatch.setenv("FOUNDRY_AGENT_NAME", "weather")
        monkeypatch.setenv("FOUNDRY_AGENT_VERSION", "1")
        monkeypatch.setenv("FOUNDRY_AGENT_ID", "guid-abc")
        config = AgentConfig.from_env()
        assert config.agent_id == "weather:1"
        assert config.agent_guid == "guid-abc"
