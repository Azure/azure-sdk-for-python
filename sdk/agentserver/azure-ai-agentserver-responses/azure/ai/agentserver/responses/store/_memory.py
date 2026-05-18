# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""In-memory response store implementation."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import contextlib
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncIterator, Dict, Iterable

from .._response_context import IsolationContext
from ..models._generated import OutputItem, ResponseObject, ResponseStreamEvent
from ..models._helpers import get_conversation_id
from ..models.runtime import ResponseExecution, ResponseModeFlags, ResponseStatus, StreamEventRecord, StreamReplayState
from ._base import ResponseProviderProtocol, ResponseStreamProviderProtocol

_DEFAULT_REPLAY_EVENT_TTL_SECONDS: int = 600
"""Minimum per-event replay TTL (10 minutes) per spec B35."""


class _StoreEntry:
    """Container for one response execution and its replay state."""

    def __init__(
        self,
        *,
        execution: ResponseExecution,
        replay: StreamReplayState,
        response: ResponseObject | None = None,
        input_item_ids: list[str] | None = None,
        output_item_ids: list[str] | None = None,
        history_item_ids: list[str] | None = None,
        deleted: bool = False,
        expires_at: datetime | None = None,
        replay_event_ttl_seconds: int = _DEFAULT_REPLAY_EVENT_TTL_SECONDS,
    ) -> None:
        self.execution = execution
        self.replay = replay
        self.response = response
        self.input_item_ids = input_item_ids
        self.output_item_ids = output_item_ids
        self.history_item_ids = history_item_ids
        self.deleted = deleted
        self.expires_at = expires_at
        self.replay_event_ttl_seconds = replay_event_ttl_seconds


