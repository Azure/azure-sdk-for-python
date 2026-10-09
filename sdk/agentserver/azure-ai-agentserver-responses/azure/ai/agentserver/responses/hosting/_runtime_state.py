# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Runtime state management for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
from copy import deepcopy
from typing import Any, cast


from ..models.runtime import ResponseExecution
from .._response_context import ResponseContext
from ..streaming._helpers import strip_nulls
from .. import models as _public_models


_RuntimeKey = tuple[str | None, str]
logger = logging.getLogger(__name__)


def _runtime_key(response_id: str, user_id_key: str | None) -> _RuntimeKey:
    return (user_id_key, response_id)


def _json_safe_agent_reference(value: Any) -> dict[str, Any]:
    """Normalize an agent reference to a plain JSON-safe dict for snapshots.

    The gateway-injected ``AgentReference`` model is a Mapping but is not
    ``json.dumps``-serializable; the status-only fallback snapshot must therefore
    coerce it to a dict before it reaches a ``JSONResponse``.

    :param value: An ``AgentReference`` model, a mapping, or ``None``.
    :type value: Any
    :returns: A JSON-safe dict (``{}`` when absent).
    :rtype: dict[str, Any]
    """
    if not value:
        return {}
    if isinstance(value, dict):
        return dict(value)
    as_dict = getattr(value, "as_dict", None)
    if callable(as_dict):
        return cast("dict[str, Any]", as_dict())
    try:
        return dict(value)
    except (TypeError, ValueError):
        return {
            "type": getattr(value, "type", "agent_reference"),
            "name": getattr(value, "name", None),
            "version": getattr(value, "version", None),
        }


