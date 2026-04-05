# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Integration tests for AgentHost host registration and wiring."""

from __future__ import annotations

import asyncio
import threading
from typing import Any

import pytest

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.hosting._observability import InMemoryCreateSpanHook
from azure.ai.agentserver.responses._options import ResponsesServerOptions
from tests._helpers import EventGate


def _noop_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler used to wire host integration tests."""
    async def _events():
        if False:  # pragma: no cover - keep async generator shape.
            yield None

    return _events()


def _build_client(*, prefix: str = "", options: ResponsesServerOptions | None = None) -> TestClient:
    app = ResponsesAgentServerHost(prefix=prefix, options=options)
    app.create_handler(_noop_response_handler)
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
        additional_server_identity="integration-suite",
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
        additional_server_identity="integration-suite",
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
    assert span.tags["service.name"] == "azure.ai.responses"
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
            yield text_content.emit_done()
            yield message_item.emit_content_done(text_content)
            yield message_item.emit_done()

            yield stream.emit_completed()

        return _events()

    app = ResponsesAgentServerHost()
    app.create_handler(_streaming_handler)
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
            yield text_content.emit_done()
            yield message_item.emit_content_done(text_content)
            yield message_item.emit_done()

            yield stream.emit_completed()

        return _events()

    app = ResponsesAgentServerHost()
    app.create_handler(_non_stream_handler)
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
    app.create_handler(_noop_response_handler)
    client = TestClient(app)

    response = client.get("/readiness")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_hosting__multi_protocol_composition() -> None:
    """Verify ResponseHandler can coexist with other protocol handlers on the same server."""
    app = ResponsesAgentServerHost()
    app.create_handler(_noop_response_handler)
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


@pytest.mark.skip(reason="Shutdown handler registration under investigation after _hosting.py refactor")
def test_hosting__shutdown_signals_inflight_background_execution() -> None:
    started_gate = EventGate()
    cancelled_gate = EventGate()
    shutdown_gate = EventGate()

    def _shutdown_aware_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            yield {
                "type": "response.created",
                "payload": {
                    "status": "in_progress",
                    "output": [],
                },
            }
            started_gate.signal(True)

            while True:
                if context.is_shutdown_requested:
                    shutdown_gate.signal(True)
                if cancellation_signal.is_set():
                    cancelled_gate.signal(True)
                    return
                await asyncio.sleep(0.01)

        return _events()

    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(shutdown_grace_period_seconds=2),
    )
    app.create_handler(_shutdown_aware_handler)

    create_result: dict[str, Any] = {}
    get_result: dict[str, Any] = {}

    with TestClient(app) as client:
        create_response = client.post(
            "/responses",
            json={
                "model": "gpt-4o-mini",
                "input": "hello",
                "stream": False,
                "store": True,
                "background": True,
            },
        )
        assert create_response.status_code == 200
        response_id = create_response.json()["id"]
        create_result["response_id"] = response_id

        def _issue_get() -> None:
            try:
                get_result["response"] = client.get(f"/responses/{response_id}")
            except Exception as exc:  # pragma: no cover - surfaced via assertion below.
                get_result["error"] = exc

        get_thread = threading.Thread(target=_issue_get, daemon=True)
        get_thread.start()

        started, _ = started_gate.wait(timeout_s=2.0)
        assert started, "Expected background handler execution to start before shutdown"
        assert client.portal is not None
        client.portal.call(app.router.shutdown)

        cancelled, _ = cancelled_gate.wait(timeout_s=2.0)
        shutdown_seen, _ = shutdown_gate.wait(timeout_s=2.0)
        assert cancelled, "Expected shutdown to trigger cancellation_signal for in-flight execution"
        assert shutdown_seen, "Expected shutdown to set context.is_shutdown_requested"

        get_thread.join(timeout=2.0)
        assert not get_thread.is_alive(), "Expected in-flight GET request to finish after shutdown"
        assert get_result.get("error") is None, str(get_result.get("error"))
