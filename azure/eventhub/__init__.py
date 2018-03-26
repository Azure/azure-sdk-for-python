# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
The module provides a client to connect to Azure Event Hubs. All service specifics
should be implemented in this module.

"""

import logging
import datetime
import sys
import threading
import uuid
import time
import asyncio
try:
    from urllib import urlparse
    from urllib import unquote_plus
except Exception:
    from urllib.parse import unquote_plus
    from urllib.parse import urlparse

import uamqp
from uamqp import Connection
from uamqp import SendClient, ReceiveClient
from uamqp import Message, BatchMessage
from uamqp import Source, Target
from uamqp import authentication
from uamqp import constants, types


__version__ = "0.2.0a1"

log = logging.getLogger(__name__)


class EventHubClient(object):
    """
    The L{EventHubClient} class defines a high level interface for sending
    events to and receiving events from the Azure Event Hubs service.
    """
    def __init__(self, address, **kwargs):
        """
        Constructs a new L{EventHubClient} with the given address Url.

        @param address: the full Uri string of the event hub.
        """
        self.container_id = "eventhub.pysdk-" + str(uuid.uuid4())[:8]
        self.address = urlparse(address)
        username = unquote_plus(self.address.username) if self.address.username else None
        username = kwargs.get('username') or username
        password = unquote_plus(self.address.password) if self.address.password else None
        password = kwargs.get('password') or password
        if not username or not password:
            raise ValueError("Missing username and/or password.")
        auth_uri = "sb://{}{}".format(self.address.hostname, self.address.path)
        self.auth = self._create_auth(auth_uri, username, password)

        self.daemon = None
        self.connection = None
        self.debug = kwargs.get('debug', False)

        self.clients = []
        self.stopped = False
        log.info("{}: Created the Event Hub client".format(self.container_id))

    def _create_auth(self, auth_uri, username, password):
        return authentication.SASTokenAuth.from_shared_access_key(auth_uri, username, password)

    def _create_properties(self):
        properties = {}
        properties["product"] = "eventhub.python"
        properties["version"] = __version__
        properties["framework"] = "Python {}.{}.{}".format(*sys.version_info[0:3])
        properties["platform"] = sys.platform
        return properties

    def _create_connection(self):
        if not self.connection:
            log.info("{}: Creating connection with address={}".format(self.container_id, self.address.geturl()))
            self.connection = Connection(
                self.address.hostname,
                self.auth,
                container_id=self.container_id,
                properties=self._create_properties(),
                debug=self.debug)

    def _close_connection(self):
        if self.connection:
            self.connection.destroy()
            self.connection = None

    def _close_clients(self):
        for client in self.clients:
            client.close()

    def run(self):
        """
        Run the L{EventHubClient} in blocking mode.
        """
        log.info("{}: Starting {} clients".format(self.container_id, len(self.clients)))
        self._create_connection()
        for client in self.clients:
            client.open(connection=self.connection)
        return self

    def stop(self):
        """
        Stop the client.
        """
        log.info("{}: Stopping {} clients".format(self.container_id, len(self.clients)))
        self.stopped = True
        self._close_clients()
        self._close_connection()

    def get_eventhub_info(self):
        eh_name = self.address.path.lstrip('/')
        target = "amqps://{}/{}".format(self.address.hostname, eh_name)
        with uamqp.AMQPClient(target, auth=self.auth, debug=True) as mgmt_client:
            mgmt_msg = Message(application_properties={'name': eh_name})
            response = mgmt_client.mgmt_request(
                mgmt_msg,
                constants.READ_OPERATION,
                op_type=b'com.microsoft:eventhub',
                status_code_field=b'status-code',
                description_fields=b'status-description')
            return response.get_data()

    def add_receiver(self, consumer_group, partition, offset=None, prefetch=300):
        """
        Registers a L{Receiver} to process L{EventData} objects received from an Event Hub partition.

        @param receiver: receiver to process the received event data. It must
        override the 'on_event_data' method to handle incoming events.

        @param consumer_group: the consumer group to which the receiver belongs.

        @param partition: the id of the event hub partition.

        @param offset: the initial L{Offset} to receive events.
        """
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, self.address.path, consumer_group, partition)
        source = Source(source_url)
        if offset is not None:
            source.set_filter(offset.selector())
        handler = Receiver(self, source, prefetch=prefetch)
        self.clients.append(handler._handler)
        return handler

    def add_epoch_receiver(self, consumer_group, partition, epoch, prefetch=300):
        """
        Registers a L{Receiver} to process L{EventData} objects received from an Event Hub partition.

        @param receiver: receiver to process the received event data. It must
        override the 'on_event_data' method to handle incoming events.

        @param consumer_group: the consumer group to which the receiver belongs.

        @param partition: the id of the event hub partition.

        @param offset: the initial L{Offset} to receive events.
        """
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, self.address.path, consumer_group, partition)
        handler = Receiver(self, source_url, prefetch=prefetch, epoch=epoch)
        self.clients.append(handler._handler)
        return handler

    def add_sender(self, partition=None):
        """
        Registers a L{Sender} to publish L{EventData} objects to an Event Hub or one of its partitions.

        @param sender: sender to publish event data.

        @param partition: the id of the destination event hub partition. If not specified, events will
        be distributed across partitions based on the default distribution logic.
        """
        target = "amqps://{}{}".format(self.address.hostname, self.address.path)
        if partition:
            target += "/Partitions/" + partition
        handler = Sender(self, target)
        self.clients.append(handler._handler)
        return handler


class Sender:
    """
    Implements an L{EventData} sender.
    """
    TIMEOUT = 60.0

    def __init__(self, client, target):
        self._handler = SendClient(
            target,
            auth=client.auth,
            debug=client.debug,
            msg_timeout=Sender.TIMEOUT)
        self._outcome = None
        self._condition = None

    def send(self, event_data):
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        @param event_data: the L{EventData} to be sent.
        """
        event_data.message.on_send_complete = self.on_outcome
        self._handler.send_message(event_data.message)
        if self._outcome != constants.MessageSendResult.Ok:
            raise Sender._error(self._outcome, self._condition)

    def transfer(self, event_data, callback=None):
        """
        Transfers an event data and notifies the callback when the operation is done.

        @param event_data: the L{EventData} to be transferred.

        @param callback: a function invoked when the operation is completed. The first
        argument to the callback function is the event data and the second item is the
        result (None on success, or a L{EventHubError} on failure).
        """
        if callback:
            event_data.message.on_send_complete = lambda o, c: callback(o, Sender._error(o, c))
        self._handler.queue_message(event_data.message)

    def wait(self):
        self._handler.wait()

    def on_outcome(self, outcome, condition):
        """
        Called when the outcome is received for a delivery.
        """
        self._outcome = outcome
        self._condition = condition

    @staticmethod
    def _error(outcome, condition):
        return None if outcome == constants.MessageSendResult.Ok else EventHubError(outcome, condition)


