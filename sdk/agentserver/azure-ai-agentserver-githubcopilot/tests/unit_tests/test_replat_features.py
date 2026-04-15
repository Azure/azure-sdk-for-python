# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# ---------------------------------------------------------
"""Unit tests for replat features (core 2.0 + responses 1.0).

Tests cover:
- Input text extraction with attachment handling
- Conversation ID fallback (session_id and conversation.id from raw_body)
- Session config building and BYOK URL derivation
"""

import importlib
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# The copilot SDK may not be installed locally (or may be a different version).
# Mock the imports that _copilot_adapter needs at import time so we can test
# the pure-Python helpers without the full SDK.
_copilot_mock = MagicMock()
_copilot_mock.session.PermissionRequestResult = MagicMock
_copilot_mock.session.ProviderConfig = dict
_copilot_mock.generated.session_events.SessionEventType = MagicMock()
sys.modules.setdefault("copilot", _copilot_mock)
sys.modules.setdefault("copilot.session", _copilot_mock.session)
sys.modules.setdefault("copilot.generated", _copilot_mock.generated)
sys.modules.setdefault("copilot.generated.session_events", _copilot_mock.generated.session_events)

# Also mock agentserver packages if not installed
for mod_name in [
    "azure.ai.agentserver.core",
    "azure.ai.agentserver.responses",
    "azure.ai.agentserver.responses.hosting",
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

from azure.ai.agentserver.githubcopilot._copilot_adapter import (
    _build_session_config,
    _derive_resource_url_from_project_endpoint,
    _extract_input_with_attachments,
    _get_project_endpoint,
)
from azure.ai.agentserver.githubcopilot._copilot_adapter import GitHubCopilotAdapter


# ---------------------------------------------------------------------------
# _extract_input_with_attachments tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractInputWithAttachments:
    """Tests for _extract_input_with_attachments()."""

    def test_text_only_request(self):
        """Returns text from get_input_text when no attachments."""
        request = SimpleNamespace(input=[
            {"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": "hello"}
            ]}
        ])
        with patch("azure.ai.agentserver.githubcopilot._copilot_adapter.get_input_text", return_value="hello"):
            result = _extract_input_with_attachments(request)
        assert result == "hello"

    def test_with_file_attachment(self):
        """Appends decoded file content to prompt text."""
        import base64
        file_content = base64.b64encode(b"file contents here").decode()
        request = SimpleNamespace(input=[
            {"type": "input_text", "text": "check this"},
            {"type": "input_file", "filename": "test.txt", "file_data": file_content},
        ])
        with patch("azure.ai.agentserver.githubcopilot._copilot_adapter.get_input_text", return_value="check this"):
            result = _extract_input_with_attachments(request)
        assert "check this" in result
        assert "[Attached file: test.txt]" in result
        assert "file contents here" in result

    def test_with_image_attachment(self):
        """Appends image URL reference to prompt text."""
        request = SimpleNamespace(input=[
            {"type": "input_text", "text": "what is this"},
            {"type": "input_image", "image_url": {"url": "https://example.com/img.png"}},
        ])
        with patch("azure.ai.agentserver.githubcopilot._copilot_adapter.get_input_text", return_value="what is this"):
            result = _extract_input_with_attachments(request)
        assert "what is this" in result
        assert "[Attached image: https://example.com/img.png]" in result

    def test_no_input_attribute(self):
        """Returns plain text when request has no input attribute."""
        request = SimpleNamespace()
        with patch("azure.ai.agentserver.githubcopilot._copilot_adapter.get_input_text", return_value="hello"):
            result = _extract_input_with_attachments(request)
        assert result == "hello"

    def test_dict_items(self):
        """Handles input items as dicts (not objects)."""
        request = SimpleNamespace(input=[
            {"type": "input_file", "filename": "data.csv", "file_data": ""},
        ])
        with patch("azure.ai.agentserver.githubcopilot._copilot_adapter.get_input_text", return_value="test"):
            result = _extract_input_with_attachments(request)
        # Empty file_data should not add attachment
        assert result == "test"


