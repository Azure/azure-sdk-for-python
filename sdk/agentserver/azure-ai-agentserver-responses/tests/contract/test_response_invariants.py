# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for response field invariants across statuses (B6, B19, B33)."""

from __future__ import annotations

import asyncio
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from tests._helpers import poll_until


def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler — auto-completes."""

    async def _events():
        if False:  # pragma: no cover
            yield None

    return _events()


def _throwing_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that raises after emitting created."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        raise RuntimeError("Simulated handler failure")

    return _events()


def _incomplete_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits an incomplete terminal event."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_incomplete(reason="max_output_tokens")

    return _events()


def _delayed_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that sleeps briefly, checking for cancellation."""

    async def _events():
        if cancellation_signal.is_set():
            return
        await asyncio.sleep(0.25)
        if cancellation_signal.is_set():
            return
        if False:  # pragma: no cover
            yield None

    return _events()


def _cancellable_bg_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits response.created then blocks until cancelled (Phase 3)."""

    async def _events():
        yield {"type": "response.created", "response": {"status": "in_progress", "output": []}}
        while not cancellation_signal.is_set():
            await asyncio.sleep(0.01)

    return _events()


def _build_client(handler: Any | None = None) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler or _noop_handler)
    return TestClient(app)


def _wait_for_status(
    client: TestClient,
    response_id: str,
    expected_status: str,
    *,
    timeout_s: float = 5.0,
) -> None:
    latest_status: str | None = None

    def _check() -> bool:
        nonlocal latest_status
        r = client.get(f"/responses/{response_id}")
        if r.status_code != 200:
            return False
        latest_status = r.json().get("status")
        return latest_status == expected_status

    ok, failure = poll_until(
        _check,
        timeout_s=timeout_s,
        interval_s=0.05,
        context_provider=lambda: {"status": latest_status},
        label=f"wait for {expected_status}",
    )
    assert ok, failure


# ══════════════════════════════════════════════════════════
# B6: completed_at invariant
# ══════════════════════════════════════════════════════════


def test_completed_at__nonnull_only_for_completed_status() -> None:
    """B6 — completed_at is non-null only when status is completed."""
    client = _build_client()

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
    assert payload.get("completed_at") is not None, "completed_at should be non-null for completed status"
    assert isinstance(payload["completed_at"], (int, float)), "completed_at should be a Unix timestamp"


def test_completed_at__null_for_failed_status() -> None:
    """B6 — completed_at is null when status is failed."""
    client = _build_client(_throwing_handler)

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
    _wait_for_status(client, response_id, "failed")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["status"] == "failed"
    assert payload.get("completed_at") is None, "completed_at should be null for failed status"


def test_completed_at__null_for_cancelled_status() -> None:
    """B6 — completed_at is null when status is cancelled."""
    client = _build_client(_cancellable_bg_handler)

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

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 200

    _wait_for_status(client, response_id, "cancelled")

    get_response = client.get(f"/responses/{response_id}")
    payload = get_response.json()
    assert payload["status"] == "cancelled"
    assert payload.get("completed_at") is None, "completed_at should be null for cancelled status"


def test_completed_at__null_for_incomplete_status() -> None:
    """B6 — completed_at is null when status is incomplete."""
    client = _build_client(_incomplete_handler)

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
    _wait_for_status(client, response_id, "incomplete")

    get_response = client.get(f"/responses/{response_id}")
    payload = get_response.json()
    assert payload["status"] == "incomplete"
    assert payload.get("completed_at") is None, "completed_at should be null for incomplete status"


# ══════════════════════════════════════════════════════════
# B19: x-platform-server header
# ══════════════════════════════════════════════════════════


def test_x_platform_server_header__present_on_post_response() -> None:
    """B19 — All responses include x-platform-server header."""
    client = _build_client()

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
    header = response.headers.get("x-platform-server")
    assert header is not None, "x-platform-server header must be present per B19"
    assert isinstance(header, str) and len(header) > 0
    # Both core and responses segments must appear
    assert "azure-ai-agentserver-core/" in header
    assert "azure-ai-agentserver-responses/" in header


def test_x_platform_server_header__present_on_get_response() -> None:
    """B19 — x-platform-server header on GET responses."""
    client = _build_client()

    create = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
        },
    )
    response_id = create.json()["id"]

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    header = get_response.headers.get("x-platform-server")
    assert header is not None, "x-platform-server header must be present on GET per B19"


# ══════════════════════════════════════════════════════════
# B33: Token usage
# ══════════════════════════════════════════════════════════


def test_token_usage__structure_valid_when_present() -> None:
    """B33 — Terminal events include optional usage field. When present, check structure."""
    client = _build_client()

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
    # B33: usage is optional. If present, verify structure.
    usage = payload.get("usage")
    if usage is not None:
        assert isinstance(usage.get("input_tokens"), int), "input_tokens should be int"
        assert isinstance(usage.get("output_tokens"), int), "output_tokens should be int"
        assert isinstance(usage.get("total_tokens"), int), "total_tokens should be int"
        assert usage["total_tokens"] == usage["input_tokens"] + usage["output_tokens"]


# ══════════════════════════════════════════════════════════
# B7: created_at present on every response
# ══════════════════════════════════════════════════════════


def test_created_at__present_on_sync_response() -> None:
    """B7 — created_at field must be present (and numeric) on every response object."""
    client = _build_client()

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
    created_at = payload.get("created_at")
    assert created_at is not None, "created_at must be present on every response"
    assert isinstance(created_at, (int, float)), f"created_at must be numeric, got: {type(created_at)}"


def test_created_at__present_on_background_response() -> None:
    """B7 — created_at is also present when fetching a background response via GET."""
    client = _build_client()

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

    _wait_for_status(client, response_id, "completed")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    payload = get_response.json()
    created_at = payload.get("created_at")
    assert created_at is not None, "created_at must be present on background response"
    assert isinstance(created_at, (int, float)), f"created_at must be numeric, got: {type(created_at)}"


# ══════════════════════════════════════════════════════════
# model field: always present in response payload
# ══════════════════════════════════════════════════════════


def test_model_field__present_when_omitted_from_request_sync() -> None:
    """model must be present in the response payload even when the request omits it."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={"input": "hello", "stream": False, "store": True, "background": False},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "model" in payload, "model field must always be present in response"
    assert isinstance(payload["model"], str), f"model must be a string, got: {type(payload['model'])}"


