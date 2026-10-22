# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
import logging
from typing import Dict, Optional, Any, TYPE_CHECKING

from .._utils import get_last_enqueued_event_properties
from .checkpoint_store import CheckpointStore

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .._common import EventData


class PartitionContext:
    """Contains partition related context information.

    A `PartitionContext` instance will be passed to the event, error and initialization callbacks defined
    when calling `EventHubConsumerClient.receive()`.
    Users can call `update_checkpoint()` of this class to persist checkpoint data.
    """

    def __init__(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        consumer_group: str,
        partition_id: str,
        checkpoint_store: Optional[CheckpointStore] = None,
    ) -> None:
        self.fully_qualified_namespace = fully_qualified_namespace
        self.partition_id = partition_id
        self.eventhub_name = eventhub_name
        self.consumer_group = consumer_group
        self._checkpoint_store = checkpoint_store
        self._last_received_event: Optional[EventData] = None

    @property
    def last_enqueued_event_properties(self) -> Optional[Dict[str, Any]]:
        """The latest enqueued event information.

        This property will be updated each time an event is received if the receiver is created
        with `track_last_enqueued_event_properties` set to `True`.
        The properties dict includes following information of the last enqueued event:

            - `sequence_number` (int)
            - `offset` (str)
            - `enqueued_time` (UTC datetime.datetime)
            - `retrieval_time` (UTC datetime.datetime)

        :rtype: Dict[str, Any] or None
        """
        if self._last_received_event:
            return get_last_enqueued_event_properties(self._last_received_event)
        return None

    def update_checkpoint(self, event: Optional[EventData] = None, **kwargs: Any) -> None:
        """Updates the receive checkpoint to the given events offset.

        :param ~azure.eventhub.EventData event: The EventData instance which contains the offset and
         sequence number information used for checkpoint.
        :rtype: None
        """
        if self._checkpoint_store:
            checkpoint_event = event or self._last_received_event
            if checkpoint_event:
                checkpoint = {
                    "fully_qualified_namespace": self.fully_qualified_namespace,
                    "eventhub_name": self.eventhub_name,
                    "consumer_group": self.consumer_group,
                    "partition_id": self.partition_id,
                    "offset": checkpoint_event.offset,
                    "sequence_number": checkpoint_event.sequence_number,
                }
                try:
                    self._checkpoint_store.update_checkpoint(checkpoint, **kwargs)
                except TypeError as e:
                    if "update_checkpoint() got an unexpected keyword argument" in str(e):
                        _LOGGER.info(
                            "The provided checkpointstore method 'update_checkpoint' does not accept keyword arguments,"
                            " so keyword arguments will be ignored. Please update method signature to support kwargs."
                        )
                        self._checkpoint_store.update_checkpoint(checkpoint)
                    else:
                        raise e
        else:
            _LOGGER.warning(
                "namespace %r, eventhub %r, consumer_group %r, partition_id %r "
                "update_checkpoint is called without checkpoint store. No checkpoint is updated.",
                self.fully_qualified_namespace,
                self.eventhub_name,
                self.consumer_group,
                self.partition_id,
            )
