from typing import Any, Optional

from agent_framework import AgentThread, BaseAgent


class AgentStateInventory:
    """Checkpoint inventory to manage saved states of agent threads and workflows."""

    async def get(self, conversation_id: str) -> Optional[Any]:
        """Retrieve the saved state for a given conversation ID.

        Args:
            conversation_id (str): The conversation ID.
        """
        pass
    
    async def set(self, conversation_id: str, state: Any) -> None:
        """Save the state for a given conversation ID.

        Args:
            conversation_id (str): The conversation ID.
            state (Any): The state to save.
        """
        pass


class InMemoryThreadAgentStateInventory(AgentStateInventory):
    """In-memory implementation of AgentStateInventory."""
    def __init__(self, agent: BaseAgent) -> None:
        self._agent = agent
        self._inventory: dict[str, AgentThread] = {}

    async def get(self, conversation_id: str) -> Optional[AgentThread]:
        """Retrieve the saved state for a given conversation ID.

        Args:
            conversation_id (str): The conversation ID.
        """
        if conversation_id in self._inventory:
            serialized_thread = self._inventory[conversation_id]
            return await self._agent.deserialize_thread(serialized_thread)
        return None

    async def set(self, conversation_id: str, state: AgentThread) -> None:
        """Save the state for a given conversation ID.

        Args:
            conversation_id (str): The conversation ID.
            state (AgentThread): The state to save.
        """
        if conversation_id and state:
            serialized_thread = await state.serialize()
            self._inventory[conversation_id] = serialized_thread


class InMemoryCheckpointAgentStateInventory(AgentStateInventory):
    """In-memory implementation of AgentStateInventory for workflow checkpoints."""
    def __init__(self) -> None:
        self._inventory: dict[str, Any] = {}

    async def get(self, conversation_id: str) -> Optional[Any]:
        """Retrieve the saved state for a given conversation ID.

        Args:
            conversation_id (str): The conversation ID.
        """
        return self._inventory.get(conversation_id, None)

    async def set(self, conversation_id: str, state: Any) -> None:
        """Save the state for a given conversation ID.

        Args:
            conversation_id (str): The conversation ID.
            state (Any): The state to save.
        """
        if conversation_id and state:
            self._inventory[conversation_id] = state