# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
from .checkpoint_store import CheckpointStore
from ..._utils import get_last_enqueued_event_properties

_LOGGER = logging.getLogger(__name__)


class PartitionContext(object):
    """Contains partition related context information for a PartitionProcessor instance to use.

    Users can use update_checkpoint() of this class to save checkpoint data.
    """
    def __init__(self, fully_qualified_namespace: str, eventhub_name: str, consumer_group: str,
                 partition_id: str, checkpoint_store: CheckpointStore = None):
        self.fully_qualified_namespace = fully_qualified_namespace
        self.partition_id = partition_id
        self.eventhub_name = eventhub_name
        self.consumer_group = consumer_group
        self._last_received_event = None
        self._checkpoint_store = checkpoint_store

    @property
    def last_enqueued_event_properties(self):
        """
        The latest enqueued event information. This property will be updated each time an event is received when
        the receiver is created with `track_last_enqueued_event_properties` being `True`.
        The dict includes following information of the partition:

            - `sequence_number`
            - `offset`
            - `enqueued_time`
            - `retrieval_time`

        :rtype: dict or None
        """
        if self._last_received_event:
            return get_last_enqueued_event_properties(self._last_received_event)
        return None

    async def update_checkpoint(self, event):
        """
        Updates the checkpoint using the given information for the associated partition and consumer group in the
        chosen storage service.

        :param ~azure.eventhub.EventData event: The EventData instance which contains the offset and
         sequence number information used for checkpoint.
        :rtype: None
        """
        if self._checkpoint_store:
            checkpoint = {
                'fully_qualified_namespace': self.fully_qualified_namespace,
                'eventhub_name': self.eventhub_name,
                'consumer_group': self.consumer_group,
                'partition_id': self.partition_id,
                'offset': event.offset,
                'sequence_number': event.sequence_number
            }
            await self._checkpoint_store.update_checkpoint(checkpoint)
        else:
            _LOGGER.warning(
                "namespace %r, eventhub %r, consumer_group %r, partition_id %r "
                "update_checkpoint is called without checkpoint store. No checkpoint is updated.",
                self.fully_qualified_namespace, self.eventhub_name, self.consumer_group, self.partition_id)
