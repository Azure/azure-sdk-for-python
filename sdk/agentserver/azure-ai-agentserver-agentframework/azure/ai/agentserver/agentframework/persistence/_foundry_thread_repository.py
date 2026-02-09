
from typing import Optional, Union, Sequence, MutableMapping, Any
from agent_framework import AgentThread, AgentProtocol, ChatMessage, WorkflowAgent
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.credentials import TokenCredential
from azure.ai.projects.aio import AIProjectClient

from azure.ai.agentserver.core.logger import get_logger

from .agent_thread_repository import AgentThreadRepository

logger = get_logger()

class FoundryConversationThreadRepository(AgentThreadRepository):
    """A Foundry Conversation implementation of AgentThreadRepository."""
    def __init__(self,
                 agent: Optional[Union[AgentProtocol, WorkflowAgent]],
                 project_endpoint: str,
                 credential: Union[TokenCredential, AsyncTokenCredential]) -> None:
        self._agent = agent
        if not project_endpoint or not credential:
            raise ValueError("Both project_endpoint and credential are required for FoundryConversationThreadRepository.")
        self._client = AIProjectClient(project_endpoint, credential)
        self._inventory: dict[str, AgentThread] = {}

    async def get(
        self,
        conversation_id: Optional[str],
        agent: Optional[Union[AgentProtocol, WorkflowAgent]] = None,
    ) -> Optional[AgentThread]:
        """Retrieve the saved thread for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]
        :param agent: The agent instance. It will be used for in-memory repository for interface consistency.
        :type agent: Optional[Union[AgentProtocol, WorkflowAgent]]
        :return: The saved AgentThread if available, None otherwise.
        :rtype: Optional[AgentThread]
        """
        if not conversation_id:
            return None
        if conversation_id in self._inventory:
            return self._inventory[conversation_id]
        message_store = FoundryConversationMessageStore(conversation_id, self._client)
        await message_store.get_conversation_history()
        return AgentThread(message_store=message_store)

    async def set(self, conversation_id: Optional[str], thread: AgentThread) -> None:
        """Save the thread for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]
        :param thread: The thread to save.
        :type thread: AgentThread
        """
        if not conversation_id:
            raise ValueError("conversation_id is required to save an AgentThread.")
        self._inventory[conversation_id] = thread


class FoundryConversationMessageStore:
    """A Foundry Conversation implementation of ChatMessageStoreProtocol."""
    def __init__(self, conversation_id: str, client: AIProjectClient):
        self._conversation_id = conversation_id
        self._client = client
        self._conversation_messages: list[ChatMessage] = []
        self._cached_new_messages: list[ChatMessage] = []

    async def list_messages(self) -> list[ChatMessage]:
        """List all messages in the conversation."""
        # For simplicity, we are caching messages in memory. In a real implementation, you would fetch from Foundry.
        return self._conversation_messages + self._cached_new_messages

    async def add_messages(self, messages: Sequence[ChatMessage]) -> None:
        self._cached_new_messages.extend(messages)
    
    @classmethod
    async def deserialize(
        cls, serialized_store_state: MutableMapping[str, Any], **kwargs: Any
    ) -> "FoundryConversationMessageStore":
        conversation_id = serialized_store_state.get("conversation_id")
        client = kwargs.get("client")
        res = cls(conversation_id, client)
        await res.get_conversation_history()
        return res

    async def update_from_state(self, serialized_store_state: MutableMapping[str, Any], **kwargs: Any) -> None:
        return None
    
    async def serialize(self) -> MutableMapping[str, Any]:
        return {"conversation_id": self._conversation_id}
    
    async def get_conversation_history(self) -> None:
        # Retrieve conversation history from Foundry.
        try:
            with self._client.get_openai_client() as openai_client:
                messages = await openai_client.conversations.items.list(self._conversation_id)
                if messages:
                    logger.info(f"Retrieved {len(messages)} messages for conversation {self._conversation_id} from Foundry.")
                    self._conversation_messages = [ChatMessage(role=msg.role, content=msg.content) for msg in messages]
        except Exception as e:
            logger.error(f"Failed to get conversation history for {self._conversation_id}: {e}")
