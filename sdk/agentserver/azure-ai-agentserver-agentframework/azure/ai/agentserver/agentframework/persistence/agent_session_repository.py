# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from agent_framework import AgentSession


class AgentSessionRepository(ABC):
    """
    Repository to manage persisted agent session state for conversations and workflows.

    :meta private:
    """

    @abstractmethod
    async def get(
        self,
        conversation_id: Optional[str],
    ) -> Optional[AgentSession]:
        """Retrieve the saved session for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]

        :return: The saved AgentSession if available, None otherwise.
        :rtype: Optional[AgentSession]
        """

    @abstractmethod
    async def set(self, conversation_id: Optional[str], session: AgentSession) -> None:
        """Save the session for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]
        :param session: The session to save.
        :type session: AgentSession
        """


class InMemoryAgentSessionRepository(AgentSessionRepository):
    """In-memory implementation of AgentSessionRepository."""

    def __init__(self) -> None:
        self._inventory: Dict[str, AgentSession] = {}

    async def get(
        self,
        conversation_id: Optional[str],
    ) -> Optional[AgentSession]:
        """Retrieve the saved session for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]
        :return: The saved AgentSession if available, None otherwise.
        :rtype: Optional[AgentSession]
        """
        if not conversation_id:
            return None
        if conversation_id in self._inventory:
            return self._inventory[conversation_id]
        return None

    async def set(self, conversation_id: Optional[str], session: AgentSession) -> None:
        """Save the session for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]
        :param session: The session to save.
        :type session: AgentSession
        """
        if not conversation_id or not session:
            return
        self._inventory[conversation_id] = session


class SerializedAgentSessionRepository(AgentSessionRepository):
    """Implementation of AgentSessionRepository with AgentSession serialization."""

    async def get(
        self,
        conversation_id: Optional[str],
    ) -> Optional[AgentSession]:
        """Retrieve the saved session for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]

        :return: The saved AgentSession if available, None otherwise.
        :rtype: Optional[AgentSession]
        """
        if not conversation_id:
            return None
        serialized_session = await self.read_from_storage(conversation_id)
        if serialized_session:
            return AgentSession.from_dict(serialized_session)
        return None

    async def set(self, conversation_id: Optional[str], session: AgentSession) -> None:
        """Save the session for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]
        :param session: The session to save.
        :type session: AgentSession
        """
        if not conversation_id:
            return
        serialized_session = session.to_dict()
        await self.write_to_storage(conversation_id, serialized_session)

    async def read_from_storage(self, conversation_id: Optional[str]) -> Optional[Any]:
        """Read the serialized session from storage.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]

        :return: The serialized session if available, None otherwise.
        :rtype: Optional[Any]
        """
        raise NotImplementedError("read_from_storage is not implemented.")

    async def write_to_storage(self, conversation_id: Optional[str], serialized_session: Any) -> None:
        """Write the serialized session to storage.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]
        :param serialized_session: The serialized session to save.
        :type serialized_session: Any
        :return: None
        :rtype: None
        """
        raise NotImplementedError("write_to_storage is not implemented.")


class JsonLocalFileAgentSessionRepository(SerializedAgentSessionRepository):
    """Json based implementation of AgentSessionRepository using local file storage."""

    def __init__(self, storage_path: str) -> None:
        self._storage_path = storage_path
        os.makedirs(self._storage_path, exist_ok=True)

    async def read_from_storage(self, conversation_id: Optional[str]) -> Optional[Any]:
        if not conversation_id:
            return None
        file_path = self._get_file_path(conversation_id)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                serialized_session = f.read()
                if serialized_session:
                    return json.loads(serialized_session)
        return None

    async def write_to_storage(self, conversation_id: Optional[str], serialized_session: Any) -> None:
        if not conversation_id:
            return
        serialized_str = json.dumps(serialized_session)
        file_path = self._get_file_path(conversation_id)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(serialized_str)

    def _get_file_path(self, conversation_id: str) -> str:
        return os.path.join(self._storage_path, f"{conversation_id}.json")
