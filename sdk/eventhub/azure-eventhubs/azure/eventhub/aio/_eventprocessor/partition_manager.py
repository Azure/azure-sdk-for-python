# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from typing import Iterable, Dict, Any
from abc import ABC, abstractmethod


class PartitionManager(ABC):
    """
    PartitionManager deals with the interaction with the chosen storage service.
    It's able to list/claim ownership and save checkpoint.
    """

    @abstractmethod
    async def list_ownership(self, fully_qualified_namespace: str, eventhub_name: str, consumer_group: str) \
            -> Iterable[Dict[str, Any]]:
        """
        Retrieves a complete ownership list from the chosen storage service.

        :param str fully_qualified_namespace: The fully qualified namespace that the event hub belongs to.
         The format is like "<namespace>.servicebus.windows.net"
        :param str eventhub_name: The name of the specific Event Hub the ownership are associated with, relative to
         the Event Hubs namespace that contains it.
        :param str consumer_group: The name of the consumer group the ownership are associated with.
        :rtype: Iterable[Dict[str, Any]], Iterable of dictionaries containing partition ownership information:

                - fully_qualified_namespace
                - eventhub_name
                - consumer_group
                - owner_id
                - partition_id
                - last_modified_time
                - etag
        """

    @abstractmethod
    async def claim_ownership(self, ownership_list: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
        """
        Tries to claim a list of specified ownership.

        :param Iterable[Dict[str,Any]] ownership_list: Iterable of dictionaries containing all the ownership to claim.
        :rtype: Iterable[Dict[str,Any]], Iterable of dictionaries containing partition ownership information:

                - fully_qualified_namespace
                - eventhub_name
                - consumer_group
                - owner_id
                - partition_id
                - last_modified_time
                - etag
        """

    @abstractmethod
    async def update_checkpoint(self, fully_qualified_namespace: str, eventhub_name: str, consumer_group: str,
                                partition_id: str, offset: str, sequence_number: int) -> None:
        """
        Updates the checkpoint using the given information for the associated partition and
        consumer group in the chosen storage service.

        :param str fully_qualified_namespace: The fully qualified namespace that the event hub belongs to.
         The format is like "<namespace>.servicebus.windows.net"
        :param str eventhub_name: The name of the specific Event Hub the ownership are associated with, relative to
         the Event Hubs namespace that contains it.
        :param str consumer_group: The name of the consumer group the ownership are associated with.
        :param str partition_id: The partition id which the checkpoint is created for.
        :param str offset: The offset of the :class:`EventData<azure.eventhub.EventData>`
         the new checkpoint will be associated with.
        :param int sequence_number: The sequence_number of the :class:`EventData<azure.eventhub.EventData>`
         the new checkpoint will be associated with.
        :rtype: None
        """

    @abstractmethod
    async def list_checkpoints(self, fully_qualified_namespace: str, eventhub_name: str, consumer_group: str):
        """List the updated checkpoints from the store

        :param str fully_qualified_namespace: The fully qualified namespace that the event hub belongs to.
         The format is like "<namespace>.servicebus.windows.net"
        :param str eventhub_name: The name of the specific Event Hub the ownership are associated with, relative to
         the Event Hubs namespace that contains it.
        :param str consumer_group: The name of the consumer group the ownership are associated with.
        :rtype: Iterable[Dict[str,Any]], Iterable of dictionaries containing partition ownership information:

                - fully_qualified_namespace
                - eventhub_name
                - consumer_group
                - partition_id
                - sequence_number
                - offset
        """
