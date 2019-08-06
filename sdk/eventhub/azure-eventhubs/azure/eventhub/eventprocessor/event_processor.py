# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from typing import Callable, List
import uuid
import asyncio
import logging

from azure.eventhub import EventPosition, EventHubError
from azure.eventhub.aio import EventHubClient
from .checkpoint_manager import CheckpointManager
from .partition_manager import PartitionManager
from .partition_processor import PartitionProcessor, CloseReason
from .utils import get_running_loop

log = logging.getLogger(__name__)

OWNER_LEVEL = 0


class EventProcessor(object):
    def __init__(self, eventhub_client: EventHubClient, consumer_group_name: str,
                 partition_processor_factory: Callable[[CheckpointManager], PartitionProcessor],
                 partition_manager: PartitionManager, **kwargs):
        """
        An EventProcessor constantly receives events from all partitions of the Event Hub in the context of a given
        consumer group. The received data will be sent to PartitionProcessor to be processed.

        It provides the user a convenient way to receive events from multiple partitions and save checkpoints.
        If multiple EventProcessors are running for an event hub, they will automatically balance load.
        This load balancing won't be available until preview 3.

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

        Example:
            ```python
                    class MyPartitionProcessor(PartitionProcessor):
                        async def process_events(self, events):
                            if events:
                                # do something sync or async to process the events
                                await self._checkpoint_manager.update_checkpoint(events[-1].offset, events[-1].sequence_number)


                    import asyncio
                    from azure.eventhub.aio import EventHubClient
                    from azure.eventhub.eventprocessor import EventProcessor, PartitionProcessor, Sqlite3PartitionManager
                    client = EventHubClient.from_connection_string("<your connection string>", receive_timeout=5, retry_total=3)
                    partition_manager = Sqlite3PartitionManager()
                    try:
                        event_processor = EventProcessor(client, "$default", MyPartitionProcessor, partition_manager)
                        asyncio.ensure_future(event_processor.start())
                        await asyncio.sleep(100)  # allow it to run 100 seconds
                        await event_processor.stop()
                    finally:
                        await partition_manager.close()
            ```

        """
        self._consumer_group_name = consumer_group_name
        self._eventhub_client = eventhub_client
        self._eventhub_name = eventhub_client.eh_name
        self._partition_processor_factory = partition_processor_factory
        self._partition_manager = partition_manager
        self._initial_event_position = kwargs.get("initial_event_position", "-1")
        self._max_batch_size = eventhub_client.config.max_batch_size
        self._receive_timeout = eventhub_client.config.receive_timeout
        self._tasks = []  # type: List[asyncio.Task]
        self._id = str(uuid.uuid4())

    def __repr__(self):
        return 'EventProcessor: id {}'.format(self._id)

    async def start(self):
        """Start the EventProcessor.

            1. retrieve the partition ids from eventhubs
            2. claim partition ownership of these partitions.
            3. repeatedly call EvenHubConsumer.receive() to retrieve events and
            call user defined PartitionProcessor.process_events()

            :return None
        """
        log.info("EventProcessor %r is being started", self._id)
        partition_ids = await self._eventhub_client.get_partition_ids()
        claimed_list = await self._claim_partitions(partition_ids)
        await self._start_claimed_partitions(claimed_list)

    async def stop(self):
        """Stop all the partition consumer

        This method cancels tasks that are running EventHubConsumer.receive() for the partitions owned by this EventProcessor.

        :return None
        """
        for i in range(len(self._tasks)):
            task = self._tasks.pop()
            task.cancel()
        log.info("EventProcessor %r has been cancelled", self._id)
        await asyncio.sleep(2)  # give some time to finish after cancelled

    async def _claim_partitions(self, partition_ids):
        partitions_ownership = await self._partition_manager.list_ownership(self._eventhub_name, self._consumer_group_name)
        partitions_ownership_dict = dict()
        for ownership in partitions_ownership:
            partitions_ownership_dict[ownership["partition_id"]] = ownership

        to_claim_list = []
        for pid in partition_ids:
            p_ownership = partitions_ownership_dict.get(pid)
            if p_ownership:
                to_claim_list.append(p_ownership)
            else:
                new_ownership = {"eventhub_name": self._eventhub_name, "consumer_group_name": self._consumer_group_name,
                                 "owner_id": self._id, "partition_id": pid, "owner_level": OWNER_LEVEL}
                to_claim_list.append(new_ownership)
        claimed_list = await self._partition_manager.claim_ownership(to_claim_list)
        return claimed_list

    async def _start_claimed_partitions(self, claimed_partitions):
        for partition in claimed_partitions:
            partition_id = partition["partition_id"]
            offset = partition.get("offset", self._initial_event_position)
            consumer = self._eventhub_client.create_consumer(self._consumer_group_name, partition_id,
                                                            EventPosition(str(offset)))
            partition_processor = self._partition_processor_factory(
                checkpoint_manager=CheckpointManager(partition_id, self._eventhub_name, self._consumer_group_name,
                                                     self._id, self._partition_manager)
            )
            loop = get_running_loop()
            task = loop.create_task(
                _receive(consumer, partition_processor, self._receive_timeout))
            self._tasks.append(task)
        try:
            await asyncio.gather(*self._tasks)
        finally:
            log.info("EventProcessor %r has stopped", self._id)


