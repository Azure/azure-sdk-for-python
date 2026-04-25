# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Unit tests covering every branch of AIProjectClient.get_openai_client (sync and async)."""

from unittest.mock import MagicMock, patch
import pytest

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

# ---------------------------------------------------------------------------
# Helpers to build lightweight client stubs without real HTTP connections
# ---------------------------------------------------------------------------

ENDPOINT = "https://myaccount.services.ai.azure.com/api/projects/myproject"
API_VERSION = "2025-01-01"


def _make_sync_client(allow_preview: bool = True, console_logging: bool = False, custom_user_agent: str = None):
    """Return a minimal AIProjectClient stub suitable for unit-testing get_openai_client."""
    client = AIProjectClient.__new__(AIProjectClient)
    client._config = MagicMock()
    client._config.endpoint = ENDPOINT
    client._config.allow_preview = allow_preview
    client._config.api_version = API_VERSION
    client._config.credential = MagicMock()
    client._console_logging_enabled = console_logging
    client._custom_user_agent = custom_user_agent
    return client


def _make_async_client(allow_preview: bool = True, console_logging: bool = False, custom_user_agent: str = None):
    """Return a minimal async AIProjectClient stub suitable for unit-testing get_openai_client."""
    client = AsyncAIProjectClient.__new__(AsyncAIProjectClient)
    client._config = MagicMock()
    client._config.endpoint = ENDPOINT
    client._config.allow_preview = allow_preview
    client._config.api_version = API_VERSION
    client._config.credential = MagicMock()
    client._console_logging_enabled = console_logging
    client._custom_user_agent = custom_user_agent
    return client


def _mock_openai(user_agent: str = "openai/1.0"):
    """Return (mock_class, mock_instance) where mock_class acts as OpenAI constructor."""
    instance = MagicMock()
    instance.user_agent = user_agent
    mock_cls = MagicMock(return_value=instance)
    return mock_cls, instance


_SYNC_PATCH = "azure.ai.projects._patch.OpenAI"
_ASYNC_PATCH = "azure.ai.projects.aio._patch.AsyncOpenAI"
_SYNC_TP = "azure.ai.projects._patch.get_bearer_token_provider"
_ASYNC_TP = "azure.ai.projects.aio._patch.get_bearer_token_provider"


# ===========================================================================
# BRANCH GROUP 1 — base_url resolution (4 branches)
# ===========================================================================


class TestBaseUrlBranches:
    def test_caller_override_base_url(self):
        """Branch: 'base_url' in kwargs → use caller value."""
        client = _make_sync_client()
        mock_cls, instance = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            result = client.get_openai_client(base_url="https://custom/")
        assert result is instance
        for c in mock_cls.call_args_list:
            assert c.kwargs["base_url"] == "https://custom/"

    def test_agent_name_with_preview_builds_agent_url(self):
        """Branch: agent_name + allow_preview=True → agent endpoint URL."""
        client = _make_sync_client(allow_preview=True)
        mock_cls, instance = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            result = client.get_openai_client(agent_name="my-agent")
        assert result is instance
        expected = f"{ENDPOINT}/agents/my-agent/endpoint/protocols/openai"
        for c in mock_cls.call_args_list:
            assert c.kwargs["base_url"] == expected

    def test_agent_name_without_preview_raises(self):
        """Branch: agent_name + allow_preview=False → ValueError."""
        client = _make_sync_client(allow_preview=False)
        with pytest.raises(ValueError, match="allow_preview=True"):
            client.get_openai_client(agent_name="my-agent")

    def test_no_agent_builds_default_openai_url(self):
        """Branch: no agent_name, no override → /openai/v1 suffix."""
        client = _make_sync_client()
        mock_cls, instance = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            result = client.get_openai_client()
        assert result is instance
        for c in mock_cls.call_args_list:
            assert c.kwargs["base_url"] == f"{ENDPOINT}/openai/v1"

    def test_trailing_slash_on_endpoint_is_stripped(self):
        """Trailing slash on endpoint must not produce double slash."""
        client = _make_sync_client()
        client._config.endpoint = ENDPOINT + "/"
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client()
        for c in mock_cls.call_args_list:
            host = c.kwargs["base_url"].replace("https://", "")
            assert "//" not in host


