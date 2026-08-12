# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Thin connection context for explicit Voice event sends."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from collections.abc import Coroutine, MutableMapping
from typing import Any, cast

from starlette.websockets import WebSocket, WebSocketState

from azure.ai.agentserver.core import experimental

from ._codec import encode_outbound_message
from ._models import OutboundVoiceMessage

_VOICE_SESSION_SCOPE_KEY = "azure.ai.agentserver.invocations.voice.session"


def _close_coroutine(coroutine: Coroutine[Any, Any, Any]) -> None:
    coroutine.close()


def _find_cancellation(error: BaseException) -> asyncio.CancelledError | None:
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        if isinstance(current, asyncio.CancelledError):
            return current
        seen.add(id(current))
        current = current.__cause__ or current.__context__
    return None


def _unlink_exception(error: BaseException, target: BaseException) -> None:
    pending = [error]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        cause = current.__cause__
        context = current.__context__
        if cause is target:
            current.__cause__ = None
        elif cause is not None:
            pending.append(cause)
        if context is target:
            current.__context__ = None
        elif context is not None:
            pending.append(context)


@experimental
class Session:
    """Send-only context for one accepted Voice WebSocket connection.

    ``Session`` retains only transport write serialization and a terminal write
    gate. Agent code owns response IDs, pending work, generation tasks,
    terminal-event correlation, cancellation, history, and reconnect
    restoration.

    Instances are created by :class:`VoiceAgentServerHost` and supplied to
    registered callbacks.
    """

    __slots__ = ("_send_lock", "_terminal", "_websocket")
    _send_lock: asyncio.Lock
    _terminal: bool
    _websocket: WebSocket

    def __init__(self) -> None:
        raise TypeError("Session instances are created by VoiceAgentServerHost")

    @classmethod
    def _create(cls, websocket: WebSocket) -> "Session":
        current = cls._current(websocket)
        if current is not None:
            return current
        instance = object.__new__(cls)
        instance._websocket = websocket
        instance._send_lock = asyncio.Lock()
        instance._terminal = False
        scope = getattr(websocket, "scope", None)
        if isinstance(scope, MutableMapping):
            scope[_VOICE_SESSION_SCOPE_KEY] = instance
        return instance

    @classmethod
    def _current(cls, websocket: WebSocket) -> "Session | None":
        scope = getattr(websocket, "scope", None)
        if not isinstance(scope, MutableMapping):
            return None
        current = scope.get(_VOICE_SESSION_SCOPE_KEY)
        return current if isinstance(current, cls) else None

    @classmethod
    def _release(cls, websocket: WebSocket, session: "Session") -> None:
        scope = getattr(websocket, "scope", None)
        if isinstance(scope, MutableMapping) and scope.get(_VOICE_SESSION_SCOPE_KEY) is session:
            del scope[_VOICE_SESSION_SCOPE_KEY]

    async def _close(
        self,
        code: int,
        reason: str,
        prior_cancellation: asyncio.CancelledError | None = None,
    ) -> None:
        self._terminal = True
        if prior_cancellation is not None:
            raise prior_cancellation
        acquire_coroutine = cast(Coroutine[Any, Any, bool], self._send_lock.acquire())
        try:
            acquire_task = asyncio.create_task(acquire_coroutine, name="voice_session_close_lock")
        except BaseException:  # pylint: disable=broad-exception-caught
            _close_coroutine(acquire_coroutine)
            raise

        cancellation: asyncio.CancelledError | None = None
        cancelled_acquire_for_outer = False
        while not acquire_task.done():
            try:
                await asyncio.shield(acquire_task)
            except asyncio.CancelledError as exc:
                if acquire_task.done():
                    if not acquire_task.cancelled() and cancellation is None:
                        cancellation = exc
                    break
                if cancellation is None:
                    cancellation = exc
                cancelled_acquire_for_outer = True
                acquire_task.cancel()

        acquired = False
        close_error: BaseException | None = None
        try:
            acquire_task.result()
            acquired = True
            if cancellation is None and self._websocket.application_state != WebSocketState.DISCONNECTED:
                await self._websocket.close(code=code, reason=reason)
        except asyncio.CancelledError as exc:
            if not cancelled_acquire_for_outer or cancellation is None:
                cancellation = exc
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            close_error = exc
            if cancellation is None:
                cancellation = _find_cancellation(exc)
        finally:
            if acquired:
                self._send_lock.release()
        if cancellation is not None:
            if close_error is not None:
                _unlink_exception(close_error, cancellation)
                raise cancellation from close_error
            raise cancellation
        if close_error is not None:
            raise close_error

    def _ensure_writable(self) -> None:
        if self._terminal:
            raise RuntimeError("Voice Session is terminating")

    async def send(self, message: OutboundVoiceMessage) -> None:
        """Encode and send one explicit agent-to-Bridge event.

        Concurrent calls are serialized at the WebSocket write boundary. The
        method does not retry, infer commitment, or update protocol state.

        :param message: One immutable selected outbound message.
        :type message: OutboundVoiceMessage
        """
        self._ensure_writable()
        frame = encode_outbound_message(message)
        async with self._send_lock:
            self._ensure_writable()
            await self._websocket.send_text(frame)
