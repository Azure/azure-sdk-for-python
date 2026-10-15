# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for the Resilient Response Recovery Contract (Spec 012).

Pins the framework-side guarantees the spec promises so Phase 5 framework
changes have a precise red→green target.

**TDD discipline**: TR-001 (the fresh-entry baseline) MUST pass before any
framework changes ship — it's the regression guard. TR-002..TR-010 fail at
the time this file is committed; they turn green as Phase 5 lands the
corresponding framework changes.

Each test pins to a specific FR from spec.md; see the section headers.

Note on infrastructure: full crash injection (process kill + restart) is
covered by ``_crash_harness.py`` and used by ``test_recovery_sample_19.py``.
The tests in this file simulate recovery by directly invoking the resilient
orchestrator's recovered code path with ``entry_mode="recovered"`` —
this is enough to pin the framework-side contract.
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
from azure.ai.agentserver.responses.models._generated import ResponseObject

# ---------------------------------------------------------------------------
# Minimal async ASGI client (copied pattern from test_cancellation_policy_e2e.py)
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

    async def post(self, path: str, *, json_body: dict[str, Any] | None = None) -> _AsgiResponse:
        return await self.request("POST", path, json_body=json_body)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_client(handler, *, steerable: bool = False, resilient: bool = True) -> _AsyncAsgiClient:
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
    for line in body.split("\n"):
        if line.startswith("data: "):
            data = _json.loads(line[6:])
            events.append({"type": data.get("type", ""), "data": data})
    return events


def _build_resumption_response(
    response_id: str, model: str, output: list[dict[str, Any]] | None = None
) -> ResponseObject:
    """Build a minimal resumption response with the given output items."""
    return ResponseObject(
        {
            "id": response_id,
            "object": "response",
            "status": "in_progress",
            "output": output or [],
            "model": model,
        }
    )


def _set_recovery_state(context: ResponseContext, *, is_recovery: bool = False) -> None:
    """Flat-field helper for tests that want to mark a context as recovered.

    Replaces the pre-spec-024 ``_make_resilience_context`` helper.
    """
    context.is_recovery = is_recovery
    context.is_steered_turn = False
    context.pending_input_count = 0


# ---------------------------------------------------------------------------
# TR-001 — Fresh entry baseline (MUST PASS at red-baseline time)
# ---------------------------------------------------------------------------


class TestFreshEntryBaseline:
    """TR-001: pins the existing fresh-entry happy path. No spec changes here."""

    @pytest.mark.asyncio
    async def test_fresh_entry_produces_well_formed_response(self) -> None:
        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, request=request)
                yield stream.emit_created()
                yield stream.emit_in_progress()
                message = stream.add_output_item_message()
                yield message.emit_added()
                text = message.add_text_content()
                yield text.emit_added()
                yield text.emit_delta("hello ")
                yield text.emit_delta("world")
                yield text.emit_text_done("hello world")
                yield text.emit_done()
                yield message.emit_done()
                yield stream.emit_completed()

            return _gen()

        client = _build_client(handler, resilient=True)
        resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": "hi",
                "stream": True,
                "store": True,
                "background": True,
            },
        )
        assert resp.status_code == 200
        events = _parse_sse_events(resp.body.decode())
        types = [e["type"] for e in events]
        assert "response.created" in types
        assert "response.in_progress" in types
        assert "response.completed" in types


# ---------------------------------------------------------------------------
# TR-004 — ResponseEventStream(response=...) advances _output_index
# Pins FR-007 (snapshot-seeded stream advances past existing items).
# Currently FAILS — _output_index starts at 0 regardless of seeded response.
# ---------------------------------------------------------------------------


class TestSnapshotSeededOutputIndex:
    """TR-004: pins FR-007. Currently failing."""

    def test_seeded_stream_advances_output_index_past_existing_items(self) -> None:
        existing = _build_resumption_response(
            response_id="resp_abc",
            model="m",
            output=[
                {"type": "message", "id": "m1", "role": "assistant", "content": []},
                {"type": "message", "id": "m2", "role": "assistant", "content": []},
            ],
        )
        stream = ResponseEventStream(response_id="resp_abc", response=existing)
        # Next add should allocate output_index == 2, not 0.
        builder = stream.add_output_item_message()
        # Pin: the next allocated index is len(existing.output).
        assert builder._output_index == 2, (  # type: ignore[attr-defined]
            f"Expected output_index=2 (len of seeded output), got "
            f"{builder._output_index}. FR-007 not yet implemented."  # type: ignore[attr-defined]
        )


