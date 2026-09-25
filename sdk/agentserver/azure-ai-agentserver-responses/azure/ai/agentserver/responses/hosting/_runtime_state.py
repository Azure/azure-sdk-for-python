# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Runtime state management for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from copy import deepcopy
from typing import Any, cast


from ..models.runtime import ResponseExecution
from ..streaming._helpers import strip_nulls
from .. import models as _public_models


_RuntimeKey = tuple[str | None, str]


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
        self._draining = False
        self._lock = asyncio.Lock()

    async def reserve(self, response_id: str, user_id_key: str | None) -> bool:
        """Reserve a caller-scoped response ID before starting execution.

        :param response_id: The caller-selected response ID.
        :type response_id: str
        :param user_id_key: The authenticated user partition, or ``None`` for anonymous.
        :type user_id_key: str | None
        :return: ``True`` when reserved; ``False`` when already live or reserved.
        :rtype: bool
        """
        key = _runtime_key(response_id, user_id_key)
        async with self._lock:
            if any(existing_key[1] == response_id for existing_key in self._records):
                return False
            if any(existing_key[1] == response_id for existing_key in self._pending_records):
                return False
            if any(existing_key[1] == response_id for existing_key in self._reservations):
                return False
            self._reservations.add(key)
            return True

    async def release_reservation(self, response_id: str, user_id_key: str | None) -> None:
        """Release an unused caller-scoped response-ID reservation."""
        async with self._lock:
            self._reservations.discard(_runtime_key(response_id, user_id_key))

    async def add(self, record: ResponseExecution) -> None:
        """Add or replace an execution record in the store.

        :param record: The execution record to store.
        :type record: ResponseExecution
        :return: None
        :rtype: None
        """
        key = _runtime_key(record.response_id, record.user_id_key)
        async with self._lock:
            self._reservations.discard(key)
            self._pending_records.pop(key, None)
            self._records[key] = record
            self._deleted_response_ids.discard(key)

    async def add_pending(self, record: ResponseExecution) -> bool:
        """Track accepted unpublished work unless shutdown has started.

        :param record: The execution awaiting its first response event.
        :type record: ResponseExecution
        :return: ``True`` when registered, ``False`` when shutdown is already draining.
        :rtype: bool
        """
        key = _runtime_key(record.response_id, record.user_id_key)
        async with self._lock:
            if self._draining:
                return False
            if key in self._records or key in self._pending_records:
                return False
            self._reservations.discard(key)
            self._pending_records[key] = record
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
        :return: None
        :rtype: None
        """
        async with self._lock:
            self._pending_records.pop(_runtime_key(response_id, user_id_key), None)

    async def get(self, response_id: str, user_id_key: str | None = None) -> ResponseExecution | None:
        """Look up an execution record by response ID.

        :param response_id: The response ID to look up.
        :type response_id: str
        :return: The matching execution record, or ``None`` if not found.
        :rtype: ResponseExecution | None
        """
        async with self._lock:
            return self._records.get(_runtime_key(response_id, user_id_key))

    async def contains_live_response_id(self, response_id: str) -> bool:
        """Return whether any user partition currently owns this live response ID."""
        async with self._lock:
            return any(key[1] == response_id for key in self._records) or any(
                key[1] == response_id for key in self._pending_records
            )

    async def is_deleted(self, response_id: str, user_id_key: str | None = None) -> bool:
        """Check whether a response ID has been deleted.

        :param response_id: The response ID to check.
        :type response_id: str
        :return: ``True`` if the response was previously deleted.
        :rtype: bool
        """
        async with self._lock:
            return _runtime_key(response_id, user_id_key) in self._deleted_response_ids

    async def delete(self, response_id: str, user_id_key: str | None = None) -> bool:
        """Delete an execution record by response ID.

        :param response_id: The response ID to delete.
        :type response_id: str
        :return: ``True`` if the record was found and deleted, ``False`` otherwise.
        :rtype: bool
        """
        key = _runtime_key(response_id, user_id_key)
        async with self._lock:
            record = self._records.pop(key, None)
            if record is None:
                return False
            self._deleted_response_ids.add(key)
            return True

    _TERMINAL_STATUSES = frozenset({"completed", "failed", "cancelled", "incomplete"})

    async def try_evict(self, response_id: str, user_id_key: str | None = None) -> bool:
        """Evict a terminal record from in-memory state to free memory.

        Unlike :meth:`delete`, eviction does **not** mark the response as
        deleted — it simply removes the runtime record so that subsequent
        requests fall through to the resilient provider (storage).

        Only records in a terminal status are evicted.  Non-terminal records
        are left untouched so that in-flight operations remain correct.

        :param response_id: The response ID to evict.
        :type response_id: str
        :return: ``True`` if the record was evicted, ``False`` otherwise.
        :rtype: bool
        """
        key = _runtime_key(response_id, user_id_key)
        async with self._lock:
            record = self._records.get(key)
            if record is None:
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
        :return: None
        :rtype: None
        """
        async with self._lock:
            self._deleted_response_ids.add(_runtime_key(response_id, user_id_key))

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
