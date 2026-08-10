# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic activation receive-boundary regression tests."""

import asyncio
import json

import pytest
from starlette.websockets import WebSocket

from azure.ai.agentserver.invocations.voice import _host as voice_host

_TS = "2026-07-23T12:00:00.000Z"


def _receive_message(payload: dict) -> dict:
    return {"type": "websocket.receive", "text": json.dumps(payload)}


class _BlockedReadyTransport:
    def __init__(self) -> None:
        self.inbound: asyncio.Queue[dict] = asyncio.Queue()
        self.ready_entered = asyncio.Event()
        self.ready_cancelled = asyncio.Event()
        self.release_ready = asyncio.Event()
        self.close_entered = asyncio.Event()
        self.active_writes = 0
        self.max_active_writes = 0
        self.sent_closes: list[dict] = []

    async def receive(self) -> dict:
        return await self.inbound.get()

    async def send(self, message: dict) -> None:
        if message["type"] == "websocket.accept":
            return
        self.active_writes += 1
        self.max_active_writes = max(self.max_active_writes, self.active_writes)
        try:
            if message["type"] == "websocket.send":
                payload = json.loads(message["text"])
                if payload["type"] == "session.ready":
                    self.ready_entered.set()
                    while not self.release_ready.is_set():
                        try:
                            await self.release_ready.wait()
                        except asyncio.CancelledError:
                            self.ready_cancelled.set()
            elif message["type"] == "websocket.close":
                self.sent_closes.append(dict(message))
                self.close_entered.set()
        finally:
            self.active_writes -= 1

    def websocket(self) -> WebSocket:
        scope = {
            "type": "websocket",
            "path": "/invocations_ws",
            "headers": [],
            "query_string": b"",
            "scheme": "ws",
            "server": ("test", 80),
            "client": ("test", 1),
            "root_path": "",
            "subprotocols": [],
            "state": {},
        }
        return WebSocket(scope, self.receive, self.send)


def _start() -> dict:
    return {
        "type": "session.start",
        "id": "m_start",
        "ts": _TS,
        "protocol_version": "1.0",
        "reconnect": False,
        "response_timeouts": {
            "first_output_ms": 15_000,
            "idle_ms": 30_000,
            "max_duration_ms": 120_000,
        },
    }


def _user_message() -> dict:
    return {
        "type": "user.message",
        "id": "m_user",
        "ts": _TS,
        "item_id": "in_1",
        "content": [{"type": "input_text", "text": "hello"}],
    }


def _connection(websocket) -> voice_host._VoiceConnection:  # pylint: disable=protected-access
    return voice_host._VoiceConnection(  # pylint: disable=protected-access
        websocket=websocket,
        on_session_start=None,
        on_user_message=None,
        on_user_no_input=None,
        on_user_speech_started=None,
        on_handoff_failed=None,
        on_barge_in=None,
        on_response_timeout=None,
        on_session_end=None,
    )


async def _require_task_done(task: asyncio.Task, *, timeout: float = 1.0) -> None:
    done, _ = await asyncio.wait((task,), timeout=timeout)
    if task in done:
        return
    task.cancel()
    done, _ = await asyncio.wait((task,), timeout=timeout)
    if task in done:
        await asyncio.gather(task, return_exceptions=True)
        pytest.fail(f"{task.get_name()} exceeded its hard completion deadline")

    current = asyncio.current_task()
    pending = {candidate for candidate in asyncio.all_tasks() if candidate is not current and not candidate.done()}
    for candidate in pending:
        try:
            candidate.get_coro().close()
        except RuntimeError:
            pass
        candidate.cancel()
    await asyncio.sleep(0)
    completed = {candidate for candidate in pending if candidate.done()}
    if completed:
        await asyncio.gather(*completed, return_exceptions=True)
    pytest.fail(f"{task.get_name()} ignored cancellation after its hard completion deadline")


class _ControlledSendLock:
    """Test lock that exposes the pre-transport send-lock wait boundary."""

    def __init__(self) -> None:
        self.acquire_started = asyncio.Event()
        self.allow_acquire = asyncio.Event()

    async def acquire(self) -> bool:
        self.acquire_started.set()
        await self.allow_acquire.wait()
        return True

    def release(self) -> None:
        return None


class _ResistantReadyWebSocket:
    def __init__(self) -> None:
        self.inbound: asyncio.Queue[dict] = asyncio.Queue()
        self.ready_wire_visible = asyncio.Event()
        self.ready_cancelled = asyncio.Event()
        self.release_ready = asyncio.Event()
        self.close_entered = asyncio.Event()
        self.closes: list[dict] = []
        self.active_writes = 0
        self.max_active_writes = 0

    async def receive(self) -> dict:
        return await self.inbound.get()

    async def send_text(self, data: str) -> None:
        payload = json.loads(data)
        self.active_writes += 1
        self.max_active_writes = max(self.max_active_writes, self.active_writes)
        try:
            if payload["type"] != "session.ready":
                return
            self.ready_wire_visible.set()
            while not self.release_ready.is_set():
                try:
                    await self.release_ready.wait()
                except asyncio.CancelledError:
                    self.ready_cancelled.set()
        finally:
            self.active_writes -= 1

    async def close(self, **fields) -> None:
        self.active_writes += 1
        self.max_active_writes = max(self.max_active_writes, self.active_writes)
        self.closes.append(fields)
        self.close_entered.set()
        self.active_writes -= 1


@pytest.mark.parametrize("eager", [False, True])
def test_frame_received_while_ready_waits_for_send_lock_is_rejected(eager: bool) -> None:
    async def scenario() -> None:
        loop = asyncio.get_running_loop()
        original_factory = loop.get_task_factory()
        baseline_termination_tasks = (
            voice_host._GLOBAL_TERMINATION_TASK_RESERVATIONS  # pylint: disable=protected-access
        )
        if eager:
            eager_factory = getattr(asyncio, "eager_task_factory", None)
            if eager_factory is None:
                pytest.skip("asyncio.eager_task_factory requires Python 3.12+")
            loop.set_task_factory(eager_factory)

        class LockedSendWebSocket:
            def __init__(self) -> None:
                self.inbound: asyncio.Future[dict] = loop.create_future()
                self.sent: list[dict] = []
                self.closes: list[dict] = []

            async def receive(self) -> dict:
                return await self.inbound

            async def send_text(self, data: str) -> None:
                self.sent.append(json.loads(data))

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        try:
            websocket = LockedSendWebSocket()
            connection = _connection(websocket)
            send_lock = _ControlledSendLock()
            connection._send_lock = send_lock  # type: ignore[assignment]  # pylint: disable=protected-access
            gate = asyncio.create_task(
                connection._send_ready_with_receive_gate(),  # pylint: disable=protected-access
                name="test_ready_gate",
            )
            await send_lock.acquire_started.wait()
            websocket.inbound.set_result(_receive_message(_user_message()))
            await asyncio.sleep(0)
            send_lock.allow_acquire.set()

            assert not await gate
            assert [message["type"] for message in websocket.sent] == ["session.rejected"]
            assert websocket.closes[-1]["code"] == 1008
            await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access
            assert (
                voice_host._GLOBAL_TERMINATION_TASK_RESERVATIONS == baseline_termination_tasks
            )  # pylint: disable=protected-access
        finally:
            loop.set_task_factory(original_factory)

    asyncio.run(scenario())


