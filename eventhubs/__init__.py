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
from uamqp import constants, utils


#from proton import DELEGATED
#from proton.handlers import EndpointStateHandler

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
        username = kwargs.get('username', unquote_plus(self.address.username))
        password = kwargs.get('password', unquote_plus(self.address.password))
        if not username or not password:
            raise ValueError("Missing username and/or password.")
        auth_uri = "sb://{}{}".format(self.address.hostname, self.address.path)
        print("Auth uri: {}".format(auth_uri))
        print("user/pass: {}, {}".format(username, password))
        self.auth = authentication.SASTokenAuth.from_shared_access_key(auth_uri, username, password)

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
        log.info("%s: Starting", self.container_id)
        self._create_connection()
        for client in self.clients:
            client.open(connection=self.connection)
        return self

    def run_daemon(self):
        """
        Run the L{EventHubClient} in non-blocking mode.
        """
        log.info("%s: starting the daemon", self.container_id)
        self._create_connection()
        for client in self.clients:
            client.run_daemon(connection=self.connection)
        log.info("started")
        return self

    def stop(self):
        """
        Stop the client.
        """
        log.info("%s: on_stop_client", self.container_id)
        self.stopped = True
        self._close_clients()
        self._close_connection()

    def subscribe(self, receiver, consumer_group, partition, offset=None):
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
        handler = receiver.handler(self, source)
        self.clients.append(handler)
        return self

    def publish(self, sender, partition=None):
        """
        Registers a L{Sender} to publish L{EventData} objects to an Event Hub or one of its partitions.

        @param sender: sender to publish event data.

        @param partition: the id of the destination event hub partition. If not specified, events will
        be distributed across partitions based on the default distribution logic.
        """
        target = "amqps://{}/{}".format(self.address.hostname, self.address.path)
        if partition:
            target += "/Partitions/" + partition
        handler = sender.handler(self, target)
        self.clients.append(handler)
        return self

    # def on_connection_remote_close(self, event):
    #     """Handles on_connection_remote_close event."""
    #     if self.stopped or event.connection != self.connection:
    #         return DELEGATED
    #     if EndpointStateHandler.is_local_closed(event.connection):
    #         return DELEGATED
    #     condition = event.connection.remote_condition
    #     if condition:
    #         log.error("%s: connection closed by peer %s:%s %s",
    #                   self.container_id,
    #                   condition.name,
    #                   condition.description,
    #                   event.connection.remote_container)
    #     else:
    #         log.error("%s: connection closed by peer %s",
    #                   self.container_id,
    #                   event.connection.remote_container)
    #     self._close_clients(condition)
    #     self._close_session()
    #     self._close_connection()
    #     self.container.schedule(1.0, self)

    # def on_session_remote_close(self, event):
    #     """Handles on_session_remote_close event."""
    #     if EndpointStateHandler.is_local_closed(event.session):
    #         return DELEGATED
    #     condition = event.session.remote_condition
    #     if condition:
    #         log.error("%s: session close %s:%s %s",
    #                   self.container_id,
    #                   condition.name,
    #                   condition.description,
    #                   self.connection.remote_container)
    #     else:
    #         log.error("%s, session close %s",
    #                   self.container_id,
    #                   self.connection.remote_container)
    #     self._close_clients(condition)
    #     self._close_session()
    #     self.container.schedule(1.0, self)

    # def on_transport_closed(self, event):
    #     """ Handles on_transport_closed event. """
    #     if event.connection != self.connection:
    #         return DELEGATED
    #     if self.connection is None or EndpointStateHandler.is_local_closed(self.connection):
    #         return DELEGATED
    #     log.error("%s: transport close, condition %s", self.container_id, event.transport.condition)
    #     self._close_clients(event.transport.condition)
    #     self._close_session()
    #     self._close_connection()
    #     self.on_reactor_init(None)


class Sender:
    """
    Implements an L{EventData} sender.
    """
    TIMEOUT = 60.0

    def __init__(self):
        self._handler = None
        self._event = threading.Event()
        self._outcome = None
        self._condition = None

    def send(self, event_data):
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        @param event_data: the L{EventData} to be sent.
        """
        self._check()
        self._event.clear()
        event_data.message.on_send_complete = self.on_outcome
        self._handler.queue_message(event_data.message)
        while self._handler._daemon.is_alive():
            if self._event.is_set():
                break
        if self._outcome != constants.MessageSendResult.Ok:
            if not self._event.is_set():
                raise Sender._error(constants.MessageSendResult.Error,
                "Message was not sent.")
            raise Sender._error(self._outcome, self._condition)

    def transfer(self, event_data, callback=None):
        """
        Transfers an event data and notifies the callback when the operation is done.

        @param event_data: the L{EventData} to be transferred.

        @param callback: a function invoked when the operation is completed. The first
        argument to the callback function is the event data and the second item is the
        result (None on success, or a L{EventHubError} on failure).
        """
        self._check()
        if callback:
            event_data.message.on_send_complete = lambda o, c: callback(o, Sender._error(o, c))
        self._handler.queue_message(event_data.message)

    def wait(self):
        self._handler.wait()

    def handler(self, client, target):
        """
        Creates a protocol handler for this sender.
        """
        self._handler = SendClient(target, auth=client.auth, debug=client.debug, msg_timeout=Sender.TIMEOUT)
        return self._handler

    def on_outcome(self, outcome, condition):
        """
        Called when the outcome is received for a delivery.
        """
        self._outcome = outcome
        self._condition = condition
        self._event.set()

    def _check(self):
        if self._handler is None:
            raise EventHubError("Call publish to register the sender before using it.")

    @staticmethod
    def _error(outcome, condition):
        return None if outcome == constants.MessageSendResult.Ok else EventHubError(outcome, condition)


class Receiver:
    """
    Implements an L{EventData} receiver.

    @param prefetch: the number of events that will be proactively prefetched
    by the library into a local buffer queue.

    """
    def __init__(self, prefetch=300):
        self.offset = None
        self.prefetch = prefetch

    def handler(self, client, source):
        """
        Creates a protocol handler for this sender.
        """
        self._handler = ReceiveClient(source, auth=client.auth, debug=client.debug, prefetch=self.prefetch, on_message_received=self.on_message)
        return self._handler

    def on_message(self, event):
        """ Proess message received event. """
        event_data = EventData.create(event.message)
        self.on_event_data(event_data)
        self.offset = event_data.offset

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


    def __init__(self, body=None):
        """
        @param kwargs: name/value pairs in properties.
        """
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
