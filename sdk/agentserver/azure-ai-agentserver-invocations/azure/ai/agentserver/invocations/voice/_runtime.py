# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Public response, item, and session helpers for typed voice callbacks."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from collections.abc import Mapping
from typing import Any, Literal, Protocol

from azure.ai.agentserver.core import experimental

from ._models import ResponseCancellationOutcome, ResponseTimeouts, SessionStartEvent
from ._protocol import (
    _PreparedFrame,
    VoiceBridgeConnectionClosedError,
    new_id,
    normalize_voice,
    safe_code,
    safe_message,
)

# VoiceTextItem and VoiceResponse are two public halves of one stateful helper.
# pylint: disable=protected-access

_MAX_OUTPUT_ITEM_BYTES = 900 * 1024
_MAX_OUTPUT_ITEM_CHUNKS = 4096
_MAX_RESPONSE_ITEMS = 1024
# Bound list/object overhead across all items; tiny deltas can consume substantial
# memory while remaining far below the encoded-text byte budget.
_MAX_RESPONSE_CHUNKS = 16 * 1024
# Cumulative encoded-text budget across every item in one response. Each item is
# already capped at _MAX_OUTPUT_ITEM_BYTES and a response may hold up to
# _MAX_RESPONSE_ITEMS items, so without this ceiling a single active response
# could accumulate ~900 MiB of retained text before completing. Voice turns are
# spoken text, so a few MiB is far above any legitimate response while bounding
# the worst-case live memory of the one active response.
_MAX_RESPONSE_BYTES = 8 * 1024 * 1024


class _ConnectionSender(Protocol):
    @property
    def ending(self) -> bool: ...

    async def send(self, message_type: str, **fields: Any) -> None: ...

    def prepare_frame(self, message_type: str, **fields: Any) -> _PreparedFrame: ...

    async def send_prepared(self, prepared: _PreparedFrame, *, state_committed: bool) -> None: ...

    def prepare_response_item(self, response_id: str, item_id: str) -> None: ...

    def discard_response_item(self, response_id: str, item_id: str) -> None: ...

    async def open_response(self, response_id: str, in_reply_to: tuple[str, ...] | None) -> bool: ...

    async def decline_response(self, in_reply_to: tuple[str, ...], reason: str | None) -> None: ...

    async def begin_cancel(
        self, response_id: str, reason: str | None
    ) -> asyncio.Future[ResponseCancellationOutcome]: ...

    async def response_completed(self, response_id: str, terminal_kind: str = "done") -> None: ...

    async def register_dtmf_collection(
        self,
        *,
        response_id: str,
        collection_id: str,
        max_digits: int,
        terminator: str | None,
        initial_timeout_ms: int,
        inter_digit_timeout_ms: int,
    ) -> None: ...

    async def cancel_dtmf_collection(self, collection_id: str) -> None: ...

    async def end_call(self, reason: str, mode: str) -> None: ...

    async def start_proactive_response(
        self,
        *,
        admission_timeout_ms: int,
        supersede_key: str | None,
    ) -> "VoiceResponse": ...

    async def report_session_error(self, code: str, message: str) -> None: ...

    def reserve_output_bytes(self, size: int) -> None: ...

    def release_output_bytes(self, size: int) -> None: ...


@experimental
class VoiceCancellationToken:
    """Read-only cooperative cancellation signal for response callbacks."""

    _event: asyncio.Event

    def __init__(self) -> None:
        raise TypeError("VoiceCancellationToken instances are created by VoiceAgentServerHost")

    @classmethod
    def _create(cls) -> "VoiceCancellationToken":
        instance = object.__new__(cls)
        instance._event = asyncio.Event()
        return instance

    @property
    def is_cancelled(self) -> bool:
        """Whether the response reached a terminal cancellation boundary.

        :return: ``True`` after timeout, barge-in, session end, or disconnect.
        :rtype: bool
        """
        return self._event.is_set()

    async def wait(self) -> None:
        """Wait until response work should stop."""
        await self._event.wait()

    def _cancel(self) -> None:
        self._event.set()


