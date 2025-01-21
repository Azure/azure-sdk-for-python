# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------
from typing import Dict, Any, Iterable, Optional, Union
from azure.eventhub._eventprocessor.in_memory_checkpoint_store import (
    InMemoryCheckpointStore as CheckPointStoreImpl,
)
from .checkpoint_store import CheckpointStore


class InMemoryCheckpointStore(CheckpointStore):
    def __init__(self):
        self._checkpoint_store_impl = CheckPointStoreImpl()

    async def list_ownership(
        self, fully_qualified_namespace: str, eventhub_name: str, consumer_group: str, **kwargs: Any
    ) -> Iterable[Dict[str, Any]]:
        return self._checkpoint_store_impl.list_ownership(fully_qualified_namespace, eventhub_name, consumer_group)

    async def claim_ownership(
        self, ownership_list: Iterable[Dict[str, Any]], **kwargs: Any
    ) -> Iterable[Dict[str, Any]]:
        return self._checkpoint_store_impl.claim_ownership(ownership_list)

    async def update_checkpoint(self, checkpoint: Dict[str, Optional[Union[str, int]]], **kwargs: Any) -> None:
        self._checkpoint_store_impl.update_checkpoint(checkpoint)

    async def list_checkpoints(
        self, fully_qualified_namespace: str, eventhub_name: str, consumer_group: str, **kwargs: Any
    ) -> Iterable[Dict[str, Any]]:
        return self._checkpoint_store_impl.list_checkpoints(fully_qualified_namespace, eventhub_name, consumer_group)
