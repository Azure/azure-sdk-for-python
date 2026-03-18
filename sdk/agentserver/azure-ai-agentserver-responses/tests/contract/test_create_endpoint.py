"""Contract tests for POST /responses endpoint behavior."""

from __future__ import annotations

from typing import Any

from starlette.applications import Starlette
from starlette.testclient import TestClient

from tests._helpers import poll_until

from azure.ai.agentserver.responses._hosting import map_responses_server


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
    assert payload.get("response_id") == payload.get("id")
    assert isinstance(payload.get("agent_reference"), dict)
    assert payload["agent_reference"].get("type") == "agent_reference"
    assert isinstance(payload["agent_reference"].get("name"), str)
    assert payload.get("object") == "response"
    assert payload.get("status") in {"completed", "in_progress", "queued"}


def test_create__preserves_client_supplied_identity_fields() -> None:
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "response_id": "resp_custom_identity_12345",
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
    assert payload.get("id") == "resp_custom_identity_12345"
    assert payload.get("response_id") == "resp_custom_identity_12345"
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