@experimental
class VoiceTextItem:
    """One ordered text item in a :class:`VoiceResponse`.

    Instances are created by :meth:`VoiceResponse.new_text_item`.
    """

    _response: "VoiceResponse"
    _item_id: str
    _chunks: list[str]
    _text_bytes: int
    _started: bool
    _send_in_flight: bool
    _done: bool

    def __init__(self) -> None:
        raise TypeError("VoiceTextItem instances are created by VoiceResponse")

    @classmethod
    def _create(cls, response: "VoiceResponse", item_id: str) -> "VoiceTextItem":
        instance = object.__new__(cls)
        instance._response = response
        instance._item_id = item_id
        instance._chunks = []
        instance._text_bytes = 0
        instance._started = False
        instance._send_in_flight = False
        instance._done = False
        return instance

    @property
    def item_id(self) -> str:
        """Return the SDK-allocated output item identifier.

        :return: Output item identifier.
        :rtype: str
        """
        return self._item_id

    async def send_text(self, text: str, *, voice: Mapping[str, Any] | None = None) -> None:
        """Send this item as one complete non-streamed message.

        :param text: Non-empty complete text to synthesize.
        :type text: str
        :keyword voice: Optional non-empty Voice Live voice patch.
        :paramtype voice: Mapping[str, Any] or None
        :raises ValueError: If the encoded item exceeds the transport-safe limit.
        """
        await self._response._send_item_text(self, text, voice=voice)

    async def send_text_delta(self, delta: str, *, voice: Mapping[str, Any] | None = None) -> None:
        """Send one streaming increment for this item.

        :param delta: Next non-empty text fragment.
        :type delta: str
        :keyword voice: Optional non-empty Voice Live voice patch.
        :paramtype voice: Mapping[str, Any] or None
        :raises ValueError: If the accumulated item exceeds local byte/chunk limits.
        """
        await self._response._send_item_delta(self, delta, voice=voice)

    async def send_text_done(self, *, voice: Mapping[str, Any] | None = None) -> None:
        """Complete this streamed item with its accumulated full text.

        :keyword voice: Optional non-empty Voice Live voice patch.
        :paramtype voice: Mapping[str, Any] or None
        """
        await self._response._send_item_done(self, voice=voice)


