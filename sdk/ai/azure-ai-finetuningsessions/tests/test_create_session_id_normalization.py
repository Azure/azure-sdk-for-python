# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from __future__ import annotations

import json
import asyncio
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from azure.ai.finetuningsessions import _patch as _sync_patch
from azure.ai.finetuningsessions.aio import _patch as _aio_patch
from azure.ai.finetuningsessions.models import FromCheckpoint


class _FakeResponse:
    def __init__(self, status_code: int, body: dict[str, Any]) -> None:
        self.status_code = status_code
        self._body = body
        self.headers: dict[str, str] = {}

    def json(self) -> dict[str, Any]:
        return self._body

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise AssertionError(f"unexpected raise_for_status for {self.status_code}")


class _RecordingClient:
    def __init__(
        self,
        post_session_id: str,
        subsequent_responses: list[_FakeResponse] | None = None,
    ) -> None:
        self.requests: list[Any] = []
        responses = [
            _FakeResponse(200, {"session_id": post_session_id, "request_id": "req-1"}),
            _FakeResponse(200, {"status": "completed", "result": {}}),
        ]
        responses.extend(subsequent_responses or [])
        self._responses = iter(responses)
        self.sessions = _RecordingSessions(self)

    def send_request(self, req: Any) -> _FakeResponse:
        self.requests.append(req)
        return next(self._responses)


class _AsyncRecordingClient(_RecordingClient):
    async def send_request(self, req: Any, **kwargs: Any) -> _FakeResponse:
        self.requests.append(req)
        return next(self._responses)


class _RecordingSessions:
    def __init__(self, client: _RecordingClient) -> None:
        self._client = client

    def heartbeat(self, session_id: str, **kwargs: Any) -> _FakeResponse:
        request = _sync_patch._HttpRequest(
            "POST",
            f"{{endpoint}}/fine_tuning/sessions/{session_id}/heartbeat",
        )
        return self._client.send_request(request)


def test_sync_create_preserves_canonical_server_session_id() -> None:
    client = _RecordingClient("session_abc12345")

    with patch.object(_sync_patch.FineTuningSession, "_start_heartbeat", MagicMock()):
        session = _sync_patch.FineTuningSession.create(
            client,
            base_model="test-model",
            timeout_sec=1,
        )

    assert session.session_id == "session_abc12345"
    poll_req = client.requests[1]
    assert "/fine_tuning/sessions/session_abc12345/request/req-1" in poll_req.url


def test_sync_create_serializes_developer_tier_string() -> None:
    client = _RecordingClient("session_abc12345")

    with patch.object(_sync_patch.FineTuningSession, "_start_heartbeat", MagicMock()):
        _sync_patch.FineTuningSession.create(
            client,
            base_model="test-model",
            training_type="DeveloperTier",
            timeout_sec=1,
        )

    body = json.loads(client.requests[0].content)
    assert body["training_type"] == "DeveloperTier"


def test_sync_create_routes_legacy_server_session_id() -> None:
    client = _RecordingClient("model_abc12345")

    with patch.object(_sync_patch.FineTuningSession, "_start_heartbeat", MagicMock()):
        session = _sync_patch.FineTuningSession.create(
            client,
            base_model="test-model",
            timeout_sec=1,
        )

    assert session.session_id == "session_abc12345"
    poll_req = client.requests[1]
    assert "/fine_tuning/sessions/model_abc12345/request/req-1" in poll_req.url


def test_sync_create_normalizes_raw_server_session_id() -> None:
    client = _RecordingClient("abc12345")

    with patch.object(_sync_patch.FineTuningSession, "_start_heartbeat", MagicMock()):
        session = _sync_patch.FineTuningSession.create(
            client,
            base_model="test-model",
            timeout_sec=1,
        )

    assert session.session_id == "session_abc12345"
    poll_req = client.requests[1]
    assert "/fine_tuning/sessions/model_abc12345/request/req-1" in poll_req.url


async def test_async_create_preserves_canonical_server_session_id() -> None:
    client = _AsyncRecordingClient("session_abc12345")

    with patch.object(_aio_patch, "_start_heartbeat", MagicMock()):
        session_id = await _aio_patch.create_session(
            client,
            base_model="test-model",
            timeout_sec=1,
        )

    assert session_id == "session_abc12345"
    poll_req = client.requests[1]
    assert "/fine_tuning/sessions/session_abc12345/request/req-1" in poll_req.url


