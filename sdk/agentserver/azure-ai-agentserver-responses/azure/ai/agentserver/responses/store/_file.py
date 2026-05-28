# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""File-backed response store provider for local-dev recovery testing.

The default ``MemoryResponseProvider`` lives in-process and evaporates on
process restart. That makes it useless for testing cross-process recovery
scenarios where the framework expects the response store to persist across
``SIGKILL`` + restart. ``FileResponseStore`` serialises each response object
to a JSON file under a configurable storage directory; restarts find the
files exactly as they were left.

**Not for production use.** This is a local-dev convenience. It does not
support distributed access, has no SLA, and uses ``asyncio.Lock`` for
single-process serialisation only — concurrent writers from multiple
processes will race on the underlying filesystem.

Atomic-write semantics mirror the pattern used by the durable task store's
``_local_provider.py``: write to a tempfile, then ``os.replace()`` it into
place.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterable

import anyio

from .._response_context import IsolationContext
from ..models._generated import OutputItem, ResponseObject, ResponseStreamEvent
from ._base import ResponseAlreadyExistsError, ResponseProviderProtocol


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    """Write ``data`` as JSON to ``path`` atomically.

    Uses a sibling tempfile and ``os.replace()`` — readers either see the
    old file or the new file, never a partial write.

    :param path: Destination path.
    :type path: ~pathlib.Path
    :param data: JSON-serialisable dict.
    :type data: dict[str, Any]
    :rtype: None
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    os.replace(tmp, path)


def _read_json_or_none(path: Path) -> dict[str, Any] | None:
    """Read JSON from ``path``, returning ``None`` if the file does not exist.

    :param path: Source path.
    :type path: ~pathlib.Path
    :returns: Parsed JSON dict, or ``None`` if missing.
    :rtype: dict[str, Any] | None
    """
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return None


def _response_to_dict(response: ResponseObject) -> dict[str, Any]:
    """Convert a ``ResponseObject`` to a JSON-safe dict for persistence."""
    if hasattr(response, "as_dict") and callable(response.as_dict):
        return response.as_dict()  # type: ignore[no-any-return]
    if isinstance(response, dict):
        return dict(response)
    return json.loads(json.dumps(response, default=str))


def _dict_to_response(data: dict[str, Any]) -> ResponseObject:
    """Convert a persisted JSON dict back to a ``ResponseObject``."""
    return ResponseObject(data)


class FileResponseStore(ResponseProviderProtocol):
    """File-backed response store provider.

    Persists each response under ``{storage_dir}/responses/{response_id}.json``
    with atomic writes. Input items and history-item indexes live alongside.

    :param storage_dir: Root directory for the store. Created if it does not
        exist. Subdirectories ``responses/`` are managed by the store.
    :type storage_dir: str | ~pathlib.Path
    """

    def __init__(self, storage_dir: str | Path) -> None:
        self._root = Path(storage_dir)
        self._responses_dir = self._root / "responses"
        self._responses_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        self._stream_events: Dict[str, list[ResponseStreamEvent]] = {}

    def _response_path(self, response_id: str) -> Path:
        return self._responses_dir / f"{response_id}.json"

    def _items_dir(self, response_id: str) -> Path:
        return self._responses_dir / f"{response_id}.items"

    def _history_path(self, response_id: str) -> Path:
        return self._responses_dir / f"{response_id}.history.json"

    def _deleted_marker(self, response_id: str) -> Path:
        return self._responses_dir / f"{response_id}.deleted"

    async def create_response(
        self,
        response: ResponseObject,
        input_items: Iterable[OutputItem] | None,
        history_item_ids: Iterable[str] | None,
        *,
        isolation: IsolationContext | None = None,
    ) -> None:
        """Persist a new response envelope.

        :param response: The response envelope to persist.
        :type response: ~azure.ai.agentserver.responses.models._generated.ResponseObject
        :param input_items: Optional resolved output items.
        :type input_items: Iterable[OutputItem] | None
        :param history_item_ids: Optional history item IDs to associate.
        :type history_item_ids: Iterable[str] | None
        :keyword isolation: Isolation context (unused — single-tenant local dev).
        :paramtype isolation: ~azure.ai.agentserver.responses.IsolationContext | None
        :rtype: None
        :raises ResponseAlreadyExistsError: If a non-deleted response with the same ID already exists.
        """
        response_id = str(getattr(response, "id"))
        async with self._lock:
            target = self._response_path(response_id)
            deleted_marker = self._deleted_marker(response_id)
            if target.exists() and not deleted_marker.exists():
                raise ResponseAlreadyExistsError(response_id)
            # If a deleted marker exists, allow re-create (matches in-memory semantics).
            if deleted_marker.exists():
                deleted_marker.unlink()
            _atomic_write_json(target, _response_to_dict(response))
            if input_items is not None:
                items_dir = self._items_dir(response_id)
                items_dir.mkdir(parents=True, exist_ok=True)
                for item in input_items:
                    item_id = getattr(item, "id", None) or (
                        item.get("id") if isinstance(item, dict) else None
                    )
                    if item_id is None:
                        continue
                    item_data = (
                        item if isinstance(item, dict)
                        else _response_to_dict(item)  # type: ignore[arg-type]
                    )
                    _atomic_write_json(items_dir / f"{item_id}.json", item_data)
            if history_item_ids is not None:
                _atomic_write_json(
                    self._history_path(response_id),
                    {"history_item_ids": list(history_item_ids)},
                )

    async def get_response(
        self, response_id: str, *, isolation: IsolationContext | None = None
    ) -> ResponseObject:
        """Retrieve one response envelope by identifier.

        :raises KeyError: If the response does not exist or has been deleted.
        """
        async with self._lock:
            if self._deleted_marker(response_id).exists():
                raise KeyError(f"response '{response_id}' not found")
            data = _read_json_or_none(self._response_path(response_id))
            if data is None:
                raise KeyError(f"response '{response_id}' not found")
            return _dict_to_response(deepcopy(data))

    async def update_response(
        self, response: ResponseObject, *, isolation: IsolationContext | None = None
    ) -> None:
        """Update a stored response envelope.

        :raises KeyError: If the response does not exist or has been deleted.
        """
        response_id = str(getattr(response, "id"))
        async with self._lock:
            if self._deleted_marker(response_id).exists():
                raise KeyError(f"response '{response_id}' not found")
            target = self._response_path(response_id)
            if not target.exists():
                raise KeyError(f"response '{response_id}' not found")
            _atomic_write_json(target, _response_to_dict(response))

    async def delete_response(
        self, response_id: str, *, isolation: IsolationContext | None = None
    ) -> None:
        """Delete a stored response envelope by identifier.

        :raises KeyError: If the response does not exist or has been deleted.
        """
        async with self._lock:
            if self._deleted_marker(response_id).exists():
                raise KeyError(f"response '{response_id}' not found")
            target = self._response_path(response_id)
            if not target.exists():
                raise KeyError(f"response '{response_id}' not found")
            self._deleted_marker(response_id).write_text("deleted")

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
        """Retrieve input items for a response.

        Minimal implementation for local-dev — no cursor pagination beyond a
        simple slice.
        """
        async with self._lock:
            items_dir = self._items_dir(response_id)
            if not items_dir.exists():
                return []
            items: list[OutputItem] = []
            for child in sorted(items_dir.iterdir()):
                data = _read_json_or_none(child)
                if data is not None:
                    items.append(data)  # type: ignore[arg-type]
            if not ascending:
                items.reverse()
            return items[: max(0, min(limit, 100))]

    async def get_history_item_ids(
        self,
        previous_response_id: str | None,
        cursor: str | None,
        limit: int,
        *,
        isolation: IsolationContext | None = None,
    ) -> list[str]:
        """Fetch history item ids for a prior turn's response.

        Returns the persisted ``history_item_ids`` list if any, else empty.
        """
        if previous_response_id is None:
            return []
        async with self._lock:
            data = _read_json_or_none(self._history_path(previous_response_id))
            if data is None:
                return []
            return list(data.get("history_item_ids", []))[: max(0, limit)]