@experimental
class VoiceResponse:  # pylint: disable=too-many-instance-attributes
    """SDK-owned response helper bound to an immutable input prefix."""

    _sender: _ConnectionSender
    _response_id: str
    _in_reply_to: tuple[str, ...] | None
    _wire_opened: bool
    _accepted: bool
    _terminal: bool
    _sealed: bool
    _cancel_pending: bool
    _items: list[VoiceTextItem]
    _response_bytes: int
    _response_chunks: int
    _simple_item: VoiceTextItem | None
    _advanced_items: bool
    _cancellation: VoiceCancellationToken
    _lock: asyncio.Lock
    _send_lock: asyncio.Lock

    def __init__(self) -> None:
        raise TypeError("VoiceResponse instances are created by VoiceAgentServerHost")

    @classmethod
    def _create(
        cls,
        sender: _ConnectionSender,
        *,
        response_id: str | None = None,
        in_reply_to: tuple[str, ...] | None,
        wire_opened: bool = False,
        accepted: bool = True,
    ) -> "VoiceResponse":
        instance = object.__new__(cls)
        instance._sender = sender
        instance._response_id = response_id or new_id("r")
        instance._in_reply_to = in_reply_to
        instance._wire_opened = wire_opened
        instance._accepted = accepted
        instance._terminal = False
        instance._sealed = False
        instance._cancel_pending = False
        instance._items = []
        instance._response_bytes = 0
        instance._response_chunks = 0
        instance._simple_item = None
        instance._advanced_items = False
        instance._cancellation = VoiceCancellationToken._create()
        instance._lock = asyncio.Lock()
        # Serializes one output operation's full validate->send->commit lifecycle
        # per response (preserving wire order and byte accounting). Network I/O is
        # performed while holding _send_lock but NEVER while holding _lock, so the
        # sole receive pump's _mark_terminal()/cancellation path (which needs only
        # _lock) can never block behind a send stalled on outbound backpressure.
        # The turn coordinator drains _send_lock (see _drain_pending_send) before
        # cancelling the customer task, so a winning terminal write still reaches
        # the wire even though the pump is no longer serialized behind it.
        instance._send_lock = asyncio.Lock()
        return instance

    @property
    def response_id(self) -> str:
        """Return the SDK-allocated response identifier.

        :return: Response identifier.
        :rtype: str
        """
        return self._response_id

    @property
    def in_reply_to(self) -> tuple[str, ...] | None:
        """Return the immutable input prefix, or ``None`` when proactive.

        :return: Ordered input identifiers or ``None``.
        :rtype: tuple[str, ...] or None
        """
        return self._in_reply_to

    @property
    def is_cancel_pending(self) -> bool:
        """Whether self-cancel is awaiting the bridge playback outcome.

        :return: ``True`` while cancellation arbitration is pending.
        :rtype: bool
        """
        return self._cancel_pending

    @property
    def is_terminal(self) -> bool:
        """Whether the response no longer accepts output.

        :return: ``True`` after any terminal transition.
        :rtype: bool
        """
        return self._terminal

    @property
    def is_wire_opened(self) -> bool:
        """Whether ``response.created`` has been emitted.

        :return: ``True`` when visible on the wire.
        :rtype: bool
        """
        return self._wire_opened

    @property
    def cancellation(self) -> VoiceCancellationToken:
        """Return the cooperative cancellation signal for this response.

        :return: Read-only response cancellation token.
        :rtype: VoiceCancellationToken
        """
        return self._cancellation

    def new_text_item(self) -> VoiceTextItem:
        """Create the next ordered output item.

        :return: A new text item helper.
        :rtype: VoiceTextItem
        :raises RuntimeError: If the previous item is incomplete or simple helpers were used.
        :raises ValueError: If the response reached the local output-item limit.
        """
        self._ensure_locally_writable()
        if self._simple_item is not None:
            raise RuntimeError("Cannot mix simple response helpers with new_text_item")
        if self._items and not self._items[-1]._done:  # pylint: disable=protected-access
            raise RuntimeError("Complete the previous response item first")
        if len(self._items) >= _MAX_RESPONSE_ITEMS:
            raise ValueError("A response cannot exceed 1024 output items")
        self._advanced_items = True
        item = VoiceTextItem._create(self, new_id("it"))
        self._items.append(item)
        return item

    async def send_text(self, text: str, *, voice: Mapping[str, Any] | None = None) -> None:
        """Send one complete non-streamed item through the simple helper.

        :param text: Non-empty complete text to synthesize.
        :type text: str
        :keyword voice: Optional non-empty Voice Live voice patch.
        :paramtype voice: Mapping[str, Any] or None
        :raises ValueError: If the encoded item exceeds the transport-safe limit.
        """
        await self._get_simple_item().send_text(text, voice=voice)

    async def send_text_delta(self, delta: str, *, voice: Mapping[str, Any] | None = None) -> None:
        """Send one streaming increment through the simple helper.

        :param delta: Next non-empty text fragment.
        :type delta: str
        :keyword voice: Optional non-empty Voice Live voice patch.
        :paramtype voice: Mapping[str, Any] or None
        :raises ValueError: If the accumulated item exceeds local byte/chunk limits.
        """
        await self._get_simple_item().send_text_delta(delta, voice=voice)

    async def send_text_done(self, *, voice: Mapping[str, Any] | None = None) -> None:
        """Complete the streamed simple item.

        :keyword voice: Optional non-empty Voice Live voice patch.
        :paramtype voice: Mapping[str, Any] or None
        """
        await self._get_simple_item(create=False).send_text_done(voice=voice)

    async def decline(self, *, reason: str | None = None) -> None:
        """Explicitly resolve this input prefix without opening a response.

        :keyword reason: Optional open-enum decline reason.
        :paramtype reason: str or None
        """
        if reason is not None:
            reason = _require_string(reason, "reason")
        async with self._send_lock:
            async with self._lock:
                self._ensure_writable_locked()
                if self._in_reply_to is None:
                    raise RuntimeError("A proactive response cannot be declined")
                if self._wire_opened or any(item._started for item in self._items):  # pylint: disable=protected-access
                    raise RuntimeError("Cannot decline after opening a response")
            await self._sender.decline_response(self._in_reply_to, reason)
            async with self._lock:
                self._terminal = True
                self._sealed = True

    async def fail(self, *, code: str, message: str) -> None:
        """Terminate this response with a sanitized response-scoped error.

        :keyword code: Machine-readable open-enum code.
        :paramtype code: str
        :keyword message: Bounded diagnostic message; do not include sensitive content.
        :paramtype message: str
        """
        code = safe_code(code, "agent_error")
        message = safe_message(message, "Agent response failed")
        async with self._send_lock:
            async with self._lock:
                self._ensure_writable_locked()
            prepared = self._prepare_frame(
                "error",
                code=code,
                message=message,
                response_id=self._response_id,
            )
            await self._ensure_open()
            async with self._lock:
                self._ensure_writable_locked()
                self._claim_local_terminal_locked()
            await self._send_prepared_committed(prepared)
        await self._notify_response_completed("error")

    async def cancel(self, *, reason: str | None = None) -> ResponseCancellationOutcome:
        """Request self-cancel and await the winning playback outcome.

        :keyword reason: Optional open-enum cancellation reason.
        :paramtype reason: str or None
        :return: ``cancelled`` or racing caller ``barge_in`` outcome.
        :rtype: ResponseCancellationOutcome
        """
        if reason is not None:
            reason = _require_string(reason, "reason")
        future: asyncio.Future[ResponseCancellationOutcome] | None = None
        try:
            async with self._send_lock:
                async with self._lock:
                    self._ensure_writable_locked()
                    if not self._wire_opened:
                        raise RuntimeError("Cannot cancel a response before response.created")
                    if self._cancel_pending:
                        raise RuntimeError("Response cancellation is already pending")
                    self._cancel_pending = True
                future = await self._sender.begin_cancel(self._response_id, reason)
        except BaseException:
            async with self._lock:
                self._cancel_pending = False
            raise
        assert future is not None
        try:
            # Shield the arbitration future: if only the caller's await is
            # cancelled, the bridge outcome must keep arbitrating and the
            # response must stay non-writable. Clearing _cancel_pending here
            # would let customer code resume output while response.cancel is
            # already on the wire and no terminal has been produced.
            return await asyncio.shield(future)
        finally:
            if future.done():
                async with self._lock:
                    self._cancel_pending = False

    async def collect_dtmf(
        self,
        *,
        max_digits: int,
        initial_timeout_ms: int,
        inter_digit_timeout_ms: int,
        terminator: str | None = None,
    ) -> str:
        """Arm structured DTMF collection after this response drains.

        :keyword max_digits: Positive maximum returned digit count.
        :paramtype max_digits: int
        :keyword initial_timeout_ms: Positive first-key timeout in milliseconds.
        :paramtype initial_timeout_ms: int
        :keyword inter_digit_timeout_ms: Positive inter-key timeout in milliseconds.
        :paramtype inter_digit_timeout_ms: int
        :keyword terminator: Optional single DTMF terminator excluded from the result.
        :paramtype terminator: str or None
        :return: SDK-allocated ``dc_`` collection identifier.
        :rtype: str
        """
        max_digits = _require_positive_int(max_digits, "max_digits")
        initial_timeout_ms = _require_positive_int(initial_timeout_ms, "initial_timeout_ms")
        inter_digit_timeout_ms = _require_positive_int(inter_digit_timeout_ms, "inter_digit_timeout_ms")
        if terminator is not None:
            terminator = _require_string(terminator, "terminator")
            if len(terminator) != 1 or terminator not in "0123456789*#":
                raise ValueError("terminator must be one DTMF key")
        collection_id = new_id("dc")
        async with self._send_lock:
            async with self._lock:
                self._ensure_writable_locked()
            await self._ensure_open()
            await self._sender.register_dtmf_collection(
                response_id=self._response_id,
                collection_id=collection_id,
                max_digits=max_digits,
                terminator=terminator,
                initial_timeout_ms=initial_timeout_ms,
                inter_digit_timeout_ms=inter_digit_timeout_ms,
            )
        return collection_id

    async def handoff(self, *, target: str, message: str | None = None) -> None:
        """Request terminal handoff to a same-project hosted text agent.

        :keyword target: Stable target agent name.
        :paramtype target: str
        :keyword message: Optional bridge-owned transition line.
        :paramtype message: str or None
        """
        target = _require_string(target, "target")
        if not target:
            raise ValueError("target must be non-empty")
        if message is not None:
            message = _require_string(message, "message")
        fields: dict[str, Any] = {
            "response_id": self._response_id,
            "target": target,
        }
        if message is not None:
            fields["message"] = message
        async with self._send_lock:
            async with self._lock:
                self._ensure_writable_locked()
            prepared = self._prepare_frame("handoff", **fields)
            await self._ensure_open()
            async with self._lock:
                self._ensure_writable_locked()
                self._claim_local_terminal_locked(cancel=True)
            await self._send_prepared_committed(prepared)
        await self._notify_response_completed("handoff")

    async def done(self) -> None:
        """Explicitly finish normal generation.

        Callback-bound responses normally auto-complete on callback return;
        proactive responses use this method explicitly.
        """
        async with self._send_lock:
            async with self._lock:
                self._ensure_writable_locked()
                if not self._wire_opened or not self._items:
                    raise RuntimeError("response.done requires at least one completed output item")
                if any(not item._done for item in self._items):  # pylint: disable=protected-access
                    raise RuntimeError("Complete every response item before response.done")
            prepared = self._prepare_frame("response.done", response_id=self._response_id)
            async with self._lock:
                self._ensure_writable_locked()
                self._claim_local_terminal_locked()
            await self._send_prepared_committed(prepared)
        await self._notify_response_completed("done")

    async def _send_item_text(
        self,
        item: VoiceTextItem,
        text: str,
        *,
        voice: Mapping[str, Any] | None,
    ) -> None:
        text = _require_string(text, "text")
        if not text:
            raise ValueError("text must be non-empty")
        text_bytes = _text_size(text)
        voice_payload = normalize_voice(voice)
        reserved = False
        retained = False
        async with self._send_lock:
            try:
                async with self._lock:
                    self._prepare_item_locked(item)
                    if item._started or item._done:  # pylint: disable=protected-access
                        raise RuntimeError("The response item has already started")
                    if text_bytes > _MAX_OUTPUT_ITEM_BYTES:
                        raise ValueError("An output item exceeds the maximum encoded text size")
                    if self._response_bytes + text_bytes > _MAX_RESPONSE_BYTES:
                        raise ValueError("A response exceeds the maximum cumulative encoded text size")
                    if self._response_chunks >= _MAX_RESPONSE_CHUNKS:
                        raise ValueError("A response exceeds the maximum cumulative text chunk count")
                    self._reserve_output_bytes(text_bytes)
                    reserved = True
                self._register_response_item(item.item_id)
                await self._ensure_open()
                fields: dict[str, Any] = {
                    "response_id": self._response_id,
                    "item_id": item.item_id,
                    "text": text,
                }
                if voice_payload is not None:
                    fields["voice"] = voice_payload
                async with self._lock:
                    item._send_in_flight = True  # pylint: disable=protected-access
                await self._sender.send("response.output_text.done", **fields)
                async with self._lock:
                    item._send_in_flight = False  # pylint: disable=protected-access
                    item._text_bytes = text_bytes  # pylint: disable=protected-access
                    item._started = True  # pylint: disable=protected-access
                    item._done = True  # pylint: disable=protected-access
                    if not self._terminal:
                        item._chunks.append(text)  # pylint: disable=protected-access
                        self._response_bytes += text_bytes
                        self._response_chunks += 1
                        retained = True
            finally:
                self._discard_prepared_response_item(item.item_id)
                async with self._lock:
                    if not retained and not self._sender.ending:
                        # The sender can prove no ambiguous connection-level
                        # commit remains, so the item may be retried locally.
                        item._send_in_flight = False  # pylint: disable=protected-access
                if reserved and not retained:
                    self._release_output_bytes(text_bytes)

    async def _send_item_delta(
        self,
        item: VoiceTextItem,
        delta: str,
        *,
        voice: Mapping[str, Any] | None,
    ) -> None:
        delta = _require_string(delta, "delta")
        if not delta:
            raise ValueError("delta must be non-empty")
        delta_bytes = _text_size(delta)
        voice_payload = normalize_voice(voice)
        reserved = False
        retained = False
        async with self._send_lock:
            try:
                async with self._lock:
                    self._prepare_item_locked(item)
                    if item._done:  # pylint: disable=protected-access
                        raise RuntimeError("The response item is already complete")
                    if len(item._chunks) >= _MAX_OUTPUT_ITEM_CHUNKS:  # pylint: disable=protected-access
                        raise ValueError("An output item cannot exceed 4096 text deltas")
                    if item._text_bytes + delta_bytes > _MAX_OUTPUT_ITEM_BYTES:  # pylint: disable=protected-access
                        raise ValueError("An output item exceeds the maximum encoded text size")
                    if self._response_bytes + delta_bytes > _MAX_RESPONSE_BYTES:
                        raise ValueError("A response exceeds the maximum cumulative encoded text size")
                    if self._response_chunks >= _MAX_RESPONSE_CHUNKS:
                        raise ValueError("A response exceeds the maximum cumulative text chunk count")
                    self._reserve_output_bytes(delta_bytes)
                    reserved = True
                self._register_response_item(item.item_id)
                await self._ensure_open()
                fields: dict[str, Any] = {
                    "response_id": self._response_id,
                    "item_id": item.item_id,
                    "delta": delta,
                }
                if voice_payload is not None:
                    fields["voice"] = voice_payload
                async with self._lock:
                    item._send_in_flight = True  # pylint: disable=protected-access
                await self._sender.send("response.output_text.delta", **fields)
                async with self._lock:
                    item._send_in_flight = False  # pylint: disable=protected-access
                    item._text_bytes += delta_bytes  # pylint: disable=protected-access
                    item._started = True  # pylint: disable=protected-access
                    if not self._terminal:
                        item._chunks.append(delta)  # pylint: disable=protected-access
                        self._response_bytes += delta_bytes
                        self._response_chunks += 1
                        retained = True
            finally:
                self._discard_prepared_response_item(item.item_id)
                async with self._lock:
                    if not retained and not self._sender.ending:
                        item._send_in_flight = False  # pylint: disable=protected-access
                if reserved and not retained:
                    self._release_output_bytes(delta_bytes)

    async def _send_item_done(
        self,
        item: VoiceTextItem,
        *,
        voice: Mapping[str, Any] | None,
    ) -> None:
        voice_payload = normalize_voice(voice)
        async with self._send_lock:
            async with self._lock:
                self._prepare_item_locked(item)
                if not item._started or not item._chunks:  # pylint: disable=protected-access
                    raise RuntimeError("send_text_done requires at least one preceding delta")
                if item._done:  # pylint: disable=protected-access
                    raise RuntimeError("The response item is already complete")
                fields: dict[str, Any] = {
                    "response_id": self._response_id,
                    "item_id": item.item_id,
                    "text": "".join(item._chunks),  # pylint: disable=protected-access
                }
                if voice_payload is not None:
                    fields["voice"] = voice_payload
            self._register_response_item(item.item_id)
            await self._sender.send("response.output_text.done", **fields)
            async with self._lock:
                item._done = True  # pylint: disable=protected-access

    async def _complete_callback(self) -> None:
        terminal_kind = "done"
        async with self._send_lock:
            async with self._lock:
                # A pending self-cancel is a terminal boundary: response.cancel is
                # already on the wire and the bridge is arbitrating the outcome, so
                # auto-completion must not emit response.done (or an SDK error for an
                # incomplete item) as a second terminal.
                if self._terminal or self._cancel_pending or self._sender.ending:
                    self._sealed = True
                    return
                incomplete = (
                    not self._wire_opened
                    or not self._items
                    or any(not item._done for item in self._items)  # pylint: disable=protected-access
                )
            if incomplete:
                prepared = self._prepare_frame(
                    "error",
                    code="handler_error",
                    message="Voice turn callback returned without complete output or decline",
                    response_id=self._response_id,
                )
                await self._ensure_open()
            else:
                prepared = self._prepare_frame("response.done", response_id=self._response_id)
            async with self._lock:
                if self._terminal or self._cancel_pending or self._sender.ending:
                    self._sealed = True
                    return
                self._claim_local_terminal_locked()
            if incomplete:
                try:
                    await self._emit_sdk_error(prepared)
                except VoiceBridgeConnectionClosedError:
                    if self._terminal or self._sender.ending:
                        return
                    raise
                terminal_kind = "error"
            else:
                try:
                    await self._send_prepared_committed(prepared)
                except VoiceBridgeConnectionClosedError:
                    if self._terminal or self._sender.ending:
                        return
                    raise
        await self._notify_response_completed(terminal_kind)

    async def _fail_callback(self) -> None:
        async with self._send_lock:
            async with self._lock:
                # As in _complete_callback, a pending self-cancel is a terminal
                # boundary; do not emit a response-scoped error while response.cancel
                # is still being arbitrated by the bridge.
                if self._terminal or self._cancel_pending or self._sender.ending:
                    self._sealed = True
                    return
            prepared = self._prepare_frame(
                "error",
                code="handler_error",
                message="Voice turn callback failed",
                response_id=self._response_id,
            )
            await self._ensure_open()
            async with self._lock:
                if self._terminal or self._cancel_pending or self._sender.ending:
                    self._sealed = True
                    return
                self._claim_local_terminal_locked()
            try:
                await self._emit_sdk_error(prepared)
            except VoiceBridgeConnectionClosedError:
                if self._terminal or self._sender.ending:
                    return
                raise
        await self._notify_response_completed("error")

    async def _mark_terminal(self) -> None:
        async with self._lock:
            self._terminal = True
            self._sealed = True
            self._cancel_pending = False
            self._cancellation._cancel()
            self._release_output_buffers_locked()

    def _release_output_buffers(self) -> None:
        # Free the accumulated per-item text once the response is retained for late
        # reconciliation. Timeout/barge-in correlation only needs response/item
        # identity and terminal state (see _owns_item_id / _find_response_locked),
        # never the emitted text, so keeping the chunks (up to _MAX_RESPONSE_BYTES
        # per response across _MAX_RECENT_RESPONSES cached entries) would let a long
        # connection pin large amounts of memory. Item ids and _started are kept.
        #
        # Safety: this is synchronous (no await) so it runs atomically on the event
        # loop, and every caller invokes it only after the response is terminal
        # (_remember_response_locked is reached post-terminal). Once terminal, the
        # send paths reject further output at _ensure_writable_locked, so no commit
        # can re-grow _chunks after release. It therefore does not need _lock, which
        # cannot be awaited from the synchronous _state_lock context of the caller.
        self._release_output_buffers_locked()

    def _release_output_buffers_locked(self) -> None:
        released_bytes = self._response_bytes
        for item in self._items:
            item._chunks = []  # pylint: disable=protected-access
        self._response_bytes = 0
        self._response_chunks = 0
        if released_bytes:
            self._release_output_bytes(released_bytes)

    def _reserve_output_bytes(self, size: int) -> None:
        reserve = getattr(self._sender, "reserve_output_bytes", None)
        if reserve is not None:
            reserve(size)

    def _register_response_item(self, item_id: str) -> None:
        prepare = getattr(self._sender, "prepare_response_item", None)
        if prepare is not None:
            prepare(self._response_id, item_id)
            return
        register = getattr(self._sender, "register_response_item", None)
        if register is not None:
            register(self._response_id, item_id)

    def _discard_prepared_response_item(self, item_id: str) -> None:
        discard = getattr(self._sender, "discard_response_item", None)
        if discard is not None:
            discard(self._response_id, item_id)

    def _release_output_bytes(self, size: int) -> None:
        release = getattr(self._sender, "release_output_bytes", None)
        if release is not None:
            release(size)

    def _claim_local_terminal_locked(self, *, cancel: bool = False) -> None:
        self._terminal = True
        self._sealed = True
        self._cancel_pending = False
        if cancel:
            self._cancellation._cancel()
        self._release_output_buffers_locked()

    async def _mark_accepted(self) -> None:
        async with self._lock:
            if self._terminal:
                raise VoiceBridgeConnectionClosedError("The proactive response is terminal")
            self._accepted = True

    def _owns_item_id(self, item_id: str) -> bool:
        return any(item.item_id == item_id and (item._started or item._send_in_flight) for item in self._items)

    def _get_simple_item(self, *, create: bool = True) -> VoiceTextItem:
        self._ensure_locally_writable()
        if self._advanced_items:
            raise RuntimeError("Cannot mix simple response helpers with new_text_item")
        if self._simple_item is None:
            if not create:
                raise RuntimeError("send_text_done requires at least one preceding delta")
            self._simple_item = VoiceTextItem._create(self, new_id("it"))
            self._items.append(self._simple_item)
        return self._simple_item

    async def _drain_pending_send(self) -> None:
        # Block until any in-flight output operation on this response has fully
        # completed its wire write and committed. The turn coordinator awaits this
        # (bounded) before cancelling the customer task so a winning terminal write
        # still reaches the wire. Must be called from a task other than the one
        # holding _send_lock (the coordinator, not the customer callback).
        async with self._send_lock:
            return

    async def _ensure_open(self) -> None:
        # Callers must hold _send_lock (never _lock) so the response.created write
        # happens off the state lock and the receive pump's _mark_terminal() path
        # is never blocked by a stalled open.
        async with self._lock:
            if self._wire_opened:
                return
        opened = await self._sender.open_response(self._response_id, self._in_reply_to)
        async with self._lock:
            if opened:
                self._wire_opened = True
            else:
                self._terminal = True
                self._sealed = True
                self._cancellation._cancel()
        if not opened:
            raise VoiceBridgeConnectionClosedError("The voice response lost terminal arbitration")

    def _prepare_item_locked(self, item: VoiceTextItem) -> None:
        self._ensure_writable_locked()
        if item not in self._items:
            raise RuntimeError("Text item does not belong to this response")
        index = self._items.index(item)
        if any(not previous._done for previous in self._items[:index]):  # pylint: disable=protected-access
            raise RuntimeError("Complete the previous response item first")

    async def _emit_sdk_error(self, prepared: _PreparedFrame) -> None:
        # Callers must hold _send_lock (never _lock); the wire writes happen off
        # the state lock.
        await self._ensure_open()
        await self._send_prepared_committed(prepared)

    def _prepare_frame(self, message_type: str, **fields: Any) -> _PreparedFrame:
        return self._sender.prepare_frame(message_type, **fields)

    async def _send_prepared_committed(self, prepared: _PreparedFrame) -> None:
        await self._sender.send_prepared(prepared, state_committed=True)

    async def _notify_response_completed(self, terminal_kind: str) -> None:
        completion = asyncio.create_task(
            self._sender.response_completed(self._response_id, terminal_kind),
            name="voice_response_completed",
        )
        cancellation: asyncio.CancelledError | None = None
        while not completion.done():
            try:
                await asyncio.shield(completion)
            except asyncio.CancelledError as exc:
                # The terminal frame already reached the transport. Keep the
                # host ownership transition alive even if the customer await is
                # cancelled, then propagate cancellation after bookkeeping.
                cancellation = exc
        await completion
        if cancellation is not None:
            raise cancellation

    def _ensure_writable_locked(self) -> None:
        self._ensure_locally_writable()
        if not self._accepted:
            raise RuntimeError("Proactive output is unavailable before response.accepted")

    def _ensure_locally_writable(self) -> None:
        if self._terminal or self._sealed or self._sender.ending:
            raise VoiceBridgeConnectionClosedError("The voice response is terminal")
        if self._cancel_pending:
            raise VoiceBridgeConnectionClosedError("The voice response is awaiting cancellation")


