"""Explicit Foundry State Store helper for resilient response samples."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from azure.ai.agentserver.core.storage import FoundryStateStore


class ConversationStateStore:
    """Persist one JSON state item per response conversation."""

    def __init__(self, sample_name: str) -> None:
        self._sample_name = sample_name

    def _local_path(self, conversation_chain_id: str) -> Path | None:
        root = os.environ.get("AGENTSERVER_STATE_ROOT")
        if not root or os.environ.get("FOUNDRY_PROJECT_ENDPOINT"):
            return None
        identity = f"{self._sample_name}\0{conversation_chain_id}".encode()
        return Path(root) / "sample-state" / f"{hashlib.sha256(identity).hexdigest()}.json"

    @asynccontextmanager
    async def _open_store(self, conversation_chain_id: str) -> AsyncIterator[FoundryStateStore]:
        store = await FoundryStateStore.get_or_create(
            f"responses/{self._sample_name}/{conversation_chain_id}",
            user_isolation=True,
            description=f"State for the {self._sample_name} response sample",
        )
        try:
            yield store
        finally:
            await store.aclose()

    async def load(self, conversation_chain_id: str) -> dict[str, Any]:
        """Load the conversation state, returning an empty object when absent."""
        local_path = self._local_path(conversation_chain_id)
        if local_path is not None:
            return await asyncio.to_thread(self._load_local, local_path)
        async with self._open_store(conversation_chain_id) as store:
            item = await store.get_item("state")
        return dict(item.value) if item is not None and isinstance(item.value, dict) else {}

    async def save(self, conversation_chain_id: str, value: dict[str, Any]) -> None:
        """Create or replace the conversation state."""
        local_path = self._local_path(conversation_chain_id)
        if local_path is not None:
            await asyncio.to_thread(self._save_local, local_path, value)
            return
        async with self._open_store(conversation_chain_id) as store:
            await store.set_item("state", value)

    async def clear(self, conversation_chain_id: str) -> None:
        """Delete the conversation state."""
        local_path = self._local_path(conversation_chain_id)
        if local_path is not None:
            await asyncio.to_thread(self._clear_local, local_path)
            return
        async with self._open_store(conversation_chain_id) as store:
            await store.delete_item("state")

    @staticmethod
    def _load_local(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        return dict(value) if isinstance(value, dict) else {}

    @staticmethod
    def _save_local(path: Path, value: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_name(f"{path.name}.{os.getpid()}.{uuid4().hex}.tmp")
        try:
            temporary_path.write_text(json.dumps(value), encoding="utf-8")
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)

    @staticmethod
    def _clear_local(path: Path) -> None:
        path.unlink(missing_ok=True)
