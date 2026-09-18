# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Tests for ``FineTuningSession.delete()`` and ``FineTuningSessionClient.delete_session()``.

Verifies:
* DELETE verb + URL + ``api-version`` query are correct on the outbound request.
* Heartbeat thread is stopped before the request is issued.
* ``200`` resolves cleanly.
* ``404`` is swallowed (idempotent — session already gone).
* Other ``4xx``/``5xx`` surface via the standard SDK error path.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from azure.core.exceptions import HttpResponseError

from azure.ai.finetuningsessions._patch import FineTuningSession


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
class _FakeResponse:
    def __init__(
        self,
        status_code: int,
        body: dict | None = None,
    ) -> None:
        self.status_code = status_code
        self._body = body or {}
        self.headers: dict[str, str] = {}

    def json(self) -> dict:
        return self._body

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HttpResponseError(message=f"HTTP {self.status_code}")


class _RecordingClient:
    """Capture every request and return scripted responses."""

    def __init__(self, responses: list[_FakeResponse]) -> None:
        self.requests: list[Any] = []
        self._responses = iter(responses)

    def send_request(self, req: Any) -> _FakeResponse:
        self.requests.append(req)
        return next(self._responses)


def _make_session(client: Any, session_id: str = "session_deadbeef") -> FineTuningSession:
    """Construct a session with the heartbeat thread immediately stopped.

    The class auto-starts a heartbeat in ``__init__``; we stop it right away
    so tests don't see spurious background traffic.
    """
    sess = FineTuningSession(client, session_id=session_id)
    sess._stop_heartbeat()
    return sess


# ---------------------------------------------------------------------------
# Sync FineTuningSession.delete()
# ---------------------------------------------------------------------------
class TestFineTuningSessionDelete:
    def test_success_issues_delete_with_correct_url(self) -> None:
        """delete() preserves a legacy resource ID on the wire."""
        client = _RecordingClient([_FakeResponse(200, {"deleted": True})])
        sess = _make_session(client, session_id="model_abc12345")

        assert sess.session_id == "session_abc12345"
        sess.delete()

        assert len(client.requests) == 1
        req = client.requests[0]
        assert req.method == "DELETE"
        assert "/fine_tuning_sessions/model_abc12345" in req.url, f"Expected model_abc12345 in URL, got: {req.url}"
        # Headers include the foundry features opt-in.
        assert "Foundry-Features" in req.headers
        assert req.headers["Accept"] == "application/json"

    def test_delete_url_derivation_bare_id(self) -> None:
        """A session_id that already has session_ prefix is handled correctly."""
        client = _RecordingClient([_FakeResponse(200)])
        sess = _make_session(client, session_id="session_abc12345")
        sess.delete()
        req = client.requests[0]
        assert req.method == "DELETE"
        assert "/fine_tuning_sessions/session_abc12345" in req.url

    def test_delete_url_derivation_raw_id(self) -> None:
        """A bare old-server session ID preserves the legacy model resource."""
        client = _RecordingClient([_FakeResponse(200)])
        sess = _make_session(client, session_id="ab12ef34")
        sess.delete()
        req = client.requests[0]
        assert "/fine_tuning_sessions/model_ab12ef34" in req.url

    def test_returns_none(self) -> None:
        client = _RecordingClient([_FakeResponse(200)])
        sess = _make_session(client)
        result = sess.delete()
        assert result is None

    def test_404_is_swallowed_as_idempotent(self) -> None:
        client = _RecordingClient([_FakeResponse(404, {"detail": "not found"})])
        sess = _make_session(client)

        # Must not raise.
        sess.delete()

    def test_500_raises(self) -> None:
        client = _RecordingClient([_FakeResponse(500, {"detail": "internal error"})])
        sess = _make_session(client)

        with pytest.raises(HttpResponseError):
            sess.delete()

    def test_403_raises(self) -> None:
        client = _RecordingClient([_FakeResponse(403, {"detail": "forbidden"})])
        sess = _make_session(client)

        with pytest.raises(HttpResponseError):
            sess.delete()

    def test_stops_heartbeat_before_request(self) -> None:
        # _stop_heartbeat must run before send_request — otherwise the
        # heartbeat could race with the cascade and re-stamp the session
        # row after delete starts.
        client = _RecordingClient([_FakeResponse(200)])
        sess = FineTuningSession(client, session_id="session_deadbeef")

        order: list[str] = []
        orig_stop = sess._stop_heartbeat
        orig_send = client.send_request

        def _spy_stop() -> None:
            order.append("stop_heartbeat")
            orig_stop()

        def _spy_send(req: Any) -> _FakeResponse:
            order.append("send_request")
            return orig_send(req)

        sess._stop_heartbeat = _spy_stop  # type: ignore[method-assign]
        client.send_request = _spy_send  # type: ignore[method-assign]

        sess.delete()

        assert order == ["stop_heartbeat", "send_request"]


