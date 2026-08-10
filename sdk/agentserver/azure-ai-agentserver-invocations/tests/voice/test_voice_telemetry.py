# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Regression tests for best-effort voice telemetry."""

import asyncio
import contextvars
import gc
import queue
import threading
import weakref

from opentelemetry import context as otel_context, trace
from starlette.testclient import TestClient

from azure.ai.agentserver.invocations.voice import VoiceAgentServerHost
from azure.ai.agentserver.invocations.voice import _host as voice_host


_TS = "2026-07-23T12:00:00.000Z"


class _FailingInstrument:
    def add(self, _value, _attributes=None, context=None) -> None:
        raise RuntimeError("counter failed")

    def record(self, _value, _attributes=None, context=None) -> None:
        raise RuntimeError("histogram failed")


class _BlockingInstrument:
    def __init__(self) -> None:
        self.entered = threading.Event()
        self.release = threading.Event()

    def add(self, _value, _attributes=None, context=None) -> None:
        self.context = context
        self.entered.set()
        self.release.wait()


class _RecordingInstrument:
    def __init__(self, expected_calls: int = 1) -> None:
        self._expected_calls = expected_calls
        self._lock = threading.Lock()
        self.calls: list[tuple[float, dict]] = []
        self.contexts: list[otel_context.Context | None] = []
        self.recorded = threading.Event()

    def add(self, value, attributes=None, context=None) -> None:
        with self._lock:
            self.calls.append((value, attributes or {}))
            self.contexts.append(context)
            if len(self.calls) == self._expected_calls:
                self.recorded.set()

    def record(self, value, attributes=None, context=None) -> None:
        self.add(value, attributes, context)


def test_blocking_counter_does_not_block_protocol_caller(monkeypatch) -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=8)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    instrument = _BlockingInstrument()
    returned = threading.Event()

    def emit() -> None:
        voice_host._metric_add(instrument, 1, {"kind": "test"})  # pylint: disable=protected-access
        returned.set()

    caller = threading.Thread(target=emit, name="test_voice_metric_caller")
    caller.start()
    try:
        assert instrument.entered.wait(timeout=1.0)
        assert returned.wait(timeout=1.0)
    finally:
        instrument.release.set()
        caller.join(timeout=1.0)
    assert not caller.is_alive()
    assert dispatcher.flush(timeout=1.0)
    assert dispatcher.close(timeout=1.0)


def test_blocking_close_metric_does_not_precede_structural_release(monkeypatch) -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=32)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    instrument = _BlockingInstrument()
    monkeypatch.setattr(voice_host, "_CLOSE_CODE_COUNTER", instrument)
    state_released = threading.Event()
    connection_finished = threading.Event()
    failures: list[BaseException] = []
    release_state = voice_host._VoiceConnection._release_connection_state  # pylint: disable=protected-access

    def observe_release(connection) -> None:
        release_state(connection)
        state_released.set()

    monkeypatch.setattr(voice_host._VoiceConnection, "_release_connection_state", observe_release)
    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_user_message
    async def on_message(_session, _event, _response) -> None:
        return

    def run_connection() -> None:
        try:
            with TestClient(app).websocket_connect("/invocations_ws") as websocket:
                websocket.send_json(
                    {
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
                )
                assert websocket.receive_json()["type"] == "session.ready"
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            failures.append(exc)
        finally:
            connection_finished.set()

    connection_thread = threading.Thread(target=run_connection, name="test_voice_metric_teardown")
    connection_thread.start()
    try:
        assert instrument.entered.wait(timeout=2.0)
        assert state_released.wait(timeout=2.0)
        assert connection_finished.wait(timeout=2.0)
    finally:
        instrument.release.set()
        connection_thread.join(timeout=2.0)
    assert not connection_thread.is_alive()
    assert not failures
    assert dispatcher.flush(timeout=1.0)
    assert dispatcher.close(timeout=1.0)


def test_reentrant_metric_callback_does_not_deadlock_dispatcher(monkeypatch) -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=8)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    nested = _RecordingInstrument()

    class ReentrantInstrument:
        def add(self, _value, _attributes=None, context=None) -> None:
            del context
            voice_host._metric_record(nested, 2.0, {"kind": "nested"})  # pylint: disable=protected-access

    voice_host._metric_add(ReentrantInstrument(), 1, {"kind": "outer"})  # pylint: disable=protected-access
    assert nested.recorded.wait(timeout=1.0)
    assert nested.calls == [(2.0, {"kind": "nested"})]
    assert dispatcher.flush(timeout=1.0)
    assert dispatcher.close(timeout=1.0)


