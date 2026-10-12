# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for the in-process async terminal-persist optimization.

The non-resilient (in-process fallback) streaming path emits the terminal
``response.completed`` event to the client and closes the wire stream BEFORE
performing the terminal provider write. This moves the ~storage-write
round-trip off the client's last-byte path.

Validated behavior:
- The terminal event reaches the client without waiting for a slow terminal
  provider write.
- A GET during the deferral window (before the write lands) serves the
  completed snapshot from the in-memory runtime state.
- A deferred terminal-write FAILURE surfaces via a later GET (the record is
  NOT evicted while the deferred write is pending), while the client still
  received ``response.completed``.

The resilient path keeps the buffer-then-persist-then-yield contract and is
covered by the existing resilience/persistence-failure suites.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Iterable

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.store._base import ResponseProviderProtocol
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

from .test_persistence_failure import (
    _AsyncAsgiClient,
    _collect_sse_events,
    _simple_completed_handler,
)


class _ControllableProvider:
    """Provider wrapper whose ``update_response`` can block or fail on demand.

    ``update_response`` awaits ``release`` (when provided) before completing,
    letting a test observe the deferral window deterministically. When
    ``fail_on_update`` is set it raises after being released/awaited.
    """

    def __init__(
        self,
        inner: ResponseProviderProtocol,
        *,
        release: asyncio.Event | None = None,
        create_release: asyncio.Event | None = None,
        fail_on_update: bool = False,
    ) -> None:
        self._inner = inner
        self._release = release
        self._create_release = create_release
        self.fail_on_update = fail_on_update
        self.create_started = asyncio.Event()
        self.update_started = asyncio.Event()
        self.update_completed = False
        self.delete_started = asyncio.Event()

    async def create_response(
        self,
        response: Any,
        input_items: Iterable[Any] | None,
        history_item_ids: Iterable[str] | None,
        *,
        context: Any = None,
    ) -> None:
        self.create_started.set()
        if self._create_release is not None:
            await self._create_release.wait()
        return await self._inner.create_response(response, input_items, history_item_ids, context=context)

    async def update_response(self, response: Any, *, context: Any = None) -> None:
        self.update_started.set()
        if self._release is not None:
            await self._release.wait()
        if self.fail_on_update:
            raise RuntimeError("Simulated terminal update failure")
        self.update_completed = True
        return await self._inner.update_response(response, context=context)

    async def get_response(self, response_id: str, *, context: Any = None) -> Any:
        return await self._inner.get_response(response_id, context=context)

    async def delete_response(self, response_id: str, *, context: Any = None) -> None:
        self.delete_started.set()
        return await self._inner.delete_response(response_id, context=context)

    async def get_history_item_ids(
        self,
        response_id: str | None,
        before: str | None,
        limit: int,
        *,
        context: Any = None,
    ) -> list[str] | None:
        return await self._inner.get_history_item_ids(response_id, before, limit, context=context)

    async def get_input_items(
        self,
        response_id: str,
        *,
        limit: int = 100,
        ascending: bool = True,
        context: Any = None,
    ) -> list[Any]:
        return await self._inner.get_input_items(response_id, limit=limit, ascending=ascending, context=context)

    async def save_stream_events(self, response_id: str, events: Any, *, context: Any = None) -> None:
        if hasattr(self._inner, "save_stream_events"):
            return await self._inner.save_stream_events(response_id, events, context=context)

    async def get_stream_events(self, response_id: str, *, context: Any = None) -> Any:
        if hasattr(self._inner, "get_stream_events"):
            return await self._inner.get_stream_events(response_id, context=context)
        return None

    async def delete_stream_events(self, response_id: str, *, context: Any = None) -> None:
        if hasattr(self._inner, "delete_stream_events"):
            return await self._inner.delete_stream_events(response_id, context=context)


def _make_app(provider: _ControllableProvider) -> ResponsesAgentServerHost:
    app = ResponsesAgentServerHost(store=provider)
    app.response_handler(_simple_completed_handler)
    return app


