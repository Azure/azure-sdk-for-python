# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""File-backed response store provider for local-dev recovery testing.

The default :class:`InMemoryResponseProvider` lives in-process and
evaporates on process restart. That makes it useless for testing
cross-process recovery scenarios where the framework expects the response
store to persist across ``SIGKILL`` + restart. ``FileResponseStore``
serialises each response object to a JSON file under a configurable
storage directory; restarts find the files exactly as they were left.

**Scope and composition.** This class implements only
:class:`ResponseProviderProtocol` — response envelope CRUD, input items,
and history-item indexes. Streaming concerns are handled by the
process-wide ``azure.ai.agentserver.core.streaming.streams`` registry,
configured by the responses hosting layer with a file-backed or
in-memory replay backing depending on ``resilient_background``.
Cancellation / execution-record state is not part of any protocol; it
lives in the in-process ``_RuntimeState`` (for live execution) and in
the resilient task layer's ``_steering`` payload (for crash recovery) —
neither requires anything from the response store.

**Drop-in for InMemoryResponseProvider.** Within the scope of
:class:`ResponseProviderProtocol`, this class is a no-side-effects
replacement: response envelopes, input items, output items, history
chains, and conversation membership are all tracked with the same
semantics. In particular:

- ``conversation_id`` membership is tracked alongside the
  ``previous_response_id`` chain so that :meth:`get_history_item_ids`
  walks both, matching :class:`InMemoryResponseProvider`.
- :class:`PlatformContext` is accepted but ignored, identical to
  :class:`InMemoryResponseProvider`. If the in-memory provider ever
  starts partitioning by platform context, this provider should follow suit.

**Not for production use.** This is a local-dev convenience. It does not
support distributed access, has no SLA, and uses ``asyncio.Lock`` for
single-process serialisation only — concurrent writers from multiple
processes will race on the underlying filesystem.

Storage layout under ``storage_dir``::

    responses/
        {response_id}.json               # envelope; output[] entries are
                                         #   pointer stubs {"$item_ref": id}
                                         #   for id'd items (id-less items
                                         #   stay inline). get_response
                                         #   rehydrates from items/.
        {response_id}.indexes.json       # input/output/history id lists
                                         #   (the only place history_item_ids
                                         #   is read from)
        {response_id}.deleted            # soft-delete marker
    items/                               # THE single copy of each item
        {item_id}.json
    conversations/                       # response_id list per conversation
        {conversation_id}.json

Each item is persisted exactly once under ``items/``; the response
envelope and conversations hold only pointers (spec 028). ``get_items``
and ``get_input_items`` resolve item content from ``items/``;
``get_response`` rehydrates the envelope's pointer stubs from the same
store. Writers persist items **before** the pointerized envelope, so a
crash can never leave the envelope referencing a missing item file.

Atomic-write semantics mirror the pattern used by the resilient task store's
``_local_provider.py``: write to a tempfile, then ``os.replace()`` it into
place.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import json
import os
import re
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, cast

from .._response_context import PlatformContext
from ..models._generated import OutputItem, ResponseObject
from ..models._helpers import get_conversation_id
from ._base import ResponseAlreadyExistsError, ResponseProviderProtocol

# Sentinel key marking an ``output[]`` entry as a pointer to an item stored
# under ``items/{id}.json`` (spec 028). A real response output item is a typed
# model that always carries at least a ``type`` field, so a dict whose ONLY
# key is this sentinel is unambiguously a pointer stub.
_ITEM_REF_KEY = "$item_ref"

# Store paths are built from response/item/conversation IDs, some of which can
# originate from client input (e.g. a client-supplied ``conversation``). Enforce
# the Public Task API contract so a value like ``"../../etc"`` cannot escape the
# store directory (path traversal).
_VALID_STORE_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def _validate_store_id(value: str, kind: str) -> str:
    """Return *value* if it is a safe on-disk identifier, else raise.

    :param value: The identifier used to build a file path.
    :type value: str
    :param kind: A human-readable name for the identifier (for error messages).
    :type kind: str
    :returns: The validated identifier, unchanged.
    :rtype: str
    :raises ValueError: If *value* contains path separators, ``..``, or any
        character outside ``[A-Za-z0-9_-]``.
    """
    if not isinstance(value, str) or not _VALID_STORE_ID.match(value):
        raise ValueError(f"Invalid {kind}: {value!r} (must match {_VALID_STORE_ID.pattern})")
    return value


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
    tmp.write_text(json.dumps(data, indent=2, default=str))
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


