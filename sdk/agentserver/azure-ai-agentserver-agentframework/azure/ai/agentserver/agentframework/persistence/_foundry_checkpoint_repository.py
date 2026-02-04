# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Foundry-backed checkpoint repository implementation."""

import logging
from typing import Dict, Optional, Union

from agent_framework import CheckpointStorage
from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential

from azure.ai.agentserver.core.checkpoints.client import (
    CheckpointSession,
    FoundryCheckpointClient,
)

from .checkpoint_repository import CheckpointRepository
from ._foundry_checkpoint_storage import FoundryCheckpointStorage

logger = logging.getLogger(__name__)


class FoundryCheckpointRepository(CheckpointRepository):
    """Repository that creates FoundryCheckpointStorage instances per conversation.

    Manages checkpoint sessions on the Foundry backend, creating sessions on demand
    and caching storage instances for reuse within the same process.

    :param endpoint: The Foundry service endpoint URL.
    :type endpoint: str
    :param credential: Credential for authentication.
    :type credential: Union[AsyncTokenCredential, TokenCredential]
    :param project_id: The project identifier.
    :type project_id: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AsyncTokenCredential, TokenCredential],
        project_id: str,
    ) -> None:
        """Initialize the Foundry checkpoint repository.

        :param endpoint: The Foundry service endpoint URL.
        :type endpoint: str
        :param credential: Credential for authentication.
        :type credential: Union[AsyncTokenCredential, TokenCredential]
        :param project_id: The project identifier.
        :type project_id: str
        """
        # Convert sync credential to async if needed
        if not isinstance(credential, AsyncTokenCredential):
            from azure.identity import get_bearer_token_provider
            # For now, we require async credentials
            raise TypeError(
                "FoundryCheckpointRepository requires an AsyncTokenCredential. "
                "Please use an async credential like DefaultAzureCredential."
            )

        self._client = FoundryCheckpointClient(endpoint, credential, project_id)
        self._inventory: Dict[str, CheckpointStorage] = {}

    async def get_or_create(
        self, conversation_id: Optional[str]
    ) -> Optional[CheckpointStorage]:
        """Get or create a checkpoint storage for the given conversation.

        :param conversation_id: The conversation ID (maps to session_id on backend).
        :type conversation_id: Optional[str]
        :return: CheckpointStorage instance or None if no conversation_id.
        :rtype: Optional[CheckpointStorage]
        """
        if not conversation_id:
            return None

        if conversation_id not in self._inventory:
            # Ensure session exists on backend
            await self._ensure_session(conversation_id)
            self._inventory[conversation_id] = FoundryCheckpointStorage(
                client=self._client,
                session_id=conversation_id,
            )
            logger.debug(
                "Created FoundryCheckpointStorage for conversation %s",
                conversation_id,
            )

        return self._inventory[conversation_id]

    async def _ensure_session(self, session_id: str) -> None:
        """Ensure a session exists on the backend, creating if needed.

        :param session_id: The session identifier.
        :type session_id: str
        """
        session = CheckpointSession(
            project_id=self._client.project_id,
            session_id=session_id,
        )
        await self._client.upsert_session(session)
        logger.debug("Ensured session %s exists on Foundry", session_id)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.close()
