# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections.abc import Sequence
from typing import Any, Optional

from agent_framework import BaseHistoryProvider, Message

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.projects import AIProjectClient

from ..models.conversation_converters import to_chat_message
from ..models.human_in_the_loop_helper import HumanInTheLoopHelper

logger = get_logger()


class FoundryConversationMessageStore(BaseHistoryProvider):
    """History provider that reads Foundry conversation history and stores in session state."""

    DEFAULT_SOURCE_ID = "foundry_conversation"

    def __init__(
        self,
        project_client: AIProjectClient,
        source_id: Optional[str] = None,
    ) -> None:
        super().__init__(source_id=source_id or self.DEFAULT_SOURCE_ID)
        self._project_client = project_client
        self._hitl_helper = HumanInTheLoopHelper()

    async def get_messages(
        self,
        session_id: Optional[str],
        *,
        state: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> list[Message]:
        if state is None:
            return []

        conversation_id = self._resolve_conversation_id(session_id, state)
        if not conversation_id:
            return list(state.get("messages", []))

        if "retrieved_messages" not in state:
            history_messages = await self._get_conversation_history(conversation_id)
            state["retrieved_messages"] = self._hitl_helper.remove_hitl_content_from_session(history_messages or [])
        retrieved_messages = state.get("retrieved_messages", [])
        cached_messages = state.get("messages", [])
        return [*retrieved_messages, *cached_messages]

    async def save_messages(
        self,
        session_id: Optional[str],
        messages: Sequence[Message],
        *,
        state: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        if state is None:
            return

        conversation_id = self._resolve_conversation_id(session_id, state)
        if conversation_id:
            state["conversation_id"] = conversation_id
        existing_messages = state.get("messages", [])
        state["messages"] = [*existing_messages, *messages]

    @staticmethod
    def _resolve_conversation_id(session_id: Optional[str], state: dict[str, Any]) -> Optional[str]:
        conversation_id = state.get("conversation_id")
        if isinstance(conversation_id, str) and conversation_id:
            return conversation_id
        return session_id

    async def _get_conversation_history(self, conversation_id: str) -> list[Message]:
        if not self._project_client:
            logger.error("AIProjectClient is not configured; cannot load conversation history.")
            return []

        try:
            async with self._project_client.get_openai_client() as openai_client:
                raw_items = await openai_client.conversations.items.list(conversation_id)
                retrieved_messages: list[Message] = []

                if raw_items is None:
                    return []

                iter_pages = getattr(raw_items, "iter_pages", None)
                if iter_pages is not None:
                    async for page in iter_pages():
                        items = getattr(page, "data", None) or []
                        for item in items:
                            chat_message = to_chat_message(item)
                            if chat_message:
                                retrieved_messages.append(chat_message)
                logger.info(
                    "Retrieved %s messages for conversation %s from Foundry.",
                    len(retrieved_messages),
                    conversation_id,
                )
                return retrieved_messages[::-1]
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                "Failed to get conversation history for %s: %s",
                conversation_id,
                exc,
            )
            return []
