# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional, Union

from agent_framework import AgentSession

from azure.ai.projects.aio import AIProjectClient
from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._foundry_conversation_history_provider import FoundryConversationHistoryProvider
from .agent_session_repository import AgentSessionRepository


class FoundryConversationSessionRepository(AgentSessionRepository):
    """A Foundry Conversation implementation of AgentSessionRepository."""

    def __init__(
        self,
        project_endpoint: str,
        credential: Union[TokenCredential, AsyncTokenCredential],
    ) -> None:
        if not project_endpoint or not credential:
            raise ValueError(
                "Both project_endpoint and credential are required for "
                "FoundryConversationSessionRepository."
            )
        self._client = AIProjectClient(project_endpoint, credential)
        self._history_provider = FoundryConversationHistoryProvider(project_client=self._client)
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
        history_provider = self._history_provider
        if conversation_id in self._inventory:
            session = self._inventory[conversation_id]
            provider_state = session.state.setdefault(history_provider.source_id, {})
            provider_state["conversation_id"] = conversation_id
            return session

        session = AgentSession(
            session_id=conversation_id,
            service_session_id=conversation_id,
        )
        provider_state = session.state.setdefault(history_provider.source_id, {})
        provider_state["conversation_id"] = conversation_id
        self._inventory[conversation_id] = session
        return session

    async def set(self, conversation_id: Optional[str], session: AgentSession) -> None:
        """Save the session for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]
        :param session: The session to save.
        :type session: AgentSession
        """
        if not conversation_id:
            raise ValueError("conversation_id is required to save an AgentSession.")

        provider_state = session.state.setdefault(FoundryConversationHistoryProvider.DEFAULT_SOURCE_ID, {})
        provider_state["conversation_id"] = conversation_id
        if not session.service_session_id:
            session.service_session_id = conversation_id
        self._inventory[conversation_id] = session

    @property
    def history_provider(self) -> FoundryConversationHistoryProvider:
        return self._history_provider