def test_frame_received_after_ready_transport_attempt_is_preserved() -> None:
    async def scenario() -> None:
        loop = asyncio.get_running_loop()

        class BlockedTransportWebSocket:
            def __init__(self) -> None:
                self.inbound: asyncio.Future[dict] = loop.create_future()
                self.ready_transport_entered = asyncio.Event()
                self.release_ready = asyncio.Event()
                self.sent: list[dict] = []

            async def receive(self) -> dict:
                return await self.inbound

            async def send_text(self, data: str) -> None:
                payload = json.loads(data)
                self.sent.append(payload)
                if payload["type"] == "session.ready":
                    self.ready_transport_entered.set()
                    await self.release_ready.wait()

            async def close(self, **_fields) -> None:
                return None

        websocket = BlockedTransportWebSocket()
        connection = _connection(websocket)
        gate = asyncio.create_task(
            connection._send_ready_with_receive_gate(),  # pylint: disable=protected-access
            name="test_ready_gate",
        )
        await websocket.ready_transport_entered.wait()
        websocket.inbound.set_result(_receive_message(_user_message()))
        await asyncio.sleep(0)
        assert not gate.done()
        websocket.release_ready.set()

        assert await gate
        receive_task = connection._prefetched_receive_task  # pylint: disable=protected-access
        assert receive_task is not None
        assert (await receive_task)["type"] == "user.message"
        connection._prefetched_receive_task = None  # pylint: disable=protected-access
        await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_post_ready_frame_dispatches_while_send_continuation_is_blocked() -> None:
    async def scenario() -> None:
        class BlockedReadyContinuationWebSocket:
            def __init__(self) -> None:
                self.inbound: asyncio.Queue[dict] = asyncio.Queue()
                self.ready_wire_visible = asyncio.Event()
                self.release_ready = asyncio.Event()
                self.sent: list[dict] = []

            async def receive(self) -> dict:
                return await self.inbound.get()

            async def send_text(self, data: str) -> None:
                payload = json.loads(data)
                self.sent.append(payload)
                if payload["type"] == "session.ready":
                    self.ready_wire_visible.set()
                    await self.release_ready.wait()

            async def close(self, **_fields) -> None:
                return None

        websocket = BlockedReadyContinuationWebSocket()
        callback_started = asyncio.Event()
        callback_completed = asyncio.Event()

        async def on_user_message(_session, _event, response) -> None:
            callback_started.set()
            await response.decline()
            callback_completed.set()

        connection = voice_host._VoiceConnection(  # pylint: disable=protected-access
            websocket=websocket,
            on_session_start=None,
            on_user_message=on_user_message,
            on_user_no_input=None,
            on_user_speech_started=None,
            on_handoff_failed=None,
            on_barge_in=None,
            on_response_timeout=None,
            on_session_end=None,
        )
        await websocket.inbound.put(_receive_message(_start()))
        run_task = asyncio.create_task(connection.run(), name="test_voice_connection")
        try:
            await asyncio.wait_for(websocket.ready_wire_visible.wait(), timeout=1.0)
            await websocket.inbound.put(_receive_message(_user_message()))

            await asyncio.wait_for(callback_started.wait(), timeout=1.0)
            assert not websocket.release_ready.is_set()
            assert not callback_completed.is_set()
            assert [message["type"] for message in websocket.sent] == ["session.ready"]
            pending_ready_send = connection._pending_ready_send_task  # pylint: disable=protected-access
            assert pending_ready_send is not None

            websocket.release_ready.set()
            await asyncio.wait_for(callback_completed.wait(), timeout=1.0)
        finally:
            websocket.release_ready.set()
            await websocket.inbound.put({"type": "websocket.disconnect", "code": 1000})
            await _require_task_done(run_task)
            await run_task

        assert pending_ready_send.done()
        assert connection._pending_ready_send_task is None  # pylint: disable=protected-access
        assert pending_ready_send not in voice_host._GLOBAL_RUNTIME_TASKS  # pylint: disable=protected-access
        assert [message["type"] for message in websocket.sent] == ["session.ready", "response.none"]

    asyncio.run(scenario())


def test_post_ready_send_failure_stops_dispatched_callback() -> None:
    async def scenario() -> None:
        class FailingReadyContinuationWebSocket:
            def __init__(self) -> None:
                self.inbound: asyncio.Queue[dict] = asyncio.Queue()
                self.ready_wire_visible = asyncio.Event()
                self.fail_ready = asyncio.Event()
                self.sent: list[dict] = []
                self.closes: list[dict] = []

            async def receive(self) -> dict:
                return await self.inbound.get()

            async def send_text(self, data: str) -> None:
                payload = json.loads(data)
                self.sent.append(payload)
                if payload["type"] == "session.ready":
                    self.ready_wire_visible.set()
                    await self.fail_ready.wait()
                    raise RuntimeError("readiness continuation failed")

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        websocket = FailingReadyContinuationWebSocket()
        callback_started = asyncio.Event()
        callback_cancelled = asyncio.Event()

        async def on_user_message(_session, _event, _response) -> None:
            callback_started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                callback_cancelled.set()
                raise

        connection = voice_host._VoiceConnection(  # pylint: disable=protected-access
            websocket=websocket,
            on_session_start=None,
            on_user_message=on_user_message,
            on_user_no_input=None,
            on_user_speech_started=None,
            on_handoff_failed=None,
            on_barge_in=None,
            on_response_timeout=None,
            on_session_end=None,
        )
        await websocket.inbound.put(_receive_message(_start()))
        run_task = asyncio.create_task(connection.run(), name="test_voice_connection")
        try:
            await asyncio.wait_for(websocket.ready_wire_visible.wait(), timeout=1.0)
            await websocket.inbound.put(_receive_message(_user_message()))
            await asyncio.wait_for(callback_started.wait(), timeout=1.0)
            pending_ready_send = connection._pending_ready_send_task  # pylint: disable=protected-access
            assert pending_ready_send is not None

            websocket.fail_ready.set()
            await _require_task_done(run_task)
            await run_task
        finally:
            websocket.fail_ready.set()
            if not run_task.done():
                run_task.cancel()
            await _require_task_done(run_task)
            await asyncio.gather(run_task, return_exceptions=True)

        assert callback_cancelled.is_set()
        assert pending_ready_send.done()
        assert connection._pending_ready_send_task is None  # pylint: disable=protected-access
        assert [message["type"] for message in websocket.sent] == ["session.ready"]
        assert [close["code"] for close in websocket.closes] == [1011]

    asyncio.run(scenario())


