# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for POST /responses endpoint behavior."""

from __future__ import annotations

from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from tests._helpers import poll_until


def _noop_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler used to wire the hosting surface in contract tests."""

    async def _events():
        if False:  # pragma: no cover - required to keep async-generator shape.
            yield None

    return _events()


def _build_client() -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(_noop_response_handler)
    return TestClient(app)


def test_create__returns_json_response_for_non_streaming_success() -> None:
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
    assert isinstance(payload.get("id"), str)
    assert payload["id"].startswith("caresp_")
    assert payload.get("response_id") == payload.get("id")
    # agent_reference may be empty/absent when the request doesn't include one
    agent_ref = payload.get("agent_reference")
    assert agent_ref is None or isinstance(agent_ref, dict)
    assert payload.get("object") == "response"
    assert payload.get("status") in {"completed", "in_progress", "queued"}
    assert "sequence_number" not in payload


def test_create__preserves_client_supplied_identity_fields() -> None:
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "response_id": "caresp_1234567890abcdef00ABCDEFGHIJKLMNOPQRSTUVWXYZ012345",
            "agent_reference": {
                "type": "agent_reference",
                "name": "custom-agent",
                "version": "v1",
            },
            "stream": False,
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload.get("id") == "caresp_1234567890abcdef00ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
    assert payload.get("response_id") == "caresp_1234567890abcdef00ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
    assert payload.get("agent_reference") == {
        "type": "agent_reference",
        "name": "custom-agent",
        "version": "v1",
    }


def test_create__rejects_invalid_response_id_format() -> None:
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "response_id": "bad-id",
            "stream": False,
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"].get("type") == "invalid_request_error"
    assert payload["error"].get("param") == "response_id"


def test_create__rejects_invalid_agent_reference_shape() -> None:
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "agent_reference": {"type": "not_agent_reference", "name": "bad"},
            "stream": False,
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"].get("type") == "invalid_request_error"
    assert payload["error"].get("param") == "agent_reference.type"


def test_create__returns_structured_400_for_invalid_payload() -> None:
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "background": True,
            "store": False,
        },
    )

    assert response.status_code == 400
    payload = response.json()
    error = payload.get("error")
    assert isinstance(error, dict)
    assert error.get("type") == "invalid_request_error"


def test_create__store_false_response_is_not_visible_via_get() -> None:
    client = _build_client()

    create_response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": False,
            "background": False,
        },
    )

    assert create_response.status_code == 200
    response_id = create_response.json()["id"]

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 404


def test_create__background_mode_returns_immediate_then_reaches_terminal_state() -> None:
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
    created_payload = create_response.json()
    # Phase 3: handler runs immediately, so POST may return completed when the
    # noop handler finishes quickly in the TestClient synchronous context.
    assert created_payload.get("status") in {"queued", "in_progress", "completed"}
    response_id = created_payload["id"]

    latest_snapshot: dict[str, Any] = {}

    def _is_terminal() -> bool:
        nonlocal latest_snapshot
        snapshot_response = client.get(f"/responses/{response_id}")
        if snapshot_response.status_code != 200:
            return False
        latest_snapshot = snapshot_response.json()
        return latest_snapshot.get("status") in {"completed", "failed", "incomplete", "cancelled"}

    ok, failure = poll_until(
        _is_terminal,
        timeout_s=5.0,
        interval_s=0.05,
        context_provider=lambda: {"last_status": latest_snapshot.get("status")},
        label="background create terminal transition",
    )
    assert ok, failure


def test_create__non_stream_returns_completed_response_with_output_items() -> None:
    from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

    def _output_producing_handler(request: Any, context: Any, cancellation_signal: Any):
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
    app.response_handler(_output_producing_handler)
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
    assert payload.get("status") == "completed"
    assert "sequence_number" not in payload
    assert isinstance(payload.get("output"), list)
    assert len(payload["output"]) == 1
    assert payload["output"][0].get("type") == "message"
    assert payload["output"][0].get("content", [])[0].get("type") == "output_text"
    assert payload["output"][0].get("content", [])[0].get("text") == "hello"


def test_create__background_non_stream_get_eventually_returns_output_items() -> None:
    from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

    def _output_producing_handler(request: Any, context: Any, cancellation_signal: Any):
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
    app.response_handler(_output_producing_handler)
    client = TestClient(app)

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

    latest_snapshot: dict[str, Any] = {}

    def _is_completed_with_output() -> bool:
        nonlocal latest_snapshot
        snapshot_response = client.get(f"/responses/{response_id}")
        if snapshot_response.status_code != 200:
            return False
        latest_snapshot = snapshot_response.json()
        output = latest_snapshot.get("output")
        return latest_snapshot.get("status") == "completed" and isinstance(output, list) and len(output) == 1

    ok, failure = poll_until(
        _is_completed_with_output,
        timeout_s=5.0,
        interval_s=0.05,
        context_provider=lambda: {
            "last_status": latest_snapshot.get("status"),
            "last_output_count": len(latest_snapshot.get("output", []))
            if isinstance(latest_snapshot.get("output"), list)
            else None,
        },
        label="background non-stream output availability",
    )
    assert ok, failure

    assert latest_snapshot["output"][0].get("type") == "message"
    assert latest_snapshot["output"][0].get("content", [])[0].get("type") == "output_text"
    assert latest_snapshot["output"][0].get("content", [])[0].get("text") == "hello"
    assert "sequence_number" not in latest_snapshot


def test_create__model_is_optional_and_resolved_to_empty_or_default() -> None:
    """B22 — model can be omitted. Resolution: request.model → default_model → empty string."""
    client = _build_client()

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
    payload = response.json()
    # B22: model should be present (possibly empty string or server default)
    assert "model" in payload
    assert isinstance(payload["model"], str)


def test_create__metadata_rejects_more_than_16_keys() -> None:
    """Metadata constraints: max 16 key-value pairs."""
    client = _build_client()

    metadata = {f"key_{i}": f"value_{i}" for i in range(17)}
    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "metadata": metadata,
            "stream": False,
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["type"] == "invalid_request_error"


def test_create__metadata_rejects_key_longer_than_64_chars() -> None:
    """Metadata constraints: key max 64 characters."""
    client = _build_client()

    metadata = {"a" * 65: "value"}
    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "metadata": metadata,
            "stream": False,
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["type"] == "invalid_request_error"


def test_create__metadata_rejects_value_longer_than_512_chars() -> None:
    """Metadata constraints: value max 512 characters."""
    client = _build_client()

    metadata = {"key": "v" * 513}
    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "metadata": metadata,
            "stream": False,
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"]["type"] == "invalid_request_error"


def test_create__validation_error_includes_details_array() -> None:
    """B29 — Invalid request returns 400 with details[] array."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": "not-a-bool",
            "store": True,
            "background": False,
        },
    )

    assert response.status_code == 400
    payload = response.json()
    error = payload.get("error")
    assert error is not None
    assert error.get("type") == "invalid_request_error"
    # B29: should have details[] array
    details = error.get("details")
    assert isinstance(details, list), f"Expected details[] array per B29, got: {type(details)}"
    assert len(details) >= 1
    for detail in details:
        assert detail.get("type") == "invalid_request_error"
        assert detail.get("code") == "invalid_value"
        assert "param" in detail
        assert "message" in detail


