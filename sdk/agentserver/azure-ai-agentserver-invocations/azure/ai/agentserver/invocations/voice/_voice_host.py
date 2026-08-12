# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Typed event relay over the existing Invocations WebSocket transport."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, NoReturn, TypeVar, cast

from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.core import experimental

from .._invocation import InvocationAgentServerHost
from ._codec import MAX_FRAME_BYTES, VoiceProtocolError, decode_inbound_message
from ._models import (
    BargeIn,
    InboundVoiceMessage,
    ResponseAccepted,
    ResponseCancelled,
    ResponseDropped,
    ResponseTimeout,
    SessionDisconnected,
    SessionEnd,
    SessionStart,
    UserMessage,
    UserNoInput,
    UserSpeechStarted,
)
from ._session import Session

SessionStartCallback = Callable[[Session, SessionStart], Awaitable[None]]
UserMessageCallback = Callable[[Session, UserMessage], Awaitable[None]]
UserNoInputCallback = Callable[[Session, UserNoInput], Awaitable[None]]
UserSpeechStartedCallback = Callable[[Session, UserSpeechStarted], Awaitable[None]]
BargeInCallback = Callable[[Session, BargeIn], Awaitable[None]]
ResponseAcceptedCallback = Callable[[Session, ResponseAccepted], Awaitable[None]]
ResponseDroppedCallback = Callable[[Session, ResponseDropped], Awaitable[None]]
ResponseCancelledCallback = Callable[[Session, ResponseCancelled], Awaitable[None]]
ResponseTimeoutCallback = Callable[[Session, ResponseTimeout], Awaitable[None]]
SessionEndCallback = Callable[[Session, SessionEnd], Awaitable[None]]
DisconnectCallback = Callable[[Session, SessionDisconnected], Awaitable[None]]

_CallbackT = TypeVar("_CallbackT", bound=Callable[..., Awaitable[None]])
_VoiceCallback = Callable[[Session, Any], Awaitable[None]]


