# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic activation receive-boundary regression tests."""

import asyncio
import json

import pytest

from azure.ai.agentserver.invocations.voice import _host as voice_host

_TS = "2026-07-23T12:00:00.000Z"


def _receive_message(payload: dict) -> dict:
    return {"type": "websocket.receive", "text": json.dumps(payload)}


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


@pytest.mark.parametrize("eager", [False, True])
def test_frame_received_while_ready_waits_for_send_lock_is_rejected(eager: bool) -> None:
    async def scenario() -> None:
        loop = asyncio.get_running_loop()
        original_factory = loop.get_task_factory()
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


def test_startup_receive_delivery_is_not_dropped_during_task_handoff() -> None:
    async def scenario() -> None:
        loop = asyncio.get_running_loop()

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
                self.sent.append(json.loads(data))

            async def close(self, **fields) -> None:
                self.closes.append(fields)

        websocket = OneShotBoundaryWebSocket()
        websocket.start_delivery.set_result(_receive_message(_start()))
        boundary_message = _receive_message(_user_message())

        async def on_session_start(_session, _event) -> None:
            # Wake the activation coordinator before the receive task resumes.
            # Replacing that receive would lose this one-shot ASGI delivery and
            # wait forever on ``after_boundary``.
            loop.call_soon(
                lambda: loop.call_soon(
                    websocket.boundary_delivery.set_result,
                    boundary_message,
                )
            )

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

        assert not await asyncio.wait_for(connection._activate(), timeout=1.0)  # pylint: disable=protected-access
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
        await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access

    asyncio.run(scenario())
