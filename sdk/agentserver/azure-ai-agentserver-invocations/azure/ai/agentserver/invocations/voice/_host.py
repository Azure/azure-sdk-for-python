# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Typed Voice Live bridge host built on the invocations_ws transport."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import hashlib
import inspect
import logging
import sys
import threading
import time
import weakref
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Coroutine, Mapping, Sequence
from dataclasses import dataclass
from dataclasses import fields as dataclass_fields, is_dataclass, replace
from types import MappingProxyType
from typing import Any, Literal, Optional

from opentelemetry import metrics
from starlette.routing import WebSocketRoute

from azure.ai.agentserver.core import experimental

from .._constants import InvocationsWSConstants
from .._invocation import InvocationAgentServerHost
from .._version import VERSION

from ._models import (
    BargeInEvent,
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
    _PreparedFrame,
    _estimate_frame_fields as _estimate_event_bytes,
    VoiceBridgeConnectionClosedError,
    VoiceBridgeProtocolError,
    VoiceProactiveResponseDroppedError,
    canonical_payload,
    decode_frame,
    new_id,
    optional_string,
    parse_handoff_failed,
    parse_response_timeout,
    parse_session_start,
    parse_user_message,
    prepare_frame as _prepare_protocol_frame,
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


def _metric_add(instrument: Any, value: int, attributes: Mapping[str, Any] | None = None) -> None:
    """Record one counter value without allowing telemetry to affect protocol control flow.

    :param instrument: Counter-like OpenTelemetry instrument.
    :type instrument: Any
    :param value: Counter increment.
    :type value: int
    :param attributes: Optional low-cardinality metric attributes.
    :type attributes: Mapping[str, Any] or None
    """
    try:
        instrument.add(value, attributes)
    except Exception:  # pylint: disable=broad-exception-caught
        logger.warning("Voice counter telemetry failed", exc_info=True)


def _metric_record(instrument: Any, value: float, attributes: Mapping[str, Any] | None = None) -> None:
    """Record one histogram value without allowing telemetry to affect protocol control flow.

    :param instrument: Histogram-like OpenTelemetry instrument.
    :type instrument: Any
    :param value: Histogram measurement.
    :type value: float
    :param attributes: Optional low-cardinality metric attributes.
    :type attributes: Mapping[str, Any] or None
    """
    try:
        instrument.record(value, attributes)
    except Exception:  # pylint: disable=broad-exception-caught
        logger.warning("Voice histogram telemetry failed", exc_info=True)


# VoiceResponse and _VoiceConnection are the public/internal halves of one
# runtime and intentionally drive each other's private terminal hooks.
# pylint: disable=protected-access

SessionStartCallback = Callable[[VoiceSession, SessionStartEvent], Awaitable[None]]
UserMessageCallback = Callable[[VoiceSession, UserMessageEvent, VoiceResponse], Awaitable[None]]
UserNoInputCallback = Callable[[VoiceSession, UserNoInputEvent, VoiceResponse], Awaitable[None]]
UserSpeechStartedCallback = Callable[[VoiceSession, UserSpeechStartedEvent], Awaitable[None]]
HandoffFailedCallback = Callable[[VoiceSession, HandoffFailedEvent, VoiceResponse], Awaitable[None]]
BargeInCallback = Callable[[VoiceSession, BargeInEvent], Awaitable[None]]
ResponseTimeoutCallback = Callable[[VoiceSession, ResponseTimeoutEvent], Awaitable[None]]
SessionEndCallback = Callable[[VoiceSession, SessionEndEvent], Awaitable[None]]

_MAX_CALLBACK_QUEUE = 128
_MAX_CALLBACK_QUEUE_BYTES = 8 * 1024 * 1024
_MAX_FRAME_BYTES = 1024 * 1024
_MAX_SEEN_MESSAGES = 4096
_MAX_ID_TOMBSTONES = 4096
_MAX_RECENT_RESPONSES = 64
_MAX_RESOLVED_PREFIXES = 64
_MAX_PENDING_PROACTIVE = 16
# Upper bound on customer tasks that were cancelled but keep running because the
# callback swallowed CancelledError. They are retained (tracked) until they
# actually complete; this cap makes a hostile or broken callback unable to
# accumulate such tasks without limit.
_MAX_RESISTANT_TASKS = 64
_MAX_GLOBAL_CUSTOMER_TASKS = 1024
_MAX_GLOBAL_CALLBACK_QUEUE_BYTES = 64 * 1024 * 1024
_MAX_GLOBAL_CUSTOMER_TASK_BYTES = 64 * 1024 * 1024
_MESSAGE_IDENTITY_BYTES = 192
_INPUT_IDENTITY_BYTES = 256
_RESPONSE_IDENTITY_BYTES = 160
_RESPONSE_ITEM_IDENTITY_BYTES = 128
_MAX_CONNECTION_IDENTITY_BYTES = 4 * 1024 * 1024
_MAX_GLOBAL_IDENTITY_BYTES = 64 * 1024 * 1024
_CLEANUP_TIMEOUT_SECONDS = 5.0
_GLOBAL_CUSTOMER_TASKS: set[asyncio.Task[None]] = set()
_GLOBAL_CUSTOMER_TASK_BYTES_BY_TASK: dict[asyncio.Task[None], int] = {}
_GLOBAL_SESSION_RETENTION_BY_TASK: dict[asyncio.Task[None], _SessionRetentionLease] = {}
_GLOBAL_CUSTOMER_TASKS_LOCK = threading.Lock()
_GLOBAL_CUSTOMER_TASK_RESERVATIONS = 0
_GLOBAL_CALLBACK_QUEUE_BYTES = 0
_GLOBAL_CUSTOMER_TASK_BYTES = 0
_GLOBAL_IDENTITY_BYTES = 0
_AGENT_TO_BRIDGE_TYPES = {
    "session.ready",
    "session.rejected",
    "response.created",
    "response.none",
    "response.output_text.delta",
    "response.output_text.done",
    "response.done",
    "response.cancel",
    "handoff",
    "end_call",
    "error",
}


class _SessionRetentionLease:
    """One global byte reservation shared by a connection and its customer tasks."""

    def __init__(self, retained_bytes: int) -> None:
        self.retained_bytes = retained_bytes
        self.references = 1
        self.released = False


def _reserve_session_retention(retained_bytes: int) -> _SessionRetentionLease | None:
    """Reserve one connection's startup context in the aggregate customer budget.

    :param retained_bytes: Estimated bytes retained by the live session graph.
    :type retained_bytes: int
    :return: New connection-owned lease, or ``None`` when the budget is full.
    :rtype: _SessionRetentionLease or None
    """
    global _GLOBAL_CUSTOMER_TASK_BYTES  # pylint: disable=global-statement
    with _GLOBAL_CUSTOMER_TASKS_LOCK:
        if _GLOBAL_CUSTOMER_TASK_BYTES + retained_bytes > _MAX_GLOBAL_CUSTOMER_TASK_BYTES:
            return None
        _GLOBAL_CUSTOMER_TASK_BYTES += retained_bytes
        return _SessionRetentionLease(retained_bytes)


def _release_session_retention_locked(lease: _SessionRetentionLease) -> None:
    """Release one lease reference while the global customer-task lock is held.

    :param lease: Shared startup-context byte reservation.
    :type lease: _SessionRetentionLease
    """
    global _GLOBAL_CUSTOMER_TASK_BYTES  # pylint: disable=global-statement
    if lease.released or lease.references <= 0:
        raise RuntimeError("Voice session retention lease accounting underflow")
    lease.references -= 1
    if lease.references == 0:
        _GLOBAL_CUSTOMER_TASK_BYTES -= lease.retained_bytes
        if _GLOBAL_CUSTOMER_TASK_BYTES < 0:
            raise RuntimeError("Voice global customer byte accounting underflow")
        lease.released = True


def _release_session_retention(lease: _SessionRetentionLease) -> None:
    """Release one connection-owned startup-context lease reference.

    :param lease: Shared startup-context byte reservation.
    :type lease: _SessionRetentionLease
    """
    with _GLOBAL_CUSTOMER_TASKS_LOCK:
        _release_session_retention_locked(lease)


def _release_global_customer_task(completed: asyncio.Task[None]) -> None:
    """Release one process-level customer/finalizer task reservation.

    :param completed: Completed tracked task.
    :type completed: asyncio.Task[None]
    """
    global _GLOBAL_CUSTOMER_TASK_RESERVATIONS  # pylint: disable=global-statement
    global _GLOBAL_CUSTOMER_TASK_BYTES  # pylint: disable=global-statement
    with _GLOBAL_CUSTOMER_TASKS_LOCK:
        if completed not in _GLOBAL_CUSTOMER_TASKS:
            return
        _GLOBAL_CUSTOMER_TASKS.discard(completed)
        _GLOBAL_CUSTOMER_TASK_RESERVATIONS -= 1
        _GLOBAL_CUSTOMER_TASK_BYTES -= _GLOBAL_CUSTOMER_TASK_BYTES_BY_TASK.pop(completed, 0)
        session_retention = _GLOBAL_SESSION_RETENTION_BY_TASK.pop(completed, None)
        if session_retention is not None:
            _release_session_retention_locked(session_retention)
    if not completed.cancelled():
        completed.exception()


def _reserve_global_callback_queue_bytes(size: int) -> bool:
    """Reserve process-wide callback-queue memory.

    :param size: Estimated retained bytes.
    :type size: int
    :return: Whether the reservation succeeded.
    :rtype: bool
    """
    global _GLOBAL_CALLBACK_QUEUE_BYTES  # pylint: disable=global-statement
    with _GLOBAL_CUSTOMER_TASKS_LOCK:
        if _GLOBAL_CALLBACK_QUEUE_BYTES + size > _MAX_GLOBAL_CALLBACK_QUEUE_BYTES:
            return False
        _GLOBAL_CALLBACK_QUEUE_BYTES += size
        return True


def _release_global_callback_queue_bytes(size: int) -> None:
    """Release process-wide callback-queue memory.

    :param size: Previously reserved retained bytes.
    :type size: int
    """
    global _GLOBAL_CALLBACK_QUEUE_BYTES  # pylint: disable=global-statement
    with _GLOBAL_CUSTOMER_TASKS_LOCK:
        _GLOBAL_CALLBACK_QUEUE_BYTES -= size
        if _GLOBAL_CALLBACK_QUEUE_BYTES < 0:
            raise RuntimeError("Voice global callback queue byte accounting underflow")


def _reserve_global_output_bytes(size: int) -> bool:
    """Reserve response text against the process-wide customer-memory budget.

    :param size: Encoded text bytes to reserve.
    :type size: int
    :return: Whether the reservation succeeded.
    :rtype: bool
    """
    global _GLOBAL_CUSTOMER_TASK_BYTES  # pylint: disable=global-statement
    with _GLOBAL_CUSTOMER_TASKS_LOCK:
        if _GLOBAL_CUSTOMER_TASK_BYTES + size > _MAX_GLOBAL_CUSTOMER_TASK_BYTES:
            return False
        _GLOBAL_CUSTOMER_TASK_BYTES += size
        return True


def _release_global_output_bytes(size: int) -> None:
    """Release response text from the process-wide customer-memory budget.

    :param size: Previously reserved encoded text bytes.
    :type size: int
    """
    global _GLOBAL_CUSTOMER_TASK_BYTES  # pylint: disable=global-statement
    with _GLOBAL_CUSTOMER_TASKS_LOCK:
        _GLOBAL_CUSTOMER_TASK_BYTES -= size
        if _GLOBAL_CUSTOMER_TASK_BYTES < 0:
            raise RuntimeError("Voice global customer byte accounting underflow")


def _reserve_global_identity_bytes(size: int) -> bool:
    """Reserve fixed-cost identity memory across active connections.

    :param size: Conservative retained-memory cost to reserve.
    :type size: int
    :return: Whether the process-wide identity budget has capacity.
    :rtype: bool
    """
    global _GLOBAL_IDENTITY_BYTES  # pylint: disable=global-statement
    with _GLOBAL_CUSTOMER_TASKS_LOCK:
        if _GLOBAL_IDENTITY_BYTES + size > _MAX_GLOBAL_IDENTITY_BYTES:
            return False
        _GLOBAL_IDENTITY_BYTES += size
        return True


def _release_global_identity_bytes(size: int) -> None:
    """Release identity memory from the process-wide budget.

    :param size: Previously reserved conservative retained-memory cost.
    :type size: int
    """
    global _GLOBAL_IDENTITY_BYTES  # pylint: disable=global-statement
    if not size:
        return
    with _GLOBAL_CUSTOMER_TASKS_LOCK:
        _GLOBAL_IDENTITY_BYTES -= size
        if _GLOBAL_IDENTITY_BYTES < 0:
            raise RuntimeError("Voice global identity byte accounting underflow")


def _observe_future_completion(completed: asyncio.Future[Any]) -> None:
    """Retrieve internal Future exceptions even when the public waiter left.

    :param completed: Completed internal correlation Future.
    :type completed: asyncio.Future[Any]
    """
    if not completed.cancelled():
        completed.exception()


@dataclass(frozen=True)
class _RuntimeFailure:
    """Typed connection-supervision failure preserving its close semantics."""

    reason: str
    close_code: int

    def to_exception(self) -> Exception:
        """Create an exception suitable for the host's close-code mapping.

        :return: Protocol or internal exception carrying the failure semantics.
        :rtype: Exception
        """
        if self.close_code == 1008:
            return VoiceBridgeProtocolError(self.reason, close_code=1008)
        return RuntimeError(self.reason)


@dataclass(frozen=True)
class _CallbackWork:
    kind: str
    event: Any
    callback: Callable[..., Awaitable[None]] | None
    response: VoiceResponse | None = None
    item_id: str | None = None
    payload_bytes: int = 0


@dataclass(frozen=True)
class _RecentResponse:
    """Compact late-terminal reconciliation state without retaining output objects."""

    response_id: str
    response_ref: weakref.ReferenceType[VoiceResponse]


@dataclass(frozen=True)
class _ResolvedPrefix:
    """Compact response state retained for one late input-prefix timeout."""

    response_id: str
    opened_response: bool
    response_ref: weakref.ReferenceType[VoiceResponse]


class _DigestPrefixMap(OrderedDict[tuple[bytes, ...], _ResolvedPrefix | tuple[VoiceResponse, bool]]):
    """Digest-keyed map accepting raw string prefixes for compatibility lookup."""

    def __contains__(self, key: object) -> bool:
        if isinstance(key, tuple) and key and all(isinstance(item, str) for item in key):
            key = tuple(_identity_digest(item) for item in key)
        return super().__contains__(key)


def _identity_digest(value: str) -> bytes:
    """Return the fixed-size binary identity used by exact ledgers.

    :param value: Protocol identifier to digest.
    :type value: str
    :return: Binary SHA-256 digest.
    :rtype: bytes
    """
    return hashlib.sha256(value.encode("utf-8")).digest()


class _IdentityBudget:
    """One byte budget shared by every exact identity ledger on a connection."""

    def __init__(self, max_bytes: int, *, on_limit: Callable[[str, int], None] | None = None) -> None:
        self._max_bytes = max_bytes
        self._used_bytes = 0
        self._on_limit = on_limit
        self._failure: tuple[str, int] | None = None

    @property
    def used_bytes(self) -> int:
        return self._used_bytes

    def reserve(self, size: int) -> None:
        if self._failure is not None:
            self._raise_failure(*self._failure)
        if self._used_bytes + size > self._max_bytes:
            self.fail("Voice connection identity byte budget exceeded", 1008)
        if not _reserve_global_identity_bytes(size):
            self.fail("Voice global identity byte budget exceeded", 1011)
        self._used_bytes += size

    def release(self, size: int) -> None:
        self._used_bytes -= size
        if self._used_bytes < 0:
            raise RuntimeError("Voice connection identity byte accounting underflow")
        _release_global_identity_bytes(size)

    def fail(self, reason: str, close_code: int) -> None:
        if self._failure is None:
            self._failure = (reason, close_code)
            if self._on_limit is not None:
                self._on_limit(reason, close_code)
        self._raise_failure(*self._failure)

    @staticmethod
    def _raise_failure(reason: str, close_code: int) -> None:
        if close_code == 1008:
            raise VoiceBridgeProtocolError(reason, close_code=1008)
        raise RuntimeError(reason)


class _ExactIdSet:
    """Monotonic exact identity set storing only binary SHA-256 digests."""

    def __init__(
        self,
        max_size: int,
        *,
        name: str,
        budget: _IdentityBudget,
    ) -> None:
        self._max_size = max_size
        self._name = name
        self._budget = budget
        self._values: set[bytes] = set()

    def __contains__(self, value: object) -> bool:
        return isinstance(value, str) and _identity_digest(value) in self._values

    def __len__(self) -> int:
        return len(self._values)

    def add(self, value: str) -> None:
        digest = _identity_digest(value)
        if digest in self._values:
            return
        if len(self._values) >= self._max_size:
            self._budget.fail(f"Voice {self._name} budget exceeded", 1008)
        self._budget.reserve(_INPUT_IDENTITY_BYTES)
        try:
            self._values.add(digest)
        except BaseException:
            self._budget.release(_INPUT_IDENTITY_BYTES)
            raise

    def clear(self) -> None:
        size = len(self._values) * _INPUT_IDENTITY_BYTES
        self._values.clear()
        self._budget.release(size)


@dataclass
class _ResponseIdentityState:
    """Connection-lifetime protocol state for one SDK-owned response id."""

    terminal: bool = False
    playback_outcome: bool = False
    abandoned_proactive_cancel: bool = False
    has_output: bool = False


class _ResponseIdentityLedger:
    """Exact response identity ledger with one reservation per response id."""

    def __init__(
        self,
        max_size: int,
        *,
        max_abandoned: int,
        budget: _IdentityBudget,
    ) -> None:
        self._max_size = max_size
        self._max_abandoned = max_abandoned
        self._budget = budget
        self._records: dict[bytes, _ResponseIdentityState] = {}
        self._item_owners: dict[bytes, bool] = {}
        self._abandoned_count = 0

    def ensure_response(self, response_id: str) -> bool:
        """Materialize an exact response identity once for the connection.

        :param response_id: SDK-owned response identifier.
        :type response_id: str
        :return: Whether a new record was created.
        :rtype: bool
        """
        digest = _identity_digest(response_id)
        if digest in self._records:
            return False
        if len(self._records) >= self._max_size:
            self._budget.fail("Voice response identity budget exceeded", 1008)
        self._budget.reserve(_RESPONSE_IDENTITY_BYTES)
        try:
            self._records[digest] = _ResponseIdentityState()
        except BaseException:
            self._budget.release(_RESPONSE_IDENTITY_BYTES)
            raise
        return True

    def is_seen(self, response_id: str) -> bool:
        """Return whether a response identity exists for this connection.

        :param response_id: SDK-owned response identifier.
        :type response_id: str
        :return: Whether the response identifier was materialized.
        :rtype: bool
        """
        return _identity_digest(response_id) in self._records

    def is_terminal(self, response_id: str) -> bool:
        """Return whether a response reached a terminal protocol state.

        :param response_id: SDK-owned response identifier.
        :type response_id: str
        :return: Whether terminal state was claimed.
        :rtype: bool
        """
        state = self._records.get(_identity_digest(response_id))
        return state is not None and state.terminal

    def claim_terminal(self, response_id: str) -> bool:
        """Atomically claim the first terminal transition for one response.

        :param response_id: SDK-owned response identifier.
        :type response_id: str
        :return: Whether this call won the terminal transition.
        :rtype: bool
        """
        self.ensure_response(response_id)
        state = self._records[_identity_digest(response_id)]
        if state.terminal:
            return False
        state.terminal = True
        return True

    def has_playback_outcome(self, response_id: str) -> bool:
        """Return whether playback reconciliation already completed.

        :param response_id: SDK-owned response identifier.
        :type response_id: str
        :return: Whether a playback outcome was recorded.
        :rtype: bool
        """
        state = self._records.get(_identity_digest(response_id))
        return state is not None and state.playback_outcome

    def mark_playback_outcome(self, response_id: str) -> bool:
        """Mark playback reconciliation and report whether it was new.

        :param response_id: SDK-owned response identifier.
        :type response_id: str
        :return: Whether a new playback marker was set.
        :rtype: bool
        """
        self.ensure_response(response_id)
        state = self._records[_identity_digest(response_id)]
        if state.playback_outcome:
            return False
        state.playback_outcome = True
        return True

    def clear_playback_outcome(self, response_id: str, *, strict: bool = False) -> None:
        """Clear a playback marker without releasing response identity.

        :param response_id: SDK-owned response identifier.
        :type response_id: str
        :keyword strict: Raise when no playback marker exists.
        :paramtype strict: bool
        """
        state = self._records.get(_identity_digest(response_id))
        if state is None or not state.playback_outcome:
            if strict:
                raise KeyError(response_id)
            return
        state.playback_outcome = False

    def is_abandoned(self, response_id: str) -> bool:
        """Return whether proactive admission was abandoned by its caller.

        :param response_id: SDK-owned response identifier.
        :type response_id: str
        :return: Whether the admission awaiter abandoned this response.
        :rtype: bool
        """
        state = self._records.get(_identity_digest(response_id))
        return state is not None and state.abandoned_proactive_cancel

    def mark_abandoned(self, response_id: str) -> bool:
        """Mark one abandoned proactive admission under its focused budget.

        :param response_id: SDK-owned response identifier.
        :type response_id: str
        :return: Whether a new abandoned-admission flag was set.
        :rtype: bool
        """
        digest = _identity_digest(response_id)
        state = self._records.get(digest)
        if state is not None and state.abandoned_proactive_cancel:
            return False
        if self._abandoned_count >= self._max_abandoned:
            self._budget.fail("Voice abandoned proactive cancellation budget exceeded", 1008)
        if state is None:
            self.ensure_response(response_id)
            state = self._records[digest]
        state.abandoned_proactive_cancel = True
        self._abandoned_count += 1
        return True

    def clear_abandoned(self, response_id: str, *, strict: bool = False) -> None:
        """Clear an abandoned-admission flag without forgetting response identity.

        :param response_id: SDK-owned response identifier.
        :type response_id: str
        :keyword strict: Raise when no abandoned-admission flag exists.
        :paramtype strict: bool
        """
        state = self._records.get(_identity_digest(response_id))
        if state is None or not state.abandoned_proactive_cancel:
            if strict:
                raise KeyError(response_id)
            return
        state.abandoned_proactive_cancel = False
        self._abandoned_count -= 1

    def register_item(self, response_id: str, item_id: str) -> None:
        """Register one output item as transport committed.

        :param response_id: Owning response identifier.
        :type response_id: str
        :param item_id: Output item identifier.
        :type item_id: str
        """
        self.prepare_item(response_id, item_id)
        self.commit_item(response_id, item_id)

    def prepare_item(self, response_id: str, item_id: str) -> None:
        """Reserve one output item before its first possible transport attempt.

        :param response_id: Owning response identifier.
        :type response_id: str
        :param item_id: Output item identifier.
        :type item_id: str
        """
        self.ensure_response(response_id)
        owner_digest = hashlib.sha256(_identity_digest(response_id) + _identity_digest(item_id)).digest()
        if owner_digest in self._item_owners:
            return
        self._budget.reserve(_RESPONSE_ITEM_IDENTITY_BYTES)
        try:
            self._item_owners[owner_digest] = False
        except BaseException:
            self._budget.release(_RESPONSE_ITEM_IDENTITY_BYTES)
            raise

    def commit_item(self, response_id: str, item_id: str) -> None:
        """Commit item ownership immediately before entering transport.

        :param response_id: Owning response identifier.
        :type response_id: str
        :param item_id: Output item identifier.
        :type item_id: str
        """
        response_digest = _identity_digest(response_id)
        owner_digest = hashlib.sha256(response_digest + _identity_digest(item_id)).digest()
        if owner_digest not in self._item_owners:
            self.prepare_item(response_id, item_id)
        self._item_owners[owner_digest] = True
        self._records[response_digest].has_output = True

    def discard_prepared_item(self, response_id: str, item_id: str) -> None:
        """Release an item after a proven pre-transport failure.

        :param response_id: Owning response identifier.
        :type response_id: str
        :param item_id: Output item identifier.
        :type item_id: str
        """
        owner_digest = hashlib.sha256(_identity_digest(response_id) + _identity_digest(item_id)).digest()
        if self._item_owners.get(owner_digest) is False:
            self._item_owners.pop(owner_digest)
            self._budget.release(_RESPONSE_ITEM_IDENTITY_BYTES)

    def owns_item(self, response_id: str, item_id: str) -> bool:
        """Return whether the response/item pair reached transport.

        :param response_id: Owning response identifier.
        :type response_id: str
        :param item_id: Output item identifier.
        :type item_id: str
        :return: Whether ownership reached the transport boundary.
        :rtype: bool
        """
        owner_digest = hashlib.sha256(_identity_digest(response_id) + _identity_digest(item_id)).digest()
        return self._item_owners.get(owner_digest) is True

    def has_output(self, response_id: str) -> bool:
        """Return whether any item for this response reached transport.

        :param response_id: Response identifier.
        :type response_id: str
        :return: Whether any output identity was committed.
        :rtype: bool
        """
        state = self._records.get(_identity_digest(response_id))
        return state is not None and state.has_output

    def count(self, flag: Literal["seen", "terminal", "playback", "abandoned"]) -> int:
        if flag == "seen":
            return len(self._records)
        if flag == "terminal":
            return sum(1 for state in self._records.values() if state.terminal)
        if flag == "playback":
            return sum(1 for state in self._records.values() if state.playback_outcome)
        return sum(1 for state in self._records.values() if state.abandoned_proactive_cancel)

    def clear_flag(self, flag: Literal["playback", "abandoned"]) -> None:
        """Clear one compatibility-view flag while retaining exact identities.

        :param flag: Non-terminal lifecycle projection to clear.
        :type flag: Literal["playback", "abandoned"]
        """
        if flag == "playback":
            for state in self._records.values():
                state.playback_outcome = False
        else:
            for state in self._records.values():
                state.abandoned_proactive_cancel = False
            self._abandoned_count = 0

    def clear_all(self) -> None:
        """Release every response identity reservation exactly once."""
        size = len(self._records) * _RESPONSE_IDENTITY_BYTES + len(self._item_owners) * _RESPONSE_ITEM_IDENTITY_BYTES
        self._records.clear()
        self._item_owners.clear()
        self._abandoned_count = 0
        self._budget.release(size)


class _ResponseIdentityView:
    """Set-compatible projection over one response identity ledger flag."""

    def __init__(
        self,
        ledger: _ResponseIdentityLedger,
        flag: Literal["seen", "terminal", "playback", "abandoned"],
    ) -> None:
        self._ledger = ledger
        self._flag = flag
        self._max_size = (
            ledger._max_abandoned if flag == "abandoned" else ledger._max_size
        )  # pylint: disable=protected-access

    def __contains__(self, value: object) -> bool:
        if not isinstance(value, str):
            return False
        if self._flag == "seen":
            return self._ledger.is_seen(value)
        if self._flag == "terminal":
            return self._ledger.is_terminal(value)
        if self._flag == "playback":
            return self._ledger.has_playback_outcome(value)
        return self._ledger.is_abandoned(value)

    def __len__(self) -> int:
        return self._ledger.count(self._flag)

    def add(self, value: str) -> None:
        if self._flag == "seen":
            self._ledger.ensure_response(value)
        elif self._flag == "terminal":
            self._ledger.claim_terminal(value)
        elif self._flag == "playback":
            self._ledger.mark_playback_outcome(value)
        else:
            self._ledger.mark_abandoned(value)

    def discard(self, value: str) -> None:
        if self._flag == "playback":
            self._ledger.clear_playback_outcome(value)
        elif self._flag == "abandoned":
            self._ledger.clear_abandoned(value)
        elif self._flag == "terminal":
            raise RuntimeError("Voice response terminal state is monotonic")

    def remove(self, value: str) -> None:
        if self._flag == "playback":
            self._ledger.clear_playback_outcome(value, strict=True)
        elif self._flag == "abandoned":
            self._ledger.clear_abandoned(value, strict=True)
        elif self._flag == "terminal":
            raise RuntimeError("Voice response terminal state is monotonic")
        elif value not in self:
            raise KeyError(value)

    def clear(self) -> None:
        if self._flag == "seen":
            self._ledger.clear_all()
        elif self._flag == "terminal":
            raise RuntimeError("Voice response terminal state is monotonic")
        else:
            assert self._flag in ("playback", "abandoned")
            self._ledger.clear_flag(self._flag)


class _ExactMessageLedger:
    """Exact message-id/payload digest ledger with no eviction false negatives."""

    def __init__(self, max_size: int, *, budget: _IdentityBudget) -> None:
        self._max_size = max_size
        self._budget = budget
        self._values: dict[bytes, bytes] = {}

    def __len__(self) -> int:
        return len(self._values)

    def get(self, key: bytes) -> bytes | None:
        """Return the payload digest previously associated with an id digest.

        :param key: Fixed-size message-id digest.
        :type key: bytes
        :return: Existing payload digest, or ``None`` when unseen.
        :rtype: bytes | None
        """
        return self._values.get(key)

    def add(self, key: bytes, value: bytes) -> None:
        """Add one exact message identity or fail before semantic dispatch.

        :param key: Fixed-size message-id digest.
        :type key: bytes
        :param value: Fixed-size canonical payload digest.
        :type value: bytes
        """
        if key in self._values:
            raise RuntimeError("Voice message identity was added twice")
        if len(self._values) >= self._max_size:
            self._budget.fail("Voice message dedupe budget exceeded", 1008)
        self._budget.reserve(_MESSAGE_IDENTITY_BYTES)
        try:
            self._values[key] = value
        except BaseException:
            self._budget.release(_MESSAGE_IDENTITY_BYTES)
            raise

    def clear(self) -> None:
        """Release all connection-scoped message identity reservations."""
        size = len(self._values) * _MESSAGE_IDENTITY_BYTES
        self._values.clear()
        self._budget.release(size)


@experimental
class VoiceAgentServerHost(InvocationAgentServerHost):  # pylint: disable=too-many-instance-attributes
    """AgentServer host implementing Voice Live Bridge Protocol 1.0."""

    def __init__(self, **kwargs: Any) -> None:
        self._on_session_start: Optional[SessionStartCallback] = None
        self._on_user_message: Optional[UserMessageCallback] = None
        self._on_user_no_input: Optional[UserNoInputCallback] = None
        self._on_user_speech_started: Optional[UserSpeechStartedCallback] = None
        self._on_handoff_failed: Optional[HandoffFailedCallback] = None
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

    def on_handoff_failed(self, fn: HandoffFailedCallback) -> HandoffFailedCallback:
        """Register the optional handoff recovery-turn callback.

        :param fn: Async response-producing recovery callback.
        :type fn: Callable[[VoiceSession, HandoffFailedEvent, VoiceResponse], Awaitable[None]]
        :return: Registered callback.
        :rtype: Callable[[VoiceSession, HandoffFailedEvent, VoiceResponse], Awaitable[None]]
        """
        self._on_handoff_failed = self._register_once("on_handoff_failed", self._on_handoff_failed, fn)
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
            on_handoff_failed=self._on_handoff_failed,
            on_barge_in=self._on_barge_in,
            on_response_timeout=self._on_response_timeout,
            on_session_end=self._on_session_end,
        )
        _metric_add(_ACTIVE_CONNECTIONS, 1)
        try:
            await connection.run()
        finally:
            _metric_add(_ACTIVE_CONNECTIONS, -1)


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
        on_handoff_failed: Optional[HandoffFailedCallback],
        on_barge_in: Optional[BargeInCallback],
        on_response_timeout: Optional[ResponseTimeoutCallback],
        on_session_end: Optional[SessionEndCallback],
    ) -> None:
        self._websocket = websocket
        self._on_session_start = on_session_start
        self._on_user_message = on_user_message
        self._on_user_no_input = on_user_no_input
        self._on_user_speech_started = on_user_speech_started
        self._on_handoff_failed = on_handoff_failed
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
        # worker. This Future carries immutable failure metadata as a successful
        # result, rather than an exception, so activation ending before supervision
        # cannot produce an un-retrieved-future warning.
        self._resource_limit_reached: asyncio.Future[_RuntimeFailure] = asyncio.get_running_loop().create_future()
        # Dedicated task for the on_session_end callback so session teardown does
        # not sit behind possibly-stalled ordinary callback work in the queue.
        self._session_end_task: asyncio.Task[None] | None = None
        self._session: VoiceSession | None = None
        self._session_retention: _SessionRetentionLease | None = None
        self._active_response: VoiceResponse | None = None
        self._pending_turns: OrderedDict[bytes, VoiceResponse] = OrderedDict()
        self._resolved_input_prefixes = _DigestPrefixMap()
        self._recent_responses: OrderedDict[str, _RecentResponse] = OrderedDict()
        self._identity_budget = _IdentityBudget(
            _MAX_CONNECTION_IDENTITY_BYTES,
            on_limit=self._signal_runtime_failure,
        )
        self._response_identities = _ResponseIdentityLedger(
            _MAX_ID_TOMBSTONES,
            max_abandoned=_MAX_PENDING_PROACTIVE,
            budget=self._identity_budget,
        )
        self._seen_response_ids = _ResponseIdentityView(self._response_identities, "seen")
        self._terminal_response_ids = _ResponseIdentityView(self._response_identities, "terminal")
        self._seen_messages = _ExactMessageLedger(
            _MAX_SEEN_MESSAGES,
            budget=self._identity_budget,
        )
        self._seen_input_ids = _ExactIdSet(
            _MAX_ID_TOMBSTONES,
            name="input id",
            budget=self._identity_budget,
        )
        self._playback_outcomes = _ResponseIdentityView(self._response_identities, "playback")
        self._abandoned_proactive_cancels = _ResponseIdentityView(self._response_identities, "abandoned")
        self._cancel_waiters: dict[str, asyncio.Future[ResponseCancellationOutcome]] = {}
        self._pending_proactive: OrderedDict[
            str,
            tuple[VoiceResponse, asyncio.Future[tuple[bool, str]]],
        ] = OrderedDict()
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
            _metric_add(_PROTOCOL_VIOLATION_COUNTER, 1, {"close_code": exc.close_code})
            logger.warning("Voice bridge protocol violation: %s", exc)
            await self._close(code=exc.close_code, reason="Protocol error")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Voice bridge runtime failed: %s", type(exc).__name__)
            await self._close(code=1011, reason="Internal server error")
        finally:
            shutdown = asyncio.create_task(
                self._shutdown_runtime(drain_callbacks=graceful_end),
                name="voice_connection_shutdown",
            )
            deferred_cancellation: asyncio.CancelledError | None = None
            while not shutdown.done():
                try:
                    await asyncio.shield(shutdown)
                except asyncio.CancelledError as exc:
                    deferred_cancellation = exc
            await shutdown
            if deferred_cancellation is not None:
                raise deferred_cancellation

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
        if receive_task in done:
            receive_error = receive_task.exception()
            if receive_error is not None:
                raise receive_error
        if worker in done:
            receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            if worker.cancelled():
                raise RuntimeError("Voice callback coordinator was cancelled unexpectedly")
            error = worker.exception()
            if error is not None:
                raise error
            raise RuntimeError("Voice callback coordinator stopped unexpectedly")
        if self._resource_limit_reached in done:
            receive_task.cancel()
            await asyncio.gather(receive_task, return_exceptions=True)
            raise self._resource_limit_reached.result().to_exception()
        return receive_task.result()

    async def send(self, message_type: str, *, _allow_while_ending: bool = False, **fields: Any) -> None:
        """Serialize one SDK-owned application frame.

        :param message_type: Wire message discriminator.
        :type message_type: str
        :keyword _allow_while_ending: Allow one SDK-owned session terminal frame.
        :paramtype _allow_while_ending: bool
        """
        if self._closed:
            raise VoiceBridgeConnectionClosedError("The voice connection is closed")
        prepared = self._prepare_frame(message_type, fields)
        await self._send_prepared(prepared, allow_while_ending=_allow_while_ending, state_committed=False)

    def prepare_frame(self, message_type: str, **fields: Any) -> _PreparedFrame:
        """Prepare a validated frame without changing connection state.

        :param message_type: Wire message discriminator.
        :type message_type: str
        :return: Immutable transport-ready frame.
        :rtype: _PreparedFrame
        """
        return self._prepare_frame(message_type, fields)

    async def send_prepared(self, prepared: _PreparedFrame, *, state_committed: bool) -> None:
        """Send a frame whose validation completed before caller state commit.

        :param prepared: Immutable transport-ready frame.
        :type prepared: _PreparedFrame
        :keyword state_committed: Whether caller state is already irreversible.
        :paramtype state_committed: bool
        """
        await self._send_prepared(prepared, state_committed=state_committed)

    def register_response_item(self, response_id: str, item_id: str) -> None:
        """Register response/item ownership as already transport committed.

        :param response_id: Owning response identifier.
        :type response_id: str
        :param item_id: Output item identifier.
        :type item_id: str
        """
        self._response_identities.register_item(response_id, item_id)

    def prepare_response_item(self, response_id: str, item_id: str) -> None:
        """Reserve response/item identity before its first wire attempt.

        :param response_id: Owning response identifier.
        :type response_id: str
        :param item_id: Output item identifier.
        :type item_id: str
        """
        self._response_identities.prepare_item(response_id, item_id)

    def discard_response_item(self, response_id: str, item_id: str) -> None:
        """Release an item reservation after a proven pre-transport failure.

        :param response_id: Owning response identifier.
        :type response_id: str
        :param item_id: Output item identifier.
        :type item_id: str
        """
        self._response_identities.discard_prepared_item(response_id, item_id)

    def reserve_output_bytes(self, size: int) -> None:
        """Reserve retained response text against the process-wide byte budget.

        :param size: Encoded text bytes to reserve.
        :type size: int
        """
        if not _reserve_global_output_bytes(size):
            self._signal_runtime_failure("Voice global customer task byte limit reached")
            raise RuntimeError("Voice global customer task byte limit reached")

    def release_output_bytes(self, size: int) -> None:
        """Release retained response text from the process-wide byte budget.

        :param size: Previously reserved encoded text bytes.
        :type size: int
        """
        _release_global_output_bytes(size)

    @staticmethod
    def _prepare_frame(message_type: str, fields: dict[str, Any]) -> _PreparedFrame:
        """Encode and validate a frame without changing protocol state.

        :param message_type: Wire message discriminator.
        :type message_type: str
        :param fields: Outbound message fields.
        :type fields: dict[str, Any]
        :return: Immutable transport-ready frame.
        :rtype: _PreparedFrame
        """
        return _prepare_protocol_frame(message_type, fields, max_frame_bytes=_MAX_FRAME_BYTES)

    async def _send_prepared(
        self,
        prepared: _PreparedFrame,
        *,
        allow_while_ending: bool = False,
        state_committed: bool,
        before_transport_attempt: Callable[[], None] | None = None,
    ) -> None:
        """Send one prepared frame with explicit commit-boundary handling.

        :param prepared: Immutable transport-ready frame.
        :type prepared: _PreparedFrame
        :keyword allow_while_ending: Permit the session terminal frame itself.
        :paramtype allow_while_ending: bool
        :keyword state_committed: Whether caller state was irreversibly committed.
        :paramtype state_committed: bool
        :keyword before_transport_attempt: Internal synchronous arbitration hook
            invoked immediately before entering the WebSocket transport call.
        :paramtype before_transport_attempt: Callable[[], None] or None
        """
        if self._closed:
            raise VoiceBridgeConnectionClosedError("The voice connection is closed")
        try:
            await self._send_lock.acquire()
        except BaseException:
            if state_committed:
                self._signal_runtime_failure("Voice send cancelled after protocol state commit")
            raise
        try:
            if self._closed:
                raise VoiceBridgeConnectionClosedError("The voice connection is closed")
            try:
                await self._state_lock.acquire()
            except BaseException:
                if state_committed:
                    self._signal_runtime_failure("Voice send cancelled after protocol state commit")
                raise
            try:
                if self._ending and not allow_while_ending:
                    raise VoiceBridgeConnectionClosedError("The voice session is ending")
                if prepared.response_id is not None and prepared.response_id in self._terminal_response_ids:
                    raise VoiceBridgeConnectionClosedError("The voice response is terminal")
            finally:
                self._state_lock.release()
            # Perform the WebSocket write OUTSIDE _state_lock. Holding the state
            # lock across a send that stalls on outbound backpressure would block
            # the receive pump from acquiring _state_lock to process barge_in,
            # response.timeout, or session termination — defeating the full-duplex
            # cancellation path. _send_lock still serializes writes; the terminal
            # check above rejects the common case, and the bridge drops any single
            # frame that races past a terminal it has already recorded.
            current_task = asyncio.current_task()
            cancelling = getattr(current_task, "cancelling", lambda: 0)
            if prepared.item_id is not None and cancelling():
                raise asyncio.CancelledError()
            if before_transport_attempt is not None:
                before_transport_attempt()
            try:
                if prepared.response_id is not None and prepared.item_id is not None:
                    self._response_identities.commit_item(prepared.response_id, prepared.item_id)
                await self._websocket.send_text(prepared.frame)
            except BaseException:
                # Any transport exception is past an ambiguous commit boundary:
                # the ASGI server may already have accepted the frame even though
                # the caller did not observe success. Never roll protocol state
                # back and continue using this connection.
                self._signal_runtime_failure("Voice WebSocket send failed")
                raise
        finally:
            self._send_lock.release()
        try:
            self._record_first_output(
                prepared.message_type,
                {"response_id": prepared.response_id} if prepared.response_id is not None else {},
            )
        except Exception:  # pylint: disable=broad-exception-caught
            # Instrument callbacks are external code. A frame already reached
            # the transport successfully, so telemetry must not redefine that
            # wire outcome or trigger a duplicate terminal.
            logger.warning("Voice first-output telemetry failed", exc_info=True)

    @staticmethod
    def _input_prefix_key(prefix: Sequence[str]) -> tuple[bytes, ...]:
        """Return fixed-size routing keys for one ordered input prefix.

        :param prefix: Ordered input identifiers.
        :type prefix: Sequence[str]
        :return: Ordered binary identity digests.
        :rtype: tuple[bytes, ...]
        """
        return tuple(_identity_digest(item_id) for item_id in prefix)

    def _pending_keys_locked(self) -> tuple[bytes, ...]:
        return tuple(key if isinstance(key, bytes) else _identity_digest(str(key)) for key in self._pending_turns)

    def _pending_response_locked(self, item_id: str) -> VoiceResponse:
        digest = _identity_digest(item_id)
        response = self._pending_turns.get(digest)
        if response is None:
            response = self._pending_turns.get(item_id)  # type: ignore[call-overload]
        if response is None:
            raise KeyError(item_id)
        return response

    def _pop_pending_locked(self, item_id: str) -> VoiceResponse | None:
        response = self._pending_turns.pop(_identity_digest(item_id), None)
        if response is None:
            response = self._pending_turns.pop(item_id, None)  # type: ignore[call-overload]
        return response

    def _remember_resolved_prefix_locked(
        self,
        prefix: tuple[str, ...],
        response: VoiceResponse,
        opened_response: bool,
    ) -> None:
        # Bounded LRU: these entries only reconcile a late response.timeout that
        # references a prefix the SDK already resolved before the bridge saw the
        # response.created — a single-round-trip window. Retaining every resolved
        # prefix (each holding a full VoiceResponse with accumulated output text)
        # for the life of the call would grow without bound; cap it and evict the
        # oldest, since a timeout arriving that far out of order is stale.
        prefix_key = self._input_prefix_key(prefix)
        self._resolved_input_prefixes.pop(prefix_key, None)
        self._resolved_input_prefixes[prefix_key] = _ResolvedPrefix(
            response_id=response.response_id,
            opened_response=opened_response,
            response_ref=weakref.ref(response),
        )
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
        prepared = self._prepare_frame(
            "response.created",
            {
                "response_id": response_id,
                "in_reply_to": list(in_reply_to),
            },
        )
        async with self._state_lock:
            if response_id in self._terminal_response_ids:
                return False
            active = self._active_response
            if active is None or active.response_id != response_id:
                raise VoiceBridgeConnectionClosedError("The response is no longer active")
            pending_keys = self._pending_keys_locked()
            in_reply_to_key = self._input_prefix_key(in_reply_to)
            if pending_keys[: len(in_reply_to_key)] != in_reply_to_key:
                raise RuntimeError("in_reply_to must be an ordered prefix of pending inputs")
            self._remember_resolved_prefix_locked(in_reply_to, active, True)
            for item_id in in_reply_to:
                self._pop_pending_locked(item_id)
        await self._send_prepared(prepared, state_committed=True)
        return True

    async def decline_response(self, in_reply_to: tuple[str, ...], reason: str | None) -> None:
        """Consume one explicit input prefix without opening a response.

        :param in_reply_to: Non-empty ordered input prefix.
        :type in_reply_to: tuple[str, ...]
        :param reason: Optional open-enum decline reason.
        :type reason: str or None
        """
        self._ensure_ready()
        fields: dict[str, Any] = {"in_reply_to": list(in_reply_to)}
        if reason is not None:
            fields["reason"] = reason
        prepared = self._prepare_frame("response.none", fields)
        response_id: str | None = None
        async with self._state_lock:
            active = self._active_response
            if (
                active is not None
                and active.in_reply_to == in_reply_to
                and active.response_id in self._terminal_response_ids
            ):
                return
            pending_keys = self._pending_keys_locked()
            in_reply_to_key = self._input_prefix_key(in_reply_to)
            if pending_keys[: len(in_reply_to_key)] != in_reply_to_key:
                raise RuntimeError("in_reply_to must be an ordered prefix of pending inputs")
            if in_reply_to:
                first_response = self._pending_response_locked(in_reply_to[0])
                response_id = first_response.response_id
                self._remember_resolved_prefix_locked(in_reply_to, first_response, False)
            for item_id in in_reply_to:
                self._pop_pending_locked(item_id)
            # Claim the terminal for this input prefix BEFORE emitting
            # response.none. It carries no response_id on the wire, so send-time
            # response checks cannot guard it. Prefix consumption and this claim
            # are one atomic state commit; cancellation cannot strand them apart.
            if response_id is not None:
                if response_id in self._terminal_response_ids:
                    return
                self._terminal_response_ids.add(response_id)
        await self._send_prepared(prepared, state_committed=True)
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
        fields: dict[str, Any] = {"response_id": response_id}
        if reason is not None:
            fields["reason"] = reason
        prepared = self._prepare_frame("response.cancel", fields)
        async with self._state_lock:
            response = self._find_response_locked(response_id)
            if response is None or not response.is_wire_opened:
                raise VoiceBridgeConnectionClosedError("The response is not open")
            if response_id in self._cancel_waiters:
                raise RuntimeError("Response cancellation is already pending")
            future: asyncio.Future[ResponseCancellationOutcome] = asyncio.get_running_loop().create_future()
            future.add_done_callback(_observe_future_completion)
            self._cancel_waiters[response_id] = future
        try:
            await self._send_prepared(prepared, state_committed=True)
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
            local_terminal_won = self._response_identities.claim_terminal(response_id)
            self._remember_response_locked(response)
            if self._active_response is response:
                self._active_response = None
        if local_terminal_won:
            self._record_terminal(response_id, terminal_kind)

    async def end_call(self, reason: str, mode: str) -> None:
        """Emit one call terminal and seal active work.

        :param reason: Non-empty open-enum termination reason.
        :type reason: str
        :param mode: Closed ``drain`` or ``immediate`` mode.
        :type mode: str
        """
        self._ensure_ready()
        prepared = self._prepare_frame("end_call", {"reason": reason, "mode": mode})
        async with self._state_lock:
            if self._ending:
                return
            self._ending = True
            response = self._active_response
            if response is not None:
                self._terminal_response_ids.add(response.response_id)
            release = self._active_release
            active_task = self._active_customer_task
            self._fail_pending_proactive_locked("Voice call ended")
        await self._send_prepared(prepared, allow_while_ending=True, state_committed=True)
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

        :keyword admission_timeout_ms: Bridge-owned maximum wait for a
            barge-safe admission point. The SDK does not run a second timer.
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
        future.add_done_callback(_observe_future_completion)
        fields: dict[str, Any] = {
            "response_id": response.response_id,
            "admission_timeout_ms": admission_timeout_ms,
        }
        if supersede_key is not None:
            fields["supersede_key"] = supersede_key
        prepared = self._prepare_frame("response.created", fields)
        async with self._state_lock:
            self._ensure_ready()
            if len(self._pending_proactive) >= _MAX_PENDING_PROACTIVE:
                raise RuntimeError("Too many proactive admission outcomes are pending")
            if response.response_id in self._seen_response_ids:
                raise RuntimeError("Generated proactive response_id was already used")
            self._seen_response_ids.add(response.response_id)
            self._pending_proactive[response.response_id] = (response, future)
        try:
            await self._send_prepared(prepared, state_committed=True)
        except BaseException:
            async with self._state_lock:
                if self.ending:
                    # Keep the response identity until shutdown so a frame that
                    # crossed the ambiguous send boundary is never reused, but
                    # cancel the now-unobserved admission Future.
                    future.cancel()
                else:
                    self._pending_proactive.pop(response.response_id, None)
            if future.done() and not future.cancelled():
                future.exception()
            raise
        try:
            accepted, reason = await future
        except asyncio.CancelledError:
            cancel_prepared = self._prepare_frame(
                "response.cancel",
                {
                    "response_id": response.response_id,
                    "reason": "cancelled_by_agent",
                },
            )
            async with self._state_lock:
                self._abandoned_proactive_cancels.add(response.response_id)
            try:
                await self._send_prepared(cancel_prepared, state_committed=True)
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
        prepared = self._prepare_frame("error", {"code": code, "message": message})
        async with self._state_lock:
            if self._ending:
                return
            self._ending = True
            response = self._active_response
            if response is not None:
                self._terminal_response_ids.add(response.response_id)
            release = self._active_release
            active_task = self._active_customer_task
            self._fail_pending_proactive_locked("Voice session failed")
        await self._send_prepared(prepared, allow_while_ending=True, state_committed=True)
        if response is not None:
            await response._mark_terminal()
            self._record_terminal(response.response_id, "session_error")
        if release is not None and active_task is not asyncio.current_task():
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
        session_retention = _reserve_session_retention(_estimate_session_retained_bytes(session, event))
        if session_retention is None:
            self._signal_runtime_failure("Voice global customer retained byte limit reached")
            await self._reject("startup_failed", close_code=1011)
            return False
        self._session_retention = session_retention
        self._session = session
        startup_receive_task: asyncio.Task[dict[str, Any] | None] | None = None
        try:
            startup_started_ns = time.monotonic_ns()
            try:
                startup_succeeded, startup_receive_task = await self._run_session_start_callback(session, event)
                if not startup_succeeded:
                    return False
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error("Voice session-start callback failed: %s", type(exc).__name__)
                _metric_add(_CALLBACK_ERROR_COUNTER, 1, {"kind": "session.start"})
                await self._reject("startup_failed", close_code=1011)
                return False
            finally:
                if self._on_session_start is not None:
                    _metric_record(
                        _CALLBACK_DURATION,
                        (time.monotonic_ns() - startup_started_ns) / 1_000_000,
                        {"kind": "session.start"},
                    )

            # Transfer sole ownership of the existing receive operation to the
            # readiness gate. Replacing it could drop an ASGI event already
            # delivered to this task but not yet observed by the coroutine.
            ready_receive_task = startup_receive_task
            startup_receive_task = None
            try:
                if not await self._send_ready_with_receive_gate(ready_receive_task):
                    return False
            except VoiceBridgeProtocolError as exc:
                await self._reject("protocol_mismatch", close_code=exc.close_code)
                return False
        finally:
            # This stage owns the task only between callback completion and the
            # explicit handoff above. All other paths clean up in their owner.
            if startup_receive_task is not None:
                if not startup_receive_task.done():
                    startup_receive_task.cancel()
                await asyncio.gather(startup_receive_task, return_exceptions=True)
        self._record_activation("ready")
        self._ready = True
        self._callback_worker = asyncio.create_task(self._callback_worker_loop(), name="voice_callback_coordinator")
        return True

    async def _send_ready_with_receive_gate(  # pylint: disable=too-many-statements
        self,
        receive_task: asyncio.Task[dict[str, Any] | None] | None = None,
    ) -> bool:
        """Send readiness while rejecting only an unambiguously early frame.

        :param receive_task: Sole receive operation transferred from startup.
        :type receive_task: asyncio.Task[dict[str, Any] | None] or None
        :return: Whether activation may proceed.
        :rtype: bool
        """
        ready_transport_attempted = asyncio.Event()
        receive_after_transport_attempt = False
        transferred_receive = receive_task
        prepared_ready = self._prepare_frame("session.ready", {})

        class _EarlyReadyReceive(Exception):
            """The receive gate won before the ready transport attempt."""

        def _enter_ready_transport() -> None:
            # No await separates this check, marker, and the following transport
            # call. This is the local arbitration point between a completed receive
            # and the ready frame entering the WebSocket transport.
            if active_receive_task.done() and not receive_after_transport_attempt:
                raise _EarlyReadyReceive()
            ready_transport_attempted.set()

        async def _send_ready() -> None:
            await self._send_prepared(
                prepared_ready,
                state_committed=False,
                before_transport_attempt=_enter_ready_transport,
            )

        async def _receive_during_ready() -> dict[str, Any] | None:
            nonlocal receive_after_transport_attempt
            try:
                if transferred_receive is not None:
                    return await transferred_receive
                return await self._receive_payload()
            finally:
                # Captured in the receive task itself, before task completion
                # callbacks or the coordinator can reorder observations.
                receive_after_transport_attempt = ready_transport_attempted.is_set()

        active_receive_task = asyncio.create_task(_receive_during_ready(), name="voice_ready_receive")

        async def _reject_early_receive() -> bool:
            try:
                early_payload = active_receive_task.result()
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

        try:
            # Give the existing receive gate one event-loop turn to consume a
            # frame that was already queued before readiness was attempted.
            await asyncio.sleep(0)
        except BaseException:
            active_receive_task.cancel()
            await asyncio.gather(active_receive_task, return_exceptions=True)
            raise
        if active_receive_task.done() and not receive_after_transport_attempt:
            return await _reject_early_receive()
        ready_task = asyncio.create_task(_send_ready(), name="voice_session_ready")
        try:
            done, _ = await asyncio.wait((ready_task, active_receive_task), return_when=asyncio.FIRST_COMPLETED)
        except BaseException:
            ready_task.cancel()
            active_receive_task.cancel()
            await asyncio.gather(ready_task, active_receive_task, return_exceptions=True)
            raise

        # A frame is provably early only when the receive coroutine completed
        # before the ready frame entered the WebSocket transport call. Once that
        # call begins, the peer may receive ready and reply before the sender
        # continuation resumes.
        if active_receive_task in done and not receive_after_transport_attempt:
            ready_task.cancel()
            await asyncio.gather(ready_task, return_exceptions=True)
            return await _reject_early_receive()

        try:
            await ready_task
        except _EarlyReadyReceive:
            return await _reject_early_receive()
        except BaseException:
            if not active_receive_task.done():
                active_receive_task.cancel()
            await asyncio.gather(active_receive_task, return_exceptions=True)
            raise

        # Preserve the sole receive operation. Cancelling it here could consume
        # and drop a frame that arrived immediately after ready was committed.
        # The main loop adopts this task under normal worker supervision.
        self._prefetched_receive_task = active_receive_task
        return True

    async def _run_session_start_callback(
        self,
        session: VoiceSession,
        event: SessionStartEvent,
    ) -> tuple[bool, asyncio.Task[dict[str, Any] | None] | None]:
        async def _invoke_customer_callback() -> None:
            if self._on_session_start is not None:
                await self._on_session_start(session, event)

        receive_task = asyncio.create_task(
            self._receive_payload(),
            name="voice_activation_receive",
        )
        transfer_receive = False
        try:
            customer_task = self._create_customer_task(
                _invoke_customer_callback(),
                name="voice_session_start",
            )
            try:
                done, _ = await asyncio.wait((customer_task, receive_task), return_when=asyncio.FIRST_COMPLETED)
            except BaseException:
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
                return False, None

            if customer_task.cancelled():
                raise RuntimeError("Voice session-start callback was cancelled")
            error = customer_task.exception()
            if error is not None:
                raise error
            transfer_receive = True
            return True, receive_task
        finally:
            if not transfer_receive:
                if not receive_task.done():
                    receive_task.cancel()
                await asyncio.gather(receive_task, return_exceptions=True)

    async def _reject(self, code: str, *, close_code: int) -> None:
        if self._closed:
            return
        self._record_activation(code)
        if code in ("invalid_session_start", "protocol_mismatch"):
            _metric_add(_PROTOCOL_VIOLATION_COUNTER, 1, {"close_code": close_code})
        try:
            await self.send(
                "session.rejected",
                _allow_while_ending=True,
                code=safe_code(code, "startup_failed"),
                retriable=False,
            )
        finally:
            await self._close(code=close_code, reason="Session rejected")

    async def _dispatch(self, payload: dict[str, Any]) -> bool:  # pylint: disable=too-many-branches
        message_type = payload["type"]
        if message_type == "user.message":
            message_event = parse_user_message(payload)
            if not message_event.content:
                async with self._state_lock:
                    if self._ending:
                        raise VoiceBridgeProtocolError(
                            "user.message arrived after session terminal",
                            close_code=1008,
                        )
                    if message_event.item_id in self._seen_input_ids:
                        raise VoiceBridgeProtocolError("Input item_id was reused", close_code=1008)
                    self._seen_input_ids.add(message_event.item_id)
                return True
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
            if item_id in self._seen_input_ids:
                raise VoiceBridgeProtocolError("Input item_id was reused", close_code=1008)
            self._seen_input_ids.add(item_id)
            if response.response_id in self._seen_response_ids:
                raise RuntimeError("Generated response_id was already used")
            self._seen_response_ids.add(response.response_id)
            self._pending_turns[_identity_digest(item_id)] = response
            self._response_start_ns[response.response_id] = time.monotonic_ns()
        self._put_work(
            _CallbackWork(
                kind=kind,
                event=event,
                callback=callback,
                response=response,
                item_id=item_id,
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

    def _put_work(self, work: _CallbackWork) -> None:
        self._ensure_dispatch_open()
        if work.payload_bytes == 0:
            work = replace(work, payload_bytes=_estimate_retained_bytes(work))
        if self._callback_queue_bytes + work.payload_bytes > _MAX_CALLBACK_QUEUE_BYTES:
            raise VoiceBridgeProtocolError("Voice callback queue byte limit exceeded", close_code=1008)
        if not _reserve_global_callback_queue_bytes(work.payload_bytes):
            self._signal_runtime_failure("Voice global callback queue byte limit reached")
            raise RuntimeError("Voice global callback queue byte limit reached")
        try:
            self._callback_queue.put_nowait(work)
        except asyncio.QueueFull as exc:
            _release_global_callback_queue_bytes(work.payload_bytes)
            raise VoiceBridgeProtocolError("Voice callback queue limit exceeded", close_code=1008) from exc
        self._callback_queue_bytes += work.payload_bytes

    def _ensure_dispatch_open(self) -> None:
        """Reject state or queue growth after a fatal/terminal gate."""
        if self._resource_limit_reached.done():
            raise self._resource_limit_reached.result().to_exception()
        if self._ending or self._closed:
            raise VoiceBridgeConnectionClosedError("The voice connection is ending")

    def _discard_callback_queue(self) -> None:
        """Release callback work that will never be dispatched."""
        while True:
            try:
                work = self._callback_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            if work is not None:
                self._callback_queue_bytes -= work.payload_bytes
                _release_global_callback_queue_bytes(work.payload_bytes)
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
                    raise self._resource_limit_reached.result().to_exception()
                if work.response is not None:
                    await self._process_turn_work(work)
                else:
                    await self._process_signal_work(work)
            finally:
                if work is not None:
                    self._callback_queue_bytes -= work.payload_bytes
                    _release_global_callback_queue_bytes(work.payload_bytes)
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
            if active is not None and active is not response:
                self._remember_response_locked(active)
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
                        self._pending_turns.pop(_identity_digest(work.item_id), None)
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
            retained_bytes=work.payload_bytes,
        )
        release_task = asyncio.create_task(release.wait(), name="voice_turn_release")
        callback_metric_recorded = False
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
                        _metric_add(_CALLBACK_ERROR_COUNTER, 1, {"kind": work.kind})
                        await self._finalize_turn_response(response, release_task, failed=True)
                else:
                    await self._finalize_turn_response(response, release_task, failed=False)
            if customer_task.done():
                async with self._state_lock:
                    if self._active_customer_task is customer_task:
                        self._active_customer_task = None
                _metric_record(
                    _CALLBACK_DURATION,
                    (time.monotonic_ns() - callback_started_ns) / 1_000_000,
                    {"kind": work.kind},
                )
                callback_metric_recorded = True
            if response.is_cancel_pending and not response.is_terminal and not self.ending:
                # Customer callback completion does not end protocol ownership.
                # Keep this response active until the Bridge commits the winning
                # cancel/barge/timeout outcome or the connection starts ending.
                await release_task
        except asyncio.CancelledError:
            if not customer_task.done():
                self._schedule_customer_cleanup(customer_task)
            raise
        finally:
            if not callback_metric_recorded:
                _metric_record(
                    _CALLBACK_DURATION,
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
                    self._pending_turns.pop(_identity_digest(work.item_id), None)
                if response.is_wire_opened:
                    self._remember_response_locked(response)

    async def _process_signal_work(self, work: _CallbackWork) -> None:
        if self._session is None or self._ending:
            return
        if work.callback is None:
            return
        callback_started_ns = time.monotonic_ns()
        try:
            await self._await_signal_callback(work)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Voice signal callback failed: %s", type(exc).__name__)
            _metric_add(_CALLBACK_ERROR_COUNTER, 1, {"kind": work.kind})
        finally:
            _metric_record(
                _CALLBACK_DURATION,
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
            retained_bytes=work.payload_bytes or _estimate_retained_bytes(work),
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
        retained_bytes: int = 0,
    ) -> asyncio.Task[None]:
        global _GLOBAL_CUSTOMER_TASK_RESERVATIONS  # pylint: disable=global-statement
        global _GLOBAL_CUSTOMER_TASK_BYTES  # pylint: disable=global-statement
        session_retention = self._session_retention
        with _GLOBAL_CUSTOMER_TASKS_LOCK:
            if _GLOBAL_CUSTOMER_TASK_RESERVATIONS >= _MAX_GLOBAL_CUSTOMER_TASKS:
                limit_error = "Voice global customer task limit reached"
            elif _GLOBAL_CUSTOMER_TASK_BYTES + retained_bytes > _MAX_GLOBAL_CUSTOMER_TASK_BYTES:
                limit_error = "Voice global customer task byte limit reached"
            elif session_retention is not None and session_retention.released:
                limit_error = "Voice session retention lease was already released"
            else:
                limit_error = None
                _GLOBAL_CUSTOMER_TASK_RESERVATIONS += 1
                _GLOBAL_CUSTOMER_TASK_BYTES += retained_bytes
                if session_retention is not None:
                    session_retention.references += 1

        if limit_error is not None:
            coroutine.close()
            self._signal_runtime_failure(limit_error)
            raise RuntimeError(limit_error)

        try:
            task = asyncio.create_task(coroutine, name=name)
        except BaseException:
            coroutine.close()
            with _GLOBAL_CUSTOMER_TASKS_LOCK:
                _GLOBAL_CUSTOMER_TASK_RESERVATIONS -= 1
                _GLOBAL_CUSTOMER_TASK_BYTES -= retained_bytes
                if session_retention is not None:
                    _release_session_retention_locked(session_retention)
            raise

        with _GLOBAL_CUSTOMER_TASKS_LOCK:
            _GLOBAL_CUSTOMER_TASKS.add(task)
            _GLOBAL_CUSTOMER_TASK_BYTES_BY_TASK[task] = retained_bytes
            if session_retention is not None:
                _GLOBAL_SESSION_RETENTION_BY_TASK[task] = session_retention

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

    def _signal_runtime_failure(self, reason: str, close_code: int = 1011) -> None:
        self._ending = True
        if not self._resource_limit_reached.done():
            logger.error("%s", reason)
            self._resource_limit_reached.set_result(_RuntimeFailure(reason=reason, close_code=close_code))

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
                self._signal_runtime_failure("Voice cancellation-resistant task limit reached")

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
            if self._response_identities.has_playback_outcome(response_id):
                return
            response = self._find_response_locked(response_id)
            recent = self._find_recent_response_locked(response_id)
            if response is None and recent is None:
                if response_id in self._pending_proactive:
                    raise VoiceBridgeProtocolError(
                        f"{kind} is invalid before proactive response.accepted",
                        close_code=1008,
                    )
                if response_id not in self._seen_response_ids:
                    raise VoiceBridgeProtocolError("Unknown playback response_id", close_code=1008)
                if item_id is None and not self._response_identities.has_output(response_id):
                    return
            if item_id is not None and not self._response_identities.owns_item(response_id, item_id):
                raise VoiceBridgeProtocolError("Playback item_id does not belong to response_id", close_code=1008)
            self._response_identities.mark_playback_outcome(response_id)
            waiter = self._cancel_waiters.get(response_id)
            abandoned = self._response_identities.is_abandoned(response_id)
            if kind == "cancelled" and waiter is None and not abandoned:
                self._response_identities.clear_playback_outcome(response_id, strict=True)
                raise VoiceBridgeProtocolError(
                    "response.cancelled requires a pending response.cancel",
                    close_code=1008,
                )
            active = response is not None and self._active_response is response
            # Always wake the active turn coordinator after a bridge terminal.
            # If response.cancel is itself stalled on outbound backpressure, the
            # coordinator's bounded drain path gives that winning write a chance to
            # finish before cancelling the customer task. Suppressing release while
            # cancel is pending would bypass that bound and wedge the callback worker.
            release = self._active_release if active else None
            playback_terminal_won = self._response_identities.claim_terminal(response_id)
        if response is not None:
            await response._mark_terminal()
        owns_waiter = False
        async with self._state_lock:
            if waiter is not None and self._cancel_waiters.get(response_id) is waiter:
                self._cancel_waiters.pop(response_id, None)
                owns_waiter = True
            owns_transition = not self._ending and not self._closed and (waiter is None or owns_waiter)
            if owns_transition and abandoned:
                self._response_identities.clear_abandoned(response_id)
        if not owns_transition:
            return
        outcome = ResponseCancellationOutcome(
            response_id=response_id,
            kind="barge_in" if kind == "barge_in" else "cancelled",
            heard_text=heard_text,
            item_id=item_id,
        )
        if owns_waiter and waiter is not None and not waiter.done():
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
        cancel_waiters: list[tuple[str, asyncio.Future[ResponseCancellationOutcome]]] = []
        async with self._state_lock:
            if event.response_id is not None:
                response = self._find_response_locked(event.response_id)
                recent = self._find_recent_response_locked(event.response_id)
                if self._response_identities.has_playback_outcome(event.response_id):
                    return
                if response is None and recent is None:
                    if event.response_id in self._pending_proactive:
                        raise VoiceBridgeProtocolError(
                            "response.timeout is invalid before proactive response.accepted",
                            close_code=1008,
                        )
                    if event.response_id in self._seen_response_ids:
                        return
                    raise VoiceBridgeProtocolError("Unknown response.timeout response_id", close_code=1008)
                if response is not None:
                    responses.append(response)
                self._response_identities.mark_playback_outcome(event.response_id)
                if self._response_identities.claim_terminal(event.response_id):
                    timeout_metric_winners.add(event.response_id)
                if response is not None and self._active_response is response:
                    release = self._active_release
                cancel_waiter = self._cancel_waiters.get(event.response_id)
                if cancel_waiter is not None:
                    cancel_waiters.append((event.response_id, cancel_waiter))
            else:
                assert event.item_ids is not None
                event_keys = self._input_prefix_key(event.item_ids)
                pending_keys = tuple(self._pending_turns)
                if pending_keys[: len(event_keys)] == event_keys:
                    for item_key in event_keys:
                        response = self._pending_turns.pop(item_key)
                        if response.is_wire_opened:
                            raise VoiceBridgeProtocolError(
                                "response.timeout item_ids referenced an open response",
                                close_code=1008,
                            )
                        responses.append(response)
                        if self._response_identities.claim_terminal(response.response_id):
                            timeout_metric_winners.add(response.response_id)
                        if self._active_response is response:
                            release = self._active_release
                else:
                    remaining = event_keys
                    while remaining:
                        resolved = next(
                            (
                                (prefix, resolved_prefix)
                                for prefix, resolved_prefix in self._resolved_input_prefixes.items()
                                if remaining[: len(prefix)]
                                == (
                                    prefix
                                    if not prefix or isinstance(prefix[0], bytes)
                                    else tuple(_identity_digest(str(item_id)) for item_id in prefix)
                                )
                            ),
                            None,
                        )
                        if resolved is not None:
                            prefix, resolved_prefix = resolved
                            self._resolved_input_prefixes.pop(prefix, None)
                            if isinstance(resolved_prefix, tuple):
                                # Compatibility for internal callers/tests that
                                # populated the pre-snapshot representation.
                                response, opened_response = resolved_prefix
                                response_id = response.response_id
                            else:
                                response = resolved_prefix.response_ref()
                                response_id = resolved_prefix.response_id
                                opened_response = resolved_prefix.opened_response
                            if response is not None and response not in responses:
                                responses.append(response)
                            if self._response_identities.claim_terminal(response_id):
                                timeout_metric_winners.add(response_id)
                            if response is not None and self._active_response is response:
                                release = self._active_release
                            if opened_response:
                                self._response_identities.mark_playback_outcome(response_id)
                                cancel_waiter = self._cancel_waiters.get(response_id)
                                if cancel_waiter is not None:
                                    cancel_waiters.append((response_id, cancel_waiter))
                            remaining = remaining[len(prefix) :]
                            continue

                        pending_keys = tuple(self._pending_turns)
                        if pending_keys[: len(remaining)] != remaining:
                            raise VoiceBridgeProtocolError(
                                "response.timeout item_ids do not match the pending or just-resolved prefix",
                                close_code=1008,
                            )
                        for item_key in remaining:
                            response = self._pending_turns.pop(item_key)
                            if response.is_wire_opened:
                                raise VoiceBridgeProtocolError(
                                    "response.timeout item_ids referenced an open response",
                                    close_code=1008,
                                )
                            if response not in responses:
                                responses.append(response)
                            if self._response_identities.claim_terminal(response.response_id):
                                timeout_metric_winners.add(response.response_id)
                            if self._active_response is response:
                                release = self._active_release
                        remaining = ()
        for response in responses:
            await response._mark_terminal()
        owned_cancel_waiters: list[asyncio.Future[ResponseCancellationOutcome]] = []
        async with self._state_lock:
            owns_transition = (
                not self._ending
                and not self._closed
                and all(self._cancel_waiters.get(response_id) is waiter for response_id, waiter in cancel_waiters)
            )
            if owns_transition:
                for response_id, cancel_waiter in cancel_waiters:
                    self._cancel_waiters.pop(response_id, None)
                    owned_cancel_waiters.append(cancel_waiter)
                if event.response_id is not None:
                    self._response_identities.clear_abandoned(event.response_id)
        if not owns_transition:
            return
        for response_id in timeout_metric_winners:
            self._record_terminal(response_id, "timeout")
        for cancel_waiter in owned_cancel_waiters:
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
            if self._ending and response_id in self._seen_response_ids:
                if pending is not None:
                    self._fail_pending_proactive_locked("Voice session is ending")
                return
            if pending is None:
                raise VoiceBridgeProtocolError("Unknown proactive response_id", close_code=1008)
            response, future = pending
            if self._active_response is not None and not self._active_response.is_terminal:
                raise VoiceBridgeProtocolError(
                    "Proactive response accepted while another response is active",
                    close_code=1008,
                )
        await response._mark_accepted()
        owns_future = False
        async with self._state_lock:
            if self._pending_proactive.get(response_id) is pending:
                active = self._active_response
                if active is not None and active is not response and not active.is_terminal:
                    raise VoiceBridgeProtocolError(
                        "Proactive response accepted while another response is active",
                        close_code=1008,
                    )
                if active is not None and active is not response:
                    self._remember_response_locked(active)
                self._pending_proactive.pop(response_id, None)
                self._active_response = response
                self._response_start_ns[response_id] = time.monotonic_ns()
                owns_future = True
        if owns_future and not future.done():
            future.set_result((True, ""))

    async def _handle_response_dropped(self, payload: dict[str, Any]) -> None:
        response_id = require_prefixed_id(payload, "response_id", "r_")
        reason = safe_code(require_string(payload, "reason", non_empty=True), "dropped")
        async with self._state_lock:
            if self._ending and response_id in self._seen_response_ids:
                if response_id in self._pending_proactive:
                    self._fail_pending_proactive_locked("Voice session is ending")
                return
            pending = self._pending_proactive.get(response_id)
            if pending is None:
                raise VoiceBridgeProtocolError("Unknown proactive response_id", close_code=1008)
            response, future = pending
            self._terminal_response_ids.add(response_id)
        await response._mark_terminal()
        owns_future = False
        async with self._state_lock:
            if self._pending_proactive.get(response_id) is pending:
                self._pending_proactive.pop(response_id, None)
                self._abandoned_proactive_cancels.discard(response_id)
                owns_future = True
        if owns_future:
            self._record_terminal(response_id, "dropped")
        if owns_future and not future.done():
            future.set_result((False, reason))

    async def _handle_session_end(self, payload: dict[str, Any]) -> None:
        event = SessionEndEvent(reason=require_string(payload, "reason", non_empty=True))
        async with self._state_lock:
            self._ending = True
            responses = list(self._pending_turns.values())
            self._pending_turns.clear()
            if self._active_response is not None and self._active_response not in responses:
                responses.append(self._active_response)
            release = self._active_release
            self._fail_pending_proactive_locked("Voice session ended")
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
            _metric_add(_CALLBACK_ERROR_COUNTER, 1, {"kind": work.kind})
        finally:
            _metric_record(
                _CALLBACK_DURATION,
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
                _metric_add(_PROTOCOL_VIOLATION_COUNTER, 1, {"close_code": 1003})
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
            # digest. Binary SHA-256 bounds both the id key and payload value to
            # 32 bytes. Reusing an id with different content still collides on the
            # key and differs on the value.
            message_key = hashlib.sha256(message_id.encode("utf-8")).digest()
            digest = hashlib.sha256(canonical_payload(payload).encode("utf-8")).digest()
            previous = self._seen_messages.get(message_key)
            if previous is not None:
                if previous != digest:
                    raise VoiceBridgeProtocolError("Message id was reused with different content", close_code=1008)
                continue
            self._seen_messages.add(message_key, digest)
            return payload

    async def _shutdown_runtime(self, *, drain_callbacks: bool) -> None:
        deadline = asyncio.get_running_loop().time() + _CLEANUP_TIMEOUT_SECONDS

        def _remaining() -> float:
            return max(0.0, deadline - asyncio.get_running_loop().time())

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
            release = self._active_release
            self._fail_pending_proactive_locked("Voice connection closed")
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
                try:
                    await asyncio.wait_for(worker, timeout=_remaining())
                except (asyncio.TimeoutError, asyncio.CancelledError):
                    pass
            else:
                try:
                    await asyncio.wait_for(self._callback_queue.join(), timeout=_remaining())
                except asyncio.TimeoutError:
                    logger.warning("Voice callback drain exceeded cleanup deadline")
            if drain_callbacks and not worker.done():
                try:
                    self._callback_queue.put_nowait(None)
                except asyncio.QueueFull:
                    worker.cancel()
                try:
                    await asyncio.wait_for(worker, timeout=_remaining())
                except asyncio.TimeoutError:
                    worker.cancel()
                    await asyncio.gather(worker, return_exceptions=True)
                except asyncio.CancelledError:
                    pass
            if worker.done() and not worker.cancelled():
                # Retrieve any failure even when session.end made the main receive
                # loop stop before normal worker supervision could observe it.
                worker.exception()

        self._discard_callback_queue()

        session_end_task = self._session_end_task
        if session_end_task is not None:
            # Dedicated bounded path for session teardown, independent of the
            # ordinary callback queue drained above.
            try:
                await asyncio.wait_for(asyncio.shield(session_end_task), timeout=_remaining())
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
                    timeout=_remaining(),
                )
            except asyncio.TimeoutError:
                for task in tuple(self._cleanup_tasks):
                    task.cancel()
        self._release_connection_state()

    def _release_connection_state(self) -> None:
        """Release connection-scoped caches after dispatch has stopped."""
        self._resolved_input_prefixes.clear()
        self._recent_responses.clear()
        self._response_identities.clear_all()
        self._seen_messages.clear()
        self._seen_input_ids.clear()
        if self._identity_budget.used_bytes:
            raise RuntimeError("Voice connection identity byte accounting leak")
        self._response_start_ns.clear()
        self._first_output_recorded.clear()
        self._cleanup_tasks.clear()
        self._active_customer_task = None
        self._active_response = None
        self._active_release = None
        self._callback_worker = None
        self._session_end_task = None
        session_retention = self._session_retention
        self._session_retention = None
        self._session = None
        if session_retention is not None:
            _release_session_retention(session_retention)

    def _fail_pending_proactive_locked(self, message: str) -> None:
        """Fail pending proactive admissions while the caller holds ``_state_lock``.

        :param message: Safe diagnostic used for admission exceptions.
        :type message: str
        """
        for response_id, (_, proactive_future) in self._pending_proactive.items():
            if proactive_future.done():
                continue
            if response_id in self._abandoned_proactive_cancels:
                proactive_future.cancel()
            else:
                proactive_future.set_exception(VoiceBridgeConnectionClosedError(message))
        self._pending_proactive.clear()
        self._abandoned_proactive_cancels.clear()

    def _fail_helper_waiters(self, message: str) -> None:
        for future in tuple(self._cancel_waiters.values()):
            if not future.done():
                future.set_exception(VoiceBridgeConnectionClosedError(message))
        self._cancel_waiters.clear()
        self._abandoned_proactive_cancels.clear()
        for _, proactive_future in self._pending_proactive.values():
            if not proactive_future.done():
                proactive_future.set_exception(VoiceBridgeConnectionClosedError(message))
        self._pending_proactive.clear()

    def _find_response_locked(self, response_id: str) -> VoiceResponse | None:
        if self._active_response is not None and self._active_response.response_id == response_id:
            return self._active_response
        recent = self._recent_responses.get(response_id)
        return recent.response_ref() if recent is not None else None

    def _find_recent_response_locked(self, response_id: str) -> _RecentResponse | None:
        return self._recent_responses.get(response_id)

    def _remember_response_locked(self, response: VoiceResponse) -> None:
        # Late timeout/barge-in reconciliation needs only identity plus the set
        # of item ids that reached or entered a wire write. Keep a weak reference
        # so a customer-retained response still receives its cancellation token,
        # but never let this cache retain the full response/item object graph.
        response._release_output_buffers()
        self._recent_responses[response.response_id] = _RecentResponse(
            response_id=response.response_id,
            response_ref=weakref.ref(response),
        )
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
        _metric_record(_FIRST_OUTPUT_DURATION, duration_ms)

    def _record_terminal(self, response_id: str, terminal_kind: str) -> None:
        _metric_add(_TERMINAL_COUNTER, 1, {"kind": terminal_kind})
        self._response_start_ns.pop(response_id, None)
        self._first_output_recorded.discard(response_id)

    def _record_activation(self, result: str) -> None:
        if self._activation_recorded:
            return
        self._activation_recorded = True
        _metric_add(_ACTIVATION_COUNTER, 1, {"result": result})

    def _record_close(self, code: int) -> None:
        if self._close_recorded:
            return
        self._close_recorded = True
        _metric_add(_CLOSE_CODE_COUNTER, 1, {"code": code})

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


def _estimate_retained_bytes(event: Any) -> int:
    """Return a container-aware CPython retained-memory estimate for callback data.

    Unlike the encoded-size estimator, this includes container/object overhead so
    a frame containing many tiny content parts cannot bypass queue memory budgets.

    :param event: Callback work or typed event to measure.
    :type event: Any
    :return: Estimated retained bytes.
    :rtype: int
    """
    total = 0
    pending = [event]
    seen: set[int] = set()
    while pending:
        value = pending.pop()
        value_id = id(value)
        if value_id in seen:
            continue
        seen.add(value_id)
        total += sys.getsizeof(value)
        if is_dataclass(value) and not isinstance(value, type):
            pending.extend(getattr(value, field.name) for field in dataclass_fields(value))
        elif isinstance(value, Mapping):
            if isinstance(value, MappingProxyType):
                # ``sys.getsizeof(mappingproxy)`` excludes its hidden backing
                # dictionary. Add an equivalent shallow table without recounting
                # keys or values, which remain traversed below.
                total += sys.getsizeof(dict.fromkeys(value))
            pending.extend(value.keys())
            pending.extend(value.values())
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            pending.extend(value)
    return total


def _estimate_session_retained_bytes(session: VoiceSession, event: SessionStartEvent) -> int:
    """Estimate the startup graph retained by a live connection.

    Measure the session shell, its attribute table, and the event graph without
    traversing ``session._sender`` back into the full connection/WebSocket graph.

    :param session: Connection-scoped public helper retaining the startup event.
    :type session: VoiceSession
    :param event: Parsed startup context retained by the session.
    :type event: SessionStartEvent
    :return: Estimated retained bytes charged once per live session graph.
    :rtype: int
    """
    return sys.getsizeof(session) + sys.getsizeof(session.__dict__) + _estimate_retained_bytes(event)
