# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from abc import ABC, abstractmethod
from typing import Dict, Optional

from agent_framework import (
    CheckpointStorage,
    FileCheckpointStorage,
    InMemoryCheckpointStorage,
)


class CheckpointRepository(ABC):
    """
    Repository interface for storing and retrieving checkpoints.
    
    :meta private:
    """
    @abstractmethod
    async def get_or_create(self, conversation_id: Optional[str]) -> Optional[CheckpointStorage]:
        """Retrieve or create a checkpoint storage by conversation ID.

        :param conversation_id: The unique identifier for the checkpoint.
        :type conversation_id: Optional[str]
        :return: The CheckpointStorage if found or created, None otherwise.
        :rtype: Optional[CheckpointStorage]
        """


class InMemoryCheckpointRepository(CheckpointRepository):
    """In-memory implementation of CheckpointRepository."""
    def __init__(self) -> None:
        self._inventory: Dict[str, CheckpointStorage] = {}

    async def get_or_create(self, conversation_id: Optional[str]) -> Optional[CheckpointStorage]:
        """Retrieve or create a checkpoint storage by conversation ID.

        :param conversation_id: The unique identifier for the checkpoint.
        :type conversation_id: Optional[str]
        :return: The CheckpointStorage if found or created, None otherwise.
        :rtype: Optional[CheckpointStorage]
        """
        if not conversation_id:
            return None
        if conversation_id not in self._inventory:
            self._inventory[conversation_id] = InMemoryCheckpointStorage()
        return self._inventory[conversation_id]


class FileCheckpointRepository(CheckpointRepository):
    """File-based implementation of CheckpointRepository."""
    def __init__(self, storage_path: str) -> None:
        self._storage_path = storage_path
        self._inventory: Dict[str, CheckpointStorage] = {}
        os.makedirs(self._storage_path, exist_ok=True)

    async def get_or_create(self, conversation_id: Optional[str]) -> Optional[CheckpointStorage]:
        """Retrieve or create a checkpoint storage by conversation ID.

        :param conversation_id: The unique identifier for the checkpoint.
        :type conversation_id: Optional[str]
        :return: The CheckpointStorage if found or created, None otherwise.
        :rtype: Optional[CheckpointStorage]
        """
        if not conversation_id:
            return None
        if conversation_id not in self._inventory:
            self._inventory[conversation_id] = FileCheckpointStorage(self._get_dir_path(conversation_id))
        return self._inventory[conversation_id]

    def _get_dir_path(self, conversation_id: str) -> str:
        return os.path.join(self._storage_path, conversation_id)