@experimental
class VoiceSession:
    """Connection-scoped context and controls exposed to callbacks."""

    _sender: _ConnectionSender
    _start: SessionStartEvent

    def __init__(self) -> None:
        raise TypeError("VoiceSession instances are created by VoiceAgentServerHost")

    @classmethod
    def _create(cls, sender: _ConnectionSender, start: SessionStartEvent) -> "VoiceSession":
        instance = object.__new__(cls)
        instance._sender = sender
        instance._start = start
        return instance

    @property
    def reconnect(self) -> bool:
        """Whether this transport reattaches the logical session.

        :return: ``True`` for a same-session transport reattach.
        :rtype: bool
        """
        return self._start.reconnect

    @property
    def greeting(self) -> str | None:
        """Return the bridge-owned initial greeting.

        :return: Greeting or ``None``.
        :rtype: str or None
        """
        return self._start.greeting

    @property
    def caller(self) -> Mapping[str, Any] | None:
        """Return deeply read-only, untrusted caller metadata.

        :return: Caller metadata or ``None``.
        :rtype: Mapping[str, Any] or None
        """
        return self._start.caller

    @property
    def no_input_timeout_ms(self) -> int | None:
        """Return the configured silence threshold.

        :return: Timeout in milliseconds or ``None``.
        :rtype: int or None
        """
        return self._start.no_input_timeout_ms

    @property
    def response_timeouts(self) -> ResponseTimeouts:
        """Return effective response deadlines.

        :return: Effective response deadlines.
        :rtype: ResponseTimeouts
        """
        return self._start.response_timeouts

    async def start_proactive_response(
        self,
        *,
        admission_timeout_ms: int = 60_000,
        supersede_key: str | None = None,
    ) -> VoiceResponse:
        """Request proactive admission and return a writable accepted response.

        The Bridge enforces the admission deadline while it waits for a
        barge-safe point. The SDK waits for ``response.accepted``,
        ``response.dropped``, connection termination, or caller cancellation;
        it does not run a second local admission timer.

        :keyword admission_timeout_ms: Maximum time, from 1 through 60000 ms,
            that the Bridge may buffer this request while waiting for a
            barge-safe admission point.
        :paramtype admission_timeout_ms: int
        :keyword supersede_key: Optional non-empty logical notification key.
        :paramtype supersede_key: str or None
        :return: Accepted proactive response.
        :rtype: VoiceResponse
        :raises VoiceProactiveResponseDroppedError: If the bridge drops admission.
        """
        if (
            not isinstance(admission_timeout_ms, int)
            or isinstance(admission_timeout_ms, bool)
            or not 1 <= admission_timeout_ms <= 60_000
        ):
            raise ValueError("admission_timeout_ms must be between 1 and 60000")
        if supersede_key is not None:
            supersede_key = _require_string(supersede_key, "supersede_key")
            if not supersede_key:
                raise ValueError("supersede_key must be non-empty")
        return await self._sender.start_proactive_response(
            admission_timeout_ms=admission_timeout_ms,
            supersede_key=supersede_key,
        )

    async def end_call(
        self,
        *,
        reason: str,
        mode: Literal["drain", "immediate"] = "drain",
    ) -> None:
        """Request call termination.

        :keyword reason: Non-empty open-enum reason.
        :paramtype reason: str
        :keyword mode: ``drain`` queued audio, or end immediately with ``immediate``.
        :paramtype mode: str
        """
        reason = _require_string(reason, "reason")
        if not reason:
            raise ValueError("reason must be a non-empty string")
        if mode not in ("drain", "immediate"):
            raise ValueError("mode must be 'drain' or 'immediate'")
        await self._sender.end_call(reason, mode)

    async def cancel_dtmf_collection(self, collection_id: str) -> None:
        """Cancel one pending or active DTMF collection.

        :param collection_id: SDK-allocated ``dc_`` collection identifier.
        :type collection_id: str
        """
        collection_id = _require_string(collection_id, "collection_id")
        if not collection_id.startswith("dc_") or len(collection_id) <= 3:
            raise ValueError("collection_id must start with dc_")
        await self._sender.cancel_dtmf_collection(collection_id)

    async def report_error(self, *, code: str, message: str) -> None:
        """Report a terminal session-scoped agent failure.

        :keyword code: Machine-readable open-enum code.
        :paramtype code: str
        :keyword message: Bounded diagnostic message; do not include sensitive content.
        :paramtype message: str
        """
        await self._sender.report_session_error(
            safe_code(code, "agent_error"),
            safe_message(message, "Voice session failed"),
        )


def _require_string(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    return value


def _require_positive_int(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _text_size(value: str) -> int:
    size = len(value.encode("utf-8"))
    if size > _MAX_OUTPUT_ITEM_BYTES:
        raise ValueError("An output item exceeds the maximum encoded text size")
    return size
