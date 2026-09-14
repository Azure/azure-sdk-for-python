# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ASGI send-order tests; buffered clients are not used to measure first content."""

from __future__ import annotations

import asyncio
import json
import threading
from typing import Any
from unittest.mock import AsyncMock

import pytest
from starlette.requests import ClientDisconnect

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.hosting import _endpoint_handler as endpoint
from azure.ai.agentserver.responses.hosting import _orchestrator as orchestration
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming import ResponseEventStream


def _scope(spec: str = "2.4") -> dict[str, Any]:
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": spec},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/responses",
        "raw_path": b"/responses",
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-type", b"application/json")],
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 12345),
    }


async def _never_receive() -> dict[str, Any]:
    await asyncio.Event().wait()
    raise AssertionError("unreachable")


@pytest.mark.parametrize("spec", ["2.3", "2.4"])
@pytest.mark.parametrize("store", [False, True])
async def test_real_body_and_ended_span_precede_flush_and_final_send(
    monkeypatch: pytest.MonkeyPatch, spec: str, store: bool
) -> None:
    events: list[str] = []
    flush_started = asyncio.Event()
    release = threading.Event()
    loop = asyncio.get_running_loop()

    class Hook:
        def on_span_start(self, name: str, tags: dict[str, Any]) -> None:
            pass

        def on_span_end(self, name: str, tags: dict[str, Any], error: BaseException | None) -> None:
            events.append("span-ended")

    class DelayedExporter:
        def force_flush(self, timeout_millis: int) -> None:
            assert timeout_millis == 5000
            events.append("flush-start")
            loop.call_soon_threadsafe(flush_started.set)
            assert release.wait(timeout_millis / 1000), "event loop could not release blocking exporter"
            events.append("flush-end")

    monkeypatch.setattr(endpoint, "flush_spans", lambda: DelayedExporter().force_flush(5000))

    async def handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
        stream = ResponseEventStream(response_id=context.response_id, model="m")
        yield stream.emit_created()
        yield stream.emit_completed()
        events.append("handler-ended")

    provider = InMemoryResponseProvider()
    original_create = provider.create_response

    async def create(*args: Any, **kwargs: Any) -> None:
        await original_create(*args, **kwargs)
        events.append("initial-persisted")

    monkeypatch.setattr(provider, "create_response", create)
    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=False, create_span_hook=Hook()),
        store=provider,
    )
    app.response_handler(handler)
    payload = json.dumps({"model": "m", "input": "hi", "stream": True, "store": store}).encode()
    request_sent = False

    async def receive() -> dict[str, Any]:
        nonlocal request_sent
        if not request_sent:
            request_sent = True
            return {"type": "http.request", "body": payload, "more_body": False}
        return await _never_receive()

    async def send(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.body":
            if b"response.created" in message.get("body", b""):
                if store:
                    assert "initial-persisted" in events
                events.append("created-body")
            if not message.get("more_body", False):
                events.append("http-complete")

    task = asyncio.create_task(app(_scope(spec), receive, send))
    try:
        await asyncio.wait_for(flush_started.wait(), 10)
        assert "created-body" in events
        assert "handler-ended" in events
        assert "span-ended" in events
        assert "flush-end" not in events
        assert "http-complete" not in events
        # This coroutine is running while the exporter is blocked in a worker.
        events.append("event-loop-responsive")
    finally:
        release.set()
        await asyncio.wait_for(task, 10)
    assert events.index("created-body") < events.index("flush-start")
    assert events.index("span-ended") < events.index("flush-start")
    assert events.index("handler-ended") < events.index("flush-start")
    assert events.index("flush-end") < events.index("http-complete")
    assert events.count("flush-start") == 1


@pytest.mark.parametrize("failure", [False, True])
async def test_sync_success_and_handler_error_still_flush_before_sending(
    monkeypatch: pytest.MonkeyPatch, failure: bool
) -> None:
    events: list[str] = []
    monkeypatch.setattr(endpoint, "flush_spans", lambda: events.append("flush"))

    async def handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
        if failure:
            raise RuntimeError("handler failed")
        stream = ResponseEventStream(response_id=context.response_id, model="m")
        yield stream.emit_created()
        yield stream.emit_completed()

    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=False), store=InMemoryResponseProvider()
    )
    app.response_handler(handler)
    receive = AsyncMock(
        return_value={
            "type": "http.request",
            "body": json.dumps({"model": "m", "input": "hi", "stream": False, "store": False}).encode(),
            "more_body": False,
        }
    )

    async def send(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.start":
            assert message["status"] == (500 if failure else 200)
            events.append("http-start")

    await app(_scope(), receive, send)
    assert events == ["flush", "http-start"]


@pytest.mark.parametrize("interval", [None, 60])
@pytest.mark.parametrize("ending", ["empty", "eof", "error", "send-error", "disconnect", "cancel"])
async def test_stream_cleanup_flushes_once_before_return(
    monkeypatch: pytest.MonkeyPatch, interval: float | None, ending: str
) -> None:
    events: list[str] = []
    disconnected = asyncio.Event()
    monkeypatch.setattr(endpoint, "flush_spans", lambda: events.append("flush"))

    async def source() -> Any:
        try:
            if ending == "empty":
                return
            yield 'event: response.created\ndata: {"type":"response.created"}\n\n'
            if ending == "error":
                raise ValueError("stream failure")
            if ending in ("disconnect", "cancel", "send-error"):
                await asyncio.Event().wait()
        finally:
            events.append("closed")

    async def send(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.body" and message.get("body"):
            events.append("body")
            if ending == "send-error":
                raise OSError("connection closed")
            if ending == "disconnect":
                disconnected.set()
            if ending == "cancel":
                asyncio.current_task().cancel()
        if message["type"] == "http.response.body" and not message.get("more_body", False):
            events.append("http-complete")

    async def receive() -> dict[str, Any]:
        await disconnected.wait()
        return {"type": "http.disconnect"}

    response = endpoint._CreateStreamingResponse(source(), interval, headers={})
    expected = {"error": ValueError, "send-error": ClientDisconnect, "cancel": asyncio.CancelledError}
    call = response(_scope("2.3" if ending == "disconnect" else "2.4"), receive, send)
    if ending in expected:
        with pytest.raises(expected[ending]):
            await asyncio.wait_for(call, 10)
    else:
        await asyncio.wait_for(call, 10)
    assert events.count("flush") == 1
    assert events.index("closed") < events.index("flush")
    if ending in ("empty", "eof"):
        assert events.index("flush") < events.index("http-complete")
    else:
        assert "http-complete" not in events


async def test_cancellation_during_flush_drains_exporter(monkeypatch: pytest.MonkeyPatch) -> None:
    started = asyncio.Event()
    release = threading.Event()
    ended = threading.Event()
    loop = asyncio.get_running_loop()

    def flush() -> None:
        loop.call_soon_threadsafe(started.set)
        assert release.wait(5)
        ended.set()

    monkeypatch.setattr(endpoint, "flush_spans", flush)
    task = asyncio.create_task(endpoint._flush_spans_async())
    try:
        await asyncio.wait_for(started.wait(), 5)
        task.cancel()
        await asyncio.sleep(0)
        task.cancel()
        await asyncio.sleep(0)
        assert not task.done()
        assert not ended.is_set()
    finally:
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, 5)
    assert ended.is_set()


@pytest.mark.parametrize("interval", [None, 60])
@pytest.mark.parametrize("handler_shape", ["async-generator", "coroutine", "async-iterable"])
@pytest.mark.parametrize(
    "ending",
    [
        "send-error",
        "disconnect",
        "cancel",
        "disconnect-awaiting-handler",
        "handler-error",
        "invalid-first",
        "empty",
        "eof",
    ],
)
async def test_real_pipeline_awaits_handler_cleanup_before_flush(
    monkeypatch: pytest.MonkeyPatch, interval: float | None, ending: str, handler_shape: str
) -> None:
    events: list[str] = []
    cleanup_started = asyncio.Event()
    cleanup_complete = asyncio.Event()
    release_cleanup = asyncio.Event()
    handler_waiting = asyncio.Event()
    disconnected = asyncio.Event()
    final_states: list[Any] = []
    frames: list[str] = []
    monkeypatch.setattr(endpoint, "flush_spans", lambda: events.append("flush"))
    original_finalize = orchestration._ResponseOrchestrator._finalize_stream

    async def finalize(self: Any, ctx: Any, state: Any) -> None:
        await original_finalize(self, ctx, state)
        final_states.append(state)
        events.append("orchestrator-finalized")

    monkeypatch.setattr(orchestration._ResponseOrchestrator, "_finalize_stream", finalize)

    async def handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
        try:
            stream = ResponseEventStream(response_id=context.response_id, model="m")
            if ending == "empty":
                return
            if ending == "invalid-first":
                yield stream.emit_in_progress()
                return
            yield stream.emit_created()
            if ending == "handler-error":
                raise ValueError("handler failed after creation")
            if ending != "eof":
                handler_waiting.set()
                await asyncio.Event().wait()
            yield stream.emit_completed()
        finally:
            events.append("handler-cleanup-start")
            cleanup_started.set()
            await release_cleanup.wait()
            events.append("handler-cleanup-complete")
            cleanup_complete.set()

    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=False, sse_keep_alive_interval_seconds=interval),
        store=InMemoryResponseProvider(),
    )

    async def returning_handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
        class HandlerEvents:
            def __aiter__(self) -> Any:
                return handler(request, context, cancellation_signal)

        if handler_shape == "async-iterable":
            return HandlerEvents()
        return handler(request, context, cancellation_signal)

    app.response_handler(handler if handler_shape == "async-generator" else returning_handler)
    payload = json.dumps({"model": "m", "input": "hi", "stream": True, "store": False}).encode()
    request_sent = False

    async def receive() -> dict[str, Any]:
        nonlocal request_sent
        if not request_sent:
            request_sent = True
            return {"type": "http.request", "body": payload, "more_body": False}
        if ending == "disconnect-awaiting-handler":
            await handler_waiting.wait()
        else:
            await disconnected.wait()
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.start":
            assert message["status"] == 200
        if message["type"] != "http.response.body":
            return
        body = message.get("body", b"").decode()
        frames.extend(line[7:] for line in body.splitlines() if line.startswith("event: "))
        if "response.created" in body:
            if ending == "send-error":
                raise OSError("connection closed")
            if ending == "cancel":
                raise asyncio.CancelledError()
            if ending == "disconnect":
                disconnected.set()
                await asyncio.Event().wait()
        if not message.get("more_body", False):
            events.append("http-complete")

    async def run_request() -> None:
        try:
            await app(_scope("2.3" if ending.startswith("disconnect") else "2.4"), receive, send)
        finally:
            events.append("request-returned")

    task = asyncio.create_task(run_request())
    try:
        await asyncio.wait_for(cleanup_started.wait(), 5)
        assert not task.done(), events
        assert "flush" not in events
        assert "orchestrator-finalized" not in events
        assert "http-complete" not in events
        if ending in ("send-error", "disconnect", "cancel"):
            assert not handler_waiting.is_set()
        release_cleanup.set()
        if ending == "send-error":
            with pytest.raises(ClientDisconnect):
                await asyncio.wait_for(task, 5)
        elif ending == "cancel":
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, 5)
        else:
            await asyncio.wait_for(task, 5)
        assert cleanup_complete.is_set()
        assert events.index("handler-cleanup-complete") < events.index("orchestrator-finalized")
        assert events.index("orchestrator-finalized") < events.index("flush")
        assert events.index("flush") < events.index("request-returned")
        assert events.count("flush") == 1
        assert len(final_states) == 1
        if ending in ("empty", "eof", "handler-error", "invalid-first"):
            assert events.index("flush") < events.index("http-complete")
            expected = {
                "empty": ["response.created", "response.in_progress", "response.completed"],
                "eof": ["response.created", "response.completed"],
                "handler-error": ["response.created", "response.failed"],
                "invalid-first": ["error"],
            }
            assert frames == expected[ending]
        else:
            assert "http-complete" not in events
            assert final_states[0].stream_interrupted
    finally:
        release_cleanup.set()
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.parametrize("interval", [None, 60])
@pytest.mark.parametrize("background", [False, True])
@pytest.mark.parametrize("ending", ["send-error", "disconnect"])
async def test_stored_producer_remains_independent_of_request_cleanup(
    monkeypatch: pytest.MonkeyPatch, interval: float | None, background: bool, ending: str
) -> None:
    events: list[str] = []
    release_producer = asyncio.Event()
    cleanup_started = asyncio.Event()
    release_cleanup = asyncio.Event()
    cleanup_complete = asyncio.Event()
    disconnected = asyncio.Event()
    initial_persisted = asyncio.Event()
    records: list[Any] = []
    monkeypatch.setattr(endpoint, "flush_spans", lambda: events.append("flush"))
    original_start = orchestration._ResponseOrchestrator._start_resilient_background

    async def start(self: Any, ctx: Any, record: Any, fallback: Any, **kwargs: Any) -> None:
        await original_start(self, ctx, record, fallback, **kwargs)
        records.append(record)

    monkeypatch.setattr(orchestration._ResponseOrchestrator, "_start_resilient_background", start)
    provider = InMemoryResponseProvider()
    original_create = provider.create_response

    async def create(*args: Any, **kwargs: Any) -> None:
        await original_create(*args, **kwargs)
        initial_persisted.set()

    monkeypatch.setattr(provider, "create_response", create)

    async def handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
        try:
            stream = ResponseEventStream(response_id=context.response_id, model="m")
            yield stream.emit_created()
            await release_producer.wait()
            yield stream.emit_completed()
        finally:
            cleanup_started.set()
            await release_cleanup.wait()
            cleanup_complete.set()

    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=False, sse_keep_alive_interval_seconds=interval),
        store=provider,
    )
    app.response_handler(handler)
    payload = json.dumps(
        {"model": "m", "input": "hi", "stream": True, "store": True, "background": background}
    ).encode()
    request_sent = False

    async def receive() -> dict[str, Any]:
        nonlocal request_sent
        if not request_sent:
            request_sent = True
            return {"type": "http.request", "body": payload, "more_body": False}
        await disconnected.wait()
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.start":
            assert message["status"] == 200
        if message["type"] == "http.response.body" and b"response.created" in message.get("body", b""):
            assert initial_persisted.is_set()
            if ending == "send-error":
                raise OSError("connection closed")
            disconnected.set()
            await asyncio.Event().wait()

    task = asyncio.create_task(app(_scope("2.3" if ending == "disconnect" else "2.4"), receive, send))
    try:
        if ending == "send-error":
            with pytest.raises(ClientDisconnect):
                await asyncio.wait_for(task, 5)
        else:
            await asyncio.wait_for(task, 5)
        assert events == ["flush"]
        assert len(records) == 1
        producer = records[0].execution_task
        assert producer is not None and not producer.done()
        assert not cleanup_started.is_set()
        release_producer.set()
        await asyncio.wait_for(cleanup_started.wait(), 5)
        assert not producer.done()
        release_cleanup.set()
        await asyncio.wait_for(producer, 5)
        assert cleanup_complete.is_set()
        stored = await provider.get_response(records[0].response_id)
        # Foreground disconnect already signals cancellation; it does not cancel
        # the independent task or close the handler before its own work finishes.
        assert stored is not None and stored["status"] == ("completed" if background else "cancelled")
    finally:
        release_producer.set()
        release_cleanup.set()
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        for record in records:
            if record.execution_task is not None:
                await asyncio.wait_for(asyncio.gather(record.execution_task, return_exceptions=True), 5)


async def test_normalized_sync_generator_closes_its_owned_source() -> None:
    from azure.ai.agentserver.responses.hosting._routing import _sync_to_async_gen

    closed: list[bool] = []

    def source() -> Any:
        try:
            yield {"type": "response.created"}
        finally:
            closed.append(True)

    iterator = _sync_to_async_gen(source())
    assert await iterator.__anext__() == {"type": "response.created"}
    await iterator.aclose()
    assert closed == [True]
