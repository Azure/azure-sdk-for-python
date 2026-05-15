# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for eager eviction of terminal response records.

Once a response reaches terminal status (completed, failed, cancelled,
incomplete) and has been persisted to durable storage, the in-memory
runtime record should be immediately evicted.  Subsequent operations
fall through to the provider (storage) path, freeing server memory.

Key invariants:
- After terminal + persist, ``_RuntimeState.get(id)`` returns ``None``.
- GET on the evicted response still returns 200 (via provider fallback).
- DELETE on the evicted response still works (via provider fallback).
- ``store=False`` responses are also evicted (nothing to fall back to → 404).
- Eviction does not break input_items history chains for other responses.
"""

from __future__ import annotations

import asyncio
import json as _json
from typing import Any

import pytest

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from tests._helpers import poll_until

# ── Helpers ───────────────────────────────────────────────


def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    async def _events():
        if False:  # pragma: no cover
            yield None

    return _events()


# ── Async ASGI client (needed for background requests) ───


class _AsgiResponse:
    def __init__(self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]) -> None:
        self.status_code = status_code
        self.body = body
        self.headers = headers

    def json(self) -> Any:
        return _json.loads(self.body)


class _AsyncAsgiClient:
    def __init__(self, app: Any) -> None:
        self._app = app

    @staticmethod
    def _build_scope(
        method: str,
        path: str,
        body: bytes,
        headers: list[tuple[bytes, bytes]] | None = None,
    ) -> dict[str, Any]:
        hdr: list[tuple[bytes, bytes]] = list(headers or [])
        query_string = b""
        if "?" in path:
            path, qs = path.split("?", 1)
            query_string = qs.encode()
        if body:
            hdr += [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ]
        return {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "headers": hdr,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string,
            "server": ("localhost", 80),
            "client": ("127.0.0.1", 123),
            "root_path": "",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> _AsgiResponse:
        body = _json.dumps(json_body).encode() if json_body else b""
        raw_headers = [(k.lower().encode(), v.encode()) for k, v in headers.items()] if headers else []
        scope = self._build_scope(method, path, body, raw_headers)
        status_code: int | None = None
        response_headers: list[tuple[bytes, bytes]] = []
        body_parts: list[bytes] = []
        request_sent = False
        response_done = asyncio.Event()

        async def receive() -> dict[str, Any]:
            nonlocal request_sent
            if not request_sent:
                request_sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            await response_done.wait()
            return {"type": "http.disconnect"}

        async def send(message: dict[str, Any]) -> None:
            nonlocal status_code, response_headers
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                chunk = message.get("body", b"")
                if chunk:
                    body_parts.append(chunk)
                if not message.get("more_body", False):
                    response_done.set()

        await self._app(scope, receive, send)
        assert status_code is not None
        return _AsgiResponse(status_code=status_code, body=b"".join(body_parts), headers=response_headers)

    async def get(self, path: str, *, headers: dict[str, str] | None = None) -> _AsgiResponse:
        return await self.request("GET", path, headers=headers)

    async def post(
        self,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> _AsgiResponse:
        return await self.request("POST", path, json_body=json_body, headers=headers)

    async def delete(self, path: str, *, headers: dict[str, str] | None = None) -> _AsgiResponse:
        return await self.request("DELETE", path, headers=headers)


# ── Sync test helpers (Starlette TestClient) ──────────────

from starlette.testclient import TestClient  # noqa: E402


def _make_client(handler=_noop_handler) -> TestClient:
    host = ResponsesAgentServerHost()
    host.response_handler(handler)
    return TestClient(host)


def _create_and_complete(client: TestClient, *, store: bool = True) -> str:
    """Create a sync response and return the response_id."""
    r = client.post(
        "/responses",
        json={
            "model": "m",
            "input": [{"role": "user", "content": "hi"}],
            "store": store,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in {"completed", "failed", "incomplete"}
    return body["id"]


def _wait_for_terminal(client: TestClient, response_id: str) -> dict[str, Any]:
    latest: dict[str, Any] = {}
    terminal = {"completed", "failed", "incomplete", "cancelled"}

    def _check() -> bool:
        nonlocal latest
        r = client.get(f"/responses/{response_id}")
        if r.status_code != 200:
            return False
        latest = r.json()
        return latest.get("status") in terminal

    poll_until(_check, timeout_s=5.0, interval_s=0.05, label="wait_terminal")
    return latest


# ══════════════════════════════════════════════════════════
# Sync path: completed responses should be evicted
# ══════════════════════════════════════════════════════════


class TestSyncEviction:
    """After sync execution, terminal records with store=True are evicted."""

    def test_sync_completed_response_get_still_returns_200(self) -> None:
        """After sync completion + persist, GET returns 200 via provider fallback."""
        client = _make_client()
        rid = _create_and_complete(client, store=True)
        # GET should still work — either in-memory or provider fallback
        r = client.get(f"/responses/{rid}")
        assert r.status_code == 200
        assert r.json()["status"] in {"completed", "failed", "incomplete"}

    def test_sync_completed_response_delete_still_works(self) -> None:
        """After sync completion + persist, DELETE returns 200 via provider fallback."""
        client = _make_client()
        rid = _create_and_complete(client, store=True)
        r = client.delete(f"/responses/{rid}")
        assert r.status_code == 200

    def test_sync_store_false_also_evicted(self) -> None:
        """store=False responses are also evicted — no provider fallback needed
        since GET/DELETE/cancel don't work for them anyway."""
        client = _make_client()
        rid = _create_and_complete(client, store=False)
        # After eviction, GET falls through to provider which has nothing → 404
        r = client.get(f"/responses/{rid}")
        assert r.status_code == 404


