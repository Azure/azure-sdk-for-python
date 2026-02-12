# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Foundry-backed checkpoint saver for LangGraph."""

import logging
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Sequence, Tuple, Union

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    SerializerProtocol,
    get_checkpoint_id,
)

from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.ai.agentserver.core.checkpoints.client import (
    CheckpointItem,
    CheckpointItemId,
    CheckpointSession,
    FoundryCheckpointClient,
)

from ._item_id import ParsedItemId, make_item_id, parse_item_id

logger = logging.getLogger(__name__)


class FoundryCheckpointSaver(
    BaseCheckpointSaver[str], AbstractAsyncContextManager["FoundryCheckpointSaver"]
):
    """Checkpoint saver backed by Azure AI Foundry checkpoint storage.

    Implements LangGraph's BaseCheckpointSaver interface using the
    FoundryCheckpointClient for remote storage.

    This saver only supports async operations. Sync methods will raise
    NotImplementedError.

    :param project_endpoint: The Azure AI Foundry project endpoint URL.
        Example: "https://<resource>.services.ai.azure.com/api/projects/<project-id>"
    :type project_endpoint: str
    :param credential: Credential for authentication. Must be an async credential.
    :type credential: Union[AsyncTokenCredential, TokenCredential]
    :param serde: Optional serializer protocol. Defaults to JsonPlusSerializer.
    :type serde: Optional[SerializerProtocol]

    Example::

        from azure.ai.agentserver.langgraph.checkpointer import FoundryCheckpointSaver
        from azure.identity.aio import DefaultAzureCredential

        saver = FoundryCheckpointSaver(
            project_endpoint="https://myresource.services.ai.azure.com/api/projects/my-project",
            credential=DefaultAzureCredential(),
        )

        # Use with LangGraph
        graph = builder.compile(checkpointer=saver)
    """

    def __init__(
        self,
        project_endpoint: str,
        credential: Union[AsyncTokenCredential, TokenCredential],
        *,
        serde: Optional[SerializerProtocol] = None,
    ) -> None:
        """Initialize the Foundry checkpoint saver.

        :param project_endpoint: The Azure AI Foundry project endpoint URL.
        :type project_endpoint: str
        :param credential: Credential for authentication. Must be an async credential.
        :type credential: Union[AsyncTokenCredential, TokenCredential]
        :param serde: Optional serializer protocol.
        :type serde: Optional[SerializerProtocol]
        :raises TypeError: If credential is not an AsyncTokenCredential.
        """
        super().__init__(serde=serde)
        if not isinstance(credential, AsyncTokenCredential):
            raise TypeError(
                "FoundryCheckpointSaver requires an AsyncTokenCredential. "
                "Please use an async credential like DefaultAzureCredential from azure.identity.aio."
            )
        self._client = FoundryCheckpointClient(project_endpoint, credential)
        self._session_cache: set[str] = set()

    async def __aenter__(self) -> "FoundryCheckpointSaver":
        """Enter the async context manager.

        :return: The saver instance.
        :rtype: FoundryCheckpointSaver
        """
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit the async context manager.

        :param exc_type: Exception type if an exception occurred.
        :type exc_type: Optional[type[BaseException]]
        :param exc_val: Exception value if an exception occurred.
        :type exc_val: Optional[BaseException]
        :param exc_tb: Exception traceback if an exception occurred.
        :type exc_tb: Optional[TracebackType]
        """
        await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def _ensure_session(self, thread_id: str) -> None:
        """Ensure a session exists for the thread.

        :param thread_id: The thread identifier.
        :type thread_id: str
        """
        if thread_id not in self._session_cache:
            session = CheckpointSession(session_id=thread_id)
            await self._client.upsert_session(session)
            self._session_cache.add(thread_id)

    async def _get_latest_checkpoint_id(
        self, thread_id: str, checkpoint_ns: str
    ) -> Optional[str]:
        """Find the latest checkpoint ID for a thread and namespace.

        :param thread_id: The thread identifier.
        :type thread_id: str
        :param checkpoint_ns: The checkpoint namespace.
        :type checkpoint_ns: str
        :return: The latest checkpoint ID, or None if not found.
        :rtype: Optional[str]
        """
        item_ids = await self._client.list_item_ids(thread_id)

        # Filter to checkpoint items in this namespace
        checkpoint_ids: List[str] = []
        for item_id in item_ids:
            try:
                parsed = parse_item_id(item_id.item_id)
                if parsed.item_type == "checkpoint" and parsed.checkpoint_ns == checkpoint_ns:
                    checkpoint_ids.append(parsed.checkpoint_id)
            except ValueError:
                continue

        if not checkpoint_ids:
            return None

        # Return the latest (max) checkpoint ID
        return max(checkpoint_ids)

    async def _load_pending_writes(
        self, thread_id: str, checkpoint_ns: str, checkpoint_id: str
    ) -> List[Tuple[str, str, Any]]:
        """Load pending writes for a checkpoint.

        :param thread_id: The thread identifier.
        :type thread_id: str
        :param checkpoint_ns: The checkpoint namespace.
        :type checkpoint_ns: str
        :param checkpoint_id: The checkpoint identifier.
        :type checkpoint_id: str
        :return: List of pending writes as (task_id, channel, value) tuples.
        :rtype: List[Tuple[str, str, Any]]
        """
        item_ids = await self._client.list_item_ids(thread_id)
        writes: List[Tuple[str, str, Any]] = []

        for item_id in item_ids:
            try:
                parsed = parse_item_id(item_id.item_id)
                if (
                    parsed.item_type == "writes"
                    and parsed.checkpoint_ns == checkpoint_ns
                    and parsed.checkpoint_id == checkpoint_id
                ):
                    item = await self._client.read_item(item_id)
                    if item:
                        task_id, channel, value, _ = self.serde.loads_typed(item.data)
                        writes.append((task_id, channel, value))
            except (ValueError, TypeError):
                continue

        return writes

    async def _load_blobs(
        self, thread_id: str, checkpoint_ns: str, checkpoint_id: str, versions: ChannelVersions
    ) -> Dict[str, Any]:
        """Load channel blobs for a checkpoint.

        :param thread_id: The thread identifier.
        :type thread_id: str
        :param checkpoint_ns: The checkpoint namespace.
        :type checkpoint_ns: str
        :param checkpoint_id: The checkpoint identifier.
        :type checkpoint_id: str
        :param versions: The channel versions to load.
        :type versions: ChannelVersions
        :return: Dictionary of channel values.
        :rtype: Dict[str, Any]
        """
        channel_values: Dict[str, Any] = {}

        for channel, version in versions.items():
            blob_item_id = make_item_id(
                checkpoint_ns, checkpoint_id, "blob", f"{channel}:{version}"
            )
            item_id = CheckpointItemId(session_id=thread_id, item_id=blob_item_id)
            item = await self._client.read_item(item_id)
            if item:
                type_tag, data = self.serde.loads_typed(item.data)
                if type_tag != "empty":
                    channel_values[channel] = data

        return channel_values

    # Async methods (primary implementation)

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Asynchronously get a checkpoint tuple by config.

        :param config: Configuration specifying which checkpoint to retrieve.
        :type config: RunnableConfig
        :return: The checkpoint tuple, or None if not found.
        :rtype: Optional[CheckpointTuple]
        """
        thread_id: str = config["configurable"]["thread_id"]
        checkpoint_ns: str = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)

        # Ensure session exists
        await self._ensure_session(thread_id)

        # If no checkpoint_id, find the latest
        if not checkpoint_id:
            checkpoint_id = await self._get_latest_checkpoint_id(thread_id, checkpoint_ns)
            if not checkpoint_id:
                return None

        # Load the checkpoint item
        item_id_str = make_item_id(checkpoint_ns, checkpoint_id, "checkpoint")
        item = await self._client.read_item(
            CheckpointItemId(session_id=thread_id, item_id=item_id_str)
        )
        if not item:
            return None

        # Deserialize checkpoint data
        checkpoint_data = self.serde.loads_typed(item.data)
        checkpoint: Checkpoint = checkpoint_data["checkpoint"]
        metadata: CheckpointMetadata = checkpoint_data["metadata"]

        # Load channel values (blobs)
        channel_values = await self._load_blobs(
            thread_id, checkpoint_ns, checkpoint_id, checkpoint.get("channel_versions", {})
        )
        checkpoint = {**checkpoint, "channel_values": channel_values}

        # Load pending writes
        pending_writes = await self._load_pending_writes(thread_id, checkpoint_ns, checkpoint_id)

        # Build parent config if parent exists
        parent_config: Optional[RunnableConfig] = None
        if item.parent_id:
            try:
                parent_parsed = parse_item_id(item.parent_id)
                parent_config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": parent_parsed.checkpoint_ns,
                        "checkpoint_id": parent_parsed.checkpoint_id,
                    }
                }
            except ValueError:
                pass

        return CheckpointTuple(
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id,
                }
            },
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=parent_config,
            pending_writes=pending_writes,
        )

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Asynchronously store a checkpoint.

        :param config: Configuration for the checkpoint.
        :type config: RunnableConfig
        :param checkpoint: The checkpoint to store.
        :type checkpoint: Checkpoint
        :param metadata: Additional metadata for the checkpoint.
        :type metadata: CheckpointMetadata
        :param new_versions: New channel versions as of this write.
        :type new_versions: ChannelVersions
        :return: Updated configuration with the checkpoint ID.
        :rtype: RunnableConfig
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]

        # Ensure session exists
        await self._ensure_session(thread_id)

        # Determine parent
        parent_checkpoint_id = config["configurable"].get("checkpoint_id")
        parent_item_id: Optional[str] = None
        if parent_checkpoint_id:
            parent_item_id = make_item_id(checkpoint_ns, parent_checkpoint_id, "checkpoint")

        # Prepare checkpoint data (without channel_values - stored as blobs)
        checkpoint_copy = checkpoint.copy()
        channel_values: Dict[str, Any] = checkpoint_copy.pop("channel_values", {})  # type: ignore[misc]

        checkpoint_data = self.serde.dumps_typed({
            "checkpoint": checkpoint_copy,
            "metadata": metadata,
        })

        # Create checkpoint item
        item_id_str = make_item_id(checkpoint_ns, checkpoint_id, "checkpoint")
        items: List[CheckpointItem] = [
            CheckpointItem(
                session_id=thread_id,
                item_id=item_id_str,
                data=checkpoint_data,
                parent_id=parent_item_id,
            )
        ]

        # Create blob items for channel values with new versions
        for channel, version in new_versions.items():
            if channel in channel_values:
                blob_data = self.serde.dumps_typed(channel_values[channel])
            else:
                blob_data = self.serde.dumps_typed(("empty", b""))

            blob_item_id = make_item_id(
                checkpoint_ns, checkpoint_id, "blob", f"{channel}:{version}"
            )
            items.append(
                CheckpointItem(
                    session_id=thread_id,
                    item_id=blob_item_id,
                    data=blob_data,
                    parent_id=item_id_str,
                )
            )

        await self._client.create_items(items)

        logger.debug(
            "Saved checkpoint %s to Foundry session %s",
            checkpoint_id,
            thread_id,
        )

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """Asynchronously store intermediate writes for a checkpoint.

        :param config: Configuration of the related checkpoint.
        :type config: RunnableConfig
        :param writes: List of writes to store as (channel, value) pairs.
        :type writes: Sequence[Tuple[str, Any]]
        :param task_id: Identifier for the task creating the writes.
        :type task_id: str
        :param task_path: Path of the task creating the writes.
        :type task_path: str
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"]["checkpoint_id"]

        checkpoint_item_id = make_item_id(checkpoint_ns, checkpoint_id, "checkpoint")

        items: List[CheckpointItem] = []
        for idx, (channel, value) in enumerate(writes):
            write_data = self.serde.dumps_typed((task_id, channel, value, task_path))
            write_item_id = make_item_id(
                checkpoint_ns, checkpoint_id, "writes", f"{task_id}:{idx}"
            )
            items.append(
                CheckpointItem(
                    session_id=thread_id,
                    item_id=write_item_id,
                    data=write_data,
                    parent_id=checkpoint_item_id,
                )
            )

        if items:
            await self._client.create_items(items)
            logger.debug(
                "Saved %d writes for checkpoint %s",
                len(items),
                checkpoint_id,
            )

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """Asynchronously list checkpoints matching filter criteria.

        :param config: Base configuration for filtering checkpoints.
        :type config: Optional[RunnableConfig]
        :keyword filter: Additional filtering criteria for metadata.
        :type filter: Optional[Dict[str, Any]]
        :keyword before: List checkpoints created before this configuration.
        :type before: Optional[RunnableConfig]
        :keyword limit: Maximum number of checkpoints to return.
        :type limit: Optional[int]
        :return: Async iterator of matching checkpoint tuples.
        :rtype: AsyncIterator[CheckpointTuple]
        """
        if not config:
            return

        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns")

        # Get all items for this session
        item_ids = await self._client.list_item_ids(thread_id)

        # Filter to checkpoint items only
        checkpoint_items: List[Tuple[ParsedItemId, CheckpointItemId]] = []
        for item_id in item_ids:
            try:
                parsed = parse_item_id(item_id.item_id)
                if parsed.item_type == "checkpoint":
                    # Filter by namespace if specified
                    if checkpoint_ns is None or parsed.checkpoint_ns == checkpoint_ns:
                        checkpoint_items.append((parsed, item_id))
            except ValueError:
                continue

        # Sort by checkpoint_id in reverse order (newest first)
        checkpoint_items.sort(key=lambda x: x[0].checkpoint_id, reverse=True)

        # Apply before cursor
        if before:
            before_id = get_checkpoint_id(before)
            if before_id:
                checkpoint_items = [
                    (p, i) for p, i in checkpoint_items if p.checkpoint_id < before_id
                ]

        # Apply limit
        if limit:
            checkpoint_items = checkpoint_items[:limit]

        # Load and yield each checkpoint
        for parsed, _ in checkpoint_items:
            tuple_config: RunnableConfig = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": parsed.checkpoint_ns,
                    "checkpoint_id": parsed.checkpoint_id,
                }
            }
            checkpoint_tuple = await self.aget_tuple(tuple_config)
            if checkpoint_tuple:
                # Apply metadata filter if provided
                if filter:
                    if not all(
                        checkpoint_tuple.metadata.get(k) == v for k, v in filter.items()
                    ):
                        continue
                yield checkpoint_tuple

    async def adelete_thread(self, thread_id: str) -> None:
        """Delete all checkpoints and writes for a thread.

        :param thread_id: The thread ID whose checkpoints should be deleted.
        :type thread_id: str
        """
        await self._client.delete_session(thread_id)
        self._session_cache.discard(thread_id)
        logger.debug("Deleted session %s", thread_id)

    # Sync methods (raise NotImplementedError)

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Sync version not supported - use aget_tuple instead.

        :param config: Configuration specifying which checkpoint to retrieve.
        :type config: RunnableConfig
        :return: The checkpoint tuple, or None if not found.
        :rtype: Optional[CheckpointTuple]
        :raises NotImplementedError: Always raised.
        """
        raise NotImplementedError(
            "FoundryCheckpointSaver requires async usage. Use aget_tuple() instead."
        )

    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """Sync version not supported - use alist instead.

        :param config: Base configuration for filtering checkpoints.
        :type config: Optional[RunnableConfig]
        :keyword filter: Additional filtering criteria for metadata.
        :type filter: Optional[Dict[str, Any]]
        :keyword before: List checkpoints created before this configuration.
        :type before: Optional[RunnableConfig]
        :keyword limit: Maximum number of checkpoints to return.
        :type limit: Optional[int]
        :return: Iterator of matching checkpoint tuples.
        :rtype: Iterator[CheckpointTuple]
        :raises NotImplementedError: Always raised.
        """
        raise NotImplementedError(
            "FoundryCheckpointSaver requires async usage. Use alist() instead."
        )

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Sync version not supported - use aput instead.

        :param config: Configuration for the checkpoint.
        :type config: RunnableConfig
        :param checkpoint: The checkpoint to store.
        :type checkpoint: Checkpoint
        :param metadata: Additional metadata for the checkpoint.
        :type metadata: CheckpointMetadata
        :param new_versions: New channel versions as of this write.
        :type new_versions: ChannelVersions
        :return: Updated configuration with the checkpoint ID.
        :rtype: RunnableConfig
        :raises NotImplementedError: Always raised.
        """
        raise NotImplementedError(
            "FoundryCheckpointSaver requires async usage. Use aput() instead."
        )

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """Sync version not supported - use aput_writes instead.

        :param config: Configuration of the related checkpoint.
        :type config: RunnableConfig
        :param writes: List of writes to store as (channel, value) pairs.
        :type writes: Sequence[Tuple[str, Any]]
        :param task_id: Identifier for the task creating the writes.
        :type task_id: str
        :param task_path: Path of the task creating the writes.
        :type task_path: str
        :return: None
        :rtype: None
        :raises NotImplementedError: Always raised.
        """
        raise NotImplementedError(
            "FoundryCheckpointSaver requires async usage. Use aput_writes() instead."
        )

    def delete_thread(self, thread_id: str) -> None:
        """Sync version not supported - use adelete_thread instead.

        :param thread_id: Identifier of the thread to delete.
        :type thread_id: str
        :return: None
        :rtype: None
        :raises NotImplementedError: Always raised.
        """
        raise NotImplementedError(
            "FoundryCheckpointSaver requires async usage. Use adelete_thread() instead."
        )

    def get_next_version(self, current: Optional[str], channel: None) -> str:
        """Generate the next version ID for a channel.

        Uses string versions with format "{counter}.{random}".

        :param current: The current version identifier.
        :type current: Optional[str]
        :param channel: Deprecated argument, kept for backwards compatibility.
        :type channel: None
        :return: The next version identifier.
        :rtype: str
        """
        import random as rand

        if current is None:
            current_v = 0
        elif isinstance(current, int):
            current_v = current
        else:
            current_v = int(current.split(".")[0])
        next_v = current_v + 1
        next_h = rand.random()
        return f"{next_v:032}.{next_h:016}"