def test_blocked_metric_worker_has_bounded_nonretaining_backlog(monkeypatch) -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    blocker = _BlockingInstrument()
    recorder = _RecordingInstrument(expected_calls=4)

    voice_host._metric_add(blocker, 1)  # pylint: disable=protected-access
    assert blocker.entered.wait(timeout=1.0)

    class Payload:
        pass

    payload = Payload()
    payload_reference = weakref.ref(payload)
    voice_host._metric_add(recorder, 0, {"payload": payload})  # pylint: disable=protected-access
    del payload
    gc.collect()
    assert payload_reference() is None

    for value in range(1, 20):
        voice_host._metric_add(recorder, value)  # pylint: disable=protected-access

    blocker.release.set()
    assert recorder.recorded.wait(timeout=1.0)
    assert len(recorder.calls) == 4
    assert dispatcher.flush(timeout=1.0)
    assert dispatcher.close(timeout=1.0)


def test_metric_snapshot_rejects_retaining_scalar_subclasses(monkeypatch) -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    blocker = _BlockingInstrument()
    recorder = _RecordingInstrument()
    voice_host._metric_add(blocker, 1)  # pylint: disable=protected-access
    assert blocker.entered.wait(timeout=1.0)

    class Payload:
        pass

    class RetainingText(str):
        pass

    class RetainingInteger(int):
        pass

    class RetainingFloat(float):
        pass

    payloads = [Payload() for _ in range(4)]
    payload_references = [weakref.ref(payload) for payload in payloads]
    measurement = RetainingInteger(1)
    measurement.payload = payloads[0]
    attribute_key = RetainingText("kind")
    attribute_key.payload = payloads[1]
    attribute_value = RetainingText("test")
    attribute_value.payload = payloads[2]
    histogram_value = RetainingFloat(1.0)
    histogram_value.payload = payloads[3]

    voice_host._metric_add(  # pylint: disable=protected-access
        recorder,
        measurement,
        {attribute_key: attribute_value},
    )
    voice_host._metric_record(recorder, histogram_value)  # pylint: disable=protected-access
    del attribute_key, attribute_value, histogram_value, measurement, payloads

    try:
        gc.collect()
        assert all(reference() is None for reference in payload_references)
    finally:
        blocker.release.set()
        dispatcher.close(timeout=1.0)


def test_dispatcher_close_is_absorbing_and_releases_pending_measurements() -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    blocker = _BlockingInstrument()
    assert dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=blocker,
            operation="add",
            value=1,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    assert blocker.entered.wait(timeout=1.0)

    pending = _RecordingInstrument()
    pending_reference = weakref.ref(pending)
    assert dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=pending,
            operation="add",
            value=2,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    del pending

    try:
        close_timed_out = not dispatcher.close(timeout=0.01)
        gc.collect()
        released_while_worker_blocked = pending_reference() is None
        accepted_while_closing = dispatcher.submit(  # pylint: disable=protected-access
            voice_host._MetricMeasurement(  # pylint: disable=protected-access
                instrument=_RecordingInstrument(),
                operation="add",
                value=3,
                attributes=(),
                context=otel_context.Context(),
            )
        )
    finally:
        blocker.release.set()
        worker = dispatcher._worker  # pylint: disable=protected-access
        if worker is not None:
            worker.join(timeout=1.0)
        dispatcher.flush(timeout=1.0)
        dispatcher.close(timeout=1.0)

    accepted_after_close = dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=_RecordingInstrument(),
            operation="add",
            value=4,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    if accepted_after_close:
        dispatcher.flush(timeout=1.0)
        dispatcher.close(timeout=1.0)

    assert close_timed_out
    assert released_while_worker_blocked
    assert not accepted_while_closing
    assert not accepted_after_close


def test_close_overtaking_claimed_active_barrier_fails_flush() -> None:
    barrier_queued = threading.Event()

    class BarrierObservedQueue(queue.Queue):
        def put_nowait(self, item) -> None:
            super().put_nowait(item)
            if isinstance(item, voice_host._MetricBarrier):  # pylint: disable=protected-access
                barrier_queued.set()

    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    dispatcher._commands = BarrierObservedQueue(maxsize=4)  # pylint: disable=protected-access
    original_execute = dispatcher._execute_command  # pylint: disable=protected-access
    barrier_claimed = threading.Event()
    barrier_release = threading.Event()
    blocker = _BlockingInstrument()
    active_connections = _RecordingInstrument()
    flush_results: list[bool] = []

    def pause_claimed_barrier(command) -> bool:
        if isinstance(command, voice_host._MetricBarrier):  # pylint: disable=protected-access
            barrier_claimed.set()
            barrier_release.wait()
        return original_execute(command)

    dispatcher._execute_command = pause_claimed_barrier  # type: ignore[method-assign]  # pylint: disable=protected-access
    assert dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=blocker,
            operation="add",
            value=1,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    assert blocker.entered.wait(timeout=1.0)
    assert dispatcher.submit_active_delta(active_connections, 1)  # pylint: disable=protected-access
    flush_thread = threading.Thread(
        target=lambda: flush_results.append(dispatcher.flush(timeout=1.0)),
        name="test_voice_metric_claimed_barrier_close",
    )
    flush_thread.start()
    try:
        assert barrier_queued.wait(timeout=1.0)
        blocker.release.set()
        assert barrier_claimed.wait(timeout=1.0)
        assert not dispatcher.close(timeout=0.01)
        barrier_release.set()
        flush_thread.join(timeout=1.0)
        assert not flush_thread.is_alive()
        assert flush_results == [False]
        assert not active_connections.calls
    finally:
        blocker.release.set()
        barrier_release.set()
        flush_thread.join(timeout=1.0)
        dispatcher.close(timeout=1.0)


