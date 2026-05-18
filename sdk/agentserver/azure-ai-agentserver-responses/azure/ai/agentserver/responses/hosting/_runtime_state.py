# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Runtime state management for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from copy import deepcopy
from typing import Any

from ..models._generated import OutputItem
from ..models.runtime import ResponseExecution
from ..streaming._helpers import strip_nulls


class _RuntimeState:
    """In-memory store for response execution records."""

    def __init__(self) -> None:
        """Initialize the runtime state with empty record and deletion sets."""
        self._records: dict[str, ResponseExecution] = {}
        self._deleted_response_ids: set[str] = set()
        self._lock = asyncio.Lock()

    async def add(self, record: ResponseExecution) -> None:
        """Add or replace an execution record in the store.

        :param record: The execution record to store.
        :type record: ResponseExecution
        :return: None
        :rtype: None
        """
        async with self._lock:
            self._records[record.response_id] = record
            self._deleted_response_ids.discard(record.response_id)

    async def get(self, response_id: str) -> ResponseExecution | None:
        """Look up an execution record by response ID.

        :param response_id: The response ID to look up.
        :type response_id: str
        :return: The matching execution record, or ``None`` if not found.
        :rtype: ResponseExecution | None
        """
        async with self._lock:
            return self._records.get(response_id)

    async def is_deleted(self, response_id: str) -> bool:
        """Check whether a response ID has been deleted.

        :param response_id: The response ID to check.
        :type response_id: str
        :return: ``True`` if the response was previously deleted.
        :rtype: bool
        """
        async with self._lock:
            return response_id in self._deleted_response_ids

    async def delete(self, response_id: str) -> bool:
        """Delete an execution record by response ID.

        :param response_id: The response ID to delete.
        :type response_id: str
        :return: ``True`` if the record was found and deleted, ``False`` otherwise.
        :rtype: bool
        """
        async with self._lock:
            record = self._records.pop(response_id, None)
            if record is None:
                return False
            self._deleted_response_ids.add(response_id)
            return True

    _TERMINAL_STATUSES = frozenset({"completed", "failed", "cancelled", "incomplete"})

    async def try_evict(self, response_id: str) -> bool:
        """Evict a terminal record from in-memory state to free memory.

        Unlike :meth:`delete`, eviction does **not** mark the response as
        deleted — it simply removes the runtime record so that subsequent
        requests fall through to the durable provider (storage).

        Only records in a terminal status are evicted.  Non-terminal records
        are left untouched so that in-flight operations remain correct.

        :param response_id: The response ID to evict.
        :type response_id: str
        :return: ``True`` if the record was evicted, ``False`` otherwise.
        :rtype: bool
        """
        async with self._lock:
            record = self._records.get(response_id)
            if record is None:
                return False
            if record.status not in self._TERMINAL_STATUSES:
                return False
            del self._records[response_id]
            return True

    async def mark_deleted(self, response_id: str) -> None:
        """Mark a response ID as deleted without requiring a runtime record.

        Used by the delete handler's provider fallback path when the record
        has already been evicted from memory but still exists in durable storage.

        :param response_id: The response ID to mark as deleted.
        :type response_id: str
        :return: None
        :rtype: None
        """
        async with self._lock:
            self._deleted_response_ids.add(response_id)

    @staticmethod
    def check_chat_isolation(stored_key: str | None, request_chat_key: str | None) -> bool:
        """Check whether the request chat key matches the creation-time key.

        Returns ``True`` if the request is allowed, ``False`` if it should be
        rejected as not-found to prevent cross-chat information leakage.

        No enforcement when the response was created without a key (backward compat).

        :param stored_key: The chat isolation key stored at creation time, or ``None``.
        :type stored_key: str | None
        :param request_chat_key: The chat key from the incoming request, or ``None``.
        :type request_chat_key: str | None
        :return: ``True`` if allowed, ``False`` if isolation mismatch.
        :rtype: bool
        """
        if stored_key is None:
            return True  # No enforcement when created without a key
        return stored_key == request_chat_key

    async def get_input_items(self, response_id: str) -> list[OutputItem]:
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
        async with self._lock:
            record = self._records.get(response_id)
            if record is None:
                if response_id in self._deleted_response_ids:
                    raise ValueError(f"response '{response_id}' has been deleted")
                raise KeyError(f"response '{response_id}' not found")

            if not record.visible_via_get:
                raise KeyError(f"response '{response_id}' not found")

            history: list[OutputItem] = []
            cursor = record.previous_response_id
            visited: set[str] = set()

            while isinstance(cursor, str) and cursor and cursor not in visited:
                visited.add(cursor)
                previous = self._records.get(cursor)
                if previous is None:
                    break
                history = [*deepcopy(previous.input_items), *history]
                cursor = previous.previous_response_id

            return [*history, *deepcopy(record.input_items)]

    async def list_records(self) -> list[ResponseExecution]:
        """Return a snapshot list of all execution records in the store.

        :return: List of all current execution records.
        :rtype: list[ResponseExecution]
        """
        async with self._lock:
            return list(self._records.values())

    @staticmethod
    def to_snapshot(execution: ResponseExecution) -> dict[str, Any]:
        """Build a normalized response snapshot dictionary from an execution.

        Uses ``execution.response.as_dict()`` directly when a response snapshot is
        available, avoiding an unnecessary ``Response(dict).as_dict()`` round-trip.
        Falls back to a minimal status-only dict when no response has been set yet.

        :param execution: The execution whose response snapshot to build.
        :type execution: ResponseExecution
        :return: A normalized response payload dictionary.
        :rtype: dict[str, Any]
        """
        if execution.response is not None:
            result: dict[str, Any] = execution.response.as_dict()
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
            "agent_reference": deepcopy(execution.initial_agent_reference) or {},
        }
        # S-038 / S-040: forcibly stamp session & conversation on fallback path
        if execution.agent_session_id is not None:
            snapshot["agent_session_id"] = execution.agent_session_id
        if execution.conversation_id is not None:
            snapshot["conversation"] = {"id": execution.conversation_id}
        return snapshot
