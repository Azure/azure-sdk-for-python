# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for error source classification headers on HTTP responses.

These tests verify that the ``x-platform-error-source`` and
``x-platform-error-detail`` headers are set correctly on error and success
responses, matching the container image spec §8 error source classification.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.ai.agentserver.core._platform_headers import (
    ERROR_DETAIL,
    ERROR_SOURCE,
)
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.store._foundry_provider import FoundryStorageProvider
from azure.ai.agentserver.responses.store._foundry_settings import FoundryStorageSettings


async def _noop_handler(request: Any, context: Any, cancellation_signal: asyncio.Event) -> AsyncIterator[Any]:
    async def _events() -> AsyncIterator[Any]:
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None) or "")
        yield stream.emit_created()
        msg = stream.add_output_text_message()
        yield msg.emit_added()
        content = msg.add_text_content()
        yield content.emit_added()
        yield content.emit_text_done("hello")
        yield content.emit_done()
        yield msg.emit_done()
        yield stream.emit_completed()

    return _events()


async def _throwing_handler(request: Any, context: Any, cancellation_signal: asyncio.Event) -> AsyncIterator[Any]:
    async def _events() -> AsyncIterator[Any]:
        raise RuntimeError("Simulated handler failure")
        yield  # pragma: no cover

    return _events()


def _build_client(handler: Any = None) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler or _noop_handler)
    return TestClient(app)


class TestErrorSourceOnSuccessResponses:
    """Verify that successful responses do NOT include error source headers."""

    def test_success_create_no_error_source_header(self) -> None:
        client = _build_client()
        resp = client.post(
            "/responses",
            json={"model": "test", "input": "hello", "stream": False, "store": True, "background": False},
        )
        assert resp.status_code == 200
        assert ERROR_SOURCE not in resp.headers
        assert ERROR_DETAIL not in resp.headers

    def test_success_get_no_error_source_header(self) -> None:
        client = _build_client()
        create = client.post(
            "/responses",
            json={"model": "test", "input": "hello", "stream": False, "store": True, "background": False},
        )
        response_id = create.json()["id"]
        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert ERROR_SOURCE not in get_resp.headers


class TestErrorSourceOnValidationErrors:
    """Verify user errors get ``x-platform-error-source: user``."""

    def test_invalid_json_returns_user_error_source(self) -> None:
        client = _build_client()
        resp = client.post(
            "/responses",
            content=b"not json",
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 400
        assert resp.headers.get(ERROR_SOURCE) == "user"
        assert ERROR_DETAIL not in resp.headers

    def test_empty_body_returns_user_error_source(self) -> None:
        client = _build_client()
        resp = client.post(
            "/responses",
            content=b"",
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 400
        assert resp.headers.get(ERROR_SOURCE) == "user"

    def test_malformed_response_id_returns_user_error_source(self) -> None:
        client = _build_client()
        resp = client.get("/responses/totally-invalid-id")
        assert resp.status_code == 400
        assert resp.headers.get(ERROR_SOURCE) == "user"

    def test_not_found_returns_user_error_source(self) -> None:
        from azure.ai.agentserver.responses._id_generator import IdGenerator

        client = _build_client()
        valid_id = IdGenerator.new_response_id()
        resp = client.get(f"/responses/{valid_id}")
        assert resp.status_code == 404
        assert resp.headers.get(ERROR_SOURCE) == "user"

    def test_invalid_limit_returns_user_error_source(self) -> None:
        from azure.ai.agentserver.responses._id_generator import IdGenerator

        client = _build_client()
        valid_id = IdGenerator.new_response_id()
        resp = client.get(f"/responses/{valid_id}/input_items?limit=abc")
        assert resp.status_code == 400
        assert resp.headers.get(ERROR_SOURCE) == "user"


class TestErrorSourceOnUpstreamErrors:
    """Verify handler errors get ``x-platform-error-source: upstream``."""

    def test_sync_handler_exception_returns_upstream(self) -> None:
        client = _build_client(_throwing_handler)
        resp = client.post(
            "/responses",
            json={"model": "test", "input": "hello", "stream": False, "store": True, "background": False},
        )
        assert resp.status_code == 500
        assert resp.headers.get(ERROR_SOURCE) == "upstream"
        # Upstream errors should NOT include error detail
        assert ERROR_DETAIL not in resp.headers


class TestErrorSourceOnDraining:
    """Verify service unavailable gets ``x-platform-error-source: platform``."""

    def test_service_unavailable_returns_platform(self) -> None:
        """When the server is draining, it returns 503 with error_source=platform."""
        from azure.ai.agentserver.responses.hosting._validation import service_unavailable_response

        resp = service_unavailable_response("shutting down", {})
        assert resp.status_code == 503
        assert resp.headers[ERROR_SOURCE] == "platform"


@pytest.mark.parametrize("status", [401, 403])
@pytest.mark.parametrize(
    "route",
    [
        "create",
        "create_update",
        "create_background",
        "create_history",
        "create_history_stream",
        "get",
        "get_stream",
        "cancel",
        "delete",
        "delete_after_lookup",
        "input_items",
    ],
)
def test_foundry_access_errors_preserve_status_and_message(status: int, route: str) -> None:
    body = {"error": {"code": "AccessDenied", "message": "Public network access is disabled."}}
    storage_response = MagicMock()
    storage_response.status_code = status
    storage_response.text.return_value = json.dumps(body)
    provider = FoundryStorageProvider(
        credential=AsyncMock(),
        settings=FoundryStorageSettings(storage_base_url="https://foundry.example.com/storage/"),
    )
    provider._client.send_request = AsyncMock(return_value=storage_response)
    app = ResponsesAgentServerHost(store=provider)

    async def handler(request: Any, context: Any, cancellation_signal: asyncio.Event) -> AsyncIterator[Any]:
        async def events() -> AsyncIterator[Any]:
            stream = ResponseEventStream(response_id=context.response_id, model="test")
            yield stream.emit_created()
            yield stream.emit_completed()

        return events()

    app.response_handler(handler)
    client = TestClient(app)
    response_id = IdGenerator.new_response_id()
    if route in {"create_update", "delete_after_lookup"}:
        success = MagicMock()
        success.status_code = 200
        success.text.return_value = json.dumps(
            {"id": response_id, "status": "completed", "model": "test", "output": []}
        )
        provider._client.send_request.side_effect = [success, storage_response]

    if route.startswith("create"):
        payload: dict[str, Any] = {"response_id": response_id, "model": "test", "input": "hello", "store": True}
        if route == "create_background":
            payload["background"] = True
        if route.startswith("create_history"):
            payload["previous_response_id"] = response_id
            payload["stream"] = route.endswith("_stream")
        response = client.post("/responses", json=payload)
    elif route == "cancel":
        response = client.post(f"/responses/{response_id}/cancel")
    elif route.startswith("delete"):
        response = client.delete(f"/responses/{response_id}")
    else:
        suffix = {"get": "", "get_stream": "?stream=true", "input_items": "/input_items"}[route]
        response = client.get(f"/responses/{response_id}{suffix}")

    assert response.status_code == status
    assert response.json() == body
    assert response.headers[ERROR_SOURCE] == "user"
    assert ERROR_DETAIL not in response.headers
    if route in {"create", "create_background", "create_update"}:
        provider._client.send_request.side_effect = None
        followup = client.get(f"/responses/{response_id}")
        assert followup.status_code == status