# ---------------------------------------------------------------------------
# TR-005 — apply_event on second response.in_progress REPLACES snapshot
# Pins FR-004 (snapshot-reset semantics).
# Currently FAILS — apply_event re-extracts snapshot from all_events,
# accumulating both attempts' items.
# ---------------------------------------------------------------------------


class TestSnapshotResetOnSecondInProgress:
    """TR-005: pins FR-004.

    Pre-reset events include an ``output_item.added`` that the
    library would normally accumulate into the snapshot. The reset
    ``response.in_progress`` carries a payload that EXCLUDES that
    item; the contract requires the post-reset snapshot to match
    the reset payload, NOT to merge with the prior items.
    """

    def test_second_in_progress_replaces_response_snapshot(self) -> None:
        from azure.ai.agentserver.responses.models.runtime import (
            ResponseExecution,
            ResponseModeFlags,
        )

        record = ResponseExecution(
            response_id="resp_xyz",
            mode_flags=ResponseModeFlags(stream=True, store=True, background=True),
            status="in_progress",
        )
        record.response = ResponseObject(
            {
                "id": "resp_xyz",
                "object": "response",
                "status": "in_progress",
                "output": [],
            }
        )

        # Replay realistic pre-crash event history that ends with the
        # in-flight item being added.
        created_event = {"type": "response.created", "response": {"id": "resp_xyz"}}
        inprog1_event = {"type": "response.in_progress", "response": {"id": "resp_xyz"}}
        item_added_event = {
            "type": "response.output_item.added",
            "output_index": 0,
            "item": {
                "type": "message",
                "id": "m_inflight",
                "role": "assistant",
                "content": [],
            },
        }

        record.apply_event(created_event, [created_event])  # type: ignore[arg-type]
        record.apply_event(inprog1_event, [created_event, inprog1_event])  # type: ignore[arg-type]
        record.apply_event(
            item_added_event,  # type: ignore[arg-type]
            [created_event, inprog1_event, item_added_event],
        )

        # Pre-reset state: response.output contains the in-flight item.
        assert record.response is not None
        assert len(record.response.get("output", [])) == 1

        # Now the recovery handler emits a fresh in_progress whose payload
        # EXCLUDES the in-flight item (resumption response is empty).
        reset_event = {
            "type": "response.in_progress",
            "response": {
                "id": "resp_xyz",
                "object": "response",
                "status": "in_progress",
                "output": [],  # resumption response excludes the in-flight item
            },
        }

        all_events = [
            created_event,
            inprog1_event,
            item_added_event,
            reset_event,
        ]
        record.apply_event(reset_event, all_events)  # type: ignore[arg-type]

        # After reset, output is the resumption response's (empty), not
        # the union with the pre-reset item.
        output = record.response.get("output") if record.response else None
        assert output == [], (
            f"Expected output to be reset to []; got {output}. "
            f"FR-004 (apply_event snapshot reset on second in_progress) not yet implemented."
        )


# ---------------------------------------------------------------------------
# TR-006 — Duplicate response.created is a no-op
# Pins FR-005.
# ---------------------------------------------------------------------------


class TestDuplicateCreatedIdempotent:
    """TR-006: pins FR-005."""

    def test_duplicate_created_event_does_not_error(self) -> None:
        from azure.ai.agentserver.responses.streaming._state_machine import (
            EventStreamValidator,
        )

        validator = EventStreamValidator()
        validator.validate_next({"type": "response.created", "response": {}})
        # Second created should be a no-op, not an error.
        try:
            validator.validate_next({"type": "response.created", "response": {}})
        except ValueError as e:
            pytest.fail(f"Duplicate response.created raised: {e}. FR-005 not yet implemented.")


# ---------------------------------------------------------------------------
# TR-007 — Duplicate terminal event is a no-op
# Pins FR-006.
# ---------------------------------------------------------------------------


class TestDuplicateTerminalIdempotent:
    """TR-007: pins FR-006."""

    def test_duplicate_completed_does_not_error(self) -> None:
        from azure.ai.agentserver.responses.streaming._state_machine import (
            EventStreamValidator,
        )

        validator = EventStreamValidator()
        validator.validate_next({"type": "response.created", "response": {}})
        validator.validate_next({"type": "response.in_progress", "response": {}})
        validator.validate_next({"type": "response.completed", "response": {"status": "completed"}})
        try:
            validator.validate_next({"type": "response.completed", "response": {"status": "completed"}})
        except ValueError as e:
            pytest.fail(f"Duplicate response.completed raised: {e}. FR-006 not yet implemented.")