def _deserialize_item(data: dict[str, Any] | None) -> OutputItem | None:
    """Deserialize a stored item dict into a typed ``OutputItem`` subtype.

    Items persist to disk as JSON dicts; consumers (and the typed
    ``OutputItem.internal_metadata`` accessor) expect proper discriminated
    subtypes. Returns ``None`` for a missing record; falls back to the raw dict
    if deserialization fails for an unrecognised shape.

    :param data: The raw stored item dict, or ``None``.
    :type data: dict[str, Any] | None
    :returns: The typed ``OutputItem`` subtype, or ``None`` if *data* is ``None``.
    :rtype: ~azure.ai.agentserver.responses.models._generated.OutputItem | None
    """
    if data is None:
        return None
    return cast(OutputItem, data)


def _response_to_dict(response: ResponseObject) -> dict[str, Any]:
    """Convert a ``ResponseObject`` to a JSON-safe dict for persistence.

    :param response: The response object to convert.
    :type response: ResponseObject
    :returns: JSON-safe representation.
    :rtype: dict[str, Any]
    """
    response_any = cast(Any, response)
    if hasattr(response_any, "as_dict") and callable(response_any.as_dict):
        return response_any.as_dict()  # type: ignore[no-any-return]
    if isinstance(response, dict):
        return dict(response)
    return json.loads(json.dumps(response, default=str))


def _dict_to_response(data: dict[str, Any]) -> ResponseObject:
    """Convert a persisted JSON dict back to a ``ResponseObject``.

    :param data: The persisted dict.
    :type data: dict[str, Any]
    :returns: A reconstructed response object.
    :rtype: ResponseObject
    """
    return cast(ResponseObject, data)


def _item_id(item: Any) -> str | None:
    """Extract the ``id`` field from an item object or mapping.

    :param item: The item to inspect.
    :type item: Any
    :returns: The item id, or ``None`` if absent.
    :rtype: str | None
    """
    extracted = getattr(item, "id", None)
    if extracted is None and isinstance(item, dict):
        extracted = item.get("id")
    return extracted


def _serialize_item(item: Any) -> dict[str, Any]:
    """Serialise an item to a JSON-safe dict.

    :param item: The item to serialise.
    :type item: Any
    :returns: JSON-safe dict.
    :rtype: dict[str, Any]
    """
    if isinstance(item, dict):
        return dict(item)
    return _response_to_dict(item)