# ===========================================================================
# BRANCH GROUP 2 — default_query / api-version injection (3 branches)
# ===========================================================================


class TestDefaultQueryBranches:
    def test_no_agent_no_api_version_injected(self):
        """Branch: no agent_name → api-version NOT injected."""
        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client()
        for c in mock_cls.call_args_list:
            assert "api-version" not in c.kwargs.get("default_query", {})

    def test_agent_injects_api_version(self):
        """Branch: agent_name + no caller api-version → inject SDK api_version."""
        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client(agent_name="my-agent")
        for c in mock_cls.call_args_list:
            assert c.kwargs["default_query"]["api-version"] == API_VERSION

    def test_agent_does_not_override_caller_api_version(self):
        """Branch: agent_name + caller provided api-version → keep caller value."""
        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client(agent_name="my-agent", default_query={"api-version": "caller-v"})
        for c in mock_cls.call_args_list:
            assert c.kwargs["default_query"]["api-version"] == "caller-v"

    def test_caller_default_query_values_preserved(self):
        """Caller-supplied default_query keys other than api-version are preserved."""
        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client(default_query={"foo": "bar"})
        for c in mock_cls.call_args_list:
            assert c.kwargs["default_query"]["foo"] == "bar"


# ===========================================================================
# BRANCH GROUP 3 — api_key resolution (2 branches)
# ===========================================================================


class TestApiKeyBranches:
    def test_caller_api_key_override(self):
        """Branch: 'api_key' in kwargs → use caller value, no token provider call."""
        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP) as mock_tp:
            client.get_openai_client(api_key="my-secret-key")
        mock_tp.assert_not_called()
        for c in mock_cls.call_args_list:
            assert c.kwargs["api_key"] == "my-secret-key"

    def test_token_provider_used_when_no_api_key(self):
        """Branch: no 'api_key' kwarg → call get_bearer_token_provider."""
        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="provider") as mock_tp:
            client.get_openai_client()
        mock_tp.assert_called_once_with(client._config.credential, "https://ai.azure.com/.default")
        for c in mock_cls.call_args_list:
            assert c.kwargs["api_key"] == "provider"


# ===========================================================================
# BRANCH GROUP 4 — http_client resolution (3 branches)
# ===========================================================================


class TestHttpClientBranches:
    def test_caller_http_client_override(self):
        """Branch: 'http_client' in kwargs → use it."""
        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        fake_http = MagicMock()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client(http_client=fake_http)
        for c in mock_cls.call_args_list:
            assert c.kwargs["http_client"] is fake_http

    def test_console_logging_creates_logging_transport(self):
        """Branch: no override + _console_logging_enabled=True → httpx.Client with transport."""
        client = _make_sync_client(console_logging=True)
        mock_cls, _ = _mock_openai()
        with (
            patch(_SYNC_PATCH, mock_cls),
            patch(_SYNC_TP, return_value="tok"),
            patch("azure.ai.projects._patch.httpx") as mock_httpx,
            patch("azure.ai.projects._patch._OpenAILoggingTransport"),
        ):
            mock_httpx.Client.return_value = MagicMock()
            client.get_openai_client()
        mock_httpx.Client.assert_called_once()

    def test_http_client_is_none_by_default(self):
        """Branch: no override + console logging off → http_client=None."""
        client = _make_sync_client(console_logging=False)
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client()
        for c in mock_cls.call_args_list:
            assert c.kwargs["http_client"] is None


# ===========================================================================
# BRANCH GROUP 5 — Foundry feature header (3 branches)
# ===========================================================================


