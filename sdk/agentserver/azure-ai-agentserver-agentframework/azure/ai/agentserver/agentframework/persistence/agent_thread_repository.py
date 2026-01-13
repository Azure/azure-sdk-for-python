from abc import ABC, abstractmethod
import json
import os
from typing import Any, Optional

from agent_framework import AgentThread, AgentProtocol


class AgentThreadRepository(ABC):
    """AgentThread repository to manage saved thread messages of agent threads and workflows."""

    @abstractmethod
    async def get(self, agent: AgentProtocol, conversation_id: str) -> Optional[AgentThread]:
        """Retrieve the savedt thread for a given conversation ID.

        :param agent: The agent instance.
        :type agent: AgentProtocol
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

    async def get(self, agent: AgentProtocol, conversation_id: str) -> Optional[AgentThread]:
        """Retrieve the saved thread for a given conversation ID.

        :param agent: The agent instance.
        :type agent: AgentProtocol
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


class JsonSerializedAgentThreadRepository(AgentThreadRepository):
    """Json File based implementation of AgentThreadRepository."""
    def __init__(self, storage_path: str) -> None:
        """
        Initialize the JsonSerializedAgentThreadRepository.

        :param storage_path: The path to the storage directory.
        :type storage_path: str
        """
        self._storage_path = storage_path
        os.makedirs(self._storage_path, exist_ok=True)

    async def get(self, agent: AgentProtocol, conversation_id: str) -> Optional[AgentThread]:
        """Retrieve the saved thread for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: str

        :return: The saved AgentThread if available, None otherwise.
        :rtype: Optional[AgentThread]
        """
        serialized_thread = self._read_from_file(conversation_id)
        if serialized_thread:
            thread_dict = json.loads(serialized_thread)
            thread = await agent.deserialize_thread(thread_dict)
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
        serialized_str = json.dumps(serialized_thread)
        self._write_to_file(conversation_id, serialized_str)

    def _write_to_file(self, conversation_id: str, serialized_thread: str) -> None:
        file_path = self._get_file_path(conversation_id)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(serialized_thread)

    def _read_from_file(self, conversation_id: str) -> Optional[str]:
        file_path = self._get_file_path(conversation_id)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return None
    
    def _get_file_path(self, conversation_id: str) -> str:
        return os.path.join(self._storage_path, f"{conversation_id}.json")