def _extract_response_id(events: list[dict[str, Any]]) -> str | None:
    for evt in events:
        resp = evt["data"].get("response", evt["data"])
        rid = resp.get("id")
        if rid:
            return rid
    return None


def _parse_sse_bytes(body: bytes) -> list[dict[str, Any]]:
    """Parse SSE events from a buffered response body (``_AsgiResponse.body``)."""
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None
    for raw in body.decode("utf-8").splitlines():
        line = raw.rstrip("\r")
        if not line:
            if current_type is not None:
                payload = json.loads(current_data) if current_data else {}
                events.append({"type": current_type, "data": payload})
            current_type = None
            current_data = None
            continue
        if line.startswith("event:"):
            current_type = line[len("event:") :].strip()
        elif line.startswith("data:"):
            current_data = line[len("data:") :].strip()
    if current_type is not None:
        payload = json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": payload})
    return events


class TestAsyncTerminalPersist:
    """The in-process streaming path defers the terminal write off the wire."""

    @pytest.mark.asyncio
    async def test_delete_is_bounded_when_deferred_write_stalls(self) -> None:
        release = asyncio.Event()
        provider = _ControllableProvider(InMemoryResponseProvider(), release=release)
        app = ResponsesAgentServerHost(
            store=provider,
            options=ResponsesServerOptions(shutdown_grace_period_seconds=1),
        )
        app.response_handler(_simple_completed_handler)
        client = _AsyncAsgiClient(app)

        post_response = await client.post(
            "/responses",
            json_body={"model": "m", "input": "hi", "stream": True, "store": True},
        )
        events = _parse_sse_bytes(post_response.body)
        response_id = _extract_response_id(events)
        assert response_id is not None
        await asyncio.wait_for(provider.update_started.wait(), 5)

        delete_task = asyncio.create_task(client.delete(f"/responses/{response_id}"))
        try:
            deleted = await asyncio.wait_for(delete_task, 2)
            assert deleted.status_code == 400
            assert deleted.json()["error"]["message"] == "Response persistence is still in progress. Retry deletion."
            assert not provider.delete_started.is_set()
        finally:
            release.set()
            await asyncio.wait_for(asyncio.gather(delete_task, return_exceptions=True), 5)

    @pytest.mark.asyncio
    async def test_delete_logs_concurrent_execution_failure_and_continues(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        drain_started = asyncio.Event()
        drain_release = asyncio.Event()
        provider = _ControllableProvider(InMemoryResponseProvider())
        app = _make_app(provider)
        client = _AsyncAsgiClient(app)

        async def _failing_drain(_ctx: Any, _state: Any) -> None:
            drain_started.set()
            await drain_release.wait()
            raise RuntimeError("deferred drain failed")

        monkeypatch.setattr(
            app._endpoint._orchestrator,  # pylint: disable=protected-access
            "_drain_deferred_terminal_persist",
            _failing_drain,
        )
        post_response = await client.post(
            "/responses",
            json_body={"model": "m", "input": "hi", "stream": True, "store": True},
        )
        events = _parse_sse_bytes(post_response.body)
        response_id = _extract_response_id(events)
        assert response_id is not None
        await asyncio.wait_for(drain_started.wait(), 5)

        delete_task = asyncio.create_task(client.delete(f"/responses/{response_id}"))
        try:
            await asyncio.sleep(0)
            assert not delete_task.done()
            drain_release.set()
            deleted = await asyncio.wait_for(delete_task, 5)
            assert deleted.status_code == 200
            assert deleted.json()["deleted"] is True
        finally:
            drain_release.set()
            await asyncio.wait_for(asyncio.gather(delete_task, return_exceptions=True), 5)

    @pytest.mark.asyncio
    async def test_shutdown_drains_fallback_created_before_pending_registration(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        release = asyncio.Event()
        provider = _ControllableProvider(InMemoryResponseProvider(), release=release)
        app = _make_app(provider)
        client = _AsyncAsgiClient(app)
        original_create_task = asyncio.create_task
        fallback_captured = asyncio.Event()
        captured: dict[str, Any] = {}

        def _delay_fallback_task(coro: Any, *args: Any, **kwargs: Any) -> Any:
            if getattr(getattr(coro, "cr_code", None), "co_name", "") == "_resilient_stream_fallback":
                captured["coro"] = coro
                captured["placeholder"] = asyncio.get_running_loop().create_future()
                fallback_captured.set()
                return captured["placeholder"]
            return original_create_task(coro, *args, **kwargs)

        monkeypatch.setattr(asyncio, "create_task", _delay_fallback_task)
        post_task = original_create_task(
            client.post(
                "/responses",
                json_body={"model": "m", "input": "hi", "stream": True, "store": True},
            )
        )
        fallback_task = None
        try:
            await asyncio.wait_for(fallback_captured.wait(), 5)
            shutdown_task = original_create_task(app._endpoint.handle_shutdown())
            done, _ = await asyncio.wait({shutdown_task}, timeout=0.25)
            shutdown_completed_before_registration = shutdown_task in done

            monkeypatch.setattr(asyncio, "create_task", original_create_task)
            fallback_task = original_create_task(captured["coro"])
            response = await asyncio.wait_for(post_task, 5)
            assert response.status_code == 200
            await asyncio.wait_for(provider.update_started.wait(), 5)
            release.set()
            await asyncio.wait_for(fallback_task, 5)
            await asyncio.wait_for(shutdown_task, 5)

            assert not shutdown_completed_before_registration, (
                "shutdown completed before the already-created fallback task registered itself"
            )
        finally:
            monkeypatch.setattr(asyncio, "create_task", original_create_task)
            release.set()
            placeholder = captured.get("placeholder")
            if placeholder is not None and not placeholder.done():
                placeholder.cancel()
            tasks = [post_task]
            if fallback_task is not None:
                tasks.append(fallback_task)
            if "shutdown_task" in locals():
                tasks.append(shutdown_task)
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), 5)

    @pytest.mark.asyncio
    async def test_rejected_admission_does_not_construct_handler(self, monkeypatch: pytest.MonkeyPatch) -> None:
        handler_called = False

        def _handler(_request: Any, _context: Any, _cancellation_signal: Any) -> Any:
            nonlocal handler_called
            handler_called = True

            async def _events():
                if False:
                    yield None

            return _events()

        app = _make_app(_ControllableProvider(InMemoryResponseProvider()))
        monkeypatch.setattr(
            app._endpoint._orchestrator,  # pylint: disable=protected-access
            "_create_fn",
            _handler,
        )
        await app._endpoint._runtime_state.begin_draining()  # pylint: disable=protected-access
        client = _AsyncAsgiClient(app)

        response = await client.post(
            "/responses",
            json_body={"model": "m", "input": "hi", "stream": True, "store": True},
        )

        assert response.status_code == 200
        assert handler_called is False

    @pytest.mark.asyncio
    async def test_cancelled_startup_discards_pending_record(self, monkeypatch: pytest.MonkeyPatch) -> None:
        startup_entered = asyncio.Event()
        startup_release = asyncio.Event()
        app = _make_app(_ControllableProvider(InMemoryResponseProvider()))
        client = _AsyncAsgiClient(app)

        async def _blocked_start(*_args: Any, **_kwargs: Any) -> None:
            startup_entered.set()
            await startup_release.wait()

        monkeypatch.setattr(
            app._endpoint._orchestrator,  # pylint: disable=protected-access
            "_start_resilient_background",
            _blocked_start,
        )
        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={"model": "m", "input": "hi", "stream": True, "store": True},
            )
        )
        try:
            await asyncio.wait_for(startup_entered.wait(), 5)
            post_task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await post_task
            assert await app._endpoint._runtime_state.list_records() == []  # pylint: disable=protected-access
        finally:
            startup_release.set()
            await asyncio.gather(post_task, return_exceptions=True)

    @pytest.mark.asyncio
    async def test_synchronous_handler_failure_closes_stream_and_discards_pending(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        app = _make_app(_ControllableProvider(InMemoryResponseProvider()))
        client = _AsyncAsgiClient(app)

        def _failing_handler(_request: Any, _context: Any, _cancellation_signal: Any) -> Any:
            raise RuntimeError("Simulated synchronous handler failure")

        monkeypatch.setattr(
            app._endpoint._orchestrator,  # pylint: disable=protected-access
            "_create_fn",
            _failing_handler,
        )

        response = await asyncio.wait_for(
            client.post(
                "/responses",
                json_body={"model": "m", "input": "hi", "stream": True, "store": True},
            ),
            5,
        )

        assert response.status_code == 200
        assert [event["type"] for event in _parse_sse_bytes(response.body)] == ["error"]
        assert await app._endpoint._runtime_state.list_records() == []  # pylint: disable=protected-access

    @pytest.mark.asyncio
    @pytest.mark.parametrize("background", [False, True])
    @pytest.mark.parametrize("empty_handler", [False, True])
    @pytest.mark.parametrize("cancel_delete", [False, True])
    async def test_delete_waits_for_deferred_write_without_resurrecting_response(
        self, background: bool, empty_handler: bool, cancel_delete: bool
    ) -> None:
        release = asyncio.Event()
        inner = InMemoryResponseProvider()
        provider = _ControllableProvider(
            inner,
            release=None if empty_handler else release,
            create_release=release if empty_handler else None,
        )
        app = _make_app(provider)
        if empty_handler:

            async def handler(_request: Any, _context: Any, _cancellation_signal: Any) -> Any:
                for event in ():
                    yield event

            app.response_handler(handler)
        client = _AsyncAsgiClient(app)
        post_response = await client.post(
            "/responses",
            json_body={"model": "m", "input": "hi", "stream": True, "store": True, "background": background},
        )
        assert post_response.status_code == 200
        events = _parse_sse_bytes(post_response.body)
        assert "response.completed" in [event["type"] for event in events]
        response_id = _extract_response_id(events)
        assert response_id is not None
        started = provider.create_started if empty_handler else provider.update_started
        await asyncio.wait_for(started.wait(), 5)
        record = await app._endpoint._runtime_state.get(response_id)
        assert record is not None and record.execution_task is not None
        execution_task = record.execution_task
        delete_task = asyncio.create_task(client.delete(f"/responses/{response_id}"))
        try:
            await asyncio.sleep(0)
            assert not delete_task.done()
            assert not provider.delete_started.is_set()
            if cancel_delete:
                delete_task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await delete_task
                assert not execution_task.done()
                delete_task = asyncio.create_task(client.delete(f"/responses/{response_id}"))
                await asyncio.sleep(0)
                assert not delete_task.done()
            release.set()
            deleted = await asyncio.wait_for(delete_task, 5)
            assert deleted.status_code == 200
            assert deleted.json()["deleted"] is True
            assert execution_task.done()
            assert provider.delete_started.is_set()
            assert (await client.get(f"/responses/{response_id}")).status_code == 404
            with pytest.raises(KeyError):
                await inner.get_response(response_id)
            restarted_client = _AsyncAsgiClient(ResponsesAgentServerHost(store=inner))
            assert (await restarted_client.get(f"/responses/{response_id}")).status_code == 404
        finally:
            release.set()
            await asyncio.wait_for(asyncio.gather(execution_task, delete_task, return_exceptions=True), 5)

    def test_terminal_completed_emitted_before_slow_write(self) -> None:
        """Client receives ``response.completed`` while the terminal write is
        still blocked — proving the last byte does not wait for the write."""
        release = asyncio.Event()
        provider = _ControllableProvider(InMemoryResponseProvider(), release=release)
        app = _make_app(provider)
        client = TestClient(app)

        response = client.post(
            "/responses",
            json={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "stream": True,
                "store": True,
            },
        )
        assert response.status_code == 200

        events = _collect_sse_events(response)
        event_types = [e["type"] for e in events]

        # The client got the success terminal even though the terminal write
        # is still blocked on ``release`` (never set before collection).
        assert "response.completed" in event_types, f"Missing response.completed in {event_types}"
        assert "response.failed" not in event_types, f"Unexpected response.failed in {event_types}"
        # The blocking write has NOT completed — the client did not wait for it.
        assert provider.update_completed is False

        # Release so the deferred persist (and app shutdown) can finish cleanly.
        release.set()

    @pytest.mark.asyncio
    async def test_get_during_deferral_window_returns_completed(self) -> None:
        """A GET issued while the terminal write is still pending serves the
        completed snapshot from in-memory runtime state."""
        release = asyncio.Event()
        provider = _ControllableProvider(InMemoryResponseProvider(), release=release)
        app = _make_app(provider)
        client = _AsyncAsgiClient(app)

        post_resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "stream": True,
                "store": True,
            },
        )
        assert post_resp.status_code == 200
        events = _parse_sse_bytes(post_resp.body)
        assert "response.completed" in [e["type"] for e in events]
        response_id = _extract_response_id(events)
        assert response_id is not None

        # Let the deferred persist begin and block on ``release``.
        for _ in range(100):
            if provider.update_started.is_set():
                break
            await asyncio.sleep(0.01)
        assert provider.update_started.is_set()
        assert provider.update_completed is False  # still within the deferral window

        # GET during the window returns the completed snapshot from memory.
        get_resp = await client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        body = get_resp.json()
        assert body["status"] == "completed"

        release.set()

    @pytest.mark.asyncio
    async def test_deferred_write_reaches_provider_after_release(self) -> None:
        """After the gate releases, the deferred terminal write actually
        resumes and reaches the backing provider — the eventual-persistence
        guarantee (the client already received ``response.completed`` before
        this write happened)."""
        release = asyncio.Event()
        provider = _ControllableProvider(InMemoryResponseProvider(), release=release)
        app = _make_app(provider)
        client = _AsyncAsgiClient(app)

        post_resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "stream": True,
                "store": True,
            },
        )
        assert post_resp.status_code == 200
        events = _parse_sse_bytes(post_resp.body)
        assert "response.completed" in [e["type"] for e in events]
        response_id = _extract_response_id(events)
        assert response_id is not None

        # Deferred write has begun but is gated (client already got the terminal).
        for _ in range(100):
            if provider.update_started.is_set():
                break
            await asyncio.sleep(0.01)
        assert provider.update_started.is_set()
        assert provider.update_completed is False

        # Release the gate and require the deferred write to actually resume and
        # reach the provider — this fails if the fallback task were cancelled
        # after the response closed instead of completing the write.
        release.set()
        for _ in range(200):
            if provider.update_completed:
                break
            await asyncio.sleep(0.01)
        assert provider.update_completed is True, "deferred terminal write never reached the provider"

        # The terminal is durably persisted in the backing provider.
        persisted = await provider._inner.get_response(response_id)  # pylint: disable=protected-access
        assert persisted is not None
        persisted_status = (
            persisted.get("status") if isinstance(persisted, dict) else getattr(persisted, "status", None)
        )
        assert persisted_status == "completed"

    @pytest.mark.asyncio
    async def test_replacement_record_retains_execution_task_during_deferral(self) -> None:
        """The Path-B record that replaces the one carrying ``execution_task``
        must keep that task while the deferred terminal write is in flight, so
        ``handle_shutdown`` drains the write instead of completing shutdown
        with ``execution_task is None`` and cancelling it."""
        release = asyncio.Event()
        provider = _ControllableProvider(InMemoryResponseProvider(), release=release)
        app = _make_app(provider)
        client = _AsyncAsgiClient(app)

        post_resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "stream": True,
                "store": True,
            },
        )
        assert post_resp.status_code == 200
        events = _parse_sse_bytes(post_resp.body)
        assert "response.completed" in [e["type"] for e in events]
        response_id = _extract_response_id(events)
        assert response_id is not None

        # Deferred write is in flight but gated.
        for _ in range(100):
            if provider.update_started.is_set():
                break
            await asyncio.sleep(0.01)
        assert provider.update_started.is_set()
        assert provider.update_completed is False

        # The record now live in runtime_state is the Path-B replacement. It must
        # still carry the in-flight execution task (not None, not done) so that
        # graceful shutdown waits for the deferred provider write.
        orchestrator = app._endpoint._orchestrator  # pylint: disable=protected-access
        record = await orchestrator._runtime_state.get(response_id)  # pylint: disable=protected-access
        assert record is not None
        assert record.execution_task is not None, "replacement record dropped execution_task"
        assert not record.execution_task.done()

        release.set()
        for _ in range(200):
            if provider.update_completed:
                break
            await asyncio.sleep(0.01)
        assert provider.update_completed is True

    @pytest.mark.asyncio
    async def test_deferred_update_failure_surfaces_via_get(self) -> None:
        """A deferred terminal-write failure surfaces on a later GET; the
        record is not evicted, and the client still saw ``response.completed``."""
        provider = _ControllableProvider(InMemoryResponseProvider(), fail_on_update=True)
        app = _make_app(provider)
        client = _AsyncAsgiClient(app)

        post_resp = await client.post(
            "/responses",
            json_body={
                "model": "test-model",
                "input": [{"role": "user", "content": "hi"}],
                "stream": True,
                "store": True,
            },
        )
        assert post_resp.status_code == 200
        events = _parse_sse_bytes(post_resp.body)
        event_types = [e["type"] for e in events]
        # Client received success terminal (failure deferred off the wire).
        assert "response.completed" in event_types
        assert "response.failed" not in event_types
        response_id = _extract_response_id(events)
        assert response_id is not None

        # Poll GET until the deferred write failure is stamped on the record.
        failed_body: dict[str, Any] = {}
        for _ in range(100):
            await asyncio.sleep(0.05)
            get_resp = await client.get(f"/responses/{response_id}")
            if get_resp.status_code == 200:
                failed_body = get_resp.json()
                if failed_body.get("status") == "failed":
                    break

        assert failed_body.get("status") == "failed", f"GET never reflected failure: {failed_body}"
        assert failed_body.get("error", {}).get("code") == "storage_error"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("background", [False, True])
    async def test_fallback_registers_drainable_record_before_first_event(self, background: bool) -> None:
        """The in-process fallback must publish a drainable record BEFORE the
        handler's first event.

        Until the first event triggers ``_register_bg_execution`` no record is
        in runtime state, so a graceful shutdown that snapshots ``list_records()``
        in this window would see no task and could cancel the fallback before its
        deferred terminal write. The fallback therefore pre-registers a record
        carrying its live ``execution_task`` up front."""
        first_gate = asyncio.Event()

        async def _gated_handler(request: Any, context: Any, _cancellation_signal: asyncio.Event):
            async def _events():
                # Block before the first event so the pre-registration window
                # (fallback started; nothing published by _register_bg_execution
                # yet) stays open for the assertions below.
                await first_gate.wait()
                stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
                yield stream.emit_created()
                for evt in stream.output_item_message("Hello, world!"):
                    yield evt
                yield stream.emit_completed()

            return _events()

        provider = _ControllableProvider(InMemoryResponseProvider())
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(_gated_handler)
        client = _AsyncAsgiClient(app)
        orchestrator = app._endpoint._orchestrator  # pylint: disable=protected-access

        # Drive the streaming POST concurrently; it blocks inside the handler on
        # ``first_gate`` before any event is emitted.
        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={
                    "model": "test-model",
                    "input": [{"role": "user", "content": "hi"}],
                    "stream": True,
                    "store": True,
                    "background": background,
                },
            )
        )
        try:
            record = None
            for _ in range(200):
                records = await orchestrator._runtime_state.list_records()  # pylint: disable=protected-access
                if records:
                    record = records[0]
                    break
                await asyncio.sleep(0.01)
            # The handler is still gated, so no event has been emitted yet.
            assert not first_gate.is_set()
            assert record is not None, "fallback did not pre-register a drainable record before the first event"
            assert record.status == "in_progress"
            # The record carries the live fallback task, so ``handle_shutdown``
            # drains it instead of racing loop teardown.
            assert record.execution_task is not None, "pre-registered record has no execution_task"
            assert not record.execution_task.done()
            assert not provider.create_started.is_set()
            assert (await client.get(f"/responses/{record.response_id}")).status_code == 404
            assert (await client.delete(f"/responses/{record.response_id}")).status_code == 404
        finally:
            first_gate.set()

        resp = await post_task
        assert resp.status_code == 200
        events = _parse_sse_bytes(resp.body)
        assert "response.completed" in [e["type"] for e in events]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("background", [False, True])
    async def test_pre_creation_error_discards_pending_shutdown_record(self, background: bool) -> None:
        async def handler(_request: Any, _context: Any, _cancellation_signal: Any) -> Any:
            for event in ():
                yield event
            raise RuntimeError("failure before response.created")

        provider = _ControllableProvider(InMemoryResponseProvider())
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(handler)
        client = _AsyncAsgiClient(app)
        response = await client.post(
            "/responses",
            json_body={"model": "m", "input": "hi", "stream": True, "store": True, "background": background},
        )
        assert response.status_code == 200
        assert [event["type"] for event in _parse_sse_bytes(response.body)] == ["error"]
        assert not provider.create_started.is_set()
        assert await app._endpoint._runtime_state.list_records() == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("background", [False, True])
    async def test_shutdown_before_first_event_drains_write_and_preserves_terminal(self, background: bool) -> None:
        started = asyncio.Event()
        first_gate = asyncio.Event()
        write_gate = asyncio.Event()

        async def handler(_request: Any, context: Any, _cancellation_signal: Any) -> Any:
            started.set()
            await first_gate.wait()
            stream = ResponseEventStream(response_id=context.response_id, model="m")
            yield stream.emit_created()
            yield stream.emit_completed()

        inner = InMemoryResponseProvider()
        provider = _ControllableProvider(inner, release=write_gate)
        app = ResponsesAgentServerHost(store=provider)
        app.response_handler(handler)
        client = _AsyncAsgiClient(app)
        post_task = asyncio.create_task(
            client.post(
                "/responses",
                json_body={"model": "m", "input": "hi", "stream": True, "store": True, "background": background},
            )
        )
        shutdown_task = None
        try:
            await asyncio.wait_for(started.wait(), 5)
            shutdown_task = asyncio.create_task(app._endpoint.handle_shutdown())
            await asyncio.sleep(0)
            assert not shutdown_task.done()
            first_gate.set()
            response = await asyncio.wait_for(post_task, 5)
            assert response.status_code == 200
            await asyncio.wait_for(provider.update_started.wait(), 5)
            assert not shutdown_task.done()
            write_gate.set()
            await asyncio.wait_for(shutdown_task, 5)
            events = _parse_sse_bytes(response.body)
            response_id = _extract_response_id(events)
            assert response_id is not None
            terminal = events[-1]["data"]["response"]
            persisted = await inner.get_response(response_id)
            assert persisted["status"] == terminal["status"]
        finally:
            first_gate.set()
            write_gate.set()
            tasks = [post_task] if shutdown_task is None else [post_task, shutdown_task]
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), 5)