class InMemoryResponseProvider(ResponseProviderProtocol, ResponseStreamProviderProtocol):
    """In-memory provider implementing both ``ResponseProviderProtocol`` and ``ResponseStreamProviderProtocol``."""

    def __init__(self) -> None:
        """Initialize in-memory state and an async mutation lock."""
        self._entries: Dict[str, _StoreEntry] = {}
        self._lock = asyncio.Lock()
        self._item_store: Dict[str, OutputItem] = {}
        self._conversation_responses: defaultdict[str, list[str]] = defaultdict(list)
        self._stream_events: Dict[str, list[ResponseStreamEvent]] = {}

    @contextlib.asynccontextmanager
    async def _locked(self) -> AsyncIterator[None]:
        """Acquire the lock and purge expired entries.

        :returns: An async context manager that yields ``None`` once the lock is acquired.
        :rtype: AsyncIterator[None]
        """
        async with self._lock:
            self._purge_expired_unlocked()
            yield

    async def create_response(
        self,
        response: ResponseObject,
        input_items: Iterable[OutputItem] | None,
        history_item_ids: Iterable[str] | None,
        *,
        isolation: IsolationContext | None = None,
    ) -> None:
        """Persist a new response envelope and optional input/history references.

        Stores a deep copy of the response, indexes input items by their IDs,
        and tracks conversation membership for history resolution.

        :param response: The response envelope to persist.
        :type response: ~azure.ai.agentserver.responses.models._generated.Response
        :param input_items: Optional resolved output items to associate with the response.
        :type input_items: Iterable[OutputItem] | None
        :param history_item_ids: Optional history item IDs to link to the response.
        :type history_item_ids: Iterable[str] | None
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        :raises ValueError: If a non-deleted response with the same ID already exists.
        """
        response_id = str(getattr(response, "id"))
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is not None and not entry.deleted:
                raise ValueError(f"response '{response_id}' already exists")

            input_ids: list[str] = []
            if input_items is not None:
                for item in input_items:
                    item_id = self._extract_item_id(item)
                    if item_id is None:
                        continue
                    self._item_store[item_id] = deepcopy(item)
                    input_ids.append(item_id)

            history_ids = list(history_item_ids) if history_item_ids is not None else []
            output_ids = self._store_output_items_unlocked(response)
            self._entries[response_id] = _StoreEntry(
                execution=ResponseExecution(
                    response_id=response_id,
                    mode_flags=self._resolve_mode_flags_from_response(response),
                ),
                replay=StreamReplayState(response_id=response_id),
                response=deepcopy(response),
                input_item_ids=input_ids,
                output_item_ids=output_ids,
                history_item_ids=history_ids,
                deleted=False,
            )

            conversation_id = get_conversation_id(response)
            if conversation_id is not None:
                self._conversation_responses[conversation_id].append(response_id)

    async def get_response(self, response_id: str, *, isolation: IsolationContext | None = None) -> ResponseObject:
        """Retrieve one response envelope by identifier.

        :param response_id: The unique identifier of the response to retrieve.
        :type response_id: str
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :returns: A deep copy of the stored response envelope.
        :rtype: ~azure.ai.agentserver.responses.models._generated.Response
        :raises KeyError: If the response does not exist or has been deleted.
        """
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is None or entry.deleted or entry.response is None:
                raise KeyError(f"response '{response_id}' not found")
            return deepcopy(entry.response)

    async def update_response(self, response: ResponseObject, *, isolation: IsolationContext | None = None) -> None:
        """Update a stored response envelope.

        Replaces the stored response with a deep copy and updates
        the execution snapshot.

        :param response: The response envelope with updated fields.
        :type response: ~azure.ai.agentserver.responses.models._generated.Response
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        :raises KeyError: If the response does not exist or has been deleted.
        """
        response_id = str(getattr(response, "id"))
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is None or entry.deleted:
                raise KeyError(f"response '{response_id}' not found")

            entry.response = deepcopy(response)
            entry.execution.set_response_snapshot(deepcopy(response))
            entry.output_item_ids = self._store_output_items_unlocked(response)

    async def delete_response(self, response_id: str, *, isolation: IsolationContext | None = None) -> None:
        """Delete a stored response envelope by identifier.

        Marks the entry as deleted and clears the response payload.

        :param response_id: The unique identifier of the response to delete.
        :type response_id: str
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        :raises KeyError: If the response does not exist or has already been deleted.
        """
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is None or entry.deleted:
                raise KeyError(f"response '{response_id}' not found")
            entry.deleted = True
            entry.response = None

    async def get_input_items(
        self,
        response_id: str,
        limit: int = 20,
        ascending: bool = False,
        after: str | None = None,
        before: str | None = None,
        *,
        isolation: IsolationContext | None = None,
    ) -> list[OutputItem]:
        """Retrieve input/history items for a response with basic cursor paging.

        Returns deep copies of stored items, combining history and input item IDs
        with optional cursor-based pagination.

        :param response_id: The unique identifier of the response whose items to fetch.
        :type response_id: str
        :param limit: Maximum number of items to return (clamped to 1–100). Defaults to 20.
        :type limit: int
        :param ascending: Whether to return items in ascending order. Defaults to False.
        :type ascending: bool
        :param after: Cursor ID; only return items after this ID.
        :type after: str | None
        :param before: Cursor ID; only return items before this ID.
        :type before: str | None
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :returns: A list of input/history items matching the pagination criteria.
        :rtype: list[OutputItem]
        :raises KeyError: If the response does not exist.
        :raises ValueError: If the response has been deleted.
        """
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is None:
                raise KeyError(f"response '{response_id}' not found")
            if entry.deleted:
                raise ValueError(f"response '{response_id}' has been deleted")

            item_ids = [
                *(entry.history_item_ids or []),
                *(entry.input_item_ids or []),
            ]
            ordered_ids = item_ids if ascending else list(reversed(item_ids))

            if after is not None:
                try:
                    ordered_ids = ordered_ids[ordered_ids.index(after) + 1 :]
                except ValueError:
                    pass
            if before is not None:
                try:
                    ordered_ids = ordered_ids[: ordered_ids.index(before)]
                except ValueError:
                    pass

            safe_limit = max(1, min(100, int(limit)))
            return [
                deepcopy(self._item_store[item_id])
                for item_id in ordered_ids[:safe_limit]
                if item_id in self._item_store
            ]

    async def get_items(
        self,
        item_ids: Iterable[str],
        *,
        isolation: IsolationContext | None = None,
    ) -> list[OutputItem | None]:
        """Retrieve items by ID, preserving request order.

        Returns deep copies of stored items. Missing IDs produce ``None`` entries.

        :param item_ids: The item identifiers to look up.
        :type item_ids: Iterable[str]
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :returns: A list of output items in the same order as *item_ids*; missing items are ``None``.
        :rtype: list[OutputItem | None]
        """
        async with self._locked():
            return [
                deepcopy(self._item_store[item_id]) if item_id in self._item_store else None for item_id in item_ids
            ]

    async def get_history_item_ids(
        self,
        previous_response_id: str | None,
        conversation_id: str | None,
        limit: int,
        *,
        isolation: IsolationContext | None = None,
    ) -> list[str]:
        """Resolve history item IDs from previous response and/or conversation scope.

        Collects history item IDs from the previous response chain and/or
        all responses within the given conversation, up to *limit*.

        :param previous_response_id: Optional response ID to chain history from.
        :type previous_response_id: str | None
        :param conversation_id: Optional conversation ID to scope history lookup.
        :type conversation_id: str | None
        :param limit: Maximum number of history item IDs to return.
        :type limit: int
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :returns: A list of history item IDs within the given scope.
        :rtype: list[str]
        """
        async with self._locked():
            resolved: list[str] = []

            if previous_response_id is not None:
                entry = self._entries.get(previous_response_id)
                if entry is not None and not entry.deleted:
                    # Resolve history chain for the previous response:
                    # return historyItemIds + inputItemIds + outputItemIds of the previous response
                    resolved.extend(entry.history_item_ids or [])
                    resolved.extend(entry.input_item_ids or [])
                    resolved.extend(entry.output_item_ids or [])

            if conversation_id is not None:
                for response_id in self._conversation_responses.get(conversation_id, []):
                    entry = self._entries.get(response_id)
                    if entry is None or entry.deleted:
                        continue
                    resolved.extend(entry.history_item_ids or [])
                    resolved.extend(entry.input_item_ids or [])
                    resolved.extend(entry.output_item_ids or [])

            if limit <= 0:
                return []
            return resolved[:limit]

    async def create_execution(self, execution: ResponseExecution, *, ttl_seconds: int | None = None) -> None:
        """Create a new execution and replay container for ``execution.response_id``.

        :param execution: The execution state to store.
        :type execution: ~azure.ai.agentserver.responses.models.runtime.ResponseExecution
        :keyword int or None ttl_seconds: Optional time-to-live in seconds for automatic expiration.
        :rtype: None
        :raises ValueError: If an entry with the same response ID already exists.
        """
        async with self._locked():
            if execution.response_id in self._entries:
                raise ValueError(f"response '{execution.response_id}' already exists")

            self._entries[execution.response_id] = _StoreEntry(
                execution=deepcopy(execution),
                replay=StreamReplayState(response_id=execution.response_id),
                expires_at=self._compute_expiry(ttl_seconds),
            )

    async def get_execution(self, response_id: str) -> ResponseExecution | None:
        """Get a defensive copy of execution state for ``response_id`` if present.

        :param response_id: The unique identifier of the response execution to retrieve.
        :type response_id: str
        :returns: A deep copy of the execution state, or ``None`` if not found.
        :rtype: ~azure.ai.agentserver.responses.models.runtime.ResponseExecution | None
        """
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is None:
                return None
            return deepcopy(entry.execution)

    async def set_response_snapshot(
        self,
        response_id: str,
        response: ResponseObject,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Set the latest response snapshot for an existing response execution.

        :param response_id: The unique identifier of the response to update.
        :type response_id: str
        :param response: The response snapshot to associate with the execution.
        :type response: ~azure.ai.agentserver.responses.models._generated.Response
        :keyword int or None ttl_seconds: Optional time-to-live in seconds to refresh expiration.
        :returns: ``True`` if the entry was found and updated, ``False`` otherwise.
        :rtype: bool
        """
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is None:
                return False

            entry.execution.set_response_snapshot(response)
            self._apply_ttl_unlocked(entry, ttl_seconds)
            return True

    async def transition_execution_status(
        self,
        response_id: str,
        next_status: ResponseStatus,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Transition execution state while preserving lifecycle invariants.

        :param response_id: The unique identifier of the response execution to transition.
        :type response_id: str
        :param next_status: The target status to transition to.
        :type next_status: ~azure.ai.agentserver.responses.models.runtime.ResponseStatus
        :keyword int or None ttl_seconds: Optional time-to-live in seconds to refresh expiration.
        :returns: ``True`` if the entry was found and transitioned, ``False`` otherwise.
        :rtype: bool
        """
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is None:
                return False

            entry.execution.transition_to(next_status)
            self._apply_ttl_unlocked(entry, ttl_seconds)
            return True

    async def set_cancel_requested(self, response_id: str, *, ttl_seconds: int | None = None) -> bool:
        """Mark cancellation requested and enforce lifecycle-safe cancel transitions.

        :param response_id: The unique identifier of the response to cancel.
        :type response_id: str
        :keyword int or None ttl_seconds: Optional time-to-live in seconds to refresh expiration.
        :returns: ``True`` if the entry was found and cancel was applied, ``False`` otherwise.
        :rtype: bool
        :raises ValueError: If the execution is already terminal in a non-cancelled state.
        """
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is None:
                return False

            self._apply_cancel_transition_unlocked(entry)
            self._apply_ttl_unlocked(entry, ttl_seconds)
            return True

    @staticmethod
    def _apply_cancel_transition_unlocked(entry: _StoreEntry) -> None:
        """Apply deterministic and lifecycle-safe cancellation status updates.

        Transitions the entry through ``queued -> in_progress -> cancelled`` when
        applicable, and sets the ``cancel_requested`` flag.

        :param entry: The store entry whose execution state will be updated.
        :type entry: _StoreEntry
        :rtype: None
        :raises ValueError: If the execution is in a terminal non-cancelled state.
        """
        status = entry.execution.status

        if status == "cancelled":
            entry.execution.cancel_requested = True
            entry.execution.updated_at = datetime.now(timezone.utc)
            return

        if status in {"completed", "failed", "incomplete"}:
            raise ValueError(f"cannot cancel terminal execution in status '{status}'")

        if status == "queued":
            entry.execution.transition_to("in_progress")

        entry.execution.transition_to("cancelled")
        entry.execution.cancel_requested = True

    async def append_stream_event(
        self,
        response_id: str,
        event: StreamEventRecord,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Append one stream event to replay state for an existing execution.

        :param response_id: The unique identifier of the response to append the event to.
        :type response_id: str
        :param event: The stream event record to append.
        :type event: ~azure.ai.agentserver.responses.models.runtime.StreamEventRecord
        :keyword int or None ttl_seconds: Optional time-to-live in seconds to refresh expiration.
        :returns: ``True`` if the entry was found and the event was appended, ``False`` otherwise.
        :rtype: bool
        """
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is None:
                return False

            entry.replay.append(deepcopy(event))
            self._apply_ttl_unlocked(entry, ttl_seconds)
            return True

    async def get_replay_events(self, response_id: str) -> list[StreamEventRecord] | None:
        """Get defensive copies of replay events for ``response_id``, filtering out expired events.

        Events older than the entry's ``replay_event_ttl_seconds`` (default 600s / 10 minutes,
        per spec B35) are excluded from the returned list.

        :param response_id: The unique identifier of the response whose events to retrieve.
        :type response_id: str
        :returns: A list of deep-copied stream event records, or ``None`` if not found.
        :rtype: list[~azure.ai.agentserver.responses.models.runtime.StreamEventRecord] | None
        """
        async with self._locked():
            entry = self._entries.get(response_id)
            if entry is None:
                return None
            cutoff = datetime.now(timezone.utc) - timedelta(seconds=entry.replay_event_ttl_seconds)
            live = [e for e in entry.replay.events if e.emitted_at >= cutoff]
            return deepcopy(live)

    async def delete(self, response_id: str) -> bool:
        """Delete all state for a response ID if present.

        Removes the entry entirely from the store (unlike ``delete_response``
        which soft-deletes).

        :param response_id: The unique identifier of the response to remove.
        :type response_id: str
        :returns: ``True`` if an entry was found and removed, ``False`` otherwise.
        :rtype: bool
        """
        async with self._locked():
            self._stream_events.pop(response_id, None)
            return self._entries.pop(response_id, None) is not None

    async def save_stream_events(
        self,
        response_id: str,
        events: list[ResponseStreamEvent],
        *,
        isolation: IsolationContext | None = None,
    ) -> None:
        """Persist the complete ordered list of SSE events for ``response_id``.

        Each event is stamped with ``_saved_at`` (UTC) so that :meth:`get_stream_events`
        can enforce per-event replay TTL (B35).

        :param response_id: The unique identifier of the response.
        :type response_id: str
        :param events: Ordered list of event instances.
        :type events: list[ResponseStreamEvent]
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        """
        now = datetime.now(timezone.utc)
        stamped: list[ResponseStreamEvent] = []
        for ev in events:
            copy = deepcopy(ev)
            copy.setdefault("_saved_at", now)
            stamped.append(copy)
        async with self._locked():
            self._stream_events[response_id] = stamped

    async def get_stream_events(
        self,
        response_id: str,
        *,
        isolation: IsolationContext | None = None,
    ) -> list[ResponseStreamEvent] | None:
        """Retrieve the persisted SSE events for ``response_id``, excluding expired events.

        Events older than the entry's ``replay_event_ttl_seconds`` (default 600s / 10 minutes,
        per spec B35) are filtered out.

        :param response_id: The unique identifier of the response whose events to retrieve.
        :type response_id: str
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :returns: A deep-copied list of event instances, or ``None`` if not found.
        :rtype: list[ResponseStreamEvent] | None
        """
        async with self._locked():
            events = self._stream_events.get(response_id)
            if events is None:
                return None
            entry = self._entries.get(response_id)
            ttl = entry.replay_event_ttl_seconds if entry is not None else _DEFAULT_REPLAY_EVENT_TTL_SECONDS
            cutoff = datetime.now(timezone.utc) - timedelta(seconds=ttl)
            live = [e for e in events if e.get("_saved_at", cutoff) >= cutoff]
            return deepcopy(live)

    async def delete_stream_events(
        self,
        response_id: str,
        *,
        isolation: IsolationContext | None = None,
    ) -> None:
        """Delete persisted SSE events for ``response_id``.

        :param response_id: The unique identifier of the response whose events to remove.
        :type response_id: str
        :keyword isolation: Isolation context for multi-tenant partitioning.
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        """
        async with self._locked():
            self._stream_events.pop(response_id, None)

    async def purge_expired(self, *, now: datetime | None = None) -> int:
        """Remove expired entries and return count.

        :keyword ~datetime.datetime or None now: Optional override for the current time (useful for testing).
        :returns: The number of expired entries that were removed.
        :rtype: int
        """
        async with self._locked():
            return self._purge_expired_unlocked(now=now)

    @staticmethod
    def _compute_expiry(ttl_seconds: int | None) -> datetime | None:
        """Compute an absolute expiration timestamp from a TTL.

        :param ttl_seconds: Time-to-live in seconds, or ``None`` for no expiration.
        :type ttl_seconds: int | None
        :returns: A UTC datetime for the expiry, or ``None`` if *ttl_seconds* is ``None``.
        :rtype: ~datetime.datetime | None
        :raises ValueError: If *ttl_seconds* is <= 0.
        """
        if ttl_seconds is None:
            return None
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be > 0 when set")
        return datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

    def _apply_ttl_unlocked(self, entry: _StoreEntry, ttl_seconds: int | None) -> None:
        """Update entry expiration timestamp when a TTL value is supplied.

        :param entry: The store entry whose expiration to update.
        :type entry: _StoreEntry
        :param ttl_seconds: Time-to-live in seconds, or ``None`` to leave unchanged.
        :type ttl_seconds: int | None
        :rtype: None
        """
        if ttl_seconds is not None:
            entry.expires_at = self._compute_expiry(ttl_seconds)

    def _purge_expired_unlocked(self, *, now: datetime | None = None) -> int:
        """Remove expired entries without acquiring the lock.

        :keyword ~datetime.datetime or None now: Optional override for the current time (useful for testing).
        :returns: The number of expired entries that were removed.
        :rtype: int
        """
        current_time = now or datetime.now(timezone.utc)
        expired_ids = [
            response_id
            for response_id, entry in self._entries.items()
            if entry.expires_at is not None and entry.expires_at <= current_time
        ]

        for response_id in expired_ids:
            del self._entries[response_id]
            self._stream_events.pop(response_id, None)

        # Prune orphaned stream events that have no corresponding entry.
        # This covers the standalone stream-only usage where
        # InMemoryResponseProvider is auto-provisioned as a fallback and
        # only receives save_stream_events() calls (no _entries).
        orphaned_ids = [rid for rid in self._stream_events if rid not in self._entries]
        cutoff = current_time - timedelta(seconds=_DEFAULT_REPLAY_EVENT_TTL_SECONDS)
        for rid in orphaned_ids:
            events = self._stream_events[rid]
            live = [e for e in events if e.get("_saved_at", cutoff) >= cutoff]
            if live:
                self._stream_events[rid] = live
            else:
                del self._stream_events[rid]

        return len(expired_ids)

    def _store_output_items_unlocked(self, response: ResponseObject) -> list[str]:
        """Extract output items from a response, store them in the item store, and return their IDs.

        Must be called while holding ``self._lock``.

        :param response: The response envelope whose output items should be stored.
        :type response: ~azure.ai.agentserver.responses.models._generated.Response
        :returns: Ordered list of output item IDs.
        :rtype: list[str]
        """
        output = getattr(response, "output", None)
        if not output:
            return []
        output_ids: list[str] = []
        for item in output:
            item_id = self._extract_item_id(item)
            if item_id is not None:
                self._item_store[item_id] = deepcopy(item)
                output_ids.append(item_id)
        return output_ids

    @staticmethod
    def _extract_item_id(item: Any) -> str | None:
        """Extract item identifier from object-like or mapping-like values.

        Supports both dict-like (``item["id"]``) and attribute-like (``item.id``)
        access patterns.

        :param item: The item to extract an ID from.
        :type item: Any
        :returns: The string ID if found, or ``None``.
        :rtype: str | None
        """
        if item is None:
            return None
        if isinstance(item, dict):
            value = item.get("id")
            return str(value) if value is not None else None
        value = getattr(item, "id", None)
        return str(value) if value is not None else None

    @staticmethod
    def _resolve_mode_flags_from_response(response: ResponseObject) -> ResponseModeFlags:
        """Build mode flags from a response snapshot where available.

        :param response: The response envelope to extract mode flags from.
        :type response: ~azure.ai.agentserver.responses.models._generated.Response
        :returns: Mode flags derived from the response's ``stream``, ``store``, and ``background`` attributes.
        :rtype: ~azure.ai.agentserver.responses.models.runtime.ResponseModeFlags
        """
        return ResponseModeFlags(
            stream=bool(getattr(response, "stream", False)),
            store=bool(getattr(response, "store", True)),
            background=bool(getattr(response, "background", False)),
        )
