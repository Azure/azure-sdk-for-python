# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for DELETE /responses/{response_id} endpoint behavior."""

from __future__ import annotations

import asyncio
from typing import Any

from starlette.applications import Starlette
from starlette.testclient import TestClient

from azure.ai.agentserver.responses.hosting import map_responses_server


class _NoopResponseHandler:
    """Minimal handler used to wire the hosting surface in contract tests."""

    def create_async(self, request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            if False:  # pragma: no cover - required to keep async-generator shape.
                yield None

        return _events()


class _DelayedResponseHandler:
    """Handler that keeps background execution in-flight for deterministic delete checks."""

    def create_async(self, request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            if cancellation_signal.is_set():
                return
            await asyncio.sleep(0.5)
            if cancellation_signal.is_set():
                return
            if False:  # pragma: no cover - required to keep async-generator shape.
                yield None

        return _events()


def _build_client(handler: Any | None = None) -> TestClient:
    app = Starlette()
    map_responses_server(app, handler or _NoopResponseHandler())
    return TestClient(app)


def test_delete__deletes_stored_completed_response() -> None:
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

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200
    payload = delete_response.json()
    assert payload.get("id") == response_id
    assert payload.get("object") == "response.deleted"
    assert payload.get("deleted") is True


def test_delete__returns_400_for_background_in_flight_response() -> None:
    client = _build_client(_DelayedResponseHandler())

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

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 400
    payload = delete_response.json()
    assert payload["error"].get("type") == "invalid_request_error"
    assert payload["error"].get("message") == "Cannot delete an in-flight response."


def test_delete__returns_404_for_unknown_response_id() -> None:
    client = _build_client()

    delete_response = client.delete("/responses/resp_does_not_exist")
    assert delete_response.status_code == 404
    payload = delete_response.json()
    assert payload["error"].get("type") == "invalid_request_error"


def test_delete__returns_404_for_store_false_response() -> None:
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

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 404
    payload = delete_response.json()
    assert payload["error"].get("type") == "invalid_request_error"


def test_delete__get_returns_400_after_deletion() -> None:
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

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 400
    payload = get_response.json()
    assert payload["error"].get("type") == "invalid_request_error"
    assert "deleted" in (payload["error"].get("message") or "").lower()


def test_delete__cancel_returns_404_after_deletion() -> None:
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

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 404
    payload = cancel_response.json()
    assert payload["error"].get("type") == "invalid_request_error"