async def test_async_create_routes_legacy_server_session_id() -> None:
    client = _AsyncRecordingClient("model_abc12345")

    with patch.object(_aio_patch, "_start_heartbeat", MagicMock()):
        session_id = await _aio_patch.create_session(
            client,
            base_model="test-model",
            timeout_sec=1,
        )

    assert session_id == "session_abc12345"
    poll_req = client.requests[1]
    assert "/fine_tuning/sessions/model_abc12345/request/req-1" in poll_req.url


async def test_async_create_normalizes_raw_server_session_id() -> None:
    client = _AsyncRecordingClient("abc12345")

    with patch.object(_aio_patch, "_start_heartbeat", MagicMock()):
        session_id = await _aio_patch.create_session(
            client,
            base_model="test-model",
            timeout_sec=1,
        )

    assert session_id == "session_abc12345"
    poll_req = client.requests[1]
    assert "/fine_tuning/sessions/model_abc12345/request/req-1" in poll_req.url


@pytest.mark.parametrize(
    ("server_session_id", "resource_session_id"),
    [
        ("session_abc12345", "session_abc12345"),
        ("model_abc12345", "model_abc12345"),
        ("abc12345", "model_abc12345"),
    ],
)
def test_sync_post_create_operation_uses_server_resource_id(
    server_session_id: str,
    resource_session_id: str,
) -> None:
    client = _RecordingClient(
        server_session_id,
        [
            _FakeResponse(200, {"session_id": server_session_id, "request_id": "req-2"}),
            _FakeResponse(200, {"status": "completed", "result": {}}),
        ],
    )

    with patch.object(_sync_patch.FineTuningSession, "_start_heartbeat", MagicMock()):
        session = _sync_patch.FineTuningSession.create(
            client,
            base_model="test-model",
            timeout_sec=1,
        )
    session.save_weights("checkpoint-1")

    assert session.session_id == "session_abc12345"
    assert f"/fine_tuning/sessions/{resource_session_id}/checkpoint" in client.requests[2].url
    assert (
        f"/fine_tuning/sessions/{resource_session_id}/request/req-2"
        in client.requests[3].url
    )


@pytest.mark.parametrize(
    ("server_session_id", "resource_session_id"),
    [
        ("session_abc12345", "session_abc12345"),
        ("model_abc12345", "model_abc12345"),
        ("abc12345", "model_abc12345"),
    ],
)
async def test_async_post_create_operation_uses_server_resource_id(
    server_session_id: str,
    resource_session_id: str,
) -> None:
    client = _AsyncRecordingClient(
        server_session_id,
        [
            _FakeResponse(200, {"session_id": server_session_id, "request_id": "req-2"}),
            _FakeResponse(200, {"status": "completed", "result": {}}),
        ],
    )

    with patch.object(_aio_patch, "_start_heartbeat", MagicMock()):
        session_id = await _aio_patch.create_session(
            client,
            base_model="test-model",
            timeout_sec=1,
        )
    await _aio_patch.save_weights(client, session_id, "checkpoint-1")

    assert session_id == "session_abc12345"
    assert f"/fine_tuning/sessions/{resource_session_id}/checkpoint" in client.requests[2].url
    assert (
        f"/fine_tuning/sessions/{resource_session_id}/request/req-2"
        in client.requests[3].url
    )


@pytest.mark.parametrize(
    ("server_session_id", "resource_session_id"),
    [
        ("session_abc12345", "session_abc12345"),
        ("model_abc12345", "model_abc12345"),
        ("abc12345", "model_abc12345"),
    ],
)
def test_sync_post_create_close_uses_server_resource_id(
    server_session_id: str,
    resource_session_id: str,
) -> None:
    client = _RecordingClient(
        server_session_id,
        [_FakeResponse(200, {})],
    )

    with patch.object(_sync_patch.FineTuningSession, "_start_heartbeat", MagicMock()):
        session = _sync_patch.FineTuningSession.create(
            client,
            base_model="test-model",
            timeout_sec=1,
        )
    session.close()

    assert session._heartbeat_session_id == "session_abc12345"
    assert (
        f"/fine_tuning/sessions/{resource_session_id}/complete"
        in client.requests[2].url
    )


@pytest.mark.parametrize(
    ("server_session_id", "resource_session_id"),
    [
        ("session_abc12345", "session_abc12345"),
        ("model_abc12345", "model_abc12345"),
        ("abc12345", "model_abc12345"),
    ],
)
async def test_async_post_create_close_uses_server_resource_id(
    server_session_id: str,
    resource_session_id: str,
) -> None:
    client = _AsyncRecordingClient(
        server_session_id,
        [_FakeResponse(200, {})],
    )

    with patch.object(_aio_patch, "_start_heartbeat", MagicMock()) as start_heartbeat:
        session_id = await _aio_patch.create_session(
            client,
            base_model="test-model",
            timeout_sec=1,
        )
    await _aio_patch.close_session(client, session_id)

    start_heartbeat.assert_called_once_with(client, "session_abc12345")
    assert (
        f"/fine_tuning/sessions/{resource_session_id}/complete"
        in client.requests[2].url
    )


