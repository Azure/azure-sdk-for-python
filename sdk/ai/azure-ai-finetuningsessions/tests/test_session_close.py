# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Session close preserves typed terminal errors and generic HTTP failures."""

import json
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest
from azure.core.exceptions import HttpResponseError

from azure.ai.finetuningsessions import FineTuningSession, TrainingEngineError
from azure.ai.finetuningsessions.aio import _patch as aio_patch


class Response:
    def __init__(self, status: int, body: Any, *, invalid_json: bool = False) -> None:
        self.status_code = status
        self.reason = "offline close fixture"
        self.headers: dict[str, str] = {}
        self._body = body
        self.invalid_json = invalid_json
        self.json_calls = 0

    def json(self) -> Any:
        self.json_calls += 1
        if self.invalid_json:
            raise ValueError("Invalid JSON")
        return self._body

    def text(self) -> str:
        return json.dumps(self._body)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HttpResponseError(response=self)


class RecordingClient:
    def __init__(self, response: Response) -> None:
        self.response = response
        self.requests: list[Any] = []

    def send_request(self, request: Any) -> Response:
        self.requests.append(request)
        return self.response


class AsyncRecordingClient(RecordingClient):
    async def send_request(self, request: Any) -> Response:
        return super().send_request(request)


@pytest.fixture(params=[RecordingClient, AsyncRecordingClient], ids=["sync", "async"])
def client(request, monkeypatch):
    monkeypatch.setattr(FineTuningSession, "_start_heartbeat", lambda *_: None)
    return request.param(Response(200, {}))


async def close(client, session_id: str = "session_12345678") -> None:
    if isinstance(client, AsyncRecordingClient):
        await aio_patch.close_session(client, session_id)
    else:
        FineTuningSession(client, session_id=session_id).close()


@pytest.mark.parametrize("status", [200, 204])
async def test_close_success_preserves_request_and_return_value(client, status: int) -> None:
    client.response = Response(status, None, invalid_json=True)
    assert await close(client) is None
    assert client.response.json_calls == 0
    [request] = client.requests
    assert request.method == "POST"
    assert urlsplit(request.url).path == "{endpoint}/fine_tuning/sessions/session_12345678/complete"
    assert parse_qs(urlsplit(request.url).query) == {"api-version": ["v1"]}
    assert request.headers["Foundry-Features"] == "FineTuningSessions=V1Preview"


@pytest.mark.parametrize("status", [409, 500])
@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize(
    "session_id,resource_id",
    [
        ("session_12345678", "session_12345678"),
        ("model_12345678", "model_12345678"),
        ("12345678", "model_12345678"),
    ],
)
async def test_close_engine_dead_preserves_identity_and_diagnostics(
    client, status: int, nested: bool, session_id: str, resource_id: str
) -> None:
    detail = {
        "reason": "engine_dead",
        "error_code": "engine_dead",
        "failure_reason": "lease expired",
        "message": "The training engine stopped",
        "debug_ref": "support-reference",
    }
    client.response = Response(status, {"detail": detail} if nested else detail)
    if isinstance(client, AsyncRecordingClient):
        aio_patch._ensure_async_state(client)
        client._session_resource_ids["session_12345678"] = resource_id

    with pytest.raises(TrainingEngineError) as caught:
        await close(client, session_id)

    assert caught.value.error_code == "engine_dead"
    assert caught.value.session_id == "session_12345678"
    assert caught.value.debug_ref == "support-reference"
    assert caught.value.response is client.response
    assert caught.value.status_code == status
    assert "completed training checkpoint" in caught.value.message
    [request] = client.requests
    assert urlsplit(request.url).path == f"{{endpoint}}/fine_tuning/sessions/{resource_id}/complete"


@pytest.mark.parametrize(
    "status,body",
    [
        (409, {"detail": {"reason": "model_busy", "message": "Model is busy"}}),
        (409, {"detail": "Conflict"}),
        (409, []),
        (409, None),
        (403, {"detail": "Forbidden"}),
        (404, {"detail": "Not found"}),
        (500, {"detail": "Internal server error"}),
    ],
)
async def test_close_unclassified_errors_still_raise(client, status: int, body: Any) -> None:
    client.response = Response(status, body)
    with pytest.raises(HttpResponseError) as caught:
        await close(client)
    assert not isinstance(caught.value, TrainingEngineError)
    assert caught.value.response is client.response
    assert caught.value.status_code == status
    assert len(client.requests) == 1


async def test_close_invalid_json_preserves_http_error(client) -> None:
    client.response = Response(409, None, invalid_json=True)
    with pytest.raises(HttpResponseError) as caught:
        await close(client)
    assert not isinstance(caught.value, TrainingEngineError)
    assert caught.value.status_code == 409
    assert len(client.requests) == 1


@pytest.mark.parametrize("code", ["worker_crashed", "engine_oom", "engine_timeout"])
async def test_close_other_typed_engine_errors_are_not_swallowed(client, code: str) -> None:
    client.response = Response(500, {"error_code": code, "message": "Request failed"})
    with pytest.raises(TrainingEngineError) as caught:
        await close(client)
    assert caught.value.error_code == code
    assert caught.value.session_id == "session_12345678"
    assert len(client.requests) == 1
