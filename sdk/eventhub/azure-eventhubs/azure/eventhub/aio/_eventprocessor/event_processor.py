# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from contextlib import contextmanager
from typing import Dict, Type, Callable, List
import uuid
import asyncio
import logging
from enum import Enum

from azure.core.tracing import SpanKind  # type: ignore
from azure.core.settings import settings  # type: ignore

from azure.eventhub import EventPosition, EventHubError, EventData
from ..._eventprocessor.event_processor import CloseReason
from .partition_context import PartitionContext
from .partition_manager import PartitionManager, OwnershipLostError
from .ownership_manager import OwnershipManager
from .utils import get_running_loop

log = logging.getLogger(__name__)


class EventProcessor(object):  # pylint:disable=too-many-instance-attributes
    """
    An EventProcessor constantly receives events from one or multiple partitions of the Event Hub
    in the context of a given consumer group.

    """
    def __init__(
            self, eventhub_client, consumer_group_name: str,
            event_handler: Callable[[PartitionContext, List[EventData]], None],
            *,
            partition_id: str = None,
            partition_manager: PartitionManager = None,
            initial_event_position=EventPosition("-1"), polling_interval: float = 10.0,
            owner_level=None, prefetch=None, track_last_enqueued_event_properties=False,
            error_handler,
            partition_initialize_handler,
            partition_close_handler,
    ):
        self._consumer_group_name = consumer_group_name
        self._eventhub_client = eventhub_client
        self._namespace = eventhub_client._address.hostname
        self._eventhub_name = eventhub_client.eh_name
        self._partition_id = partition_id
        self._event_handler = event_handler
        self._error_handler = error_handler
        self._partition_initialize_handler = partition_initialize_handler
        self._partition_close_handler = partition_close_handler
        self._partition_manager = partition_manager
        self._initial_event_position = initial_event_position  # will be replaced by reset event position in preview 4
        self._polling_interval = polling_interval
        self._ownership_timeout = self._polling_interval * 2
        self._tasks = {}  # type: Dict[str, asyncio.Task]
        self._partition_contexts = {}
        self._owner_level = owner_level
        self._prefetch = prefetch
        self._track_last_enqueued_event_properties = track_last_enqueued_event_properties,
        self._last_enqueued_event_properties = {}
        self._id = str(uuid.uuid4())
        self._running = False

    def __repr__(self):
        return 'EventProcessor: id {}'.format(self._id)

    def _get_last_enqueued_event_properties(self, partition_id):
        if partition_id in self._tasks and partition_id in self._last_enqueued_event_properties:
            return self._last_enqueued_event_properties[partition_id]
        else:
            raise ValueError("You're not receiving events from partition {}".format(partition_id))

    def _cancel_tasks_for_partitions(self, to_cancel_partitions):
        for partition_id in to_cancel_partitions:
            if partition_id in self._tasks:
                task = self._tasks.pop(partition_id)
                task.cancel()
        if to_cancel_partitions:
            log.info("EventProcesor %r has cancelled partitions %r", self._id, to_cancel_partitions)

    def _create_tasks_for_claimed_ownership(self, claimed_partitions, checkpoints=None):
        for partition_id in claimed_partitions:
            checkpoint = checkpoints.get(partition_id) if checkpoints else None
            if partition_id not in self._tasks or self._tasks[partition_id].done():
                self._tasks[partition_id] = get_running_loop().create_task(self._receive(partition_id, checkpoint))

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

    async def _receive(self, partition_id, checkpoint=None):  # pylint: disable=too-many-statements
        log.info("start ownership %r, checkpoint %r", partition_id, checkpoint)
        namespace = self._namespace
        eventhub_name = self._eventhub_name
        consumer_group_name = self._consumer_group_name
        owner_id = self._id
        checkpoint_offset = checkpoint.get("offset") if checkpoint else None
        if checkpoint_offset:
            initial_event_position = EventPosition(checkpoint_offset)
        elif isinstance(self._initial_event_position, EventPosition):
            initial_event_position = self._initial_event_position
        elif isinstance(self._initial_event_position, dict):
            initial_event_position = self._initial_event_position.get(partition_id, EventPosition("-1"))
        else:
            initial_event_position = EventPosition(self._initial_event_position)
        if partition_id in self._partition_contexts:
            partition_context = self._partition_contexts[partition_id]
        else:
            partition_context = PartitionContext(
                namespace,
                eventhub_name,
                consumer_group_name,
                partition_id,
                owner_id,
                self._partition_manager
            )
            self._partition_contexts[partition_id] = partition_context

        partition_consumer = self._eventhub_client._create_consumer(
            consumer_group_name,
            partition_id,
            initial_event_position,
            owner_level=self._owner_level,
            track_last_enqueued_event_properties=self._track_last_enqueued_event_properties,
            prefetch=self._prefetch,
        )

        async def process_error(err):
            log.warning(
                "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                " has met an error. The exception is %r.",
                owner_id, eventhub_name, partition_id, consumer_group_name, err
            )
            if self._error_handler:
                try:
                    await self._error_handler(partition_context, err)
                except Exception as err_again:  # pylint:disable=broad-except
                    log.warning(
                        "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " has another error during running process_error(). The exception is %r.",
                        owner_id, eventhub_name, partition_id, consumer_group_name, err_again
                    )

        async def close(reason):
            if self._partition_close_handler:
                log.info(
                    "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                    " is being closed. Reason is: %r",
                    owner_id, eventhub_name, partition_id, consumer_group_name, reason
                )
                try:
                    await self._partition_close_handler(partition_context, reason)
                except Exception as err:  # pylint:disable=broad-except
                    log.warning(
                        "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " has an error during running close(). The exception is %r.",
                        owner_id, eventhub_name, partition_id, consumer_group_name, err
                    )

        try:
            if self._partition_initialize_handler:
                try:
                    await self._partition_initialize_handler(partition_context)
                except Exception as err:  # pylint:disable=broad-except
                    log.warning(
                        "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " has an error during running initialize(). The exception is %r.",
                        owner_id, eventhub_name, partition_id, consumer_group_name, err
                    )
            while True:
                try:
                    events = await partition_consumer.receive()
                    self._last_enqueued_event_properties[partition_id] = \
                        partition_consumer.last_enqueued_event_properties
                    with self._context(events):
                        await self._event_handler(partition_context, events)
                except asyncio.CancelledError:
                    log.info(
                        "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " is cancelled",
                        owner_id,
                        eventhub_name,
                        partition_id,
                        consumer_group_name
                    )
                    raise
                except Exception as error:  # pylint:disable=broad-except
                    await process_error(error)
                    break
                # Go to finally to stop this partition processor.
                # Later an EventProcessor(this one or another one) will pick up this partition again
        finally:
            if self._running is False:
                await close(CloseReason.SHUTDOWN)
            else:
                await close(CloseReason.OWNERSHIP_LOST)
            await partition_consumer.close()
            if partition_id in self._tasks:
                del self._tasks[partition_id]

    async def start(self):
        """Start the EventProcessor.

        The EventProcessor will try to claim and balance partition ownership with other `EventProcessor`
         and asynchronously start receiving EventData from EventHub and processing events.

        :return: None

        """
        log.info("EventProcessor %r is being started", self._id)
        ownership_manager = OwnershipManager(self._eventhub_client, self._consumer_group_name, self._id,
                                             self._partition_manager, self._ownership_timeout, self._partition_id)
        if not self._running:
            self._running = True
            while self._running:
                try:
                    checkpoints = await ownership_manager.get_checkpoints() if self._partition_manager else None
                    claimed_partition_ids = await ownership_manager.claim_ownership()
                    if claimed_partition_ids:
                        to_cancel_list = self._tasks.keys() - claimed_partition_ids
                        self._create_tasks_for_claimed_ownership(claimed_partition_ids, checkpoints)
                    else:
                        log.info("EventProcessor %r hasn't claimed an ownership. It keeps claiming.", self._id)
                        to_cancel_list = set(self._tasks.keys())
                    self._cancel_tasks_for_partitions(to_cancel_list)
                except Exception as err:  # pylint:disable=broad-except
                    log.warning("An exception (%r) occurred during balancing and claiming ownership for "
                                "eventhub %r consumer group %r. Retrying after %r seconds",
                                err, self._eventhub_name, self._consumer_group_name, self._polling_interval)
                    '''
                    ownership_manager.get_checkpoints() and ownership_manager.claim_ownership() may raise exceptions
                    when there are load balancing and/or checkpointing (partition_manager isn't None).
                    They're swallowed here to retry every self._polling_interval seconds. Meanwhile this event processor
                    won't lose the partitions it has claimed before.
                    If it keeps failing, other EventProcessors will start to claim ownership of the partitions 
                    that this EventProcessor is working on. So two or multiple EventProcessors may be working 
                    on the same partition.

                    Should we raise this exception out to users?
                    '''
                    # TODO: This exception handling requires more thinking
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
        log.info("EventProcessor %r has been cancelled.", self._id)
        await asyncio.gather(*self._tasks.values())
