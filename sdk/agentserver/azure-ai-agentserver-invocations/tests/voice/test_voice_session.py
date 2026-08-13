# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the thin Voice Session context."""

import asyncio
import json
import sys
import threading

import pytest
from starlette.websockets import WebSocketDisconnect, WebSocketState

from azure.ai.agentserver.invocations.voice import EndCall, Session, SessionReady
from azure.ai.agentserver.invocations.voice import _session as session_module


class _BlockingWebSocket:
    def __init__(self):
        self.entered = asyncio.Event()
        self.release = asyncio.Event()
        self.frames = []
        self.closes = []
        self.close_error = None
        self.application_state = WebSocketState.CONNECTED
        self.active_sends = 0
        self.maximum_active_sends = 0
        self._send = self._send_message

    async def _send_message(self, message):
        if message["type"] == "websocket.close":
            await self.close(code=message["code"], reason=message["reason"])

    async def send_text(self, frame):
        self.active_sends += 1
        self.maximum_active_sends = max(self.maximum_active_sends, self.active_sends)
        self.frames.append(json.loads(frame))
        self.entered.set()
        await self.release.wait()
        self.active_sends -= 1

    async def close(self, *, code, reason):
        self.active_sends += 1
        self.maximum_active_sends = max(self.maximum_active_sends, self.active_sends)
        self.closes.append((code, reason))
        self.active_sends -= 1
        if self.close_error is not None:
            raise self.close_error


async def _finish_close_attempts(baseline):
    outstanding = set(session_module._CLOSE_ATTEMPTS) - baseline  # pylint: disable=protected-access
    if outstanding:
        await asyncio.wait_for(asyncio.gather(*outstanding, return_exceptions=True), timeout=1)
    await asyncio.sleep(0)
    assert set(session_module._CLOSE_ATTEMPTS) == baseline  # pylint: disable=protected-access


def test_session_cannot_be_constructed_by_customer():
    with pytest.raises(TypeError, match="created by VoiceAgentServerHost"):
        Session()


@pytest.mark.asyncio
async def test_session_has_only_transport_and_send_gate_and_serializes_writes():
    websocket = _BlockingWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access
    assert not hasattr(session, "__dict__")
    assert set(Session.__slots__) == {"_websocket", "_send_lock", "_terminal"}

    first = asyncio.create_task(session.send(SessionReady()))
    await websocket.entered.wait()
    second = asyncio.create_task(session.send(EndCall(reason="completed")))
    await asyncio.sleep(0)
    assert len(websocket.frames) == 1

    websocket.release.set()
    await asyncio.gather(first, second)
    assert websocket.maximum_active_sends == 1
    assert [frame["type"] for frame in websocket.frames] == ["session.ready", "end_call"]


@pytest.mark.asyncio
async def test_session_serializes_application_send_and_close():
    websocket = _BlockingWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access

    send_task = asyncio.create_task(session.send(SessionReady()))
    await websocket.entered.wait()
    close_task = asyncio.create_task(session._close(1002, "protocol error"))  # pylint: disable=protected-access
    await asyncio.sleep(0)

    assert websocket.closes == []
    websocket.release.set()
    await asyncio.gather(send_task, close_task)

    assert websocket.maximum_active_sends == 1
    assert websocket.closes == [(1002, "protocol error")]


