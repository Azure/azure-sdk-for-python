# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

from contextlib import contextmanager
from typing import Dict, Type, Callable, List
import uuid
import logging
import time
import threading
from enum import Enum

from azure.core.tracing import SpanKind  # type: ignore
from azure.core.settings import settings  # type: ignore

from azure.eventhub import EventPosition, EventHubError, EventData
# from ..consumer_client_async import EventHubConsumerClient
from .partition_context import PartitionContext
from .partition_manager import PartitionManager, OwnershipLostError
from .ownership_manager import OwnershipManager

log = logging.getLogger(__name__)


class CloseReason(Enum):
    SHUTDOWN = 0  # user call EventProcessor.stop()
    OWNERSHIP_LOST = 1  # lose the ownership of a partition.


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

        self._partition_contexts = {}

        # Receive parameters
        self._owner_level = owner_level
        self._prefetch = prefetch
        self._track_last_enqueued_event_properties = track_last_enqueued_event_properties,
        self._last_enqueued_event_properties = {}
        self._id = str(uuid.uuid4())
        self._running = False

        # Each partition consumer is working in its own thread
        self._working_threads = {}  # type: Dict[str, threading.Thread]
        self._threads_stop_flags = {}  # type: Dict[str, bool]

    def __repr__(self):
        return 'EventProcessor: id {}'.format(self._id)

    def start(self):
        """Start the EventProcessor.

        The EventProcessor will try to claim and balance partition ownership with other `EventProcessor`
        and start receiving EventData from EventHub and processing events.

        :return: None

        """
        log.info("EventProcessor %r is being started", self._id)
        ownership_manager = OwnershipManager(self._eventhub_client, self._consumer_group_name, self._id,
                                             self._partition_manager, self._ownership_timeout)
        if not self._running:
            self._running = True
            if self._partition_id is None and self._partition_manager is not None:
                while self._running:
                    try:
                        claimed_ownership_list = ownership_manager.claim_ownership()
                        checkpoints = ownership_manager.get_checkpoints() if self._partition_manager else None
                        if claimed_ownership_list:
                            claimed_partition_ids = [x["partition_id"] for x in claimed_ownership_list]
                            to_cancel_list = self._working_threads.keys() - claimed_partition_ids
                            self._create_tasks_for_claimed_ownership(claimed_ownership_list, checkpoints)
                        else:
                            to_cancel_list = set(self._working_threads.keys())
                            log.info("EventProcessor %r hasn't claimed an ownership. It keeps claiming.", self._id)
                        if to_cancel_list:
                            self._cancel_tasks_for_partitions(to_cancel_list)
                            log.info("EventProcesor %r has cancelled partitions %r", self._id, to_cancel_list)
                    except Exception as err:  # pylint:disable=broad-except
                        log.warning("An exception (%r) occurred during balancing and claiming ownership for "
                                    "eventhub %r consumer group %r. Retrying after %r seconds",
                                    err, self._eventhub_name, self._consumer_group_name, self._polling_interval)
                    time.sleep(self._polling_interval)
            else:
                checkpoints = ownership_manager.get_checkpoints() if self._partition_manager else None
                if self._partition_id is not None:
                    ownership = [{
                        "namespace": self._namespace,
                        "partition_id": self._partition_id,
                        "eventhub_name": self._eventhub_name,
                        "consumer_group_name": self._consumer_group_name,
                        "owner_id": self._id
                    }]
                else:  # partition_id is None and partition_manager is None
                    partition_ids = self._eventhub_client.get_partition_ids()
                    ownership = []
                    for pid in partition_ids:
                        ownership.append(
                            {
                                "namespace": self._namespace,
                                "partition_id": pid,
                                "eventhub_name": self._eventhub_name,
                                "consumer_group_name": self._consumer_group_name,
                                "owner_id": self._id
                            }
                        )
                self._create_tasks_for_claimed_ownership(ownership, checkpoints)
                while self._working_threads:  # keep it running. No load balancing.
                    time.sleep(self._polling_interval)

    def stop(self):
        """Stop the EventProcessor.

        The EventProcessor will stop receiving events from EventHubs and release the ownership of the partitions
        it is working on.
        Other running EventProcessor will take over these released partitions.

        A stopped EventProcessor can be restarted by calling method `start` again.

        :return: None

        """
        self._running = False
        for partition_id, thread in self._working_threads.items():
            self._threads_stop_flags[partition_id] = True
            thread.join()

        self._working_threads.clear()
        self._threads_stop_flags.clear()

        log.info("EventProcessor %r has been stopped", self._id)

    def get_last_enqueued_event_properties(self, partition_id):
        if partition_id in self._working_threads and partition_id in self._last_enqueued_event_properties:
            return self._last_enqueued_event_properties[partition_id]
        else:
            raise ValueError("You're not receiving events from partition {}".format(partition_id))

    def _cancel_tasks_for_partitions(self, to_cancel_partitions):
        for partition_id in to_cancel_partitions:
            if partition_id in self._working_threads:
                thread = self._working_threads.pop(partition_id)
                self._threads_stop_flags[partition_id] = True
                thread.join()
                del self._threads_stop_flags[partition_id]

    def _create_tasks_for_claimed_ownership(self, to_claim_ownership_list, checkpoints=None):
        for ownership in to_claim_ownership_list:
            partition_id = ownership["partition_id"]
            checkpoint = checkpoints.get(partition_id) if checkpoints else None
            if partition_id not in self._working_threads or not self._working_threads[partition_id].is_alive():
                self._working_threads[partition_id] = threading.Thread(target=self._receive, args=(ownership, checkpoint))
                self._threads_stop_flags[partition_id] = False
                self._working_threads[partition_id].start()
                log.info("Working thread started, ownership %r, checkpoint %r", ownership, checkpoint)

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

    def _receive(self, ownership, checkpoint=None):  # pylint: disable=too-many-statements
        log.info("start ownership %r, checkpoint %r", ownership, checkpoint)
        namespace = ownership["namespace"]
        partition_id = ownership["partition_id"]
        eventhub_name = ownership["eventhub_name"]
        consumer_group_name = ownership["consumer_group_name"]
        owner_id = ownership["owner_id"]
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

        def process_error(err):
            log.warning(
                "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                " has met an error. The exception is %r.",
                owner_id, eventhub_name, partition_id, consumer_group_name, err
            )
            if self._error_handler:
                try:
                    self._error_handler(partition_context, err)
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
                    self._partition_close_handler(partition_context, reason)
                except Exception as err:  # pylint:disable=broad-except
                    log.warning(
                        "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " has an error during running close(). The exception is %r.",
                        owner_id, eventhub_name, partition_id, consumer_group_name, err
                    )

        try:
            if self._partition_initialize_handler:
                try:
                    self._partition_initialize_handler(partition_context)
                except Exception as err:  # pylint:disable=broad-except
                    log.warning(
                        "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                        " has an error during running initialize(). The exception is %r.",
                        owner_id, eventhub_name, partition_id, consumer_group_name, err
                    )
            while not self._threads_stop_flags[partition_id]:
                try:
                    events = partition_consumer.receive()
                    self._last_enqueued_event_properties[partition_id] = \
                        partition_consumer.last_enqueued_event_properties
                    with self._context(events):
                        self._event_handler(partition_context, events)
                except EventHubError as eh_err:  # Keep retrying forever
                    process_error(eh_err)
                    continue
                except Exception as other_error:  # pylint:disable=broad-except
                    process_error(other_error)
                    continue
        finally:
            if self._running is False:
                close(CloseReason.SHUTDOWN)
            else:
                close(CloseReason.OWNERSHIP_LOST)
            partition_consumer.close()
            if partition_id in self._working_threads:
                del self._working_threads[partition_id]
