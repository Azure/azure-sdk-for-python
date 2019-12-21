# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------
from typing import (
    Dict,
    Callable,
    List,
    Any,
    Union,
    TYPE_CHECKING,
    Optional,
    Iterable,
    Awaitable,
    cast,
)
import uuid
import asyncio
import logging
from functools import partial

from azure.eventhub import EventData
from azure.eventhub.exceptions import EventHubError
from ..._eventprocessor.common import CloseReason
from ..._eventprocessor._eventprocessor_mixin import EventProcessorMixin
from .partition_context import PartitionContext
from .checkpoint_store import CheckpointStore
from ._ownership_manager import OwnershipManager
from .utils import get_running_loop

if TYPE_CHECKING:
    from datetime import datetime
    from .._consumer_async import EventHubConsumer
    from .._consumer_client_async import EventHubConsumerClient

_LOGGER = logging.getLogger(__name__)


class EventProcessor(
    EventProcessorMixin
):  # pylint:disable=too-many-instance-attributes
    """
    An EventProcessor constantly receives events from one or multiple partitions of the Event Hub
    in the context of a given consumer group.

    """

    def __init__(
        self,
        eventhub_client: "EventHubConsumerClient",
        consumer_group: str,
        event_handler: Callable[[PartitionContext, EventData], Awaitable[None]],
        *,
        partition_id: Optional[str] = None,
        checkpoint_store: Optional[CheckpointStore] = None,
        initial_event_position: Union[str, int, "datetime", Dict[str, Any]] = "-1",
        initial_event_position_inclusive: Union[bool, Dict[str, bool]] = False,
        load_balancing_interval: float = 10.0,
        owner_level: Optional[int] = None,
        prefetch: Optional[int] = None,
        track_last_enqueued_event_properties: bool = False,
        error_handler: Optional[
            Callable[[PartitionContext, Exception], Awaitable[None]]
        ] = None,
        partition_initialize_handler: Optional[
            Callable[[PartitionContext], Awaitable[None]]
        ] = None,
        partition_close_handler: Optional[
            Callable[[PartitionContext, CloseReason], Awaitable[None]]
        ] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        self._consumer_group = consumer_group
        self._eventhub_client = eventhub_client
        self._namespace = (
            eventhub_client._address.hostname  # pylint: disable=protected-access
        )
        self._eventhub_name = eventhub_client.eventhub_name
        self._partition_id = partition_id
        self._event_handler = event_handler
        self._error_handler = error_handler
        self._partition_initialize_handler = partition_initialize_handler
        self._partition_close_handler = partition_close_handler
        self._checkpoint_store = checkpoint_store
        self._initial_event_position = initial_event_position
        self._initial_event_position_inclusive = initial_event_position_inclusive
        self._load_balancing_interval = load_balancing_interval
        self._ownership_timeout = self._load_balancing_interval * 2
        self._tasks = {}  # type: Dict[str, asyncio.Task]
        self._partition_contexts = {}  # type: Dict[str, PartitionContext]
        self._owner_level = owner_level
        if self._checkpoint_store and self._owner_level is None:
            self._owner_level = 0
        self._prefetch = prefetch
        self._track_last_enqueued_event_properties = (
            track_last_enqueued_event_properties
        )
        self._id = str(uuid.uuid4())
        self._loop = loop or get_running_loop()
        self._running = False

        self._consumers = {}  # type: Dict[str, EventHubConsumer]
        self._ownership_manager = OwnershipManager(
            cast("EventHubConsumerClient", self._eventhub_client),
            self._consumer_group,
            self._id,
            self._checkpoint_store,
            self._ownership_timeout,
            self._partition_id,
        )

    def __repr__(self) -> str:
        return "EventProcessor: id {}".format(self._id)

    async def _cancel_tasks_for_partitions(
        self, to_cancel_partitions: Iterable[str]
    ) -> None:
        for partition_id in to_cancel_partitions:
            task = self._tasks.get(partition_id)
            if task:
                task.cancel()
        if to_cancel_partitions:
            _LOGGER.info(
                "EventProcesor %r has cancelled partitions %r",
                self._id,
                to_cancel_partitions,
            )

    def _create_tasks_for_claimed_ownership(
        self,
        claimed_partitions: Iterable[str],
        checkpoints: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        for partition_id in claimed_partitions:
            if partition_id not in self._tasks or self._tasks[partition_id].done():
                checkpoint = checkpoints.get(partition_id) if checkpoints else None
                self._tasks[partition_id] = self._loop.create_task(
                    self._receive(partition_id, checkpoint)
                )

    async def _process_error(
        self, partition_context: PartitionContext, err: Exception
    ) -> None:
        _LOGGER.warning(
            "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
            " has met an error. The exception is %r.",
            self._id,
            self._eventhub_name,
            partition_context.partition_id if partition_context else None,
            self._consumer_group,
            err,
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
                    partition_context.consumer_group,
                    err_again,
                )

    async def _close_partition(
        self, partition_context: PartitionContext, reason: CloseReason
    ) -> None:
        if self._partition_close_handler:
            _LOGGER.info(
                "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                " is being closed. Reason is: %r",
                self._id,
                partition_context.eventhub_name,
                partition_context.partition_id,
                partition_context.consumer_group,
                reason,
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
                    partition_context.consumer_group,
                    err,
                )

    async def _on_event_received(
        self, partition_context: PartitionContext, event: EventData
    ) -> None:
        with self._context(event):
            if self._track_last_enqueued_event_properties:
                partition_context._last_received_event = (  # pylint: disable=protected-access
                    event
                )
            await self._event_handler(partition_context, event)

    async def _receive(
        self, partition_id: str, checkpoint: Optional[Dict[str, Any]] = None
    ) -> None:  # pylint: disable=too-many-statements
        partition_context = None
        try:  # pylint:disable=too-many-nested-blocks
            _LOGGER.info("start ownership %r, checkpoint %r", partition_id, checkpoint)
            (
                initial_event_position,
                event_position_inclusive,
            ) = self.get_init_event_position(partition_id, checkpoint)
            if partition_id in self._partition_contexts:
                partition_context = self._partition_contexts[partition_id]
            else:
                partition_context = PartitionContext(
                    self._namespace,
                    self._eventhub_name,
                    self._consumer_group,
                    partition_id,
                    self._checkpoint_store,
                )
                self._partition_contexts[partition_id] = partition_context

            event_received_callback = partial(
                self._on_event_received, partition_context
            )
            self._consumers[partition_id] = self.create_consumer(  # type: ignore
                partition_id,
                initial_event_position,
                event_position_inclusive,
                event_received_callback,  # type: ignore
            )

            if self._partition_initialize_handler:
                try:
                    await self._partition_initialize_handler(partition_context)
                except Exception as err:  # pylint:disable=broad-except
                    _LOGGER.warning(
                        "EventProcessor instance %r of eventhub %r partition %r consumer group %r. "
                        "An error occurred while running initialize(). The exception is %r.",
                        self._id,
                        self._eventhub_name,
                        partition_id,
                        self._consumer_group,
                        err,
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
                        self._consumer_group,
                    )
                    raise
                except Exception as error:  # pylint:disable=broad-except
                    await self._process_error(partition_context, error)
                    break
        finally:
            await self._consumers[partition_id].close()
            await self._close_partition(
                partition_context,
                CloseReason.OWNERSHIP_LOST if self._running else CloseReason.SHUTDOWN,
            )
            await self._ownership_manager.release_ownership(partition_id)
            if partition_id in self._tasks:
                del self._tasks[partition_id]

    async def start(self) -> None:
        """Start the EventProcessor.

        The EventProcessor will try to claim and balance partition ownership with other `EventProcessor`
         and asynchronously start receiving EventData from EventHub and processing events.

        :return: None

        """
        _LOGGER.info("EventProcessor %r is being started", self._id)
        if not self._running:
            self._running = True
            while self._running:
                try:
                    claimed_partition_ids = (
                        await self._ownership_manager.claim_ownership()
                    )
                    if claimed_partition_ids:
                        existing_pids = set(self._consumers.keys())
                        claimed_pids = set(claimed_partition_ids)
                        to_cancel_pids = existing_pids - claimed_pids
                        newly_claimed_pids = claimed_pids - existing_pids
                        if newly_claimed_pids:
                            checkpoints = (
                                await self._ownership_manager.get_checkpoints()
                                if self._checkpoint_store
                                else None
                            )
                            self._create_tasks_for_claimed_ownership(
                                newly_claimed_pids, checkpoints
                            )
                    else:
                        _LOGGER.info(
                            "EventProcessor %r hasn't claimed an ownership. It keeps claiming.",
                            self._id,
                        )
                        to_cancel_pids = set(self._tasks.keys())
                    await self._cancel_tasks_for_partitions(to_cancel_pids)
                except Exception as err:  # pylint:disable=broad-except
                    await self._process_error(None, err)  # type: ignore
                    """
                    ownership_manager.get_checkpoints() and ownership_manager.claim_ownership() may raise exceptions
                    when there are load balancing and/or checkpointing (checkpoint_store isn't None).
                    They're swallowed here to retry every self._load_balancing_interval seconds. Meanwhile this event
                    processor won't lose the partitions it has claimed before.
                    If it keeps failing, other EventProcessors will start to claim ownership of the partitions
                    that this EventProcessor is working on. So two or multiple EventProcessors may be working
                    on the same partition for a short while.
                    Setting owner_level would create exclusive connection to the partition and
                    alleviate duplicate-receiving greatly.
                    """  # pylint:disable=pointless-string-statement
                    _LOGGER.warning(
                        "An exception (%r) occurred during balancing and claiming ownership for "
                        "eventhub %r consumer group %r. Retrying after %r seconds",
                        err,
                        self._eventhub_name,
                        self._consumer_group,
                        self._load_balancing_interval,
                    )
                await asyncio.sleep(self._load_balancing_interval, loop=self._loop)

    async def stop(self) -> None:
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
            await asyncio.sleep(1, loop=self._loop)
        _LOGGER.info("EventProcessor %r has been stopped.", self._id)
