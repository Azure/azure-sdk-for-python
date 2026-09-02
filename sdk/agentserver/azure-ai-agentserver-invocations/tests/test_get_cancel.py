# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for GET /invocations/{id} and POST /invocations/{id}/cancel."""
import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core import get_request_context
from azure.ai.agentserver.invocations import InvocationAgentServerHost


# ---------------------------------------------------------------------------
# GET after invoke
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_after_invoke_returns_stored_result(async_storage_client):
    """GET /invocations/{id} after invoke returns the stored result."""
    resp = await async_storage_client.post("/invocations", content=b"stored-data")
    assert resp.status_code == 200
    inv_id = resp.headers["x-agent-invocation-id"]

    get_resp = await async_storage_client.get(f"/invocations/{inv_id}")
    assert get_resp.status_code == 200
    assert get_resp.content == b"stored-data"


# ---------------------------------------------------------------------------
# GET unknown ID
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_unknown_id_returns_404(async_storage_client):
    """GET /invocations/{unknown} returns 404."""
    resp = await async_storage_client.get("/invocations/unknown-id-12345")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Cancel after invoke
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_after_invoke_returns_cancelled(async_storage_client):
    """POST /invocations/{id}/cancel after invoke returns cancelled status."""
    resp = await async_storage_client.post("/invocations", content=b"cancel-me")
    inv_id = resp.headers["x-agent-invocation-id"]

    cancel_resp = await async_storage_client.post(f"/invocations/{inv_id}/cancel")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"


# ---------------------------------------------------------------------------
# Cancel unknown ID
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_unknown_id_returns_404(async_storage_client):
    """POST /invocations/{unknown}/cancel returns 404."""
    resp = await async_storage_client.post("/invocations/unknown-id-12345/cancel")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET after cancel
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_after_cancel_returns_404(async_storage_client):
    """GET after cancel returns 404 (data has been removed)."""
    resp = await async_storage_client.post("/invocations", content=b"temp")
    inv_id = resp.headers["x-agent-invocation-id"]
    await async_storage_client.post(f"/invocations/{inv_id}/cancel")

    get_resp = await async_storage_client.get(f"/invocations/{inv_id}")
    assert get_resp.status_code == 404


# ---------------------------------------------------------------------------
# GET error returns 500 (inline InvocationAgentServerHost)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_invocation_error_returns_500():
    """GET handler raising an exception returns 500."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @app.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        raise RuntimeError("get failed")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations/some-id")
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "internal_error"


# ---------------------------------------------------------------------------
# Cancel error returns 500 (inline InvocationAgentServerHost)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_invocation_error_returns_500():
    """Cancel handler raising an exception returns 500."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @app.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        raise RuntimeError("cancel failed")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations/some-id/cancel")
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "internal_error"


# ---------------------------------------------------------------------------
# Regression: ``request.state.session_id`` is populated on cancel + get
# endpoints.
#
# Per the invocation protocol spec
# (`invocation-protocol-spec.md` §1.2 GET, §1.3 cancel), neither GET nor
# cancel has a platform-defined ``agent_session_id`` query parameter.
# The session is implicit and sourced from the
# ``FOUNDRY_AGENT_SESSION_ID`` environment variable the platform sets
# on the container (surfaced via ``self.config.session_id``).
#
# These tests pin the contract that the framework surfaces that
# resolved session id on ``request.state.session_id`` for custom
# cancel / get handlers, with the same source-precedence as the
# invoke endpoint (caller-provided query param wins, env var falls
# back, empty string if both absent).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_propagates_session_id_from_env_var(monkeypatch):
    """``POST /invocations/{id}/cancel`` exposes
    ``request.state.session_id`` populated from the
    ``FOUNDRY_AGENT_SESSION_ID`` env var when no query param is
    present (the hosted-platform default per the invocation protocol
    spec)."""
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "platform-session-hosted")
    app = InvocationAgentServerHost()

    captured: dict[str, str] = {}

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @app.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        captured["session_id"] = request.state.session_id
        captured["invocation_id"] = request.state.invocation_id
        return JSONResponse({"status": "cancelled"})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations/some-id/cancel")
    assert resp.status_code == 200
    assert captured["session_id"] == "platform-session-hosted"
    assert captured["invocation_id"] == "some-id"


@pytest.mark.asyncio
async def test_get_propagates_session_id_from_env_var(monkeypatch):
    """``GET /invocations/{id}`` mirrors the cancel behaviour:
    ``request.state.session_id`` resolves from
    ``FOUNDRY_AGENT_SESSION_ID`` when no query param is present."""
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "platform-session-get")
    app = InvocationAgentServerHost()

    captured: dict[str, str] = {}

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @app.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        captured["session_id"] = request.state.session_id
        captured["invocation_id"] = request.state.invocation_id
        return JSONResponse({"status": "ok"})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations/some-id")
    assert resp.status_code == 200
    assert captured["session_id"] == "platform-session-get"
    assert captured["invocation_id"] == "some-id"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "path", "decorator_name"),
    [
        ("GET", "/invocations/some-id", "get_invocation_handler"),
        ("POST", "/invocations/some-id/cancel", "cancel_invocation_handler"),
    ],
)
async def test_get_and_cancel_bind_platform_request_context(method, path, decorator_name):
    """GET and cancel handlers receive the platform identity context."""
    app = InvocationAgentServerHost()
    captured: dict[str, str | None] = {}

    async def handler(request: Request) -> Response:
        context = get_request_context()
        captured["call_id"] = context.call_id
        captured["user_id"] = context.user_id
        captured["state_call_id"] = request.state.call_id
        captured["state_user_id"] = request.state.user_id
        return JSONResponse({"status": "ok"})

    getattr(app, decorator_name)(handler)

    transport = ASGITransport(app=app)
    headers = {
        "x-agent-foundry-call-id": "foundry-call",
        "x-agent-user-id": "foundry-user",
    }
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.request(method, path, headers=headers)

    assert resp.status_code == 200
    assert captured == {
        "call_id": "foundry-call",
        "user_id": "foundry-user",
        "state_call_id": "foundry-call",
        "state_user_id": "foundry-user",
    }


@pytest.mark.asyncio
async def test_cancel_caller_query_param_overrides_env_var(monkeypatch):
    """A caller-provided ``agent_session_id`` query param wins over the
    env var (matches the invoke endpoint's precedence). The spec does
    not require callers to pass it on cancel/get, but if they do, the
    framework forwards it transparently — and the framework's
    ``request.state.session_id`` reflects the override."""
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "env-session")
    app = InvocationAgentServerHost()

    captured: dict[str, str] = {}

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @app.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        captured["session_id"] = request.state.session_id
        return JSONResponse({"status": "cancelled"})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations/some-id/cancel?agent_session_id=caller-override")
    assert resp.status_code == 200
    assert captured["session_id"] == "caller-override"


@pytest.mark.asyncio
async def test_cancel_without_env_var_or_query_param_yields_empty_session_id(monkeypatch):
    """When neither the env var nor a caller-supplied query param is
    present, ``request.state.session_id`` is the empty string —
    handlers can branch on falsy without an AttributeError."""
    monkeypatch.delenv("FOUNDRY_AGENT_SESSION_ID", raising=False)
    app = InvocationAgentServerHost()

    captured: dict[str, str] = {}

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @app.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        captured["session_id"] = request.state.session_id
        return JSONResponse({"status": "cancelled"})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations/some-id/cancel")
    assert resp.status_code == 200
    assert captured["session_id"] == ""
