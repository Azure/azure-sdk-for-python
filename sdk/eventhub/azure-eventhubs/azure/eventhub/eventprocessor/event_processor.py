# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from typing import Callable, Dict
import uuid
import asyncio
import logging

from azure.eventhub import EventPosition, EventHubError
from azure.eventhub.aio import EventHubClient
from .checkpoint_manager import CheckpointManager
from .partition_manager import PartitionManager
from ._ownership_manager import OwnershipManager
from .partition_processor import CloseReason, PartitionProcessor

log = logging.getLogger(__name__)

OWNER_LEVEL = 0


class EventProcessor(object):
    """
    An EventProcessor constantly receives events from all partitions of the Event Hub in the context of a given
    consumer group. The received data will be sent to PartitionProcessor to be processed.

    It provides the user a convenient way to receive events from multiple partitions and save checkpoints.
    If multiple EventProcessors are running for an event hub, they will automatically balance load.

    Example:
        .. code-block:: python

            import asyncio
            from azure.eventhub.aio import EventHubClient
            from azure.eventhub.eventprocessor import EventProcessor, PartitionProcessor, Sqlite3PartitionManager

            class MyPartitionProcessor(object):
                async def process_events(self, events, checkpoint_manager):
                    if events:
                        # do something sync or async to process the events
                        await checkpoint_manager.update_checkpoint(events[-1].offset, events[-1].sequence_number)


            client = EventHubClient.from_connection_string("<your connection string>", receive_timeout=5, retry_total=3)
            partition_manager = Sqlite3PartitionManager()
            try:
                event_processor = EventProcessor(client, "$default", MyPartitionProcessor, partition_manager)
                asyncio.ensure_future(event_processor.start())
                await asyncio.sleep(100)  # allow it to run 100 seconds
                await event_processor.stop()
            finally:
                await partition_manager.close()

    """
    def __init__(self, eventhub_client: EventHubClient, consumer_group_name: str,
                 partition_processor_factory: Callable[..., PartitionProcessor],
                 partition_manager: PartitionManager, **kwargs):
        """
        Instantiate an EventProcessor.

        :param eventhub_client: An instance of ~azure.eventhub.aio.EventClient object
        :type eventhub_client: ~azure.eventhub.aio.EventClient
        :param consumer_group_name: The name of the consumer group this event processor is associated with. Events will
         be read only in the context of this group.
        :type consumer_group_name: str
        :param partition_processor_factory: A callable(type or function) object that creates an instance of a class
         implementing the ~azure.eventhub.eventprocessor.PartitionProcessor.
        :type partition_processor_factory: callable object
        :param partition_manager: Interacts with the storage system, dealing with ownership and checkpoints.
         For preview 2, sample Sqlite3PartitionManager is provided.
        :type partition_manager: Class implementing the ~azure.eventhub.eventprocessor.PartitionManager.
        :param initial_event_position: The offset to start a partition consumer if the partition has no checkpoint yet.
        :type initial_event_position: int or str
        :param polling_interval: The interval between any two pollings of balancing and claiming
        :type float

        """

        self._consumer_group_name = consumer_group_name
        self._eventhub_client = eventhub_client
        self._eventhub_name = eventhub_client.eh_name
        self._partition_processor_factory = partition_processor_factory
        self._partition_manager = partition_manager
        self._initial_event_position = kwargs.get("initial_event_position", "-1")
        # TODO: initial position provider will be a callable
        #  so users can create initial event position for every partition
        self._max_batch_size = eventhub_client.config.max_batch_size
        self._receive_timeout = eventhub_client.config.receive_timeout
        self._polling_interval = kwargs.get("polling_interval", 10)
        self._ownership_timeout = self._polling_interval * 2  # TODO: Team haven't decided if this is a separate argument
        self._tasks = {}  # type: Dict[str, asyncio.Task]
        self._id = str(uuid.uuid4())
        self._running = False

    def __repr__(self):
        return 'EventProcessor: id {}'.format(self._id)

    async def start(self):
        """Start the EventProcessor.

        1. Calls the OwnershipManager to keep claiming and balancing ownership of partitions in an
        infinitely loop until self.stop() is called.
        2. Cancels tasks for partitions that are no longer owned by this EventProcessor
        3. Creates tasks for partitions that are newly claimed by this EventProcessor
        4. Keeps tasks running for partitions that haven't changed ownership
        5. Each task repeatedly calls EvenHubConsumer.receive() to retrieve events and call user defined partition processor

        :return: None

        """
        log.info("EventProcessor %r is being started", self._id)
        ownership_manager = OwnershipManager(self, self._eventhub_client, self._ownership_timeout)
        if not self._running:
            self._running = True
            while self._running:
                claimed_ownership_list = await ownership_manager.claim_ownership()
                if claimed_ownership_list:
                    claimed_partition_ids = [x["partition_id"] for x in claimed_ownership_list]
                    to_cancel_list = self._tasks.keys() - claimed_partition_ids
                    self._create_tasks_for_claimed_ownership(claimed_ownership_list)
                else:
                    log.warning("EventProcessor %r hasn't claimed an ownership. It keeps claiming.", self._id)
                    to_cancel_list = self._tasks.keys()
                if to_cancel_list:
                    self._cancel_tasks_for_partitions(to_cancel_list)
                    log.info("EventProcesor %r has cancelled partitions %r", self._id, to_cancel_list)
                await asyncio.sleep(self._polling_interval)

    async def stop(self):
        """Stop claiming ownership and all the partition consumers owned by this EventProcessor

        This method stops claiming ownership of owned partitions and cancels tasks that are running
        EventHubConsumer.receive() for the partitions owned by this EventProcessor.

        :return: None

        """
        self._running = False
        for _ in range(len(self._tasks)):
            _, task = self._tasks.popitem()
            task.cancel()
        log.info("EventProcessor %r has been cancelled", self._id)
        await asyncio.sleep(2)  # give some time to finish after cancelled

    def _cancel_tasks_for_partitions(self, to_cancel_partitions):
        for partition_id in to_cancel_partitions:
            if partition_id in self._tasks:
                task = self._tasks.pop(partition_id)
                task.cancel()

    def _create_tasks_for_claimed_ownership(self, to_claim_ownership_list):
        for ownership in to_claim_ownership_list:
            partition_id = ownership["partition_id"]
            if partition_id not in self._tasks:
                self._tasks[partition_id] = asyncio.create_task(self._receive(ownership))

    async def _receive(self, ownership):
        log.info("start ownership, %r", ownership)
        partition_processor = self._partition_processor_factory()
        if not hasattr(partition_processor, "process_events"):
            log.error(
                "Fatal error: a partition processor should at least have method process_events(events, checkpoint_manager). EventProcessor will stop.")
            await self.stop()
            raise TypeError("Partition processor must has method process_events(events, checkpoint_manager")

        partition_consumer = self._eventhub_client.create_consumer(ownership["consumer_group_name"],
                                                                   ownership["partition_id"],
                                                                   EventPosition(ownership.get("offset", self._initial_event_position))
                                                                   )
        checkpoint_manager = CheckpointManager(ownership["partition_id"],
                                               ownership["eventhub_name"],
                                               ownership["consumer_group_name"],
                                               ownership["owner_id"],
                                               self._partition_manager)
        async def initialize():
            if hasattr(partition_processor, "initialize"):
                await partition_processor.initialize(checkpoint_manager)

        async def process_error(err):
            if hasattr(partition_processor, "process_error"):
                await partition_processor.process_error(err, checkpoint_manager)

        async def close(close_reason):
            if hasattr(partition_processor, "close"):
                await partition_processor.close(close_reason, checkpoint_manager)

        try:
            while True:
                try:
                    await initialize()
                    events = await partition_consumer.receive(timeout=self._receive_timeout)
                    await partition_processor.process_events(events, checkpoint_manager)
                except asyncio.CancelledError as cancelled_error:
                    log.info(
                        "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r "
                        "is cancelled",
                        ownership["owner_id"],
                        ownership["eventhub_name"],
                        ownership["partition_id"],
                        ownership["consumer_group_name"]
                    )
                    await process_error(cancelled_error)
                    await close(CloseReason.SHUTDOWN)
                    # TODO: release the ownership immediately via partition manager
                    break
                except EventHubError as eh_err:
                    reason = CloseReason.OWNERSHIP_LOST if eh_err.error == "link:stolen" else CloseReason.EVENTHUB_EXCEPTION
                    log.warning(
                        "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r "
                        "has met an exception receiving events. It's being closed. The exception is %r.",
                        ownership["owner_id"],
                        ownership["eventhub_name"],
                        ownership["partition_id"],
                        ownership["consumer_group_name"],
                        eh_err
                    )
                    await process_error(eh_err)
                    await close(reason)  # An EventProcessor will pick up this partition again after the ownership is released
                    # TODO: release the ownership immediately via partition manager
                    break
                except Exception as exp:
                    log.warning(exp)
        finally:
            await partition_consumer.close()