def test_dispatcher_unexpected_worker_exit_releases_stop_and_task_accounting() -> None:
    stop_queued = threading.Event()

    class StopObservedQueue(queue.Queue):
        def put_nowait(self, item) -> None:
            super().put_nowait(item)
            if isinstance(item, voice_host._MetricStop):  # pylint: disable=protected-access
                stop_queued.set()

    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    dispatcher._commands = StopObservedQueue(maxsize=4)  # pylint: disable=protected-access
    worker_entered = threading.Event()
    worker_release = threading.Event()
    close_results: list[bool] = []

    def fail_measurement(_measurement) -> bool:
        worker_entered.set()
        worker_release.wait()
        raise RuntimeError("unexpected worker failure")

    dispatcher._execute_measurement = fail_measurement  # type: ignore[method-assign]  # pylint: disable=protected-access
    assert dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=_RecordingInstrument(),
            operation="add",
            value=1,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    assert worker_entered.wait(timeout=1.0)

    close_thread = threading.Thread(
        target=lambda: close_results.append(dispatcher.close(timeout=1.0)),
        name="test_voice_metric_unexpected_exit",
    )
    close_thread.start()
    try:
        assert stop_queued.wait(timeout=1.0)
        worker_release.set()
        close_thread.join(timeout=1.0)
        assert not close_thread.is_alive()
        assert close_results == [True]
        assert dispatcher._commands.empty()  # pylint: disable=protected-access
        assert dispatcher._commands.unfinished_tasks == 0  # pylint: disable=protected-access
        assert dispatcher.close(timeout=1.0)
    finally:
        worker_release.set()
        close_thread.join(timeout=1.0)
        dispatcher.close(timeout=1.0)


def test_dispatcher_recovers_active_target_after_unexpected_open_worker_exit() -> None:
    barrier_queued = threading.Event()

    class BarrierObservedQueue(queue.Queue):
        def put_nowait(self, item) -> None:
            super().put_nowait(item)
            if isinstance(item, voice_host._MetricBarrier):  # pylint: disable=protected-access
                barrier_queued.set()

    dispatcher = voice_host._MetricDispatcher(max_pending=8)  # pylint: disable=protected-access
    dispatcher._commands = BarrierObservedQueue(maxsize=8)  # pylint: disable=protected-access
    original_execute = dispatcher._execute_measurement  # pylint: disable=protected-access
    worker_entered = threading.Event()
    worker_release = threading.Event()
    active_connections = _RecordingInstrument(expected_calls=2)
    queued_measurement = _RecordingInstrument()
    flush_results: list[bool] = []

    def fail_measurement(_measurement) -> bool:
        worker_entered.set()
        worker_release.wait()
        raise RuntimeError("unexpected open worker failure")

    dispatcher._execute_measurement = fail_measurement  # type: ignore[method-assign]  # pylint: disable=protected-access
    assert dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=_RecordingInstrument(),
            operation="add",
            value=1,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    assert worker_entered.wait(timeout=1.0)
    assert dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=queued_measurement,
            operation="add",
            value=2,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    assert dispatcher.submit_active_delta(active_connections, 1)  # pylint: disable=protected-access

    flush_thread = threading.Thread(
        target=lambda: flush_results.append(dispatcher.flush(timeout=1.0)),
        name="test_voice_metric_open_worker_exit",
    )
    flush_thread.start()
    try:
        assert barrier_queued.wait(timeout=1.0)
        worker_release.set()
        flush_thread.join(timeout=1.0)
        assert not flush_thread.is_alive()
        assert flush_results == [False]
        assert dispatcher._stopped.wait(timeout=1.0)  # pylint: disable=protected-access
        assert dispatcher._worker is None  # pylint: disable=protected-access
        assert dispatcher._commands.empty()  # pylint: disable=protected-access
        assert dispatcher._commands.unfinished_tasks == 0  # pylint: disable=protected-access
        assert not queued_measurement.calls

        dispatcher._execute_measurement = original_execute  # type: ignore[method-assign]  # pylint: disable=protected-access
        assert dispatcher.flush(timeout=1.0)
        assert active_connections.calls == [(1, {})]
        assert dispatcher.submit_active_delta(active_connections, -1)  # pylint: disable=protected-access
        assert dispatcher.flush(timeout=1.0)
    finally:
        worker_release.set()
        flush_thread.join(timeout=1.0)
        dispatcher._execute_measurement = original_execute  # type: ignore[method-assign]  # pylint: disable=protected-access
        dispatcher.close(timeout=1.0)

    assert active_connections.calls == [(1, {}), (-1, {})]


