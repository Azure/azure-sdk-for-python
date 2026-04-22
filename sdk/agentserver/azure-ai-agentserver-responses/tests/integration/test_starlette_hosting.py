# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Integration tests for AgentHost host registration and wiring."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._options import ResponsesServerOptions
from azure.ai.agentserver.responses.hosting._observability import InMemoryCreateSpanHook
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream


def _noop_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler used to wire host integration tests."""

    async def _events():
        if False:  # pragma: no cover - keep async generator shape.
            yield None

    return _events()


def _build_client(*, prefix: str = "", options: ResponsesServerOptions | None = None) -> TestClient:
    app = ResponsesAgentServerHost(prefix=prefix, options=options)
    app.response_handler(_noop_response_handler)
    return TestClient(app)


def test_hosting__registers_create_get_cancel_routes_under_prefix() -> None:
    client = _build_client(prefix="/v1")

    create_response = client.post(
        "/v1/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
        },
    )
    assert create_response.status_code == 200
    response_id = create_response.json()["id"]

    get_response = client.get(f"/v1/responses/{response_id}")
    assert get_response.status_code in {200, 404}

    cancel_response = client.post(f"/v1/responses/{response_id}/cancel")
    assert cancel_response.status_code in {200, 400, 404}


def test_hosting__options_are_applied_to_runtime_behavior() -> None:
    options = ResponsesServerOptions(
        additional_server_version="integration-suite",
        default_model="gpt-4o-mini",
        sse_keep_alive_interval_seconds=5,
    )
    client = _build_client(options=options)

    response = client.post(
        "/responses",
        json={
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 200
    assert "x-platform-server" in response.headers


def test_hosting__client_disconnect_behavior_remains_contract_compliant() -> None:
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        first_line = next(response.iter_lines(), "")
        assert first_line.startswith("event:") or first_line.startswith("data:")

    # Post-disconnect visibility and state should remain contract-compliant.
    # This call should not raise and should return a defined protocol outcome.
    follow_up = client.get("/responses/resp_disconnect_probe")
    assert follow_up.status_code in {200, 400, 404}


def test_hosting__create_emits_single_root_span_with_key_tags_and_identity_header() -> None:
    hook = InMemoryCreateSpanHook()
    options = ResponsesServerOptions(
        additional_server_version="integration-suite",
        create_span_hook=hook,
    )
    client = _build_client(options=options)

    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 200
    assert "x-platform-server" in response.headers

    assert len(hook.spans) == 1
    span = hook.spans[0]
    assert span.name == "create_response"
    assert span.error is None
    assert span.ended_at is not None
    assert span.tags["service.name"] == "azure.ai.agentserver"
    assert span.tags["gen_ai.operation.name"] == "invoke_agent"
    assert span.tags["gen_ai.system"] == "responses"
    assert span.tags["gen_ai.request.model"] == "gpt-4o-mini"
    assert isinstance(span.tags["gen_ai.response.id"], str)


def test_hosting__stream_mode_surfaces_handler_output_item_and_content_events() -> None:
    from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

    def _streaming_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
            yield stream.emit_created()
            yield stream.emit_in_progress()

            message_item = stream.add_output_item_message()
            yield message_item.emit_added()

            text_content = message_item.add_text_content()
            yield text_content.emit_added()
            yield text_content.emit_delta("hello")
            yield text_content.emit_text_done()
            yield text_content.emit_done()
            yield message_item.emit_done()

            yield stream.emit_completed()

        return _events()

    app = ResponsesAgentServerHost()
    app.response_handler(_streaming_handler)
    client = TestClient(app)

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        lines = [line for line in response.iter_lines() if line]

    event_lines = [line for line in lines if line.startswith("event:")]
    assert "event: response.output_item.added" in event_lines
    assert "event: response.content_part.added" in event_lines
    assert "event: response.output_text.delta" in event_lines
    assert "event: response.output_text.done" in event_lines
    assert "event: response.content_part.done" in event_lines
    assert "event: response.output_item.done" in event_lines


def test_hosting__non_stream_mode_returns_completed_response_with_output_items() -> None:
    from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

    def _non_stream_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
            yield stream.emit_created()
            yield stream.emit_in_progress()

            message_item = stream.add_output_item_message()
            yield message_item.emit_added()

            text_content = message_item.add_text_content()
            yield text_content.emit_added()
            yield text_content.emit_delta("hello")
            yield text_content.emit_text_done()
            yield text_content.emit_done()
            yield message_item.emit_done()

            yield stream.emit_completed()

        return _events()

    app = ResponsesAgentServerHost()
    app.response_handler(_non_stream_handler)
    client = TestClient(app)

    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["id"].startswith("caresp_")
    assert isinstance(payload.get("output"), list)
    assert len(payload["output"]) == 1
    assert payload["output"][0]["type"] == "message"
    assert payload["output"][0]["content"][0]["type"] == "output_text"
    assert payload["output"][0]["content"][0]["text"] == "hello"


def test_hosting__health_endpoint_is_available() -> None:
    """Verify AgentHost provides health endpoint automatically."""
    app = ResponsesAgentServerHost()
    app.response_handler(_noop_response_handler)
    client = TestClient(app)

    response = client.get("/readiness")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_hosting__multi_protocol_composition() -> None:
    """Verify ResponseHandler can coexist with other protocol handlers on the same server."""
    app = ResponsesAgentServerHost()
    app.response_handler(_noop_response_handler)
    client = TestClient(app)

    # Responses endpoint works
    create_response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
        },
    )
    assert create_response.status_code == 200

    # Health endpoint works
    health_response = client.get("/readiness")
    assert health_response.status_code == 200


@pytest.mark.asyncio
async def test_hosting__shutdown_signals_inflight_background_execution() -> None:
    """Verify that graceful shutdown cancels in-flight background responses.

    Uses a real Hypercorn server so that shutdown triggers the Starlette
    lifespan exit, which calls our handle_shutdown() handler.
    """
    import socket

    from hypercorn.asyncio import serve as _hc_serve
    from hypercorn.config import Config as _HcConfig

    handler_started = asyncio.Event()
    handler_cancelled = asyncio.Event()
    shutdown_seen = asyncio.Event()

    def _shutdown_aware_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_in_progress()
            handler_started.set()

            while True:
                if context.is_shutdown_requested:
                    shutdown_seen.set()
                if cancellation_signal.is_set():
                    handler_cancelled.set()
                    yield stream.emit_incomplete(reason="cancelled")
                    return
                await asyncio.sleep(0.01)

        return _events()

    test_app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(shutdown_grace_period_seconds=2),
    )
    test_app.response_handler(_shutdown_aware_handler)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    hc_config = _HcConfig()
    hc_config.bind = [f"127.0.0.1:{port}"]
    shutdown_event = asyncio.Event()

    server_task = asyncio.create_task(
        _hc_serve(test_app, hc_config, shutdown_trigger=shutdown_event.wait)  # type: ignore[arg-type]
    )
    await asyncio.sleep(0.5)

    try:
        import httpx

        async with httpx.AsyncClient(
            base_url=f"http://127.0.0.1:{port}",
            timeout=httpx.Timeout(10.0),
        ) as client:
            # Create a background response
            create_resp = await client.post(
                "/responses",
                json={
                    "model": "gpt-4o-mini",
                    "input": "hello",
                    "stream": False,
                    "store": True,
                    "background": True,
                },
            )
            assert create_resp.status_code == 200
            _response_id = create_resp.json()["id"]  # noqa: F841

            # Wait for handler to start
            await asyncio.wait_for(handler_started.wait(), timeout=3.0)

            # Trigger graceful shutdown
            shutdown_event.set()

            # Wait for handler to see shutdown + cancellation
            await asyncio.wait_for(handler_cancelled.wait(), timeout=5.0)

            assert handler_cancelled.is_set(), "Shutdown should trigger cancellation_signal"
            assert shutdown_seen.is_set(), "Shutdown should set context.is_shutdown_requested"

    finally:
        shutdown_event.set()  # ensure shutdown in case of test failure
        await asyncio.wait_for(server_task, timeout=10.0)


def test_hosting__client_headers_keys_are_normalized_to_lowercase() -> None:
    """Verify that x-client-* headers are stored with lowercase keys."""
    captured_headers: dict[str, str] = {}

    def _header_capturing_handler(request: Any, context: Any, cancellation_signal: Any):
        captured_headers.update(context.client_headers)

        async def _events():
            if False:  # pragma: no cover
                yield None

        return _events()

    app = ResponsesAgentServerHost()
    app.response_handler(_header_capturing_handler)
    client = TestClient(app)

    client.post(
        "/responses",
        json={"model": "test", "input": "hi", "stream": False, "store": True, "background": False},
        headers={
            "X-Client-Foo": "bar",
            "x-client-baz": "qux",
        },
    )

    assert "x-client-foo" in captured_headers
    assert "x-client-baz" in captured_headers
    assert captured_headers["x-client-foo"] == "bar"
    assert captured_headers["x-client-baz"] == "qux"
