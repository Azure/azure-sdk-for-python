# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Mock implementation of FoundryCheckpointClient for testing."""

from typing import Any, Dict, List, Optional

from azure.ai.agentserver.core.checkpoints.client import (
    CheckpointItem,
    CheckpointItemId,
    CheckpointSession,
)


class MockFoundryCheckpointClient:
    """In-memory mock for FoundryCheckpointClient for unit testing.

    Stores checkpoints in memory without making any HTTP calls.
    """

    def __init__(self, endpoint: str = "https://mock.endpoint") -> None:
        """Initialize the mock client.

        :param endpoint: The mock endpoint URL.
        :type endpoint: str
        """
        self._endpoint = endpoint
        self._sessions: Dict[str, CheckpointSession] = {}
        self._items: Dict[str, CheckpointItem] = {}

    def _item_key(self, item_id: CheckpointItemId) -> str:
        """Generate a unique key for a checkpoint item.

        :param item_id: The checkpoint item identifier.
        :type item_id: CheckpointItemId
        :return: The unique key.
        :rtype: str
        """
        return f"{item_id.session_id}:{item_id.item_id}"

    # Session operations

    async def upsert_session(self, session: CheckpointSession) -> CheckpointSession:
        """Create or update a checkpoint session.

        :param session: The checkpoint session to upsert.
        :type session: CheckpointSession
        :return: The upserted checkpoint session.
        :rtype: CheckpointSession
        """
        self._sessions[session.session_id] = session
        return session

    async def read_session(self, session_id: str) -> Optional[CheckpointSession]:
        """Read a checkpoint session by ID.

        :param session_id: The session identifier.
        :type session_id: str
        :return: The checkpoint session if found, None otherwise.
        :rtype: Optional[CheckpointSession]
        """
        return self._sessions.get(session_id)

    async def delete_session(self, session_id: str) -> None:
        """Delete a checkpoint session.

        :param session_id: The session identifier.
        :type session_id: str
        """
        self._sessions.pop(session_id, None)
        # Also delete all items in the session
        keys_to_delete = [
            key for key, item in self._items.items() if item.session_id == session_id
        ]
        for key in keys_to_delete:
            del self._items[key]

    # Item operations

    async def create_items(self, items: List[CheckpointItem]) -> List[CheckpointItem]:
        """Create checkpoint items in batch.

        :param items: The checkpoint items to create.
        :type items: List[CheckpointItem]
        :return: The created checkpoint items.
        :rtype: List[CheckpointItem]
        """
        for item in items:
            key = self._item_key(item.to_item_id())
            self._items[key] = item
        return items

    async def read_item(self, item_id: CheckpointItemId) -> Optional[CheckpointItem]:
        """Read a checkpoint item by ID.

        :param item_id: The checkpoint item identifier.
        :type item_id: CheckpointItemId
        :return: The checkpoint item if found, None otherwise.
        :rtype: Optional[CheckpointItem]
        """
        key = self._item_key(item_id)
        return self._items.get(key)

    async def delete_item(self, item_id: CheckpointItemId) -> bool:
        """Delete a checkpoint item.

        :param item_id: The checkpoint item identifier.
        :type item_id: CheckpointItemId
        :return: True if the item was deleted, False if not found.
        :rtype: bool
        """
        key = self._item_key(item_id)
        if key in self._items:
            del self._items[key]
            return True
        return False

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
        result = []
        for item in self._items.values():
            if item.session_id == session_id:
                if parent_id is None or item.parent_id == parent_id:
                    result.append(item.to_item_id())
        return result

    # Context manager methods

    async def close(self) -> None:
        """Close the client (no-op for mock)."""
        pass

    async def __aenter__(self) -> "MockFoundryCheckpointClient":
        """Enter the async context manager.

        :return: The client instance.
        :rtype: MockFoundryCheckpointClient
        """
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        """Exit the async context manager.

        :param exc_details: Exception details if an exception occurred.
        """
        pass