def test_model_field__present_when_omitted_from_request_streaming() -> None:
    """model must be present in SSE response.created / response.completed events when request omits it."""
    client = _build_client()

    with client.stream("POST", "/responses", json={"input": "hello", "stream": True}) as resp:
        assert resp.status_code == 200
        events: list[dict[str, Any]] = []
        for line in resp.iter_lines():
            if line.startswith("data: "):
                import json

                events.append(json.loads(line[len("data: ") :]))

    # Check the terminal event (response.completed or response.failed)
    terminal = [e for e in events if e.get("type", "").startswith("response.completed")]
    assert len(terminal) >= 1, f"Expected response.completed event, got types: {[e.get('type') for e in events]}"
    response_obj = terminal[0].get("response", {})
    assert "model" in response_obj, "model field must be present in streaming response.completed event"
    assert isinstance(response_obj["model"], str), f"model must be a string, got: {type(response_obj['model'])}"


# ══════════════════════════════════════════════════════════
# B8: ResponseError shape (only code + message, no type/param)
# ══════════════════════════════════════════════════════════


def test_response_error__shape_has_only_code_and_message() -> None:
    """B8 — The error field on a failed response has code and message but NOT type or param."""
    client = _build_client(_throwing_handler)

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

    _wait_for_status(client, response_id, "failed")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    payload = get_response.json()
    error = payload.get("error")
    assert error is not None, "error field must be present on a failed response"
    assert isinstance(error, dict)
    # ResponseError shape: MUST have code and message
    assert "code" in error, f"error must have 'code' field, got: {list(error.keys())}"
    assert "message" in error, f"error must have 'message' field, got: {list(error.keys())}"
    # ResponseError shape: must NOT have type or param (those are for request errors)
    assert "type" not in error, (
        f"error must NOT have 'type' field (that is for request errors), got: {list(error.keys())}"
    )
    assert "param" not in error, (
        f"error must NOT have 'param' field (that is for request errors), got: {list(error.keys())}"
    )


# ══════════════════════════════════════════════════════════
# B12: GET /responses/{id} returns 200 for all terminal statuses
# ══════════════════════════════════════════════════════════


def test_get__returns_200_for_failed_response() -> None:
    """B12 — GET returns HTTP 200 for a response in failed status."""
    client = _build_client(_throwing_handler)

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
    _wait_for_status(client, response_id, "failed")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "failed"


def test_get__returns_200_for_incomplete_response() -> None:
    """B12 — GET returns HTTP 200 for a response in incomplete status."""
    client = _build_client(_incomplete_handler)

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
    _wait_for_status(client, response_id, "incomplete")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "incomplete"


def test_get__returns_200_for_cancelled_response() -> None:
    """B12 — GET returns HTTP 200 for a response in cancelled status."""
    client = _build_client(_cancellable_bg_handler)

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

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 200
    _wait_for_status(client, response_id, "cancelled")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "cancelled"