def test_shutdown_retains_cancellation_resistant_ready_send_until_done(monkeypatch) -> None:
    monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.02)

    async def scenario() -> None:
        class ResistantReadyContinuationWebSocket:
            def __init__(self) -> None:
                self.inbound: asyncio.Queue[dict] = asyncio.Queue()
                self.ready_wire_visible = asyncio.Event()
                self.ready_cancelled = asyncio.Event()
                self.release_ready = asyncio.Event()

            async def receive(self) -> dict:
                return await self.inbound.get()

            async def send_text(self, data: str) -> None:
                payload = json.loads(data)
                if payload["type"] != "session.ready":
                    return
                self.ready_wire_visible.set()
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    self.ready_cancelled.set()
                    await self.release_ready.wait()

            async def close(self, **_fields) -> None:
                return None

        websocket = ResistantReadyContinuationWebSocket()
        callback_started = asyncio.Event()

        async def on_user_message(_session, _event, _response) -> None:
            callback_started.set()
            await asyncio.Event().wait()

        connection = voice_host._VoiceConnection(  # pylint: disable=protected-access
            websocket=websocket,
            on_session_start=None,
            on_user_message=on_user_message,
            on_user_no_input=None,
            on_user_speech_started=None,
            on_handoff_failed=None,
            on_barge_in=None,
            on_response_timeout=None,
            on_session_end=None,
        )
        await websocket.inbound.put(_receive_message(_start()))
        run_task = asyncio.create_task(connection.run(), name="test_voice_connection")
        try:
            await asyncio.wait_for(websocket.ready_wire_visible.wait(), timeout=1.0)
            await websocket.inbound.put(_receive_message(_user_message()))
            await asyncio.wait_for(callback_started.wait(), timeout=1.0)
            pending_ready_send = connection._pending_ready_send_task  # pylint: disable=protected-access
            assert pending_ready_send is not None

            await websocket.inbound.put({"type": "websocket.disconnect", "code": 1000})
            await asyncio.wait_for(websocket.ready_cancelled.wait(), timeout=1.0)
            await _require_task_done(run_task)
            await run_task

            assert pending_ready_send in voice_host._GLOBAL_RUNTIME_TASKS  # pylint: disable=protected-access
            assert connection._pending_ready_send_task is None  # pylint: disable=protected-access

            globally_released = asyncio.Event()
            pending_ready_send.add_done_callback(lambda _task: globally_released.set())
            websocket.release_ready.set()
            await asyncio.wait_for(globally_released.wait(), timeout=1.0)
            assert pending_ready_send not in voice_host._GLOBAL_RUNTIME_TASKS  # pylint: disable=protected-access
        finally:
            websocket.release_ready.set()
            if not run_task.done():
                run_task.cancel()
            await _require_task_done(run_task)
            await asyncio.gather(run_task, return_exceptions=True)

    asyncio.run(scenario())


@pytest.mark.parametrize("terminal_kind", ["owner_cancel", "protocol_error"])
def test_resistant_ready_send_cannot_block_terminal_cleanup_or_race_close(monkeypatch, terminal_kind: str) -> None:
    monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.02)

    async def scenario() -> None:
        baseline_bytes = voice_host._GLOBAL_CUSTOMER_TASK_BYTES  # pylint: disable=protected-access
        websocket = _ResistantReadyWebSocket()
        connection = voice_host._VoiceConnection(  # pylint: disable=protected-access
            websocket=websocket,
            on_session_start=None,
            on_user_message=lambda *_args: asyncio.sleep(0),
            on_user_no_input=None,
            on_user_speech_started=None,
            on_handoff_failed=None,
            on_barge_in=None,
            on_response_timeout=None,
            on_session_end=None,
        )
        await websocket.inbound.put(_receive_message(_start()))
        run_task = asyncio.create_task(connection.run(), name="test_voice_connection")
        try:
            await asyncio.wait_for(websocket.ready_wire_visible.wait(), timeout=1.0)
            pending_ready_send = connection._pending_ready_send_task  # pylint: disable=protected-access
            assert pending_ready_send is not None

            if terminal_kind == "owner_cancel":
                run_task.cancel()
            else:
                invalid_post_ready = _start()
                invalid_post_ready["id"] = "m_second_start"
                await websocket.inbound.put(_receive_message(invalid_post_ready))

            await asyncio.wait_for(websocket.ready_cancelled.wait(), timeout=1.0)
            await _require_task_done(run_task)
            if terminal_kind == "owner_cancel":
                with pytest.raises(asyncio.CancelledError):
                    await run_task
            else:
                await run_task

            assert pending_ready_send in voice_host._GLOBAL_RUNTIME_TASKS  # pylint: disable=protected-access
            assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES > baseline_bytes  # pylint: disable=protected-access
            assert websocket.max_active_writes == 1
            assert not websocket.close_entered.is_set()

            globally_released = asyncio.Event()
            pending_ready_send.add_done_callback(lambda _task: globally_released.set())
            websocket.release_ready.set()
            await asyncio.wait_for(globally_released.wait(), timeout=1.0)
            if terminal_kind == "protocol_error":
                await asyncio.wait_for(websocket.close_entered.wait(), timeout=1.0)
                assert websocket.closes == [{"code": 1008, "reason": "Protocol error"}]
            else:
                assert not websocket.close_entered.is_set()
                assert not websocket.closes
            await asyncio.sleep(0)
            assert pending_ready_send not in voice_host._GLOBAL_RUNTIME_TASKS  # pylint: disable=protected-access
            assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == baseline_bytes  # pylint: disable=protected-access
        finally:
            websocket.release_ready.set()
            if not run_task.done():
                run_task.cancel()
            await _require_task_done(run_task)
            await asyncio.gather(run_task, return_exceptions=True)

    asyncio.run(scenario())


def test_parent_websocket_finalizer_does_not_overtake_retained_voice_close(monkeypatch) -> None:
    monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.02)

    async def scenario() -> None:
        app = voice_host.VoiceAgentServerHost(configure_observability=None)

        @app.on_user_message
        async def on_user_message(_session, _event, _response) -> None:
            return None

        transport = _BlockedReadyTransport()
        websocket = transport.websocket()
        await transport.inbound.put({"type": "websocket.connect"})
        await transport.inbound.put(_receive_message(_start()))
        endpoint = asyncio.create_task(
            app._ws_endpoint(websocket), name="test_voice_ws_endpoint"
        )  # pylint: disable=protected-access
        try:
            await asyncio.wait_for(transport.ready_entered.wait(), timeout=1.0)
            invalid_post_ready = _start()
            invalid_post_ready["id"] = "m_second_start"
            await transport.inbound.put(_receive_message(invalid_post_ready))
            await asyncio.wait_for(transport.ready_cancelled.wait(), timeout=1.0)
            await _require_task_done(endpoint)
            await endpoint

            assert not transport.sent_closes
            assert transport.max_active_writes == 1

            transport.release_ready.set()
            await asyncio.wait_for(transport.close_entered.wait(), timeout=1.0)
            assert [message["code"] for message in transport.sent_closes] == [1008]
            assert transport.max_active_writes == 1
        finally:
            transport.release_ready.set()
            if not endpoint.done():
                endpoint.cancel()
            await _require_task_done(endpoint)
            await asyncio.gather(endpoint, return_exceptions=True)

    asyncio.run(scenario())


