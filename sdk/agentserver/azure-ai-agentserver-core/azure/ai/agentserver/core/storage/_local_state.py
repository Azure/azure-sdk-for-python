# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Local filesystem backend for ``FoundryStateStore``."""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ._errors import (
    FoundryStorageConflictError,
    FoundryStorageNotFoundError,
    FoundryStoragePreconditionError,
)
from ._state_serializer import (
    DeletedStateStore,
    DeletedStateStoreItem,
    JSONObject,
    Order,
    StateStore,
    StateStoreItem,
    StateStoreItemKey,
    StateStoreItemKeyPage,
    StateStoreItemRef,
)

_LOCKS: dict[Path, threading.RLock] = {}
_LOCKS_GUARD = threading.Lock()


def _now() -> int:
    return int(time.time())


def _resource_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}_{digest}"


def _new_etag() -> str:
    return f'"local-{uuid.uuid4().hex}"'


def _lock_for(path: Path) -> threading.RLock:
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(path, threading.RLock())


class LocalStateStoreBackend:
    """Persist one state store as an atomic JSON document."""

    def __init__(
        self,
        path: Path,
        *,
        name: str,
        user_isolation: bool,
        item_ttl_seconds: int,
        description: str | None,
        tags: Mapping[str, str],
    ) -> None:
        self._path = path
        self._name = name
        self._user_isolation = user_isolation
        self._item_ttl_seconds = item_ttl_seconds
        self._description = description
        self._tags = dict(tags)
        self._lock = _lock_for(path)

    def ensure_store(self) -> StateStore:
        with self._lock:
            document = self._read()
            if document is None:
                now = _now()
                document = {
                    "store": {
                        "id": _resource_id("ss", self._name),
                        "object": "state_store",
                        "name": self._name,
                        "user_isolation": self._user_isolation,
                        "item_ttl_seconds": self._item_ttl_seconds,
                        "description": self._description,
                        "tags": dict(self._tags),
                        "created_at": now,
                        "updated_at": now,
                    },
                    "items": {},
                }
                self._write(document)
            else:
                self._sync_store_config(document["store"])
            return StateStore(document["store"])

    def get_store(self) -> StateStore:
        with self._lock:
            document = self._require_document()
            return StateStore(document["store"])

    def update_store(
        self,
        *,
        description: str | None | object,
        tags: Mapping[str, str] | None | object,
        unset: object,
    ) -> StateStore:
        with self._lock:
            document = self._require_document()
            store = document["store"]
            if description is not unset:
                store["description"] = description
            if tags is not unset:
                store["tags"] = dict(tags) if isinstance(tags, Mapping) else {}
            store["updated_at"] = _now()
            self._write(document)
            return StateStore(store)

    def delete_store(self) -> DeletedStateStore:
        with self._lock:
            document = self._read()
            store_id = document["store"]["id"] if document is not None else None
            if self._path.exists():
                self._path.unlink()
            return DeletedStateStore(
                {
                    "id": store_id,
                    "object": "state_store",
                    "name": self._name,
                    "deleted": True,
                }
            )

    def create_item(
        self,
        key: str,
        value: JSONObject,
        tags: Mapping[str, str] | None,
    ) -> StateStoreItemRef:
        with self._lock:
            document = self._require_document()
            self._remove_expired(document)
            items = document["items"]
            if key in items:
                raise FoundryStorageConflictError(
                    f"State store item {key!r} already exists.",
                    status_code=409,
                )
            item = self._new_item(key, value, tags)
            items[key] = item
            self._write(document)
            return self._item_ref(item)

    def set_item(
        self,
        key: str,
        value: JSONObject,
        tags: Mapping[str, str] | None,
        if_match: str | None,
    ) -> StateStoreItemRef:
        with self._lock:
            document = self._require_document()
            self._remove_expired(document)
            current = document["items"].get(key)
            self._check_precondition(key, current, if_match)
            now = _now()
            item = {
                "id": (
                    current["id"]
                    if current is not None
                    else _resource_id("it", f"{self._name}/{key}")
                ),
                "object": "state_store.item",
                "key": key,
                "value": dict(value),
                "tags": dict(tags) if tags else None,
                "etag": _new_etag(),
                "created_at": current["created_at"] if current is not None else now,
                "updated_at": now,
                "expires_at": self._expires_at(now),
            }
            document["items"][key] = item
            self._write(document)
            return self._item_ref(item)

    def get_item(self, key: str) -> StateStoreItem | None:
        with self._lock:
            document = self._require_document()
            changed = self._remove_expired(document)
            item = document["items"].get(key)
            if changed:
                self._write(document)
            return StateStoreItem(self._public_item(item)) if item is not None else None

    def delete_item(self, key: str, if_match: str | None) -> DeletedStateStoreItem:
        with self._lock:
            document = self._require_document()
            self._remove_expired(document)
            current = document["items"].get(key)
            self._check_precondition(key, current, if_match)
            deleted_id = current["id"] if current is not None else None
            if current is not None:
                del document["items"][key]
                self._write(document)
            return DeletedStateStoreItem(
                {
                    "id": deleted_id,
                    "object": "state_store.item",
                    "key": key,
                    "deleted": True,
                }
            )

    def list_keys(
        self,
        *,
        tags: Mapping[str, str] | None,
        limit: int | None,
        after: str | None,
        before: str | None,
        order: Order,
    ) -> StateStoreItemKeyPage:
        with self._lock:
            document = self._require_document()
            changed = self._remove_expired(document)
            items = [
                item
                for item in document["items"].values()
                if not tags
                or all(
                    (item.get("tags") or {}).get(key) == value
                    for key, value in tags.items()
                )
            ]
            items.sort(
                key=lambda item: (item["created_at"], item["id"]),
                reverse=order == "desc",
            )
            if after is not None:
                items = self._after_cursor(items, after)
            elif before is not None:
                items = self._before_cursor(items, before)
            page_size = 20 if limit is None else limit
            page_items = items[:page_size]
            if changed:
                self._write(document)
            keys = [
                StateStoreItemKey(self._public_item_ref(item, include_tags=True))
                for item in page_items
            ]
            return StateStoreItemKeyPage(
                keys=keys,
                first_id=keys[0].id if keys else None,
                last_id=keys[-1].id if keys else None,
                has_more=len(items) > len(page_items),
            )

    def _require_document(self) -> dict[str, Any]:
        document = self._read()
        if document is None:
            raise FoundryStorageNotFoundError(
                f"State store {self._name!r} does not exist.",
                status_code=404,
            )
        self._sync_store_config(document["store"])
        return document

    def _sync_store_config(self, store: Mapping[str, Any]) -> None:
        self._user_isolation = bool(store["user_isolation"])
        self._item_ttl_seconds = int(store["item_ttl_seconds"])
        self._description = store.get("description")
        self._tags = dict(store.get("tags") or {})

    def _read(self) -> dict[str, Any] | None:
        if not self._path.exists():
            return None
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _write(self, document: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_name(f".{self._path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(
                json.dumps(document, indent=2, sort_keys=True), encoding="utf-8"
            )
            os.replace(temporary, self._path)
        finally:
            if temporary.exists():
                temporary.unlink()

    def _new_item(
        self,
        key: str,
        value: JSONObject,
        tags: Mapping[str, str] | None,
    ) -> dict[str, Any]:
        now = _now()
        return {
            "id": _resource_id("it", f"{self._name}/{key}"),
            "object": "state_store.item",
            "key": key,
            "value": dict(value),
            "tags": dict(tags) if tags else None,
            "etag": _new_etag(),
            "created_at": now,
            "updated_at": now,
            "expires_at": self._expires_at(now),
        }

    def _expires_at(self, now: int) -> int | None:
        return None if self._item_ttl_seconds == -1 else now + self._item_ttl_seconds

    @staticmethod
    def _public_item(item: Mapping[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in item.items() if key != "expires_at"}

    @classmethod
    def _public_item_ref(
        cls, item: Mapping[str, Any], *, include_tags: bool = False
    ) -> dict[str, Any]:
        result = {
            key: value
            for key, value in cls._public_item(item).items()
            if key in {"id", "object", "key", "etag", "created_at", "updated_at"}
        }
        if include_tags:
            result["tags"] = item.get("tags")
        return result

    @classmethod
    def _item_ref(cls, item: Mapping[str, Any]) -> StateStoreItemRef:
        return StateStoreItemRef(cls._public_item_ref(item))

    @staticmethod
    def _check_precondition(
        key: str, current: Mapping[str, Any] | None, if_match: str | None
    ) -> None:
        if if_match is None:
            return
        current_etag = current.get("etag") if current is not None else None
        if current is None or if_match not in ("*", current_etag):
            raise FoundryStoragePreconditionError(
                f"ETag precondition failed for state store item {key!r}.",
                status_code=412,
                current_etag=current_etag if isinstance(current_etag, str) else None,
            )

    @staticmethod
    def _after_cursor(items: list[dict[str, Any]], cursor: str) -> list[dict[str, Any]]:
        for index, item in enumerate(items):
            if item["id"] == cursor:
                return items[index + 1 :]
        return []

    @staticmethod
    def _before_cursor(
        items: list[dict[str, Any]], cursor: str
    ) -> list[dict[str, Any]]:
        for index, item in enumerate(items):
            if item["id"] == cursor:
                return items[:index]
        return []

    @staticmethod
    def _remove_expired(document: dict[str, Any]) -> bool:
        now = _now()
        expired = [
            key
            for key, item in document["items"].items()
            if item.get("expires_at") is not None and item["expires_at"] <= now
        ]
        for key in expired:
            del document["items"][key]
        return bool(expired)