@pytest.mark.parametrize("server_session_id", ["model_abc12345", "abc12345"])
def test_sync_legacy_create_heartbeat_uses_server_resource_id(
    server_session_id: str,
) -> None:
    client = _RecordingClient(
        server_session_id,
        [_FakeResponse(200, {})],
    )

    with patch.object(_sync_patch.FineTuningSession, "_start_heartbeat", MagicMock()):
        session = _sync_patch.FineTuningSession.create(
            client,
            base_model="test-model",
            timeout_sec=1,
        )
    session.heartbeat()

    assert session.session_id == "session_abc12345"
    assert "/fine_tuning/sessions/model_abc12345/heartbeat" in client.requests[2].url


@pytest.mark.parametrize("server_session_id", ["model_abc12345", "abc12345"])
async def test_async_legacy_create_heartbeat_uses_server_resource_id(
    server_session_id: str,
) -> None:
    client = _AsyncRecordingClient(
        server_session_id,
        [_FakeResponse(200, {})],
    )

    with patch.object(_aio_patch, "_start_heartbeat", MagicMock()):
        session_id = await _aio_patch.create_session(
            client,
            base_model="test-model",
            timeout_sec=1,
        )

    _aio_patch._start_heartbeat(client, session_id, interval_sec=0)
    for _ in range(10):
        if len(client.requests) >= 3:
            break
        await asyncio.sleep(0)
    _aio_patch._stop_heartbeat(client, session_id)
    await asyncio.sleep(0)

    assert session_id == "session_abc12345"
    assert list(client._heartbeat_tasks) == []
    assert "/fine_tuning/sessions/model_abc12345/heartbeat" in client.requests[2].url


def test_sync_create_serializes_checkpoint_source_as_session_id() -> None:
    client = _RecordingClient("session_abc12345")

    with patch.object(_sync_patch.FineTuningSession, "_start_heartbeat", MagicMock()):
        _sync_patch.FineTuningSession.create(
            client,
            base_model="test-model",
            from_checkpoint=FromCheckpoint(
                source_session_id="model_deadbeef",
                checkpoint_id="checkpoint-1",
            ),
            timeout_sec=1,
        )

    body = json.loads(client.requests[0].content)
    assert body["from_checkpoint"]["source_session_id"] == "session_deadbeef"


def test_sync_create_from_checkpoint_canonicalizes_result_path_source_session_id() -> None:
    client = _RecordingClient("session_abc12345")

    with patch.object(_sync_patch.FineTuningSession, "_start_heartbeat", MagicMock()):
        _sync_patch.FineTuningSession.create_from_checkpoint(
            client,
            checkpoint_path="loom://model_deadbeef/weights/checkpoint-1",
            base_model="test-model",
            timeout_sec=1,
        )

    body = json.loads(client.requests[0].content)
    assert body["from_checkpoint"] == {
        "source_session_id": "session_deadbeef",
        "checkpoint_id": "checkpoint-1",
    }


async def test_async_create_from_checkpoint_canonicalizes_result_path_source_session_id() -> None:
    client = _AsyncRecordingClient("session_abc12345")

    with patch.object(_aio_patch, "_start_heartbeat", MagicMock()):
        await _aio_patch.create_session_from_checkpoint(
            client,
            checkpoint_path="loom://model_deadbeef/weights/checkpoint-1",
            base_model="test-model",
            timeout_sec=1,
        )

    body = json.loads(client.requests[0].content)
    assert body["from_checkpoint"] == {
        "source_session_id": "session_deadbeef",
        "checkpoint_id": "checkpoint-1",
    }


async def test_async_create_serializes_checkpoint_source_as_session_id() -> None:
    client = _AsyncRecordingClient("session_abc12345")

    with patch.object(_aio_patch, "_start_heartbeat", MagicMock()):
        await _aio_patch.create_session(
            client,
            base_model="test-model",
            from_checkpoint=FromCheckpoint(
                source_session_id="model_deadbeef",
                checkpoint_id="checkpoint-1",
            ),
            timeout_sec=1,
        )

    body = json.loads(client.requests[0].content)
    assert body["from_checkpoint"]["source_session_id"] == "session_deadbeef"
