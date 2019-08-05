# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from typing import Iterable, Dict, Any
from abc import ABC, abstractmethod


class PartitionManager(ABC):
    """Subclass PartitionManager to implement the read/write access to storage service to list/claim ownership and save checkpoint.

    """

    @abstractmethod
    async def list_ownership(self, eventhub_name: str, consumer_group_name: str) -> Iterable[Dict[str, Any]]:
        """

        :param eventhub_name:
        :param consumer_group_name:
        :return: Iterable of dictionaries containing the following partition ownership information:
                eventhub_name
                consumer_group_name
                owner_id
                partition_id
                owner_level
                offset
                sequence_number
                last_modified_time
                etag
        """
        pass

    @abstractmethod
    async def claim_ownership(self, partitions: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update_checkpoint(self, eventhub_name, consumer_group_name, partition_id, owner_id,
                                offset, sequence_number) -> None:
        pass

    async def close(self):
        pass
