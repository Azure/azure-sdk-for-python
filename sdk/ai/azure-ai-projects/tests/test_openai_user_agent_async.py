# pylint: disable=missing-class-docstring,missing-function-docstring
from typing import Any, Dict, Optional

import pytest
import httpx
from openai import AsyncOpenAI
from azure.core.credentials import AccessToken
from azure.core.credentials_async import AsyncTokenCredential

from azure.ai.projects.aio import AIProjectClient


BASE_OPENAI_UA = AsyncOpenAI(api_key="dummy").user_agent


class DummyAsyncTokenCredential(AsyncTokenCredential):
    async def get_token(self, *scopes: str, **kwargs: Any):  # type: ignore[override]
        return AccessToken("token", 0)


def _build_client(
    project_user_agent: Optional[str],
    default_headers: Optional[Dict[str, str]],
):
    project_client = AIProjectClient(
        "https://example.com/api/projects/test",
        DummyAsyncTokenCredential(),
        user_agent=project_user_agent,
    )
    kwargs: Dict[str, Any] = {"default_headers": default_headers}
    return project_client.get_openai_client(**kwargs)


@pytest.mark.parametrize(
    "project_ua,openai_default_header,expected_ua",
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
            {"User-Agent": "custom-openai-ua"},
            f"AIProjectClient {BASE_OPENAI_UA} custom-openai-ua",
        ),
        # 4) user_agent at both clients only
        (
            "custom-client-ua",
            {"User-Agent": "custom-openai-ua"},
            f"AIProjectClient custom-client-ua {BASE_OPENAI_UA} custom-openai-ua",
        ),
    ],
)
@pytest.mark.asyncio
async def test_user_agent_patching_via_response_create(project_ua, openai_default_header, expected_ua):
    client = _build_client(project_ua, openai_default_header)

    calls = []

    async def fake_send(request: httpx.Request, *args: Any, **kwargs: Any):
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
    await client.responses.create(model="gpt-4o")

    # Assert
    assert calls, "Expected a responses.create call to be captured"
    headers_used = {k.lower(): v for k, v in calls[0].items()}

    assert headers_used["user-agent"] == expected_ua
