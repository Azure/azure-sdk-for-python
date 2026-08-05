"""Foundry State Store persistence for research checkpoints."""

from __future__ import annotations

import asyncio
from typing import Any

from azure.ai.agentserver.core.storage import FoundryStateStore


class CheckpointStore:
    """Lazy client for the sample's explicit Foundry state store."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._store: FoundryStateStore | None = None
        self._lock = asyncio.Lock()

    async def _get_store(self) -> FoundryStateStore:
        if self._store is None:
            async with self._lock:
                if self._store is None:
                    self._store = await FoundryStateStore.get_or_create(
                        self._name,
                        user_isolation=True,
                        description="Deep-research recovery checkpoints",
                    )
        return self._store

    async def get(self, key: str) -> dict[str, Any]:
        """Load one checkpoint, returning an empty object when absent."""
        store = await self._get_store()
        item = await store.get_item(key)
        return dict(item.value) if item is not None and isinstance(item.value, dict) else {}

    async def put(self, key: str, value: dict[str, Any], *, session_id: str) -> None:
        """Persist one checkpoint."""
        store = await self._get_store()
        await store.set_item(key, value, tags={"session_id": session_id})