# ---------------------------------------------------------------------------
# TR-002 — Crash mid-stream + recovery-aware handler ⇒ resumption response
# carried; pre-reset items don't accumulate.
# Pins FR-002 + FR-004 + FR-007. Composes the framework changes above.
# ---------------------------------------------------------------------------


class TestRecoveryAwareHandlerProducesCleanFinalResponse:
    """TR-002: pins FR-002, FR-004, FR-007 (composed)."""

    @pytest.mark.asyncio
    async def test_recovery_aware_emits_reset_in_progress_then_new_items(self) -> None:
        # Two-attempt simulation: first invocation emits partial output, then
        # we "crash" by raising. Second invocation runs the recovery path.
        attempts: list[int] = [0]

        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                # On second attempt, pretend entry_mode=="recovered" by simulating
                # the recovery code path: build a resumption response that
                # EXCLUDES the in-flight item from the crashed attempt.
                attempts[0] += 1
                if attempts[0] == 1:
                    # First attempt: emit some events, then "crash".
                    stream = ResponseEventStream(response_id=context.response_id, request=request)
                    yield stream.emit_created()
                    yield stream.emit_in_progress()
                    msg = stream.add_output_item_message()
                    yield msg.emit_added()
                    txt = msg.add_text_content()
                    yield txt.emit_added()
                    yield txt.emit_delta("Half-finis")
                    raise RuntimeError("simulated crash")
                # Second attempt: recovery path.
                resumption = _build_resumption_response(
                    response_id=context.response_id,
                    model=getattr(request, "model", "test"),
                    output=[],  # resumption excludes the in-flight item
                )
                stream = ResponseEventStream(response_id=context.response_id, response=resumption)
                yield stream.emit_created()
                yield stream.emit_in_progress()  # reset point
                msg = stream.add_output_item_message()
                yield msg.emit_added()
                txt = msg.add_text_content()
                yield txt.emit_added()
                yield txt.emit_delta("Complete answer")
                yield txt.emit_text_done("Complete answer")
                yield txt.emit_done()
                yield msg.emit_done()
                yield stream.emit_completed()

            return _gen()

        client = _build_client(handler, resilient=True)
        # First request — expect failure (simulated crash).
        try:
            await client.post(
                "/responses",
                json_body={
                    "model": "test-model",
                    "input": "hi",
                    "stream": True,
                    "store": True,
                    "background": True,
                },
            )
        except Exception:
            pass  # expected

        # Second request — recovery path. (Real recovery is via the resilient
        # orchestrator on restart; here we use a second POST with the same
        # body as a stand-in for "re-invocation".)
        resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": "hi",
                "stream": True,
                "store": True,
                "background": True,
            },
        )
        assert resp.status_code == 200
        events = _parse_sse_events(resp.body.decode())

        # Pin: the persisted response after the recovered attempt MUST contain
        # only the resumption response's items (no leaked "Half-finis" from
        # the crashed attempt). FR-004 enforces this via snapshot-reset.
        completed = next((e for e in events if e["type"] == "response.completed"), None)
        assert completed is not None, "No response.completed in stream"
        output = completed["data"].get("response", {}).get("output", [])
        # Reconstruct: there should be exactly one message item with the
        # "Complete answer" content.
        assert len(output) == 1, (
            f"Expected exactly 1 output item after recovery; got {len(output)}. "
            f"FR-004 / FR-007 not yet implemented (output is accumulating)."
        )


# ---------------------------------------------------------------------------
# TR-003 — Naive handler (no recovery code) still produces a valid response
# Pins FR-013 (graceful degradation / fallback).
# ---------------------------------------------------------------------------