def test_parent_does_not_close_over_active_write_when_close_owner_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.02)

    async def scenario() -> None:
        app = voice_host.VoiceAgentServerHost(configure_observability=None)

        @app.on_user_message
        async def on_user_message(_session, _event, _response) -> None:
            return None

        original_create_runtime_task = (
            voice_host._VoiceConnection._create_runtime_task
        )  # pylint: disable=protected-access
        retained_ready: list[asyncio.Task] = []

        def fail_close_owner(self, coroutine, *, name, termination=False, direct=False):
            if name in ("voice_connection_close", "voice_connection_factory_close"):
                if not retained_ready:
                    pending_ready = self._pending_ready_send_task  # pylint: disable=protected-access
                    assert pending_ready is not None
                    retained_ready.append(pending_ready)
                coroutine.close()
                raise RuntimeError("close owner unavailable")
            return original_create_runtime_task(
                self,
                coroutine,
                name=name,
                termination=termination,
                direct=direct,
            )

        monkeypatch.setattr(voice_host._VoiceConnection, "_create_runtime_task", fail_close_owner)
        transport = _BlockedReadyTransport()
        websocket = transport.websocket()
        await transport.inbound.put({"type": "websocket.connect"})
        await transport.inbound.put(_receive_message(_start()))
        endpoint = asyncio.create_task(
            app._ws_endpoint(websocket), name="test_voice_ws_endpoint"
        )  # pylint: disable=protected-access
        try:
            await asyncio.wait_for(transport.ready_entered.wait(), timeout=1.0)
            invalid_post_ready = _start()
            invalid_post_ready["id"] = "m_second_start"
            await transport.inbound.put(_receive_message(invalid_post_ready))
            await asyncio.wait_for(transport.ready_cancelled.wait(), timeout=1.0)
            await _require_task_done(endpoint)
            await endpoint

            assert len(retained_ready) == 1
            assert retained_ready[0] in voice_host._GLOBAL_RUNTIME_TASKS  # pylint: disable=protected-access
            assert not transport.sent_closes
            assert not transport.close_entered.is_set()
            assert transport.max_active_writes == 1

            released = asyncio.Event()
            retained_ready[0].add_done_callback(lambda _task: released.set())
            transport.release_ready.set()
            await asyncio.wait_for(released.wait(), timeout=1.0)
            assert retained_ready[0] not in voice_host._GLOBAL_RUNTIME_TASKS  # pylint: disable=protected-access
            assert not transport.sent_closes
            assert transport.max_active_writes == 1
        finally:
            transport.release_ready.set()
            if not endpoint.done():
                endpoint.cancel()
            await _require_task_done(endpoint)
            await asyncio.gather(endpoint, return_exceptions=True)

    asyncio.run(scenario())


def test_late_owned_close_failure_is_reported_without_second_transport_attempt(caplog) -> None:
    async def scenario() -> None:
        app = voice_host.VoiceAgentServerHost(configure_observability=None)
        close_entered = asyncio.Event()
        fail_close = asyncio.Event()
        ready_started = asyncio.Event()
        release_ready = asyncio.Event()
        close_attempts = 0

        async def receive() -> dict:
            return {"type": "websocket.connect"}

        async def send(message: dict) -> None:
            nonlocal close_attempts
            if message["type"] == "websocket.close":
                close_attempts += 1
                close_entered.set()
                await fail_close.wait()
                raise RuntimeError("transport close failed")

        async def resistant_ready() -> None:
            ready_started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                await release_ready.wait()

        scope = {
            "type": "websocket",
            "path": "/invocations_ws",
            "headers": [],
            "query_string": b"",
            "scheme": "ws",
            "server": ("test", 80),
            "client": ("test", 1),
            "root_path": "",
            "subprotocols": [],
            "state": {},
        }
        websocket = WebSocket(scope, receive, send)
        await websocket.accept()
        connection = _connection(websocket)
        pending_ready = asyncio.create_task(resistant_ready(), name="test_resistant_ready")
        await ready_started.wait()
        connection._pending_ready_send_task = pending_ready  # pylint: disable=protected-access
        await connection._send_lock.acquire()  # pylint: disable=protected-access
        try:
            await connection._close(code=1008, reason="Protocol error")  # pylint: disable=protected-access
            close_task = connection._pending_close_task  # pylint: disable=protected-access
            assert close_task is not None
            await app._finalize_session(  # pylint: disable=protected-access
                websocket=websocket,
                session_id="test-session",
                start_ns=0,
                close_code=1008,
                error_code="protocol_error",
            )
            assert close_attempts == 0

            connection._send_lock.release()  # pylint: disable=protected-access
            await asyncio.wait_for(close_entered.wait(), timeout=1.0)
            fail_close.set()
            await asyncio.gather(close_task, return_exceptions=True)
            await asyncio.sleep(0)

            assert close_attempts == 1
            assert "Voice WebSocket close failed: RuntimeError" in caplog.text
        finally:
            if connection._send_lock.locked():  # pylint: disable=protected-access
                connection._send_lock.release()  # pylint: disable=protected-access
            fail_close.set()
            release_ready.set()
            if not pending_ready.done():
                pending_ready.cancel()
            await asyncio.gather(pending_ready, return_exceptions=True)

    asyncio.run(scenario())


def test_runtime_task_admission_is_bounded(monkeypatch) -> None:
    async def scenario() -> None:
        baseline = voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS  # pylint: disable=protected-access
        monkeypatch.setattr(voice_host, "_MAX_GLOBAL_RUNTIME_TASKS", baseline + 1)
        connection = _connection(None)
        release = asyncio.Event()

        first = connection._create_runtime_task(
            release.wait(), name="test_runtime_owner"
        )  # pylint: disable=protected-access
        with pytest.raises(RuntimeError, match="Voice global runtime task limit reached"):
            connection._create_runtime_task(  # pylint: disable=protected-access
                asyncio.Event().wait(),
                name="test_runtime_overflow",
            )

        assert voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS == baseline + 1  # pylint: disable=protected-access
        released = asyncio.Event()
        first.add_done_callback(lambda _task: released.set())
        release.set()
        await asyncio.wait_for(released.wait(), timeout=1.0)
        assert voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS == baseline  # pylint: disable=protected-access
        assert first not in voice_host._GLOBAL_RUNTIME_TASKS  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_termination_task_creation_failure_rolls_back_reservations(monkeypatch) -> None:
    async def scenario() -> None:
        baseline_tasks = voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS  # pylint: disable=protected-access
        baseline_termination_tasks = (
            voice_host._GLOBAL_TERMINATION_TASK_RESERVATIONS  # pylint: disable=protected-access
        )
        baseline_bytes = voice_host._GLOBAL_CUSTOMER_TASK_BYTES  # pylint: disable=protected-access
        lease = voice_host._reserve_session_retention(19)  # pylint: disable=protected-access
        assert lease is not None
        connection = _connection(None)
        connection._session_retention = lease  # pylint: disable=protected-access

        def fail_create_task(_coroutine, *, name=None, context=None):
            del name, context
            raise RuntimeError("termination task creation failed")

        monkeypatch.setattr(voice_host.asyncio, "create_task", fail_create_task)
        with pytest.raises(RuntimeError, match="termination task creation failed"):
            connection._create_runtime_task(  # pylint: disable=protected-access
                asyncio.Event().wait(),
                name="test_termination_creation_failure",
                termination=True,
            )

        assert lease.references == 1
        assert voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS == baseline_tasks  # pylint: disable=protected-access
        assert (
            voice_host._GLOBAL_TERMINATION_TASK_RESERVATIONS == baseline_termination_tasks
        )  # pylint: disable=protected-access
        assert not voice_host._GLOBAL_TERMINATION_TASKS  # pylint: disable=protected-access
        connection._release_connection_state()  # pylint: disable=protected-access
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == baseline_bytes  # pylint: disable=protected-access

    asyncio.run(scenario())