def test_active_connection_deltas_remain_balanced_when_metric_queue_is_full(monkeypatch) -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=2)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    blocker = _BlockingInstrument()
    active_connections = _RecordingInstrument()
    filler = _RecordingInstrument(expected_calls=2)
    monkeypatch.setattr(voice_host, "_ACTIVE_CONNECTIONS", active_connections)
    connection_open = threading.Event()
    connection_release = threading.Event()
    failures: list[BaseException] = []

    voice_host._metric_add(blocker, 1)  # pylint: disable=protected-access
    assert blocker.entered.wait(timeout=1.0)
    voice_host._metric_add(filler, 7)  # pylint: disable=protected-access
    voice_host._metric_add(filler, 8)  # pylint: disable=protected-access

    async def hold_connection(_connection) -> None:
        connection_open.set()
        await asyncio.to_thread(connection_release.wait)

    monkeypatch.setattr(voice_host._VoiceConnection, "run", hold_connection)
    app = VoiceAgentServerHost(configure_observability=None)

    def run_connection() -> None:
        try:
            asyncio.run(app._handle_voice_websocket(object()))  # pylint: disable=protected-access
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            failures.append(exc)

    connection_thread = threading.Thread(target=run_connection, name="test_voice_metric_active_connection")
    connection_thread.start()
    try:
        assert connection_open.wait(timeout=1.0)
        blocker.release.set()
        assert filler.recorded.wait(timeout=1.0)
        assert active_connections.recorded.wait(timeout=1.0)
        assert active_connections.calls == [(1, {})]
        assert dispatcher.flush(timeout=1.0)

        connection_release.set()
        connection_thread.join(timeout=1.0)
        assert not connection_thread.is_alive()
        assert not failures
        assert dispatcher.flush(timeout=1.0)
    finally:
        blocker.release.set()
        connection_release.set()
        connection_thread.join(timeout=1.0)
        dispatcher.close(timeout=1.0)

    assert [value for value, _attributes in active_connections.calls] == [1, -1]


def test_active_connection_decrement_uses_admitted_instrument(monkeypatch) -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    admitted_instrument = _RecordingInstrument(expected_calls=2)
    replacement_instrument = _RecordingInstrument()
    monkeypatch.setattr(voice_host, "_ACTIVE_CONNECTIONS", admitted_instrument)
    connection_open = asyncio.Event()
    connection_release = asyncio.Event()

    async def hold_connection(_connection) -> None:
        connection_open.set()
        await connection_release.wait()

    monkeypatch.setattr(voice_host._VoiceConnection, "run", hold_connection)
    app = VoiceAgentServerHost(configure_observability=None)

    async def scenario() -> None:
        connection_task = asyncio.create_task(app._handle_voice_websocket(object()))  # pylint: disable=protected-access
        await asyncio.wait_for(connection_open.wait(), timeout=1.0)
        assert dispatcher.flush(timeout=1.0)
        monkeypatch.setattr(voice_host, "_ACTIVE_CONNECTIONS", replacement_instrument)
        connection_release.set()
        await asyncio.wait_for(connection_task, timeout=1.0)

    try:
        asyncio.run(scenario())
        assert dispatcher.flush(timeout=1.0)
    finally:
        connection_release.set()
        dispatcher.close(timeout=1.0)

    assert admitted_instrument.calls == [(1, {}), (-1, {})]
    assert not replacement_instrument.calls


def test_active_connection_delta_cannot_cross_flush_boundary() -> None:
    barrier_queued = threading.Event()

    class BarrierObservedQueue(queue.Queue):
        def put_nowait(self, item) -> None:
            super().put_nowait(item)
            if isinstance(item, voice_host._MetricBarrier):  # pylint: disable=protected-access
                barrier_queued.set()

    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    dispatcher._commands = BarrierObservedQueue(maxsize=4)  # pylint: disable=protected-access
    blocker = _BlockingInstrument()
    active_connections = _RecordingInstrument(expected_calls=2)
    flush_results: list[bool] = []

    assert dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=blocker,
            operation="add",
            value=1,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    assert blocker.entered.wait(timeout=1.0)
    assert dispatcher.submit_active_delta(active_connections, 1)  # pylint: disable=protected-access

    flush_thread = threading.Thread(
        target=lambda: flush_results.append(dispatcher.flush(timeout=1.0)),
        name="test_voice_metric_flush_boundary",
    )
    flush_thread.start()
    try:
        assert barrier_queued.wait(timeout=1.0)
        assert dispatcher.submit_active_delta(active_connections, -1)  # pylint: disable=protected-access
        blocker.release.set()
        flush_thread.join(timeout=1.0)
        assert not flush_thread.is_alive()
        assert flush_results == [True]
        assert dispatcher.flush(timeout=1.0)
    finally:
        blocker.release.set()
        flush_thread.join(timeout=1.0)
        dispatcher.close(timeout=1.0)

    values = [value for value, _attributes in active_connections.calls]
    assert values == [1, -1]


