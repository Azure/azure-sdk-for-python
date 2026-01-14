from abc import ABC, abstractmethod
import json
import os
from typing import Any, Optional

from agent_framework import AgentThread, AgentProtocol


class AgentThreadRepository(ABC):
    """AgentThread repository to manage saved thread messages of agent threads and workflows."""

    @abstractmethod
    async def get(self, conversation_id: str) -> Optional[AgentThread]:
        """Retrieve the savedt thread for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: str

        :return: The saved AgentThread if available, None otherwise.
        :rtype: Optional[AgentThread]
        """

    @abstractmethod    
    async def set(self, conversation_id: str, thread: AgentThread) -> None:
        """Save the thread for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: str
        :param thread: The thread to save.
        :type thread: AgentThread
        """


class InMemoryAgentThreadRepository(AgentThreadRepository):
    """In-memory implementation of AgentThreadRepository."""
    def __init__(self) -> None:
        self._inventory: dict[str, AgentThread] = {}

    async def get(self, conversation_id: str) -> Optional[AgentThread]:
        """Retrieve the saved thread for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: str

        :return: The saved AgentThread if available, None otherwise.
        :rtype: Optional[AgentThread]
        """
        if conversation_id in self._inventory:
            return self._inventory[conversation_id]
        return None

    async def set(self, conversation_id: str, thread: AgentThread) -> None:
        """Save the thread for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: str
        :param thread: The thread to save.
        :type thread: AgentThread
        """
        if conversation_id and thread:
            self._inventory[conversation_id] = thread


class SerializedAgentThreadRepository(AgentThreadRepository):
    """Implementation of AgentThreadRepository with AgentThread serialization."""
    def __init__(self, agent: AgentProtocol) -> None:
        """
        Initialize the repository with the given agent.
        
        :param agent: The agent instance.
        :type agent: AgentProtocol
        """
        self._agent = agent

    async def get(self, conversation_id: str) -> Optional[AgentThread]:
        """Retrieve the saved thread for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: str

        :return: The saved AgentThread if available, None otherwise.
        :rtype: Optional[AgentThread]
        """
        serialized_thread = await self.read_from_storage(conversation_id)
        if serialized_thread:
            thread = await self._agent.deserialize_thread(serialized_thread)
            return thread
        return None

    async def set(self, conversation_id: str, thread: AgentThread) -> None:
        """Save the thread for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: str
        :param thread: The thread to save.
        :type thread: AgentThread
        """
        serialized_thread = await thread.serialize()
        await self.write_to_storage(conversation_id, serialized_thread)

    async def read_from_storage(self, conversation_id: str) -> Optional[Any]:
        """Read the serialized thread from storage.

        :param conversation_id: The conversation ID.
        :type conversation_id: str

        :return: The serialized thread if available, None otherwise.
        :rtype: Optional[Any]
        """
        raise NotImplementedError("read_from_storage is not implemented.")
    
    async def write_to_storage(self, conversation_id: str, serialized_thread: Any) -> None:
        """Write the serialized thread to storage.

        :param conversation_id: The conversation ID.
        :type conversation_id: str
        :param serialized_thread: The serialized thread to save.
        :type serialized_thread: Any
        """
        raise NotImplementedError("write_to_storage is not implemented.")
    

class JsonLocalFileAgentThreadRepository(SerializedAgentThreadRepository):
    """Json based implementation of AgentThreadRepository using local file storage."""
    def __init__(self, agent: AgentProtocol, storage_path: str) -> None:
        super().__init__(agent)
        self._storage_path = storage_path
        os.makedirs(self._storage_path, exist_ok=True)

    async def read_from_storage(self, conversation_id: str) -> Optional[Any]:
        file_path = self._get_file_path(conversation_id)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                serialized_thread = f.read()
                if serialized_thread:
                    return json.loads(serialized_thread)
        return None

    async def write_to_storage(self, conversation_id: str, serialized_thread: Any) -> None:
        serialized_str = json.dumps(serialized_thread)
        file_path = self._get_file_path(conversation_id)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(serialized_str)

    def _get_file_path(self, conversation_id: str) -> str:
        return os.path.join(self._storage_path, f"{conversation_id}.json")