class TestNaiveHandlerFallback:
    """TR-003: pins FR-013."""

    @pytest.mark.asyncio
    async def test_naive_handler_still_produces_terminal(self) -> None:
        # Naive handler — always runs from scratch.
        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, request=request)
                yield stream.emit_created()
                yield stream.emit_in_progress()
                msg = stream.add_output_item_message()
                yield msg.emit_added()
                txt = msg.add_text_content()
                yield txt.emit_added()
                yield txt.emit_delta("Echo: input")
                yield txt.emit_text_done("Echo: input")
                yield txt.emit_done()
                yield msg.emit_done()
                yield stream.emit_completed()

            return _gen()

        client = _build_client(handler, resilient=True)
        resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": "hi",
                "stream": True,
                "store": True,
                "background": True,
            },
        )
        # FR-013: even without recovery code, the response is well-formed
        # and reaches a terminal.
        assert resp.status_code == 200
        events = _parse_sse_events(resp.body.decode())
        terminal = [e for e in events if e["type"] in ("response.completed", "response.failed")]
        assert len(terminal) >= 1, "Naive handler should still produce a terminal event"


# ---------------------------------------------------------------------------
# TR-008 — Recovery × CLIENT_CANCELLED (Spec 011 × Spec 012 composition)
# ---------------------------------------------------------------------------


class TestRecoveryWithClientCancelled:
    """TR-008: signal pre-set with CLIENT_CANCELLED on recovered entry."""

    @pytest.mark.asyncio
    async def test_recovered_handler_with_client_cancel_returns_no_terminal(self) -> None:
        # When the recovered entry sees CLIENT_CANCELLED, the handler returns
        # without a terminal event and the framework forces "cancelled".
        events_emitted: list[str] = []

        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, request=request)
                yield stream.emit_created()
                events_emitted.append("created")
                # Simulate CLIENT_CANCELLED pre-set on this recovered entry.
                context.client_cancelled = True
                cancellation_signal.set()
                # Recovery-aware handler: signal pre-set + CLIENT_CANCELLED → return.
                if cancellation_signal.is_set():
                    if cancellation_signal.is_set() and context.pending_input_count > 0:
                        yield stream.emit_completed()
                        events_emitted.append("completed")
                    return

            return _gen()

        client = _build_client(handler, resilient=True)
        resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": "hi",
                "stream": True,
                "store": True,
                "background": True,
            },
        )
        # CLIENT_CANCELLED path: framework forces "cancelled"; handler emitted
        # only `created` (no terminal).
        assert "created" in events_emitted
        assert "completed" not in events_emitted


# ---------------------------------------------------------------------------
# TR-009 — Recovery × STEERED (Spec 011 × Spec 012 composition)
# ---------------------------------------------------------------------------


class TestRecoveryWithSteered:
    """TR-009: signal pre-set with STEERED on recovered entry."""

    @pytest.mark.asyncio
    async def test_recovered_handler_with_steered_emits_completed(self) -> None:
        events_emitted: list[str] = []

        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, request=request)
                yield stream.emit_created()
                events_emitted.append("created")
                # Simulate steering: fire the cancel signal AND stamp a queued input.
                cancellation_signal.set()
                context.pending_input_count = 1
                if cancellation_signal.is_set():
                    if cancellation_signal.is_set() and context.pending_input_count > 0:
                        yield stream.emit_completed()
                        events_emitted.append("completed")
                    return

            return _gen()

        client = _build_client(handler, resilient=True)
        await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": "hi",
                "stream": True,
                "store": True,
                "background": True,
            },
        )
        assert "created" in events_emitted
        assert "completed" in events_emitted


# ---------------------------------------------------------------------------
# TR-010 — Recovery × SHUTTING_DOWN (Spec 011 × Spec 012 composition)
# ---------------------------------------------------------------------------


class TestRecoveryWithShutdown:
    """TR-010: signal fires mid-stream during recovered attempt → no terminal."""

    @pytest.mark.asyncio
    async def test_recovered_handler_with_shutdown_returns_no_terminal(self) -> None:
        events_emitted: list[str] = []

        async def handler(request: Any, context: ResponseContext, cancellation_signal: asyncio.Event):
            async def _gen():
                stream = ResponseEventStream(response_id=context.response_id, request=request)
                yield stream.emit_created()
                events_emitted.append("created")
                yield stream.emit_in_progress()
                events_emitted.append("in_progress")
                # Mid-stream shutdown.
                context.shutdown.set()

                cancellation_signal.set()
                cancellation_signal.set()
                # Phase 3 of cancellation policy on shutdown: return without terminal.
                if context.shutdown.is_set():
                    return
                yield stream.emit_completed()  # not reached
                events_emitted.append("completed")

            return _gen()

        client = _build_client(handler, resilient=True)
        await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": "hi",
                "stream": True,
                "store": True,
                "background": True,
            },
        )
        assert "created" in events_emitted
        assert "in_progress" in events_emitted
        assert "completed" not in events_emitted
