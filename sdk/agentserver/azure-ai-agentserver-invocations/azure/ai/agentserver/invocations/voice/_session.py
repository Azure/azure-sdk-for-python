# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Thin connection context for explicit Voice event sends."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import contextvars
from collections.abc import Coroutine, MutableMapping
from threading import Lock
from typing import Any

from starlette.types import Send
from starlette.websockets import WebSocket, WebSocketState

from azure.ai.agentserver.core import experimental

from ._codec import encode_outbound_message
from ._models import OutboundVoiceMessage

_VOICE_SESSION_SCOPE_KEY = "azure.ai.agentserver.invocations.voice.session"
CLOSE_TIMEOUT_SECONDS = 5.0
_MAX_CLOSE_ATTEMPTS = 256
_CLOSE_ATTEMPTS: set[asyncio.Task[None]] = set()
_CLOSE_ATTEMPT_RESERVATIONS = 0
_CLOSE_ATTEMPT_LOCK = Lock()


def _close_coroutine(coroutine: Coroutine[Any, Any, Any]) -> None:
    coroutine.close()


def _find_cancellation(error: BaseException) -> asyncio.CancelledError | None:
    pending = [error]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, asyncio.CancelledError):
            return current
        if current.__context__ is not None:
            pending.append(current.__context__)
        if current.__cause__ is not None:
            pending.append(current.__cause__)
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


async def _run_close_attempt(
    send_lock: asyncio.Lock,
    send: Send,
    message: dict[str, Any],
) -> None:
    async with send_lock:
        await send(message)


def _observe_close_attempt(task: asyncio.Task[None]) -> None:
    with _CLOSE_ATTEMPT_LOCK:
        _CLOSE_ATTEMPTS.discard(task)
    if task.cancelled():
        return
    task.exception()


def _start_close_attempt(
    send_lock: asyncio.Lock,
    websocket: WebSocket,
    code: int,
    reason: str,
) -> asyncio.Task[None] | None:
    global _CLOSE_ATTEMPT_RESERVATIONS  # pylint: disable=global-statement
    send = websocket._send  # pylint: disable=protected-access
    message = {"type": "websocket.close", "code": code, "reason": reason}
    with _CLOSE_ATTEMPT_LOCK:
        if websocket.application_state == WebSocketState.DISCONNECTED:
            return None
        if len(_CLOSE_ATTEMPTS) + _CLOSE_ATTEMPT_RESERVATIONS >= _MAX_CLOSE_ATTEMPTS:
            raise RuntimeError("Voice WebSocket close attempt limit reached")
        _CLOSE_ATTEMPT_RESERVATIONS += 1
        websocket.application_state = WebSocketState.DISCONNECTED
    close_coroutine = _run_close_attempt(send_lock, send, message)
    try:
        task = contextvars.Context().run(asyncio.create_task, close_coroutine, name="voice_websocket_close")
    except BaseException as creation_error:  # pylint: disable=broad-exception-caught
        with _CLOSE_ATTEMPT_LOCK:
            _CLOSE_ATTEMPT_RESERVATIONS -= 1
        try:
            _close_coroutine(close_coroutine)
        except BaseException:  # pylint: disable=broad-exception-caught
            pass
        raise creation_error
    with _CLOSE_ATTEMPT_LOCK:
        _CLOSE_ATTEMPT_RESERVATIONS -= 1
        _CLOSE_ATTEMPTS.add(task)
    task.add_done_callback(_observe_close_attempt, context=contextvars.Context())
    return task


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

    def _begin_termination(self) -> None:
        self._terminal = True

    def _start_close(self, code: int, reason: str) -> asyncio.Task[None] | None:
        self._begin_termination()
        return _start_close_attempt(self._send_lock, self._websocket, code, reason)

    @staticmethod
    async def _wait_close(attempt: asyncio.Task[None] | None, deadline: float) -> None:
        if attempt is None:
            return
        loop = asyncio.get_running_loop()
        remaining = max(0.0, deadline - loop.time())
        done, _ = await asyncio.wait((attempt,), timeout=remaining)
        if not done:
            raise TimeoutError("Voice WebSocket close deadline elapsed")
        try:
            attempt.result()
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            cancellation = _find_cancellation(exc)
            if cancellation is not None and cancellation is not exc:
                _unlink_exception(exc, cancellation)
                raise cancellation from exc
            raise

    async def _close(
        self,
        code: int,
        reason: str,
        deadline: float | None = None,
    ) -> None:
        self._begin_termination()
        loop = asyncio.get_running_loop()
        if deadline is None:
            deadline = loop.time() + CLOSE_TIMEOUT_SECONDS
        remaining = deadline - loop.time()
        if remaining <= 0:
            raise TimeoutError("Voice WebSocket close deadline elapsed")
        attempt = self._start_close(code, reason)
        await self._wait_close(attempt, deadline)

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
