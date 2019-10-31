# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from contextlib import contextmanager
from typing import Dict, Type
import uuid
import logging
import time
import threading
from enum import Enum

from azure.core.tracing import SpanKind  # type: ignore
from azure.core.settings import settings  # type: ignore

from azure.eventhub import EventPosition, EventHubError, EventData
from .partition_context import PartitionContext
from .partition_manager import PartitionManager, OwnershipLostError
from .ownership_manager import OwnershipManager
from uamqp.compat import queue

log = logging.getLogger(__name__)


class CloseReason(Enum):
    SHUTDOWN = 0  # user call EventProcessor.stop()
    OWNERSHIP_LOST = 1  # lose the ownership of a partition.


class EventProcessor(object):  # pylint:disable=too-many-instance-attributes
    """
    An EventProcessor constantly receives events from one or multiple partitions of the Event Hub
    in the context of a given consumer group.

    """
    def __init__(self, eventhub_client, consumer_group_name, event_handler, **kwargs):
        self._consumer_group_name = consumer_group_name
        self._eventhub_client = eventhub_client
        self._namespace = eventhub_client._address.hostname  # pylint: disable=protected-access
        self._eventhub_name = eventhub_client.eh_name
        self._event_handler = event_handler
        self._partition_id = kwargs.get("partition_id", None)
        self._error_handler = kwargs.get("error_handler", None)
        self._partition_initialize_handler = kwargs.get("partition_initialize_handler", None)
        self._partition_close_handler = kwargs.get("partition_close_handler", None)
        self._partition_manager = kwargs.get("partition_manager", None)
        self._initial_event_position = kwargs.get("initial_event_position", EventPosition("-1"))

        self._polling_interval = kwargs.get("polling_interval", 10.0)
        self._ownership_timeout = self._polling_interval * 2

        self._partition_contexts = {}

        # Receive parameters
        self._owner_level = kwargs.get("owner_level", None)
        self._prefetch = kwargs.get("prefetch", None)
        self._track_last_enqueued_event_properties = kwargs.get("track_last_enqueued_event_properties", False)
        self._last_enqueued_event_properties = {}
        self._id = str(uuid.uuid4())
        self._running = False

        # Each partition consumer is working in its own thread
        self._working_threads = {}  # type: Dict[str, threading.Thread]
        self._threads_stop_flags = {}  # type: Dict[str, bool]

        self._callback_queue = queue.Queue(maxsize=10000)  # Right now the limitation of receiving speed is ~10k

    def __repr__(self):
        return 'EventProcessor: id {}'.format(self._id)

    def _cancel_tasks_for_partitions(self, to_cancel_partitions):
        to_stop_partition_threads = []
        for partition_id in to_cancel_partitions:
            if partition_id in self._working_threads:
                thread = self._working_threads.pop(partition_id)
                self._threads_stop_flags[partition_id] = True
                to_stop_partition_threads.append((partition_id, thread))
        for thread in to_stop_partition_threads:
            thread[1].join()
            del self._threads_stop_flags[thread[0]]
        if to_cancel_partitions:
            log.info("EventProcesor %r has cancelled partitions %r", self._id, to_cancel_partitions)

    def _create_tasks_for_claimed_ownership(self, claimed_partitions, checkpoints=None):
        for partition_id in claimed_partitions:
            checkpoint = checkpoints.get(partition_id) if checkpoints else None
            if partition_id not in self._working_threads or not self._working_threads[partition_id].is_alive():
                self._working_threads[partition_id] = threading.Thread(target=self._receive, args=(partition_id, checkpoint))
                self._threads_stop_flags[partition_id] = False
                self._working_threads[partition_id].start()
                log.info("Working thread started, ownership %r, checkpoint %r", partition_id, checkpoint)

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

    def _receive(self, partition_id, checkpoint=None):  # pylint: disable=too-many-statements
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

        partition_consumer = self._eventhub_client._create_consumer(  # pylint: disable=protected-access
            consumer_group_name,
            partition_id,
            initial_event_position,
            owner_level=self._owner_level,
            track_last_enqueued_event_properties=self._track_last_enqueued_event_properties,
            prefetch=self._prefetch,
        )

        def process_error(err):
            log.warning(
                "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                " has met an error. The exception is %r.",
                owner_id, eventhub_name, partition_id, consumer_group_name, err
            )
            if self._error_handler:
                try:
                    self._callback_queue.put((self._error_handler, partition_context, err), block=True)
                except Exception as err_again:  # pylint:disable=broad-except
                    log.warning(
                        "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " has another error during running process_error(). The exception is %r.",
                        owner_id, eventhub_name, partition_id, consumer_group_name, err_again
                    )

        def close(reason):
            if self._partition_close_handler:
                log.info(
                    "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                    " is being closed. Reason is: %r",
                    owner_id, eventhub_name, partition_id, consumer_group_name, reason
                )
                try:
                    self._callback_queue.put((self._partition_close_handler, partition_context, reason), block=True)
                except Exception as err:  # pylint:disable=broad-except
                    log.warning(
                        "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " has an error during running close(). The exception is %r.",
                        owner_id, eventhub_name, partition_id, consumer_group_name, err
                    )

        try:
            if self._partition_initialize_handler:
                try:
                    self._callback_queue.put((self._partition_initialize_handler, partition_context), block=True)
                except Exception as err:  # pylint:disable=broad-except
                    log.warning(
                        "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " has an error during running initialize(). The exception is %r.",
                        owner_id, eventhub_name, partition_id, consumer_group_name, err
                    )
            while self._running and not self._threads_stop_flags[partition_id]:
                try:
                    events = partition_consumer.receive()
                    self._last_enqueued_event_properties[partition_id] = \
                        partition_consumer.last_enqueued_event_properties
                    with self._context(events):
                        self._callback_queue.put((self._event_handler, partition_context, events), block=True)
                except Exception as error:  # pylint:disable=broad-except
                    process_error(error)
                    break
                    # Go to finally to stop this partition processor.
                    # Later an EventProcessor(this one or another one) will pick up this partition again
        finally:
            if self._running is False or self._threads_stop_flags[partition_id]:
                close(CloseReason.SHUTDOWN)
            else:
                close(CloseReason.OWNERSHIP_LOST)
            partition_consumer.close()

    def _start(self):
        """Start the EventProcessor.

        The EventProcessor will try to claim and balance partition ownership with other `EventProcessor`
        and start receiving EventData from EventHub and processing events.

        :return: None

        """
        log.info("EventProcessor %r is being started", self._id)
        ownership_manager = OwnershipManager(self._eventhub_client, self._consumer_group_name, self._id,
                                             self._partition_manager, self._ownership_timeout, self._partition_id)
        if not self._running:
            self._running = True
            while self._running:
                try:
                    checkpoints = ownership_manager.get_checkpoints() if self._partition_manager else None
                    claimed_partition_ids = ownership_manager.claim_ownership()
                    if claimed_partition_ids:
                        to_cancel_list = self._working_threads.keys() - claimed_partition_ids
                        self._create_tasks_for_claimed_ownership(claimed_partition_ids, checkpoints)
                    else:
                        log.info("EventProcessor %r hasn't claimed an ownership. It keeps claiming.", self._id)
                        to_cancel_list = set(self._working_threads.keys())
                    if to_cancel_list:
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
                    '''
                time.sleep(self._polling_interval)

    def _get_last_enqueued_event_properties(self, partition_id):
        if partition_id in self._working_threads and partition_id in self._last_enqueued_event_properties:
            return self._last_enqueued_event_properties[partition_id]
        else:
            raise ValueError("You're not receiving events from partition {}".format(partition_id))

    def start(self):
        if not self._running:
            thread = threading.Thread(target=self._start)
            thread.start()
            while not self._running:
                time.sleep(0.1)
            while self._running or self._callback_queue.qsize() > 0:
                callback_and_args = self._callback_queue.get(True)
                callback = callback_and_args[0]
                callback(*callback_and_args[1:])
        else:
            log.info("EventProcessor %r has already started.", self._id)

    def stop(self):
        """Stop the EventProcessor.

        The EventProcessor will stop receiving events from EventHubs and release the ownership of the partitions
        it is working on.
        Other running EventProcessor will take over these released partitions.

        A stopped EventProcessor can be restarted by calling method `start` again.

        :return: None

        """
        if not self._running:
            log.info("EventProcessor %r has already been stopped.", self._id)
            return

        self._running = False

        for _ in range(len(self._working_threads)):
            partition_id, thread = self._working_threads.popitem()
            self._threads_stop_flags[partition_id] = True
            thread.join()

        self._working_threads.clear()
        self._threads_stop_flags.clear()

        log.info("EventProcessor %r has been stopped.", self._id)
