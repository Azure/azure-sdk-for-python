# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import inspect
from collections.abc import MutableMapping, Sequence
from typing import Any, Optional, Union

from agent_framework import ChatMessage

from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    ItemContentInputText,
    ItemContentOutputText,
    ItemType,
    ResponsesMessageItemResource,
)

from azure.ai.agentserver.core.logger import get_logger

logger = get_logger()

def _convert_item_to_chat_message(item: ResponsesMessageItemResource) -> Optional[ChatMessage]:
    """Convert an ItemResource from the Conversations API to a ChatMessage.

    :param item: The item resource from the Conversations API.
    :type item: ResponsesMessageItemResource
    :return: The converted ChatMessage, or None if conversion is not possible.
    :rtype: Optional[ChatMessage]
    """
    if item.type != ItemType.MESSAGE:
        return None

    role = str(item.role).lower()
    content_parts: list[str] = []

    if hasattr(item, "content") and item.content:
        for content_item in item.content:
            if isinstance(content_item, ItemContentInputText):
                content_parts.append(content_item.text)
            elif isinstance(content_item, ItemContentOutputText):
                content_parts.append(content_item.text)

    if not content_parts:
        return None

    return ChatMessage(role=role, content="\n".join(content_parts))


class FoundryConversationMessageStore:
    """A ChatMessageStoreProtocol implementation that reads messages from Azure AI Foundry Conversations API.

    This message store fetches messages from the Foundry Conversations API and converts them
    to ChatMessage format. Messages added via add_messages() are cached locally but not
    persisted back to the API.

    :param conversation_id: The conversation ID to fetch messages from.
    :type conversation_id: str
    :param project_endpoint: The Azure AI Foundry project endpoint.
    :type project_endpoint: str
    :param credentials: The token credential for authentication.
    :type credentials: Union[TokenCredential, AsyncTokenCredential]
    """

    def __init__(
        self,
        conversation_id: str,
        project_client: AIProjectClient
    ) -> None:
        """Initialize the FoundryConversationMessageStore.

        :param conversation_id: The conversation ID to fetch messages from.
        :type conversation_id: str
        :param project_endpoint: The Azure AI Foundry project endpoint.
        :type project_endpoint: str
        :param credentials: The token credential for authentication.
        :type credentials: Union[TokenCredential, AsyncTokenCredential]
        :keyword _project_client_factory: Optional factory for creating project client (for testing).
        :paramtype _project_client_factory: Optional[Any]
        """
        self._conversation_id = conversation_id
        self._project_client = project_client
        self._retrieved_messages: list[ChatMessage] = []
        self._cached_messages: list[ChatMessage] = []


    async def list_messages(self) -> list[ChatMessage]:
        """Get all messages from the conversation, including cached messages.

        Fetches messages from the Foundry Conversations API, converts them to ChatMessage format,
        and combines them with any locally cached messages.

        :return: List of ChatMessage objects, ordered from oldest to newest.
        :rtype: list[ChatMessage]
        """
        return self._retrieved_messages + self._cached_messages

    async def add_messages(self, messages: Sequence[ChatMessage]) -> None:
        """Add messages to the local cache.

        Messages are cached locally but not persisted to the API.

        :param messages: The sequence of ChatMessage objects to add.
        :type messages: Sequence[ChatMessage]
        """
        self._cached_messages.extend(messages)

    @classmethod
    async def deserialize(
        cls,
        serialized_store_state: MutableMapping[str, Any],
        *,
        project_client: Optional[AIProjectClient] = None,
        **kwargs: Any,
    ) -> "FoundryConversationMessageStore":
        """Create a new FoundryConversationMessageStore instance from serialized state.

        :param serialized_store_state: The serialized state data.
        :type serialized_store_state: MutableMapping[str, Any]
        :param project_client: The AIProjectClient instance to use for API interactions.
        :type project_client: Optional[AIProjectClient]
        :return: A new FoundryConversationMessageStore instance.
        :rtype: FoundryConversationMessageStore
        :raises ValueError: If required parameters are missing.
        """

        conversation_id = serialized_store_state.get("conversation_id")
        if not conversation_id:
            raise ValueError("conversation_id is required in serialized state")
        
        store = cls(
            conversation_id=conversation_id,
            project_client=project_client
        )

        # Restore cached messages
        await store.update_from_state(serialized_store_state)

        return store

    async def update_from_state(
        self,
        serialized_store_state: MutableMapping[str, Any],
        **kwargs: Any,
    ) -> None:
        """Update the current store instance from serialized state data.

        :param serialized_store_state: The serialized state data.
        :type serialized_store_state: MutableMapping[str, Any]
        """
        if not serialized_store_state:
            return
        
        # Update cached messages
        cached_messages_data = serialized_store_state.get("messages", [])
        self._cached_messages = []
        for msg_data in cached_messages_data:
            if isinstance(msg_data, dict):
                self._cached_messages.append(ChatMessage.from_dict(msg_data))
            elif isinstance(msg_data, ChatMessage):
                self._cached_messages.append(msg_data)
        
        await self.get_conversation_history()

    async def get_conversation_history(self) -> None:
        # Retrieve conversation history from Foundry.
        if not self._project_client:
            logger.error("AIProjectClient is not configured; cannot load conversation history.")
            return

        try:
            async with self._project_client.get_openai_client() as openai_client:
                raw_items = await openai_client.conversations.items.list(self._conversation_id)
                logger.info(f"Fetched conversation items for conversation {self._conversation_id} from Foundry.")
                retrieved_messages: list[ChatMessage] = []

                if raw_items is None:
                    self._retrieved_messages = []
                    return

                iter_pages = getattr(raw_items, "iter_pages", None)
                if iter_pages is not None:
                    async for page in iter_pages():
                        items = getattr(page, "data", None) or []
                        for item in items:
                            logger.info(f"Processing item {type(item)}: {item}")
                            chat_message = _convert_item_to_chat_message(item)
                            if chat_message:
                                retrieved_messages.append(chat_message)

                self._retrieved_messages = retrieved_messages
                logger.info(
                    "Retrieved %s messages for conversation %s from Foundry.",
                    len(self._retrieved_messages),
                    self._conversation_id,
                )
        except Exception:
            logger.exception(
                "Failed to get conversation history for %s",
                self._conversation_id,
            )


    async def serialize(self, **kwargs: Any) -> dict[str, Any]:
        """Serialize the current store state.

        :return: The serialized state data containing conversation_id and cached messages.
        :rtype: dict[str, Any]
        """
        return {
            "conversation_id": self._conversation_id,
            "messages": [msg.to_dict() for msg in self._cached_messages],
        }