class TestFoundryFeatureHeaderBranches:
    def test_no_agent_no_feature_header_injected(self):
        """Branch: no agent_name → Foundry feature header NOT injected."""
        from azure.ai.projects._patch import _FOUNDRY_FEATURES_HEADER_NAME

        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client()
        real_call = mock_cls.call_args_list[-1]
        assert _FOUNDRY_FEATURES_HEADER_NAME not in real_call.kwargs.get("default_headers", {})

    def test_agent_injects_foundry_feature_header(self):
        """Branch: agent_name + header not present → inject it."""
        from azure.ai.projects._patch import _FOUNDRY_FEATURES_HEADER_NAME

        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client(agent_name="my-agent")
        real_call = mock_cls.call_args_list[-1]
        assert _FOUNDRY_FEATURES_HEADER_NAME in real_call.kwargs.get("default_headers", {})

    def test_agent_does_not_override_existing_feature_header(self):
        """Branch: agent_name + header already in caller headers → keep caller value."""
        from azure.ai.projects._patch import _FOUNDRY_FEATURES_HEADER_NAME

        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client(
                agent_name="my-agent",
                default_headers={_FOUNDRY_FEATURES_HEADER_NAME: "caller-value"},
            )
        real_call = mock_cls.call_args_list[-1]
        assert real_call.kwargs["default_headers"][_FOUNDRY_FEATURES_HEADER_NAME] == "caller-value"

    def test_caller_headers_other_keys_preserved(self):
        """Caller-supplied non-feature headers are passed through."""
        client = _make_sync_client()
        mock_cls, _ = _mock_openai()
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client(default_headers={"X-My-Header": "hello"})
        real_call = mock_cls.call_args_list[-1]
        assert real_call.kwargs["default_headers"]["X-My-Header"] == "hello"


# ===========================================================================
# BRANCH GROUP 6 — User-Agent construction (2 branches)
# ===========================================================================


class TestUserAgentBranches:
    def test_caller_user_agent_used_verbatim(self):
        """Branch: 'User-Agent' in default_headers → use as-is."""
        client = _make_sync_client()
        mock_cls, _ = _mock_openai("openai/sdk-ua")
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client(default_headers={"User-Agent": "MyApp/1.0"})
        real_call = mock_cls.call_args_list[-1]
        assert real_call.kwargs["default_headers"]["User-Agent"] == "MyApp/1.0"

    def test_sdk_user_agent_without_custom_prefix(self):
        """Branch: no caller UA, no _custom_user_agent → 'AIProjectClient <openai_ua>'."""
        client = _make_sync_client(custom_user_agent=None)
        openai_ua = "openai/1.2.3"
        mock_cls, _ = _mock_openai(openai_ua)
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client()
        real_call = mock_cls.call_args_list[-1]
        ua = real_call.kwargs["default_headers"]["User-Agent"]
        assert "AIProjectClient" in ua
        assert openai_ua in ua

    def test_sdk_user_agent_with_custom_prefix(self):
        """Branch: no caller UA, _custom_user_agent set → 'custom-AIProjectClient <openai_ua>'."""
        client = _make_sync_client(custom_user_agent="MySDK")
        openai_ua = "openai/1.2.3"
        mock_cls, _ = _mock_openai(openai_ua)
        with patch(_SYNC_PATCH, mock_cls), patch(_SYNC_TP, return_value="tok"):
            client.get_openai_client()
        real_call = mock_cls.call_args_list[-1]
        ua = real_call.kwargs["default_headers"]["User-Agent"]
        assert ua.startswith("MySDK-AIProjectClient")
        assert openai_ua in ua


# ===========================================================================
# ASYNC CLIENT — mirror of all branches via AsyncOpenAI
# ===========================================================================