# ════════════════════════════════════════════════════════
# N-8, B6: error=null for non-failed terminal statuses
# ════════════════════════════════════════════════════════


def test_error_field__null_for_completed_status() -> None:
    """B6 — error must be null for status=completed."""
    client = _build_client()

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
    assert payload.get("error") is None, "B6: error must be null for status=completed"


def test_error_field__null_for_cancelled_status() -> None:
    """B6 — error must be null for status=cancelled."""
    client = _build_client(_cancellable_bg_handler)

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

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 200
    _wait_for_status(client, response_id, "cancelled")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["status"] == "cancelled"
    assert payload.get("error") is None, "B6: error must be null for status=cancelled"


# ════════════════════════════════════════════════════════
# N-1, N-2, B20/B21: response_id and agent_reference on output items
# ════════════════════════════════════════════════════════


def _output_item_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits a single output message item."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_in_progress()

        message_item = stream.add_output_item_message()
        yield message_item.emit_added()

        text_content = message_item.add_text_content()
        yield text_content.emit_added()
        yield text_content.emit_delta("hi")
        yield text_content.emit_text_done()
        yield text_content.emit_done()
        yield message_item.emit_done()

        yield stream.emit_completed()

    return _events()


def test_output_item__response_id_stamped_on_item() -> None:
    """B20 — Output items carry response_id stamped from the parent Response."""
    client = _build_client(_output_item_handler)

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
    assert len(payload.get("output", [])) == 1
    item = payload["output"][0]
    assert item.get("response_id") == payload["id"], (
        f"B20: response_id on output item must match parent Response id, got: {item!r}"
    )


def test_output_item__agent_reference_stamped_on_item() -> None:
    """B21 — agent_reference from the request is stamped on output items when the stream knows about it."""

    def _handler_with_agent_ref(request: Any, context: Any, cancellation_signal: Any):
        """Handler that creates a stream with agent_reference and emits a message item."""
        agent_ref = None
        if hasattr(request, "agent_reference") and request.agent_reference is not None:
            agent_ref_raw = request.agent_reference
            if hasattr(agent_ref_raw, "as_dict"):
                agent_ref = agent_ref_raw.as_dict()
            elif isinstance(agent_ref_raw, dict):
                agent_ref = agent_ref_raw

        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
                agent_reference=agent_ref,
            )
            yield stream.emit_created()
            yield stream.emit_in_progress()

            message_item = stream.add_output_item_message()
            yield message_item.emit_added()

            text_content = message_item.add_text_content()
            yield text_content.emit_added()
            yield text_content.emit_delta("hi")
            yield text_content.emit_text_done()
            yield text_content.emit_done()
            yield message_item.emit_done()

            yield stream.emit_completed()

        return _events()

    app = ResponsesAgentServerHost()
    app.response_handler(_handler_with_agent_ref)
    client = TestClient(app)

    agent_ref = {"type": "agent_reference", "name": "my-agent", "version": "v2"}

    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "agent_reference": agent_ref,
            "stream": False,
            "store": True,
            "background": False,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    # agent_reference is propagated to the Response
    assert payload.get("agent_reference", {}).get("name") == "my-agent"
    assert payload.get("agent_reference", {}).get("version") == "v2"
    # B21: agent_reference is also stamped on individual output items
    assert len(payload.get("output", [])) == 1
    item = payload["output"][0]
    assert item.get("agent_reference") is not None, (
        f"B21: agent_reference must be stamped on output items, got: {item!r}"
    )
    assert item["agent_reference"].get("name") == "my-agent"
    assert item["agent_reference"].get("version") == "v2"


# ════════════════════════════════════════════════════════
# N-3, B19: x-platform-server on SSE streaming responses
# ════════════════════════════════════════════════════════


def test_x_platform_server_header__present_on_sse_streaming_post_response() -> None:
    """B19 — x-platform-server header must be present on SSE streaming POST /responses."""
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
        header = response.headers.get("x-platform-server")

    assert header is not None, "B19: x-platform-server header must be present on SSE streaming POST per B19"
    assert isinstance(header, str) and len(header) > 0


def test_x_platform_server_header__present_on_sse_replay_get_response() -> None:
    """B19 — x-platform-server header must be present on GET ?stream=true replay."""
    import json as _json

    client = _build_client()

    # Create a background+stream response so SSE replay is available
    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": True,
        },
    ) as post_response:
        assert post_response.status_code == 200
        first_data: str | None = None
        for line in post_response.iter_lines():
            if line.startswith("data:"):
                first_data = line.split(":", 1)[1].strip()
                break
    assert first_data is not None
    response_id = _json.loads(first_data)["response"]["id"]

    with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_response:
        assert replay_response.status_code == 200
        header = replay_response.headers.get("x-platform-server")

    assert header is not None, "B19: x-platform-server header must be present on SSE replay GET per B19"
    assert isinstance(header, str) and len(header) > 0


