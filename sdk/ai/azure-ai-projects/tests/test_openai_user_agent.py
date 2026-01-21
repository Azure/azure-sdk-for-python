# pylint: disable=missing-class-docstring,missing-function-docstring
from typing import Any, Dict, Optional

import pytest
import httpx
from openai import OpenAI
from azure.core.credentials import TokenCredential

from azure.ai.projects import AIProjectClient


BASE_OPENAI_UA = OpenAI(api_key="dummy").user_agent


class DummyTokenCredential(TokenCredential):
    def get_token(self, *scopes: str, **kwargs: Any):  # type: ignore[override]
        return None


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    # Ensure no real network/token calls are made during the test.
    monkeypatch.setattr("azure.ai.projects._patch.get_bearer_token_provider", lambda *_, **__: "token-provider")


def _build_client(
    client_user_agent: Optional[str],
    openai_user_agent: Optional[str],
    default_headers: Optional[Dict[str, str]],
):
    project_client = AIProjectClient(
        "https://example.com/api/projects/test",
        DummyTokenCredential(),
        user_agent=client_user_agent,
    )
    kwargs: Dict[str, Any] = {"default_headers": default_headers}
    if openai_user_agent:
        kwargs["user_agent"] = openai_user_agent

    return project_client.get_openai_client(**kwargs)


@pytest.mark.parametrize(
    "client_ua,openai_ua,expected_ua",
    [
        # 1) No user_agent anywhere
        (
            None,
            None,
            f"AIProjectClient {BASE_OPENAI_UA}",
        ),
        # 2) user_agent at project client only
        (
            "custom-client-ua",
            None,
            f"AIProjectClient custom-client-ua {BASE_OPENAI_UA}",
        ),
        # 3) user_agent at openai client only
        (
            None,
            "custom-openai-ua",
            f"AIProjectClient {BASE_OPENAI_UA} custom-openai-ua",
        ),
        # 4) user_agent at both clients only
        (
            "custom-client-ua",
            "custom-openai-ua",
            f"AIProjectClient custom-client-ua {BASE_OPENAI_UA} custom-openai-ua",
        ),
    ],
)
def test_user_agent_patching_via_response_create(client_ua, openai_ua, expected_ua):
    default_headers = {"X-Default": "present"}
    client = _build_client(client_ua, openai_ua, default_headers)

    calls = []

    def fake_send(request: httpx.Request, *args: Any, **kwargs: Any):
        # Capture headers that would be sent over the wire.
        calls.append(dict(request.headers))
        return httpx.Response(
            200,
            request=request,
            json={
                "id": "resp_123",
                "object": "response",
                "model": kwargs.get("model", ""),
                "status": "ok",
                "output": "",
            },
        )

    # Monkeypatch the underlying httpx client used by the OpenAI client instance.
    client._client.send = fake_send  # type: ignore[attr-defined]

    # Act through the actual call surface
    client.responses.create(model="gpt-4o")

    # Assert
    assert calls, "Expected a responses.create call to be captured"
    headers_used = {k.lower(): v for k, v in calls[0].items()}

    assert headers_used["user-agent"] == expected_ua

    assert headers_used["x-default"] == "present"