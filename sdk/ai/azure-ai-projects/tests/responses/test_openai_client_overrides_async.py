# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests covering caller-side overrides (http_client, api_key, base_url, default_headers)
and the user-agent / token-provider / logging-transport branches of
AIProjectClient.get_openai_client() (async).
"""

import os
from typing import Any
from unittest.mock import patch

import pytest
import httpx
from azure.core.credentials_async import AsyncTokenCredential
from azure.ai.projects.aio import AIProjectClient

from openai_test_helpers import (
    ASYNC_OPENAI_PATCH,
    ASYNC_TOKEN_PROVIDER_PATCH,
    make_async_client,
    mock_openai,
)


class DummyAsyncTokenCredential(AsyncTokenCredential):
    """A dummy async credential that returns None for testing purposes."""

    async def get_token(self, *scopes: str, **kwargs: Any):  # type: ignore[override]
        return None

    async def close(self) -> None:
        pass


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    """Ensure no real network/token calls are made during the test."""
    monkeypatch.setattr("azure.ai.projects.aio._patch.get_bearer_token_provider", lambda *_, **__: "token-provider")


class TestGetOpenAIClientWithOverridesAsync:
    """Tests for custom http_client override in async get_openai_client()."""

    @pytest.mark.skipif(
        os.environ.get("AZURE_AI_PROJECTS_CONSOLE_LOGGING", "false").lower() == "true",
        reason="Test skipped because AZURE_AI_PROJECTS_CONSOLE_LOGGING is set to 'true'",
    )
    @pytest.mark.asyncio
    async def test_http_client_override_async(self):
        """
        Test that a custom http_client passed to get_openai_client() is actually used
        by the returned AsyncOpenAI client when making API calls.
        """
        # Track whether our custom http_client was invoked
        request_intercepted = {"called": False, "request": None}

        class TrackingTransport(httpx.AsyncBaseTransport):
            """Custom async transport that tracks requests and returns mock responses."""

            async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
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
        custom_http_client = httpx.AsyncClient(transport=TrackingTransport())

        # Create the AIProjectClient
        project_client = AIProjectClient(
            endpoint="https://example.com/api/projects/test",
            credential=DummyAsyncTokenCredential(),
        )

        # Get an AsyncOpenAI client with our custom http_client
        openai_client = project_client.get_openai_client(http_client=custom_http_client)

        # Make an API call
        response = await openai_client.responses.create(
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

    @pytest.mark.asyncio
    async def test_api_key_and_base_url_overrides_async(self):
        """
        Test that api_key and base_url passed to get_openai_client() are used
        by the returned AsyncOpenAI client instead of the default values.
        """
        # Define custom values
        custom_api_key = "my-custom-api-key"
        custom_base_url = "https://my.custom.endpoint.com/path1/path2"

        # Create the AIProjectClient using async with pattern
        async with AIProjectClient(
            endpoint="https://example.com/api/projects/test",
            credential=DummyAsyncTokenCredential(),
        ) as project_client:

            # Get an AsyncOpenAI client with custom api_key and base_url
            async with project_client.get_openai_client(
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
# api_key resolution branches (async)
# ===========================================================================


class TestApiKeyBranchesAsync:
    @pytest.mark.asyncio
    async def test_token_provider_used_when_no_api_key(self):
        """Branch: no 'api_key' kwarg -> get_bearer_token_provider() is invoked."""
        client = make_async_client()
        mock_cls, _ = mock_openai()
        with (
            patch(ASYNC_OPENAI_PATCH, mock_cls),
            patch(ASYNC_TOKEN_PROVIDER_PATCH, return_value="async-provider") as mock_tp,
        ):
            client.get_openai_client()
        mock_tp.assert_called_once_with(client._config.credential, "https://ai.azure.com/.default")
        for c in mock_cls.call_args_list:
            assert c.kwargs["api_key"] == "async-provider"

    @pytest.mark.asyncio
    async def test_caller_api_key_skips_token_provider(self):
        """Branch: 'api_key' in kwargs -> token provider is NOT called."""
        client = make_async_client()
        mock_cls, _ = mock_openai()
        with patch(ASYNC_OPENAI_PATCH, mock_cls), patch(ASYNC_TOKEN_PROVIDER_PATCH) as mock_tp:
            client.get_openai_client(api_key="async-secret")
        mock_tp.assert_not_called()
        for c in mock_cls.call_args_list:
            assert c.kwargs["api_key"] == "async-secret"


# ===========================================================================
# http_client resolution branches (async)
# ===========================================================================


class TestHttpClientBranchesAsync:
    @pytest.mark.asyncio
    async def test_http_client_is_none_by_default(self):
        """Branch: no override + console logging off -> http_client is None."""
        client = make_async_client(console_logging=False)
        mock_cls, _ = mock_openai()
        with patch(ASYNC_OPENAI_PATCH, mock_cls), patch(ASYNC_TOKEN_PROVIDER_PATCH, return_value="tok"):
            client.get_openai_client()
        for c in mock_cls.call_args_list:
            assert c.kwargs["http_client"] is None

    @pytest.mark.asyncio
    async def test_console_logging_creates_async_logging_transport(self):
        """Branch: no override + _console_logging_enabled=True -> httpx.AsyncClient with logging transport."""
        client = make_async_client(console_logging=True)
        mock_cls, _ = mock_openai()
        with (
            patch(ASYNC_OPENAI_PATCH, mock_cls),
            patch(ASYNC_TOKEN_PROVIDER_PATCH, return_value="tok"),
            patch("azure.ai.projects.aio._patch.httpx") as mock_httpx,
            patch("azure.ai.projects.aio._patch._OpenAILoggingTransport"),
        ):
            mock_httpx.AsyncClient.return_value = object()
            client.get_openai_client()
        mock_httpx.AsyncClient.assert_called_once()