def test_active_instrument_rebind_waits_for_all_detached_targets() -> None:
    barrier_queued = threading.Event()

    class BarrierObservedQueue(queue.Queue):
        def put_nowait(self, item) -> None:
            super().put_nowait(item)
            if isinstance(item, voice_host._MetricBarrier):  # pylint: disable=protected-access
                barrier_queued.set()

    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    dispatcher._commands = BarrierObservedQueue(maxsize=4)  # pylint: disable=protected-access
    blocker = _BlockingInstrument()
    first_instrument = _RecordingInstrument(expected_calls=2)
    replacement_instrument = _RecordingInstrument(expected_calls=2)
    flush_results: list[bool] = []

    assert dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=blocker,
            operation="add",
            value=1,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    assert blocker.entered.wait(timeout=1.0)
    assert dispatcher.submit_active_delta(first_instrument, 1)  # pylint: disable=protected-access
    flush_thread = threading.Thread(
        target=lambda: flush_results.append(dispatcher.flush(timeout=1.0)),
        name="test_voice_metric_instrument_rebind",
    )
    flush_thread.start()
    try:
        assert barrier_queued.wait(timeout=1.0)
        assert dispatcher.submit_active_delta(first_instrument, -1)  # pylint: disable=protected-access
        assert not dispatcher.submit_active_delta(replacement_instrument, 1)  # pylint: disable=protected-access
        blocker.release.set()
        flush_thread.join(timeout=1.0)
        assert not flush_thread.is_alive()
        assert flush_results == [True]
        assert dispatcher.flush(timeout=1.0)
        assert dispatcher._active.instrument is None  # pylint: disable=protected-access

        assert dispatcher.submit_active_delta(replacement_instrument, 1)  # pylint: disable=protected-access
        assert dispatcher.flush(timeout=1.0)
        assert dispatcher.submit_active_delta(replacement_instrument, -1)  # pylint: disable=protected-access
        assert dispatcher.flush(timeout=1.0)
    finally:
        blocker.release.set()
        flush_thread.join(timeout=1.0)
        dispatcher.close(timeout=1.0)

    assert first_instrument.calls == [(1, {}), (-1, {})]
    assert replacement_instrument.calls == [(1, {}), (-1, {})]


def test_active_targets_remain_ordered_across_full_queue_flush_rotation() -> None:
    barrier_queued = threading.Event()

    class BarrierObservedQueue(queue.Queue):
        def put_nowait(self, item) -> None:
            super().put_nowait(item)
            if isinstance(item, voice_host._MetricBarrier):  # pylint: disable=protected-access
                barrier_queued.set()

    dispatcher = voice_host._MetricDispatcher(max_pending=2)  # pylint: disable=protected-access
    dispatcher._commands = BarrierObservedQueue(maxsize=2)  # pylint: disable=protected-access
    blocker = _BlockingInstrument()
    active_connections = _RecordingInstrument(expected_calls=2)
    flush_results: list[bool] = []

    assert dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=blocker,
            operation="add",
            value=1,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    assert blocker.entered.wait(timeout=1.0)
    assert dispatcher.submit_active_delta(active_connections, 1)  # pylint: disable=protected-access

    flush_thread = threading.Thread(
        target=lambda: flush_results.append(dispatcher.flush(timeout=1.0)),
        name="test_voice_metric_full_queue_rotation",
    )
    flush_thread.start()
    try:
        assert barrier_queued.wait(timeout=1.0)
        for value in (-1, 1, -1):
            assert dispatcher.submit_active_delta(  # pylint: disable=protected-access
                active_connections,
                value,
            )
        blocker.release.set()
        flush_thread.join(timeout=1.0)
        assert not flush_thread.is_alive()
        assert flush_results == [True]
        assert dispatcher.flush(timeout=1.0)
    finally:
        blocker.release.set()
        flush_thread.join(timeout=1.0)
        dispatcher.close(timeout=1.0)

    assert [value for value, _attributes in active_connections.calls] == [1, -1]