@pytest.mark.parametrize("outcome", ["raised", "cancelled", "failed"])
def test_unusable_direct_close_uses_factory_fallback(monkeypatch, outcome: str) -> None:
    async def scenario() -> None:
        baseline_tasks = voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS  # pylint: disable=protected-access
        baseline_termination_tasks = (
            voice_host._GLOBAL_TERMINATION_TASK_RESERVATIONS  # pylint: disable=protected-access
        )

        class RecordingWebSocket:
            def __init__(self) -> None:
                self.closes: list[dict] = []

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        websocket = RecordingWebSocket()
        connection = _connection(websocket)
        original_create_runtime_task = connection._create_runtime_task  # pylint: disable=protected-access

        def unusable_direct_close(coroutine, *, name, termination=False, direct=False):
            if not direct:
                return original_create_runtime_task(
                    coroutine,
                    name=name,
                    termination=termination,
                    direct=direct,
                )
            coroutine.close()
            if outcome == "raised":
                raise RuntimeError("close task creation failed")
            task = asyncio.get_running_loop().create_future()
            if outcome == "cancelled":
                task.cancel()
            else:
                task.set_exception(RuntimeError("close task failed"))
            return task

        monkeypatch.setattr(connection, "_create_runtime_task", unusable_direct_close)
        await connection._close(code=1008, reason="Protocol error")  # pylint: disable=protected-access
        await asyncio.sleep(0)

        assert websocket.closes == [{"code": 1008, "reason": "Protocol error"}]
        assert connection._pending_close_task is None  # pylint: disable=protected-access
        assert voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS == baseline_tasks  # pylint: disable=protected-access
        assert (
            voice_host._GLOBAL_TERMINATION_TASK_RESERVATIONS == baseline_termination_tasks
        )  # pylint: disable=protected-access

    asyncio.run(scenario())


@pytest.mark.parametrize("outcome", ["cancelled", "failed"])
def test_unusable_factory_close_relinquishes_parent_ownership(monkeypatch, outcome: str) -> None:
    async def scenario() -> None:
        app = voice_host.VoiceAgentServerHost(configure_observability=None)
        sent: list[dict] = []
        inbound = iter(({"type": "websocket.connect"},))

        async def receive() -> dict:
            return next(inbound)

        async def send(message: dict) -> None:
            sent.append(dict(message))

        scope = {
            "type": "websocket",
            "path": "/invocations_ws",
            "headers": [],
            "query_string": b"",
            "scheme": "ws",
            "server": ("test", 80),
            "client": ("test", 1),
            "root_path": "",
            "subprotocols": [],
            "state": {},
        }
        websocket = WebSocket(scope, receive, send)
        await websocket.accept()
        connection = _connection(websocket)
        original_create_runtime_task = connection._create_runtime_task  # pylint: disable=protected-access
        original_create_task = asyncio.create_task

        def fail_direct_close(coroutine, *, name, termination=False, direct=False):
            if direct:
                coroutine.close()
                raise RuntimeError("direct close creation failed")
            return original_create_runtime_task(
                coroutine,
                name=name,
                termination=termination,
                direct=direct,
            )

        def unusable_factory_close(coroutine, *, name=None, context=None):
            if name != "voice_connection_factory_close":
                if context is None:
                    return original_create_task(coroutine, name=name)
                return original_create_task(coroutine, name=name, context=context)
            coroutine.close()

            async def finish_unusable() -> None:
                await asyncio.sleep(0)
                if outcome == "cancelled":
                    raise asyncio.CancelledError()
                raise RuntimeError("factory close failed")

            return original_create_task(finish_unusable(), name=name)

        monkeypatch.setattr(connection, "_create_runtime_task", fail_direct_close)
        monkeypatch.setattr(voice_host.asyncio, "create_task", unusable_factory_close)
        await connection._close(code=1008, reason="Protocol error")  # pylint: disable=protected-access

        assert [message for message in sent if message["type"] == "websocket.close"] == []
        await app._finalize_session(  # pylint: disable=protected-access
            websocket=websocket,
            session_id="test-session",
            start_ns=0,
            close_code=1008,
            error_code="protocol_error",
        )
        await asyncio.sleep(0)

        closes = [message for message in sent if message["type"] == "websocket.close"]
        assert [message["code"] for message in closes] == [1008]

    asyncio.run(scenario())


def test_pending_cancelling_factory_close_does_not_start_a_second_close(monkeypatch) -> None:
    async def scenario() -> None:
        class CancellationResistantCloseWebSocket:
            def __init__(self) -> None:
                self.close_calls = 0

            async def close(self, **_fields) -> None:
                self.close_calls += 1
                try:
                    await asyncio.sleep(0)
                except asyncio.CancelledError:
                    await asyncio.sleep(0)

        websocket = CancellationResistantCloseWebSocket()
        connection = _connection(websocket)
        original_create_runtime_task = connection._create_runtime_task  # pylint: disable=protected-access
        original_create_task = asyncio.create_task

        def fail_direct_close(coroutine, *, name, termination=False, direct=False):
            if direct:
                coroutine.close()
                raise RuntimeError("direct close creation failed")
            return original_create_runtime_task(
                coroutine,
                name=name,
                termination=termination,
                direct=direct,
            )

        def cancelling_factory_close(coroutine, *, name=None, context=None):
            if context is None:
                task = original_create_task(coroutine, name=name)
            else:
                task = original_create_task(coroutine, name=name, context=context)
            if name == "voice_connection_factory_close":
                asyncio.get_running_loop().call_soon(task.cancel)
            return task

        monkeypatch.setattr(connection, "_create_runtime_task", fail_direct_close)
        monkeypatch.setattr(voice_host.asyncio, "create_task", cancelling_factory_close)
        await connection._close(code=1008, reason="Protocol error")  # pylint: disable=protected-access
        await asyncio.sleep(0)

        assert websocket.close_calls == 1

    asyncio.run(scenario())