async def _receive(partition_consumer, partition_processor, receive_timeout):
    try:
        while True:
            try:
                events = await partition_consumer.receive(timeout=receive_timeout)
            except asyncio.CancelledError as cancelled_error:
                log.info(
                    "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r "
                    "is cancelled",
                    partition_processor._checkpoint_manager.owner_id,
                    partition_processor._checkpoint_manager.eventhub_name,
                    partition_processor._checkpoint_manager.partition_id,
                    partition_processor._checkpoint_manager.consumer_group_name
                )
                await partition_processor.process_error(cancelled_error)
                await partition_processor.close(reason=CloseReason.SHUTDOWN)
                break
            except EventHubError as eh_err:
                reason = CloseReason.LEASE_LOST if eh_err.error == "link:stolen" else CloseReason.EVENTHUB_EXCEPTION
                log.warning(
                    "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r "
                    "has met an exception receiving events. It's being closed. The exception is %r.",
                    partition_processor._checkpoint_manager.owner_id,
                    partition_processor._checkpoint_manager.eventhub_name,
                    partition_processor._checkpoint_manager.partition_id,
                    partition_processor._checkpoint_manager.consumer_group_name,
                    eh_err
                )
                await partition_processor.process_error(eh_err)
                await partition_processor.close(reason=reason)
                break
            try:
                await partition_processor.process_events(events)
            except asyncio.CancelledError as cancelled_error:
                log.info(
                    "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r "
                    "is cancelled.",
                    partition_processor._checkpoint_manager.owner_id,
                    partition_processor._checkpoint_manager.eventhub_name,
                    partition_processor._checkpoint_manager.partition_id,
                    partition_processor._checkpoint_manager.consumer_group_name
                )
                await partition_processor.process_error(cancelled_error)
                await partition_processor.close(reason=CloseReason.SHUTDOWN)
                break
            except Exception as exp:  # user code has caused an error
                log.warning(
                    "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r "
                    "has met an exception from user code process_events. It's being closed. The exception is %r.",
                    partition_processor._checkpoint_manager.owner_id,
                    partition_processor._checkpoint_manager.eventhub_name,
                    partition_processor._checkpoint_manager.partition_id,
                    partition_processor._checkpoint_manager.consumer_group_name,
                    exp
                )
                await partition_processor.process_error(exp)
                await partition_processor.close(reason=CloseReason.EVENTHUB_EXCEPTION)
                break
                # TODO: will review whether to break and close partition processor after user's code has an exception
        # TODO: try to inform other EventProcessors to take the partition when this partition is closed in preview 3?
    finally:
        await partition_consumer.close()
