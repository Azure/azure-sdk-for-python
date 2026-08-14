# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Thin connection context for explicit Voice event sends."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import contextvars
import sys
from collections.abc import Coroutine, MutableMapping
from threading import Lock
from typing import Any, TypeVar, cast

from starlette.types import Send
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from azure.ai.agentserver.core import experimental

from ._codec import encode_outbound_message
from ._models import OutboundVoiceMessage, SessionDisconnected

_VOICE_SESSION_SCOPE_KEY = "azure.ai.agentserver.invocations.voice.session"
_VOICE_CLOSE_CODE_SCOPE_KEY = "azure.ai.agentserver.invocations.voice.close_code"
_VOICE_DISCONNECT_EVENT_SCOPE_KEY = "azure.ai.agentserver.invocations.voice.disconnect_event"
CLOSE_TIMEOUT_SECONDS = 5.0
_MAX_CLOSE_ATTEMPTS = 256
_CLOSE_ATTEMPTS: set[asyncio.Task[None]] = set()
_CLOSE_ATTEMPT_RESERVATIONS = 0
_CLOSE_ATTEMPT_LOCK = Lock()


_TransportResultT = TypeVar("_TransportResultT")


class _OperationCancellationState:
    __slots__ = ("cancellation", "cancellation_requests", "operation_cancel_requested")

    def __init__(self) -> None:
        self.cancellation: asyncio.CancelledError | None = None
        self.cancellation_requests = 0
        self.operation_cancel_requested = False


class _OperationCancellationWaiter(asyncio.Future):
    __slots__ = ("operation", "state")

    def __init__(self, operation: asyncio.Task[Any], state: _OperationCancellationState) -> None:
        super().__init__()
        self.operation = operation
        self.state = state

    def cancel(self, msg: object | None = None) -> bool:
        if self.done():
            return False
        self.state.cancellation = asyncio.CancelledError(msg) if msg is not None else asyncio.CancelledError()
        self.state.cancellation_requests += 1
        self.state.operation_cancel_requested = self.operation.cancel(msg)
        return True


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


def _task_cancellation_requests() -> int | None:
    if sys.version_info < (3, 11):
        return None
    try:
        task = asyncio.current_task()
    except RuntimeError:
        return None
    cancelling = getattr(task, "cancelling", None)
    return int(cancelling()) if callable(cancelling) else None


def _raise_task_cancellation(
    error: BaseException,
    cancellation_requests: int | None,
) -> None:
    cancellation = _find_cancellation(error)
    if cancellation is None or cancellation is error:
        return
    current_requests = _task_cancellation_requests()
    task_cancelled = (
        cancellation_requests is not None and current_requests is not None and current_requests > cancellation_requests
    )
    if not task_cancelled:
        return
    _unlink_exception(error, cancellation)
    raise cancellation from error


def _transfer_send_result(operation: asyncio.Task[BaseException | None], waiter: _OperationCancellationWaiter) -> None:
    if waiter.done():
        if not operation.cancelled():
            operation.exception()
        return
    if operation.cancelled():
        cancellation = waiter.state.cancellation
        if cancellation is None:
            try:
                operation.result()
            except asyncio.CancelledError as operation_cancellation:
                cancellation = operation_cancellation
        waiter.set_result(cancellation)
        return
    waiter.set_result(operation.result())


async def _run_send_operation(
    operation_coroutine: Coroutine[Any, Any, BaseException | None],
    state: _OperationCancellationState,
) -> None:
    try:
        operation = asyncio.create_task(operation_coroutine, name="voice_websocket_send")
    except BaseException:  # pylint: disable=broad-exception-caught
        _close_coroutine(operation_coroutine)
        raise
    waiter = _OperationCancellationWaiter(operation, state)
    operation.add_done_callback(lambda completed: _transfer_send_result(completed, waiter))
    outcome = await waiter
    if isinstance(outcome, BaseException):
        error = outcome
        cancellation = state.cancellation
        if cancellation is None:
            raise error
        nested_cancellation = _find_cancellation(error)
        if nested_cancellation is not None:
            if nested_cancellation is not error:
                _unlink_exception(error, nested_cancellation)
                raise nested_cancellation from error
            raise error
        raise cancellation from error
    if state.cancellation is not None:
        raise state.cancellation


def _transfer_transport_result(operation: asyncio.Task[Any], waiter: _OperationCancellationWaiter) -> None:
    if waiter.done():
        if not operation.cancelled():
            operation.exception()
        return
    if operation.cancelled():
        try:
            operation.result()
        except asyncio.CancelledError as cancellation:
            waiter.set_result((None, cancellation))
        return
    error = operation.exception()
    waiter.set_result((None, error) if error is not None else (operation.result(), None))


async def _run_transport_operation(
    operation_coroutine: Coroutine[Any, Any, _TransportResultT],
) -> _TransportResultT:
    """Run one SDK-owned transport await without losing owner cancellation.

    :param operation_coroutine: SDK-owned transport coroutine to execute.
    :type operation_coroutine: Coroutine[Any, Any, _TransportResultT]
    :return: The result produced by the transport coroutine.
    :rtype: _TransportResultT

    The transport must eventually settle after cancellation. A single delivered
    cancellation preserves its nested identity when available. After repeated
    owner cancellation, the latest saved owner request wins; exact cancellation
    identity from a transport-defined exception graph is unspecified. This helper
    is not used for application callbacks, whose cancellation is cooperative.
    """
    state = _OperationCancellationState()
    try:
        operation = asyncio.create_task(operation_coroutine, name="voice_websocket_transport")
    except BaseException:  # pylint: disable=broad-exception-caught
        _close_coroutine(operation_coroutine)
        raise
    waiter = _OperationCancellationWaiter(operation, state)
    operation.add_done_callback(lambda completed: _transfer_transport_result(completed, waiter))
    result, error = cast(tuple[Any, BaseException | None], await waiter)
    if state.cancellation is not None:
        if error is None:
            raise state.cancellation
        nested_cancellation = _find_cancellation(error)
        if state.cancellation_requests == 1 and state.operation_cancel_requested and nested_cancellation is not None:
            if nested_cancellation is not error:
                _unlink_exception(error, nested_cancellation)
                raise nested_cancellation from error
            raise error
        raise state.cancellation from error
    if error is not None:
        raise error
    return cast(_TransportResultT, result)


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
        application_state = websocket.application_state
        if application_state == WebSocketState.DISCONNECTED:
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
            websocket.application_state = application_state
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
        attempt.result()

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
        cancellation_state = _OperationCancellationState()

        async def send_frame() -> BaseException | None:
            try:
                async with self._send_lock:
                    self._ensure_writable()
                    try:
                        await self._websocket.send_text(frame)
                    except WebSocketDisconnect as error:
                        if cancellation_state.cancellation is None or _find_cancellation(error) is None:
                            self._begin_termination()
                            scope = getattr(self._websocket, "scope", None)
                            if isinstance(scope, MutableMapping):
                                raw_reason = getattr(error, "reason", None)
                                reason = raw_reason if isinstance(raw_reason, str) and raw_reason else None
                                code = int(error.code or 1006)
                                scope.setdefault(_VOICE_CLOSE_CODE_SCOPE_KEY, code)
                                scope.setdefault(
                                    _VOICE_DISCONNECT_EVENT_SCOPE_KEY,
                                    SessionDisconnected(code=code, reason=reason),
                                )
                        return error
            except BaseException as error:  # pylint: disable=broad-exception-caught
                return error
            return None

        await _run_send_operation(send_frame(), cancellation_state)
