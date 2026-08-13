# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the thin Voice Session context."""

import asyncio
import json
import threading

import pytest
from starlette.websockets import WebSocketState

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

        assert raised.value.args == ("queued-close-cancel",)
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
async def test_session_close_finds_cancellation_in_context_beside_independent_cause():
    websocket = _BlockingWebSocket()
    cancellation = asyncio.CancelledError("transport cancellation")
    close_error = OSError("transport wrapped cancellation")
    close_error.__cause__ = RuntimeError("independent cause")
    close_error.__context__ = cancellation
    websocket.close_error = close_error
    session = Session._create(websocket)  # pylint: disable=protected-access

    with pytest.raises(asyncio.CancelledError) as raised:
        await session._close(1002, "protocol error")  # pylint: disable=protected-access

    assert raised.value is cancellation
    assert raised.value.__cause__ is close_error
    assert close_error.__cause__ is not None
    assert close_error.__context__ is None


def test_find_cancellation_prefers_explicit_cause_branch():
    cause_cancellation = asyncio.CancelledError("explicit cause")
    context_cancellation = asyncio.CancelledError("implicit context")
    wrapper = OSError("transport wrapper")
    wrapper.__cause__ = cause_cancellation
    wrapper.__context__ = context_cancellation

    assert session_module._find_cancellation(wrapper) is cause_cancellation  # pylint: disable=protected-access


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


def test_close_attempt_reservation_rolls_back_when_task_construction_fails(monkeypatch):
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    def fail_create_task(_coroutine, *, name=None):
        del name
        raise RuntimeError("task construction failed")

    monkeypatch.setattr(session_module.asyncio, "create_task", fail_create_task)

    with pytest.raises(RuntimeError, match="task construction failed"):
        session_module._start_close_attempt(  # pylint: disable=protected-access
            asyncio.Lock(),
            _BlockingWebSocket(),
            1002,
            "failed close",
        )

    assert set(session_module._CLOSE_ATTEMPTS) == baseline_attempts  # pylint: disable=protected-access
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
