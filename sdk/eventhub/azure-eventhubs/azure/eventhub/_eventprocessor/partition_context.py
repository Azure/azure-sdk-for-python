# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
from .partition_manager import PartitionManager

_LOGGER = logging.getLogger(__name__)


class PartitionContext(object):
    """Contains partition related context information for a PartitionProcessor instance to use.

    Users can use update_checkpoint() of this class to save checkpoint data.
    """
    def __init__(self, fully_qualified_namespace, eventhub_name, consumer_group_name,
                 partition_id, owner_id, partition_manager=None):
        # type: (str, str, str, str, str, PartitionManager) -> None
        self.fully_qualified_namespace = fully_qualified_namespace
        self.partition_id = partition_id
        self.eventhub_name = eventhub_name
        self.consumer_group_name = consumer_group_name
        self.owner_id = owner_id
        self._partition_manager = partition_manager

    def update_checkpoint(self, event):
        """
        Updates the checkpoint using the given information for the associated partition and consumer group in the
        chosen storage service.

        :param ~azure.eventhub.EventData event: The EventData instance which contains the offset and
         sequence number information used for checkpoint.
        :rtype: None
        """
        if self._partition_manager:
            self._partition_manager.update_checkpoint(
                self.fully_qualified_namespace, self.eventhub_name, self.consumer_group_name,
                self.partition_id, event.offset, event.sequence_number
            )
        else:
            _LOGGER.info(
                "namespace %r, eventhub %r, consumer_group %r, partition_id %r "
                "update_checkpoint is called without partition manager. No checkpoint is updated.",
                self.fully_qualified_namespace, self.eventhub_name, self.consumer_group_name, self.partition_id)