class Receiver:
    """
    Implements an L{EventData} receiver.

    @param prefetch: the number of events that will be proactively prefetched
    by the library into a local buffer queue.

    """
    timeout = 0 #60.0
    _epoch = b'com.microsoft:epoch'

    def __init__(self, client, source, prefetch=300, epoch=None):
        self.offset = None
        self._callback = None
        self.prefetch = prefetch
        self.epoch = epoch
        self.delivered = 0
        properties = None
        if epoch:
            properties = {types.AMQPSymbol(self._epoch): types.AMQPLong(int(epoch))}
        self._handler = ReceiveClient(
            source,
            auth=client.auth,
            debug=client.debug,
            prefetch=self.prefetch,
            link_properties=properties,
            timeout=self.timeout)

    @property
    def queue_size(self):
        if self._handler._received_messages:
            return self._handler._received_messages.qsize()
        return 0

    def on_message(self, event):
        """ Proess message received event. """
        self.delivered += 1
        event_data = EventData.create(event)
        if self._callback:
            self._callback(event_data)
        self.offset = event_data.offset
        return event_data

    def receive(self, batch_size=None, callback=None, timeout=None):
        timeout_ms = 1000 * timeout if timeout else 0
        self._callback = callback
        if batch_size:
            message_iter = self._handler.receive_message_batch(
                batch_size=batch_size,
                on_message_received=self.on_message,
                timeout=timeout_ms)
            for event_data in message_iter:
                yield event_data
        else:
            receive_timeout = time.time() + timeout if timeout else None
            message_iter = self._handler.receive_message_batch(
                on_message_received=self.on_message,
                timeout=timeout_ms)
            while message_iter and (not receive_timeout or time.time() < receive_timeout):
                for event_data in message_iter:
                    yield event_data
                if receive_timeout:
                    timeout_ms = int((receive_timeout - time.time()) * 1000)
                message_iter = self._handler.receive_message_batch(
                    on_message_received=self.on_message,
                    timeout=timeout_ms)

    def selector(self, default):
        """ Create a selector for the current offset if it is set. """
        if self.offset is not None:
            return Offset(self.offset).selector()
        return default


