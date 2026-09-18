# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for the cancellation policy.

Verifies the three cancellation rules:

1. **Steered cancellations** — If handler returns without terminal event,
   framework auto-emits ``response.failed``. If handler emits terminal, that wins.

2. **Shutdown cancellations** — If handler returns terminal, that wins. Otherwise:
   - resilient=True, background=True: leave in_progress for re-entry on restart
   - resilient=True, background=False: best-effort mark failed after grace period
   - store=False: best-effort mark failed after grace period

3. **Client explicit cancellation** (/cancel for bg, disconnect for non-bg) —
   Framework forces ``cancelled`` regardless of handler output.

Key invariants:
- ``cancelled`` status is ONLY produced by explicit client cancellation
- ``incomplete`` status is NEVER set by the framework
- Steering and shutdown NEVER produce ``cancelled``
"""

from __future__ import annotations

import asyncio
import json as _json
from typing import Any

import pytest

from azure.ai.agentserver.responses import (
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)
from azure.ai.agentserver.responses._id_generator import IdGenerator

# ---------------------------------------------------------------------------
# Minimal async ASGI client (same pattern as contract tests)
# ---------------------------------------------------------------------------


class _AsgiResponse:
    def __init__(self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]) -> None:
        self.status_code = status_code
        self.body = body
        self.headers = headers

    def json(self) -> Any:
        return _json.loads(self.body)


class _AsyncAsgiClient:
    def __init__(self, app: Any) -> None:
        self.app = app
        self._app = app

    @staticmethod
    def _build_scope(method: str, path: str, body: bytes) -> dict[str, Any]:
        headers: list[tuple[bytes, bytes]] = []
        query_string = b""
        if "?" in path:
            path, qs = path.split("?", 1)
            query_string = qs.encode()
        if body:
            headers = [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ]
        return {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "headers": headers,
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string,
            "server": ("localhost", 80),
            "client": ("127.0.0.1", 123),
            "root_path": "",
        }

    async def request(self, method: str, path: str, *, json_body: dict[str, Any] | None = None) -> _AsgiResponse:
        body = _json.dumps(json_body).encode() if json_body else b""
        scope = self._build_scope(method, path, body)
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

    async def get(self, path: str) -> _AsgiResponse:
        return await self.request("GET", path)

    async def post(self, path: str, *, json_body: dict[str, Any] | None = None) -> _AsgiResponse:
        return await self.request("POST", path, json_body=json_body)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_client(handler, *, steerable: bool = False, resilient: bool = False) -> _AsyncAsgiClient:
    """Build an async ASGI test client with the given handler and options."""
    options = ResponsesServerOptions(
        resilient_background=resilient,
        steerable_conversations=steerable,
    )
    app = ResponsesAgentServerHost(options=options)
    app.response_handler(handler)
    return _AsyncAsgiClient(app)


def _parse_sse_events(body: str) -> list[dict[str, Any]]:
    """Parse SSE body into a list of {type, data} dicts."""
    events: list[dict[str, Any]] = []
    event_type = None
    for line in body.split("\n"):
        if line.startswith("event: "):
            event_type = line[7:].strip()
        elif line.startswith("data: "):
            data = _json.loads(line[6:])
            events.append({"type": event_type or data.get("type", ""), "data": data})
            event_type = None
    return events


# ---------------------------------------------------------------------------
# Rule 1: Steered cancellations
# ---------------------------------------------------------------------------


class TestSteeringCancellation:
    """Steering cancellation: handler terminal wins; no terminal → failed."""

    @pytest.mark.asyncio
    async def test_steered_no_terminal_produces_failed(self) -> None:
        """Rule 1: Handler returns without terminal on steering → response.failed.

        The framework prevents orphan responses by marking as failed.
        Status must NOT be 'cancelled' (reserved for explicit cancel).

        Simulates steering by having the handler stamp STEERED reason
        and fire the cancellation signal (same as resilient orchestrator does).
        """

        started = asyncio.Event()

        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
                yield stream.emit_created()
                yield stream.emit_in_progress()
                started.set()
                # Simulate steering: stamp reason then fire signal
                # (in production, ResilientResponseOrchestrator does this)
                # Spec 024 Phase 5: steering pressure → no cause flag, cancel event only.
                cancellation_signal.set()
                # Give framework a tick to notice
                await asyncio.sleep(0.01)
                # Return without emitting terminal — framework should emit failed
                return

            return _gen()

        client = _build_client(handler, resilient=True)

        response_id = IdGenerator.new_response_id()

        post_resp = await client.post(
            "/responses",
            json_body={
                "response_id": response_id,
                "model": "test",
                "input": "turn 1",
                "stream": True,
                "store": True,
                "background": True,
            },
        )
        await asyncio.wait_for(started.wait(), timeout=5.0)
        # Wait for bg producer to complete
        await asyncio.sleep(0.1)

        assert post_resp.status_code == 200
        events = _parse_sse_events(post_resp.body.decode())
        terminal_events = [
            e for e in events if e["type"] in {"response.completed", "response.failed", "response.incomplete"}
        ]
        # Framework should have emitted response.failed
        assert len(terminal_events) == 1
        terminal = terminal_events[0]
        assert terminal["type"] == "response.failed"
        # Status MUST be 'failed', NOT 'cancelled'
        assert (
            terminal["data"]["response"]["status"] == "failed"
        ), "Steered cancellation must produce 'failed', never 'cancelled'"

    @pytest.mark.asyncio
    async def test_steered_handler_terminal_wins(self) -> None:
        """Rule 1: Handler emits response.completed on steering → that wins.

        This is the recommended pattern: handler detects steering, emits
        terminal (completed/failed/incomplete) for the old turn, then returns.
        """

        started = asyncio.Event()

        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
                yield stream.emit_created()
                yield stream.emit_in_progress()
                started.set()
                # Simulate steering signal
                # Spec 024 Phase 5: steering pressure → no cause flag, cancel event only.
                cancellation_signal.set()
                await asyncio.sleep(0.01)
                # Handler chooses to emit completed (recommended pattern)
                yield stream.emit_completed()

            return _gen()

        client = _build_client(handler, resilient=True)

        response_id = IdGenerator.new_response_id()

        post_resp = await client.post(
            "/responses",
            json_body={
                "response_id": response_id,
                "model": "test",
                "input": "turn 1",
                "stream": True,
                "store": True,
                "background": True,
            },
        )
        await asyncio.wait_for(started.wait(), timeout=5.0)
        await asyncio.sleep(0.1)

        assert post_resp.status_code == 200
        events = _parse_sse_events(post_resp.body.decode())
        terminal_events = [
            e for e in events if e["type"] in {"response.completed", "response.failed", "response.incomplete"}
        ]
        assert len(terminal_events) == 1
        terminal = terminal_events[0]
        # Handler's terminal wins
        assert terminal["type"] == "response.completed"
        assert terminal["data"]["response"]["status"] == "completed"


# ---------------------------------------------------------------------------
# Rule 2: Shutdown cancellations (covered in test_shutdown_status_e2e.py,
#          these tests verify the status-never-cancelled invariant)
# ---------------------------------------------------------------------------


class TestShutdownNeverCancelled:
    """Shutdown NEVER produces 'cancelled' status — always 'failed' or stays in_progress."""

    @pytest.mark.asyncio
    async def test_shutdown_non_resilient_bg_produces_failed_not_cancelled(self) -> None:
        """Rule 2: Non-resilient bg shutdown → failed (never cancelled)."""
        started = asyncio.Event()

        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
                yield stream.emit_created()
                yield stream.emit_in_progress()
                started.set()
                # Wait for signal without emitting terminal
                while not cancellation_signal.is_set():
                    await asyncio.sleep(0.01)
                return

            return _gen()

        client = _build_client(handler, resilient=False)

        response_id = IdGenerator.new_response_id()

        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "response_id": response_id,
                    "model": "test",
                    "input": "hello",
                    "stream": True,
                    "store": True,
                    "background": True,
                },
            )
        )
        await asyncio.wait_for(started.wait(), timeout=5.0)

        # Trigger shutdown — sets flag and fires signals on all records
        client.app.request_shutdown()
        await client.app._endpoint.handle_shutdown()

        post_resp = await asyncio.wait_for(post_task, timeout=5.0)
        assert post_resp.status_code == 200

        events = _parse_sse_events(post_resp.body.decode())
        terminal_events = [
            e for e in events if e["type"] in {"response.completed", "response.failed", "response.incomplete"}
        ]
        assert len(terminal_events) == 1
        terminal = terminal_events[0]
        assert terminal["type"] == "response.failed"
        # Status must be 'failed', NEVER 'cancelled'
        assert terminal["data"]["response"]["status"] == "failed", "Shutdown must produce 'failed', never 'cancelled'"


# ---------------------------------------------------------------------------
# Rule 3: Client explicit cancellation
# ---------------------------------------------------------------------------


class TestClientExplicitCancellation:
    """Client cancel (/cancel endpoint) forces 'cancelled' regardless of handler."""

    @pytest.mark.asyncio
    async def test_cancel_endpoint_forces_cancelled_status(self) -> None:
        """Rule 3: /cancel → status='cancelled', output cleared."""
        started = asyncio.Event()

        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
                yield stream.emit_created()
                yield stream.emit_in_progress()
                started.set()
                while not cancellation_signal.is_set():
                    await asyncio.sleep(0.01)
                # Return without terminal — framework forces cancelled
                return

            return _gen()

        client = _build_client(handler)

        response_id = IdGenerator.new_response_id()

        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "response_id": response_id,
                    "model": "test",
                    "input": "hello",
                    "stream": True,
                    "store": True,
                    "background": True,
                },
            )
        )
        await asyncio.wait_for(started.wait(), timeout=5.0)

        # Explicit cancel
        cancel_resp = await client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["status"] == "cancelled"

        post_resp = await asyncio.wait_for(post_task, timeout=5.0)
        assert post_resp.status_code == 200

        # GET should return cancelled
        get_resp = await client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "cancelled"
        assert get_resp.json()["output"] == []

    @pytest.mark.asyncio
    async def test_cancel_overrides_handler_terminal(self) -> None:
        """Rule 3: Even if handler emits completed AFTER cancel signal, stored status is cancelled.

        'Does not matter what developer does after cancellation.'
        """
        started = asyncio.Event()

        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
                yield stream.emit_created()
                yield stream.emit_in_progress()
                started.set()
                while not cancellation_signal.is_set():
                    await asyncio.sleep(0.01)
                # Handler attempts to emit completed after cancel signal
                yield stream.emit_completed()

            return _gen()

        client = _build_client(handler)

        response_id = IdGenerator.new_response_id()

        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "response_id": response_id,
                    "model": "test",
                    "input": "hello",
                    "stream": True,
                    "store": True,
                    "background": True,
                },
            )
        )
        await asyncio.wait_for(started.wait(), timeout=5.0)

        # Cancel fires
        cancel_resp = await client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["status"] == "cancelled"

        await asyncio.wait_for(post_task, timeout=5.0)

        # Stored state is cancelled regardless of handler output
        get_resp = await client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "cancelled", "Client cancel always wins over handler terminal"


# ---------------------------------------------------------------------------
# Invariant: 'incomplete' is NEVER set by framework
# ---------------------------------------------------------------------------


class TestIncompleteNeverFramework:
    """Framework NEVER sets 'incomplete' — it's exclusively developer-controlled."""

    @pytest.mark.asyncio
    async def test_handler_incomplete_honoured(self) -> None:
        """Developer emitting incomplete is passed through."""

        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
                yield stream.emit_created()
                yield stream.emit_in_progress()
                yield stream.emit_incomplete(reason="max_output_tokens")

            return _gen()

        client = _build_client(handler)

        response_id = IdGenerator.new_response_id()

        resp = await client.post(
            "/responses",
            json_body={
                "response_id": response_id,
                "model": "test",
                "input": "hello",
                "stream": True,
                "store": True,
                "background": True,
            },
        )
        assert resp.status_code == 200

        events = _parse_sse_events(resp.body.decode())
        terminal_events = [
            e for e in events if e["type"] in {"response.completed", "response.failed", "response.incomplete"}
        ]
        assert len(terminal_events) == 1
        assert terminal_events[0]["type"] == "response.incomplete"