def test_ready_wrapper_admission_failure_retains_transferred_receive(monkeypatch) -> None:
    monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.02)

    async def scenario() -> None:
        baseline_tasks = voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS  # pylint: disable=protected-access
        baseline_termination_tasks = (
            voice_host._GLOBAL_TERMINATION_TASK_RESERVATIONS  # pylint: disable=protected-access
        )
        baseline_bytes = voice_host._GLOBAL_CUSTOMER_TASK_BYTES  # pylint: disable=protected-access
        monkeypatch.setattr(voice_host, "_MAX_GLOBAL_RUNTIME_TASKS", baseline_tasks + 1)

        class ResistantActivationReceiveWebSocket:
            def __init__(self) -> None:
                self.receive_count = 0
                self.receive_cancelled = asyncio.Event()
                self.release_receive = asyncio.Event()
                self.closes: list[dict] = []

            async def receive(self) -> dict:
                self.receive_count += 1
                if self.receive_count == 1:
                    return _receive_message(_start())
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    self.receive_cancelled.set()
                    await self.release_receive.wait()
                return {"type": "websocket.disconnect", "code": 1000}

            async def send_text(self, _data: str) -> None:
                raise AssertionError("ready transport must not be entered")

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        websocket = ResistantActivationReceiveWebSocket()

        async def on_user_message(_session, _event, _response) -> None:
            return None

        connection = voice_host._VoiceConnection(  # pylint: disable=protected-access
            websocket=websocket,
            on_session_start=None,
            on_user_message=on_user_message,
            on_user_no_input=None,
            on_user_speech_started=None,
            on_handoff_failed=None,
            on_barge_in=None,
            on_response_timeout=None,
            on_session_end=None,
        )
        run_task = asyncio.create_task(connection.run(), name="test_voice_connection")
        try:
            await asyncio.wait_for(websocket.receive_cancelled.wait(), timeout=1.0)
            await _require_task_done(run_task)
            await run_task
            assert websocket.closes == [{"code": 1011, "reason": "Internal server error"}]
            assert (
                voice_host._GLOBAL_TERMINATION_TASK_RESERVATIONS == baseline_termination_tasks
            )  # pylint: disable=protected-access

            retained = [
                task
                for task in voice_host._GLOBAL_RUNTIME_TASKS  # pylint: disable=protected-access
                if task.get_name() == "voice_activation_receive"
            ]
            assert len(retained) == 1
            receive_task = retained[0]
            assert (
                voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS == baseline_tasks + 1
            )  # pylint: disable=protected-access
            assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES > baseline_bytes  # pylint: disable=protected-access
            assert connection._prefetched_receive_task is None  # pylint: disable=protected-access

            globally_released = asyncio.Event()
            receive_task.add_done_callback(lambda _task: globally_released.set())
            websocket.release_receive.set()
            await asyncio.wait_for(globally_released.wait(), timeout=1.0)
            assert voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS == baseline_tasks  # pylint: disable=protected-access
            assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == baseline_bytes  # pylint: disable=protected-access
        finally:
            websocket.release_receive.set()
            if not run_task.done():
                run_task.cancel()
            await _require_task_done(run_task)
            await asyncio.gather(run_task, return_exceptions=True)

    asyncio.run(scenario())


@pytest.mark.parametrize("outcome", ["cancelled", "failed"])
def test_unusable_ready_wrapper_retains_transferred_receive(monkeypatch, outcome: str) -> None:
    async def scenario() -> None:
        class PendingReceiveWebSocket:
            def __init__(self) -> None:
                self.receive_count = 0
                self.receive_started = asyncio.Event()
                self.receive_cancelled = asyncio.Event()
                self.sent: list[dict] = []
                self.closes: list[dict] = []

            async def receive(self) -> dict:
                self.receive_count += 1
                if self.receive_count == 1:
                    return _receive_message(_start())
                self.receive_started.set()
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    self.receive_cancelled.set()
                    raise

            async def send_text(self, data: str) -> None:
                self.sent.append(json.loads(data))

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        websocket = PendingReceiveWebSocket()
        connection = _connection(websocket)

        async def on_session_start(_session, _event) -> None:
            await websocket.receive_started.wait()

        async def on_user_message(_session, _event, _response) -> None:
            raise AssertionError("user callback must not run before readiness")

        connection._on_session_start = on_session_start  # pylint: disable=protected-access
        connection._on_user_message = on_user_message  # pylint: disable=protected-access
        original_create_runtime_task = connection._create_runtime_task  # pylint: disable=protected-access

        def create_runtime_task(coroutine, *, name, termination=False, direct=False):
            if name != "voice_ready_receive":
                return original_create_runtime_task(
                    coroutine,
                    name=name,
                    termination=termination,
                    direct=direct,
                )
            coroutine.close()
            unusable = asyncio.get_running_loop().create_future()
            if outcome == "cancelled":
                unusable.cancel()
            else:
                unusable.set_exception(RuntimeError("ready wrapper failed"))
            return unusable

        monkeypatch.setattr(connection, "_create_runtime_task", create_runtime_task)
        await connection.run()

        assert not websocket.sent
        assert websocket.closes == [{"code": 1011, "reason": "Internal server error"}]
        assert websocket.receive_count == 2
        assert websocket.receive_cancelled.is_set()
        assert connection._prefetched_receive_task is None  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_callback_worker_admission_failure_prevents_ready_commit(monkeypatch) -> None:
    async def scenario() -> None:
        baseline_tasks = voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS  # pylint: disable=protected-access
        baseline_bytes = voice_host._GLOBAL_CUSTOMER_TASK_BYTES  # pylint: disable=protected-access
        monkeypatch.setattr(voice_host, "_MAX_GLOBAL_RUNTIME_TASKS", baseline_tasks + 3)

        class PendingReceiveWebSocket:
            def __init__(self) -> None:
                self.receive_count = 0
                self.receive_cancelled = asyncio.Event()
                self.sent: list[dict] = []
                self.closes: list[dict] = []

            async def receive(self) -> dict:
                self.receive_count += 1
                if self.receive_count == 1:
                    return _receive_message(_start())
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    self.receive_cancelled.set()
                    raise

            async def send_text(self, data: str) -> None:
                self.sent.append(json.loads(data))

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        websocket = PendingReceiveWebSocket()

        async def on_user_message(_session, _event, _response) -> None:
            return None

        connection = voice_host._VoiceConnection(  # pylint: disable=protected-access
            websocket=websocket,
            on_session_start=None,
            on_user_message=on_user_message,
            on_user_no_input=None,
            on_user_speech_started=None,
            on_handoff_failed=None,
            on_barge_in=None,
            on_response_timeout=None,
            on_session_end=None,
        )
        run_task = asyncio.create_task(connection.run(), name="test_voice_connection")
        try:
            await _require_task_done(run_task)
            await run_task

            assert not websocket.sent
            assert websocket.closes == [{"code": 1011, "reason": "Internal server error"}]
            assert websocket.receive_count == 2
            assert websocket.receive_cancelled.is_set()
            assert not connection._ready  # pylint: disable=protected-access
            assert connection._callback_worker is None  # pylint: disable=protected-access
            assert voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS == baseline_tasks  # pylint: disable=protected-access
            assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == baseline_bytes  # pylint: disable=protected-access
        finally:
            if not run_task.done():
                run_task.cancel()
            await _require_task_done(run_task)
            await asyncio.gather(run_task, return_exceptions=True)

    asyncio.run(scenario())