@pytest.mark.asyncio
async def test_session_close_cancellation_does_not_wait_for_blocked_send():
    websocket = _BlockingWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    send_task = asyncio.create_task(session.send(SessionReady()))
    close_task = None
    try:
        await asyncio.wait_for(websocket.entered.wait(), timeout=1)
        close_task = asyncio.create_task(session._close(1002, "protocol error"))  # pylint: disable=protected-access
        await asyncio.sleep(0)

        with pytest.raises(RuntimeError, match="terminating"):
            await session.send(EndCall(reason="too late"))

        close_task.cancel("queued-close-cancel")
        with pytest.raises(asyncio.CancelledError) as raised:
            await asyncio.wait_for(close_task, timeout=1)

        assert raised.value.args == (("queued-close-cancel",) if sys.version_info >= (3, 11) else ())
        assert websocket.closes == []
        with pytest.raises(RuntimeError, match="terminating"):
            await session.send(EndCall(reason="too late"))
    finally:
        websocket.release.set()
        await asyncio.wait_for(asyncio.gather(send_task, return_exceptions=True), timeout=1)
        if close_task is not None and not close_task.done():
            close_task.cancel()
            await asyncio.wait_for(asyncio.gather(close_task, return_exceptions=True), timeout=1)
        await _finish_close_attempts(baseline_attempts)
    assert not session._send_lock.locked()  # pylint: disable=protected-access
    assert websocket.closes == [(1002, "protocol error")]


@pytest.mark.asyncio
async def test_session_queued_cancellation_skips_transport_close():
    websocket = _BlockingWebSocket()
    websocket.close_error = OSError("transport close failed")
    session = Session._create(websocket)  # pylint: disable=protected-access
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    send_task = asyncio.create_task(session.send(SessionReady()))
    close_task = None
    try:
        await asyncio.wait_for(websocket.entered.wait(), timeout=1)
        close_task = asyncio.create_task(session._close(1002, "protocol error"))  # pylint: disable=protected-access
        await asyncio.sleep(0)
        close_task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(close_task, timeout=1)

        assert websocket.closes == []
        with pytest.raises(RuntimeError, match="terminating"):
            await session.send(EndCall(reason="too late"))
    finally:
        websocket.release.set()
        await asyncio.wait_for(asyncio.gather(send_task, return_exceptions=True), timeout=1)
        if close_task is not None and not close_task.done():
            close_task.cancel()
            await asyncio.wait_for(asyncio.gather(close_task, return_exceptions=True), timeout=1)
        await _finish_close_attempts(baseline_attempts)
    assert not session._send_lock.locked()  # pylint: disable=protected-access
    assert websocket.closes == [(1002, "protocol error")]


@pytest.mark.asyncio
async def test_session_close_does_not_infer_cancellation_from_exception_graph():
    websocket = _BlockingWebSocket()
    cancellation = asyncio.CancelledError("transport cancellation")
    close_error = OSError("transport wrapped cancellation")
    close_error.__cause__ = RuntimeError("independent cause")
    close_error.__context__ = cancellation
    websocket.close_error = close_error
    session = Session._create(websocket)  # pylint: disable=protected-access

    with pytest.raises(OSError) as raised:
        await session._close(1002, "protocol error")  # pylint: disable=protected-access

    assert raised.value is close_error
    assert close_error.__cause__ is not None
    assert close_error.__context__ is cancellation


def test_find_cancellation_prefers_explicit_cause_branch():
    cause_cancellation = asyncio.CancelledError("explicit cause")
    context_cancellation = asyncio.CancelledError("implicit context")
    wrapper = OSError("transport wrapper")
    wrapper.__cause__ = cause_cancellation
    wrapper.__context__ = context_cancellation

    assert session_module._find_cancellation(wrapper) is cause_cancellation  # pylint: disable=protected-access


def test_untracked_generic_wrapper_does_not_become_task_cancellation():
    cancellation = asyncio.CancelledError("inner cancellation")
    wrapper = RuntimeError("callback wrapper")
    wrapper.__cause__ = cancellation

    session_module._raise_task_cancellation(wrapper, None)  # pylint: disable=protected-access

    assert wrapper.__cause__ is cancellation


@pytest.mark.asyncio
async def test_send_operation_closes_coroutine_when_task_construction_fails(monkeypatch):
    websocket = _BlockingWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access
    closed_coroutines = []
    close_coroutine = session_module._close_coroutine  # pylint: disable=protected-access

    def track_close(coroutine):
        closed_coroutines.append(coroutine)
        close_coroutine(coroutine)

    def fail_create_task(_coroutine, *, name=None):
        del name
        raise RuntimeError("send task construction failed")

    monkeypatch.setattr(session_module, "_close_coroutine", track_close)
    monkeypatch.setattr(session_module.asyncio, "create_task", fail_create_task)

    with pytest.raises(RuntimeError, match="send task construction failed"):
        await session.send(SessionReady())

    assert len(closed_coroutines) == 1
    assert websocket.frames == []