def test_concurrent_flushes_do_not_clone_failing_active_target() -> None:
    barriers_queued = threading.Event()
    barrier_count = 0
    barrier_count_lock = threading.Lock()

    class BarriersObservedQueue(queue.Queue):
        def put_nowait(self, item) -> None:
            nonlocal barrier_count
            super().put_nowait(item)
            if isinstance(item, voice_host._MetricBarrier):  # pylint: disable=protected-access
                with barrier_count_lock:
                    barrier_count += 1
                    if barrier_count == 3:
                        barriers_queued.set()

    class FailingActiveInstrument:
        def __init__(self) -> None:
            self.attempts: list[int] = []

        def add(self, value, _attributes=None, context=None) -> None:
            del context
            self.attempts.append(value)
            raise RuntimeError("active target failed")

    dispatcher = voice_host._MetricDispatcher(max_pending=8)  # pylint: disable=protected-access
    dispatcher._commands = BarriersObservedQueue(maxsize=8)  # pylint: disable=protected-access
    blocker = _BlockingInstrument()
    active_connections = FailingActiveInstrument()
    flush_results: list[bool] = []

    assert dispatcher.submit(  # pylint: disable=protected-access
        voice_host._MetricMeasurement(  # pylint: disable=protected-access
            instrument=blocker,
            operation="add",
            value=1,
            attributes=(),
            context=otel_context.Context(),
        )
    )
    assert blocker.entered.wait(timeout=1.0)
    assert dispatcher.submit_active_delta(active_connections, 1)  # pylint: disable=protected-access
    flush_threads = [
        threading.Thread(
            target=lambda: flush_results.append(dispatcher.flush(timeout=1.0)),
            name=f"test_voice_metric_concurrent_flush_{index}",
        )
        for index in range(3)
    ]
    for flush_thread in flush_threads:
        flush_thread.start()
    try:
        assert barriers_queued.wait(timeout=1.0)
        blocker.release.set()
        for flush_thread in flush_threads:
            flush_thread.join(timeout=1.0)
            assert not flush_thread.is_alive()
        assert flush_results == [True, True, True]
    finally:
        blocker.release.set()
        for flush_thread in flush_threads:
            flush_thread.join(timeout=1.0)
        dispatcher.close(timeout=1.0)

    assert active_connections.attempts == [1]


def test_concurrent_active_connection_epochs_remain_balanced() -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=8)  # pylint: disable=protected-access
    active_connections = _RecordingInstrument(expected_calls=2)

    def submit_concurrently(value: int) -> None:
        start = threading.Barrier(9)
        accepted = [False] * 8

        def submit(index: int) -> None:
            start.wait()
            accepted[index] = dispatcher.submit_active_delta(  # pylint: disable=protected-access
                active_connections,
                value,
            )

        threads = [threading.Thread(target=submit, args=(index,)) for index in range(8)]
        for thread in threads:
            thread.start()
        start.wait()
        for thread in threads:
            thread.join(timeout=1.0)
            assert not thread.is_alive()
        assert all(accepted)

    try:
        for value in (1, -1):
            blocker = _BlockingInstrument()
            assert dispatcher.submit(  # pylint: disable=protected-access
                voice_host._MetricMeasurement(  # pylint: disable=protected-access
                    instrument=blocker,
                    operation="add",
                    value=1,
                    attributes=(),
                    context=otel_context.Context(),
                )
            )
            assert blocker.entered.wait(timeout=1.0)
            submit_concurrently(value)
            blocker.release.set()
            assert dispatcher.flush(timeout=1.0)
    finally:
        dispatcher.close(timeout=1.0)

    assert [value for value, _attributes in active_connections.calls] == [8, -8]


def test_active_connection_start_failure_cannot_export_unmatched_decrement(monkeypatch) -> None:
    original_thread = threading.Thread

    class FailFirstStartThread(original_thread):
        start_calls = 0

        def start(self) -> None:
            FailFirstStartThread.start_calls += 1
            if FailFirstStartThread.start_calls == 1:
                raise RuntimeError("thread start failed")
            super().start()

    monkeypatch.setattr(voice_host.threading, "Thread", FailFirstStartThread)
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    active_connections = _RecordingInstrument()

    try:
        increment_accepted = dispatcher.submit_active_delta(  # pylint: disable=protected-access
            active_connections,
            1,
        )
        decrement_accepted = dispatcher.submit_active_delta(  # pylint: disable=protected-access
            active_connections,
            -1,
        )
        assert dispatcher.flush(timeout=1.0)
    finally:
        dispatcher.close(timeout=1.0)

    assert increment_accepted
    assert decrement_accepted
    assert not active_connections.calls


def test_active_connection_thread_constructor_failure_does_not_escape_host(monkeypatch) -> None:
    original_thread = threading.Thread
    construction_calls = 0

    def fail_first_thread_construction(*args, **kwargs):
        nonlocal construction_calls
        construction_calls += 1
        if construction_calls == 1:
            raise RuntimeError("thread construction failed")
        return original_thread(*args, **kwargs)  # pylint: disable=bad-thread-instantiation

    monkeypatch.setattr(voice_host.threading, "Thread", fail_first_thread_construction)
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    active_connections = _RecordingInstrument()
    monkeypatch.setattr(voice_host, "_ACTIVE_CONNECTIONS", active_connections)
    connection_ran = False

    async def run_connection(_connection) -> None:
        nonlocal connection_ran
        connection_ran = True

    monkeypatch.setattr(voice_host._VoiceConnection, "run", run_connection)
    app = VoiceAgentServerHost(configure_observability=None)

    try:
        asyncio.run(app._handle_voice_websocket(object()))  # pylint: disable=protected-access
        assert dispatcher.flush(timeout=1.0)
    finally:
        dispatcher.close(timeout=1.0)

    assert connection_ran
    assert not active_connections.calls