@pytest.mark.parametrize("outcome", ["cancelled", "failed"])
def test_unusable_callback_worker_prevents_ready_commit(monkeypatch, outcome: str) -> None:
    async def scenario() -> None:
        class PendingReceiveWebSocket:
            def __init__(self) -> None:
                self.receive_count = 0
                self.receive_started = asyncio.Event()
                self.receive_cancelled = asyncio.Event()
                self.sent: list[dict] = []
                self.closes: list[dict] = []

            async def receive(self) -> dict:
                self.receive_count += 1
                if self.receive_count == 1:
                    return _receive_message(_start())
                self.receive_started.set()
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    self.receive_cancelled.set()
                    raise

            async def send_text(self, data: str) -> None:
                self.sent.append(json.loads(data))

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        websocket = PendingReceiveWebSocket()
        connection = _connection(websocket)

        async def on_session_start(_session, _event) -> None:
            await websocket.receive_started.wait()

        async def on_user_message(_session, _event, _response) -> None:
            raise AssertionError("user callback must not run before readiness")

        connection._on_session_start = on_session_start  # pylint: disable=protected-access
        connection._on_user_message = on_user_message  # pylint: disable=protected-access
        original_create_runtime_task = connection._create_runtime_task  # pylint: disable=protected-access

        def create_runtime_task(coroutine, *, name, termination=False, direct=False):
            if name != "voice_callback_coordinator":
                return original_create_runtime_task(
                    coroutine,
                    name=name,
                    termination=termination,
                    direct=direct,
                )
            coroutine.close()
            unusable = asyncio.get_running_loop().create_future()
            if outcome == "cancelled":
                unusable.cancel()
            else:
                unusable.set_exception(RuntimeError("callback worker failed"))
            return unusable

        monkeypatch.setattr(connection, "_create_runtime_task", create_runtime_task)
        await connection.run()

        assert not websocket.sent
        assert websocket.closes == [{"code": 1011, "reason": "Internal server error"}]
        assert websocket.receive_count == 2
        assert websocket.receive_cancelled.is_set()
        assert not connection._ready  # pylint: disable=protected-access
        assert connection._callback_worker is None  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_cancellation_requested_callback_worker_prevents_ready_commit(monkeypatch) -> None:
    async def scenario() -> None:
        class PendingReceiveWebSocket:
            def __init__(self) -> None:
                self.receive_count = 0
                self.sent: list[dict] = []
                self.closes: list[dict] = []

            async def receive(self) -> dict:
                self.receive_count += 1
                if self.receive_count == 1:
                    return _receive_message(_start())
                await asyncio.Event().wait()
                raise AssertionError("unreachable")

            async def send_text(self, data: str) -> None:
                self.sent.append(json.loads(data))

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        websocket = PendingReceiveWebSocket()
        connection = _connection(websocket)

        async def on_user_message(_session, _event, _response) -> None:
            return None

        connection._on_user_message = on_user_message  # pylint: disable=protected-access
        original_create_runtime_task = connection._create_runtime_task  # pylint: disable=protected-access

        def create_runtime_task(coroutine, *, name, termination=False, direct=False):
            task = original_create_runtime_task(
                coroutine,
                name=name,
                termination=termination,
                direct=direct,
            )
            if name == "voice_callback_coordinator":
                task.cancel()
            return task

        monkeypatch.setattr(connection, "_create_runtime_task", create_runtime_task)
        await connection.run()

        assert not websocket.sent
        assert websocket.closes == [{"code": 1011, "reason": "Internal server error"}]
        assert not connection._ready  # pylint: disable=protected-access

    asyncio.run(scenario())


@pytest.mark.parametrize("task_name", ["voice_activation_receive", "voice_session_ready"])
def test_internal_activation_task_cancellation_closes_1011(monkeypatch, task_name: str) -> None:
    async def scenario() -> None:
        class PendingReceiveWebSocket:
            def __init__(self) -> None:
                self.receive_count = 0
                self.sent: list[dict] = []
                self.closes: list[dict] = []

            async def receive(self) -> dict:
                self.receive_count += 1
                if self.receive_count == 1:
                    return _receive_message(_start())
                await asyncio.Event().wait()
                raise AssertionError("unreachable")

            async def send_text(self, data: str) -> None:
                self.sent.append(json.loads(data))

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        websocket = PendingReceiveWebSocket()
        connection = _connection(websocket)

        async def on_user_message(_session, _event, _response) -> None:
            return None

        connection._on_user_message = on_user_message  # pylint: disable=protected-access
        original_create_runtime_task = connection._create_runtime_task  # pylint: disable=protected-access

        def create_runtime_task(coroutine, *, name, termination=False, direct=False):
            task = original_create_runtime_task(
                coroutine,
                name=name,
                termination=termination,
                direct=direct,
            )
            if name == task_name:
                task.cancel()
            return task

        monkeypatch.setattr(connection, "_create_runtime_task", create_runtime_task)
        await connection.run()

        assert all(message["type"] != "session.ready" for message in websocket.sent)
        assert websocket.closes == [{"code": 1011, "reason": "Internal server error"}]

    asyncio.run(scenario())


def test_internal_post_ready_receive_cancellation_is_runtime_failure(monkeypatch) -> None:
    async def scenario() -> None:
        connection = _connection(None)
        connection._callback_worker = asyncio.create_task(  # pylint: disable=protected-access
            asyncio.Event().wait(),
            name="test_callback_worker",
        )
        original_create_runtime_task = connection._create_runtime_task  # pylint: disable=protected-access

        def create_runtime_task(coroutine, *, name, termination=False, direct=False):
            task = original_create_runtime_task(
                coroutine,
                name=name,
                termination=termination,
                direct=direct,
            )
            if name == "voice_receive":
                task.cancel()
            return task

        monkeypatch.setattr(connection, "_create_runtime_task", create_runtime_task)
        try:
            with pytest.raises(RuntimeError, match="Voice receive was cancelled"):
                await connection._receive_with_worker_supervision()  # pylint: disable=protected-access
        finally:
            connection._callback_worker.cancel()  # pylint: disable=protected-access
            await asyncio.gather(
                connection._callback_worker, return_exceptions=True
            )  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_shutdown_deadline_does_not_join_resistant_callback_worker(monkeypatch) -> None:
    monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.02)

    async def scenario() -> None:
        baseline = voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS  # pylint: disable=protected-access
        connection = _connection(None)
        worker_started = asyncio.Event()
        worker_cancelled = asyncio.Event()
        release_worker = asyncio.Event()

        async def resistant_worker() -> None:
            worker_started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                worker_cancelled.set()
                await release_worker.wait()

        worker = connection._create_runtime_task(  # pylint: disable=protected-access
            resistant_worker(),
            name="voice_callback_coordinator",
        )
        connection._callback_worker = worker  # pylint: disable=protected-access
        await asyncio.wait_for(worker_started.wait(), timeout=1.0)

        shutdown = asyncio.create_task(
            connection._shutdown_runtime(drain_callbacks=False)
        )  # pylint: disable=protected-access
        try:
            await asyncio.wait_for(worker_cancelled.wait(), timeout=1.0)
            await _require_task_done(shutdown)
            await shutdown

            assert worker in voice_host._GLOBAL_RUNTIME_TASKS  # pylint: disable=protected-access
            assert connection._callback_worker is None  # pylint: disable=protected-access

            globally_released = asyncio.Event()
            worker.add_done_callback(lambda _task: globally_released.set())
            release_worker.set()
            await asyncio.wait_for(globally_released.wait(), timeout=1.0)
            assert voice_host._GLOBAL_RUNTIME_TASK_RESERVATIONS == baseline  # pylint: disable=protected-access
        finally:
            release_worker.set()
            if not shutdown.done():
                shutdown.cancel()
            await _require_task_done(shutdown)
            await asyncio.gather(shutdown, return_exceptions=True)

    asyncio.run(scenario())