@pytest.mark.asyncio
async def test_send_cancellation_before_transport_operation_starts():
    websocket = _BlockingWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access

    send_task = asyncio.create_task(session.send(SessionReady()))
    send_task.cancel("pre-start-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(send_task, timeout=1)

    assert raised.value.args == (("pre-start-cancel",) if sys.version_info >= (3, 11) else ())
    assert send_task.cancelled()
    assert websocket.frames == []
    assert [task for task in asyncio.all_tasks() if task.get_name() == "voice_websocket_send"] == []


@pytest.mark.asyncio
async def test_send_side_peer_loss_closes_gate_before_queued_writer_enters_transport():
    class PeerLossWebSocket:
        def __init__(self):
            self.application_state = WebSocketState.CONNECTED
            self.scope = {}
            self.send_started = asyncio.Event()
            self.release_send = asyncio.Event()
            self.frames = []

        async def send_text(self, frame):
            self.frames.append(json.loads(frame))
            self.send_started.set()
            await self.release_send.wait()
            raise WebSocketDisconnect(code=1006)

    websocket = PeerLossWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access
    first_send = asyncio.create_task(session.send(SessionReady()))
    await websocket.send_started.wait()
    second_send = asyncio.create_task(session.send(EndCall(reason="queued")))
    await asyncio.sleep(0)

    websocket.release_send.set()
    first_result, second_result = await asyncio.gather(first_send, second_send, return_exceptions=True)

    assert isinstance(first_result, WebSocketDisconnect)
    assert isinstance(second_result, RuntimeError)
    assert str(second_result) == "Voice Session is terminating"
    assert [frame["type"] for frame in websocket.frames] == ["session.ready"]


@pytest.mark.asyncio
async def test_session_close_recomputes_deadline_after_attempt_start(monkeypatch):
    current_time = 0.0
    observed_timeouts = []

    class FakeLoop:
        @staticmethod
        def time():
            return current_time

    class CompletedAttempt:
        @staticmethod
        def result():
            return None

    def start_close_attempt(*_args):
        nonlocal current_time
        current_time = 4.0
        return CompletedAttempt()

    async def wait_for_attempt(attempts, *, timeout):
        observed_timeouts.append(timeout)
        return set(attempts), set()

    monkeypatch.setattr(session_module.asyncio, "get_running_loop", lambda: FakeLoop())
    monkeypatch.setattr(session_module, "_start_close_attempt", start_close_attempt)
    monkeypatch.setattr(session_module.asyncio, "wait", wait_for_attempt)
    session = Session._create(_BlockingWebSocket())  # pylint: disable=protected-access

    await session._close(1002, "protocol error", deadline=5.0)  # pylint: disable=protected-access

    assert observed_timeouts == [1.0]


@pytest.mark.asyncio
async def test_close_attempt_rolls_back_when_task_construction_fails_and_can_retry(monkeypatch):
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access
    create_task = asyncio.create_task
    create_attempts = 0
    closed_coroutines = []
    close_coroutine = session_module._close_coroutine  # pylint: disable=protected-access

    def track_close(coroutine):
        closed_coroutines.append(coroutine)
        close_coroutine(coroutine)

    def fail_first_create_task(coroutine, *, name=None):
        nonlocal create_attempts
        create_attempts += 1
        if create_attempts == 1:
            raise RuntimeError("task construction failed")
        return create_task(coroutine, name=name)

    monkeypatch.setattr(session_module.asyncio, "create_task", fail_first_create_task)
    monkeypatch.setattr(session_module, "_close_coroutine", track_close)
    websocket = _BlockingWebSocket()

    with pytest.raises(RuntimeError, match="task construction failed"):
        session_module._start_close_attempt(  # pylint: disable=protected-access
            asyncio.Lock(),
            websocket,
            1002,
            "failed close",
        )

    assert set(session_module._CLOSE_ATTEMPTS) == baseline_attempts  # pylint: disable=protected-access
    assert session_module._CLOSE_ATTEMPT_RESERVATIONS == 0  # pylint: disable=protected-access
    assert websocket.application_state == WebSocketState.CONNECTED
    assert websocket.closes == []
    assert len(closed_coroutines) == 1
    assert closed_coroutines[0].cr_frame is None

    retry = session_module._start_close_attempt(  # pylint: disable=protected-access
        asyncio.Lock(),
        websocket,
        1002,
        "retry close",
    )

    assert retry is not None
    await _finish_close_attempts(baseline_attempts)
    assert create_attempts == 2
    assert websocket.application_state == WebSocketState.DISCONNECTED
    assert websocket.closes == [(1002, "retry close")]
    assert len(closed_coroutines) == 1
    assert session_module._CLOSE_ATTEMPT_RESERVATIONS == 0  # pylint: disable=protected-access


def test_close_attempt_cap_is_atomic_across_event_loop_threads(monkeypatch):
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access
    monkeypatch.setattr(session_module, "_MAX_CLOSE_ATTEMPTS", len(baseline_attempts) + 1)
    barrier = threading.Barrier(2)
    results = []
    result_lock = threading.Lock()

    def worker():
        async def run():
            attempt = None
            try:
                attempt = session_module._start_close_attempt(  # pylint: disable=protected-access
                    asyncio.Lock(),
                    _BlockingWebSocket(),
                    1002,
                    "thread close",
                )
                outcome = "admitted"
            except RuntimeError as exc:
                outcome = str(exc)
            barrier.wait(timeout=1)
            if attempt is not None:
                await asyncio.wait_for(attempt, timeout=1)
            with result_lock:
                results.append(outcome)

        asyncio.run(run())

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=2)

    assert all(not thread.is_alive() for thread in threads)
    assert sorted(results) == ["Voice WebSocket close attempt limit reached", "admitted"]
    assert session_module._CLOSE_ATTEMPT_RESERVATIONS == 0  # pylint: disable=protected-access
    assert set(session_module._CLOSE_ATTEMPTS) == baseline_attempts  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_session_close_attempt_cap_fails_closed_and_recovers(monkeypatch):
    monkeypatch.setattr(session_module, "CLOSE_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(session_module, "_MAX_CLOSE_ATTEMPTS", 1)
    close_started = asyncio.Event()
    close_release = asyncio.Event()

    class CancellationResistantCloseWebSocket(_BlockingWebSocket):
        async def close(self, *, code, reason):
            self.closes.append((code, reason))
            close_started.set()
            try:
                await close_release.wait()
            except asyncio.CancelledError:
                await close_release.wait()

    first_websocket = CancellationResistantCloseWebSocket()
    first_session = Session._create(first_websocket)  # pylint: disable=protected-access
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    try:
        with pytest.raises(TimeoutError, match="deadline elapsed"):
            await asyncio.wait_for(  # pylint: disable=protected-access
                first_session._close(1002, "protocol error"),
                timeout=1,
            )
        await asyncio.wait_for(close_started.wait(), timeout=1)
        outstanding = set(session_module._CLOSE_ATTEMPTS) - baseline_attempts  # pylint: disable=protected-access
        assert len(outstanding) == 1

        second_websocket = _BlockingWebSocket()
        second_session = Session._create(second_websocket)  # pylint: disable=protected-access
        with pytest.raises(RuntimeError, match="close attempt limit reached"):
            await asyncio.wait_for(  # pylint: disable=protected-access
                second_session._close(1002, "protocol error"),
                timeout=1,
            )
        assert second_websocket.closes == []
    finally:
        close_release.set()
        await _finish_close_attempts(baseline_attempts)