class TestAsyncClientBranches:
    def test_caller_override_base_url(self):
        client = _make_async_client()
        mock_cls, instance = _mock_openai()
        with patch(_ASYNC_PATCH, mock_cls), patch(_ASYNC_TP, return_value="tok"):
            result = client.get_openai_client(base_url="https://custom/")
        assert result is instance
        for c in mock_cls.call_args_list:
            assert c.kwargs["base_url"] == "https://custom/"

    def test_agent_with_preview(self):
        client = _make_async_client(allow_preview=True)
        mock_cls, instance = _mock_openai()
        with patch(_ASYNC_PATCH, mock_cls), patch(_ASYNC_TP, return_value="tok"):
            result = client.get_openai_client(agent_name="my-agent")
        assert result is instance
        for c in mock_cls.call_args_list:
            assert "/agents/my-agent/endpoint/protocols/openai" in c.kwargs["base_url"]

    def test_agent_without_preview_raises(self):
        client = _make_async_client(allow_preview=False)
        with pytest.raises(ValueError, match="allow_preview=True"):
            client.get_openai_client(agent_name="my-agent")

    def test_default_url(self):
        client = _make_async_client()
        mock_cls, _ = _mock_openai()
        with patch(_ASYNC_PATCH, mock_cls), patch(_ASYNC_TP, return_value="tok"):
            client.get_openai_client()
        for c in mock_cls.call_args_list:
            assert c.kwargs["base_url"].endswith("/openai/v1")

    def test_api_key_override(self):
        client = _make_async_client()
        mock_cls, _ = _mock_openai()
        with patch(_ASYNC_PATCH, mock_cls), patch(_ASYNC_TP) as mock_tp:
            client.get_openai_client(api_key="async-secret")
        mock_tp.assert_not_called()
        for c in mock_cls.call_args_list:
            assert c.kwargs["api_key"] == "async-secret"

    def test_token_provider_when_no_api_key(self):
        client = _make_async_client()
        mock_cls, _ = _mock_openai()
        with patch(_ASYNC_PATCH, mock_cls), patch(_ASYNC_TP, return_value="async-provider") as mock_tp:
            client.get_openai_client()
        mock_tp.assert_called_once_with(client._config.credential, "https://ai.azure.com/.default")

    def test_http_client_none_by_default(self):
        client = _make_async_client(console_logging=False)
        mock_cls, _ = _mock_openai()
        with patch(_ASYNC_PATCH, mock_cls), patch(_ASYNC_TP, return_value="tok"):
            client.get_openai_client()
        for c in mock_cls.call_args_list:
            assert c.kwargs["http_client"] is None

    def test_console_logging_creates_async_transport(self):
        client = _make_async_client(console_logging=True)
        mock_cls, _ = _mock_openai()
        with (
            patch(_ASYNC_PATCH, mock_cls),
            patch(_ASYNC_TP, return_value="tok"),
            patch("azure.ai.projects.aio._patch.httpx") as mock_httpx,
            patch("azure.ai.projects.aio._patch._OpenAILoggingTransport"),
        ):
            mock_httpx.AsyncClient.return_value = MagicMock()
            client.get_openai_client()
        mock_httpx.AsyncClient.assert_called_once()

    def test_agent_injects_foundry_header(self):
        from azure.ai.projects.aio._patch import _FOUNDRY_FEATURES_HEADER_NAME

        client = _make_async_client()
        mock_cls, _ = _mock_openai()
        with patch(_ASYNC_PATCH, mock_cls), patch(_ASYNC_TP, return_value="tok"):
            client.get_openai_client(agent_name="my-agent")
        real_call = mock_cls.call_args_list[-1]
        assert _FOUNDRY_FEATURES_HEADER_NAME in real_call.kwargs.get("default_headers", {})

    def test_agent_injects_api_version(self):
        client = _make_async_client()
        mock_cls, _ = _mock_openai()
        with patch(_ASYNC_PATCH, mock_cls), patch(_ASYNC_TP, return_value="tok"):
            client.get_openai_client(agent_name="my-agent")
        for c in mock_cls.call_args_list:
            assert c.kwargs["default_query"]["api-version"] == API_VERSION

    def test_caller_user_agent_verbatim(self):
        client = _make_async_client()
        mock_cls, _ = _mock_openai("openai/x")
        with patch(_ASYNC_PATCH, mock_cls), patch(_ASYNC_TP, return_value="tok"):
            client.get_openai_client(default_headers={"User-Agent": "AsyncApp/2.0"})
        real_call = mock_cls.call_args_list[-1]
        assert real_call.kwargs["default_headers"]["User-Agent"] == "AsyncApp/2.0"

    def test_sdk_user_agent_built_without_custom_prefix(self):
        client = _make_async_client(custom_user_agent=None)
        mock_cls, _ = _mock_openai("openai/async-sdk")
        with patch(_ASYNC_PATCH, mock_cls), patch(_ASYNC_TP, return_value="tok"):
            client.get_openai_client()
        real_call = mock_cls.call_args_list[-1]
        ua = real_call.kwargs["default_headers"]["User-Agent"]
        assert "AIProjectClient" in ua
        assert "openai/async-sdk" in ua