# ---------------------------------------------------------------------------
# Async FineTuningSessionClient.delete_session()
# ---------------------------------------------------------------------------
class _AsyncFakeResponse:
    def __init__(self, status_code: int, body: dict | None = None) -> None:
        self.status_code = status_code
        self._body = body or {}
        self.headers: dict[str, str] = {}

    def json(self) -> dict:
        return self._body

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HttpResponseError(message=f"HTTP {self.status_code}")


class _AsyncRecordingClient:
    def __init__(self, responses: list[_AsyncFakeResponse]) -> None:
        self.requests: list[Any] = []
        self._responses = iter(responses)

    async def send_request(self, req: Any) -> _AsyncFakeResponse:
        self.requests.append(req)
        return next(self._responses)


class TestAsyncDeleteSession:
    """The async path lives as a free function patched onto the client."""

    def _import(self) -> Any:
        from azure.ai.finetuningsessions.aio import _patch as aio_patch

        return aio_patch

    def test_success_issues_delete_with_correct_url(self) -> None:
        """Async delete_session must send DELETE .../sessions/session_<raw>."""
        aio_patch = self._import()
        client = _AsyncRecordingClient([_AsyncFakeResponse(200, {"deleted": True})])

        with patch.object(aio_patch, "_stop_heartbeat", MagicMock()):
            asyncio.run(aio_patch.delete_session(client, "model_abc12345"))

        assert len(client.requests) == 1
        req = client.requests[0]
        assert req.method == "DELETE"
        assert "/fine_tuning_sessions/session_abc12345" in req.url, f"Expected session_abc12345, got: {req.url}"
        assert "model_abc12345" not in req.url
        assert "Foundry-Features" in req.headers

    def test_404_is_swallowed(self) -> None:
        aio_patch = self._import()
        client = _AsyncRecordingClient([_AsyncFakeResponse(404)])

        with patch.object(aio_patch, "_stop_heartbeat", MagicMock()):
            # Must not raise.
            asyncio.run(aio_patch.delete_session(client, "session_deadbeef"))

    def test_500_raises(self) -> None:
        aio_patch = self._import()
        client = _AsyncRecordingClient([_AsyncFakeResponse(500, {"detail": "boom"})])

        with patch.object(aio_patch, "_stop_heartbeat", MagicMock()):
            with pytest.raises(HttpResponseError):
                asyncio.run(aio_patch.delete_session(client, "session_deadbeef"))

    def test_stops_heartbeat_before_send(self) -> None:
        aio_patch = self._import()
        client = _AsyncRecordingClient([_AsyncFakeResponse(200)])

        order: list[str] = []
        orig_send = client.send_request

        def _spy_stop(self_arg: Any, session_id: str) -> None:
            order.append(f"stop:{session_id}")

        async def _spy_send(req: Any) -> _AsyncFakeResponse:
            order.append("send")
            return await orig_send(req)

        client.send_request = _spy_send  # type: ignore[method-assign]
        with patch.object(aio_patch, "_stop_heartbeat", _spy_stop):
            asyncio.run(aio_patch.delete_session(client, "session_deadbeef"))

        assert order == ["stop:session_deadbeef", "send"]

    def test_registered_in_patch_sdk(self) -> None:
        # patch_sdk attaches delete_session onto the public patched client.
        aio_patch = self._import()
        from azure.ai.finetuningsessions.aio import (
            FineTuningSessionClient as Gen,
        )

        assert hasattr(Gen, "delete_session")
        assert getattr(Gen, "delete_session") is aio_patch.delete_session