class EventData(object):
    """
    The L{EventData} class is a holder of event content.
    """

    PROP_SEQ_NUMBER = b"x-opt-sequence-number"
    PROP_OFFSET = b"x-opt-offset"
    PROP_PARTITION_KEY = b"x-opt-partition-key"

    def __init__(self, body=None, batch=None):
        """
        @param kwargs: name/value pairs in properties.
        """
        if batch:
            self.message = BatchMessage(data=batch, multi_messages=True)
        elif body:
            self.message = Message(body)
        self._annotations = {}
        self._properties = {}

    @property
    def sequence_number(self):
        """
        Return the sequence number of the received event data object.
        """
        return self._annotations.get(EventData.PROP_SEQ_NUMBER, None)

    @property
    def offset(self):
        """
        Return the offset of the received event data object.
        """
        return self._annotations.get(EventData.PROP_OFFSET, None)

    @property
    def partition_key(self):
        """
        Return the partition key of the event data object.
        """
        return self._annotations.get(EventData.PROP_PARTITION_KEY, None)

    @partition_key.setter
    def partition_key(self, value):
        """
        Set the partition key of the event data object.
        """
        annotations = dict(self._annotations)
        annotations[types.AMQPSymbol(EventData.PROP_PARTITION_KEY)] = value
        self.message.message_annotations = annotations
        self._annotations = annotations

    @property
    def properties(self):
        """Application defined properties (dict)."""
        return self._properties

    @property
    def body(self):
        """Return the body of the event data object."""
        return self.message.get_data()

    @classmethod
    def create(cls, message):
        """Creates an event data object from an AMQP message."""
        event_data = EventData()
        event_data.message = message
        event_data._annotations = message.message_annotations
        event_data._properties = message.application_properties
        return event_data


class Offset(object):
    """
    The offset (position or timestamp) where a receiver starts. Examples:
    Beginning of the event stream:
      >>> offset = Offset("-1")
    End of the event stream:
      >>> offset = Offset("@latest")
    Events after the specified offset:
      >>> offset = Offset("12345")
    Events from the specified offset:
      >>> offset = Offset("12345", True)
    Events after current time:
      >>> offset = Offset(datetime.datetime.utcnow())
    Events after a specific timestmp:
      >>> offset = Offset(timestamp(1506968696002))

    """
    def __init__(self, value, inclusive=False):
        self.value = value
        self.inclusive = inclusive

    def selector(self):
        """ Creates a selector expression of the offset """
        if isinstance(self.value, datetime.datetime):
            epoch = datetime.datetime.utcfromtimestamp(0)
            milli_seconds = timestamp((self.value - epoch).total_seconds() * 1000.0)  # TODO
            return ("amqp.annotation.x-opt-enqueued-time > '{}'".format(milli_seconds)).encode('utf-8')
        elif isinstance(self.value, int):
            return ("amqp.annotation.x-opt-enqueued-time > '{}'".format(self.value)).encode('utf-8')
        else:
            operator = ">=" if self.inclusive else ">"
            return ("amqp.annotation.x-opt-offset {} '{}'".format(operator, self.value)).encode('utf-8')


class EventHubError(Exception):
    """
    Represents an error happened in the client.
    """
    pass
