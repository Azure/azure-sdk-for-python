# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from contextlib import contextmanager
from typing import Dict, Type
import uuid
import asyncio
import logging

from azure.core.tracing import SpanKind  # type: ignore
from azure.core.settings import settings  # type: ignore

from azure.eventhub import EventPosition, EventHubError
from azure.eventhub.aio import EventHubClient
from .partition_context import PartitionContext
from .partition_manager import PartitionManager, OwnershipLostError
from ._ownership_manager import OwnershipManager
from .partition_processor import CloseReason, PartitionProcessor
from .utils import get_running_loop

log = logging.getLogger(__name__)

OWNER_LEVEL = 0


class EventProcessor(object):  # pylint:disable=too-many-instance-attributes
    """
    An EventProcessor constantly receives events from multiple partitions of the Event Hub in the context of a given
    consumer group. The received data will be sent to PartitionProcessor to be processed.

    It provides the user a convenient way to receive events from multiple partitions and save checkpoints.
    If multiple EventProcessors are running for an event hub, they will automatically balance load.

    Example:
        .. code-block:: python

            import asyncio
            import logging
            import os
            from azure.eventhub.aio import EventHubClient
            from azure.eventhub.aio.eventprocessor import EventProcessor, PartitionProcessor
            from azure.eventhub.aio.eventprocessor import SamplePartitionManager

            RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
            RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout.
                             # Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
            CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]

            logging.basicConfig(level=logging.INFO)

            async def do_operation(event):
                # do some sync or async operations. If the operation is i/o bound, async will have better performance
                print(event)


            class MyPartitionProcessor(PartitionProcessor):
                async def process_events(self, events, partition_context):
                    if events:
                        await asyncio.gather(*[do_operation(event) for event in events])
                        await partition_context.update_checkpoint(events[-1].offset, events[-1].sequence_number)

            async def main():
                client = EventHubClient.from_connection_string(CONNECTION_STR, receive_timeout=RECEIVE_TIMEOUT,
                                                               retry_total=RETRY_TOTAL)
                partition_manager = SamplePartitionManager(db_filename=":memory:")  # a filename to persist checkpoint
                try:
                    event_processor = EventProcessor(client, "$default", MyPartitionProcessor,
                                                     partition_manager, polling_interval=10)
                    asyncio.create_task(event_processor.start())
                    await asyncio.sleep(60)
                    await event_processor.stop()
                finally:
                    await partition_manager.close()

            if __name__ == '__main__':
                asyncio.get_event_loop().run_until_complete(main())

    """
    def __init__(
            self, eventhub_client: EventHubClient, consumer_group_name: str,
            partition_processor_type: Type[PartitionProcessor],
            partition_manager: PartitionManager, *,
            initial_event_position: EventPosition = EventPosition("-1"), polling_interval: float = 10.0
    ):
        """
        Instantiate an EventProcessor.

        :param eventhub_client: An instance of ~azure.eventhub.aio.EventClient object
        :type eventhub_client: ~azure.eventhub.aio.EventClient
        :param consumer_group_name: The name of the consumer group this event processor is associated with. Events will
         be read only in the context of this group.
        :type consumer_group_name: str
        :param partition_processor_type: A subclass type of ~azure.eventhub.eventprocessor.PartitionProcessor.
        :type partition_processor_type: type
        :param partition_manager: Interacts with the data storage that stores ownership and checkpoints data.
         ~azure.eventhub.aio.eventprocessor.SamplePartitionManager demonstrates the basic usage of `PartitionManager`
          which stores data in memory or a file.
         Users can either use the provided `PartitionManager` plug-ins or develop their own `PartitionManager`.
        :type partition_manager: Subclass of ~azure.eventhub.eventprocessor.PartitionManager.
        :param initial_event_position: The event position to start a partition consumer.
        if the partition has no checkpoint yet. This could be replaced by "reset" checkpoint in the near future.
        :type initial_event_position: EventPosition
        :param polling_interval: The interval between any two pollings of balancing and claiming
        :type polling_interval: float

        """

        self._consumer_group_name = consumer_group_name
        self._eventhub_client = eventhub_client
        self._eventhub_name = eventhub_client.eh_name
        self._partition_processor_factory = partition_processor_type
        self._partition_manager = partition_manager
        self._initial_event_position = initial_event_position  # will be replaced by reset event position in preview 4
        self._polling_interval = polling_interval
        self._ownership_timeout = self._polling_interval * 2
        self._tasks = {}  # type: Dict[str, asyncio.Task]
        self._id = str(uuid.uuid4())
        self._running = False

    def __repr__(self):
        return 'EventProcessor: id {}'.format(self._id)

    async def start(self):
        """Start the EventProcessor.

        The EventProcessor will try to claim and balance partition ownership with other `EventProcessor`
         and asynchronously start receiving EventData from EventHub and processing events.

        :return: None

        """
        log.info("EventProcessor %r is being started", self._id)
        ownership_manager = OwnershipManager(self._eventhub_client, self._consumer_group_name, self._id,
                                             self._partition_manager, self._ownership_timeout)
        if not self._running:
            self._running = True
            while self._running:
                try:
                    claimed_ownership_list = await ownership_manager.claim_ownership()
                except Exception as err:  # pylint:disable=broad-except
                    log.warning("An exception (%r) occurred during balancing and claiming ownership for eventhub %r "
                                "consumer group %r. Retrying after %r seconds",
                                err, self._eventhub_name, self._consumer_group_name, self._polling_interval)
                    await asyncio.sleep(self._polling_interval)
                    continue

                if claimed_ownership_list:
                    claimed_partition_ids = [x["partition_id"] for x in claimed_ownership_list]
                    to_cancel_list = self._tasks.keys() - claimed_partition_ids
                    self._create_tasks_for_claimed_ownership(claimed_ownership_list)
                else:
                    to_cancel_list = set(self._tasks.keys())
                    log.info("EventProcessor %r hasn't claimed an ownership. It keeps claiming.", self._id)
                if to_cancel_list:
                    self._cancel_tasks_for_partitions(to_cancel_list)
                    log.info("EventProcesor %r has cancelled partitions %r", self._id, to_cancel_list)
                await asyncio.sleep(self._polling_interval)

    async def stop(self):
        """Stop the EventProcessor.

        The EventProcessor will stop receiving events from EventHubs and release the ownership of the partitions
        it is working on.
        Other running EventProcessor will take over these released partitions.

        A stopped EventProcessor can be restarted by calling method `start` again.

        :return: None

        """
        self._running = False
        for _ in range(len(self._tasks)):
            _, task = self._tasks.popitem()
            task.cancel()
        log.info("EventProcessor %r has been cancelled", self._id)
        await asyncio.sleep(2)  # give some time to finish after cancelled.

    def _cancel_tasks_for_partitions(self, to_cancel_partitions):
        for partition_id in to_cancel_partitions:
            if partition_id in self._tasks:
                task = self._tasks.pop(partition_id)
                task.cancel()

    def _create_tasks_for_claimed_ownership(self, to_claim_ownership_list):
        for ownership in to_claim_ownership_list:
            partition_id = ownership["partition_id"]
            if partition_id not in self._tasks or self._tasks[partition_id].done():
                self._tasks[partition_id] = get_running_loop().create_task(self._receive(ownership))

    @contextmanager
    def _context(self, events):
        # Tracing
        span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
        if span_impl_type is None:
            yield
        else:
            child = span_impl_type(name="Azure.EventHubs.process")
            self._eventhub_client._add_span_request_attributes(child)  # pylint: disable=protected-access
            child.kind = SpanKind.SERVER

            for event in events:
                event._trace_link_message(child)  # pylint: disable=protected-access
            with child:
                yield

    async def _receive(self, ownership):  # pylint: disable=too-many-statements
        log.info("start ownership, %r", ownership)
        partition_processor = self._partition_processor_factory()
        partition_id = ownership["partition_id"]
        eventhub_name = ownership["eventhub_name"]
        consumer_group_name = ownership["consumer_group_name"]
        owner_id = ownership["owner_id"]
        partition_context = PartitionContext(
            eventhub_name,
            consumer_group_name,
            partition_id,
            owner_id,
            self._partition_manager
        )
        partition_consumer = self._eventhub_client.create_consumer(
            consumer_group_name,
            partition_id,
            EventPosition(ownership.get("offset", self._initial_event_position.value))
        )

        async def process_error(err):
            log.warning(
                "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                " has met an error. The exception is %r.",
                owner_id, eventhub_name, partition_id, consumer_group_name, err
            )
            try:
                await partition_processor.process_error(err, partition_context)
            except Exception as err_again:  # pylint:disable=broad-except
                log.warning(
                    "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                    " has another error during running process_error(). The exception is %r.",
                    owner_id, eventhub_name, partition_id, consumer_group_name, err_again
                )

        async def close(reason):
            log.info(
                "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                " is being closed. Reason is: %r",
                owner_id, eventhub_name, partition_id, consumer_group_name, reason
            )
            try:
                await partition_processor.close(reason, partition_context)
            except Exception as err:  # pylint:disable=broad-except
                log.warning(
                    "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                    " has an error during running close(). The exception is %r.",
                    owner_id, eventhub_name, partition_id, consumer_group_name, err
                )

        try:
            try:
                await partition_processor.initialize(partition_context)
            except Exception as err:  # pylint:disable=broad-except
                log.warning(
                    "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                    " has an error during running initialize(). The exception is %r.",
                    owner_id, eventhub_name, partition_id, consumer_group_name, err
                )
            while True:
                try:
                    events = await partition_consumer.receive()
                    with self._context(events):
                        await partition_processor.process_events(events, partition_context)

                except asyncio.CancelledError:
                    log.info(
                        "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " is cancelled",
                        owner_id,
                        eventhub_name,
                        partition_id,
                        consumer_group_name
                    )
                    if self._running is False:
                        await close(CloseReason.SHUTDOWN)
                    else:
                        await close(CloseReason.OWNERSHIP_LOST)
                    raise
                except EventHubError as eh_err:
                    await process_error(eh_err)
                    await close(CloseReason.EVENTHUB_EXCEPTION)
                    # An EventProcessor will pick up this partition again after the ownership is released
                    break
                except OwnershipLostError:
                    await close(CloseReason.OWNERSHIP_LOST)
                    break
                except Exception as other_error:  # pylint:disable=broad-except
                    await process_error(other_error)
                    await close(CloseReason.PROCESS_EVENTS_ERROR)
                    break
        finally:
            await partition_consumer.close()
