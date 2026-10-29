# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Native A2A task persistence using the shared Foundry state-store client."""

from __future__ import annotations

from asyncio import Lock  # pylint: disable=do-not-import-asyncio  # Synchronization only, no transport sleeps.
import base64
import hashlib
import json
import logging
import os

from a2a.server.context import ServerCallContext
from a2a.server.tasks import InMemoryTaskStore, TaskStore
from a2a.types import ListTasksRequest, ListTasksResponse, Task
from azure.core.credentials_async import AsyncTokenCredential

from azure.ai.agentserver.core import get_request_context
from azure.ai.agentserver.core._experimental import experimental
from azure.ai.agentserver.core.storage import (
    DEFAULT_ITEM_TTL_SECONDS,
    FoundryStateStore,
    FoundryStorageEndpoint,
    FoundryStorageNotFoundError,
    JSONObject,
    StateStoreItem,
)

logger = logging.getLogger(__name__)


@experimental
class FoundryTaskStore(TaskStore):
    """Persist native A2A Tasks in one named Core state store.

    Task snapshots are serialized losslessly as protobuf data. Hosted caller
    isolation is enforced by Foundry storage using the brokered request context.
    Available platform user, native user, and tenant scopes are layered into keys. A hosted
    request needs brokered context or a usable caller identity, and every
    operation verifies that the backing store enables server-side isolation.

    Locally, Core's file-backed state-store implementation is used. Persisting
    task records does not restart interrupted executors or create resilient tasks.

    :param name: Stable store name, scoped to the owning agent.
    :type name: str
    :keyword credential: Async credential; defaults to Core's managed credential.
    :paramtype credential: ~azure.core.credentials_async.AsyncTokenCredential or None
    :keyword endpoint: Foundry storage or project endpoint; defaults to the environment.
    :paramtype endpoint: ~azure.ai.agentserver.core.storage.FoundryStorageEndpoint or str or None
    :keyword item_ttl_seconds: Retention inherited by newly created store items.
    :paramtype item_ttl_seconds: int
    """

    def __init__(
        self,
        name: str,
        *,
        credential: AsyncTokenCredential | None = None,
        endpoint: FoundryStorageEndpoint | str | None = None,
        item_ttl_seconds: int = DEFAULT_ITEM_TTL_SECONDS,
    ) -> None:
        if not name:
            raise ValueError("name must be a non-empty string")
        self._name = name
        self._credential = credential
        self._endpoint = endpoint
        self._item_ttl_seconds = item_ttl_seconds
        self._reader: FoundryStateStore | None = None
        self._writer: FoundryStateStore | None = None
        self._lock = Lock()
        self._closed = False

    @staticmethod
    def _owner(context: ServerCallContext) -> str:
        platform = get_request_context()
        hosted = bool(os.environ.get("FOUNDRY_HOSTING_ENVIRONMENT"))
        if hosted and not (platform.user_id or platform.call_id or context.user.is_authenticated):
            raise PermissionError("Hosted A2A task persistence requires caller identity or brokered context")
        identity = json.dumps(
            [platform.user_id, context.tenant, context.user.user_name],
            ensure_ascii=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(identity.encode("utf-8")).hexdigest()

    @staticmethod
    def _key(task_id: str, owner: str) -> str:
        if not task_id:
            raise ValueError("task_id must be a non-empty string")
        encoded = base64.urlsafe_b64encode(task_id.encode("utf-8")).decode("ascii").rstrip("=")
        return f"{owner}:{encoded}"

    async def _store(self, *, create: bool = False) -> FoundryStateStore:
        async with self._lock:
            if self._closed:
                raise RuntimeError("FoundryTaskStore is closed")
            if self._writer is not None:
                return self._writer
            if create:
                self._writer = await FoundryStateStore.get_or_create(
                    self._name,
                    credential=self._credential,
                    endpoint=self._endpoint,
                    user_isolation=True,
                    item_ttl_seconds=self._item_ttl_seconds,
                )
                return self._writer
            if self._reader is None:
                self._reader = FoundryStateStore(
                    self._name,
                    credential=self._credential,
                    endpoint=self._endpoint,
                    user_isolation=True,
                    item_ttl_seconds=self._item_ttl_seconds,
                )
            return self._reader

    @staticmethod
    async def _verify_isolation(store: FoundryStateStore, *, missing_ok: bool = False) -> bool:
        try:
            descriptor = await store.get()
        except FoundryStorageNotFoundError:
            if missing_ok:
                return False
            raise
        if getattr(descriptor, "user_isolation", None) is not True:
            raise PermissionError("A2A task persistence requires a user-isolated backing store")
        return True

    @classmethod
    def _deserialize(cls, item: StateStoreItem, owner: str) -> Task:
        return cls._decode_task(item.value.get("task"), item.key, owner)

    @classmethod
    def _decode_task(cls, encoded: object, key: str, owner: str) -> Task:
        if not isinstance(encoded, str):
            raise ValueError("Stored A2A task payload must contain serialized task data")
        task = Task()
        task.ParseFromString(base64.b64decode(encoded, validate=True))
        if key != cls._key(task.id, owner):
            raise ValueError("Stored A2A task identity does not match its storage key")
        return task

    async def save(self, task: Task, context: ServerCallContext) -> None:
        """Save a complete native Task snapshot for the current caller.

        :param task: Task to create or replace.
        :type task: ~a2a.types.Task
        :param context: Native caller context.
        :type context: ~a2a.server.context.ServerCallContext
        """
        owner = self._owner(context)
        key = self._key(task.id, owner)
        value: JSONObject = {"task": base64.b64encode(task.SerializeToString()).decode("ascii")}
        summary = Task(id=task.id, context_id=task.context_id)
        if task.HasField("status"):
            summary.status.state = task.status.state
            if task.status.HasField("timestamp"):
                summary.status.timestamp.CopyFrom(task.status.timestamp)
        store = await self._store(create=True)
        await self._verify_isolation(store)
        await store.set_item(
            key,
            value,
            tags={
                "a2a_owner": owner,
                "a2a_list": base64.b64encode(summary.SerializeToString()).decode("ascii"),
            },
        )

    async def get(self, task_id: str, context: ServerCallContext) -> Task | None:
        """Read a caller-scoped Task, or return ``None`` when absent.

        :param task_id: Native task identifier.
        :type task_id: str
        :param context: Native caller context.
        :type context: ~a2a.server.context.ServerCallContext
        :return: The stored Task, if present.
        :rtype: ~a2a.types.Task or None
        """
        owner = self._owner(context)
        store = await self._store()
        if not await self._verify_isolation(store, missing_ok=True):
            return None
        try:
            item = await store.get_item(self._key(task_id, owner))
        except FoundryStorageNotFoundError:
            return None
        return None if item is None else self._deserialize(item, owner)

    async def list(self, params: ListTasksRequest, context: ServerCallContext) -> ListTasksResponse:
        """List caller-scoped Tasks using the native SDK's filtering and paging.

        :param params: Native task-list filters and pagination.
        :type params: ~a2a.types.ListTasksRequest
        :param context: Native caller context.
        :type context: ~a2a.server.context.ServerCallContext
        :return: Native task-list response.
        :rtype: ~a2a.types.ListTasksResponse
        """
        owner = self._owner(context)
        store = await self._store()
        view = InMemoryTaskStore()
        if not await self._verify_isolation(store, missing_ok=True):
            return await view.list(params, context)
        after = None
        legacy_tasks: dict[str, Task] = {}
        while True:
            try:
                page = await store.list_keys(tags={"a2a_owner": owner}, limit=100, after=after)
            except FoundryStorageNotFoundError:
                break
            for key in page.keys:
                tags = key.tags or {}
                if "a2a_list" in tags:
                    summary = self._decode_task(tags["a2a_list"], key.key, owner)
                else:
                    # Previously saved preview records have no lightweight listing metadata.
                    item = await store.get_item(key.key)
                    if item is None:
                        continue
                    summary = self._deserialize(item, owner)
                    legacy_tasks[summary.id] = summary
                await view.save(summary, context)
            if not page.has_more:
                break
            if page.last_id is None or page.last_id == after:
                raise ValueError("Foundry state store returned an invalid pagination cursor")
            after = page.last_id
        result = await view.list(params, context)
        tasks = []
        for summary in result.tasks:
            if summary.id in legacy_tasks:
                tasks.append(legacy_tasks[summary.id])
            else:
                item = await store.get_item(self._key(summary.id, owner))
                if item is not None:
                    tasks.append(self._deserialize(item, owner))
        del result.tasks[:]
        result.tasks.extend(tasks)
        return result

    async def delete(self, task_id: str, context: ServerCallContext) -> None:
        """Delete a caller-scoped Task without affecting other callers.

        :param task_id: Native task identifier.
        :type task_id: str
        :param context: Native caller context.
        :type context: ~a2a.server.context.ServerCallContext
        """
        owner = self._owner(context)
        store = await self._store()
        if not await self._verify_isolation(store, missing_ok=True):
            logger.warning("Attempted to delete a missing A2A task")
            return
        try:
            await store.delete_item(self._key(task_id, owner))
        except FoundryStorageNotFoundError:
            logger.warning("Attempted to delete a missing A2A task")

    async def aclose(self) -> None:
        """Close owned storage clients, without closing a supplied credential."""
        async with self._lock:
            if self._closed:
                return
            self._closed = True
            try:
                if self._writer is not None:
                    await self._writer.aclose()
            finally:
                if self._reader is not None and self._reader is not self._writer:
                    await self._reader.aclose()

    async def __aenter__(self) -> FoundryTaskStore:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
