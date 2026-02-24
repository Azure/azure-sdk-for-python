# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections.abc import MutableMapping, Sequence
from typing import Any, List, Optional

from agent_framework import Message

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.projects import AIProjectClient

from ..models.conversation_converters import ConversationItemConverter
from ..models.human_in_the_loop_helper import HumanInTheLoopHelper

logger = get_logger()


class FoundryConversationMessageStore:
    """Message store that reads messages from Azure AI Foundry Conversations API.

    This message store fetches messages from the Foundry Conversations API and converts them
    to Agent Framework ``Message`` objects. Messages added via add_messages() are cached
    locally but not persisted back to the API.

    :param conversation_id: The conversation ID to fetch messages from.
    :type conversation_id: str
    :param project_client: The Azure AI Project client used to retrieve conversation history.
    :type project_client: AIProjectClient
    """

    def __init__(
        self,
        conversation_id: str,
        project_client: AIProjectClient,
    ) -> None:
        self._conversation_id = conversation_id
        self._project_client = project_client
        self._retrieved_messages: list[Message] = []
        self._cached_messages: list[Message] = []

    async def list_messages(self) -> list[Message]:
        """Get all messages from the conversation, including cached messages."""
        return self._retrieved_messages + self._cached_messages

    async def add_messages(self, messages: Sequence[Message]) -> None:
        """Add messages to the local cache."""
        self._cached_messages.extend(messages)

    @classmethod
    async def deserialize(  # pylint: disable=unused-argument
        cls,
        serialized_store_state: MutableMapping[str, Any],
        *,
        project_client: Optional[AIProjectClient] = None,
        **kwargs: Any,
    ) -> "FoundryConversationMessageStore":
        conversation_id = serialized_store_state.get("conversation_id")
        if not conversation_id:
            raise ValueError("conversation_id is required in serialized state")

        store = cls(
            conversation_id=conversation_id,
            project_client=project_client,
        )

        await store.update_from_state(serialized_store_state)
        return store

    async def update_from_state(  # pylint: disable=unused-argument
        self,
        serialized_store_state: MutableMapping[str, Any],
        **kwargs: Any,
    ) -> None:
        if not serialized_store_state:
            return

        cached_messages_data = serialized_store_state.get("messages", [])
        self._cached_messages = []
        for msg_data in cached_messages_data:
            if isinstance(msg_data, dict):
                self._cached_messages.append(Message.from_dict(msg_data))
            elif isinstance(msg_data, Message):
                self._cached_messages.append(msg_data)
        await self.retrieve_messages()

    async def serialize(self, **kwargs: Any) -> dict[str, Any]:  # pylint: disable=unused-argument
        return {
            "conversation_id": self._conversation_id,
            "messages": [msg.to_dict() for msg in self._cached_messages],
        }

    async def retrieve_messages(self) -> None:
        history_messages = await self._get_conversation_history()
        filtered_messages = HumanInTheLoopHelper().remove_hitl_content_from_thread(history_messages or [])
        self._retrieved_messages = filtered_messages

    async def _get_conversation_history(self) -> List[Message]:
        if not self._project_client:
            logger.error("AIProjectClient is not configured; cannot load conversation history.")
            return []

        try:
            converter = ConversationItemConverter()
            async with self._project_client.get_openai_client() as openai_client:
                raw_items = await openai_client.conversations.items.list(self._conversation_id)
                retrieved_messages: list[Message] = []

                if raw_items is None:
                    self._retrieved_messages = []
                    return []

                iter_pages = getattr(raw_items, "iter_pages", None)
                if iter_pages is not None:
                    async for page in iter_pages():
                        items = getattr(page, "data", None) or []
                        for item in items:
                            chat_message = converter.to_chat_message(item)
                            if chat_message:
                                retrieved_messages.append(chat_message)
                logger.info(
                    "Retrieved %s messages for conversation %s from Foundry.",
                    len(retrieved_messages),
                    self._conversation_id,
                )
                return retrieved_messages[::-1]
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                "Failed to get conversation history for %s: %s",
                self._conversation_id,
                exc,
            )
            return []