def test_balanced_active_pair_rebinds_after_persistent_worker_construction_failure(monkeypatch) -> None:
    def fail_thread_construction(*_args, **_kwargs):
        raise RuntimeError("thread construction failed")

    monkeypatch.setattr(voice_host.threading, "Thread", fail_thread_construction)
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    first_instrument = _RecordingInstrument()
    replacement_instrument = _RecordingInstrument()

    try:
        assert dispatcher.submit_active_delta(first_instrument, 1)  # pylint: disable=protected-access
        assert dispatcher.submit_active_delta(first_instrument, -1)  # pylint: disable=protected-access
        assert dispatcher.submit_active_delta(replacement_instrument, 1)  # pylint: disable=protected-access
        assert dispatcher.submit_active_delta(replacement_instrument, -1)  # pylint: disable=protected-access
        assert dispatcher._active.instrument is None  # pylint: disable=protected-access
        assert dispatcher._active.pending is None  # pylint: disable=protected-access
        assert dispatcher._active.pending_wake is None  # pylint: disable=protected-access
        assert dispatcher._active.detached == 0  # pylint: disable=protected-access
    finally:
        dispatcher.close(timeout=1.0)

    assert not first_instrument.calls
    assert not replacement_instrument.calls


def test_failed_active_increment_cannot_export_unmatched_decrement() -> None:
    class FailFirstActiveInstrument:
        def __init__(self) -> None:
            self.attempts: list[int] = []
            self.successful: list[int] = []
            self.first_attempted = threading.Event()

        def add(self, value, _attributes=None, context=None) -> None:
            del context
            self.attempts.append(value)
            if len(self.attempts) == 1:
                self.first_attempted.set()
                raise RuntimeError("active increment failed")
            self.successful.append(value)

    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    active_connections = FailFirstActiveInstrument()

    try:
        assert dispatcher.submit_active_delta(active_connections, 1)  # pylint: disable=protected-access
        assert active_connections.first_attempted.wait(timeout=1.0)
        assert dispatcher.submit_active_delta(active_connections, -1)  # pylint: disable=protected-access
        assert dispatcher.flush(timeout=1.0)
    finally:
        dispatcher.close(timeout=1.0)

    assert active_connections.attempts == [1]
    assert not active_connections.successful


def test_metric_dispatch_does_not_retain_caller_context(monkeypatch) -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    blocker = _BlockingInstrument()
    recorder = _RecordingInstrument()
    voice_host._metric_add(blocker, 1)  # pylint: disable=protected-access
    assert blocker.entered.wait(timeout=1.0)

    class Payload:
        pass

    payload = Payload()
    payload_reference = weakref.ref(payload)
    span_context = trace.SpanContext(
        trace_id=0x1234567890ABCDEF1234567890ABCDEF,
        span_id=0x1234567890ABCDEF,
        is_remote=False,
        trace_flags=trace.TraceFlags(trace.TraceFlags.SAMPLED),
        trace_state=trace.TraceState([("vendor", "opaque")]),
    )
    caller_context = trace.set_span_in_context(trace.NonRecordingSpan(span_context))
    caller_context = otel_context.set_value("test.voice.payload", payload, context=caller_context)
    token = otel_context.attach(caller_context)
    try:
        voice_host._metric_add(recorder, 1)  # pylint: disable=protected-access
    finally:
        otel_context.detach(token)
    del caller_context, payload, token

    try:
        gc.collect()
        assert payload_reference() is None
        blocker.release.set()
        assert recorder.recorded.wait(timeout=1.0)
        metric_context = recorder.contexts[0]
        assert metric_context == otel_context.Context()
        assert not trace.get_current_span(metric_context).get_span_context().is_valid
        assert otel_context.get_value("test.voice.payload", context=metric_context) is None
        assert dispatcher.flush(timeout=1.0)
    finally:
        blocker.release.set()
        dispatcher.close(timeout=1.0)


def test_metric_submission_does_not_call_ambient_span(monkeypatch) -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    span_entered = threading.Event()
    span_release = threading.Event()
    caller_returned = threading.Event()
    recorder = _RecordingInstrument()

    class BlockingSpan:
        def get_span_context(self):
            span_entered.set()
            span_release.wait()
            return trace.INVALID_SPAN_CONTEXT

    caller_context = trace.set_span_in_context(BlockingSpan())

    def emit() -> None:
        token = otel_context.attach(caller_context)
        try:
            voice_host._metric_add(recorder, 1)  # pylint: disable=protected-access
            caller_returned.set()
        finally:
            otel_context.detach(token)

    caller = threading.Thread(target=emit, name="test_voice_metric_span_context")
    caller.start()
    try:
        assert caller_returned.wait(timeout=1.0)
        assert not span_entered.is_set()
        assert recorder.recorded.wait(timeout=1.0)
        assert recorder.contexts == [otel_context.Context()]
    finally:
        span_release.set()
        caller.join(timeout=1.0)
        dispatcher.close(timeout=1.0)
    assert not caller.is_alive()


