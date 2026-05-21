# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Unit tests for verifying the base_url, default_query (api-version) and Foundry feature
header behavior of the OpenAI client returned by AIProjectClient.get_openai_client().
No network calls are made.
"""

from unittest.mock import patch

import pytest
from azure.core.credentials import AccessToken
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models._patch import _FOUNDRY_FEATURES_HEADER_NAME

from openai_test_helpers import (
    ENDPOINT,
    API_VERSION,
    SYNC_OPENAI_PATCH,
    SYNC_TOKEN_PROVIDER_PATCH,
    make_sync_client,
    mock_openai,
)

FAKE_ENDPOINT = "https://fake-account.services.ai.azure.com/api/projects/fake-project"
AGENT_NAME = "fake-agent-name"


class FakeCredential:
    """Sync stub credential that returns a never-expiring token."""

    def get_token(self, *args, **kwargs) -> AccessToken:
        return AccessToken("fake-token", 9_999_999_999)


class TestGetOpenaiClient:

    def test_get_openai_client_default_endpoint(self):
        """Verify that the OpenAI client base_url is set to {endpoint}/openai/v1."""
        project_client = AIProjectClient(
            endpoint=FAKE_ENDPOINT,
            credential=FakeCredential(),  # type: ignore[arg-type]
        )
        openai_client = project_client.get_openai_client()

        expected_base_url = FAKE_ENDPOINT.rstrip("/") + "/openai/v1"
        assert str(openai_client.base_url).rstrip("/") == expected_base_url

    def test_get_openai_client_with_agent_name_raises_without_allow_preview(self):
        """Verify that passing agent_name without allow_preview=True raises ValueError."""
        project_client = AIProjectClient(
            endpoint=FAKE_ENDPOINT,
            credential=FakeCredential(),  # type: ignore[arg-type]
        )

        with pytest.raises(ValueError) as exc_info:
            project_client.get_openai_client(agent_name=AGENT_NAME)

        assert "allow_preview=True" in str(exc_info.value)

    def test_get_openai_client_with_agent_name_and_allow_preview(self):
        """Verify that the OpenAI client base_url includes the agent endpoint when allow_preview=True."""
        project_client = AIProjectClient(
            endpoint=FAKE_ENDPOINT,
            credential=FakeCredential(),  # type: ignore[arg-type]
            allow_preview=True,
        )
        openai_client = project_client.get_openai_client(agent_name=AGENT_NAME)

        expected_base_url = FAKE_ENDPOINT.rstrip("/") + f"/agents/{AGENT_NAME}/endpoint/protocols/openai"
        assert str(openai_client.base_url).rstrip("/") == expected_base_url

    def test_trailing_slash_on_endpoint_is_stripped(self):
        """Trailing slash on endpoint must not produce a double slash in the base URL."""
        client = make_sync_client()
        client._config.endpoint = ENDPOINT + "/"
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client()
        for c in mock_cls.call_args_list:
            host = c.kwargs["base_url"].replace("https://", "")
            assert "//" not in host


# ===========================================================================
# default_query / api-version injection branches
# ===========================================================================


class TestDefaultQueryBranches:
    def test_no_agent_no_api_version_injected(self):
        """Branch: no agent_name -> api-version is NOT injected into default_query."""
        client = make_sync_client()
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client()
        for c in mock_cls.call_args_list:
            assert "api-version" not in c.kwargs.get("default_query", {})

    def test_agent_injects_api_version(self):
        """Branch: agent_name + no caller api-version -> inject SDK api_version."""
        client = make_sync_client()
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client(agent_name="my-agent")
        for c in mock_cls.call_args_list:
            assert c.kwargs["default_query"]["api-version"] == API_VERSION

    def test_agent_does_not_override_caller_api_version(self):
        """Branch: agent_name + caller-provided api-version -> keep caller value."""
        client = make_sync_client()
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client(agent_name="my-agent", default_query={"api-version": "caller-v"})
        for c in mock_cls.call_args_list:
            assert c.kwargs["default_query"]["api-version"] == "caller-v"

    def test_caller_default_query_values_preserved(self):
        """Caller-supplied default_query keys other than api-version are preserved."""
        client = make_sync_client()
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client(default_query={"foo": "bar"})
        for c in mock_cls.call_args_list:
            assert c.kwargs["default_query"]["foo"] == "bar"


# ===========================================================================
# Foundry feature header injection branches
# ===========================================================================


class TestFoundryFeatureHeaderBranches:
    def test_no_agent_no_feature_header_injected(self):
        """Branch: no agent_name -> Foundry feature header is NOT injected."""

        client = make_sync_client()
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client()
        real_call = mock_cls.call_args_list[-1]
        assert _FOUNDRY_FEATURES_HEADER_NAME not in real_call.kwargs.get("default_headers", {})

    def test_agent_injects_foundry_feature_header(self):
        """Branch: agent_name + header not present -> inject the Foundry feature header."""

        client = make_sync_client()
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client(agent_name="my-agent")
        real_call = mock_cls.call_args_list[-1]
        assert _FOUNDRY_FEATURES_HEADER_NAME in real_call.kwargs.get("default_headers", {})

    def test_agent_does_not_override_existing_feature_header(self):
        """Branch: agent_name + header already in caller headers -> keep caller value."""

        client = make_sync_client()
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client(
                agent_name="my-agent",
                default_headers={_FOUNDRY_FEATURES_HEADER_NAME: "caller-value"},
            )
        real_call = mock_cls.call_args_list[-1]
        assert real_call.kwargs["default_headers"][_FOUNDRY_FEATURES_HEADER_NAME] == "caller-value"

    def test_caller_headers_other_keys_preserved(self):
        """Caller-supplied non-feature headers are passed through to the OpenAI client."""
        client = make_sync_client()
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client(default_headers={"X-My-Header": "hello"})
        real_call = mock_cls.call_args_list[-1]
        assert real_call.kwargs["default_headers"]["X-My-Header"] == "hello"
