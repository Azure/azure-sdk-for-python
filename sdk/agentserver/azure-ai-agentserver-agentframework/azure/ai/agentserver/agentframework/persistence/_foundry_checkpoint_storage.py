# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Foundry-backed checkpoint storage implementation."""

import json
import logging
from typing import List, Optional

from agent_framework import WorkflowCheckpoint

from azure.ai.agentserver.core.checkpoints.client import (
    CheckpointItem,
    CheckpointItemId,
    FoundryCheckpointClient,
)

logger = logging.getLogger(__name__)


class FoundryCheckpointStorage:
    """CheckpointStorage implementation backed by Azure AI Foundry.

    Implements the agent_framework.CheckpointStorage protocol by delegating
    to the FoundryCheckpointClient HTTP client for remote storage.

    :param client: The Foundry checkpoint client.
    :type client: FoundryCheckpointClient
    :param session_id: The session identifier (maps to conversation_id).
    :type session_id: str
    """

    def __init__(self, client: FoundryCheckpointClient, session_id: str) -> None:
        """Initialize the Foundry checkpoint storage.

        :param client: The Foundry checkpoint client.
        :type client: FoundryCheckpointClient
        :param session_id: The session identifier.
        :type session_id: str
        """
        self._client = client
        self._session_id = session_id

    async def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> str:
        """Save a checkpoint and return its ID.

        :param checkpoint: The workflow checkpoint to save.
        :type checkpoint: WorkflowCheckpoint
        :return: The checkpoint ID.
        :rtype: str
        """
        serialized = self._serialize_checkpoint(checkpoint)
        item = CheckpointItem(
            session_id=self._session_id,
            item_id=checkpoint.checkpoint_id,
            data=serialized,
            parent_id=None,
        )
        result = await self._client.create_items([item])
        if result:
            logger.debug(
                "Saved checkpoint %s to Foundry session %s",
                checkpoint.checkpoint_id,
                self._session_id,
            )
            return result[0].item_id
        return checkpoint.checkpoint_id

    async def load_checkpoint(self, checkpoint_id: str) -> Optional[WorkflowCheckpoint]:
        """Load a checkpoint by ID.

        :param checkpoint_id: The checkpoint identifier.
        :type checkpoint_id: str
        :return: The workflow checkpoint if found, None otherwise.
        :rtype: Optional[WorkflowCheckpoint]
        """
        item_id = CheckpointItemId(
            session_id=self._session_id,
            item_id=checkpoint_id,
        )
        item = await self._client.read_item(item_id)
        if item is None:
            return None
        checkpoint = self._deserialize_checkpoint(item.data)
        logger.debug(
            "Loaded checkpoint %s from Foundry session %s",
            checkpoint_id,
            self._session_id,
        )
        return checkpoint

    async def list_checkpoint_ids(
        self, workflow_id: Optional[str] = None
    ) -> List[str]:
        """List checkpoint IDs.

        If workflow_id is provided, filter by that workflow.

        :param workflow_id: Optional workflow identifier for filtering.
        :type workflow_id: Optional[str]
        :return: List of checkpoint identifiers.
        :rtype: List[str]
        """
        item_ids = await self._client.list_item_ids(self._session_id)
        ids = [item_id.item_id for item_id in item_ids]

        # Filter by workflow_id if provided
        if workflow_id is not None:
            filtered_ids = []
            for checkpoint_id in ids:
                checkpoint = await self.load_checkpoint(checkpoint_id)
                if checkpoint and checkpoint.workflow_id == workflow_id:
                    filtered_ids.append(checkpoint_id)
            return filtered_ids

        return ids

    async def list_checkpoints(
        self, workflow_id: Optional[str] = None
    ) -> List[WorkflowCheckpoint]:
        """List checkpoint objects.

        If workflow_id is provided, filter by that workflow.

        :param workflow_id: Optional workflow identifier for filtering.
        :type workflow_id: Optional[str]
        :return: List of workflow checkpoints.
        :rtype: List[WorkflowCheckpoint]
        """
        ids = await self.list_checkpoint_ids(workflow_id=None)
        checkpoints: List[WorkflowCheckpoint] = []

        for checkpoint_id in ids:
            checkpoint = await self.load_checkpoint(checkpoint_id)
            if checkpoint is not None:
                if workflow_id is None or checkpoint.workflow_id == workflow_id:
                    checkpoints.append(checkpoint)

        return checkpoints

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint by ID.

        :param checkpoint_id: The checkpoint identifier.
        :type checkpoint_id: str
        :return: True if the checkpoint was deleted, False otherwise.
        :rtype: bool
        """
        item_id = CheckpointItemId(
            session_id=self._session_id,
            item_id=checkpoint_id,
        )
        deleted = await self._client.delete_item(item_id)
        if deleted:
            logger.debug(
                "Deleted checkpoint %s from Foundry session %s",
                checkpoint_id,
                self._session_id,
            )
        return deleted

    def _serialize_checkpoint(self, checkpoint: WorkflowCheckpoint) -> bytes:
        """Serialize a WorkflowCheckpoint to bytes.

        :param checkpoint: The workflow checkpoint.
        :type checkpoint: WorkflowCheckpoint
        :return: Serialized checkpoint data.
        :rtype: bytes
        """
        checkpoint_dict = checkpoint.to_dict()
        return json.dumps(checkpoint_dict, ensure_ascii=False).encode("utf-8")

    def _deserialize_checkpoint(self, data: bytes) -> WorkflowCheckpoint:
        """Deserialize bytes to WorkflowCheckpoint.

        :param data: Serialized checkpoint data.
        :type data: bytes
        :return: The workflow checkpoint.
        :rtype: WorkflowCheckpoint
        """
        checkpoint_dict = json.loads(data.decode("utf-8"))
        return WorkflowCheckpoint.from_dict(checkpoint_dict)