@experimental
class VoiceAgentServerHost(InvocationAgentServerHost):
    """Invocations host with typed Voice event decorators.

    The host performs only per-frame decoding and static callback dispatch.
    Agent code owns IDs, application tasks, response lifecycle, terminal-event
    correlation, cancellation, history, and reconnect restoration.

    :param openapi_spec: Optional OpenAPI document inherited from Invocations.
    :param asyncapi_spec_json: Optional AsyncAPI JSON document.
    :param asyncapi_spec_yaml: Optional AsyncAPI YAML document.
    :param kwargs: Remaining :class:`InvocationAgentServerHost` options.
    """

    def __init__(
        self,
        *,
        openapi_spec: dict[str, Any] | None = None,
        asyncapi_spec_json: dict[str, Any] | None = None,
        asyncapi_spec_yaml: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._voice_callbacks: dict[str, _VoiceCallback] = {}
        super().__init__(
            openapi_spec=openapi_spec,
            asyncapi_spec_json=asyncapi_spec_json,
            asyncapi_spec_yaml=asyncapi_spec_yaml,
            **kwargs,
        )
        super().ws_handler(self._handle_voice_connection)

    def ws_handler(self, fn: Any) -> NoReturn:
        """Reject raw-handler registration on the typed Voice host.

        :param fn: Raw handler supplied by the caller.
        :type fn: Any
        :raises RuntimeError: Always; the typed host owns ``/invocations_ws``.
        """
        del fn
        raise RuntimeError("VoiceAgentServerHost owns /invocations_ws; use on_<event> decorators")

    def on_session_start(self, callback: SessionStartCallback) -> SessionStartCallback:
        """Register the ``session.start`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: SessionStartCallback
        :return: The callback, unchanged.
        :rtype: SessionStartCallback
        """
        return self._register_voice_callback(SessionStart.type, callback)

    def on_user_message(self, callback: UserMessageCallback) -> UserMessageCallback:
        """Register the ``user.message`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: UserMessageCallback
        :return: The callback, unchanged.
        :rtype: UserMessageCallback
        """
        return self._register_voice_callback(UserMessage.type, callback)

    def on_user_no_input(self, callback: UserNoInputCallback) -> UserNoInputCallback:
        """Register the ``user.no_input`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: UserNoInputCallback
        :return: The callback, unchanged.
        :rtype: UserNoInputCallback
        """
        return self._register_voice_callback(UserNoInput.type, callback)

    def on_user_speech_started(self, callback: UserSpeechStartedCallback) -> UserSpeechStartedCallback:
        """Register the ``user.speech_started`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: UserSpeechStartedCallback
        :return: The callback, unchanged.
        :rtype: UserSpeechStartedCallback
        """
        return self._register_voice_callback(UserSpeechStarted.type, callback)

    def on_barge_in(self, callback: BargeInCallback) -> BargeInCallback:
        """Register the ``barge_in`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: BargeInCallback
        :return: The callback, unchanged.
        :rtype: BargeInCallback
        """
        return self._register_voice_callback(BargeIn.type, callback)

    def on_response_accepted(self, callback: ResponseAcceptedCallback) -> ResponseAcceptedCallback:
        """Register the ``response.accepted`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: ResponseAcceptedCallback
        :return: The callback, unchanged.
        :rtype: ResponseAcceptedCallback
        """
        return self._register_voice_callback(ResponseAccepted.type, callback)

    def on_response_dropped(self, callback: ResponseDroppedCallback) -> ResponseDroppedCallback:
        """Register the ``response.dropped`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: ResponseDroppedCallback
        :return: The callback, unchanged.
        :rtype: ResponseDroppedCallback
        """
        return self._register_voice_callback(ResponseDropped.type, callback)

    def on_response_cancelled(self, callback: ResponseCancelledCallback) -> ResponseCancelledCallback:
        """Register the ``response.cancelled`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: ResponseCancelledCallback
        :return: The callback, unchanged.
        :rtype: ResponseCancelledCallback
        """
        return self._register_voice_callback(ResponseCancelled.type, callback)

    def on_response_timeout(self, callback: ResponseTimeoutCallback) -> ResponseTimeoutCallback:
        """Register the ``response.timeout`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: ResponseTimeoutCallback
        :return: The callback, unchanged.
        :rtype: ResponseTimeoutCallback
        """
        return self._register_voice_callback(ResponseTimeout.type, callback)

    def on_session_end(self, callback: SessionEndCallback) -> SessionEndCallback:
        """Register the ``session.end`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: SessionEndCallback
        :return: The callback, unchanged.
        :rtype: SessionEndCallback
        """
        return self._register_voice_callback(SessionEnd.type, callback)

    def on_disconnect(self, callback: DisconnectCallback) -> DisconnectCallback:
        """Register the local transport-disconnect callback.

        :param callback: Async callback receiving the thin Session and transport event.
        :type callback: DisconnectCallback
        :return: The callback, unchanged.
        :rtype: DisconnectCallback
        """
        return self._register_voice_callback("disconnect", callback)

    def _register_voice_callback(self, message_type: str, callback: _CallbackT) -> _CallbackT:
        if not inspect.iscoroutinefunction(callback):
            raise TypeError(f"on_{message_type.replace('.', '_')} expects an async function")
        try:
            inspect.signature(callback).bind(None, None)
        except TypeError as exc:
            raise TypeError("Voice callbacks must accept Session and event positional arguments") from exc
        if message_type in self._voice_callbacks:
            raise RuntimeError(f"A callback is already registered for {message_type}")
        self._voice_callbacks[message_type] = cast(_VoiceCallback, callback)
        return cast(_CallbackT, callback)

    async def _handle_voice_connection(self, websocket: WebSocket) -> None:
        session = Session._create(websocket)  # pylint: disable=protected-access
        while True:
            raw_message = await websocket.receive()
            raw_type = raw_message.get("type")
            if raw_type == "websocket.disconnect":
                code = int(raw_message.get("code") or 1000)
                raw_reason = raw_message.get("reason")
                reason = raw_reason if isinstance(raw_reason, str) else None
                callback = self._voice_callbacks.get("disconnect")
                if callback is not None:
                    await callback(session, SessionDisconnected(code=code, reason=reason))
                raise WebSocketDisconnect(
                    code=code,
                    reason=reason,
                )
            if raw_type != "websocket.receive":
                await websocket.close(code=1002, reason="Invalid Voice WebSocket event")
                return
            frame = raw_message.get("text")
            if frame is None:
                await websocket.close(code=1003, reason="Voice messages must be text frames")
                return
            try:
                event = decode_inbound_message(frame)
            except VoiceProtocolError as exc:
                await websocket.close(code=exc.close_code, reason="Invalid Voice message")
                return
            if event is None:
                continue
            callback = self._voice_callbacks.get(event.type)
            if callback is not None:
                await callback(session, cast(InboundVoiceMessage, event))

    def _build_hypercorn_config(self, host: str, port: int) -> object:
        """Create a Hypercorn config with the Voice frame admission limit.

        :param host: Network interface to bind.
        :type host: str
        :param port: Port to bind.
        :type port: int
        :return: Configured Hypercorn config.
        :rtype: hypercorn.config.Config
        """
        config = super()._build_hypercorn_config(host, port)
        setattr(config, "websocket_max_message_size", MAX_FRAME_BYTES)
        return config
