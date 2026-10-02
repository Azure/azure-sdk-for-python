# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for invocations SSE keep-alive behavior."""

import asyncio
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations._sse import _with_keep_alive


async def _collect(source: AsyncIterator[object]) -> list[object]:
    return [item async for item in source]


@pytest.mark.asyncio
async def test_with_keep_alive_emits_comment_during_idle_gap() -> None:
    async def source() -> AsyncIterator[str]:
        yield "started"
        await asyncio.sleep(0.1)
        yield "finished"

    chunks = await _collect(_with_keep_alive(source(), 0.02))

    assert ": keep-alive\n\n" in chunks
    assert [chunk for chunk in chunks if chunk != ": keep-alive\n\n"] == [
        "started",
        "finished",
    ]


@pytest.mark.asyncio
async def test_with_keep_alive_passthrough_when_disabled() -> None:
    async def source() -> AsyncIterator[bytes]:
        yield b"first"
        yield b"second"

    assert await _collect(_with_keep_alive(source(), 0)) == [b"first", b"second"]


@pytest.mark.asyncio
async def test_with_keep_alive_propagates_source_error() -> None:
    async def source() -> AsyncIterator[str]:
        yield "started"
        raise RuntimeError("stream failed")

    stream = _with_keep_alive(source(), 0.02)

    assert await anext(stream) == "started"
    with pytest.raises(RuntimeError, match="stream failed"):
        await anext(stream)


@pytest.mark.asyncio
async def test_with_keep_alive_propagates_source_cancellation() -> None:
    async def source() -> AsyncIterator[str]:
        yield "started"
        raise asyncio.CancelledError

    stream = _with_keep_alive(source(), 0.02)

    assert await anext(stream) == "started"
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(anext(stream), timeout=1.0)


@pytest.mark.asyncio
async def test_with_keep_alive_closes_source_when_consumer_stops() -> None:
    finalized = asyncio.Event()

    async def source() -> AsyncIterator[str]:
        try:
            yield "started"
            await asyncio.Event().wait()
        finally:
            finalized.set()

    stream = _with_keep_alive(source(), 0.02)

    assert await anext(stream) == "started"
    await stream.aclose()

    await asyncio.wait_for(finalized.wait(), timeout=1.0)


@pytest.mark.asyncio
async def test_with_keep_alive_preserves_source_backpressure() -> None:
    produced = 0

    async def source() -> AsyncIterator[str]:
        nonlocal produced
        for index in range(100):
            produced += 1
            yield str(index)

    stream = _with_keep_alive(source(), 0.02)

    assert await anext(stream) == "0"
    await asyncio.sleep(0.05)
    assert produced == 1

    await stream.aclose()


@pytest.mark.asyncio
async def test_invocations_sse_stream_uses_configured_keep_alive(monkeypatch) -> None:
    monkeypatch.setenv("SSE_KEEPALIVE_INTERVAL", "1")
    app = InvocationAgentServerHost(configure_observability=None)

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate() -> AsyncIterator[str]:
            yield "data: started\n\n"
            await asyncio.sleep(1.1)
            yield "data: finished\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/invocations",
            headers={"accept": "text/event-stream"},
        )

    assert response.status_code == 200
    assert ": keep-alive\n\n" in response.text
    assert response.text.index("data: started") < response.text.index("data: finished")


@pytest.mark.asyncio
async def test_invocations_non_sse_stream_does_not_get_keep_alive(monkeypatch) -> None:
    monkeypatch.setenv("SSE_KEEPALIVE_INTERVAL", "1")
    app = InvocationAgentServerHost(configure_observability=None)

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate() -> AsyncIterator[str]:
            yield '{"chunk": 1}\n'
            await asyncio.sleep(1.1)
            yield '{"chunk": 2}\n'

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/invocations")

    assert response.status_code == 200
    assert ": keep-alive" not in response.text


@pytest.mark.asyncio
async def test_invocations_uses_final_content_type_header(monkeypatch) -> None:
    monkeypatch.setenv("SSE_KEEPALIVE_INTERVAL", "1")
    app = InvocationAgentServerHost(configure_observability=None)

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate() -> AsyncIterator[str]:
            yield '{"chunk": 1}\n'
            await asyncio.sleep(1.1)
            yield '{"chunk": 2}\n'

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"content-type": "application/x-ndjson"},
        )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/invocations")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-ndjson"
    assert ": keep-alive" not in response.text


@pytest.mark.asyncio
async def test_invocations_adds_keep_alive_for_final_sse_header(monkeypatch) -> None:
    monkeypatch.setenv("SSE_KEEPALIVE_INTERVAL", "1")
    app = InvocationAgentServerHost(configure_observability=None)

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate() -> AsyncIterator[str]:
            yield "data: started\n\n"
            await asyncio.sleep(1.1)
            yield "data: finished\n\n"

        return StreamingResponse(
            generate(),
            media_type="application/x-ndjson",
            headers={"content-type": "text/event-stream"},
        )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/invocations")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"
    assert ": keep-alive\n\n" in response.text