def test_metric_worker_does_not_inherit_first_caller_context(monkeypatch) -> None:
    class InheritingThread(threading.Thread):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.inherited_context: contextvars.Context | None = None

        def start(self) -> None:
            self.inherited_context = contextvars.copy_context()
            super().start()

        def run(self) -> None:
            assert self.inherited_context is not None
            self.inherited_context.run(super().run)

    class AmbientRecordingInstrument:
        def __init__(self) -> None:
            self.ambient_payload_present = False
            self.explicit_context = None
            self.recorded = threading.Event()

        def add(self, _value, _attributes=None, context=None) -> None:
            self.ambient_payload_present = otel_context.get_value("test.voice.worker_payload") is not None
            self.explicit_context = context
            self.recorded.set()

    monkeypatch.setattr(voice_host.threading, "Thread", InheritingThread)
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    instrument = AmbientRecordingInstrument()

    class Payload:
        pass

    payload = Payload()
    payload_reference = weakref.ref(payload)
    caller_context = otel_context.set_value("test.voice.worker_payload", payload)
    token = otel_context.attach(caller_context)
    try:
        voice_host._metric_add(instrument, 1)  # pylint: disable=protected-access
    finally:
        otel_context.detach(token)
    del caller_context, payload, token

    try:
        assert instrument.recorded.wait(timeout=1.0)
        gc.collect()
        assert not instrument.ambient_payload_present
        assert instrument.explicit_context == otel_context.Context()
        assert payload_reference() is None
    finally:
        dispatcher.close(timeout=1.0)


def test_metric_provider_cannot_contaminate_worker_context(monkeypatch) -> None:
    dispatcher = voice_host._MetricDispatcher(max_pending=4)  # pylint: disable=protected-access
    monkeypatch.setattr(voice_host, "_METRIC_DISPATCHER", dispatcher)
    provider_value = contextvars.ContextVar("test_voice_metric_provider_value")

    class Payload:
        pass

    class ContaminatingInstrument:
        def __init__(self, payload) -> None:
            self.payload = payload

        def add(self, _value, _attributes=None, context=None) -> None:
            del context
            provider_value.set(self.payload)
            self.payload = None

    class AmbientRecordingInstrument:
        def __init__(self) -> None:
            self.ambient_value = None

        def add(self, _value, _attributes=None, context=None) -> None:
            del context
            self.ambient_value = provider_value.get(None)

    payload = Payload()
    payload_reference = weakref.ref(payload)
    contaminating_instrument = ContaminatingInstrument(payload)
    recorder = AmbientRecordingInstrument()
    del payload

    try:
        voice_host._metric_add(contaminating_instrument, 1)  # pylint: disable=protected-access
        assert dispatcher.flush(timeout=1.0)
        del contaminating_instrument
        gc.collect()
        assert payload_reference() is None

        voice_host._metric_add(recorder, 1)  # pylint: disable=protected-access
        assert dispatcher.flush(timeout=1.0)
        assert recorder.ambient_value is None
    finally:
        dispatcher.close(timeout=1.0)


def test_counter_failure_is_isolated() -> None:
    voice_host._metric_add(_FailingInstrument(), 1, {"kind": "test"})  # pylint: disable=protected-access
    assert voice_host._flush_metric_dispatch(timeout=1.0)  # pylint: disable=protected-access


def test_histogram_failure_is_isolated() -> None:
    voice_host._metric_record(  # pylint: disable=protected-access
        _FailingInstrument(),
        1.0,
        {"kind": "test"},
    )
    assert voice_host._flush_metric_dispatch(timeout=1.0)  # pylint: disable=protected-access


def test_telemetry_failures_do_not_change_protocol_outcome(monkeypatch) -> None:
    instrument = _FailingInstrument()
    for name in (
        "_ACTIVATION_COUNTER",
        "_CALLBACK_DURATION",
        "_FIRST_OUTPUT_DURATION",
        "_TERMINAL_COUNTER",
        "_ACTIVE_CONNECTIONS",
        "_CLOSE_CODE_COUNTER",
    ):
        monkeypatch.setattr(voice_host, name, instrument)

    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.send_text("still works")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        websocket.send_json(
            {
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
        )
        assert websocket.receive_json()["type"] == "session.ready"
        websocket.send_json(
            {
                "type": "user.message",
                "id": "m_user",
                "ts": _TS,
                "item_id": "in_1",
                "content": [{"type": "input_text", "text": "hello"}],
            }
        )
        created = websocket.receive_json()
        output = websocket.receive_json()
        done = websocket.receive_json()

    assert voice_host._flush_metric_dispatch(timeout=1.0)  # pylint: disable=protected-access

    assert created["type"] == "response.created"
    assert output["type"] == "response.output_text.done"
    assert done["type"] == "response.done"