class _RuntimeState:
    """In-memory store for response execution records."""

    def __init__(self) -> None:
        """Initialize the runtime state with empty record and deletion sets."""
        self._records: dict[_RuntimeKey, ResponseExecution] = {}
        self._pending_records: dict[_RuntimeKey, ResponseExecution] = {}
        self._deleted_response_ids: set[_RuntimeKey] = set()
        self._reservations: set[_RuntimeKey] = set()
        self._publication_contexts: dict[_RuntimeKey, ResponseContext | None] = {}
        self._deletions: set[_RuntimeKey] = set()
        self._retained_deletions: set[_RuntimeKey] = set()
        self._draining = False
        self._lock = asyncio.Lock()

    async def reserve(
        self,
        response_id: str,
        user_id_key: str | None,
        *,
        recovery: bool = False,
        incarnation_id: str | None = None,
        publication_context: ResponseContext | None = None,
    ) -> bool:
        """Reserve a caller-scoped response ID before starting execution.

        :param response_id: The caller-selected response ID.
        :type response_id: str
        :param user_id_key: The authenticated user partition, or ``None`` for anonymous.
        :type user_id_key: str | None
        :keyword recovery: Guard recovered admission and retire an exact stopped nonterminal execution.
        :paramtype recovery: bool
        :keyword incarnation_id: Recovery incarnation already validated against durable task state.
        :paramtype incarnation_id: str | None
        :keyword publication_context: The fresh request's exact runtime publication owner.
        :paramtype publication_context: ResponseContext | None
        :return: ``True`` when reserved; ``False`` when already live or reserved.
        :rtype: bool
        """
        key = _runtime_key(response_id, user_id_key)
        async with self._lock:
            record = self._records.get(key)
            stale_execution = (
                recovery
                and record is not None
                and not record.is_terminal
                and record.execution_task is not None
                and record.execution_task.done()
            )
            if record is not None and not stale_execution:
                return False
            if recovery and self._draining:
                return False
            if recovery and incarnation_id is None and key in self._deleted_response_ids:
                return False
            if (
                key in self._pending_records
                or key in self._reservations
                or key in self._deletions
                or key in self._retained_deletions
            ):
                return False
            if stale_execution:
                del self._records[key]
            self._reservations.add(key)
            self._publication_contexts[key] = publication_context
            return True

    async def release_reservation(self, response_id: str, user_id_key: str | None) -> None:
        """Release an unused caller-scoped response-ID reservation.

        :param response_id: The reserved response identifier.
        :type response_id: str
        :param user_id_key: The user partition, or ``None`` for anonymous.
        :type user_id_key: str | None
        :rtype: None
        """
        async with self._lock:
            self._reservations.discard(_runtime_key(response_id, user_id_key))
            self._publication_contexts.pop(_runtime_key(response_id, user_id_key), None)

    async def begin_deletion(self, response_id: str, user_id_key: str | None) -> bool:
        """Block new creates while a caller deletes an existing response.

        :param response_id: The response identifier to delete.
        :type response_id: str
        :param user_id_key: The caller's user partition.
        :type user_id_key: str | None
        :return: Whether deletion acquired the scoped lifecycle reservation.
        :rtype: bool
        """
        key = _runtime_key(response_id, user_id_key)
        async with self._lock:
            if key in self._deletions:
                return False
            if key not in self._records and (key in self._reservations or key in self._pending_records):
                return False
            self._deletions.add(key)
            return True

    async def end_deletion(self, response_id: str, user_id_key: str | None) -> None:
        """Release a deletion reservation without releasing a create reservation.

        :param response_id: The response identifier being deleted.
        :type response_id: str
        :param user_id_key: The caller's user partition.
        :type user_id_key: str | None
        :rtype: None
        """
        async with self._lock:
            self._deletions.discard(_runtime_key(response_id, user_id_key))

    async def retain_for_deletion(self, record: ResponseExecution) -> bool:
        """Retain exact authorized ownership until all deletion steps succeed.

        :param record: The existing execution or authorized provider snapshot.
        :type record: ResponseExecution
        :return: Whether the record was retained under the deletion reservation.
        :rtype: bool
        """
        key = _runtime_key(record.response_id, record.user_id_key)
        async with self._lock:
            existing = self._records.get(key)
            if key not in self._deletions or (existing is not None and existing is not record):
                return False
            self._records[key] = record
            self._retained_deletions.add(key)
            return True

    async def is_retained_for_deletion(self, response_id: str, user_id_key: str | None) -> bool:
        """Check whether authorized cleanup is awaiting a retry.

        :param response_id: The response identifier.
        :type response_id: str
        :param user_id_key: The caller's user partition.
        :type user_id_key: str | None
        :return: Whether deletion owns the retained record.
        :rtype: bool
        """
        async with self._lock:
            return _runtime_key(response_id, user_id_key) in self._retained_deletions

    async def add(self, record: ResponseExecution, *, expected_record: ResponseExecution | None = None) -> bool:
        """Publish only within the current execution's scoped lifecycle ownership.

        :param record: The execution record to store.
        :type record: ResponseExecution
        :keyword expected_record: An exact predecessor for an intentional replacement.
        :paramtype expected_record: ResponseExecution | None
        :return: Whether publication succeeded without changing another lifecycle.
        :rtype: bool
        """
        key = _runtime_key(record.response_id, record.user_id_key)
        async with self._lock:
            existing = self._records.get(key)
            pending = self._pending_records.get(key)
            context = record.response_context
            reserved_context = self._publication_contexts.get(key)
            blocked = (
                key in self._deletions
                or key in self._retained_deletions
                or (key in self._deleted_response_ids and key not in self._publication_contexts)
                or (reserved_context is not None and context is not reserved_context)
                or (expected_record is not None and existing is not expected_record and pending is not expected_record)
            )
            for owner in (existing, pending):
                if owner is not None and owner is not record and owner is not expected_record:
                    blocked = blocked or context is None or context is not owner.response_context
            if blocked:
                logger.warning(
                    "Rejected runtime publication during conflicting response lifecycle: %s", record.response_id
                )
                return False
            self._pending_records.pop(key, None)
            self._records[key] = record
            self._deleted_response_ids.discard(key)
            if key in self._publication_contexts:
                self._publication_contexts[key] = context
            return True

    async def add_pending(self, record: ResponseExecution) -> bool:
        """Track accepted unpublished work unless shutdown has started.

        :param record: The execution awaiting its first response event.
        :type record: ResponseExecution
        :return: Whether this exact execution can be tracked within the current lifecycle.
        :rtype: bool
        """
        key = _runtime_key(record.response_id, record.user_id_key)
        async with self._lock:
            if self._draining:
                return False
            if (
                key in self._records
                or key in self._pending_records
                or key in self._deletions
                or key in self._retained_deletions
            ):
                return False
            if key in self._deleted_response_ids and key not in self._publication_contexts:
                return False
            owner = self._publication_contexts.get(key)
            if owner is not None and record.response_context is not owner:
                return False
            self._pending_records[key] = record
            if key in self._publication_contexts:
                self._publication_contexts[key] = record.response_context
            return True

    async def begin_draining(self) -> list[ResponseExecution]:
        """Atomically reject new pending work and snapshot active executions.

        :return: Published and pending executions accepted before shutdown.
        :rtype: list[ResponseExecution]
        """
        async with self._lock:
            self._draining = True
            return list(self._records.values()) + list(self._pending_records.values())

    async def discard_pending(self, response_id: str, user_id_key: str | None = None) -> None:
        """Discard shutdown bookkeeping for an execution that never published.

        :param response_id: The pending execution's response ID.
        :type response_id: str
        :param user_id_key: The user partition, or ``None`` for anonymous.
        :type user_id_key: str | None
        :return: None
        :rtype: None
        """
        async with self._lock:
            self._pending_records.pop(_runtime_key(response_id, user_id_key), None)

    async def get(self, response_id: str, user_id_key: str | None = None) -> ResponseExecution | None:
        """Look up an execution record by response ID.

        :param response_id: The response ID to look up.
        :type response_id: str
        :param user_id_key: The user partition, or ``None`` for anonymous.
        :type user_id_key: str | None
        :return: The matching execution record, or ``None`` if not found.
        :rtype: ResponseExecution | None
        """
        async with self._lock:
            return self._records.get(_runtime_key(response_id, user_id_key))

    async def is_deleted(self, response_id: str, user_id_key: str | None = None) -> bool:
        """Check whether a response ID has been deleted.

        :param response_id: The response ID to check.
        :type response_id: str
        :param user_id_key: The user partition, or ``None`` for anonymous.
        :type user_id_key: str | None
        :return: ``True`` if the response was previously deleted.
        :rtype: bool
        """
        async with self._lock:
            return _runtime_key(response_id, user_id_key) in self._deleted_response_ids

    async def delete(
        self,
        response_id: str,
        user_id_key: str | None = None,
        *,
        expected_record: ResponseExecution | None = None,
    ) -> bool:
        """Delete an execution record by response ID.

        :param response_id: The response ID to delete.
        :type response_id: str
        :param user_id_key: The user partition, or ``None`` for anonymous.
        :type user_id_key: str | None
        :keyword expected_record: Only remove this exact record when supplied.
        :paramtype expected_record: ResponseExecution | None
        :return: ``True`` if the record was found and deleted, ``False`` otherwise.
        :rtype: bool
        """
        key = _runtime_key(response_id, user_id_key)
        async with self._lock:
            record = self._records.get(key)
            if record is None or (expected_record is not None and record is not expected_record):
                return False
            del self._records[key]
            self._retained_deletions.discard(key)
            self._deleted_response_ids.add(key)
            self._publication_contexts.pop(key, None)
            return True

    _TERMINAL_STATUSES = frozenset({"completed", "failed", "cancelled", "incomplete"})

    async def try_evict(
        self, response_id: str, user_id_key: str | None = None, *, expected_record: ResponseExecution | None = None
    ) -> bool:
        """Evict a terminal record from in-memory state to free memory.

        Unlike :meth:`delete`, eviction does **not** mark the response as
        deleted — it simply removes the runtime record so that subsequent
        requests fall through to the resilient provider (storage).

        Only records in a terminal status are evicted.  Non-terminal records
        are left untouched so that in-flight operations remain correct.
        In-flight and failed deletion ownership is retained for cleanup retries.

        :param response_id: The response ID to evict.
        :type response_id: str
        :param user_id_key: The user partition, or ``None`` for anonymous.
        :type user_id_key: str | None
        :keyword expected_record: Evict only this exact execution when supplied.
        :paramtype expected_record: ResponseExecution | None
        :return: ``True`` if the record was evicted, ``False`` otherwise.
        :rtype: bool
        """
        key = _runtime_key(response_id, user_id_key)
        async with self._lock:
            if key in self._deletions or key in self._retained_deletions:
                return False
            record = self._records.get(key)
            if record is None or (expected_record is not None and record is not expected_record):
                return False
            if record.status not in self._TERMINAL_STATUSES:
                return False
            del self._records[key]
            return True

    async def mark_deleted(self, response_id: str, user_id_key: str | None = None) -> None:
        """Mark a response ID as deleted without requiring a runtime record.

        Used by the delete handler's provider fallback path when the record
        has already been evicted from memory but still exists in persistent storage.

        :param response_id: The response ID to mark as deleted.
        :type response_id: str
        :param user_id_key: The user partition, or ``None`` for anonymous.
        :type user_id_key: str | None
        :return: None
        :rtype: None
        """
        async with self._lock:
            key = _runtime_key(response_id, user_id_key)
            self._deleted_response_ids.add(key)
            self._publication_contexts.pop(key, None)

    @staticmethod
    def check_user_isolation(stored_key: str | None, request_user_id_key: str | None) -> bool:
        """Check whether the request user ID matches the creation-time key.

        Returns ``True`` if the request is allowed, ``False`` if it should be
        rejected as not-found to prevent cross-user information leakage.

        :param stored_key: The user ID key stored at creation time, or ``None``.
        :type stored_key: str | None
        :param request_user_id_key: The user ID key from the incoming request, or ``None``.
        :type request_user_id_key: str | None
        :return: ``True`` if allowed, ``False`` if isolation mismatch.
        :rtype: bool
        """
        return stored_key == request_user_id_key

    async def get_input_items(
        self, response_id: str, user_id_key: str | None = None
    ) -> list[_public_models.OutputItem]:
        """Retrieve the full input item chain for a response, including ancestors.

        Walks the ``previous_response_id`` chain to build the complete ordered
        list of input items.

        :param response_id: The response ID whose input items to retrieve.
        :type response_id: str
        :param user_id_key: The user partition, or ``None`` for anonymous.
        :type user_id_key: str | None
        :return: Ordered list of deep-copied output items.
        :rtype: list[OutputItem]
        :raises ValueError: If the response has been deleted.
        :raises KeyError: If the response is not found or not visible.
        """
        key = _runtime_key(response_id, user_id_key)
        async with self._lock:
            record = self._records.get(key)
            if record is None:
                if key in self._deleted_response_ids:
                    raise ValueError(f"response '{response_id}' has been deleted")
                raise KeyError(f"response '{response_id}' not found")

            if not record.visible_via_get:
                raise KeyError(f"response '{response_id}' not found")

            history: list[_public_models.OutputItem] = []
            cursor = record.previous_response_id
            visited: set[_RuntimeKey] = set()

            while isinstance(cursor, str) and cursor:
                cursor_key = _runtime_key(cursor, user_id_key)
                if cursor_key in visited:
                    break
                visited.add(cursor_key)
                previous = self._records.get(cursor_key)
                if previous is None:
                    break
                history = [*deepcopy(previous.input_items), *history]
                cursor = previous.previous_response_id

            return [*history, *deepcopy(record.input_items)]

    async def list_records(self) -> list[ResponseExecution]:
        """Return published and pending execution records for shutdown draining.

        :return: List of all current execution records, including unpublished work.
        :rtype: list[ResponseExecution]
        """
        async with self._lock:
            return list(self._records.values()) + list(self._pending_records.values())

    @staticmethod
    def to_snapshot(execution: ResponseExecution) -> dict[str, Any]:
        """Build a normalized response snapshot dictionary from an execution.

        Uses the execution's response dict directly when a response snapshot is
        available.
        Falls back to a minimal status-only dict when no response has been set yet.

        :param execution: The execution whose response snapshot to build.
        :type execution: ResponseExecution
        :return: A normalized response payload dictionary.
        :rtype: dict[str, Any]
        """
        if execution.response is not None:
            result: dict[str, Any] = deepcopy(dict(execution.response))
            result.setdefault("id", execution.response_id)
            result.setdefault("response_id", execution.response_id)
            result.setdefault("object", "response")
            result["status"] = execution.status
            # S-038 / S-040: forcibly stamp session & conversation on every snapshot
            if execution.agent_session_id is not None:
                result["agent_session_id"] = execution.agent_session_id
            if execution.conversation_id is not None:
                result["conversation"] = {"id": execution.conversation_id}
            return strip_nulls(result)
        snapshot: dict[str, Any] = {
            "id": execution.response_id,
            "response_id": execution.response_id,
            "object": "response",
            "status": execution.status,
            "created_at": int(execution.created_at.timestamp()),
            "output": [],
            "model": execution.initial_model,
            "agent_reference": _json_safe_agent_reference(execution.initial_agent_reference),
        }
        # S-038 / S-040: forcibly stamp session & conversation on fallback path
        if execution.agent_session_id is not None:
            snapshot["agent_session_id"] = execution.agent_session_id
        if execution.conversation_id is not None:
            snapshot["conversation"] = {"id": execution.conversation_id}
        return snapshot
