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
        yield {"type": "response.created", "payload": {"status": "in_progress", "output": []}}
        while not cancellation_signal.is_set():
            await asyncio.sleep(0.01)

    return _events()


def _build_client(handler: Any | None = None) -> TestClient:
    app = ResponsesAgentServerHost()
    app.create_handler(handler or _noop_handler)
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
# B-7: created_at present on every response
# ══════════════════════════════════════════════════════════


def test_created_at__present_on_sync_response() -> None:
    """B-7 — created_at field must be present (and numeric) on every response object."""
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
    """B-7 — created_at is also present when fetching a background response via GET."""
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
# B-8: ResponseError shape (only code + message, no type/param)
# ══════════════════════════════════════════════════════════


def test_response_error__shape_has_only_code_and_message() -> None:
    """B-8 — The error field on a failed response has code and message but NOT type or param."""
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
    assert "type" not in error, f"error must NOT have 'type' field (that is for request errors), got: {list(error.keys())}"
    assert "param" not in error, f"error must NOT have 'param' field (that is for request errors), got: {list(error.keys())}"


# ══════════════════════════════════════════════════════════
# B-12: GET /responses/{id} returns 200 for all terminal statuses
# ══════════════════════════════════════════════════════════


def test_get__returns_200_for_failed_response() -> None:
    """B-12 — GET returns HTTP 200 for a response in failed status."""
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
    """B-12 — GET returns HTTP 200 for a response in incomplete status."""
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
    """B-12 — GET returns HTTP 200 for a response in cancelled status."""
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
        yield text_content.emit_done()
        yield message_item.emit_content_done(text_content)
        yield message_item.emit_done()

        yield stream.emit_completed()

    return _events()


def test_output_item__no_response_id_on_item() -> None:
    """Output items do not carry response_id — that field belongs on the Response only."""
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
    assert "response_id" not in item, (
        f"response_id must not appear on output items (belongs on Response only), got: {item!r}"
    )


def test_output_item__agent_reference_on_response_not_item() -> None:
    """agent_reference from the request is present on the Response but not on individual output items."""
    app = ResponsesAgentServerHost()
    app.create_handler(_output_item_handler)
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
    # agent_reference does NOT appear on individual output items
    assert len(payload.get("output", [])) == 1
    item = payload["output"][0]
    assert "agent_reference" not in item, (
        f"agent_reference must not appear on output items (belongs on Response only), got: {item!r}"
    )


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
# B-14: x-platform-server header on 4xx error responses
# ══════════════════════════════════════════════════════════


def test_x_platform_server__present_on_400_create_error() -> None:
    """B-14 — x-platform-server header must be present on 4xx error responses (not just 2xx)."""
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
# B-15: output[] preserved for completed, cleared for cancelled
# ══════════════════════════════════════════════════════════


def test_output__preserved_for_completed_response() -> None:
    """B-15 — output[] is preserved (may be non-empty) for completed responses."""
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
    """B-15 — output[] is cleared (empty list) when a response is cancelled."""
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
