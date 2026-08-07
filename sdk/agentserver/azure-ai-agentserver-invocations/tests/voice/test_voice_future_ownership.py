# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic correlation ownership tests for awaited transitions."""

import asyncio
import gc
import json

from azure.ai.agentserver.invocations.voice import (
    ResponseTimeoutEvent,
    VoiceBridgeConnectionClosedError,
    VoiceResponse,
)
from azure.ai.agentserver.invocations.voice import _host as voice_host


class _RecordingWebSocket:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send_text(self, frame: str) -> None:
        self.sent.append(json.loads(frame))

    async def close(self, **_fields) -> None:
        return None


def _connection() -> voice_host._VoiceConnection:  # pylint: disable=protected-access
    connection = voice_host._VoiceConnection(  # pylint: disable=protected-access
        websocket=_RecordingWebSocket(),
        on_session_start=None,
        on_user_message=None,
        on_user_no_input=None,
        on_user_speech_started=None,
        on_handoff_failed=None,
        on_barge_in=None,
        on_response_timeout=None,
        on_session_end=None,
    )
    connection._ready = True  # pylint: disable=protected-access
    return connection


def test_shutdown_owns_proactive_future_while_accept_transition_waits() -> None:
    async def scenario() -> None:
        connection = _connection()
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_accept",
            in_reply_to=None,
            wire_opened=True,
            accepted=False,
        )
        future: asyncio.Future[tuple[bool, str]] = asyncio.get_running_loop().create_future()
        pending = (response, future)
        connection._pending_proactive[response.response_id] = pending  # pylint: disable=protected-access
        connection._seen_response_ids.add(response.response_id)  # pylint: disable=protected-access

        entered = asyncio.Event()
        release = asyncio.Event()
        original_mark_accepted = response._mark_accepted  # pylint: disable=protected-access

        async def blocked_mark_accepted() -> None:
            entered.set()
            await release.wait()
            await original_mark_accepted()

        response._mark_accepted = blocked_mark_accepted  # type: ignore[method-assign]  # pylint: disable=protected-access
        handler = asyncio.create_task(
            connection._handle_response_accepted(  # pylint: disable=protected-access
                {"response_id": response.response_id}
            )
        )
        await entered.wait()

        assert connection._pending_proactive.get(response.response_id) is pending  # pylint: disable=protected-access
        assert connection._active_response is None  # pylint: disable=protected-access
        async with connection._state_lock:  # pylint: disable=protected-access
            connection._ending = True  # pylint: disable=protected-access
            connection._fail_pending_proactive_locked("closed")  # pylint: disable=protected-access

        release.set()
        await handler

        assert isinstance(future.exception(), VoiceBridgeConnectionClosedError)
        assert connection._active_response is None  # pylint: disable=protected-access
        assert response.response_id not in connection._response_start_ns  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_shutdown_owns_proactive_future_while_drop_transition_waits() -> None:
    async def scenario() -> None:
        connection = _connection()
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_drop",
            in_reply_to=None,
            wire_opened=True,
            accepted=False,
        )
        future: asyncio.Future[tuple[bool, str]] = asyncio.get_running_loop().create_future()
        pending = (response, future)
        connection._pending_proactive[response.response_id] = pending  # pylint: disable=protected-access
        connection._seen_response_ids.add(response.response_id)  # pylint: disable=protected-access

        entered = asyncio.Event()
        release = asyncio.Event()
        original_mark_terminal = response._mark_terminal  # pylint: disable=protected-access

        async def blocked_mark_terminal() -> None:
            entered.set()
            await release.wait()
            await original_mark_terminal()

        response._mark_terminal = blocked_mark_terminal  # type: ignore[method-assign]  # pylint: disable=protected-access
        handler = asyncio.create_task(
            connection._handle_response_dropped(  # pylint: disable=protected-access
                {"response_id": response.response_id, "reason": "superseded"}
            )
        )
        await entered.wait()

        assert connection._pending_proactive.get(response.response_id) is pending  # pylint: disable=protected-access
        async with connection._state_lock:  # pylint: disable=protected-access
            connection._ending = True  # pylint: disable=protected-access
            connection._fail_pending_proactive_locked("closed")  # pylint: disable=protected-access

        release.set()
        await handler

        assert isinstance(future.exception(), VoiceBridgeConnectionClosedError)
        assert response.response_id not in connection._pending_proactive  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_shutdown_owns_cancel_waiter_while_playback_transition_waits() -> None:
    async def scenario() -> None:
        connection = _connection()
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_cancel",
            in_reply_to=None,
            wire_opened=True,
        )
        connection._active_response = response  # pylint: disable=protected-access
        connection._seen_response_ids.add(response.response_id)  # pylint: disable=protected-access
        waiter: asyncio.Future = asyncio.get_running_loop().create_future()
        connection._cancel_waiters[response.response_id] = waiter  # pylint: disable=protected-access

        entered = asyncio.Event()
        release = asyncio.Event()
        original_mark_terminal = response._mark_terminal  # pylint: disable=protected-access

        async def blocked_mark_terminal() -> None:
            entered.set()
            await release.wait()
            await original_mark_terminal()

        response._mark_terminal = blocked_mark_terminal  # type: ignore[method-assign]  # pylint: disable=protected-access
        handler = asyncio.create_task(
            connection._handle_playback_terminal(  # pylint: disable=protected-access
                {
                    "response_id": response.response_id,
                    "heard_text": "partial",
                },
                kind="cancelled",
            )
        )
        await entered.wait()

        assert connection._cancel_waiters.get(response.response_id) is waiter  # pylint: disable=protected-access
        connection._fail_helper_waiters("closed")  # pylint: disable=protected-access
        release.set()
        await handler

        assert isinstance(waiter.exception(), VoiceBridgeConnectionClosedError)
        assert response.response_id not in connection._cancel_waiters  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_shutdown_owns_cancel_waiter_while_timeout_transition_waits() -> None:
    async def scenario() -> None:
        connection = _connection()
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_timeout",
            in_reply_to=None,
            wire_opened=True,
        )
        connection._active_response = response  # pylint: disable=protected-access
        connection._seen_response_ids.add(response.response_id)  # pylint: disable=protected-access
        waiter: asyncio.Future = asyncio.get_running_loop().create_future()
        connection._cancel_waiters[response.response_id] = waiter  # pylint: disable=protected-access

        entered = asyncio.Event()
        release = asyncio.Event()
        original_mark_terminal = response._mark_terminal  # pylint: disable=protected-access

        async def blocked_mark_terminal() -> None:
            entered.set()
            await release.wait()
            await original_mark_terminal()

        response._mark_terminal = blocked_mark_terminal  # type: ignore[method-assign]  # pylint: disable=protected-access
        handler = asyncio.create_task(
            connection._handle_response_timeout(  # pylint: disable=protected-access
                ResponseTimeoutEvent(stage="idle", response_id=response.response_id)
            )
        )
        await entered.wait()

        assert connection._cancel_waiters.get(response.response_id) is waiter  # pylint: disable=protected-access
        connection._fail_helper_waiters("closed")  # pylint: disable=protected-access
        release.set()
        await handler

        assert isinstance(waiter.exception(), VoiceBridgeConnectionClosedError)
        assert response.response_id not in connection._cancel_waiters  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_abandoned_cancel_waiter_observes_shutdown_exception() -> None:
    async def scenario() -> None:
        loop = asyncio.get_running_loop()
        unhandled: list[dict] = []
        loop.set_exception_handler(lambda _loop, context: unhandled.append(context))
        connection = _connection()
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_abandoned",
            in_reply_to=None,
            wire_opened=True,
        )
        connection._active_response = response  # pylint: disable=protected-access
        connection._seen_response_ids.add(response.response_id)  # pylint: disable=protected-access

        cancel_task = asyncio.create_task(response.cancel())
        while response.response_id not in connection._cancel_waiters:  # pylint: disable=protected-access
            await asyncio.sleep(0)
        cancel_task.cancel()
        await asyncio.gather(cancel_task, return_exceptions=True)

        connection._fail_helper_waiters("closed")  # pylint: disable=protected-access
        await asyncio.sleep(0)
        del cancel_task
        gc.collect()
        await asyncio.sleep(0)

        assert not [context for context in unhandled if "never retrieved" in context.get("message", "")]

    asyncio.run(scenario())
