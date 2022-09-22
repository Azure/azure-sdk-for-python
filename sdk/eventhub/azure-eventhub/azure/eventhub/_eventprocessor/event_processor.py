# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import random
import uuid
import logging
import time
import threading
from typing import (
    Dict,
    Callable,
    List,
    Any,
    Union,
    TYPE_CHECKING,
    Optional,
    Iterable,
    cast,
)
from functools import partial

from .._utils import get_event_links
from .partition_context import PartitionContext
from .in_memory_checkpoint_store import InMemoryCheckpointStore
from .ownership_manager import OwnershipManager
from .common import CloseReason, LoadBalancingStrategy
from ._eventprocessor_mixin import EventProcessorMixin

if TYPE_CHECKING:
    from datetime import datetime
    from .checkpoint_store import CheckpointStore
    from .._common import EventData
    from .._consumer import EventHubConsumer
    from .._consumer_client import EventHubConsumerClient


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
        eventhub_client,  # type: EventHubConsumerClient
        consumer_group,  # type: str
        on_event,  # type: Callable[[PartitionContext, Union[Optional[EventData], List[EventData]]], None]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        # pylint: disable=line-too-long
        self._consumer_group = consumer_group
        self._eventhub_client = eventhub_client
        self._namespace = (
            eventhub_client._address.hostname  # pylint: disable=protected-access
        )
        self._eventhub_name = eventhub_client.eventhub_name
        self._event_handler = on_event
        self._batch = kwargs.get("batch") or False
        self._max_batch_size = kwargs.get("max_batch_size") or 300
        self._max_wait_time = kwargs.get("max_wait_time")
        self._partition_id = kwargs.get("partition_id", None)  # type: Optional[str]
        self._error_handler = kwargs.get(
            "on_error", None
        )  # type: Optional[Callable[[PartitionContext, Exception], None]]
        self._partition_initialize_handler = kwargs.get(
            "on_partition_initialize", None
        )  # type: Optional[Callable[[PartitionContext], None]]
        self._partition_close_handler = kwargs.get(
            "on_partition_close", None
        )  # type: Optional[Callable[[PartitionContext, CloseReason], None]]
        checkpoint_store = kwargs.get(
            "checkpoint_store"
        )  # type: Optional[CheckpointStore]
        self._checkpoint_store = checkpoint_store or InMemoryCheckpointStore()
        self._initial_event_position = kwargs.get(
            "initial_event_position", "@latest"
        )  # type: Union[str, int, datetime, Dict[str, Any]]
        self._initial_event_position_inclusive = kwargs.get(
            "initial_event_position_inclusive", False
        )  # type: Union[bool, Dict[str, bool]]

        self._load_balancing_interval = kwargs.get(
            "load_balancing_interval", 10.0
        )  # type: float
        self._load_balancing_strategy = (
            kwargs.get("load_balancing_strategy") or LoadBalancingStrategy.GREEDY
        )
        self._ownership_timeout = kwargs.get(
            "partition_ownership_expiration_interval", self._load_balancing_interval * 6
        )

        self._partition_contexts = {}  # type: Dict[str, PartitionContext]

        # Receive parameters
        self._owner_level = kwargs.get("owner_level", None)  # type: Optional[int]
        if checkpoint_store and self._owner_level is None:
            self._owner_level = 0
        self._prefetch = kwargs.get("prefetch", None)  # type: Optional[int]
        self._track_last_enqueued_event_properties = kwargs.get(
            "track_last_enqueued_event_properties", False
        )
        self._id = str(uuid.uuid4())
        self._running = False
        self._lock = threading.RLock()

        self._consumers = {}  # type: Dict[str, EventHubConsumer]
        self._ownership_manager = OwnershipManager(
            self._eventhub_client,
            self._consumer_group,
            self._id,
            self._checkpoint_store,
            self._ownership_timeout,
            self._load_balancing_strategy,
            self._partition_id,
        )

    def __repr__(self):
        # type: () -> str
        return "EventProcessor: id {}".format(self._id)

    def _process_error(self, partition_context, err):
        if self._error_handler:
            try:
                self._error_handler(partition_context, err)
            except Exception as err_again:  # pylint:disable=broad-except
                _LOGGER.warning(
                    "EventProcessor instance %r of eventhub %r partition %r consumer group %r. "
                    "An error occurred while running on_error. The exception is %r.",
                    self._id,
                    partition_context.eventhub_name,
                    partition_context.partition_id,
                    partition_context.consumer_group,
                    err_again,
                )

    def _cancel_tasks_for_partitions(self, to_cancel_partitions):
        # type: (Iterable[str]) -> None
        with self._lock:
            _LOGGER.debug(
                "EventProcessor %r tries to cancel partitions %r",
                self._id,
                to_cancel_partitions,
            )
            for partition_id in to_cancel_partitions:
                if partition_id in self._consumers:
                    self._consumers[partition_id].stop = True
                    _LOGGER.info(
                        "EventProcessor %r has cancelled partition %r",
                        self._id,
                        partition_id,
                    )

    def _initialize_partition_consumer(self, partition_id):
        if self._partition_initialize_handler:
            try:
                self._partition_initialize_handler(
                    self._partition_contexts[partition_id]
                )
            except Exception as err:  # pylint:disable=broad-except
                _LOGGER.warning(
                    "EventProcessor instance %r of eventhub %r partition %r consumer group %r. "
                    "An error occurred while running on_partition_initialize. The exception is %r.",
                    self._id,
                    self._partition_contexts[partition_id].eventhub_name,
                    self._partition_contexts[partition_id].partition_id,
                    self._partition_contexts[partition_id].consumer_group,
                    err,
                )
                self._process_error(self._partition_contexts[partition_id], err)
        _LOGGER.info(
            "EventProcessor %r has claimed partition %r", self._id, partition_id
        )

    def _create_tasks_for_claimed_ownership(self, claimed_partitions, checkpoints=None):
        # type: (Iterable[str], Optional[Dict[str, Dict[str, Any]]]) -> None
        with self._lock:
            _LOGGER.debug(
                "EventProcessor %r tries to claim partition %r",
                self._id,
                claimed_partitions,
            )
            for partition_id in claimed_partitions:
                if partition_id not in self._consumers:
                    if partition_id in self._partition_contexts:
                        partition_context = self._partition_contexts[partition_id]
                        partition_context._last_received_event = (  # pylint:disable=protected-access
                            None
                        )
                    else:
                        partition_context = PartitionContext(
                            self._namespace,
                            self._eventhub_name,
                            self._consumer_group,
                            partition_id,
                            self._checkpoint_store,
                        )
                        self._partition_contexts[partition_id] = partition_context

                    checkpoint = checkpoints.get(partition_id) if checkpoints else None
                    (
                        initial_event_position,
                        event_postition_inclusive,
                    ) = self.get_init_event_position(partition_id, checkpoint)
                    event_received_callback = partial(
                        self._on_event_received, partition_context
                    )
                    self._consumers[partition_id] = cast(
                        "EventHubConsumer",
                        self.create_consumer(
                            partition_id,
                            initial_event_position,
                            event_postition_inclusive,
                            event_received_callback,
                        ),
                    )
                    self._initialize_partition_consumer(partition_id)

    def _on_event_received(self, partition_context, event):
        # type: (PartitionContext, Union[Optional[EventData], List[EventData]]) -> None
        if event:
            try:
                partition_context._last_received_event = event[-1]  # type: ignore  #pylint:disable=protected-access
            except TypeError:
                partition_context._last_received_event = event  # type: ignore  #pylint:disable=protected-access
            links = get_event_links(event)
            with self._context(links=links):
                self._event_handler(partition_context, event)
        else:
            self._event_handler(partition_context, event)

    def _load_balancing(self):
        # type: () -> None
        """Start the EventProcessor.

        The EventProcessor will try to claim and balance partition ownership with other `EventProcessor`
        and start receiving EventData from EventHub and processing events.

        :return: None

        """
        while self._running:
            random_jitter = self._load_balancing_interval * random.random() * 0.2
            load_balancing_interval = self._load_balancing_interval + random_jitter
            try:
                claimed_partition_ids = self._ownership_manager.claim_ownership()
                if claimed_partition_ids:
                    existing_pids = set(self._consumers.keys())
                    claimed_pids = set(claimed_partition_ids)
                    to_cancel_pids = existing_pids - claimed_pids
                    newly_claimed_pids = claimed_pids - existing_pids
                    if newly_claimed_pids:
                        checkpoints = (
                            self._ownership_manager.get_checkpoints()
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
                    to_cancel_pids = set(self._consumers.keys())
                if to_cancel_pids:
                    self._cancel_tasks_for_partitions(to_cancel_pids)
            except Exception as err:  # pylint:disable=broad-except
                # ownership_manager.get_checkpoints() and ownership_manager.claim_ownership() may raise exceptions
                # when there are load balancing and/or checkpointing (checkpoint_store isn't None).
                # They're swallowed here to retry every self._load_balancing_interval seconds.
                # Meanwhile this event processor won't lose the partitions it has claimed before.
                # If it keeps failing, other EventProcessors will start to claim ownership of the partitions
                # that this EventProcessor is working on. So two or multiple EventProcessors may be working
                # on the same partition for a short while.
                # Setting owner_level would create exclusive connection to the partition and
                # alleviate duplicate-receiving greatly.
                _LOGGER.warning(
                    "EventProcessor instance %r of eventhub %r consumer group %r. "
                    "An error occurred while load-balancing and claiming ownership. "
                    "The exception is %r. Retrying after %r seconds",
                    self._id,
                    self._eventhub_name,
                    self._consumer_group,
                    err,
                    load_balancing_interval,
                )
                self._process_error(None, err)  # type: ignore

            time.sleep(load_balancing_interval)

    def _close_consumer(self, partition_id, consumer, reason):
        # type: (str, EventHubConsumer, CloseReason) -> None
        consumer.close()
        with self._lock:
            del self._consumers[partition_id]

        _LOGGER.info(
            "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
            " is being closed. Reason is: %r",
            self._id,
            self._partition_contexts[partition_id].eventhub_name,
            self._partition_contexts[partition_id].partition_id,
            self._partition_contexts[partition_id].consumer_group,
            reason,
        )

        if self._partition_close_handler:
            try:
                self._partition_close_handler(
                    self._partition_contexts[partition_id], reason
                )
            except Exception as err:  # pylint:disable=broad-except
                _LOGGER.warning(
                    "EventProcessor instance %r of eventhub %r partition %r consumer group %r. "
                    "An error occurred while running on_partition_close. The exception is %r.",
                    self._id,
                    self._partition_contexts[partition_id].eventhub_name,
                    self._partition_contexts[partition_id].partition_id,
                    self._partition_contexts[partition_id].consumer_group,
                    err,
                )
                self._process_error(self._partition_contexts[partition_id], err)

        self._ownership_manager.release_ownership(partition_id)

    def _do_receive(self, partition_id, consumer):
        # type: (str, EventHubConsumer) -> None
        """Call the consumer.receive() and handle exceptions if any after it exhausts retries."""
        try:
            consumer.receive(self._batch, self._max_batch_size, self._max_wait_time)
        except Exception as error:  # pylint:disable=broad-except
            _LOGGER.warning(
                "EventProcessor instance %r of eventhub %r partition %r consumer group %r. "
                "An error occurred while receiving. The exception is %r.",
                self._id,
                self._partition_contexts[partition_id].eventhub_name,
                self._partition_contexts[partition_id].partition_id,
                self._partition_contexts[partition_id].consumer_group,
                error,
            )
            self._process_error(self._partition_contexts[partition_id], error)
            self._close_consumer(partition_id, consumer, CloseReason.OWNERSHIP_LOST)

    def start(self):
        # type: () -> None
        if self._running:
            _LOGGER.info("EventProcessor %r has already started.", self._id)
            return

        _LOGGER.info("EventProcessor %r is being started", self._id)
        self._running = True
        thread = threading.Thread(target=self._load_balancing)
        thread.daemon = True
        thread.start()

        while self._running:
            for partition_id, consumer in list(self._consumers.items()):
                if consumer.stop:
                    self._close_consumer(
                        partition_id, consumer, CloseReason.OWNERSHIP_LOST
                    )
                    continue

                self._do_receive(partition_id, consumer)

        with self._lock:
            for partition_id, consumer in list(self._consumers.items()):
                self._close_consumer(partition_id, consumer, CloseReason.SHUTDOWN)

    def stop(self):
        # type: () -> None
        """Stop the EventProcessor.

        The EventProcessor will stop receiving events from EventHubs and release the ownership of the partitions
        it is working on.
        Other running EventProcessor will take over these released partitions.

        A stopped EventProcessor can be restarted by calling method `start` again.

        :return: None

        """
        if not self._running:
            _LOGGER.info("EventProcessor %r has already been stopped.", self._id)
            return

        self._running = False
        _LOGGER.info("EventProcessor %r has been stopped.", self._id)
