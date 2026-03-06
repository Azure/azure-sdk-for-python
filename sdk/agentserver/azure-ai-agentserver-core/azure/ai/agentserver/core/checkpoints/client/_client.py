# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=client-method-missing-kwargs,client-accepts-api-version-keyword,missing-client-constructor-parameter-kwargs
"""Asynchronous client for Azure AI Foundry checkpoint storage API."""

from typing import Any, AsyncContextManager, List, Optional

from azure.core import AsyncPipelineClient
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async

from ._configuration import FoundryCheckpointClientConfiguration
from ._models import CheckpointItem, CheckpointItemId, CheckpointSession
from .operations import CheckpointItemOperations, CheckpointSessionOperations


class FoundryCheckpointClient(AsyncContextManager["FoundryCheckpointClient"]):
    """Asynchronous client for Azure AI Foundry checkpoint storage API.

    This client provides access to checkpoint storage for workflow state persistence,
    enabling checkpoint save, load, list, and delete operations.

    :param endpoint: The fully qualified project endpoint for the Azure AI Foundry service.
        Example: "https://<resource>.services.ai.azure.com/api/projects/<project-id>"
    :type endpoint: str
    :param credential: Credential for authenticating requests to the service.
        Use credentials from azure-identity like DefaultAzureCredential.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    """

    def __init__(
        self,
        endpoint: str,
        credential: "AsyncTokenCredential",
    ) -> None:
        """Initialize the asynchronous Azure AI Checkpoint Client.

        :param endpoint: The project endpoint URL (includes project context).
        :type endpoint: str
        :param credential: Credentials for authenticating requests.
        :type credential: ~azure.core.credentials_async.AsyncTokenCredential
        """
        config = FoundryCheckpointClientConfiguration(credential)
        self._client: AsyncPipelineClient = AsyncPipelineClient(
            base_url=endpoint, config=config
        )
        self._sessions = CheckpointSessionOperations(self._client)
        self._items = CheckpointItemOperations(self._client)

    # Session operations

    @distributed_trace_async
    async def upsert_session(self, session: CheckpointSession) -> CheckpointSession:
        """Create or update a checkpoint session.

        :param session: The checkpoint session to upsert.
        :type session: CheckpointSession
        :return: The upserted checkpoint session.
        :rtype: CheckpointSession
        """
        return await self._sessions.upsert(session)

    @distributed_trace_async
    async def read_session(self, session_id: str) -> Optional[CheckpointSession]:
        """Read a checkpoint session by ID.

        :param session_id: The session identifier.
        :type session_id: str
        :return: The checkpoint session if found, None otherwise.
        :rtype: Optional[CheckpointSession]
        """
        return await self._sessions.read(session_id)

    @distributed_trace_async
    async def delete_session(self, session_id: str) -> None:
        """Delete a checkpoint session.

        :param session_id: The session identifier.
        :type session_id: str
        """
        await self._sessions.delete(session_id)

    # Item operations

    @distributed_trace_async
    async def create_items(self, items: List[CheckpointItem]) -> List[CheckpointItem]:
        """Create checkpoint items in batch.

        :param items: The checkpoint items to create.
        :type items: List[CheckpointItem]
        :return: The created checkpoint items.
        :rtype: List[CheckpointItem]
        """
        return await self._items.create_batch(items)

    @distributed_trace_async
    async def read_item(self, item_id: CheckpointItemId) -> Optional[CheckpointItem]:
        """Read a checkpoint item by ID.

        :param item_id: The checkpoint item identifier.
        :type item_id: CheckpointItemId
        :return: The checkpoint item if found, None otherwise.
        :rtype: Optional[CheckpointItem]
        """
        return await self._items.read(item_id)

    @distributed_trace_async
    async def delete_item(self, item_id: CheckpointItemId) -> bool:
        """Delete a checkpoint item.

        :param item_id: The checkpoint item identifier.
        :type item_id: CheckpointItemId
        :return: True if the item was deleted, False if not found.
        :rtype: bool
        """
        return await self._items.delete(item_id)

    @distributed_trace_async
    async def list_item_ids(
        self, session_id: str, parent_id: Optional[str] = None
    ) -> List[CheckpointItemId]:
        """List checkpoint item IDs for a session.

        :param session_id: The session identifier.
        :type session_id: str
        :param parent_id: Optional parent item identifier for filtering.
        :type parent_id: Optional[str]
        :return: List of checkpoint item identifiers.
        :rtype: List[CheckpointItemId]
        """
        return await self._items.list_ids(session_id, parent_id)

    # Context manager methods

    async def close(self) -> None:
        """Close the underlying HTTP pipeline."""
        await self._client.close()

    async def __aenter__(self) -> "FoundryCheckpointClient":
        """Enter the async context manager.

        :return: The client instance.
        :rtype: FoundryCheckpointClient
        """
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        """Exit the async context manager.

        :param exc_details: Exception details if an exception occurred.
        :type exc_details: Any
        :return: None
        :rtype: None
        """
        await self._client.__aexit__(*exc_details)
