# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Iterable, Dict, Any, Union, Optional
from abc import abstractmethod


class CheckpointStore:
    """CheckpointStore deals with the interaction with the chosen storage service.

    It can list and claim partition ownerships as well as list and save checkpoints.
    """

    @abstractmethod
    def list_ownership(
        self, fully_qualified_namespace: str, eventhub_name: str, consumer_group: str, **kwargs: Any
    ) -> Iterable[Dict[str, Any]]:
        """Retrieves a complete ownership list from the chosen storage service.

        :param str fully_qualified_namespace: The fully qualified namespace that the Event Hub belongs to.
         The format is like "<namespace>.servicebus.windows.net".
        :param str eventhub_name: The name of the specific Event Hub the partition ownerships are associated with,
         relative to the Event Hubs namespace that contains it.
        :param str consumer_group: The name of the consumer group the ownerships are associated with.
        :rtype: Iterable[Dict[str, Any]], Iterable of dictionaries containing partition ownership information:

                - `fully_qualified_namespace` (str): The fully qualified namespace that the Event Hub belongs to.
                  The format is like "<namespace>.servicebus.windows.net".
                - `eventhub_name` (str): The name of the specific Event Hub the checkpoint is associated with,
                  relative to the Event Hubs namespace that contains it.
                - `consumer_group` (str): The name of the consumer group the ownership are associated with.
                - `partition_id` (str): The partition ID which the checkpoint is created for.
                - `owner_id` (str): A UUID representing the current owner of this partition.
                - `last_modified_time` (UTC datetime.datetime): The last time this ownership was claimed.
                - `etag` (str): The Etag value for the last time this ownership was modified. Optional depending
                  on storage implementation.
        """

    @abstractmethod
    def claim_ownership(self, ownership_list: Iterable[Dict[str, Any]], **kwargs: Any) -> Iterable[Dict[str, Any]]:
        """Tries to claim ownership for a list of specified partitions.

        :param Iterable[Dict[str,Any]] ownership_list: Iterable of dictionaries containing all the ownerships to claim.
        :rtype: Iterable[Dict[str,Any]], Iterable of dictionaries containing partition ownership information:

                - `fully_qualified_namespace` (str): The fully qualified namespace that the Event Hub belongs to.
                  The format is like "<namespace>.servicebus.windows.net".
                - `eventhub_name` (str): The name of the specific Event Hub the checkpoint is associated with,
                  relative to the Event Hubs namespace that contains it.
                - `consumer_group` (str): The name of the consumer group the ownership are associated with.
                - `partition_id` (str): The partition ID which the checkpoint is created for.
                - `owner_id` (str): A UUID representing the owner attempting to claim this partition.
                - `last_modified_time` (UTC datetime.datetime): The last time this ownership was claimed.
                - `etag` (str): The Etag value for the last time this ownership was modified. Optional depending
                  on storage implementation.
        """

    @abstractmethod
    def update_checkpoint(self, checkpoint: Dict[str, Optional[Union[str, int]]], **kwargs: Any) -> None:
        """Updates the checkpoint using the given information for the offset, associated partition and
        consumer group in the chosen storage service.

        Note: If you plan to implement a custom checkpoint store with the intention of running between
        cross-language EventHubs SDKs, it is recommended to persist the offset value as an integer.

        :param Dict[str,Any] checkpoint: A dict containing checkpoint information:

                - `fully_qualified_namespace` (str): The fully qualified namespace that the Event Hub belongs to.
                  The format is like "<namespace>.servicebus.windows.net".
                - `eventhub_name` (str): The name of the specific Event Hub the checkpoint is associated with,
                  relative to the Event Hubs namespace that contains it.
                - `consumer_group` (str): The name of the consumer group the checkpoint is associated with.
                - `partition_id` (str): The partition ID which the checkpoint is created for.
                - `sequence_number` (int): The sequence number of the :class:`EventData<azure.eventhub.EventData>`
                  the new checkpoint will be associated with.
                - `offset` (str): The offset of the :class:`EventData<azure.eventhub.EventData>`
                  the new checkpoint will be associated with.

        :rtype: None
        """

    @abstractmethod
    def list_checkpoints(
        self, fully_qualified_namespace: str, eventhub_name: str, consumer_group: str, **kwargs: Any
    ) -> Iterable[Dict[str, Any]]:
        """List the updated checkpoints from the chosen storage service.

        :param str fully_qualified_namespace: The fully qualified namespace that the Event Hub belongs to.
         The format is like "<namespace>.servicebus.windows.net".
        :param str eventhub_name: The name of the specific Event Hub the checkpoints are associated with, relative to
         the Event Hubs namespace that contains it.
        :param str consumer_group: The name of the consumer group the checkpoints are associated with.
        :rtype: Iterable[Dict[str,Any]], Iterable of dictionaries containing partition checkpoint information:

                - `fully_qualified_namespace` (str): The fully qualified namespace that the Event Hub belongs to.
                  The format is like "<namespace>.servicebus.windows.net".
                - `eventhub_name` (str): The name of the specific Event Hub the checkpoints are associated with,
                  relative to the Event Hubs namespace that contains it.
                - `consumer_group` (str): The name of the consumer group the checkpoints are associated with.
                - `partition_id` (str): The partition ID which the checkpoint is created for.
                - `sequence_number` (int): The sequence number of the :class:`EventData<azure.eventhub.EventData>`.
                - `offset` (str): The offset of the :class:`EventData<azure.eventhub.EventData>`.
        """
