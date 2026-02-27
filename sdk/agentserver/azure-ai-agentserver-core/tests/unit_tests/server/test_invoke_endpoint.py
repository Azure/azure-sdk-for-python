# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for the ``/invoke`` POST endpoint on :class:`FoundryCBAgent`."""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from starlette.responses import JSONResponse

from azure.ai.agentserver.core.server.common.agent_invoke_context import AgentInvokeContext


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_agent(invoke_side_effect=None):
    """Return a concrete :class:`FoundryCBAgent` with Azure dependencies patched out.

    :param invoke_side_effect: If set, a callable ``async (context) -> Response`` that will
        be used as the ``agent_invoke`` implementation. If ``None``, the default
        (``NotImplementedError``) implementation is kept.
    :type invoke_side_effect: callable or None
    :return: A :class:`FoundryCBAgent` subclass instance whose ``.app`` is ready for testing.
    """
    from azure.ai.agentserver.core.server.base import FoundryCBAgent

    class _TestAgent(FoundryCBAgent):
        async def agent_run(self, context):  # pragma: no cover
            raise NotImplementedError("agent_run is not exercised in these tests")

        async def agent_invoke(self, context: AgentInvokeContext):
            if invoke_side_effect is not None:
                return await invoke_side_effect(context)
            return await super().agent_invoke(context)

    with (
        patch("azure.ai.agentserver.core.server.base.AgentServerContext"),
        patch("azure.ai.agentserver.core.server.base.create_tool_runtime"),
        patch("azure.ai.agentserver.core.tools.UserInfoContextMiddleware.install"),
    ):
        return _TestAgent(credentials=MagicMock(), project_endpoint="http://fake-endpoint")


def _client(agent) -> httpx.AsyncClient:
    """Create an ``httpx.AsyncClient`` wired to the agent's ASGI app."""
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent.app),
        base_url="http://test",
    )


def _json_post_kwargs(payload: dict) -> dict:
    """Build kwargs for posting a JSON body."""
    return {
        "content": json.dumps(payload).encode(),
        "headers": {"content-type": "application/json"},
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
async def test_invoke_endpoint_returns_agent_invoke_result():
    """POST /invoke — happy path: the response returned by ``agent_invoke`` is forwarded."""
    expected = {"answer": "42", "status": "ok"}

    async def _invoke(context: AgentInvokeContext):
        assert isinstance(context, AgentInvokeContext)
        assert context.payload == {"question": "hello"}
        return JSONResponse(expected)

    agent = _build_agent(invoke_side_effect=_invoke)
    async with _client(agent) as client:
        response = await client.post("/invoke", **_json_post_kwargs({"question": "hello"}))

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invoke_endpoint_exposes_request_headers():
    """POST /invoke — ``AgentInvokeContext.headers`` contains the forwarded request headers."""
    received_headers: dict = {}

    async def _invoke(context: AgentInvokeContext):
        received_headers.update(context.headers)
        return JSONResponse({"ok": True})

    agent = _build_agent(invoke_side_effect=_invoke)
    async with _client(agent) as client:
        response = await client.post(
            "/invoke",
            content=json.dumps({}).encode(),
            headers={"content-type": "application/json", "x-custom-header": "test-value"},
        )

    assert response.status_code == 200
    assert received_headers.get("x-custom-header") == "test-value"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invoke_endpoint_invalid_json_returns_400():
    """POST /invoke with a non-JSON body returns HTTP 400 with an ``error`` field."""
    agent = _build_agent()  # agent_invoke never reached
    async with _client(agent) as client:
        response = await client.post(
            "/invoke",
            content=b"this is not valid json",
            headers={"content-type": "application/json"},
        )

    assert response.status_code == 400
    body = response.json()
    assert "error" in body


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invoke_endpoint_agent_invoke_exception_returns_500():
    """POST /invoke — when ``agent_invoke`` raises, the endpoint returns HTTP 500."""
    async def _invoke(context: AgentInvokeContext):
        raise RuntimeError("internal agent error")

    agent = _build_agent(invoke_side_effect=_invoke)
    async with _client(agent) as client:
        response = await client.post("/invoke", **_json_post_kwargs({"q": "test"}))

    assert response.status_code == 500
    body = response.json()
    assert "error" in body
    assert "internal agent error" in body["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invoke_endpoint_default_raises_not_implemented():
    """POST /invoke — default ``agent_invoke`` raises ``NotImplementedError`` → HTTP 500."""
    agent = _build_agent(invoke_side_effect=None)  # keeps default NotImplementedError impl
    async with _client(agent) as client:
        response = await client.post("/invoke", **_json_post_kwargs({"q": "hi"}))

    assert response.status_code == 500
    body = response.json()
    assert "error" in body
