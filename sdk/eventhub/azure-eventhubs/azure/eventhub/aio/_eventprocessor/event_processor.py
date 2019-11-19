# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------
from typing import Dict, Callable, List, Any
import uuid
import asyncio
import logging
from functools import partial

from azure.eventhub import EventPosition, EventData, EventHubError
from ..._eventprocessor.common import CloseReason
from ..._eventprocessor._eventprocessor_mixin import EventProcessorMixin
from .partition_context import PartitionContext
from .partition_manager import PartitionManager
from ._ownership_manager import OwnershipManager
from .utils import get_running_loop

_LOGGER = logging.getLogger(__name__)


class EventProcessor(EventProcessorMixin):  # pylint:disable=too-many-instance-attributes
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
            partition_close_handler
    ):
        self._consumer_group_name = consumer_group_name
        self._eventhub_client = eventhub_client
        self._namespace = eventhub_client._address.hostname  # pylint: disable=protected-access
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
        self._partition_contexts = {}  # type: Dict[str, PartitionContext]
        self._owner_level = owner_level
        self._prefetch = prefetch
        self._track_last_enqueued_event_properties = track_last_enqueued_event_properties
        self._last_enqueued_event_properties = {}  # type: Dict[str, Dict[str, Any]]
        self._id = str(uuid.uuid4())
        self._running = False

        self._consumers = {}

    def __repr__(self):
        return 'EventProcessor: id {}'.format(self._id)

    def _get_last_enqueued_event_properties(self, partition_id):
        if partition_id in self._tasks and partition_id in self._last_enqueued_event_properties:
            return self._last_enqueued_event_properties[partition_id]
        raise ValueError("You're not receiving events from partition {}".format(partition_id))

    async def _cancel_tasks_for_partitions(self, to_cancel_partitions):
        for partition_id in to_cancel_partitions:
            task = self._tasks.get(partition_id)
            if task:
                task.cancel()
        if to_cancel_partitions:
            _LOGGER.info("EventProcesor %r has cancelled partitions %r", self._id, to_cancel_partitions)

    def _create_tasks_for_claimed_ownership(self, claimed_partitions, checkpoints=None):
        for partition_id in claimed_partitions:
            if partition_id not in self._tasks or self._tasks[partition_id].done():
                checkpoint = checkpoints.get(partition_id) if checkpoints else None
                self._tasks[partition_id] = get_running_loop().create_task(self._receive(partition_id, checkpoint))

    async def _process_error(self, partition_context, err):
        _LOGGER.warning(
            "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
            " has met an error. The exception is %r.",
            self._id,
            partition_context.eventhub_name,
            partition_context.partition_id,
            partition_context.consumer_group_name,
            err
        )
        if self._error_handler:
            try:
                await self._error_handler(partition_context, err)
            except Exception as err_again:  # pylint:disable=broad-except
                _LOGGER.warning(
                    "EventProcessor instance %r of eventhub %r partition %r consumer group %r. "
                    "An error occurred while running process_error(). The exception is %r.",
                    self._id,
                    partition_context.eventhub_name,
                    partition_context.partition_id,
                    partition_context.consumer_group_name,
                    err_again
                )

    async def _close_partition(self, partition_context, reason):
        if self._partition_close_handler:
            _LOGGER.info(
                "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                " is being closed. Reason is: %r",
                self._id,
                partition_context.eventhub_name,
                partition_context.partition_id,
                partition_context.consumer_group_name,
                reason
            )
            try:
                await self._partition_close_handler(partition_context, reason)
            except Exception as err:  # pylint:disable=broad-except
                _LOGGER.warning(
                    "EventProcessor instance %r of eventhub %r partition %r consumer group %r. "
                    "An error occurred while running close(). The exception is %r.",
                    self._id,
                    partition_context.eventhub_name,
                    partition_context.partition_id,
                    partition_context.consumer_group_name,
                    err
                )

    async def _on_event_received(self, partition_context, event):
        with self._context(event):
            try:
                await self._event_handler(partition_context, event)
            except asyncio.CancelledError:  # pylint: disable=try-except-raise
                raise
            except Exception as error:  # pylint:disable=broad-except
                await self._process_error(partition_context, error)

    async def _receive(self, partition_id, checkpoint=None):  # pylint: disable=too-many-statements
        try:  # pylint:disable=too-many-nested-blocks
            _LOGGER.info("start ownership %r, checkpoint %r", partition_id, checkpoint)
            initial_event_position = self.get_init_event_position(partition_id, checkpoint)
            if partition_id in self._partition_contexts:
                partition_context = self._partition_contexts[partition_id]
            else:
                partition_context = PartitionContext(
                    self._namespace,
                    self._eventhub_name,
                    self._consumer_group_name,
                    partition_id,
                    self._partition_manager
                )
                self._partition_contexts[partition_id] = partition_context

            event_received_callback = partial(self._on_event_received, partition_context)
            self._consumers[partition_id] = self.create_consumer(partition_id,
                                                                 initial_event_position,
                                                                 event_received_callback)

            if self._partition_initialize_handler:
                try:
                    await self._partition_initialize_handler(partition_context)
                except Exception as err:  # pylint:disable=broad-except
                    _LOGGER.warning(
                        "EventProcessor instance %r of eventhub %r partition %r consumer group %r. "
                        "An error occurred while running initialize(). The exception is %r.",
                        self._id, self._eventhub_name, partition_id, self._consumer_group_name, err
                    )

            while self._running:
                try:
                    await self._consumers[partition_id].receive()
                except asyncio.CancelledError:
                    _LOGGER.info(
                        "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " is cancelled",
                        self._id,
                        self._eventhub_name,
                        partition_id,
                        self._consumer_group_name
                    )
                    raise
                except EventHubError as eh_error:
                    await self._process_error(partition_context, eh_error)
                    break
                except Exception as error:  # pylint:disable=broad-except
                    await self._process_error(partition_context, error)
        finally:
            await self._consumers[partition_id].close()
            await self._close_partition(
                partition_context,
                CloseReason.OWNERSHIP_LOST if self._running else CloseReason.SHUTDOWN
            )
            if partition_id in self._tasks:
                del self._tasks[partition_id]

    async def start(self):
        """Start the EventProcessor.

        The EventProcessor will try to claim and balance partition ownership with other `EventProcessor`
         and asynchronously start receiving EventData from EventHub and processing events.

        :return: None

        """
        _LOGGER.info("EventProcessor %r is being started", self._id)
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
                        _LOGGER.info("EventProcessor %r hasn't claimed an ownership. It keeps claiming.", self._id)
                        to_cancel_list = set(self._tasks.keys())
                    await self._cancel_tasks_for_partitions(to_cancel_list)
                except Exception as err:  # pylint:disable=broad-except
                    '''
                    ownership_manager.get_checkpoints() and ownership_manager.claim_ownership() may raise exceptions
                    when there are load balancing and/or checkpointing (partition_manager isn't None).
                    They're swallowed here to retry every self._polling_interval seconds. Meanwhile this event processor
                    won't lose the partitions it has claimed before.
                    If it keeps failing, other EventProcessors will start to claim ownership of the partitions
                    that this EventProcessor is working on. So two or multiple EventProcessors may be working
                    on the same partition.
                    '''  # pylint:disable=pointless-string-statement
                    _LOGGER.warning("An exception (%r) occurred during balancing and claiming ownership for "
                                    "eventhub %r consumer group %r. Retrying after %r seconds",
                                    err, self._eventhub_name, self._consumer_group_name, self._polling_interval)
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
        pids = list(self._tasks.keys())
        await self._cancel_tasks_for_partitions(pids)
        _LOGGER.info("EventProcessor %r tasks have been cancelled.", self._id)
        while self._tasks:
            await asyncio.sleep(1)
        _LOGGER.info("EventProcessor %r has been stopped.", self._id)