# ══════════════════════════════════════════════════════════
# B14: x-platform-server header on 4xx error responses
# ══════════════════════════════════════════════════════════


def test_x_platform_server__present_on_400_create_error() -> None:
    """B14 — x-platform-server header must be present on 4xx error responses (not just 2xx)."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": "not-a-bool",  # invalid value → 400
        },
    )
    assert response.status_code == 400
    header = response.headers.get("x-platform-server")
    assert header is not None, "x-platform-server header must be present on 400 error responses per B14"


# ══════════════════════════════════════════════════════════
# B15: output[] preserved for completed, cleared for cancelled
# ══════════════════════════════════════════════════════════


def test_output__preserved_for_completed_response() -> None:
    """B15 — output[] is preserved (may be non-empty) for completed responses."""
    client = _build_client()

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
    # output must be present as a list (may be empty for noop handler, but must not be absent)
    assert "output" in payload, "output field must be present on completed response"
    assert isinstance(payload["output"], list), f"output must be a list, got: {type(payload['output'])}"


def test_output__cleared_for_cancelled_response() -> None:
    """B15 — output[] is cleared (empty list) when a response is cancelled."""
    client = _build_client(_cancellable_bg_handler)

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

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 200
    _wait_for_status(client, response_id, "cancelled")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload.get("output") == [], (
        f"output must be cleared (empty []) for cancelled responses, got: {payload.get('output')}"
    )


# ══════════════════════════════════════════════════════════
# StatusLifecycle: queued status round-trip
# (ported from StatusLifecycleTests.cs)
# ══════════════════════════════════════════════════════════


def _collect_sse_events(response: Any) -> list[dict[str, Any]]:
    """Collect SSE events from a streaming response."""
    import json as _json

    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None
    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                payload = _json.loads(current_data) if current_data else {}
                events.append({"type": current_type, "data": payload})
            current_type = None
            current_data = None
            continue
        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()
    if current_type is not None:
        payload = _json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": payload})
    return events


def _queued_then_completed_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits created(queued) → in_progress → completed."""

    async def _events():
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created(status="queued")
        yield stream.emit_in_progress()
        yield stream.emit_completed()

    return _events()


def test_streaming_queued_status_honoured_in_created_event() -> None:
    """Handler that sets queued status — the response.created SSE event must reflect status: 'queued'.

    Ported from StatusLifecycleTests.Streaming_QueuedStatus_HonouredInCreatedEvent.
    """
    client = _build_client(_queued_then_completed_handler)

    with client.stream(
        "POST",
        "/responses",
        json={"model": "test", "input": "hello", "stream": True},
    ) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    created = [e for e in events if e["type"] == "response.created"]
    assert created, "Expected response.created event"
    assert created[0]["data"]["response"]["status"] == "queued", (
        f"Expected queued status on response.created, got {created[0]['data']['response']['status']!r}"
    )


def test_background_queued_status_honoured_in_post_response() -> None:
    """Background mode: POST response body reflects status: 'queued' when handler sets it.

    Ported from StatusLifecycleTests.Background_QueuedStatus_HonouredInPostResponse.
    """

    def _queued_waiting_handler(request: Any, context: Any, cancellation_signal: Any):
        """Handler that emits created(queued), pauses, then in_progress → completed."""

        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created(status="queued")
            # Pause to ensure the bg POST response sees 'queued' status
            await asyncio.sleep(0.3)
            yield stream.emit_in_progress()
            yield stream.emit_completed()

        return _events()

    client = _build_client(_queued_waiting_handler)

    response = client.post(
        "/responses",
        json={"model": "test", "input": "hello", "background": True, "store": True},
    )
    assert response.status_code == 200
    payload = response.json()
    # Initial status must be queued (from the response.created event the handler emits)
    assert payload["status"] == "queued", (
        f"Expected queued status on background POST response, got {payload['status']!r}"
    )


def test_background_queued_status_eventually_completes() -> None:
    """Background queued response eventually transitions to status: 'completed' after handler finishes.

    Ported from StatusLifecycleTests.Background_QueuedStatus_EventuallyCompletes.
    """
    client = _build_client(_queued_then_completed_handler)

    response = client.post(
        "/responses",
        json={"model": "test", "input": "hello", "background": True, "store": True},
    )
    assert response.status_code == 200
    response_id = response.json()["id"]

    # Poll until the response reaches completed
    _wait_for_status(client, response_id, "completed", timeout_s=5.0)

    get = client.get(f"/responses/{response_id}")
    assert get.status_code == 200
    assert get.json()["status"] == "completed"