def test_ready_pre_transport_failure_cleans_receive_task() -> None:
    async def scenario() -> None:
        loop = asyncio.get_running_loop()

        class PendingWebSocket:
            def __init__(self) -> None:
                self.pending_receive: asyncio.Future[dict] = loop.create_future()

            async def receive(self) -> dict:
                return await self.pending_receive

            async def send_text(self, _data: str) -> None:
                raise AssertionError("transport must not be entered")

            async def close(self, **_fields) -> None:
                return None

        websocket = PendingWebSocket()
        connection = _connection(websocket)
        connection._ending = True  # pylint: disable=protected-access

        try:
            await connection._send_ready_with_receive_gate()  # pylint: disable=protected-access
        except voice_host.VoiceBridgeConnectionClosedError:
            pass
        else:
            raise AssertionError("pre-transport terminal state was not propagated")

        assert websocket.pending_receive.cancelled()
        assert connection._prefetched_receive_task is None  # pylint: disable=protected-access
        await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access

    asyncio.run(scenario())


@pytest.mark.parametrize("after_transport_attempt", [False, True])
def test_ready_gate_cancellation_cleans_single_receive(after_transport_attempt: bool) -> None:
    async def scenario() -> None:
        loop = asyncio.get_running_loop()

        class BlockingWebSocket:
            def __init__(self) -> None:
                self.pending_receive: asyncio.Future[dict] = loop.create_future()
                self.transport_entered = asyncio.Event()

            async def receive(self) -> dict:
                return await self.pending_receive

            async def send_text(self, _data: str) -> None:
                self.transport_entered.set()
                await asyncio.Event().wait()

            async def close(self, **_fields) -> None:
                return None

        websocket = BlockingWebSocket()
        connection = _connection(websocket)
        if not after_transport_attempt:
            send_lock = _ControlledSendLock()
            connection._send_lock = send_lock  # type: ignore[assignment]  # pylint: disable=protected-access
        gate = asyncio.create_task(
            connection._send_ready_with_receive_gate(),  # pylint: disable=protected-access
            name="test_ready_gate",
        )
        if after_transport_attempt:
            await websocket.transport_entered.wait()
        else:
            await send_lock.acquire_started.wait()
        gate.cancel()
        with pytest.raises(asyncio.CancelledError):
            await gate

        assert websocket.pending_receive.cancelled()
        assert connection._prefetched_receive_task is None  # pylint: disable=protected-access
        assert connection.ending is after_transport_attempt
        await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access

    asyncio.run(scenario())


@pytest.mark.parametrize("delivery_hops", [2, 3])
def test_startup_receive_delivery_is_not_dropped_during_task_handoff(delivery_hops: int) -> None:
    async def scenario() -> None:
        loop = asyncio.get_running_loop()
        timeline: list[str] = []

        class OneShotBoundaryWebSocket:
            def __init__(self) -> None:
                self.start_delivery: asyncio.Future[dict] = loop.create_future()
                self.boundary_delivery: asyncio.Future[dict] = loop.create_future()
                self.after_boundary: asyncio.Future[dict] = loop.create_future()
                self.sent: list[dict] = []
                self.closes: list[dict] = []
                self.receive_count = 0
                self.active_receives = 0
                self.max_active_receives = 0

            async def receive(self) -> dict:
                self.receive_count += 1
                self.active_receives += 1
                self.max_active_receives = max(self.max_active_receives, self.active_receives)
                try:
                    if self.receive_count == 1:
                        return await self.start_delivery
                    if self.receive_count == 2:
                        return await self.boundary_delivery
                    return await self.after_boundary
                finally:
                    self.active_receives -= 1

            async def send_text(self, data: str) -> None:
                payload = json.loads(data)
                timeline.append(f"send:{payload['type']}")
                self.sent.append(payload)

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        websocket = OneShotBoundaryWebSocket()
        websocket.start_delivery.set_result(_receive_message(_start()))
        boundary_message = _receive_message(_user_message())

        async def on_session_start(_session, _event) -> None:
            # Wake the activation coordinator before the receive task resumes.
            # Replacing that receive would lose this one-shot ASGI delivery and
            # wait forever on ``after_boundary``.
            def deliver_after_hops(remaining: int) -> None:
                if remaining:
                    loop.call_soon(deliver_after_hops, remaining - 1)
                    return
                timeline.append("deliver")
                websocket.boundary_delivery.set_result(boundary_message)

            loop.call_soon(deliver_after_hops, delivery_hops - 1)

        async def on_user_message(_session, _event, response) -> None:
            await response.decline()

        connection = voice_host._VoiceConnection(  # pylint: disable=protected-access
            websocket=websocket,
            on_session_start=on_session_start,
            on_user_message=on_user_message,
            on_user_no_input=None,
            on_user_speech_started=None,
            on_handoff_failed=None,
            on_barge_in=None,
            on_response_timeout=None,
            on_session_end=None,
        )

        activation = asyncio.create_task(connection._activate())  # pylint: disable=protected-access
        await _require_task_done(activation)
        assert not await activation
        assert timeline[0] == "deliver"
        assert [message["type"] for message in websocket.sent] == ["session.rejected"]
        assert websocket.closes[-1]["code"] == 1008
        assert websocket.receive_count == 2
        assert websocket.max_active_receives == 1
        await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access

    asyncio.run(scenario())


@pytest.mark.parametrize("yield_before_failure", [False, True])
def test_readiness_failure_cleans_transferred_receive_task(yield_before_failure: bool) -> None:
    async def scenario() -> None:
        loop = asyncio.get_running_loop()

        class PendingWebSocket:
            def __init__(self) -> None:
                self.start_delivery: asyncio.Future[dict] = loop.create_future()
                self.pending_delivery: asyncio.Future[dict] = loop.create_future()
                self.receive_count = 0
                self.active_receives = 0

            async def receive(self) -> dict:
                self.receive_count += 1
                self.active_receives += 1
                try:
                    if self.receive_count == 1:
                        return await self.start_delivery
                    return await self.pending_delivery
                finally:
                    self.active_receives -= 1

            async def send_text(self, _data: str) -> None:
                if yield_before_failure:
                    await asyncio.sleep(0)
                raise RuntimeError("readiness send failed")

            async def close(self, **_fields) -> None:
                return None

        websocket = PendingWebSocket()
        websocket.start_delivery.set_result(_receive_message(_start()))

        async def on_user_message(_session, _event, response) -> None:
            await response.decline()

        connection = voice_host._VoiceConnection(  # pylint: disable=protected-access
            websocket=websocket,
            on_session_start=None,
            on_user_message=on_user_message,
            on_user_no_input=None,
            on_user_speech_started=None,
            on_handoff_failed=None,
            on_barge_in=None,
            on_response_timeout=None,
            on_session_end=None,
        )

        try:
            await connection._activate()  # pylint: disable=protected-access
        except RuntimeError as exc:
            assert str(exc) == "readiness send failed"
        else:
            raise AssertionError("readiness failure was not propagated")

        assert websocket.pending_delivery.cancelled()
        assert websocket.active_receives == 0
        assert connection._prefetched_receive_task is None  # pylint: disable=protected-access
        callback_worker = connection._callback_worker  # pylint: disable=protected-access
        assert callback_worker is not None
        await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access
        assert callback_worker.done()
        assert connection._callback_worker is None  # pylint: disable=protected-access

    asyncio.run(scenario())
