# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from typing import Iterable, Dict, Any
from abc import ABC, abstractmethod


class PartitionManager(ABC):
    """
    PartitionManager deals with the interaction with the chosen storage service.
    It's able to list/claim ownership and create checkpoint.
    """

    @abstractmethod
    async def list_ownership(self, eventhub_name: str, consumer_group_name: str) -> Iterable[Dict[str, Any]]:
        """
        Retrieves a complete ownership list from the chosen storage service.

        :param eventhub_name: The name of the specific Event Hub the ownership are associated with, relative to
         the Event Hubs namespace that contains it.
        :type eventhub_name: str
        :param consumer_group_name: The name of the consumer group the ownership are associated with.
        :type consumer_group_name: str
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
        """
        Tries to claim a list of specified ownership.

        :param partitions: Iterable of dictionaries containing all the ownership to claim.
        :type partitions: Iterable of dict
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
    async def update_checkpoint(self, eventhub_name, consumer_group_name, partition_id, owner_id,
                                offset, sequence_number) -> None:
        """
        Updates the checkpoint using the given information for the associated partition and consumer group in the chosen storage service.

        :param eventhub_name: The name of the specific Event Hub the ownership are associated with, relative to
         the Event Hubs namespace that contains it.
        :type eventhub_name: str
        :param consumer_group_name: The name of the consumer group the ownership are associated with.
        :type consumer_group_name: str
        :param partition_id: The partition id which the checkpoint is created for.
        :type partition_id: str
        :param owner_id: The identifier of the ~azure.eventhub.eventprocessor.EventProcessor.
        :type owner_id: str
        :param offset: The offset of the ~azure.eventhub.EventData the new checkpoint will be associated with.
        :type offset: str
        :param sequence_number: The sequence_number of the ~azure.eventhub.EventData the new checkpoint will be associated with.
        :type sequence_number: int
        :return:
        """
        pass

    async def close(self):
        pass