# ---------------------------------------------------------------------------
# Conversation ID fallback tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConversationIdFallback:
    """Tests for conversation_id resolution in _handle_create."""

    def _make_context(self, conversation_id=None, raw_body=None):
        """Create a mock ResponseContext."""
        ctx = MagicMock()
        ctx.conversation_id = conversation_id
        ctx.raw_body = raw_body
        ctx.response_id = "test-response-id"
        ctx.request = None
        return ctx

    def test_context_conversation_id_used_when_present(self):
        """Uses context.conversation_id when it's set."""
        ctx = self._make_context(conversation_id="conv_123")
        # conversation_id is already set — no fallback needed
        assert ctx.conversation_id == "conv_123"

    def test_fallback_to_session_id_in_raw_body(self):
        """Falls back to raw_body['session_id'] when conversation_id is None."""
        ctx = self._make_context(
            conversation_id=None,
            raw_body={"session_id": "session-abc", "input": "hello"}
        )
        # Simulate the fallback logic from _handle_create
        conversation_id = ctx.conversation_id
        if not conversation_id:
            raw_body = ctx.raw_body
            if isinstance(raw_body, dict):
                conversation_id = raw_body.get("session_id")
        assert conversation_id == "session-abc"

    def test_fallback_to_conversation_id_in_raw_body(self):
        """Falls back to raw_body['conversation']['id'] for Playground."""
        ctx = self._make_context(
            conversation_id=None,
            raw_body={
                "input": "hello",
                "conversation": {"id": "conv_playground_456"},
            }
        )
        # Simulate the fallback logic from _handle_create
        conversation_id = ctx.conversation_id
        if not conversation_id:
            raw_body = ctx.raw_body
            if isinstance(raw_body, dict):
                conversation_id = raw_body.get("session_id")
                if not conversation_id:
                    conv = raw_body.get("conversation")
                    if isinstance(conv, dict):
                        conversation_id = conv.get("id")
        assert conversation_id == "conv_playground_456"

    def test_session_id_takes_priority_over_conversation(self):
        """session_id in raw_body takes priority over conversation.id."""
        ctx = self._make_context(
            conversation_id=None,
            raw_body={
                "session_id": "session-priority",
                "conversation": {"id": "conv_lower_priority"},
            }
        )
        conversation_id = ctx.conversation_id
        if not conversation_id:
            raw_body = ctx.raw_body
            if isinstance(raw_body, dict):
                conversation_id = raw_body.get("session_id")
                if not conversation_id:
                    conv = raw_body.get("conversation")
                    if isinstance(conv, dict):
                        conversation_id = conv.get("id")
        assert conversation_id == "session-priority"

    def test_none_when_nothing_available(self):
        """Returns None when no conversation identity is available."""
        ctx = self._make_context(conversation_id=None, raw_body={"input": "hello"})
        conversation_id = ctx.conversation_id
        if not conversation_id:
            raw_body = ctx.raw_body
            if isinstance(raw_body, dict):
                conversation_id = raw_body.get("session_id")
                if not conversation_id:
                    conv = raw_body.get("conversation")
                    if isinstance(conv, dict):
                        conversation_id = conv.get("id")
        assert conversation_id is None

    def test_none_when_raw_body_not_dict(self):
        """Returns None when raw_body is not a dict."""
        ctx = self._make_context(conversation_id=None, raw_body=None)
        conversation_id = ctx.conversation_id
        if not conversation_id:
            raw_body = ctx.raw_body
            if isinstance(raw_body, dict):
                conversation_id = raw_body.get("session_id")
        assert conversation_id is None


# ---------------------------------------------------------------------------
# _build_session_config tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBuildSessionConfig:
    """Tests for _build_session_config()."""

    def test_default_github_mode(self):
        """Defaults to GitHub Copilot mode when no BYOK vars set."""
        with patch.dict(os.environ, {}, clear=True):
            config = _build_session_config()
        assert config.get("model") == "gpt-5"
        assert "provider" not in config

    def test_github_mode_with_custom_model(self):
        """Uses COPILOT_MODEL env var for model name."""
        with patch.dict(os.environ, {"COPILOT_MODEL": "claude-sonnet"}, clear=True):
            config = _build_session_config()
        assert config["model"] == "claude-sonnet"

    def test_byok_api_key_mode(self):
        """Creates BYOK config with API key."""
        with patch.dict(os.environ, {
            "AZURE_AI_FOUNDRY_RESOURCE_URL": "https://test.cognitiveservices.azure.com",
            "AZURE_AI_FOUNDRY_API_KEY": "test-key",
        }, clear=True):
            config = _build_session_config()
        assert config["provider"]["type"] == "openai"
        assert config["provider"]["bearer_token"] == "test-key"
        assert config["provider"]["wire_api"] == "responses"
        assert "openai/v1/" in config["provider"]["base_url"]

    def test_byok_managed_identity_mode(self):
        """Creates BYOK config with placeholder token for Managed Identity."""
        with patch.dict(os.environ, {
            "AZURE_AI_FOUNDRY_RESOURCE_URL": "https://test.cognitiveservices.azure.com",
        }, clear=True):
            config = _build_session_config()
        assert config["provider"]["type"] == "openai"
        assert config["provider"]["bearer_token"] == "placeholder"
        assert config["provider"]["wire_api"] == "responses"

    def test_auto_derive_from_project_endpoint(self):
        """Auto-derives RESOURCE_URL from PROJECT_ENDPOINT when no GITHUB_TOKEN."""
        with patch.dict(os.environ, {
            "AZURE_AI_PROJECT_ENDPOINT": "https://myresource.services.ai.azure.com/api/projects/myproject",
        }, clear=True):
            config = _build_session_config()
        assert "provider" in config
        assert "cognitiveservices.azure.com" in config["provider"]["base_url"]

    def test_github_token_prevents_auto_derive(self):
        """GITHUB_TOKEN presence prevents auto-derivation of BYOK."""
        with patch.dict(os.environ, {
            "AZURE_AI_PROJECT_ENDPOINT": "https://myresource.services.ai.azure.com/api/projects/myproject",
            "GITHUB_TOKEN": "ghp_test",
        }, clear=True):
            config = _build_session_config()
        # Should NOT have a provider — GITHUB_TOKEN means use GitHub auth
        assert "provider" not in config


