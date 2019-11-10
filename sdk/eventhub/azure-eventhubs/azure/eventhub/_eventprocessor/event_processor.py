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
from functools import partial

from uamqp.compat import queue  # type: ignore

from azure.core.tracing import SpanKind  # type: ignore
from azure.core.settings import settings  # type: ignore

from azure.eventhub import EventPosition
from .partition_context import PartitionContext
from .ownership_manager import OwnershipManager
from .common import CloseReason
from. _eventprocessor_mixin import EventProcessorMixin

log = logging.getLogger(__name__)


class EventProcessor(EventProcessorMixin):  # pylint:disable=too-many-instance-attributes
    """
    An EventProcessor constantly receives events from one or multiple partitions of the Event Hub
    in the context of a given consumer group.

    """
    def __init__(self, eventhub_client, consumer_group_name, on_event, **kwargs):
        self._consumer_group_name = consumer_group_name
        self._eventhub_client = eventhub_client
        self._namespace = eventhub_client._address.hostname  # pylint: disable=protected-access
        self._eventhub_name = eventhub_client.eh_name
        self._event_handler = on_event
        self._partition_id = kwargs.get("partition_id", None)
        self._error_handler = kwargs.get("on_error", None)
        self._partition_initialize_handler = kwargs.get("on_partition_initialize", None)
        self._partition_close_handler = kwargs.get("on_partition_close", None)
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
        self._lock = threading.RLock()

        # Each partition consumer is working in its own thread
        self._consumers = {}
        self._working_threads = {}  # type: Dict[str, threading.Thread]

        self._callback_queue = queue.Queue(maxsize=100)  # Right now the limitation of receiving speed is ~10k

    def __repr__(self):
        return 'EventProcessor: id {}'.format(self._id)

    def _cancel_tasks_for_partitions(self, to_cancel_partitions):
        with self._lock:
            for partition_id in to_cancel_partitions:
                if partition_id in self._working_threads:
                    self._consumers[partition_id].close()

        if to_cancel_partitions:
            log.info("EventProcesor %r has cancelled partitions %r", self._id, to_cancel_partitions)

    def _create_tasks_for_claimed_ownership(self, claimed_partitions, checkpoints=None):
        with self._lock:
            for partition_id in claimed_partitions:
                if partition_id not in self._working_threads or not self._working_threads[partition_id].is_alive():
                    checkpoint = checkpoints.get(partition_id) if checkpoints else None
                    self._working_threads[partition_id] = threading.Thread(target=self._receive,
                                                                           args=(partition_id, checkpoint))
                    self._working_threads[partition_id].daemon = True
                    self._working_threads[partition_id].start()
                    log.info("Working thread started, ownership %r, checkpoint %r", partition_id, checkpoint)

    def _process_error(self, partition_context, err):
        log.warning(
            "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
            " has met an error. The exception is %r.",
            partition_context.owner_id,
            partition_context.eventhub_name,
            partition_context.partition_id,
            partition_context.consumer_group_name,
            err
        )
        if self._error_handler:
            self._callback_queue.put((self._error_handler, partition_context, err), block=True)

    def _process_close(self, partition_context, reason):
        if self._partition_close_handler:
            log.info(
                "PartitionProcessor of EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                " is being closed. Reason is: %r",
                partition_context.owner_id,
                partition_context.eventhub_name,
                partition_context.partition_id,
                partition_context.consumer_group_name,
                reason
            )
            if self._partition_close_handler:
                self._callback_queue.put((self._partition_close_handler, partition_context, reason), block=True)

    def _handle_callback(self, callback_and_args):
        callback = callback_and_args[0]
        try:
            callback(*callback_and_args[1:])
        except Exception as exp:  # pylint:disable=broad-except
            partition_context = callback_and_args[1]
            if callback != self._error_handler:
                self._process_error(partition_context, exp)
            else:
                log.warning(
                    "EventProcessor instance %r of eventhub %r partition %r consumer group %r"
                    " has another error during running process_error(). The exception is %r.",
                    partition_context.owner_id,
                    partition_context.eventhub_name,
                    partition_context.partition_id,
                    partition_context.consumer_group_name,
                    exp
                )

    def _on_event_received(self, partition_context, event):
        with self._context(event):
            self._callback_queue.put((self._event_handler, partition_context, event), block=True)

    def _receive(self, partition_id, checkpoint=None):  # pylint: disable=too-many-statements
        try:  # pylint:disable =too-many-nested-blocks
            log.info("start ownership %r, checkpoint %r", partition_id, checkpoint)
            initial_event_position = self.get_init_event_position(partition_id, checkpoint)
            if partition_id in self._partition_contexts:
                partition_context = self._partition_contexts[partition_id]
            else:
                partition_context = PartitionContext(
                    self._namespace,
                    self._eventhub_name,
                    self._consumer_group_name,
                    partition_id,
                    self._id,
                    self._partition_manager
                )
                self._partition_contexts[partition_id] = partition_context

            self._consumers[partition_id] = self.create_consumer(partition_id, initial_event_position)

            if self._partition_initialize_handler:
                self._callback_queue.put((self._partition_initialize_handler, partition_context), block=True)

            try:
                event_received_callback = partial(self._on_event_received, partition_context)
                self._consumers[partition_id].receive(event_received_callback)
            except Exception as error:
                self._process_error(partition_context, error)
            finally:
                self._consumers[partition_id].close()
                self._process_close(
                    partition_context,
                    CloseReason.OWNERSHIP_LOST if self._running else CloseReason.SHUTDOWN
                )
        finally:
            with self._lock:
                del self._working_threads[partition_id]

    def _start(self):
        """Start the EventProcessor.

        The EventProcessor will try to claim and balance partition ownership with other `EventProcessor`
        and start receiving EventData from EventHub and processing events.

        :return: None

        """
        ownership_manager = OwnershipManager(self._eventhub_client, self._consumer_group_name, self._id,
                                             self._partition_manager, self._ownership_timeout, self._partition_id)
        while self._running:
            try:
                checkpoints = ownership_manager.get_checkpoints() if self._partition_manager else None
                claimed_partition_ids = ownership_manager.claim_ownership()
                if claimed_partition_ids:
                    to_cancel_list = set(self._working_threads.keys()) - set(claimed_partition_ids)
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
                # ownership_manager.get_checkpoints() and ownership_manager.claim_ownership() may raise exceptions
                # when there are load balancing and/or checkpointing (partition_manager isn't None).
                # They're swallowed here to retry every self._polling_interval seconds.
                # Meanwhile this event processor won't lose the partitions it has claimed before.
                # If it keeps failing, other EventProcessors will start to claim ownership of the partitions
                # that this EventProcessor is working on. So two or multiple EventProcessors may be working
                # on the same partition.
            time.sleep(self._polling_interval)

    def _get_last_enqueued_event_properties(self, partition_id):
        if partition_id in self._working_threads and partition_id in self._last_enqueued_event_properties:
            return self._last_enqueued_event_properties[partition_id]
        raise ValueError("You're not receiving events from partition {}".format(partition_id))

    def start(self):
        if not self._running:
            log.info("EventProcessor %r is being started", self._id)
            self._running = True
            thread = threading.Thread(target=self._start)
            thread.daemon = True
            thread.start()

            while self._running or self._callback_queue.qsize() or self._working_threads:
                try:
                    callback_and_args = self._callback_queue.get(block=False)
                    self._handle_callback(callback_and_args)
                    self._callback_queue.task_done()
                except queue.Empty:
                    # ignore queue empty exception
                    time.sleep(0.01)  # sleep a short while to avoid this thread dominating CPU.

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

        with self._lock:
            to_join_threads = [x for x in self._working_threads.values()]
            self._cancel_tasks_for_partitions(list(self._working_threads.keys()))

        for thread in to_join_threads:
            thread.join()

        log.info("EventProcessor %r has been stopped.", self._id)