# ══════════════════════════════════════════════════════════
# B1, B2, B3: Request body edge cases
# ══════════════════════════════════════════════════════════


def test_create__returns_400_for_empty_body() -> None:
    """B1 — Empty request body → HTTP 400, error.type: invalid_request_error."""
    client = _build_client()

    response = client.post(
        "/responses",
        content=b"",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    payload = response.json()
    assert isinstance(payload.get("error"), dict)
    assert payload["error"].get("type") == "invalid_request_error"


def test_create__returns_400_for_invalid_json_body() -> None:
    """B2 — Malformed JSON body → HTTP 400, error.type: invalid_request_error."""
    client = _build_client()

    response = client.post(
        "/responses",
        content=b"{invalid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    payload = response.json()
    assert isinstance(payload.get("error"), dict)
    assert payload["error"].get("type") == "invalid_request_error"


def test_create__ignores_unknown_fields_in_request_body() -> None:
    """B3 — Unknown fields are ignored for forward compatibility → HTTP 200."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
            "foo": "bar",
            "unknown_nested": {"key": "value"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload.get("object") == "response"


# ══════════════════════════════════════════════════════════
# Task 4.1 — _process_handler_events sync contract tests
# ══════════════════════════════════════════════════════════


def test_sync_handler_exception_returns_500() -> None:
    """T5 — Handler raises an exception; stream=False → HTTP 500.

    B8 / B13 for sync mode: any handler exception surfaces as HTTP 500.
    """

    def _raising_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            raise RuntimeError("Simulated handler failure")
            if False:  # pragma: no cover
                yield None

        return _events()

    _app = ResponsesAgentServerHost()
    _app.response_handler(_raising_handler)
    client = TestClient(_app, raise_server_exceptions=False)

    response = client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": False, "store": True, "background": False},
    )

    assert response.status_code == 500


def test_sync_no_terminal_event_still_completes() -> None:
    """T6 — Handler yields response.created + response.in_progress but no terminal.

    stream=False → HTTP 200, status=failed.

    S-015: When the handler completes without emitting a terminal event, the library
    synthesises a ``response.failed`` terminal.  Sync callers receive HTTP 200 with
    a "failed" response body (not HTTP 500).
    """
    from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

    def _no_terminal_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
            yield stream.emit_created()
            yield stream.emit_in_progress()
            # Intentionally omit terminal event (response.completed / response.failed)

        return _events()

    _app = ResponsesAgentServerHost()
    _app.response_handler(_no_terminal_handler)
    client = TestClient(_app)

    response = client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": False, "store": True, "background": False},
    )

    assert response.status_code == 200, (
        f"S-015: sync no-terminal handler must return HTTP 200, got {response.status_code}"
    )
    payload = response.json()
    assert payload.get("status") == "failed", (
        f"S-015: synthesised terminal must set status to 'failed', got {payload.get('status')!r}"
    )


# ══════════════════════════════════════════════════════════
# Phase 5 — Task 5.1: FR-006 / FR-007 first-event contract first-event contract tests
# ══════════════════════════════════════════════════════════


def test_s007_wrong_first_event_sync() -> None:
    """T1 — Handler yields response.in_progress as first event; stream=False → HTTP 500.

    FR-006: The first event MUST be response.created.  Violations are treated as
    pre-creation errors (B8) and map to HTTP 500 in sync mode.
    Uses a raw dict to bypass ResponseEventStream internal ordering validation so
    the orchestrator's _check_first_event_contract is the authority under test.
    """

    def _wrong_first_event_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            # Raw dict bypasses ResponseEventStream validation so _check_first_event_contract runs
            yield {
                "type": "response.in_progress",
                "response": {
                    "status": "in_progress",
                    "object": "response",
                },
            }

        return _events()

    _app = ResponsesAgentServerHost()
    _app.response_handler(_wrong_first_event_handler)
    client = TestClient(_app, raise_server_exceptions=False)

    response = client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": False, "store": True, "background": False},
    )

    assert response.status_code == 500, (
        f"FR-006 violation in sync mode must return HTTP 500, got {response.status_code}"
    )


def test_s007_wrong_first_event_stream() -> None:
    """T2 — Handler yields response.in_progress as first event; stream=True → SSE contains only 'error'.

    FR-006: Violation → single standalone error event; no response.created in stream.
    Uses a raw dict to bypass ResponseEventStream internal ordering validation.
    """

    def _wrong_first_event_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            yield {
                "type": "response.in_progress",
                "response": {
                    "status": "in_progress",
                    "object": "response",
                },
            }

        return _events()

    _app = ResponsesAgentServerHost()
    _app.response_handler(_wrong_first_event_handler)
    client = TestClient(_app, raise_server_exceptions=False)

    import json as _json

    events: list[dict[str, Any]] = []
    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": False},
    ) as response:
        assert response.status_code == 200
        current_type: str | None = None
        current_data: str | None = None
        for line in response.iter_lines():
            if not line:
                if current_type is not None:
                    events.append({"type": current_type, "data": _json.loads(current_data) if current_data else {}})
                current_type = None
                current_data = None
                continue
            if line.startswith("event:"):
                current_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                current_data = line.split(":", 1)[1].strip()
        if current_type is not None:
            events.append({"type": current_type, "data": _json.loads(current_data) if current_data else {}})

    event_types = [e["type"] for e in events]
    assert event_types == ["error"], (
        f"FR-006 violation in stream mode must produce exactly ['error'], got: {event_types}"
    )
    assert "response.created" not in event_types


def test_s008_mismatched_id_stream() -> None:
    """T3 — Handler yields response.created with wrong id; stream=True → SSE contains only 'error'.

    FR-006b: The id in response.created MUST equal the library-assigned response_id.
    """

    def _mismatched_id_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            # Emit response.created with a deliberately wrong id
            yield {
                "type": "response.created",
                "response": {
                    "id": "caresp_WRONG00000000000000000000000000000000000000000000",
                    "response_id": "caresp_WRONG00000000000000000000000000000000000000000000",
                    "status": "queued",
                    "object": "response",
                },
            }

        return _events()

    _app = ResponsesAgentServerHost()
    _app.response_handler(_mismatched_id_handler)
    client = TestClient(_app, raise_server_exceptions=False)

    import json as _json

    events: list[dict[str, Any]] = []
    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": False},
    ) as response:
        assert response.status_code == 200
        current_type: str | None = None
        current_data: str | None = None
        for line in response.iter_lines():
            if not line:
                if current_type is not None:
                    events.append({"type": current_type, "data": _json.loads(current_data) if current_data else {}})
                current_type = None
                current_data = None
                continue
            if line.startswith("event:"):
                current_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                current_data = line.split(":", 1)[1].strip()
        if current_type is not None:
            events.append({"type": current_type, "data": _json.loads(current_data) if current_data else {}})

    event_types = [e["type"] for e in events]
    assert event_types == ["error"], f"FR-006b violation must produce exactly ['error'], got: {event_types}"


def test_s009_terminal_status_on_created_stream() -> None:
    """T4 — Handler yields response.created with terminal status; stream=True → SSE contains only 'error'.

    FR-007: The status in response.created MUST be non-terminal (queued or in_progress).
    """

    def _terminal_on_created_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            yield {
                "type": "response.created",
                "response": {
                    "status": "completed",
                    "object": "response",
                },
            }

        return _events()

    _app = ResponsesAgentServerHost()
    _app.response_handler(_terminal_on_created_handler)
    client = TestClient(_app, raise_server_exceptions=False)

    import json as _json

    events: list[dict[str, Any]] = []
    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": False},
    ) as response:
        assert response.status_code == 200
        current_type: str | None = None
        current_data: str | None = None
        for line in response.iter_lines():
            if not line:
                if current_type is not None:
                    events.append({"type": current_type, "data": _json.loads(current_data) if current_data else {}})
                current_type = None
                current_data = None
                continue
            if line.startswith("event:"):
                current_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                current_data = line.split(":", 1)[1].strip()
        if current_type is not None:
            events.append({"type": current_type, "data": _json.loads(current_data) if current_data else {}})

    event_types = [e["type"] for e in events]
    assert event_types == ["error"], f"FR-007 violation must produce exactly ['error'], got: {event_types}"


def test_s007_valid_handler_not_affected() -> None:
    """T5 — Compliant handler emits response.created with correct id; stream=True → normal SSE flow.

    Regression: the FR-006/FR-007 validation must not block valid handlers.
    """
    from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

    def _compliant_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
            yield stream.emit_created()
            yield stream.emit_completed()

        return _events()

    _app = ResponsesAgentServerHost()
    _app.response_handler(_compliant_handler)
    client = TestClient(_app)

    import json as _json

    events: list[dict[str, Any]] = []
    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": False},
    ) as response:
        assert response.status_code == 200
        current_type: str | None = None
        current_data: str | None = None
        for line in response.iter_lines():
            if not line:
                if current_type is not None:
                    events.append({"type": current_type, "data": _json.loads(current_data) if current_data else {}})
                current_type = None
                current_data = None
                continue
            if line.startswith("event:"):
                current_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                current_data = line.split(":", 1)[1].strip()
        if current_type is not None:
            events.append({"type": current_type, "data": _json.loads(current_data) if current_data else {}})

    event_types = [e["type"] for e in events]
    assert "response.created" in event_types, (
        f"Compliant handler must not be blocked; expected response.created in: {event_types}"
    )
    assert "error" not in event_types, f"Compliant handler must not produce error event; got: {event_types}"
