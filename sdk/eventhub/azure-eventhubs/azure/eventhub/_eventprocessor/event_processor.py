# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid
import logging
import time
import threading
from functools import partial

from .partition_context import PartitionContext
from .ownership_manager import OwnershipManager
from .common import CloseReason
from. _eventprocessor_mixin import EventProcessorMixin

_LOGGER = logging.getLogger(__name__)


class EventProcessor(EventProcessorMixin):  # pylint:disable=too-many-instance-attributes
    """
    An EventProcessor constantly receives events from one or multiple partitions of the Event Hub
    in the context of a given consumer group.

    """
    def __init__(self, eventhub_client, consumer_group, on_event, **kwargs):
        self._consumer_group = consumer_group
        self._eventhub_client = eventhub_client
        self._namespace = eventhub_client._address.hostname  # pylint: disable=protected-access
        self._eventhub_name = eventhub_client.eventhub_name
        self._event_handler = on_event
        self._partition_id = kwargs.get("partition_id", None)
        self._error_handler = kwargs.get("on_error", None)
        self._partition_initialize_handler = kwargs.get("on_partition_initialize", None)
        self._partition_close_handler = kwargs.get("on_partition_close", None)
        self._checkpoint_store = kwargs.get("checkpoint_store", None)
        self._initial_event_position = kwargs.get("initial_event_position", "-1")
        self._initial_event_position_inclusive = kwargs.get("initial_event_position_inclusive", False)

        self._polling_interval = kwargs.get("polling_interval", 10.0)
        self._ownership_timeout = self._polling_interval * 2

        self._partition_contexts = {}

        # Receive parameters
        self._owner_level = kwargs.get("owner_level", None)
        if self._checkpoint_store and self._owner_level is None:
            self._owner_level = 0
        self._prefetch = kwargs.get("prefetch", None)
        self._track_last_enqueued_event_properties = kwargs.get("track_last_enqueued_event_properties", False)
        self._id = str(uuid.uuid4())
        self._running = False
        self._lock = threading.RLock()

        self._consumers = {}

    def __repr__(self):
        return 'EventProcessor: id {}'.format(self._id)

    def _cancel_tasks_for_partitions(self, to_cancel_partitions):
        with self._lock:
            for partition_id in to_cancel_partitions:
                if partition_id in self._consumers:
                    self._consumers[partition_id].stop = True

        if to_cancel_partitions:
            _LOGGER.info("EventProcesor %r has cancelled partitions %r", self._id, to_cancel_partitions)

    def _create_tasks_for_claimed_ownership(self, claimed_partitions, checkpoints=None):
        with self._lock:
            for partition_id in claimed_partitions:
                if partition_id not in self._consumers:

                    if partition_id not in self._partition_contexts:
                        partition_context = PartitionContext(
                            self._namespace,
                            self._eventhub_name,
                            self._consumer_group,
                            partition_id,
                            self._checkpoint_store
                        )
                        self._partition_contexts[partition_id] = partition_context

                    checkpoint = checkpoints.get(partition_id) if checkpoints else None
                    initial_event_position = self.get_init_event_position(partition_id, checkpoint)
                    event_received_callback = partial(self._on_event_received, partition_context)

                    self._consumers[partition_id] = self.create_consumer(partition_id,
                                                                         initial_event_position,
                                                                         event_received_callback)

                    if self._partition_initialize_handler:
                        self._handle_callback(
                            [self._partition_initialize_handler,
                             self._partition_contexts[partition_id]]
                        )

    def _handle_callback(self, callback_and_args):
        callback = callback_and_args[0]
        try:
            callback(*callback_and_args[1:])
        except Exception as exp:  # pylint:disable=broad-except
            partition_context = callback_and_args[1]
            if self._error_handler and callback != self._error_handler:
                self._handle_callback([self._error_handler, partition_context, exp])
            else:
                _LOGGER.warning(
                    "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                    " has another error during running process_error(). The exception is %r.",
                    self._id,
                    partition_context.eventhub_name,
                    partition_context.partition_id,
                    partition_context.consumer_group,
                    exp
                )

    def _on_event_received(self, partition_context, event):
        with self._context(event):
            if self._track_last_enqueued_event_properties:
                partition_context._last_received_event = event  # pylint: disable=protected-access
            self._handle_callback([self._event_handler, partition_context, event])

    def _load_balancing(self):
        """Start the EventProcessor.

        The EventProcessor will try to claim and balance partition ownership with other `EventProcessor`
        and start receiving EventData from EventHub and processing events.

        :return: None

        """
        ownership_manager = OwnershipManager(self._eventhub_client, self._consumer_group, self._id,
                                             self._checkpoint_store, self._ownership_timeout, self._partition_id)
        while self._running:
            try:
                checkpoints = ownership_manager.get_checkpoints() if self._checkpoint_store else None
                claimed_partition_ids = ownership_manager.claim_ownership()
                if claimed_partition_ids:
                    to_cancel_list = set(self._consumers.keys()) - set(claimed_partition_ids)
                    self._create_tasks_for_claimed_ownership(claimed_partition_ids, checkpoints)
                else:
                    _LOGGER.info("EventProcessor %r hasn't claimed an ownership. It keeps claiming.", self._id)
                    to_cancel_list = set(self._consumers.keys())
                if to_cancel_list:
                    self._cancel_tasks_for_partitions(to_cancel_list)
            except Exception as err:  # pylint:disable=broad-except
                _LOGGER.warning("An exception (%r) occurred during balancing and claiming ownership for "
                                "eventhub %r consumer group %r. Retrying after %r seconds",
                                err, self._eventhub_name, self._consumer_group, self._polling_interval)
                # ownership_manager.get_checkpoints() and ownership_manager.claim_ownership() may raise exceptions
                # when there are load balancing and/or checkpointing (checkpoint_store isn't None).
                # They're swallowed here to retry every self._polling_interval seconds.
                # Meanwhile this event processor won't lose the partitions it has claimed before.
                # If it keeps failing, other EventProcessors will start to claim ownership of the partitions
                # that this EventProcessor is working on. So two or multiple EventProcessors may be working
                # on the same partition.
            time.sleep(self._polling_interval)

    def _close_consumer(self, partition_id, consumer, reason):
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
            reason
        )

        if self._partition_close_handler:
            self._handle_callback([self._partition_close_handler, self._partition_contexts[partition_id], reason])

    def start(self):
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
                    self._close_consumer(partition_id, consumer, CloseReason.OWNERSHIP_LOST)
                    continue

                try:
                    consumer.receive()
                except Exception as error:  # pylint:disable=broad-except
                    _LOGGER.warning(
                        "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " has met an error. The exception is %r.",
                        self._id,
                        self._partition_contexts[partition_id].eventhub_name,
                        self._partition_contexts[partition_id].partition_id,
                        self._partition_contexts[partition_id].consumer_group,
                        error
                    )
                    if self._error_handler:
                        self._handle_callback([self._error_handler, self._partition_contexts[partition_id], error])
                    self._close_consumer(partition_id, consumer, CloseReason.OWNERSHIP_LOST)

        with self._lock:
            for partition_id, consumer in list(self._consumers.items()):
                self._close_consumer(partition_id, consumer, CloseReason.SHUTDOWN)

    def stop(self):
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
