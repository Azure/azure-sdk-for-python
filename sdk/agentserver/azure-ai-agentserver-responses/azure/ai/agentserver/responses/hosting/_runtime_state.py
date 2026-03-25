# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Runtime state management for the Responses server."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from copy import deepcopy
from typing import Any

from .._handlers import ResponseContext
from ..models import _generated as generated_models
from ..models.runtime import ResponseExecution
from ..streaming._helpers import (
    EVENT_TYPE,
    _RESPONSE_SNAPSHOT_EVENT_TYPES,
    _extract_response_snapshot_from_events,
)
from ._event_subject import _ResponseEventSubject


class _ExecutionRecord:  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        *,
        response_id: str,
        agent_reference: dict[str, Any],
        stream: bool,
        store: bool,
        background: bool,
        replay_enabled: bool,
        visible_via_get: bool,
        status: str,
        model: str | None,
        response_payload: dict[str, Any] | None = None,
        subject: _ResponseEventSubject | None = None,
        cancel_signal: asyncio.Event | None = None,
        background_runner: Any | None = None,
        background_execution_started: bool = False,
        input_items: list[dict[str, Any]] | None = None,
        previous_response_id: str | None = None,
        response_context: ResponseContext | None = None,
    ) -> None:
        self.response_id = response_id
        self.agent_reference = agent_reference
        self.stream = stream
        self.store = store
        self.background = background
        self.replay_enabled = replay_enabled
        self.visible_via_get = visible_via_get
        self.status = status
        self.model = model
        self.response_payload = response_payload
        self.subject = subject
        self.cancel_signal = cancel_signal if cancel_signal is not None else asyncio.Event()
        self.background_runner = background_runner
        self.background_execution_started = background_execution_started
        self.input_items = input_items if input_items is not None else []
        self.previous_response_id = previous_response_id
        self.response_context = response_context

    def apply_event(self, normalized: dict[str, Any], all_events: list[dict[str, Any]]) -> None:
        """Apply a normalised stream event to this record's state.

        Updates ``response_payload`` and ``status`` according to the event type.
        Does nothing if the record is already ``"cancelled"``.

        :param normalized: The normalised event dictionary (``{"type": ..., "payload": {...}}``).
        :type normalized: dict[str, Any]
        :param all_events: The full ordered list of handler events seen so far
            (used to extract the latest response snapshot).
        :type all_events: list[dict[str, Any]]
        """
        if self.status == "cancelled":
            return
        event_type = normalized.get("type")
        payload = normalized.get("payload", {})
        if event_type in _RESPONSE_SNAPSHOT_EVENT_TYPES:
            self.response_payload = _extract_response_snapshot_from_events(
                all_events,
                response_id=self.response_id,
                agent_reference=self.agent_reference,
                model=self.model,
            )
            resolved = self.response_payload.get("status")
            if isinstance(resolved, str):
                self.status = resolved
        elif event_type == EVENT_TYPE.RESPONSE_OUTPUT_ITEM_ADDED.value:
            item = payload.get("item")
            if isinstance(item, dict) and isinstance(self.response_payload, dict):
                output = self.response_payload.setdefault("output", [])
                output.append(deepcopy(item))
        elif event_type == EVENT_TYPE.RESPONSE_OUTPUT_ITEM_DONE.value:
            item = payload.get("item")
            output_index = payload.get("output_index")
            if (
                isinstance(item, dict)
                and isinstance(output_index, int)
                and isinstance(self.response_payload, dict)
            ):
                output = self.response_payload.get("output", [])
                if 0 <= output_index < len(output):
                    output[output_index] = deepcopy(item)

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
            return result
        return {
            "id": execution.response_id,
            "response_id": execution.response_id,
            "object": "response",
            "status": execution.status,
        }
