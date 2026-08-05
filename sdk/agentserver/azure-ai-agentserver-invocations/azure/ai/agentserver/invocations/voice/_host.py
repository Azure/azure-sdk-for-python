# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Typed Voice Live bridge host built on the invocations_ws transport."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import hashlib
import inspect
import logging
import threading
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Coroutine, Mapping, Sequence
from dataclasses import dataclass
from dataclasses import fields as dataclass_fields, is_dataclass, replace
from typing import Any, Optional

from opentelemetry import metrics
from starlette.routing import WebSocketRoute

from azure.ai.agentserver.core import experimental

from .._constants import InvocationsWSConstants
from .._invocation import InvocationAgentServerHost
from .._version import VERSION

from ._models import (
    BargeInEvent,
    ConversationItemCreateEvent,
    ConversationItemDeleteEvent,
    DtmfCollectedEvent,
    DtmfCollectionCancelledEvent,
    DtmfCollectionRejectedEvent,
    DtmfKeyEvent,
    HandoffFailedEvent,
    ResponseCancellationOutcome,
    ResponseTimeoutEvent,
    SessionEndEvent,
    SessionStartEvent,
    UserMessageEvent,
    UserNoInputEvent,
    UserSpeechStartedEvent,
)
from ._protocol import (
    PROTOCOL_VERSION,
    VoiceBridgeConnectionClosedError,
    VoiceBridgeProtocolError,
    VoiceProactiveResponseDroppedError,
    canonical_payload,
    decode_frame,
    encode_frame,
    new_id,
    optional_string,
    parse_conversation_item_create,
    parse_conversation_item_delete,
    parse_dtmf,
    parse_dtmf_collection_cancelled,
    parse_dtmf_collection_rejected,
    parse_handoff_failed,
    parse_response_timeout,
    parse_session_start,
    parse_user_message,
    require_positive_int,
    require_prefixed_id,
    require_string,
    safe_code,
)
from ._runtime import VoiceResponse, VoiceSession

logger = logging.getLogger("azure.ai.agentserver")
_METER = metrics.get_meter("Azure.AI.AgentServer.Invocations.Voice", VERSION)
_ACTIVATION_COUNTER = _METER.create_counter("azure.ai.agentserver.invocations.voice.activations")
_CALLBACK_DURATION = _METER.create_histogram(
    "azure.ai.agentserver.invocations.voice.callback.duration",
    unit="ms",
)
_CALLBACK_ERROR_COUNTER = _METER.create_counter("azure.ai.agentserver.invocations.voice.callback.errors")
_FIRST_OUTPUT_DURATION = _METER.create_histogram(
    "azure.ai.agentserver.invocations.voice.first_output.duration",
    unit="ms",
)
_TERMINAL_COUNTER = _METER.create_counter("azure.ai.agentserver.invocations.voice.response.terminals")
_PROTOCOL_VIOLATION_COUNTER = _METER.create_counter("azure.ai.agentserver.invocations.voice.protocol.violations")
_ACTIVE_CONNECTIONS = _METER.create_up_down_counter("azure.ai.agentserver.invocations.voice.active_connections")
_CLOSE_CODE_COUNTER = _METER.create_counter("azure.ai.agentserver.invocations.voice.close_codes")

# VoiceResponse and _VoiceConnection are the public/internal halves of one
# runtime and intentionally drive each other's private terminal hooks.
# pylint: disable=protected-access

SessionStartCallback = Callable[[VoiceSession, SessionStartEvent], Awaitable[None]]
UserMessageCallback = Callable[[VoiceSession, UserMessageEvent, VoiceResponse], Awaitable[None]]
UserNoInputCallback = Callable[[VoiceSession, UserNoInputEvent, VoiceResponse], Awaitable[None]]
UserSpeechStartedCallback = Callable[[VoiceSession, UserSpeechStartedEvent], Awaitable[None]]
DtmfKeyCallback = Callable[[VoiceSession, DtmfKeyEvent], Awaitable[None]]
DtmfCollectedCallback = Callable[[VoiceSession, DtmfCollectedEvent, VoiceResponse], Awaitable[None]]
DtmfCollectionRejectedCallback = Callable[[VoiceSession, DtmfCollectionRejectedEvent], Awaitable[None]]
DtmfCollectionCancelledCallback = Callable[[VoiceSession, DtmfCollectionCancelledEvent], Awaitable[None]]
HandoffFailedCallback = Callable[[VoiceSession, HandoffFailedEvent, VoiceResponse], Awaitable[None]]
ConversationItemCreateCallback = Callable[[VoiceSession, ConversationItemCreateEvent], Awaitable[None]]
ConversationItemDeleteCallback = Callable[[VoiceSession, ConversationItemDeleteEvent], Awaitable[None]]
BargeInCallback = Callable[[VoiceSession, BargeInEvent], Awaitable[None]]
ResponseTimeoutCallback = Callable[[VoiceSession, ResponseTimeoutEvent], Awaitable[None]]
SessionEndCallback = Callable[[VoiceSession, SessionEndEvent], Awaitable[None]]

_MAX_CALLBACK_QUEUE = 128
_MAX_CALLBACK_QUEUE_BYTES = 8 * 1024 * 1024
_MAX_FRAME_BYTES = 1024 * 1024
_MAX_SEEN_MESSAGES = 4096
_MAX_RECENT_RESPONSES = 64
_MAX_RESOLVED_PREFIXES = 64
_MAX_PENDING_PROACTIVE = 16
# Upper bound on customer tasks that were cancelled but keep running because the
# callback swallowed CancelledError. They are retained (tracked) until they
# actually complete; this cap makes a hostile or broken callback unable to
# accumulate such tasks without limit.
_MAX_RESISTANT_TASKS = 64
_MAX_GLOBAL_CUSTOMER_TASKS = 1024
_CLEANUP_TIMEOUT_SECONDS = 5.0
_GLOBAL_CUSTOMER_TASKS: set[asyncio.Task[None]] = set()
_GLOBAL_CUSTOMER_TASKS_LOCK = threading.Lock()
_GLOBAL_CUSTOMER_TASK_RESERVATIONS = 0
_AGENT_TO_BRIDGE_TYPES = {
    "session.ready",
    "session.rejected",
    "conversation.item.created",
    "conversation.item.deleted",
    "conversation.item.failed",
    "response.created",
    "response.none",
    "response.output_text.delta",
    "response.output_text.done",
    "response.done",
    "response.cancel",
    "handoff",
    "end_call",
    "dtmf.collect",
    "dtmf.collect.cancel",
    "error",
}


def _release_global_customer_task(completed: asyncio.Task[None]) -> None:
    """Release one process-level customer/finalizer task reservation.

    :param completed: Completed tracked task.
    :type completed: asyncio.Task[None]
    """
    global _GLOBAL_CUSTOMER_TASK_RESERVATIONS  # pylint: disable=global-statement
    with _GLOBAL_CUSTOMER_TASKS_LOCK:
        if completed not in _GLOBAL_CUSTOMER_TASKS:
            return
        _GLOBAL_CUSTOMER_TASKS.discard(completed)
        _GLOBAL_CUSTOMER_TASK_RESERVATIONS -= 1
    if not completed.cancelled():
        completed.exception()


@dataclass(frozen=True)
class _CallbackWork:
    kind: str
    event: Any
    callback: Callable[..., Awaitable[None]] | None
    response: VoiceResponse | None = None
    item_id: str | None = None
    request_id: str | None = None
    success_type: str | None = None
    payload_bytes: int = 0


