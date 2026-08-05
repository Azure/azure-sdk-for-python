# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic activation receive-boundary regression tests."""

import asyncio
import json

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
            on_dtmf_key=None,
            on_dtmf_collected=None,
            on_dtmf_collection_rejected=None,
            on_dtmf_collection_cancelled=None,
            on_handoff_failed=None,
            on_conversation_item_create=None,
            on_conversation_item_delete=None,
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


def test_readiness_failure_cleans_transferred_receive_task() -> None:
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
            on_dtmf_key=None,
            on_dtmf_collected=None,
            on_dtmf_collection_rejected=None,
            on_dtmf_collection_cancelled=None,
            on_handoff_failed=None,
            on_conversation_item_create=None,
            on_conversation_item_delete=None,
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
