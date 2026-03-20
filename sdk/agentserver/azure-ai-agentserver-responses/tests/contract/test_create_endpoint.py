"""Contract tests for POST /responses endpoint behavior."""

from __future__ import annotations

from typing import Any

from starlette.applications import Starlette
from starlette.testclient import TestClient

from tests._helpers import poll_until

from azure.ai.agentserver.responses.hosting import map_responses_server


class _NoopResponseHandler:
    """Minimal handler used to wire the hosting surface in contract tests."""

    def create_async(self, request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            if False:  # pragma: no cover - required to keep async-generator shape.
                yield None

        return _events()


def _build_client() -> TestClient:
    app = Starlette()
    map_responses_server(app, _NoopResponseHandler())
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
    assert isinstance(payload.get("agent_reference"), dict)
    assert payload["agent_reference"].get("type") == "agent_reference"
    assert isinstance(payload["agent_reference"].get("name"), str)
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
    assert created_payload.get("status") in {"queued", "in_progress"}
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
    class _OutputProducingHandler:
        def create_async(self, request: Any, context: Any, cancellation_signal: Any):
            async def _events():
                from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

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

    app = Starlette()
    map_responses_server(app, _OutputProducingHandler())
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
    assert payload["output"][0].get("type") == "output_message"
    assert payload["output"][0].get("content", [])[0].get("type") == "output_text"
    assert payload["output"][0].get("content", [])[0].get("text") == "hello"


def test_create__background_non_stream_get_eventually_returns_output_items() -> None:
    class _OutputProducingHandler:
        def create_async(self, request: Any, context: Any, cancellation_signal: Any):
            async def _events():
                from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

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

    app = Starlette()
    map_responses_server(app, _OutputProducingHandler())
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

    assert latest_snapshot["output"][0].get("type") == "output_message"
    assert latest_snapshot["output"][0].get("content", [])[0].get("type") == "output_text"
    assert latest_snapshot["output"][0].get("content", [])[0].get("text") == "hello"
    assert "sequence_number" not in latest_snapshot
