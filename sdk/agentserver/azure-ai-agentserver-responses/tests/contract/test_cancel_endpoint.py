"""Contract tests for POST /responses/{response_id}/cancel behavior."""

from __future__ import annotations

from typing import Any

from starlette.applications import Starlette
from starlette.testclient import TestClient

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


def test_cancel__cancels_background_in_progress_response() -> None:
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

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 200
    payload = cancel_response.json()
    assert payload.get("status") == "cancelled"


def test_cancel__is_idempotent_for_already_cancelled_response() -> None:
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

    first_cancel = client.post(f"/responses/{response_id}/cancel")
    assert first_cancel.status_code == 200
    second_cancel = client.post(f"/responses/{response_id}/cancel")
    assert second_cancel.status_code == 200
    assert second_cancel.json().get("status") == "cancelled"


def test_cancel__returns_error_for_terminal_response() -> None:
    client = _build_client()

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
    response_id = create_response.json()["id"]

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 400
    payload = cancel_response.json()
    assert isinstance(payload.get("error"), dict)
    assert payload["error"].get("type") == "invalid_request_error"


def test_cancel__returns_404_for_unknown_response_id() -> None:
    client = _build_client()

    cancel_response = client.post("/responses/resp_does_not_exist/cancel")
    assert cancel_response.status_code == 404
    payload = cancel_response.json()
    assert isinstance(payload.get("error"), dict)