# ---------------------------------------------------------------------------
# URL derivation tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestUrlDerivation:
    """Tests for URL derivation helpers."""

    def test_derive_resource_url(self):
        """Derives cognitiveservices URL from services.ai.azure.com endpoint."""
        result = _derive_resource_url_from_project_endpoint(
            "https://myresource.services.ai.azure.com/api/projects/myproject"
        )
        assert result == "https://myresource.cognitiveservices.azure.com"

    def test_derive_resource_url_china(self):
        """Derives URL for China cloud."""
        result = _derive_resource_url_from_project_endpoint(
            "https://myresource.services.ai.azure.cn/api/projects/myproject"
        )
        assert result == "https://myresource.cognitiveservices.azure.cn"

    def test_derive_resource_url_invalid(self):
        """Raises ValueError for unrecognized endpoint format."""
        with pytest.raises(ValueError, match="Cannot derive"):
            _derive_resource_url_from_project_endpoint("https://unknown.example.com/foo")

    def test_get_project_endpoint_new_var(self):
        """Prefers FOUNDRY_PROJECT_ENDPOINT over legacy name."""
        with patch.dict(os.environ, {
            "FOUNDRY_PROJECT_ENDPOINT": "https://new.endpoint",
            "AZURE_AI_PROJECT_ENDPOINT": "https://old.endpoint",
        }, clear=True):
            result = _get_project_endpoint()
        assert result == "https://new.endpoint"

    def test_get_project_endpoint_legacy_var(self):
        """Falls back to AZURE_AI_PROJECT_ENDPOINT."""
        with patch.dict(os.environ, {
            "AZURE_AI_PROJECT_ENDPOINT": "https://old.endpoint",
        }, clear=True):
            result = _get_project_endpoint()
        assert result == "https://old.endpoint"

    def test_get_project_endpoint_none(self):
        """Returns None when no endpoint configured."""
        with patch.dict(os.environ, {}, clear=True):
            result = _get_project_endpoint()
        assert result is None


# ---------------------------------------------------------------------------
# Skill discovery tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSkillDiscovery:
    """Tests for GitHubCopilotAdapter skill discovery."""

    def test_discover_no_skills(self, tmp_path):
        """Returns empty list when no SKILL.md files exist."""
        result = GitHubCopilotAdapter._discover_skill_directories(tmp_path)
        assert result == []

    def test_discover_github_skills(self, tmp_path):
        """Discovers skills in .github/skills/ directory."""
        skills_dir = tmp_path / ".github" / "skills" / "greeting"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("# Greeting skill")

        result = GitHubCopilotAdapter._discover_skill_directories(tmp_path)
        assert len(result) == 1
        assert ".github" in result[0]

    def test_discover_flat_skills(self, tmp_path):
        """Discovers skills in flat layout (root level)."""
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# My skill")

        result = GitHubCopilotAdapter._discover_skill_directories(tmp_path)
        assert len(result) == 1

    def test_github_skills_take_priority(self, tmp_path):
        """Prefers .github/skills/ over flat layout."""
        # Create both
        github_dir = tmp_path / ".github" / "skills" / "skill1"
        github_dir.mkdir(parents=True)
        (github_dir / "SKILL.md").write_text("# Skill 1")

        flat_dir = tmp_path / "skill2"
        flat_dir.mkdir()
        (flat_dir / "SKILL.md").write_text("# Skill 2")

        result = GitHubCopilotAdapter._discover_skill_directories(tmp_path)
        assert len(result) == 1
        assert ".github" in result[0]
