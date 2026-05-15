# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for SSE keep-alive interleaving on the invocations server.

The invocations server uses the ``SSE_KEEPALIVE_INTERVAL`` environment
variable (resolved via :class:`AgentConfig`) to drive keep-alive frame
injection.  These tests exercise both the env-var-driven path and the
default-disabled path, and also verify that keep-alive is only injected
for ``text/event-stream`` responses (not for arbitrary streaming
content types such as NDJSON).
"""
import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost


def _make_slow_sse_agent(delay_seconds: float = 0.6, event_count: int = 2) -> InvocationAgentServerHost:
    """Agent whose invoke handler yields SSE events spaced by *delay_seconds*."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(_request: Request) -> StreamingResponse:
        async def _events():
            for i in range(event_count):
                if i > 0:
                    await asyncio.sleep(delay_seconds)
                yield f"event: msg\ndata: {{\"i\": {i}}}\n\n".encode("utf-8")

        return StreamingResponse(_events(), media_type="text/event-stream")

    return app


def _make_slow_ndjson_agent(delay_seconds: float = 0.6, event_count: int = 2) -> InvocationAgentServerHost:
    """Agent whose invoke handler streams NDJSON (not SSE) with delays."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(_request: Request) -> StreamingResponse:
        async def _events():
            for i in range(event_count):
                if i > 0:
                    await asyncio.sleep(delay_seconds)
                yield f'{{"i": {i}}}\n'.encode("utf-8")

        return StreamingResponse(_events(), media_type="application/x-ndjson")

    return app


def _parse_lines(text: str) -> list[str]:
    return text.splitlines()


# ---------------------------------------------------------------------------
# Default (env var unset) — no keep-alive frames are emitted
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sse_keepalive_disabled_by_default(monkeypatch):
    """With SSE_KEEPALIVE_INTERVAL unset, no ``: keep-alive`` lines appear."""
    monkeypatch.delenv("SSE_KEEPALIVE_INTERVAL", raising=False)
    app = _make_slow_sse_agent(delay_seconds=0.4, event_count=2)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"")
        assert resp.status_code == 200
        lines = _parse_lines(resp.text)

    keepalive_lines = [line for line in lines if line.startswith(": keep-alive")]
    assert keepalive_lines == []


# ---------------------------------------------------------------------------
# Env-var driven — keep-alive frames are injected into idle SSE streams
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sse_keepalive_interleaves_frames_when_env_var_set(monkeypatch):
    """When SSE_KEEPALIVE_INTERVAL is set, ``: keep-alive`` frames appear
    during gaps between handler events."""
    monkeypatch.setenv("SSE_KEEPALIVE_INTERVAL", "1")
    # Construct the host AFTER setting the env var so AgentConfig.from_env()
    # picks up the value.
    app = _make_slow_sse_agent(delay_seconds=2.5, event_count=2)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"")
        assert resp.status_code == 200
        lines = _parse_lines(resp.text)

    keepalive_lines = [line for line in lines if line.startswith(": keep-alive")]
    assert len(keepalive_lines) >= 1, f"Expected at least one keep-alive comment, got lines={lines!r}"
    # Original handler events are still present and intact.
    assert any(line == "event: msg" for line in lines)
    assert any(line.startswith("data:") for line in lines)


# ---------------------------------------------------------------------------
# Keep-alive must not be applied to non-SSE streaming responses
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sse_keepalive_not_applied_to_non_sse_streams(monkeypatch):
    """Keep-alive comment frames must not be injected into NDJSON streams
    even when SSE_KEEPALIVE_INTERVAL is set."""
    monkeypatch.setenv("SSE_KEEPALIVE_INTERVAL", "1")
    app = _make_slow_ndjson_agent(delay_seconds=2.5, event_count=2)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"")
        assert resp.status_code == 200
        body = resp.text

    assert ": keep-alive" not in body