# ══════════════════════════════════════════════════════════
# Background path: completed responses should be evicted
# ══════════════════════════════════════════════════════════


def _make_cancellable_bg_handler() -> Any:
    """Handler that emits created + completed after a brief delay."""
    started = asyncio.Event()

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_in_progress()
            started.set()
            # Wait briefly for cancel, then complete
            while not cancellation_signal.is_set():
                await asyncio.sleep(0.01)

        return _events()

    handler.started = started  # type: ignore[attr-defined]
    return handler


def _build_async_client(handler: Any) -> tuple[_AsyncAsgiClient, ResponsesAgentServerHost]:
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    return _AsyncAsgiClient(app), app


class TestBackgroundEviction:
    """After background execution completes + persists, records are evicted."""

    @pytest.mark.asyncio
    async def test_bg_completed_response_get_returns_200(self) -> None:
        """After bg handler completes and persists, GET returns 200 via provider."""
        handler = _make_cancellable_bg_handler()
        client, app = _build_async_client(handler)
        response_id = IdGenerator.new_response_id()

        # Start background response
        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "response_id": response_id,
                    "model": "test",
                    "background": True,
                    "stream": True,
                },
            )
        )

        # Wait for handler to start
        await asyncio.wait_for(handler.started.wait(), timeout=5.0)

        # Cancel to bring it to terminal
        cancel_resp = await client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["status"] == "cancelled"

        # Wait for POST to finish
        handler.started.set()
        try:
            await asyncio.wait_for(post_task, timeout=5.0)
        except (asyncio.CancelledError, Exception):
            pass

        # Allow async cleanup
        await asyncio.sleep(0.3)

        # GET should return 200 — either still in memory or via provider
        get_resp = await client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200


# ══════════════════════════════════════════════════════════
# Unit-level: _RuntimeState.try_evict
# ══════════════════════════════════════════════════════════


class TestTryEvict:
    """Direct unit tests for _RuntimeState.try_evict method."""

    @pytest.mark.asyncio
    async def test_try_evict_removes_terminal_record(self) -> None:
        """try_evict on a terminal record removes it from _records."""
        from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState
        from azure.ai.agentserver.responses.models.runtime import ResponseExecution, ResponseModeFlags

        state = _RuntimeState()
        record = ResponseExecution(
            response_id="caresp_test123456789012345678901234567890",
            mode_flags=ResponseModeFlags(stream=False, store=True, background=False),
            status="completed",
        )
        await state.add(record)
        assert await state.get(record.response_id) is not None

        evicted = await state.try_evict(record.response_id)
        assert evicted is True
        assert await state.get(record.response_id) is None

    @pytest.mark.asyncio
    async def test_try_evict_unknown_id_returns_false(self) -> None:
        """try_evict on a non-existent ID returns False."""
        from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState

        state = _RuntimeState()
        evicted = await state.try_evict("caresp_unknown99999999999999999999999999999")
        assert evicted is False

    @pytest.mark.asyncio
    async def test_try_evict_non_terminal_returns_false(self) -> None:
        """try_evict on an in-progress record returns False (not evicted)."""
        from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState
        from azure.ai.agentserver.responses.models.runtime import ResponseExecution, ResponseModeFlags

        state = _RuntimeState()
        record = ResponseExecution(
            response_id="caresp_test123456789012345678901234567890",
            mode_flags=ResponseModeFlags(stream=False, store=True, background=False),
            status="in_progress",
        )
        await state.add(record)

        evicted = await state.try_evict(record.response_id)
        assert evicted is False
        # Record should still be there
        assert await state.get(record.response_id) is not None

    @pytest.mark.asyncio
    async def test_try_evict_does_not_mark_as_deleted(self) -> None:
        """Eviction must NOT add the ID to _deleted_response_ids.

        Eviction != deletion. Evicted responses are still retrievable
        from the provider. Only explicit DELETE marks as deleted.
        """
        from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState
        from azure.ai.agentserver.responses.models.runtime import ResponseExecution, ResponseModeFlags

        state = _RuntimeState()
        record = ResponseExecution(
            response_id="caresp_test123456789012345678901234567890",
            mode_flags=ResponseModeFlags(stream=False, store=True, background=False),
            status="completed",
        )
        await state.add(record)
        await state.try_evict(record.response_id)

        assert await state.is_deleted(record.response_id) is False

    @pytest.mark.asyncio
    async def test_try_evict_removes_record_so_isolation_falls_to_storage(self) -> None:
        """After eviction the record is gone — isolation is enforced by Foundry storage, not locally."""
        from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState
        from azure.ai.agentserver.responses.models.runtime import ResponseExecution, ResponseModeFlags

        state = _RuntimeState()
        rid = "caresp_test123456789012345678901234567890"
        record = ResponseExecution(
            response_id=rid,
            mode_flags=ResponseModeFlags(stream=False, store=True, background=False),
            status="completed",
            chat_isolation_key="my_key",
        )
        await state.add(record)

        # In-flight: static helper enforces isolation via the record's key
        assert _RuntimeState.check_chat_isolation(record.chat_isolation_key, "my_key") is True
        assert _RuntimeState.check_chat_isolation(record.chat_isolation_key, "wrong") is False
        assert _RuntimeState.check_chat_isolation(record.chat_isolation_key, None) is False

        await state.try_evict(rid)

        # After eviction the record is gone; callers fall through to the
        # Foundry storage provider which enforces isolation server-side.
        assert await state.get(rid) is None
        assert await state.is_deleted(rid) is False
