# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests to verify that a custom http_client can be passed to get_openai_client()
and that the returned OpenAI client uses it instead of the default one.
"""

import os
import pytest
import httpx
from typing import Any
from azure.core.credentials import TokenCredential
from azure.ai.projects import AIProjectClient


class DummyTokenCredential(TokenCredential):
    """A dummy credential that returns None for testing purposes."""

    def get_token(self, *scopes: str, **kwargs: Any):  # type: ignore[override]
        return None


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    """Ensure no real network/token calls are made during the test."""
    monkeypatch.setattr("azure.ai.projects._patch.get_bearer_token_provider", lambda *_, **__: "token-provider")


@pytest.mark.skipif(
    os.environ.get("AZURE_AI_PROJECTS_CONSOLE_LOGGING", "false").lower() == "true",
    reason="Test skipped because AZURE_AI_PROJECTS_CONSOLE_LOGGING is set to 'true'",
)
class TestResponsesWithHttpClientOverride:
    """Tests for custom http_client override in get_openai_client()."""

    def test_custom_http_client_is_used(self):
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
