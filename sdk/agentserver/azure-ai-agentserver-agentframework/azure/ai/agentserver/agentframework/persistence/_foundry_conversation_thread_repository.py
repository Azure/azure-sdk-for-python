# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Union

from agent_framework import AgentThread, AgentProtocol, WorkflowAgent
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.credentials import TokenCredential
from azure.ai.projects.aio import AIProjectClient

from azure.ai.agentserver.core.logger import get_logger

from .agent_thread_repository import AgentThreadRepository
from ._foundry_conversation_message_store import FoundryConversationMessageStore

logger = get_logger()

class FoundryConversationThreadRepository(AgentThreadRepository):
    """A Foundry Conversation implementation of AgentThreadRepository."""
    def __init__(self,
                 agent: Optional[Union[AgentProtocol, WorkflowAgent]],
                 project_endpoint: str,
                 credential: Union[TokenCredential, AsyncTokenCredential]) -> None:
        self._agent = agent
        if not project_endpoint or not credential:
            raise ValueError(
                "Both project_endpoint and credential are required for "
                "FoundryConversationThreadRepository."
            )
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
        await message_store.retrieve_messages()
        self._inventory[conversation_id] = FoundryConversationThread(message_store=message_store)
        return self._inventory[conversation_id]

    async def set(self,
            conversation_id: Optional[str],
            thread: AgentThread) -> None:
        """Save the thread for a given conversation ID.

        :param conversation_id: The conversation ID.
        :type conversation_id: Optional[str]
        :param thread: The thread to save.
        :type thread: AgentThread
        """
        if not conversation_id:
            raise ValueError("conversation_id is required to save an AgentThread.")
        self._inventory[conversation_id] = thread


class FoundryConversationThread(AgentThread):
    @property
    def service_thread_id(self) -> str | None:
        return self._service_thread_id

    @service_thread_id.setter
    def service_thread_id(self, service_thread_id: str | None) -> None:
        if service_thread_id is None:
            return
        self._service_thread_id = service_thread_id
