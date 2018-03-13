# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
The module provides a client to connect to Azure Event Hubs. All service specifics
should be implemented in this module.

"""

__version__ = "0.2.0"


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
from uamqp.async import SASTokenAsync
from uamqp.async import ConnectionAsync
from uamqp import constants, utils


log = logging.getLogger("eventhubs")

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
        self.container_id = "eventhubs.pycli-" + str(uuid.uuid4())[:8]
        self.address = urlparse(address)
        username = unquote_plus(self.address.username) if self.address.username else None
        username = kwargs.get('username', username)
        password = unquote_plus(self.address.password) if self.address.password else None
        password = kwargs.get('password', password)
        if not username or not password:
            raise ValueError("Missing username and/or password.")
        auth_uri = "sb://{}{}".format(self.address.hostname, self.address.path)
        self.auth = SASTokenAsync.from_shared_access_key(auth_uri, username, password)

        self.daemon = None
        self.connection = None
        self.debug = kwargs.get('debug', False)

        self.clients = []
        self.stopped = False
        log.info("%s: created the event hub client", self.container_id)

    def _create_connection(self):
        if not self.connection:
            log.info("%s: client starts address=%s", self.container_id, self.address)
            properties = {}
            properties["product"] = "eventhubs.python"
            properties["version"] = __version__
            properties["framework"] = "Python %d.%d.%d" % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
            properties["platform"] = sys.platform
            self.connection = Connection(
                self.address.hostname,
                self.auth,
                container_id=self.container_id,
                properties=properties,
                debug=self.debug)

    def _create_connection_async(self):
        if not self.connection:
            log.info("%s: client starts address=%s", self.container_id, self.address)
            properties = {}
            properties["product"] = "eventhubs.python"
            properties["version"] = __version__
            properties["framework"] = "Python %d.%d.%d" % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
            properties["platform"] = sys.platform
            self.connection = ConnectionAsync(
                self.address.hostname,
                self.auth,
                container_id=self.container_id,
                properties=properties,
                debug=self.debug)

    def _close_connection(self):
        if self.connection:
            self.connection.destroy()
            self.connection = None

    def _close_clients(self):
        for client in self.clients:
            client.close()

    async def _close_connection_async(self):
        if self.connection:
            await self.connection.destroy_async()
            self.connection = None

    async def _close_clients_async(self):
        for client in self.clients:
            await client.close_async()

    async def run_async(self):
        log.info("%s: Starting", self.container_id)
        self._create_connection_async()
        for client in self.clients:
            await client.open_async(connection=self.connection)
        return self

    def run(self):
        """
        Run the L{EventHubClient} in blocking mode.
        """
        log.info("%s: Starting", self.container_id)
        self._create_connection()
        for client in self.clients:
            client.open(connection=self.connection)
        return self

    # def run_daemon(self):
    #     """
    #     Run the L{EventHubClient} in non-blocking mode.
    #     """
    #     log.info("%s: starting the daemon", self.container_id)
    #     self._create_connection()
    #     for client in self.clients:
    #         client.run_daemon(connection=self.connection)
    #     log.info("started")
    #     return self

    def stop(self):
        """
        Stop the client.
        """
        log.info("%s: on_stop_client", self.container_id)
        self.stopped = True
        self._close_clients()
        self._close_connection()

    async def stop_async(self):
        """
        Stop the client.
        """
        log.info("%s: on_stop_client", self.container_id)
        self.stopped = True
        await self._close_clients_async()
        await self._close_connection_async()

    def add_receiver(self, consumer_group, partition, offset=None):
        """
        Registers a L{Receiver} to process L{EventData} objects received from an Event Hub partition.

        @param receiver: receiver to process the received event data. It must
        override the 'on_event_data' method to handle incoming events.

        @param consumer_group: the consumer group to which the receiver belongs.

        @param partition: the id of the event hub partition.

        @param offset: the initial L{Offset} to receive events.
        """
        source_url = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, self.address.path, consumer_group, partition)
        source = Source(source_url)
        if offset is not None:
            source.set_filter(offset.selector())
        handler = Receiver(self, source)
        self.clients.append(handler)
        return handler

    def add_sender(self, partition=None):
        """
        Registers a L{Sender} to publish L{EventData} objects to an Event Hub or one of its partitions.

        @param sender: sender to publish event data.

        @param partition: the id of the destination event hub partition. If not specified, events will
        be distributed across partitions based on the default distribution logic.
        """
        target = "amqps://{}/{}".format(self.address.hostname, self.address.path)
        if partition:
            target += "/Partitions/" + partition
        handler = Sender(self, target)
        self.clients.append(handler)
        return handler


class Sender:
    """
    Implements an L{EventData} sender.
    """
    TIMEOUT = 60.0

    def __init__(self, client, target):
        self._handler = SendClient(target, auth=client.auth, debug=client.debug, msg_timeout=Sender.TIMEOUT)
        self._outcome = None
        self._condition = None

    def send(self, event_data):
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        @param event_data: the L{EventData} to be sent.
        """
        self._event.clear()
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
    def __init__(self, client, source, prefetch=300):
        self.offset = None
        self.prefetch = prefetch
        self._handler = ReceiveClient(source, auth=client.auth, debug=client.debug, prefetch=self.prefetch)

    def on_message(self, event):
        """ Proess message received event. """
        event_data = EventData.create(event.message)
        self.on_event_data(event_data)
        self.offset = event_data.offset

    def receive(self, callback, count=None, timeout=None):
        messages = self._handler.receive_messages_iter()
        return messages

    def on_event_data(self, event_data):
        """ Proess event data received event. """
        assert False, "Subclass must override this!"

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
        annotations[utils.AMQPSymbol(EventData.PROP_PARTITION_KEY)] = value
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
            milli_seconds = timestamp((self.value - epoch).total_seconds() * 1000.0)
            return b"amqp.annotation.x-opt-enqueued-time > '{}'".format(str(milli_seconds).encode('utf-8'))
        elif isinstance(self.value, timestamp):
            return b"amqp.annotation.x-opt-enqueued-time > '{}'".format(str(self.value).encode('utf-8'))
        else:
            operator = b">=" if self.inclusive else b">"
            return b"amqp.annotation.x-opt-offset {} '{}'".format(operator, str(self.value).encode('utf-8'))


class EventHubError(Exception):
    """
    Represents an error happened in the client.
    """
    pass