class FileResponseStore(ResponseProviderProtocol):
    """File-backed response store provider.

    Implements :class:`ResponseProviderProtocol`. Streaming concerns are
    handled separately by the process-wide
    ``azure.ai.agentserver.core.streaming.streams`` registry, configured
    by the responses hosting layer.

    :param storage_dir: Root directory for the store. Created if it does
        not exist. Subdirectories ``responses/``, ``items/``, and
        ``conversations/`` are managed by the store. Defaults to
        ``resolve_state_subdir("responses")`` — a ``responses`` directory
        under the shared agent-server state root (``AGENTSERVER_STATE_ROOT``,
        or ``~/.agentserver`` when unset), alongside ``tasks`` and
        ``streams``.
    :type storage_dir: str | ~pathlib.Path | None
    """

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        if storage_dir is None:
            from azure.ai.agentserver.core import (  # pylint: disable=import-outside-toplevel,import-error,no-name-in-module
                resolve_state_subdir,
            )

            storage_dir = cast("str | Path", resolve_state_subdir("responses"))
        self._root = Path(storage_dir)
        self._responses_dir = self._root / "responses"
        self._items_dir_global = self._root / "items"
        self._conversations_dir = self._root / "conversations"
        for d in (
            self._responses_dir,
            self._items_dir_global,
            self._conversations_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _response_path(self, response_id: str) -> Path:
        return self._responses_dir / f"{_validate_store_id(response_id, 'response_id')}.json"

    def _per_response_items_dir(self, response_id: str) -> Path:
        return self._responses_dir / f"{_validate_store_id(response_id, 'response_id')}.items"

    def _indexes_path(self, response_id: str) -> Path:
        return self._responses_dir / f"{_validate_store_id(response_id, 'response_id')}.indexes.json"

    def _deleted_marker(self, response_id: str) -> Path:
        return self._responses_dir / f"{_validate_store_id(response_id, 'response_id')}.deleted"

    def _global_item_path(self, item_id: str) -> Path:
        return self._items_dir_global / f"{_validate_store_id(item_id, 'item_id')}.json"

    def _conversation_path(self, conversation_id: str) -> Path:
        return self._conversations_dir / f"{_validate_store_id(conversation_id, 'conversation_id')}.json"

    # ------------------------------------------------------------------
    # ResponseProviderProtocol — envelope CRUD
    # ------------------------------------------------------------------

    async def create_response(
        self,
        response: ResponseObject,
        input_items: Iterable[OutputItem] | None,
        history_item_ids: Iterable[str] | None,
        *,
        context: PlatformContext | None = None,
    ) -> None:
        """Persist a new response envelope.

        :param response: The response envelope to persist.
        :type response: ResponseObject
        :param input_items: Optional resolved input items.
        :type input_items: Iterable[OutputItem] | None
        :param history_item_ids: Optional history item ids to link.
        :type history_item_ids: Iterable[str] | None
        :keyword context: Platform context (accepted but unused —
            matches :class:`InMemoryResponseProvider`).
        :paramtype context: PlatformContext | None
        :rtype: None
        :raises ResponseAlreadyExistsError: If a non-deleted response with
            the same id already exists.
        """
        del context
        response_id = str(response.get("id"))
        async with self._lock:
            target = self._response_path(response_id)
            deleted_marker = self._deleted_marker(response_id)
            if target.exists() and not deleted_marker.exists():
                raise ResponseAlreadyExistsError(response_id)
            if deleted_marker.exists():
                deleted_marker.unlink()

            # (Spec 028) Best-effort removal of any legacy per-response items
            # directory from a pre-normalization layout — it is dead weight.
            legacy_items = self._per_response_items_dir(response_id)
            if legacy_items.exists():
                shutil.rmtree(legacy_items, ignore_errors=True)

            # Items first, pointerized envelope last: a crash can never leave
            # the envelope referencing an item file that does not exist.
            input_ids = self._store_items_unlocked(input_items or [])
            output_ids = self._store_output_items_unlocked(response)
            history_ids = list(history_item_ids) if history_item_ids is not None else []

            _atomic_write_json(target, self._pointerize_output(_response_to_dict(response)))
            _atomic_write_json(
                self._indexes_path(response_id),
                {
                    "input_item_ids": input_ids,
                    "output_item_ids": output_ids,
                    "history_item_ids": history_ids,
                },
            )
            # (Spec 028) Best-effort removal of a legacy per-response
            # history file from a pre-normalization layout — history_item_ids
            # live in indexes.json (the only place any reader consults).
            legacy_history = self._responses_dir / f"{response_id}.history.json"
            if legacy_history.exists():
                legacy_history.unlink()

            conversation_id = get_conversation_id(response)
            if conversation_id is not None:
                self._add_response_to_conversation_unlocked(conversation_id, response_id)

    async def get_response(self, response_id: str, *, context: PlatformContext | None = None) -> ResponseObject:
        """Retrieve one response envelope by identifier.

        :param response_id: The response identifier.
        :type response_id: str
        :keyword context: Platform context (accepted but unused —
            matches :class:`InMemoryResponseProvider`).
        :paramtype context: PlatformContext | None
        :returns: The persisted response envelope (deep-copied).
        :rtype: ResponseObject
        :raises KeyError: If the response does not exist or has been deleted.
        """
        del context
        async with self._lock:
            if self._deleted_marker(response_id).exists():
                raise KeyError(f"response '{response_id}' not found")
            data = _read_json_or_none(self._response_path(response_id))
            if data is None:
                raise KeyError(f"response '{response_id}' not found")
            return _dict_to_response(deepcopy(self._rehydrate_output(data)))

    async def update_response(self, response: ResponseObject, *, context: PlatformContext | None = None) -> None:
        """Update a stored response envelope.

        Output items present on the updated response are persisted to the
        per-response items directory and the global items index so that
        :meth:`get_items` can resolve them on subsequent history lookups —
        matches :class:`InMemoryResponseProvider`.

        :param response: The new response envelope.
        :type response: ResponseObject
        :keyword context: Platform context (accepted but unused —
            matches :class:`InMemoryResponseProvider`).
        :paramtype context: PlatformContext | None
        :rtype: None
        :raises KeyError: If the response does not exist or has been deleted.
        """
        del context
        response_id = str(response.get("id"))
        async with self._lock:
            if self._deleted_marker(response_id).exists():
                raise KeyError(f"response '{response_id}' not found")
            target = self._response_path(response_id)
            if not target.exists():
                raise KeyError(f"response '{response_id}' not found")
            response_dict = _response_to_dict(response)
            # Items first, pointerized envelope last (spec 028 — same
            # crash-ordering invariant as create_response).
            output_ids = self._store_output_items_unlocked(response)
            _atomic_write_json(target, self._pointerize_output(response_dict))
            self._update_indexes_unlocked(response_id, output_item_ids=output_ids)

    async def delete_response(self, response_id: str, *, context: PlatformContext | None = None) -> None:
        """Soft-delete a stored response envelope by identifier.

        Writes a deleted marker file so that subsequent
        :meth:`create_response` calls with the same id can re-create the
        entry while concurrent reads see a ``KeyError``. Mirrors
        :class:`InMemoryResponseProvider`.

        :param response_id: The response identifier.
        :type response_id: str
        :keyword context: Platform context (accepted but unused —
            matches :class:`InMemoryResponseProvider`).
        :paramtype context: PlatformContext | None
        :rtype: None
        :raises KeyError: If the response does not exist or has already been deleted.
        """
        del context
        async with self._lock:
            if self._deleted_marker(response_id).exists():
                raise KeyError(f"response '{response_id}' not found")
            target = self._response_path(response_id)
            if not target.exists():
                raise KeyError(f"response '{response_id}' not found")
            self._deleted_marker(response_id).write_text("deleted")

    # ------------------------------------------------------------------
    # ResponseProviderProtocol — items + history
    # ------------------------------------------------------------------

    async def get_input_items(
        self,
        response_id: str,
        limit: int = 20,
        ascending: bool = False,
        after: str | None = None,
        before: str | None = None,
        *,
        context: PlatformContext | None = None,
    ) -> list[OutputItem]:
        """Retrieve input + history items for a response with cursor paging.

        Returns the same ordered union of ``history_item_ids`` followed by
        ``input_item_ids`` that :class:`InMemoryResponseProvider` returns,
        with the same ``limit`` clamp (1–100) and the same cursor
        semantics.

        :param response_id: The response identifier.
        :type response_id: str
        :param limit: Maximum number of items to return (clamped to 1–100).
        :type limit: int
        :param ascending: Return items in ascending order.
        :type ascending: bool
        :param after: Cursor — return items after this id.
        :type after: str | None
        :param before: Cursor — return items before this id.
        :type before: str | None
        :keyword context: Platform context (accepted but unused —
            matches :class:`InMemoryResponseProvider`).
        :paramtype context: PlatformContext | None
        :returns: Paginated list of items.
        :rtype: list[OutputItem]
        :raises KeyError: If the response does not exist.
        :raises ValueError: If the response has been deleted.
        """
        del context
        async with self._lock:
            target = self._response_path(response_id)
            if not target.exists():
                raise KeyError(f"response '{response_id}' not found")
            if self._deleted_marker(response_id).exists():
                raise ValueError(f"response '{response_id}' has been deleted")

            indexes = _read_json_or_none(self._indexes_path(response_id)) or {}
            item_ids = [
                *(indexes.get("history_item_ids") or []),
                *(indexes.get("input_item_ids") or []),
            ]
            ordered = item_ids if ascending else list(reversed(item_ids))
            if after is not None:
                try:
                    ordered = ordered[ordered.index(after) + 1 :]
                except ValueError:
                    pass
            if before is not None:
                try:
                    ordered = ordered[: ordered.index(before)]
                except ValueError:
                    pass
            safe_limit = max(1, min(100, int(limit)))
            results: list[OutputItem] = []
            for iid in ordered[:safe_limit]:
                data = _read_json_or_none(self._global_item_path(iid))
                item = _deserialize_item(data)
                if item is not None:
                    results.append(item)
            return results

    async def get_items(
        self,
        item_ids: Iterable[str],
        *,
        context: PlatformContext | None = None,
    ) -> list[OutputItem | None]:
        """Retrieve items by id, preserving request order.

        Missing ids produce ``None`` entries — matches
        :class:`InMemoryResponseProvider`.

        :param item_ids: The item ids to look up.
        :type item_ids: Iterable[str]
        :keyword context: Platform context (accepted but unused —
            matches :class:`InMemoryResponseProvider`).
        :paramtype context: PlatformContext | None
        :returns: Items in the same order as ``item_ids``, ``None`` for misses.
        :rtype: list[OutputItem | None]
        """
        del context
        async with self._lock:
            results: list[OutputItem | None] = []
            for iid in item_ids:
                data = _read_json_or_none(self._global_item_path(iid))
                results.append(_deserialize_item(data))
            return results

    async def get_history_item_ids(
        self,
        previous_response_id: str | None,
        conversation_id: str | None,
        limit: int,
        *,
        context: PlatformContext | None = None,
    ) -> list[str]:
        """Resolve history item ids from previous response and/or conversation.

        Mirrors :meth:`InMemoryResponseProvider.get_history_item_ids`:

        - When ``previous_response_id`` is set, contributes that response's
          ``history_item_ids + input_item_ids + output_item_ids``.
        - When ``conversation_id`` is set, iterates all non-deleted
          responses in that conversation and contributes their
          ``history_item_ids + input_item_ids + output_item_ids``.
        - Both may be set; results are concatenated in the same order.

        Deleted responses are skipped (matches the in-memory provider).

        :param previous_response_id: Optional response id to chain history from.
        :type previous_response_id: str | None
        :param conversation_id: Optional conversation id to scope history lookup.
        :type conversation_id: str | None
        :param limit: Maximum number of history item ids to return.
        :type limit: int
        :keyword context: Platform context (accepted but unused —
            matches :class:`InMemoryResponseProvider`).
        :paramtype context: PlatformContext | None
        :returns: List of history item ids (possibly empty).
        :rtype: list[str]
        """
        del context
        async with self._lock:
            resolved: list[str] = []

            if previous_response_id is not None and not self._deleted_marker(previous_response_id).exists():
                indexes = _read_json_or_none(self._indexes_path(previous_response_id))
                if indexes is not None:
                    resolved.extend(indexes.get("history_item_ids") or [])
                    resolved.extend(indexes.get("input_item_ids") or [])
                    resolved.extend(indexes.get("output_item_ids") or [])

            if conversation_id is not None:
                conv_data = _read_json_or_none(self._conversation_path(conversation_id))
                for rid in (conv_data or {}).get("response_ids", []):
                    if self._deleted_marker(rid).exists():
                        continue
                    indexes = _read_json_or_none(self._indexes_path(rid))
                    if indexes is None:
                        continue
                    resolved.extend(indexes.get("history_item_ids") or [])
                    resolved.extend(indexes.get("input_item_ids") or [])
                    resolved.extend(indexes.get("output_item_ids") or [])

            if limit <= 0:
                return []
            return resolved[:limit]

    # ------------------------------------------------------------------
    # Internal helpers (must be called with self._lock held)
    # ------------------------------------------------------------------

    def _store_items_unlocked(self, items: Iterable[Any]) -> list[str]:
        """Persist items to the single global ``items/`` store.

        :param items: Iterable of items (each must expose an ``id``).
        :type items: Iterable[Any]
        :returns: Ordered list of stored item ids.
        :rtype: list[str]
        """
        stored_ids: list[str] = []
        for item in items:
            iid = _item_id(item)
            if not iid:
                continue
            _atomic_write_json(self._global_item_path(iid), _serialize_item(item))
            stored_ids.append(iid)
        return stored_ids

    def _store_output_items_unlocked(self, response: ResponseObject) -> list[str]:
        """Extract output items from a response and persist them.

        Mirrors :meth:`InMemoryResponseProvider._store_output_items_unlocked`.

        :param response: The response envelope.
        :type response: ResponseObject
        :returns: Ordered list of stored output item ids.
        :rtype: list[str]
        """
        output = response.get("output")
        if not output:
            return []
        return self._store_items_unlocked(output)

    @staticmethod
    def _pointerize_output(envelope: dict[str, Any]) -> dict[str, Any]:
        """Replace each id'd ``output[]`` item with a pointer stub.

        Id'd items live (once) under ``items/``; the envelope keeps only a
        ``{"$item_ref": id}`` stub in their place. Items without an ``id``
        (which are not stored under ``items/``) are kept inline so they
        survive the round-trip. Order and position are preserved.

        :param envelope: The JSON-safe response envelope dict.
        :type envelope: dict[str, Any]
        :returns: A shallow copy of *envelope* with a pointerized ``output``.
        :rtype: dict[str, Any]
        """
        output = envelope.get("output")
        if not output or not isinstance(output, list):
            return envelope
        new_output: list[Any] = []
        for entry in output:
            iid = entry.get("id") if isinstance(entry, dict) else None
            new_output.append({_ITEM_REF_KEY: iid} if iid else entry)
        envelope = dict(envelope)
        envelope["output"] = new_output
        return envelope

    def _rehydrate_output(self, envelope: dict[str, Any]) -> dict[str, Any]:
        """Substitute ``output[]`` pointer stubs with item content from ``items/``.

        Inverse of :meth:`_pointerize_output`. Non-stub entries (id-less
        items, or legacy fully-inline items) are kept as-is, preserving
        order and position.

        :param envelope: The persisted response envelope dict.
        :type envelope: dict[str, Any]
        :returns: A shallow copy of *envelope* with ``output`` rehydrated.
        :rtype: dict[str, Any]
        :raises RuntimeError: If a pointer references an item file that is
            missing. This is **not** a ``KeyError`` / not-found: the response
            envelope exists (was resiliently created), so the resilient recovery
            prefetch must treat this as transient corruption, not as the
            spec-026 "never persisted" drop signal.
        """
        output = envelope.get("output")
        if not output or not isinstance(output, list):
            return envelope
        new_output: list[Any] = []
        for entry in output:
            if (
                isinstance(entry, dict)
                and set(entry.keys()) == {_ITEM_REF_KEY}
                and isinstance(entry[_ITEM_REF_KEY], str)
            ):
                iid = entry[_ITEM_REF_KEY]
                item = _read_json_or_none(self._global_item_path(iid))
                if item is None:
                    raise RuntimeError(
                        f"FileResponseStore: response envelope references item "
                        f"'{iid}' but items/{iid}.json is missing (store corruption)"
                    )
                new_output.append(item)
            else:
                new_output.append(entry)
        envelope = dict(envelope)
        envelope["output"] = new_output
        return envelope

    def _update_indexes_unlocked(
        self,
        response_id: str,
        *,
        input_item_ids: list[str] | None = None,
        output_item_ids: list[str] | None = None,
        history_item_ids: list[str] | None = None,
    ) -> None:
        """Merge the supplied id lists into the persisted indexes file.

        :param response_id: The response identifier.
        :type response_id: str
        :keyword input_item_ids: New input ids to overwrite.
        :keyword output_item_ids: New output ids to overwrite.
        :keyword history_item_ids: New history ids to overwrite.
        :rtype: None
        """
        path = self._indexes_path(response_id)
        current = _read_json_or_none(path) or {}
        if input_item_ids is not None:
            current["input_item_ids"] = input_item_ids
        if output_item_ids is not None:
            current["output_item_ids"] = output_item_ids
        if history_item_ids is not None:
            current["history_item_ids"] = history_item_ids
        _atomic_write_json(path, current)

    def _add_response_to_conversation_unlocked(self, conversation_id: str, response_id: str) -> None:
        """Append ``response_id`` to the conversation's response list.

        Idempotent: appending the same id twice is a no-op.

        :param conversation_id: The conversation identifier.
        :type conversation_id: str
        :param response_id: The response identifier to register.
        :type response_id: str
        :rtype: None
        """
        path = self._conversation_path(conversation_id)
        data = _read_json_or_none(path) or {"response_ids": []}
        ids = list(data.get("response_ids") or [])
        if response_id not in ids:
            ids.append(response_id)
        data["response_ids"] = ids
        _atomic_write_json(path, data)
