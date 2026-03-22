# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Runtime state management for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .._handlers import RuntimeResponseContext
from ..models import _generated as generated_models


@dataclass(slots=True)
class _ExecutionRecord:  # pylint: disable=too-many-instance-attributes
    response_id: str
    agent_reference: dict[str, Any]
    stream: bool
    store: bool
    background: bool
    replay_enabled: bool
    visible_via_get: bool
    status: str
    model: str | None
    response_payload: dict[str, Any] | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
    cancel_signal: asyncio.Event = field(default_factory=asyncio.Event)
    background_runner: Any | None = None
    background_execution_started: bool = False
    input_items: list[dict[str, Any]] = field(default_factory=list)
    previous_response_id: str | None = None
    response_context: RuntimeResponseContext | None = None

    def to_snapshot(self) -> dict[str, Any]:
        """Build a normalized response snapshot dictionary from this record.

        :return: A deep-copied, normalized response payload dictionary.
        :rtype: dict[str, Any]
        """
        def _normalize_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
            normalized = generated_models.Response(payload).as_dict()
            if isinstance(normalized, dict):
                return normalized
            return payload

        if isinstance(self.response_payload, dict):
            payload = deepcopy(self.response_payload)
            payload.setdefault("id", self.response_id)
            payload.setdefault("response_id", self.response_id)
            payload.setdefault("agent_reference", deepcopy(self.agent_reference))
            payload.setdefault("object", "response")
            payload["status"] = self.status
            if self.model is not None:
                payload.setdefault("model", self.model)
            return _normalize_snapshot(payload)

        payload = {
            "id": self.response_id,
            "response_id": self.response_id,
            "agent_reference": deepcopy(self.agent_reference),
            "object": "response",
            "status": self.status,
            "model": self.model,
        }
        return _normalize_snapshot(payload)


class _RuntimeState:
    """In-memory store for response execution records."""

    def __init__(self) -> None:
        """Initialize the runtime state with empty record and deletion sets."""
        self._records: dict[str, _ExecutionRecord] = {}
        self._deleted_response_ids: set[str] = set()
        self._lock = asyncio.Lock()

    async def add(self, record: _ExecutionRecord) -> None:
        """Add or replace an execution record in the store.

        :param record: The execution record to store.
        :type record: _ExecutionRecord
        :return: None
        :rtype: None
        """
        async with self._lock:
            self._records[record.response_id] = record
            self._deleted_response_ids.discard(record.response_id)

    async def get(self, response_id: str) -> _ExecutionRecord | None:
        """Look up an execution record by response ID.

        :param response_id: The response ID to look up.
        :type response_id: str
        :return: The matching execution record, or ``None`` if not found.
        :rtype: _ExecutionRecord | None
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

    async def get_input_items(self, response_id: str) -> list[dict[str, Any]]:
        """Retrieve the full input item chain for a response, including ancestors.

        Walks the ``previous_response_id`` chain to build the complete ordered
        list of input items.

        :param response_id: The response ID whose input items to retrieve.
        :type response_id: str
        :return: Ordered list of deep-copied input item dictionaries.
        :rtype: list[dict[str, Any]]
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

            history: list[dict[str, Any]] = []
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

    async def list_records(self) -> list[_ExecutionRecord]:
        """Return a snapshot list of all execution records in the store.

        :return: List of all current execution records.
        :rtype: list[_ExecutionRecord]
        """
        async with self._lock:
            return list(self._records.values())
