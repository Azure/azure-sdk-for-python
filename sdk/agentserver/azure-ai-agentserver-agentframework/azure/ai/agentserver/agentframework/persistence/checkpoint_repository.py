from abc import ABC, abstractmethod
import os
from typing import Any, Optional

from agent_framework import (
    CheckpointStorage,
    InMemoryCheckpointStorage,
    FileCheckpointStorage,
)

class CheckpointRepository(ABC):
    """Repository interface for storing and retrieving checkpoints."""
    @abstractmethod
    async def get_or_create(self, conversation_id: str) -> Optional[CheckpointStorage]:
        """Retrieve or create a checkpoint storage by conversation ID.

        :param conversation_id: The unique identifier for the checkpoint.
        :type conversation_id: str
        :return: The CheckpointStorage if found or created, None otherwise.
        :rtype: Optional[CheckpointStorage]
        """


class InMemoryCheckpointRepository(CheckpointRepository):
    """In-memory implementation of CheckpointRepository."""
    def __init__(self) -> None:
        self._inventory: dict[str, CheckpointStorage] = {}

    async def get_or_create(self, conversation_id: str) -> Optional[CheckpointStorage]:
        """Retrieve or create a checkpoint storage by conversation ID.

        :param conversation_id: The unique identifier for the checkpoint.
        :type conversation_id: str
        :return: The CheckpointStorage if found or created, None otherwise.
        :rtype: Optional[CheckpointStorage]
        """
        if conversation_id not in self._inventory:
            self._inventory[conversation_id] = InMemoryCheckpointStorage()
        return self._inventory[conversation_id]


class FileCheckpointRepository(CheckpointRepository):
    """File-based implementation of CheckpointRepository."""
    def __init__(self, storage_path: str) -> None:
        self._storage_path = storage_path
        self._inventory: dict[str, CheckpointStorage] = {}
        os.makedirs(self._storage_path, exist_ok=True)

    async def get_or_create(self, conversation_id: str) -> Optional[CheckpointStorage]:
        """Retrieve or create a checkpoint storage by conversation ID.

        :param conversation_id: The unique identifier for the checkpoint.
        :type conversation_id: str
        :return: The CheckpointStorage if found or created, None otherwise.
        :rtype: Optional[CheckpointStorage]
        """
        if conversation_id not in self._inventory:
            self._inventory[conversation_id] = FileCheckpointStorage(self._get_dir_path(conversation_id))
        return self._inventory[conversation_id]
    
    def _get_dir_path(self, conversation_id: str) -> str:
        return os.path.join(self._storage_path, conversation_id)