@experimental
class VoiceAgentServerHost(InvocationAgentServerHost):  # pylint: disable=too-many-instance-attributes
    """AgentServer host implementing Voice Live Bridge Protocol 1.0."""

    def __init__(self, **kwargs: Any) -> None:
        self._on_session_start: Optional[SessionStartCallback] = None
        self._on_user_message: Optional[UserMessageCallback] = None
        self._on_user_no_input: Optional[UserNoInputCallback] = None
        self._on_user_speech_started: Optional[UserSpeechStartedCallback] = None
        self._on_dtmf_key: Optional[DtmfKeyCallback] = None
        self._on_dtmf_collected: Optional[DtmfCollectedCallback] = None
        self._on_dtmf_collection_rejected: Optional[DtmfCollectionRejectedCallback] = None
        self._on_dtmf_collection_cancelled: Optional[DtmfCollectionCancelledCallback] = None
        self._on_handoff_failed: Optional[HandoffFailedCallback] = None
        self._on_conversation_item_create: Optional[ConversationItemCreateCallback] = None
        self._on_conversation_item_delete: Optional[ConversationItemDeleteCallback] = None
        self._on_barge_in: Optional[BargeInCallback] = None
        self._on_response_timeout: Optional[ResponseTimeoutCallback] = None
        self._on_session_end: Optional[SessionEndCallback] = None
        super().__init__(**kwargs)
        InvocationAgentServerHost.ws_handler(self, self._handle_voice_websocket)
        voice_route = next(
            (
                route
                for route in self.router.routes
                if isinstance(route, WebSocketRoute)
                and getattr(route, "path", None) == InvocationsWSConstants.ROUTE_PATH
            ),
            None,
        )
        if voice_route is None or getattr(getattr(voice_route, "endpoint", None), "__self__", None) is not self:
            raise RuntimeError(
                "VoiceAgentServerHost cannot own /invocations_ws because the route is already registered"
            )

    def _build_hypercorn_config(self, host: str, port: int) -> object:
        config = super()._build_hypercorn_config(host, port)
        setattr(config, "websocket_max_message_size", _MAX_FRAME_BYTES)
        return config

    def ws_handler(self, fn: Any) -> Any:
        """Reject raw handler replacement on the typed host.

        :param fn: Raw handler that cannot be registered.
        :type fn: Any
        :raises RuntimeError: Always.
        """
        del fn
        raise RuntimeError(
            "VoiceAgentServerHost owns /invocations_ws. "
            "Use typed voice callbacks, or InvocationAgentServerHost for a custom protocol."
        )

    def on_session_start(self, fn: SessionStartCallback) -> SessionStartCallback:
        """Register the optional application-start callback.

        :param fn: Async callback invoked before readiness.
        :type fn: Callable[[VoiceSession, SessionStartEvent], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, SessionStartEvent], Awaitable[None]]
        """
        self._on_session_start = self._register_once("on_session_start", self._on_session_start, fn)
        return fn

    def on_user_message(self, fn: UserMessageCallback) -> UserMessageCallback:
        """Register the required completed-user-turn callback.

        :param fn: Async callback receiving ordered content and a lazy response.
        :type fn: Callable[[VoiceSession, UserMessageEvent, VoiceResponse], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, UserMessageEvent, VoiceResponse], Awaitable[None]]
        """
        self._on_user_message = self._register_once("on_user_message", self._on_user_message, fn)
        return fn

    def on_user_no_input(self, fn: UserNoInputCallback) -> UserNoInputCallback:
        """Register the optional bridge-generated silence-turn callback.

        :param fn: Async no-input callback.
        :type fn: Callable[[VoiceSession, UserNoInputEvent, VoiceResponse], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, UserNoInputEvent, VoiceResponse], Awaitable[None]]
        """
        self._on_user_no_input = self._register_once("on_user_no_input", self._on_user_no_input, fn)
        return fn

    def on_user_speech_started(self, fn: UserSpeechStartedCallback) -> UserSpeechStartedCallback:
        """Register the optional advisory speech-start callback.

        :param fn: Async advisory callback.
        :type fn: Callable[[VoiceSession, UserSpeechStartedEvent], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, UserSpeechStartedEvent], Awaitable[None]]
        """
        self._on_user_speech_started = self._register_once("on_user_speech_started", self._on_user_speech_started, fn)
        return fn

    def on_dtmf_key(self, fn: DtmfKeyCallback) -> DtmfKeyCallback:
        """Register the optional raw DTMF key callback.

        :param fn: Async session-signal callback.
        :type fn: Callable[[VoiceSession, DtmfKeyEvent], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, DtmfKeyEvent], Awaitable[None]]
        """
        self._on_dtmf_key = self._register_once("on_dtmf_key", self._on_dtmf_key, fn)
        return fn

    def on_dtmf_collected(self, fn: DtmfCollectedCallback) -> DtmfCollectedCallback:
        """Register the optional completed DTMF collection turn callback.

        :param fn: Async response-producing callback.
        :type fn: Callable[[VoiceSession, DtmfCollectedEvent, VoiceResponse], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, DtmfCollectedEvent, VoiceResponse], Awaitable[None]]
        """
        self._on_dtmf_collected = self._register_once("on_dtmf_collected", self._on_dtmf_collected, fn)
        return fn

    def on_dtmf_collection_rejected(self, fn: DtmfCollectionRejectedCallback) -> DtmfCollectionRejectedCallback:
        """Register the optional DTMF collection rejection callback.

        :param fn: Async collection-control callback.
        :type fn: Callable[[VoiceSession, DtmfCollectionRejectedEvent], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, DtmfCollectionRejectedEvent], Awaitable[None]]
        """
        self._on_dtmf_collection_rejected = self._register_once(
            "on_dtmf_collection_rejected", self._on_dtmf_collection_rejected, fn
        )
        return fn

    def on_dtmf_collection_cancelled(self, fn: DtmfCollectionCancelledCallback) -> DtmfCollectionCancelledCallback:
        """Register the optional DTMF collection cancellation callback.

        :param fn: Async collection-control callback.
        :type fn: Callable[[VoiceSession, DtmfCollectionCancelledEvent], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, DtmfCollectionCancelledEvent], Awaitable[None]]
        """
        self._on_dtmf_collection_cancelled = self._register_once(
            "on_dtmf_collection_cancelled", self._on_dtmf_collection_cancelled, fn
        )
        return fn

    def on_handoff_failed(self, fn: HandoffFailedCallback) -> HandoffFailedCallback:
        """Register the optional handoff recovery-turn callback.

        :param fn: Async response-producing recovery callback.
        :type fn: Callable[[VoiceSession, HandoffFailedEvent, VoiceResponse], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, HandoffFailedEvent, VoiceResponse], Awaitable[None]]
        """
        self._on_handoff_failed = self._register_once("on_handoff_failed", self._on_handoff_failed, fn)
        return fn

    def on_conversation_item_create(self, fn: ConversationItemCreateCallback) -> ConversationItemCreateCallback:
        """Register the optional durable history-create callback.

        :param fn: Async history mutation callback.
        :type fn: Callable[[VoiceSession, ConversationItemCreateEvent], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, ConversationItemCreateEvent], Awaitable[None]]
        """
        self._on_conversation_item_create = self._register_once(
            "on_conversation_item_create", self._on_conversation_item_create, fn
        )
        return fn

    def on_conversation_item_delete(self, fn: ConversationItemDeleteCallback) -> ConversationItemDeleteCallback:
        """Register the optional durable history-delete callback.

        :param fn: Async history mutation callback.
        :type fn: Callable[[VoiceSession, ConversationItemDeleteEvent], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, ConversationItemDeleteEvent], Awaitable[None]]
        """
        self._on_conversation_item_delete = self._register_once(
            "on_conversation_item_delete", self._on_conversation_item_delete, fn
        )
        return fn

    def on_barge_in(self, fn: BargeInCallback) -> BargeInCallback:
        """Register the optional caller-interruption callback.

        :param fn: Async callback invoked after response cancellation.
        :type fn: Callable[[VoiceSession, BargeInEvent], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, BargeInEvent], Awaitable[None]]
        """
        self._on_barge_in = self._register_once("on_barge_in", self._on_barge_in, fn)
        return fn

    def on_response_timeout(self, fn: ResponseTimeoutCallback) -> ResponseTimeoutCallback:
        """Register the optional response-timeout callback.

        :param fn: Async callback invoked after local work is tombstoned.
        :type fn: Callable[[VoiceSession, ResponseTimeoutEvent], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, ResponseTimeoutEvent], Awaitable[None]]
        """
        self._on_response_timeout = self._register_once("on_response_timeout", self._on_response_timeout, fn)
        return fn

    def on_session_end(self, fn: SessionEndCallback) -> SessionEndCallback:
        """Register the optional session-end callback.

        :param fn: Async callback invoked during bounded teardown.
        :type fn: Callable[[VoiceSession, SessionEndEvent], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, SessionEndEvent], Awaitable[None]]
        """
        self._on_session_end = self._register_once("on_session_end", self._on_session_end, fn)
        return fn

    @staticmethod
    def _register_once(name: str, current: Any, fn: Any) -> Any:
        if current is not None:
            raise RuntimeError(f"{name} callback is already registered")
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(f"{name} expects an async function")
        return fn

    async def _handle_voice_websocket(self, websocket: Any) -> None:
        connection = _VoiceConnection(
            websocket=websocket,
            on_session_start=self._on_session_start,
            on_user_message=self._on_user_message,
            on_user_no_input=self._on_user_no_input,
            on_user_speech_started=self._on_user_speech_started,
            on_dtmf_key=self._on_dtmf_key,
            on_dtmf_collected=self._on_dtmf_collected,
            on_dtmf_collection_rejected=self._on_dtmf_collection_rejected,
            on_dtmf_collection_cancelled=self._on_dtmf_collection_cancelled,
            on_handoff_failed=self._on_handoff_failed,
            on_conversation_item_create=self._on_conversation_item_create,
            on_conversation_item_delete=self._on_conversation_item_delete,
            on_barge_in=self._on_barge_in,
            on_response_timeout=self._on_response_timeout,
            on_session_end=self._on_session_end,
        )
        _ACTIVE_CONNECTIONS.add(1)
        try:
            await connection.run()
        finally:
            _ACTIVE_CONNECTIONS.add(-1)


