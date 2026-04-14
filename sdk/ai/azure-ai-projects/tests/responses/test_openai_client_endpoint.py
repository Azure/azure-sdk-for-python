# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Unit tests for verifying the base_url of the OpenAI client returned by AIProjectClient.get_openai_client().
No network calls are made.
"""

import pytest
from azure.core.credentials import AccessToken
from azure.ai.projects import AIProjectClient

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
