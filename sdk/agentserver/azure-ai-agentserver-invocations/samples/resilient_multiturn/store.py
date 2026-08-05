"""Foundry State Store persistence for the multi-turn sample."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from azure.ai.agentserver.core.storage import FoundryStateStore, FoundryStorageNotFoundError


class StateStore:
    """Lazy client for one explicit Foundry state store."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._store: FoundryStateStore | None = None
        self._lock = asyncio.Lock()

    def _local_path(self, key: str) -> Path | None:
        root = os.environ.get("AGENTSERVER_STATE_ROOT")
        if not root or os.environ.get("FOUNDRY_PROJECT_ENDPOINT"):
            return None
        identity = f"{self._name}\0{key}".encode()
        return Path(root) / "sample-state" / f"{hashlib.sha256(identity).hexdigest()}.json"

    async def _get_store(self) -> FoundryStateStore:
        if self._store is None:
            async with self._lock:
                if self._store is None:
                    self._store = await FoundryStateStore.get_or_create(
                        self._name,
                        user_isolation=True,
                        description="Multi-turn conversation state and invocation results",
                    )
        return self._store

    async def save(self, key: str, data: dict[str, Any], *, session_id: str) -> None:
        """Persist one JSON object."""
        local_path = self._local_path(key)
        if local_path is not None:
            await asyncio.to_thread(self._save_local, local_path, data)
            return
        store = await self._get_store()
        await store.set_item(key, data, tags={"session_id": session_id})

    async def load(self, key: str) -> dict[str, Any] | None:
        """Load one JSON object."""
        local_path = self._local_path(key)
        if local_path is not None:
            return await asyncio.to_thread(self._load_local, local_path)
        store = await self._get_store()
        item = await store.get_item(key)
        return dict(item.value) if item is not None and isinstance(item.value, dict) else None

    async def delete(self, key: str) -> None:
        """Delete one item."""
        local_path = self._local_path(key)
        if local_path is not None:
            await asyncio.to_thread(self._delete_local, local_path)
            return
        store = await self._get_store()
        try:
            await store.delete_item(key)
        except FoundryStorageNotFoundError:
            pass

    @staticmethod
    def _load_local(path: Path) -> dict[str, Any] | None:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        return dict(value) if isinstance(value, dict) else None

    @staticmethod
    def _save_local(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_name(f"{path.name}.{os.getpid()}.{uuid4().hex}.tmp")
        try:
            temporary_path.write_text(json.dumps(data), encoding="utf-8")
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)

    @staticmethod
    def _delete_local(path: Path) -> None:
        path.unlink(missing_ok=True)