class _VoiceConnection:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """Per-WebSocket protocol runtime."""

    def __init__(  # pylint: disable=too-many-statements
        self,
        *,
        websocket: Any,
        on_session_start: Optional[SessionStartCallback],
        on_user_message: Optional[UserMessageCallback],
        on_user_no_input: Optional[UserNoInputCallback],
        on_user_speech_started: Optional[UserSpeechStartedCallback],
        on_dtmf_key: Optional[DtmfKeyCallback],
        on_dtmf_collected: Optional[DtmfCollectedCallback],
        on_dtmf_collection_rejected: Optional[DtmfCollectionRejectedCallback],
        on_dtmf_collection_cancelled: Optional[DtmfCollectionCancelledCallback],
        on_handoff_failed: Optional[HandoffFailedCallback],
        on_conversation_item_create: Optional[ConversationItemCreateCallback],
        on_conversation_item_delete: Optional[ConversationItemDeleteCallback],
        on_barge_in: Optional[BargeInCallback],
        on_response_timeout: Optional[ResponseTimeoutCallback],
        on_session_end: Optional[SessionEndCallback],
    ) -> None:
        self._websocket = websocket
        self._on_session_start = on_session_start
        self._on_user_message = on_user_message
        self._on_user_no_input = on_user_no_input
        self._on_user_speech_started = on_user_speech_started
        self._on_dtmf_key = on_dtmf_key
        self._on_dtmf_collected = on_dtmf_collected
        self._on_dtmf_collection_rejected = on_dtmf_collection_rejected
        self._on_dtmf_collection_cancelled = on_dtmf_collection_cancelled
        self._on_handoff_failed = on_handoff_failed
        self._on_conversation_item_create = on_conversation_item_create
        self._on_conversation_item_delete = on_conversation_item_delete
        self._on_barge_in = on_barge_in
        self._on_response_timeout = on_response_timeout
        self._on_session_end = on_session_end
        self._send_lock = asyncio.Lock()
        self._state_lock = asyncio.Lock()
        self._callback_queue: asyncio.Queue[_CallbackWork | None] = asyncio.Queue(maxsize=_MAX_CALLBACK_QUEUE)
        self._callback_queue_bytes = 0
        self._callback_worker: asyncio.Task[None] | None = None
        self._active_customer_task: asyncio.Task[None] | None = None
        self._active_release: asyncio.Event | None = None
        self._cleanup_tasks: set[asyncio.Task[None]] = set()
        # Underlying customer tasks that were cancelled but may outlive their
        # bounded cleanup wrapper (they swallowed CancelledError). Tracked here
        # until they actually finish so they are never left running untracked.
        self._resistant_tasks: set[asyncio.Task[None]] = set()
        # One-shot fatal signal observed alongside the receive pump and callback
        # worker. This is a successful Future[None], rather than a future carrying
        # an exception, so activation ending before supervision cannot produce an
        # un-retrieved-future warning.
        self._resource_limit_reached: asyncio.Future[None] = asyncio.get_running_loop().create_future()
        # Dedicated task for the on_session_end callback so session teardown does
        # not sit behind possibly-stalled ordinary callback work in the queue.
        self._session_end_task: asyncio.Task[None] | None = None
        self._session: VoiceSession | None = None
        self._active_response: VoiceResponse | None = None
        self._pending_turns: OrderedDict[str, VoiceResponse] = OrderedDict()
        self._resolved_input_prefixes: OrderedDict[tuple[str, ...], tuple[VoiceResponse, bool]] = OrderedDict()
        self._recent_responses: OrderedDict[str, VoiceResponse] = OrderedDict()
        self._seen_response_ids: set[str] = set()
        self._terminal_response_ids: set[str] = set()
        self._seen_messages: OrderedDict[str, str] = OrderedDict()
        self._seen_input_ids: set[str] = set()
        self._playback_outcomes: set[str] = set()
        self._abandoned_proactive_cancels: set[str] = set()
        self._cancel_waiters: dict[str, asyncio.Future[ResponseCancellationOutcome]] = {}
        self._pending_proactive: OrderedDict[
            str,
            tuple[VoiceResponse, asyncio.Future[tuple[bool, str]]],
        ] = OrderedDict()
        self._dtmf_collections: dict[str, str] = {}
        self._dtmf_cancel_pending: set[str] = set()
        self._recent_dtmf_cancel_races: OrderedDict[str, None] = OrderedDict()
        self._response_start_ns: dict[str, int] = {}
        self._first_output_recorded: set[str] = set()
        self._activation_recorded = False
        self._close_recorded = False
        self._ready = False
        self._closed = False
        self._ending = False
        self._prefetched_receive_task: asyncio.Task[dict[str, Any] | None] | None = None

    @property
    def ending(self) -> bool:
        return self._ending or self._closed

    async def run(self) -> None:
        """Activate the protocol and run the sole receive pump."""
        graceful_end = False
        try:
            if not await self._activate():
                return
            while not self._closed:
                payload = await self._receive_with_worker_supervision()
                if payload is None:
                    break
                if not await self._dispatch(payload):
                    graceful_end = True
                    break
        except VoiceBridgeProtocolError as exc:
            _PROTOCOL_VIOLATION_COUNTER.add(1, {"close_code": exc.close_code})
            logger.warning("Voice bridge protocol violation: %s", exc)
            await self._close(code=exc.close_code, reason="Protocol error")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Voice bridge runtime failed: %s", type(exc).__name__)
            await self._close(code=1011, reason="Internal server error")
        finally:
            await self._shutdown_runtime(drain_callbacks=graceful_end)

    async def _receive_with_worker_supervision(self) -> dict[str, Any] | None:
        worker = self._callback_worker
        assert worker is not None
        receive_task = self._prefetched_receive_task
        self._prefetched_receive_task = None
        if receive_task is None:
            receive_task = asyncio.create_task(
                self._receive_payload(),
                name="voice_receive",
            )
        try:
            done, _ = await asyncio.wait(
                (receive_task, worker, self._resource_limit_reached),
                return_when=asyncio.FIRST_COMPLETED,
            )
        except BaseException:
            receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            raise
        if self._resource_limit_reached in done:
            receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            raise RuntimeError("Voice cancellation-resistant task limit reached")
        if worker in done:
            receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            if worker.cancelled():
                raise RuntimeError("Voice callback coordinator was cancelled unexpectedly")
            error = worker.exception()
            if error is not None:
                raise error
            raise RuntimeError("Voice callback coordinator stopped unexpectedly")
        return receive_task.result()

    async def send(self, message_type: str, **fields: Any) -> None:
        """Serialize one SDK-owned application frame.

        :param message_type: Wire message discriminator.
        :type message_type: str
        """
        if self._closed:
            raise VoiceBridgeConnectionClosedError("The voice connection is closed")
        async with self._send_lock:
            if self._closed:
                raise VoiceBridgeConnectionClosedError("The voice connection is closed")
            response_id = fields.get("response_id")
            if isinstance(response_id, str):
                async with self._state_lock:
                    if response_id in self._terminal_response_ids:
                        raise VoiceBridgeConnectionClosedError("The voice response is terminal")
            # Perform the WebSocket write OUTSIDE _state_lock. Holding the state
            # lock across a send that stalls on outbound backpressure would block
            # the receive pump from acquiring _state_lock to process barge_in,
            # response.timeout, or session termination — defeating the full-duplex
            # cancellation path. _send_lock still serializes writes; the terminal
            # check above rejects the common case, and the bridge drops any single
            # frame that races past a terminal it has already recorded.
            if _estimate_event_bytes(fields) > _MAX_FRAME_BYTES:
                raise ValueError("Voice bridge fields exceed the maximum encoded size")
            frame = encode_frame(message_type, **fields)
            if len(frame.encode("utf-8")) > _MAX_FRAME_BYTES:
                raise ValueError("Voice bridge frame exceeds the maximum encoded size")
            try:
                await self._websocket.send_text(frame)
            except BaseException:
                # Any transport exception is past an ambiguous commit boundary:
                # the ASGI server may already have accepted the frame even though
                # the caller did not observe success. Never roll protocol state
                # back and continue using this connection.
                self._signal_runtime_failure("Voice WebSocket send failed")
                raise
            self._record_first_output(message_type, fields)

    def _remember_resolved_prefix_locked(self, prefix: tuple[str, ...], value: tuple[VoiceResponse, bool]) -> None:
        # Bounded LRU: these entries only reconcile a late response.timeout that
        # references a prefix the SDK already resolved before the bridge saw the
        # response.created — a single-round-trip window. Retaining every resolved
        # prefix (each holding a full VoiceResponse with accumulated output text)
        # for the life of the call would grow without bound; cap it and evict the
        # oldest, since a timeout arriving that far out of order is stale.
        self._resolved_input_prefixes.pop(prefix, None)
        self._resolved_input_prefixes[prefix] = value
        while len(self._resolved_input_prefixes) > _MAX_RESOLVED_PREFIXES:
            self._resolved_input_prefixes.popitem(last=False)

    async def open_response(self, response_id: str, in_reply_to: tuple[str, ...] | None) -> bool:
        """Consume one explicit input prefix and announce a reply response.

        :param response_id: SDK-allocated response identifier.
        :type response_id: str
        :param in_reply_to: Non-empty ordered input prefix.
        :type in_reply_to: tuple[str, ...] or None
        :return: ``False`` when a bridge terminal already won; otherwise ``True``.
        :rtype: bool
        """
        self._ensure_ready()
        if not in_reply_to:
            raise RuntimeError("Reply response requires a non-empty in_reply_to prefix")
        async with self._state_lock:
            if response_id in self._terminal_response_ids:
                return False
            active = self._active_response
            if active is None or active.response_id != response_id:
                raise VoiceBridgeConnectionClosedError("The response is no longer active")
            pending_ids = tuple(self._pending_turns)
            if pending_ids[: len(in_reply_to)] != in_reply_to:
                raise RuntimeError("in_reply_to must be an ordered prefix of pending inputs")
            self._remember_resolved_prefix_locked(in_reply_to, (active, True))
            for item_id in in_reply_to:
                self._pending_turns.pop(item_id, None)
        await self.send(
            "response.created",
            response_id=response_id,
            in_reply_to=list(in_reply_to),
        )
        return True

    async def decline_response(self, in_reply_to: tuple[str, ...], reason: str | None) -> None:
        """Consume one explicit input prefix without opening a response.

        :param in_reply_to: Non-empty ordered input prefix.
        :type in_reply_to: tuple[str, ...]
        :param reason: Optional open-enum decline reason.
        :type reason: str or None
        """
        self._ensure_ready()
        response_id: str | None = None
        async with self._state_lock:
            active = self._active_response
            if (
                active is not None
                and active.in_reply_to == in_reply_to
                and active.response_id in self._terminal_response_ids
            ):
                return
            pending_ids = tuple(self._pending_turns)
            if pending_ids[: len(in_reply_to)] != in_reply_to:
                raise RuntimeError("in_reply_to must be an ordered prefix of pending inputs")
            if in_reply_to:
                response_id = self._pending_turns[in_reply_to[0]].response_id
                self._remember_resolved_prefix_locked(in_reply_to, (self._pending_turns[in_reply_to[0]], False))
            for item_id in in_reply_to:
                self._pending_turns.pop(item_id, None)
        # Claim the terminal for this input prefix BEFORE emitting response.none.
        # response.none carries no response_id on the wire, so send()'s
        # response-scoped terminal check cannot guard it. Without claiming here, a
        # response.timeout processed by the receive pump while this send is
        # suspended (send lock or transport backpressure) would let response.none
        # reach the wire after the bridge terminal already won. Serializing the
        # claim with timeout arbitration ensures only the winning terminal is emitted.
        if response_id is not None:
            async with self._state_lock:
                if response_id in self._terminal_response_ids:
                    return
                self._terminal_response_ids.add(response_id)
        fields: dict[str, Any] = {"in_reply_to": list(in_reply_to)}
        if reason is not None:
            fields["reason"] = reason
        await self.send("response.none", **fields)
        if response_id is not None:
            self._record_first_output_for_response(response_id)
            self._record_terminal(response_id, "none")

    async def begin_cancel(self, response_id: str, reason: str | None) -> asyncio.Future[ResponseCancellationOutcome]:
        """Register cancellation arbitration before sending ``response.cancel``.

        :param response_id: Open response to cancel.
        :type response_id: str
        :param reason: Optional open-enum cancellation reason.
        :type reason: str or None
        :return: Future resolved by the winning playback terminal.
        :rtype: asyncio.Future[ResponseCancellationOutcome]
        """
        self._ensure_ready()
        async with self._state_lock:
            response = self._find_response_locked(response_id)
            if response is None or not response.is_wire_opened:
                raise VoiceBridgeConnectionClosedError("The response is not open")
            if response_id in self._cancel_waiters:
                raise RuntimeError("Response cancellation is already pending")
            future: asyncio.Future[ResponseCancellationOutcome] = asyncio.get_running_loop().create_future()
            self._cancel_waiters[response_id] = future
        fields: dict[str, Any] = {"response_id": response_id}
        if reason is not None:
            fields["reason"] = reason
        try:
            await self.send("response.cancel", **fields)
        except BaseException:
            async with self._state_lock:
                self._cancel_waiters.pop(response_id, None)
            raise
        return future

    async def response_completed(self, response_id: str, terminal_kind: str = "done") -> None:
        """Move a response into bounded playback-reconciliation state.

        :param response_id: Completed response identifier.
        :type response_id: str
        :param terminal_kind: Low-cardinality terminal classification.
        :type terminal_kind: str
        """
        async with self._state_lock:
            response = self._find_response_locked(response_id)
            if response is None:
                return
            local_terminal_won = response_id not in self._terminal_response_ids
            self._terminal_response_ids.add(response_id)
            self._remember_response_locked(response)
            if self._active_response is response:
                self._active_response = None
        if local_terminal_won:
            self._record_terminal(response_id, terminal_kind)

    async def register_dtmf_collection(
        self,
        *,
        response_id: str,
        collection_id: str,
        max_digits: int,
        terminator: str | None,
        initial_timeout_ms: int,
        inter_digit_timeout_ms: int,
    ) -> None:
        """Register and emit one response-scoped DTMF collection request.

        :keyword response_id: Open source response identifier.
        :paramtype response_id: str
        :keyword collection_id: SDK-allocated collection identifier.
        :paramtype collection_id: str
        :keyword max_digits: Positive maximum returned digit count.
        :paramtype max_digits: int
        :keyword terminator: Optional single DTMF terminator.
        :paramtype terminator: str or None
        :keyword initial_timeout_ms: Positive first-key timeout.
        :paramtype initial_timeout_ms: int
        :keyword inter_digit_timeout_ms: Positive inter-key timeout.
        :paramtype inter_digit_timeout_ms: int
        """
        self._ensure_ready()
        async with self._state_lock:
            if self._dtmf_collections:
                raise RuntimeError("Only one DTMF collection may be pending or active")
            response = self._find_response_locked(response_id)
            if response is None or response.is_terminal:
                raise VoiceBridgeConnectionClosedError("The source response is not open")
            self._dtmf_collections[collection_id] = response_id
        fields: dict[str, Any] = {
            "response_id": response_id,
            "collection_id": collection_id,
            "max_digits": max_digits,
            "initial_timeout_ms": initial_timeout_ms,
            "inter_digit_timeout_ms": inter_digit_timeout_ms,
        }
        if terminator is not None:
            fields["terminator"] = terminator
        try:
            await self.send("dtmf.collect", **fields)
        except BaseException:
            async with self._state_lock:
                self._dtmf_collections.pop(collection_id, None)
            raise

    async def cancel_dtmf_collection(self, collection_id: str) -> None:
        """Emit explicit cancellation for one known DTMF collection.

        :param collection_id: SDK-allocated collection identifier.
        :type collection_id: str
        """
        self._ensure_ready()
        async with self._state_lock:
            if collection_id not in self._dtmf_collections:
                raise RuntimeError("Unknown or completed DTMF collection_id")
            if collection_id in self._dtmf_cancel_pending:
                raise RuntimeError("DTMF collection cancellation is already pending")
            self._dtmf_cancel_pending.add(collection_id)
        try:
            await self.send("dtmf.collect.cancel", collection_id=collection_id)
        except BaseException:
            async with self._state_lock:
                self._dtmf_cancel_pending.discard(collection_id)
            raise

    async def end_call(self, reason: str, mode: str) -> None:
        """Emit one call terminal and seal active work.

        :param reason: Non-empty open-enum termination reason.
        :type reason: str
        :param mode: Closed ``drain`` or ``immediate`` mode.
        :type mode: str
        """
        self._ensure_ready()
        async with self._state_lock:
            if self._ending:
                return
            self._ending = True
            response = self._active_response
            if response is not None:
                self._terminal_response_ids.add(response.response_id)
            release = self._active_release
            active_task = self._active_customer_task
        await self.send("end_call", reason=reason, mode=mode)
        if response is not None:
            await response._mark_terminal()
            self._record_terminal(response.response_id, "end_call")
        if release is not None and active_task is not asyncio.current_task():
            release.set()

    async def start_proactive_response(
        self,
        *,
        admission_timeout_ms: int,
        supersede_key: str | None,
    ) -> VoiceResponse:
        """Request admission and return only after ``response.accepted``.

        :keyword admission_timeout_ms: Positive admission deadline.
        :paramtype admission_timeout_ms: int
        :keyword supersede_key: Optional non-empty supersession key.
        :paramtype supersede_key: str or None
        :return: Accepted proactive response.
        :rtype: VoiceResponse
        """
        self._ensure_ready()
        response = VoiceResponse._create(
            self,
            response_id=new_id("r"),
            in_reply_to=None,
            wire_opened=True,
            accepted=False,
        )
        future: asyncio.Future[tuple[bool, str]] = asyncio.get_running_loop().create_future()
        async with self._state_lock:
            if len(self._pending_proactive) >= _MAX_PENDING_PROACTIVE:
                raise RuntimeError("Too many proactive admission outcomes are pending")
            if response.response_id in self._seen_response_ids:
                raise RuntimeError("Generated proactive response_id was already used")
            self._seen_response_ids.add(response.response_id)
            self._pending_proactive[response.response_id] = (response, future)
        fields: dict[str, Any] = {
            "response_id": response.response_id,
            "admission_timeout_ms": admission_timeout_ms,
        }
        if supersede_key is not None:
            fields["supersede_key"] = supersede_key
        try:
            await self.send("response.created", **fields)
        except BaseException:
            async with self._state_lock:
                if self.ending:
                    # Keep the response identity until shutdown so a frame that
                    # crossed the ambiguous send boundary is never reused, but
                    # cancel the now-unobserved admission Future.
                    future.cancel()
                else:
                    self._pending_proactive.pop(response.response_id, None)
            raise
        try:
            accepted, reason = await future
        except asyncio.CancelledError:
            async with self._state_lock:
                self._abandoned_proactive_cancels.add(response.response_id)
            try:
                await self.send(
                    "response.cancel",
                    response_id=response.response_id,
                    reason="cancelled_by_agent",
                )
            except VoiceBridgeConnectionClosedError:
                pass
            raise
        if not accepted:
            await response._mark_terminal()
            raise VoiceProactiveResponseDroppedError(response.response_id, reason)
        return response

    async def report_session_error(self, code: str, message: str) -> None:
        """Emit a session-scoped terminal error.

        :param code: Bounded machine-readable code.
        :type code: str
        :param message: Bounded diagnostic message.
        :type message: str
        """
        self._ensure_ready()
        async with self._state_lock:
            if self._ending:
                return
            self._ending = True
            response = self._active_response
            if response is not None:
                self._terminal_response_ids.add(response.response_id)
            release = self._active_release
        await self.send("error", code=code, message=message)
        if response is not None:
            await response._mark_terminal()
            self._record_terminal(response.response_id, "session_error")
        if release is not None:
            release.set()

    async def _activate(self) -> bool:  # pylint: disable=too-many-return-statements
        try:
            payload = await self._receive_payload()
        except VoiceBridgeProtocolError as exc:
            await self._reject("invalid_session_start", close_code=exc.close_code)
            return False
        if payload is None:
            self._record_activation("closed")
            return False
        if payload.get("type") != "session.start":
            await self._reject("invalid_session_start", close_code=1002)
            return False
        try:
            event = parse_session_start(payload)
        except VoiceBridgeProtocolError:
            code = (
                "protocol_mismatch" if payload.get("protocol_version") != PROTOCOL_VERSION else "invalid_session_start"
            )
            await self._reject(code, close_code=1002)
            return False
        if self._on_user_message is None:
            await self._reject("startup_failed", close_code=1011)
            return False
        session = VoiceSession._create(self, event)
        self._session = session
        startup_started_ns = time.monotonic_ns()
        try:
            if not await self._run_session_start_callback(session, event):
                return False
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Voice session-start callback failed: %s", type(exc).__name__)
            _CALLBACK_ERROR_COUNTER.add(1, {"kind": "session.start"})
            await self._reject("startup_failed", close_code=1011)
            return False
        finally:
            if self._on_session_start is not None:
                _CALLBACK_DURATION.record(
                    (time.monotonic_ns() - startup_started_ns) / 1_000_000,
                    {"kind": "session.start"},
                )
        try:
            if not await self._send_ready_with_receive_gate():
                return False
        except VoiceBridgeProtocolError as exc:
            await self._reject("protocol_mismatch", close_code=exc.close_code)
            return False
        self._record_activation("ready")
        self._ready = True
        self._callback_worker = asyncio.create_task(self._callback_worker_loop(), name="voice_callback_coordinator")
        return True

    async def _send_ready_with_receive_gate(self) -> bool:
        """Send readiness while rejecting only an unambiguously early frame.

        :return: Whether activation may proceed.
        :rtype: bool
        """
        ready_send_started = False
        receive_completed_after_send_started = False

        async def _send_ready() -> None:
            nonlocal ready_send_started
            ready_send_started = True
            await self.send("session.ready")

        async def _receive_during_ready() -> dict[str, Any] | None:
            nonlocal receive_completed_after_send_started
            try:
                return await self._receive_payload()
            finally:
                # Captured in the receive task itself, before task completion
                # callbacks or the coordinator can reorder observations.
                receive_completed_after_send_started = ready_send_started

        async def _reject_early_receive() -> bool:
            try:
                early_payload = receive_task.result()
            except VoiceBridgeProtocolError:
                raise
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error("Voice readiness receive failed: %s", type(exc).__name__)
                self._record_activation("startup_failed")
                await self._close(code=1011, reason="Internal server error")
                return False
            if early_payload is None:
                self._record_activation("closed")
            else:
                await self._reject("protocol_mismatch", close_code=1008)
            return False

        receive_task = asyncio.create_task(_receive_during_ready(), name="voice_ready_receive")
        try:
            # Give the existing receive gate one event-loop turn to consume a
            # frame that was already queued before readiness was attempted.
            await asyncio.sleep(0)
        except BaseException:
            receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            raise
        if receive_task.done() and not receive_completed_after_send_started:
            return await _reject_early_receive()
        ready_task = asyncio.create_task(_send_ready(), name="voice_session_ready")
        try:
            done, _ = await asyncio.wait((ready_task, receive_task), return_when=asyncio.FIRST_COMPLETED)
        except BaseException:
            ready_task.cancel()
            receive_task.cancel()
            await asyncio.gather(ready_task, receive_task, return_exceptions=True)
            raise

        # A frame is provably early only when the receive coroutine completed
        # before the ready send attempt began. Once send starts, the peer may
        # receive ready and reply before the sender continuation resumes.
        if receive_task in done and not receive_completed_after_send_started:
            ready_task.cancel()
            await asyncio.gather(ready_task, return_exceptions=True)
            return await _reject_early_receive()

        try:
            await ready_task
        except BaseException:
            if not receive_task.done():
                receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            raise

        # Preserve the sole receive operation. Cancelling it here could consume
        # and drop a frame that arrived immediately after ready was committed.
        # The main loop adopts this task under normal worker supervision.
        self._prefetched_receive_task = receive_task
        return True

    async def _run_session_start_callback(self, session: VoiceSession, event: SessionStartEvent) -> bool:
        async def _invoke_customer_callback() -> None:
            if self._on_session_start is not None:
                await self._on_session_start(session, event)

        receive_task = asyncio.create_task(
            self._receive_payload(),
            name="voice_activation_receive",
        )
        try:
            customer_task = self._create_customer_task(
                _invoke_customer_callback(),
                name="voice_session_start",
            )
        except BaseException:
            receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            raise
        try:
            done, _ = await asyncio.wait((customer_task, receive_task), return_when=asyncio.FIRST_COMPLETED)
        except BaseException:
            receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            if not customer_task.done():
                self._schedule_customer_cleanup(customer_task)
            raise

        if receive_task in done:
            if not customer_task.done():
                self._schedule_customer_cleanup(customer_task)
            else:
                await asyncio.gather(customer_task, return_exceptions=True)
            try:
                early_payload = receive_task.result()
            except VoiceBridgeProtocolError as exc:
                await self._reject("protocol_mismatch", close_code=exc.close_code)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error("Voice activation receive failed: %s", type(exc).__name__)
                self._record_activation("startup_failed")
                await self._close(code=1011, reason="Internal server error")
            else:
                if early_payload is None:
                    self._record_activation("closed")
                else:
                    await self._reject("protocol_mismatch", close_code=1008)
            return False

        receive_task.cancel()
        await asyncio.gather(receive_task, return_exceptions=True)
        if customer_task.cancelled():
            raise RuntimeError("Voice session-start callback was cancelled")
        error = customer_task.exception()
        if error is not None:
            raise error
        return True

    async def _reject(self, code: str, *, close_code: int) -> None:
        if self._closed:
            return
        self._record_activation(code)
        if code in ("invalid_session_start", "protocol_mismatch"):
            _PROTOCOL_VIOLATION_COUNTER.add(1, {"close_code": close_code})
        try:
            await self.send(
                "session.rejected",
                code=safe_code(code, "startup_failed"),
                retriable=False,
            )
        finally:
            await self._close(code=close_code, reason="Session rejected")

    async def _dispatch(self, payload: dict[str, Any]) -> bool:  # pylint: disable=too-many-branches
        message_type = payload["type"]
        if message_type == "user.message":
            message_event = parse_user_message(payload)
            await self._enqueue_turn(
                message_event.item_id,
                message_event,
                self._on_user_message,
                "user.message",
            )
        elif message_type == "user.no_input":
            no_input_event = UserNoInputEvent(
                item_id=require_prefixed_id(payload, "item_id", "in_"),
                count=require_positive_int(payload, "count"),
            )
            await self._enqueue_turn(
                no_input_event.item_id,
                no_input_event,
                self._on_user_no_input,
                "user.no_input",
            )
        elif message_type == "user.speech_started":
            await self._enqueue_signal(UserSpeechStartedEvent(), self._on_user_speech_started, "user.speech_started")
        elif message_type == "conversation.item.create":
            create_event = parse_conversation_item_create(payload)
            self._enqueue_history(
                create_event,
                self._on_conversation_item_create,
                "conversation.item.create",
                "conversation.item.created",
            )
        elif message_type == "conversation.item.delete":
            delete_event = parse_conversation_item_delete(payload)
            self._enqueue_history(
                delete_event,
                self._on_conversation_item_delete,
                "conversation.item.delete",
                "conversation.item.deleted",
            )
        elif message_type == "dtmf":
            dtmf_event = parse_dtmf(payload)
            if isinstance(dtmf_event, DtmfKeyEvent):
                await self._enqueue_signal(dtmf_event, self._on_dtmf_key, "dtmf.key")
            else:
                await self._consume_dtmf_collection(
                    dtmf_event.collection_id,
                    preserve_cancel_race=True,
                )
                await self._enqueue_turn(
                    dtmf_event.item_id,
                    dtmf_event,
                    self._on_dtmf_collected,
                    "dtmf.collected",
                )
        elif message_type == "dtmf.collect.rejected":
            rejected_event = parse_dtmf_collection_rejected(payload)
            await self._consume_dtmf_collection(
                rejected_event.collection_id,
                allow_late_cancel_rejection=rejected_event.reason == "collection_not_found",
                preserve_cancel_race=rejected_event.reason != "collection_not_found",
            )
            await self._enqueue_signal(
                rejected_event,
                self._on_dtmf_collection_rejected,
                "dtmf.collect.rejected",
            )
        elif message_type == "dtmf.collect.cancelled":
            cancelled_event = parse_dtmf_collection_cancelled(payload)
            await self._consume_dtmf_collection(
                cancelled_event.collection_id,
                preserve_cancel_race=cancelled_event.reason != "cancelled_by_agent",
            )
            await self._enqueue_signal(
                cancelled_event,
                self._on_dtmf_collection_cancelled,
                "dtmf.collect.cancelled",
            )
        elif message_type == "handoff.failed":
            handoff_event = parse_handoff_failed(payload)
            await self._enqueue_turn(
                handoff_event.item_id,
                handoff_event,
                self._on_handoff_failed,
                "handoff.failed",
            )
        elif message_type == "barge_in":
            await self._handle_playback_terminal(payload, kind="barge_in")
        elif message_type == "response.cancelled":
            await self._handle_playback_terminal(payload, kind="cancelled")
        elif message_type == "response.timeout":
            await self._handle_response_timeout(parse_response_timeout(payload))
        elif message_type == "response.accepted":
            await self._handle_response_accepted(payload)
        elif message_type == "response.dropped":
            await self._handle_response_dropped(payload)
        elif message_type == "session.end":
            await self._handle_session_end(payload)
            return False
        else:
            if message_type == "session.start" or message_type in _AGENT_TO_BRIDGE_TYPES:
                raise VoiceBridgeProtocolError(
                    f"{message_type} is not valid from the bridge after readiness",
                    close_code=1008,
                )
            logger.debug("Ignoring unknown post-readiness voice message")
        return True

    async def _enqueue_turn(
        self,
        item_id: str,
        event: Any,
        callback: Callable[..., Awaitable[None]] | None,
        kind: str,
    ) -> None:
        response = VoiceResponse._create(self, in_reply_to=(item_id,))
        async with self._state_lock:
            if self._ending:
                raise VoiceBridgeProtocolError(f"{kind} arrived after session terminal", close_code=1008)
            item_key = hashlib.sha256(item_id.encode("utf-8")).hexdigest()
            if item_key in self._seen_input_ids:
                raise VoiceBridgeProtocolError("Input item_id was reused", close_code=1008)
            self._seen_input_ids.add(item_key)
            if response.response_id in self._seen_response_ids:
                raise RuntimeError("Generated response_id was already used")
            self._seen_response_ids.add(response.response_id)
            self._pending_turns[item_id] = response
            self._response_start_ns[response.response_id] = time.monotonic_ns()
        self._put_work(
            _CallbackWork(
                kind=kind,
                event=event,
                callback=callback,
                response=response,
                item_id=item_id,
                payload_bytes=_estimate_event_bytes(event),
            )
        )

    async def _enqueue_signal(
        self,
        event: Any,
        callback: Callable[..., Awaitable[None]] | None,
        kind: str,
    ) -> None:
        if callback is not None:
            self._put_work(_CallbackWork(kind=kind, event=event, callback=callback))

    def _enqueue_history(
        self,
        event: ConversationItemCreateEvent | ConversationItemDeleteEvent,
        callback: Callable[..., Awaitable[None]] | None,
        kind: str,
        success_type: str,
    ) -> None:
        self._put_work(
            _CallbackWork(
                kind=kind,
                event=event,
                callback=callback,
                request_id=event.request_id,
                success_type=success_type,
            )
        )

    async def _consume_dtmf_collection(
        self,
        collection_id: str,
        *,
        allow_late_cancel_rejection: bool = False,
        preserve_cancel_race: bool = False,
    ) -> None:
        async with self._state_lock:
            source_response_id = self._dtmf_collections.pop(collection_id, None)
            if source_response_id is None:
                if allow_late_cancel_rejection and collection_id in self._recent_dtmf_cancel_races:
                    self._recent_dtmf_cancel_races.pop(collection_id, None)
                    return
                raise VoiceBridgeProtocolError("Unknown DTMF collection_id", close_code=1008)
            cancel_pending = collection_id in self._dtmf_cancel_pending
            self._dtmf_cancel_pending.discard(collection_id)
            if cancel_pending and preserve_cancel_race:
                self._recent_dtmf_cancel_races[collection_id] = None
                while len(self._recent_dtmf_cancel_races) > _MAX_RECENT_RESPONSES:
                    self._recent_dtmf_cancel_races.popitem(last=False)

    def _put_work(self, work: _CallbackWork) -> None:
        if work.payload_bytes == 0:
            work = replace(work, payload_bytes=_estimate_event_bytes(work.event))
        if self._callback_queue_bytes + work.payload_bytes > _MAX_CALLBACK_QUEUE_BYTES:
            raise VoiceBridgeProtocolError("Voice callback queue byte limit exceeded", close_code=1008)
        try:
            self._callback_queue.put_nowait(work)
        except asyncio.QueueFull as exc:
            raise VoiceBridgeProtocolError("Voice callback queue limit exceeded", close_code=1008) from exc
        self._callback_queue_bytes += work.payload_bytes

    def _discard_callback_queue(self) -> None:
        """Release callback work that will never be dispatched."""
        while True:
            try:
                work = self._callback_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            if work is not None:
                self._callback_queue_bytes -= work.payload_bytes
            self._callback_queue.task_done()

    async def _callback_worker_loop(self) -> None:
        while True:
            work = await self._callback_queue.get()
            try:
                if work is None:
                    return
                if self._resource_limit_reached.done():
                    # Defensive backstop for work already queued when the fatal
                    # signal won: never dispatch another customer callback.
                    raise RuntimeError("Voice cancellation-resistant task limit reached")
                if work.response is not None:
                    await self._process_turn_work(work)
                else:
                    await self._process_signal_work(work)
            finally:
                if work is not None:
                    self._callback_queue_bytes -= work.payload_bytes
                self._callback_queue.task_done()

    # pylint: disable=too-many-statements,too-many-branches
    async def _process_turn_work(self, work: _CallbackWork) -> None:
        response = work.response
        assert response is not None
        assert self._session is not None
        if response.is_terminal:
            return

        release = asyncio.Event()
        async with self._state_lock:
            if response.is_terminal or self._ending:
                return
            active = self._active_response
            if active is not None and active is not response and not active.is_terminal:
                # A previously accepted proactive response is still active. Overwriting
                # ``_active_response`` here would make that response undiscoverable to
                # ``_find_response_locked`` before it is remembered, so its later
                # barge-in/timeout could be dropped and two responses could emit
                # concurrently. This violates the single-active-response invariant and
                # is treated as an illegal protocol state, mirroring the symmetric guard
                # in ``_handle_response_accepted``.
                raise VoiceBridgeProtocolError(
                    "A new turn started while another response is still active",
                    close_code=1008,
                )
            self._active_response = response
            self._active_release = release

        if work.callback is None:
            release_task = asyncio.create_task(release.wait(), name="voice_turn_release")
            try:
                await self._finalize_turn_response(response, release_task, failed=True)
            finally:
                release_task.cancel()
                await asyncio.gather(release_task, return_exceptions=True)
                async with self._state_lock:
                    if self._active_response is response:
                        self._active_response = None
                    if self._active_release is release:
                        self._active_release = None
                    if work.item_id is not None:
                        self._pending_turns.pop(work.item_id, None)
                    if response.is_wire_opened:
                        self._remember_response_locked(response)
            return

        callback_started_ns = time.monotonic_ns()

        async def _invoke_customer_callback() -> None:
            assert work.callback is not None
            await work.callback(self._session, work.event, response)

        customer_task = self._create_customer_task(
            _invoke_customer_callback(),
            name=f"voice_{work.kind}",
        )
        release_task = asyncio.create_task(release.wait(), name="voice_turn_release")
        async with self._state_lock:
            self._active_customer_task = customer_task
        try:
            done, _ = await asyncio.wait((customer_task, release_task), return_when=asyncio.FIRST_COMPLETED)
            if customer_task.done():
                # Transfer the process-level slot to automatic finalization
                # without waiting for the event loop to run done callbacks.
                _release_global_customer_task(customer_task)
            if release_task in done and not customer_task.done():
                # The response's output methods perform their wire writes off the
                # per-response state lock, so this coordinator (not the receive
                # pump) is now responsible for letting an in-flight winning
                # terminal write reach the wire before we cancel the customer
                # task. Draining runs on the callback worker, so the pump stays
                # free to set the cancellation token and process control frames.
                await self._drain_active_send(response)
                await self._schedule_customer_cleanup(customer_task)
            elif customer_task.cancelled():
                if not response.is_terminal and not self.ending:
                    await self._finalize_turn_response(response, release_task, failed=True)
            else:
                error = customer_task.exception()
                if error is not None:
                    terminal_race = isinstance(error, VoiceBridgeConnectionClosedError) and (
                        response.is_terminal or response.response_id in self._terminal_response_ids
                    )
                    if not terminal_race:
                        logger.error("Voice callback failed: %s", type(error).__name__)
                        _CALLBACK_ERROR_COUNTER.add(1, {"kind": work.kind})
                        await self._finalize_turn_response(response, release_task, failed=True)
                else:
                    await self._finalize_turn_response(response, release_task, failed=False)
        except asyncio.CancelledError:
            if not customer_task.done():
                self._schedule_customer_cleanup(customer_task)
            raise
        finally:
            _CALLBACK_DURATION.record(
                (time.monotonic_ns() - callback_started_ns) / 1_000_000,
                {"kind": work.kind},
            )
            release_task.cancel()
            await asyncio.gather(release_task, return_exceptions=True)
            async with self._state_lock:
                if self._active_customer_task is customer_task:
                    self._active_customer_task = None
                if self._active_response is response:
                    self._active_response = None
                if self._active_release is release:
                    self._active_release = None
                if work.item_id is not None:
                    self._pending_turns.pop(work.item_id, None)
                if response.is_wire_opened:
                    self._remember_response_locked(response)

    async def _process_signal_work(self, work: _CallbackWork) -> None:
        if self._session is None:
            return
        if work.success_type is not None:
            assert work.request_id is not None
            if work.callback is None:
                await self.send(
                    "conversation.item.failed",
                    request_id=work.request_id,
                    code="mutation_failed",
                    message="No history mutation callback is registered",
                )
                return
            callback_started_ns = time.monotonic_ns()
            try:
                await self._await_signal_callback(work)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error("Voice history callback failed: %s", type(exc).__name__)
                _CALLBACK_ERROR_COUNTER.add(1, {"kind": work.kind})
                await self.send(
                    "conversation.item.failed",
                    request_id=work.request_id,
                    code="mutation_failed",
                    message="History mutation callback failed",
                )
            else:
                await self.send(work.success_type, request_id=work.request_id)
            finally:
                _CALLBACK_DURATION.record(
                    (time.monotonic_ns() - callback_started_ns) / 1_000_000,
                    {"kind": work.kind},
                )
            return
        if work.callback is None:
            return
        callback_started_ns = time.monotonic_ns()
        try:
            await self._await_signal_callback(work)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Voice signal callback failed: %s", type(exc).__name__)
            _CALLBACK_ERROR_COUNTER.add(1, {"kind": work.kind})
        finally:
            _CALLBACK_DURATION.record(
                (time.monotonic_ns() - callback_started_ns) / 1_000_000,
                {"kind": work.kind},
            )

    async def _await_signal_callback(self, work: _CallbackWork) -> None:
        assert self._session is not None
        assert work.callback is not None

        async def _invoke_customer_callback() -> None:
            assert self._session is not None
            assert work.callback is not None
            await work.callback(self._session, work.event)

        customer_task = self._create_customer_task(
            _invoke_customer_callback(),
            name=f"voice_{work.kind}",
        )
        try:
            await asyncio.shield(customer_task)
        except asyncio.CancelledError as exc:
            if not customer_task.done():
                self._schedule_customer_cleanup(customer_task)
                raise
            current_task = asyncio.current_task()
            cancelling = getattr(current_task, "cancelling", lambda: 0)
            if customer_task.cancelled() and cancelling() == 0:
                raise RuntimeError("Voice signal callback was cancelled") from exc
            raise

    async def _drain_active_send(self, response: VoiceResponse) -> None:
        # Give any in-flight winning write on the response a bounded window to
        # reach the wire before the customer task is cancelled. Bounded so genuine
        # indefinite outbound backpressure cannot wedge the callback worker.
        try:
            await asyncio.wait_for(response._drain_pending_send(), timeout=_CLEANUP_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            logger.warning("Voice in-flight send did not drain before cleanup deadline")

    def _create_customer_task(
        self,
        coroutine: Coroutine[Any, Any, None],
        *,
        name: str,
    ) -> asyncio.Task[None]:
        global _GLOBAL_CUSTOMER_TASK_RESERVATIONS  # pylint: disable=global-statement
        with _GLOBAL_CUSTOMER_TASKS_LOCK:
            if _GLOBAL_CUSTOMER_TASK_RESERVATIONS >= _MAX_GLOBAL_CUSTOMER_TASKS:
                at_limit = True
            else:
                at_limit = False
                _GLOBAL_CUSTOMER_TASK_RESERVATIONS += 1

        if at_limit:
            coroutine.close()
            self._signal_runtime_failure("Voice global customer task limit reached")
            raise RuntimeError("Voice global customer task limit reached")

        try:
            task = asyncio.create_task(coroutine, name=name)
        except BaseException:
            coroutine.close()
            with _GLOBAL_CUSTOMER_TASKS_LOCK:
                _GLOBAL_CUSTOMER_TASK_RESERVATIONS -= 1
            raise

        with _GLOBAL_CUSTOMER_TASKS_LOCK:
            _GLOBAL_CUSTOMER_TASKS.add(task)

        task.add_done_callback(_release_global_customer_task)
        if task.done():
            # Eager task factories may complete the coroutine before
            # create_task returns. Release synchronously; the scheduled done
            # callback is idempotent through the membership check above.
            _release_global_customer_task(task)
        return task

    async def _finalize_turn_response(
        self,
        response: VoiceResponse,
        release_task: asyncio.Task[bool],
        *,
        failed: bool,
    ) -> None:
        finalize = self._create_customer_task(
            response._fail_callback() if failed else response._complete_callback(),
            name="voice_response_callback_finalize",
        )
        done, _ = await asyncio.wait((finalize, release_task), return_when=asyncio.FIRST_COMPLETED)
        if release_task in done and not finalize.done():
            # The bridge terminal already won. Unlike a customer-owned output
            # write, an automatic done/error is now a losing terminal and must
            # be cancelled rather than drained onto the wire.
            finalize.cancel()
            try:
                await asyncio.wait_for(asyncio.shield(finalize), timeout=_CLEANUP_TIMEOUT_SECONDS)
            except asyncio.CancelledError:
                current_task = asyncio.current_task()
                cancelling = getattr(current_task, "cancelling", lambda: 0)
                if cancelling() > 0:
                    raise
            except asyncio.TimeoutError:
                logger.error("Voice response finalization ignored cancellation")
                self._signal_runtime_failure("Voice response finalization did not stop")
                return
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        result = (await asyncio.gather(finalize, return_exceptions=True))[0]
        if isinstance(result, BaseException):
            async with self._state_lock:
                terminal_won = (
                    response.is_terminal
                    or response.response_id in self._terminal_response_ids
                    or self._ending
                    or self._closed
                )
            terminal_race = (
                isinstance(result, (asyncio.CancelledError, VoiceBridgeConnectionClosedError)) and terminal_won
            )
            if not terminal_race:
                raise result

    def _signal_runtime_failure(self, reason: str) -> None:
        self._ending = True
        if not self._resource_limit_reached.done():
            logger.error("%s", reason)
            self._resource_limit_reached.set_result(None)

    def _schedule_customer_cleanup(self, task: asyncio.Task[None]) -> asyncio.Task[None]:
        task.cancel()

        # Retain a reference to the underlying task until it actually completes,
        # even if it swallows CancelledError and runs past the cleanup deadline.
        # The bounded wrapper below only waits _CLEANUP_TIMEOUT_SECONDS and is then
        # discarded; without this the underlying task would keep running with no
        # owner (untracked resource leak). Once the cap is reached, signal the
        # connection supervisor immediately so no more callbacks are dispatched.
        self._resistant_tasks.difference_update(
            existing for existing in tuple(self._resistant_tasks) if existing.done()
        )
        if not task.done():
            self._resistant_tasks.add(task)
            task.add_done_callback(self._resistant_tasks.discard)
            if len(self._resistant_tasks) >= _MAX_RESISTANT_TASKS and not self._resource_limit_reached.done():
                logger.error(
                    "Voice cancellation-resistant task limit reached (%d); closing connection",
                    _MAX_RESISTANT_TASKS,
                )
                self._resource_limit_reached.set_result(None)

        async def _bounded_cleanup() -> None:
            try:
                await asyncio.wait_for(asyncio.shield(task), timeout=_CLEANUP_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                logger.warning("Voice callback ignored cancellation beyond cleanup deadline")
            except asyncio.CancelledError:
                pass
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        cleanup = asyncio.create_task(_bounded_cleanup(), name="voice_callback_cleanup")
        self._cleanup_tasks.add(cleanup)
        cleanup.add_done_callback(self._cleanup_tasks.discard)
        return cleanup

    async def _handle_playback_terminal(self, payload: dict[str, Any], *, kind: str) -> None:
        response_id = require_prefixed_id(payload, "response_id", "r_")
        heard_text = require_string(payload, "heard_text")
        item_id = optional_string(payload, "item_id")
        if item_id is not None and (not item_id.startswith("it_") or len(item_id) <= 3):
            raise VoiceBridgeProtocolError("Playback item_id must start with it_", close_code=1008)
        async with self._state_lock:
            if response_id in self._playback_outcomes:
                return
            response = self._find_response_locked(response_id)
            if response is None:
                if response_id in self._pending_proactive:
                    raise VoiceBridgeProtocolError(
                        f"{kind} is invalid before proactive response.accepted",
                        close_code=1008,
                    )
                if response_id in self._seen_response_ids:
                    return
                raise VoiceBridgeProtocolError("Unknown playback response_id", close_code=1008)
            if item_id is not None and not response._owns_item_id(item_id):
                raise VoiceBridgeProtocolError("Playback item_id does not belong to response_id", close_code=1008)
            self._playback_outcomes.add(response_id)
            waiter = self._cancel_waiters.pop(response_id, None)
            abandoned = response_id in self._abandoned_proactive_cancels
            self._abandoned_proactive_cancels.discard(response_id)
            if kind == "cancelled" and waiter is None and not abandoned:
                self._playback_outcomes.remove(response_id)
                raise VoiceBridgeProtocolError(
                    "response.cancelled requires a pending response.cancel",
                    close_code=1008,
                )
            active = self._active_response is response
            release = self._active_release if active and not response.is_cancel_pending else None
            playback_terminal_won = response_id not in self._terminal_response_ids
            self._terminal_response_ids.add(response_id)
        await response._mark_terminal()
        outcome = ResponseCancellationOutcome(
            response_id=response_id,
            kind="barge_in" if kind == "barge_in" else "cancelled",
            heard_text=heard_text,
            item_id=item_id,
        )
        if waiter is not None and not waiter.done():
            waiter.set_result(outcome)
        if playback_terminal_won:
            self._record_terminal(response_id, kind)
        if release is not None:
            release.set()
        if kind == "barge_in" and self._on_barge_in is not None:
            self._put_work(
                _CallbackWork(
                    kind="barge_in",
                    event=BargeInEvent(
                        response_id=response_id,
                        heard_text=heard_text,
                        item_id=item_id,
                    ),
                    callback=self._on_barge_in,
                )
            )

    async def _handle_response_timeout(  # pylint: disable=too-many-nested-blocks
        self, event: ResponseTimeoutEvent
    ) -> None:
        responses: list[VoiceResponse] = []
        timeout_metric_winners: set[str] = set()
        release: asyncio.Event | None = None
        cancel_waiters: list[asyncio.Future[ResponseCancellationOutcome]] = []
        async with self._state_lock:
            if event.response_id is not None:
                response = self._find_response_locked(event.response_id)
                if event.response_id in self._playback_outcomes:
                    return
                if response is None:
                    if event.response_id in self._seen_response_ids:
                        return
                    raise VoiceBridgeProtocolError("Unknown response.timeout response_id", close_code=1008)
                responses.append(response)
                self._playback_outcomes.add(event.response_id)
                if event.response_id not in self._terminal_response_ids:
                    timeout_metric_winners.add(event.response_id)
                self._terminal_response_ids.add(event.response_id)
                if self._active_response is response:
                    release = self._active_release
                cancel_waiter = self._cancel_waiters.pop(event.response_id, None)
                if cancel_waiter is not None:
                    cancel_waiters.append(cancel_waiter)
            else:
                assert event.item_ids is not None
                pending_ids = tuple(self._pending_turns)
                if pending_ids[: len(event.item_ids)] == event.item_ids:
                    for item_id in event.item_ids:
                        response = self._pending_turns.pop(item_id)
                        if response.is_wire_opened:
                            raise VoiceBridgeProtocolError(
                                "response.timeout item_ids referenced an open response",
                                close_code=1008,
                            )
                        responses.append(response)
                        if response.response_id not in self._terminal_response_ids:
                            timeout_metric_winners.add(response.response_id)
                        self._terminal_response_ids.add(response.response_id)
                        if self._active_response is response:
                            release = self._active_release
                else:
                    remaining = event.item_ids
                    while remaining:
                        resolved = next(
                            (
                                (prefix, response, opened_response)
                                for prefix, (response, opened_response) in self._resolved_input_prefixes.items()
                                if remaining[: len(prefix)] == prefix
                            ),
                            None,
                        )
                        if resolved is not None:
                            prefix, response, opened_response = resolved
                            self._resolved_input_prefixes.pop(prefix, None)
                            if response not in responses:
                                responses.append(response)
                            if response.response_id not in self._terminal_response_ids:
                                timeout_metric_winners.add(response.response_id)
                            self._terminal_response_ids.add(response.response_id)
                            if self._active_response is response:
                                release = self._active_release
                            if opened_response:
                                self._playback_outcomes.add(response.response_id)
                                cancel_waiter = self._cancel_waiters.pop(response.response_id, None)
                                if cancel_waiter is not None:
                                    cancel_waiters.append(cancel_waiter)
                            remaining = remaining[len(prefix) :]
                            continue

                        pending_ids = tuple(self._pending_turns)
                        if pending_ids[: len(remaining)] != remaining:
                            raise VoiceBridgeProtocolError(
                                "response.timeout item_ids do not match the pending or just-resolved prefix",
                                close_code=1008,
                            )
                        for item_id in remaining:
                            response = self._pending_turns.pop(item_id)
                            if response.is_wire_opened:
                                raise VoiceBridgeProtocolError(
                                    "response.timeout item_ids referenced an open response",
                                    close_code=1008,
                                )
                            if response not in responses:
                                responses.append(response)
                            if response.response_id not in self._terminal_response_ids:
                                timeout_metric_winners.add(response.response_id)
                            self._terminal_response_ids.add(response.response_id)
                            if self._active_response is response:
                                release = self._active_release
                        remaining = ()
        for response in responses:
            await response._mark_terminal()
            if response.response_id in timeout_metric_winners:
                self._record_terminal(response.response_id, "timeout")
        for cancel_waiter in cancel_waiters:
            if not cancel_waiter.done():
                cancel_waiter.set_exception(VoiceBridgeConnectionClosedError("Response terminated by timeout"))
        if release is not None:
            release.set()
        if self._on_response_timeout is not None:
            self._put_work(
                _CallbackWork(
                    kind="response.timeout",
                    event=event,
                    callback=self._on_response_timeout,
                )
            )

    async def _handle_response_accepted(self, payload: dict[str, Any]) -> None:
        response_id = require_prefixed_id(payload, "response_id", "r_")
        async with self._state_lock:
            pending = self._pending_proactive.get(response_id)
            if pending is None:
                raise VoiceBridgeProtocolError("Unknown proactive response_id", close_code=1008)
            response, future = pending
            if self._active_response is not None and not self._active_response.is_terminal:
                raise VoiceBridgeProtocolError(
                    "Proactive response accepted while another response is active",
                    close_code=1008,
                )
            self._pending_proactive.pop(response_id, None)
            self._active_response = response
            self._response_start_ns[response_id] = time.monotonic_ns()
        await response._mark_accepted()
        if not future.done():
            future.set_result((True, ""))

    async def _handle_response_dropped(self, payload: dict[str, Any]) -> None:
        response_id = require_prefixed_id(payload, "response_id", "r_")
        reason = safe_code(require_string(payload, "reason", non_empty=True), "dropped")
        async with self._state_lock:
            pending = self._pending_proactive.pop(response_id, None)
            if pending is None:
                raise VoiceBridgeProtocolError("Unknown proactive response_id", close_code=1008)
            response, future = pending
            self._abandoned_proactive_cancels.discard(response_id)
            self._terminal_response_ids.add(response_id)
        await response._mark_terminal()
        self._record_terminal(response_id, "dropped")
        if not future.done():
            future.set_result((False, reason))

    async def _handle_session_end(self, payload: dict[str, Any]) -> None:
        event = SessionEndEvent(reason=require_string(payload, "reason", non_empty=True))
        async with self._state_lock:
            self._ending = True
            responses = list(self._pending_turns.values())
            self._pending_turns.clear()
            if self._active_response is not None and self._active_response not in responses:
                responses.append(self._active_response)
            self._terminal_response_ids.update(response.response_id for response in responses)
            release = self._active_release
        for response in responses:
            was_terminal = response.is_terminal
            await response._mark_terminal()
            if not was_terminal:
                self._record_terminal(response.response_id, "session_end")
        self._fail_helper_waiters("Voice session ended")
        if release is not None:
            release.set()
        if self._on_session_end is not None:
            # Run the teardown callback on a dedicated task instead of enqueuing it
            # behind ordinary callback work. If a prior callback is stalled and the
            # worker is cancelled at shutdown before draining the queue, a queued
            # session.end item would never run; the dedicated task is awaited on its
            # own bounded path in _shutdown_runtime.
            work = _CallbackWork(kind="session.end", event=event, callback=self._on_session_end)
            self._session_end_task = asyncio.create_task(
                self._run_session_end_callback(work),
                name="voice_session_end",
            )

    async def _run_session_end_callback(self, work: _CallbackWork) -> None:
        callback_started_ns = time.monotonic_ns()
        try:
            await self._await_signal_callback(work)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Voice session.end callback failed: %s", type(exc).__name__)
            _CALLBACK_ERROR_COUNTER.add(1, {"kind": work.kind})
        finally:
            _CALLBACK_DURATION.record(
                (time.monotonic_ns() - callback_started_ns) / 1_000_000,
                {"kind": work.kind},
            )

    async def _receive_payload(self) -> dict[str, Any] | None:
        while True:
            message = await self._websocket.receive()
            message_type = message.get("type")
            if message_type == "websocket.disconnect":
                self._record_close(int(message.get("code") or 1006))
                self._closed = True
                return None
            if message_type != "websocket.receive":
                raise VoiceBridgeProtocolError("Unexpected ASGI WebSocket event")
            if message.get("bytes") is not None:
                _PROTOCOL_VIOLATION_COUNTER.add(1, {"close_code": 1003})
                await self._close(code=1003, reason="Binary data is unsupported")
                return None
            frame = message.get("text")
            if not isinstance(frame, str):
                raise VoiceBridgeProtocolError("Voice bridge requires JSON text frames")
            try:
                frame_bytes = len(frame.encode("utf-8"))
            except UnicodeEncodeError as exc:
                raise VoiceBridgeProtocolError("Voice bridge frame contains invalid Unicode") from exc
            if frame_bytes > _MAX_FRAME_BYTES:
                raise VoiceBridgeProtocolError("Voice bridge frame exceeds the maximum encoded size", close_code=1009)
            payload = decode_frame(frame)
            message_id = require_string(payload, "id", non_empty=True)
            # Bound BOTH the key and the value to fixed-size digests. The untrusted
            # message id has no length limit, so keying by the raw id would let a
            # peer pin gigabytes (up to _MAX_SEEN_MESSAGES ids of ~1 MB each) before
            # the entry-count cap is reached, even though the value is already a
            # digest. A sha256 hexdigest bounds each id key to 64 chars; the value
            # digest bounds each stored payload the same way. Reusing an id with
            # different content still collides on the key and differs on the value.
            message_key = hashlib.sha256(message_id.encode("utf-8")).hexdigest()
            digest = hashlib.sha256(canonical_payload(payload).encode("utf-8")).hexdigest()
            previous = self._seen_messages.get(message_key)
            if previous is not None:
                if previous != digest:
                    raise VoiceBridgeProtocolError("Message id was reused with different content", close_code=1008)
                continue
            if len(self._seen_messages) >= _MAX_SEEN_MESSAGES:
                raise VoiceBridgeProtocolError("Message dedupe limit exceeded", close_code=1008)
            self._seen_messages[message_key] = digest
            return payload

    async def _shutdown_runtime(self, *, drain_callbacks: bool) -> None:
        self._ending = True
        prefetched_receive = self._prefetched_receive_task
        self._prefetched_receive_task = None
        if prefetched_receive is not None and not prefetched_receive.done():
            prefetched_receive.cancel()
            await asyncio.gather(prefetched_receive, return_exceptions=True)
        async with self._state_lock:
            responses = list(self._pending_turns.values())
            self._pending_turns.clear()
            if self._active_response is not None and self._active_response not in responses:
                responses.append(self._active_response)
            self._terminal_response_ids.update(response.response_id for response in responses)
            release = self._active_release
        for response in responses:
            was_terminal = response.is_terminal
            await response._mark_terminal()
            if not was_terminal:
                self._record_terminal(response.response_id, "connection_closed")
        self._fail_helper_waiters("Voice connection closed")
        if release is not None:
            release.set()

        worker = self._callback_worker
        if worker is not None:
            if not drain_callbacks:
                worker.cancel()
                await asyncio.gather(worker, return_exceptions=True)
            else:
                try:
                    await asyncio.wait_for(self._callback_queue.join(), timeout=_CLEANUP_TIMEOUT_SECONDS)
                except asyncio.TimeoutError:
                    logger.warning("Voice callback drain exceeded cleanup deadline")
            if drain_callbacks and not worker.done():
                try:
                    self._callback_queue.put_nowait(None)
                except asyncio.QueueFull:
                    worker.cancel()
                try:
                    await asyncio.wait_for(worker, timeout=_CLEANUP_TIMEOUT_SECONDS)
                except asyncio.TimeoutError:
                    worker.cancel()
                    await asyncio.gather(worker, return_exceptions=True)
                except asyncio.CancelledError:
                    pass

        self._discard_callback_queue()

        session_end_task = self._session_end_task
        if session_end_task is not None:
            # Dedicated bounded path for session teardown, independent of the
            # ordinary callback queue drained above.
            try:
                await asyncio.wait_for(asyncio.shield(session_end_task), timeout=_CLEANUP_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                logger.warning("Voice session.end callback exceeded shutdown deadline")
                if not session_end_task.done():
                    self._schedule_customer_cleanup(session_end_task)
            except asyncio.CancelledError:
                pass
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        self._closed = True
        self._record_close(1000)
        if self._cleanup_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tuple(self._cleanup_tasks), return_exceptions=True),
                    timeout=_CLEANUP_TIMEOUT_SECONDS,
                )
            except asyncio.TimeoutError:
                for task in tuple(self._cleanup_tasks):
                    task.cancel()
        self._release_connection_state()

    def _release_connection_state(self) -> None:
        """Release connection-scoped caches after dispatch has stopped."""
        self._resolved_input_prefixes.clear()
        self._recent_responses.clear()
        self._seen_response_ids.clear()
        self._terminal_response_ids.clear()
        self._seen_messages.clear()
        self._seen_input_ids.clear()
        self._playback_outcomes.clear()
        self._response_start_ns.clear()
        self._first_output_recorded.clear()
        self._resistant_tasks.clear()
        self._cleanup_tasks.clear()
        self._active_customer_task = None
        self._active_response = None
        self._active_release = None
        self._callback_worker = None
        self._session_end_task = None
        self._session = None

    def _fail_helper_waiters(self, message: str) -> None:
        for future in tuple(self._cancel_waiters.values()):
            if not future.done():
                future.set_exception(VoiceBridgeConnectionClosedError(message))
        self._cancel_waiters.clear()
        self._abandoned_proactive_cancels.clear()
        self._dtmf_collections.clear()
        self._dtmf_cancel_pending.clear()
        self._recent_dtmf_cancel_races.clear()
        for _, proactive_future in self._pending_proactive.values():
            if not proactive_future.done():
                proactive_future.set_exception(VoiceBridgeConnectionClosedError(message))
        self._pending_proactive.clear()

    def _find_response_locked(self, response_id: str) -> VoiceResponse | None:
        if self._active_response is not None and self._active_response.response_id == response_id:
            return self._active_response
        return self._recent_responses.get(response_id)

    def _remember_response_locked(self, response: VoiceResponse) -> None:
        # Retained only for late timeout/barge-in reconciliation, which needs
        # identity and terminal state, not the emitted text. Free the accumulated
        # per-item buffers so _MAX_RECENT_RESPONSES entries stay lightweight rather
        # than pinning up to _MAX_RESPONSE_BYTES of text each.
        response._release_output_buffers()
        self._recent_responses[response.response_id] = response
        self._recent_responses.move_to_end(response.response_id)
        while len(self._recent_responses) > _MAX_RECENT_RESPONSES:
            self._recent_responses.popitem(last=False)

    def _record_first_output(self, message_type: str, fields: dict[str, Any]) -> None:
        if message_type not in ("response.output_text.delta", "response.output_text.done"):
            return
        response_id = fields.get("response_id")
        if isinstance(response_id, str):
            self._record_first_output_for_response(response_id)

    def _record_first_output_for_response(self, response_id: str) -> None:
        if response_id in self._first_output_recorded:
            return
        started = self._response_start_ns.get(response_id)
        if started is None:
            return
        self._first_output_recorded.add(response_id)
        duration_ms = (time.monotonic_ns() - started) / 1_000_000
        _FIRST_OUTPUT_DURATION.record(duration_ms)

    def _record_terminal(self, response_id: str, terminal_kind: str) -> None:
        _TERMINAL_COUNTER.add(1, {"kind": terminal_kind})
        self._response_start_ns.pop(response_id, None)
        self._first_output_recorded.discard(response_id)

    def _record_activation(self, result: str) -> None:
        if self._activation_recorded:
            return
        self._activation_recorded = True
        _ACTIVATION_COUNTER.add(1, {"result": result})

    def _record_close(self, code: int) -> None:
        if self._close_recorded:
            return
        self._close_recorded = True
        _CLOSE_CODE_COUNTER.add(1, {"code": code})

    def _ensure_ready(self) -> None:
        if not self._ready or self._closed:
            raise VoiceBridgeConnectionClosedError("The voice connection is not ready")
        if self._ending:
            raise VoiceBridgeConnectionClosedError("The voice session is ending")

    async def _close(self, *, code: int, reason: str) -> None:
        if self._closed:
            return
        self._record_close(code)
        self._closed = True
        await self._websocket.close(code=code, reason=reason)


def _estimate_event_bytes(event: Any) -> int:
    """Return a conservative recursive byte estimate for queued event data.

    :param event: Typed callback event to measure.
    :type event: Any
    :return: Estimated retained byte count.
    :rtype: int
    """
    total = 0
    pending = [event]
    seen: set[int] = set()
    while pending:
        value = pending.pop()
        if isinstance(value, str):
            total += len(value.encode("utf-8"))
            continue
        if value is None or isinstance(value, (bool, int, float)):
            total += 8
            continue
        value_id = id(value)
        if value_id in seen:
            continue
        seen.add(value_id)
        if is_dataclass(value) and not isinstance(value, type):
            pending.extend(getattr(value, field.name) for field in dataclass_fields(value))
        elif isinstance(value, Mapping):
            pending.extend(value.keys())
            pending.extend(value.values())
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            pending.extend(value)
    return total
