# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests covering caller-side overrides (http_client, api_key, base_url, default_headers)
and the user-agent / token-provider / logging-transport branches of
AIProjectClient.get_openai_client() (sync).
"""

import os
from typing import Any
from unittest.mock import patch

import pytest
import httpx
from azure.core.credentials import TokenCredential
from azure.ai.projects import AIProjectClient

from openai_test_helpers import (
    SYNC_OPENAI_PATCH,
    SYNC_TOKEN_PROVIDER_PATCH,
    make_sync_client,
    mock_openai,
)


class DummyTokenCredential(TokenCredential):
    """A dummy credential that returns None for testing purposes."""

    def get_token(self, *scopes: str, **kwargs: Any):  # type: ignore[override]
        return None


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    """Ensure no real network/token calls are made during the test."""
    monkeypatch.setattr("azure.ai.projects._patch.get_bearer_token_provider", lambda *_, **__: "token-provider")


class TestGetOpenAIClientWithOverrides:
    """Tests for custom http_client override in get_openai_client()."""

    @pytest.mark.skipif(
        os.environ.get("AZURE_AI_PROJECTS_CONSOLE_LOGGING", "false").lower() == "true",
        reason="Test skipped because AZURE_AI_PROJECTS_CONSOLE_LOGGING is set to 'true'",
    )
    def test_http_client_override(self):
        """
        Test that a custom http_client passed to get_openai_client() is actually used
        by the returned OpenAI client when making API calls.
        """
        # Track whether our custom http_client was invoked
        request_intercepted = {"called": False, "request": None}

        class TrackingTransport(httpx.BaseTransport):
            """Custom transport that tracks requests and returns mock responses."""

            def handle_request(self, request: httpx.Request) -> httpx.Response:
                # Mark that our custom transport was called
                request_intercepted["called"] = True
                request_intercepted["request"] = request

                # Return a mock response for the OpenAI responses.create() call
                return httpx.Response(
                    200,
                    request=request,
                    json={
                        "id": "resp_test_123",
                        "output": [
                            {
                                "type": "message",
                                "id": "msg_test_123",
                                "role": "assistant",
                                "content": [
                                    {
                                        "type": "output_text",
                                        "text": "This is a test response from the mock.",
                                    }
                                ],
                            }
                        ],
                    },
                )

        # Create a custom http_client with our tracking transport
        custom_http_client = httpx.Client(transport=TrackingTransport())

        # Create the AIProjectClient
        project_client = AIProjectClient(
            endpoint="https://example.com/api/projects/test",
            credential=DummyTokenCredential(),
        )

        # Get an OpenAI client with our custom http_client
        openai_client = project_client.get_openai_client(http_client=custom_http_client)

        # Make an API call
        response = openai_client.responses.create(
            model="gpt-4o",
            input="Test input",
        )

        # Verify the custom http_client was used
        assert request_intercepted["called"], "Custom http_client was not used for the request"
        assert request_intercepted["request"] is not None, "Request was not captured"

        # Verify the request was made to the expected endpoint
        assert "/openai/v1/responses" in str(request_intercepted["request"].url)

        # Verify we got a valid response
        assert response.id == "resp_test_123"
        assert response.output_text == "This is a test response from the mock."

    # To run this test: pytest tests/responses/test_responses_with_http_client_override.py::TestResponsesWithHttpClientOverride::test_api_key_and_base_url_overrides -s
    def test_api_key_and_base_url_overrides(self):
        """
        Test that api_key and base_url passed to get_openai_client() are used
        by the returned OpenAI client instead of the default values.
        """
        # Create the AIProjectClient
        with AIProjectClient(
            endpoint="https://example.com/api/projects/test",
            credential=DummyTokenCredential(),
        ) as project_client:

            # Define custom values
            custom_api_key = "my-custom-api-key"
            custom_base_url = "https://my.custom.endpoint.com/path1/path2"

            # Get an OpenAI client with custom api_key and base_url
            with project_client.get_openai_client(
                api_key=custom_api_key,
                base_url=custom_base_url,
            ) as openai_client:

                # Verify the custom api_key was used
                assert (
                    openai_client.api_key == custom_api_key
                ), f"Expected api_key '{custom_api_key}', got '{openai_client.api_key}'"

                # Verify the custom base_url was used
                assert (
                    str(openai_client.base_url) == custom_base_url + "/"
                ), f"Expected base_url '{custom_base_url}/', got '{openai_client.base_url}'"


# ===========================================================================
# api_key resolution branches
# ===========================================================================


class TestApiKeyBranches:
    def test_token_provider_used_when_no_api_key(self):
        """Branch: no 'api_key' kwarg -> get_bearer_token_provider() is invoked."""
        client = make_sync_client()
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="provider") as mock_tp:
            client.get_openai_client()
        mock_tp.assert_called_once_with(client._config.credential, "https://ai.azure.com/.default")
        for c in mock_cls.call_args_list:
            assert c.kwargs["api_key"] == "provider"

    def test_caller_api_key_skips_token_provider(self):
        """Branch: 'api_key' in kwargs -> token provider is NOT called."""
        client = make_sync_client()
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH) as mock_tp:
            client.get_openai_client(api_key="my-secret-key")
        mock_tp.assert_not_called()
        for c in mock_cls.call_args_list:
            assert c.kwargs["api_key"] == "my-secret-key"


# ===========================================================================
# http_client resolution branches
# ===========================================================================


class TestHttpClientBranches:
    def test_http_client_is_none_by_default(self):
        """Branch: no override + console logging off -> http_client is None."""
        client = make_sync_client(console_logging=False)
        mock_cls, _ = mock_openai()
        with patch(SYNC_OPENAI_PATCH, mock_cls), patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client()
        for c in mock_cls.call_args_list:
            assert c.kwargs["http_client"] is None

    def test_console_logging_creates_logging_transport(self):
        """Branch: no override + _console_logging_enabled=True -> httpx.Client with logging transport."""
        client = make_sync_client(console_logging=True)
        mock_cls, _ = mock_openai()
        with (
            patch(SYNC_OPENAI_PATCH, mock_cls),
            patch(SYNC_TOKEN_PROVIDER_PATCH, return_value="tok"),
            patch("azure.ai.projects._patch.httpx") as mock_httpx,
            patch("azure.ai.projects._patch._OpenAILoggingTransport"),
        ):
            mock_httpx.Client.return_value = object()
            client.get_openai_client()
        mock_httpx.Client.assert_called_once()
