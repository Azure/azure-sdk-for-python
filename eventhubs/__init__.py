# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
The module provides a client to connect to Azure Event Hubs. All service specifics
should be implemented in this module.

"""

__version__ = "0.1.0"

# pylint: disable=line-too-long
# pylint: disable=W0613
# pylint: disable=W0702
# pylint: disable=C0103

import logging
import datetime
import sys
import threading
from proton import DELEGATED, Url, timestamp, generate_uuid, utf82unicode
from proton import Delivery, Message
from proton.reactor import dispatch, Container, Selector, ApplicationEvent
from proton.handlers import Handler, EndpointStateHandler
from proton.handlers import IncomingMessageHandler
from proton.handlers import CFlowController, OutgoingMessageHandler
from ._impl import SenderHandler, ReceiverHandler, SessionPolicy

if sys.platform.startswith("win"):
    from ._win import EventInjector
else:
    from proton.reactor import EventInjector

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
        self.container_id = "eventhubs.pycli-" + str(generate_uuid())[:8]
        self.address = Url(address)
        self.injector = EventInjector()
        self.container = self._create_container(self.address, **kwargs)
        self.daemon = None
        self.connection = None
        self.session_policy = None
        self.clients = []
        self.stopped = False
        log.info("%s: created the event hub client", self.container_id)

    def run(self):
        """
        Run the L{EventHubClient} in blocking mode.
        """
        self.container.run()

    def run_daemon(self):
        """
        Run the L{EventHubClient} in non-blocking mode.
        """
        log.info("%s: starting the daemon", self.container_id)
        self.daemon = threading.Thread(target=self.run)
        self.daemon.daemon = True
        self.daemon.start()
        return self

    def stop(self):
        """
        Stop the client.
        """
        if self.daemon is not None:
            log.info("%s: stopping daemon", self.container_id)
            self.injector.trigger(ApplicationEvent("stop_client"))
            self.injector.close()
            self.daemon.join()
        else:
            self.on_stop_client(None)

    def subscribe(self, receiver, consumer_group, partition, offset=None):
        """
        Registers a L{Receiver} to process L{EventData} objects received from an Event Hub partition.

        @param receiver: receiver to process the received event data. It must
        override the 'on_event_data' method to handle incoming events.

        @param consumer_group: the consumer group to which the receiver belongs.

        @param partition: the id of the event hub partition.

        @param offset: the initial L{Offset} to receive events.
        """
        source = "%s/ConsumerGroups/%s/Partitions/%s" % (self.address.path, consumer_group, partition)
        selector = None
        if offset is not None:
            selector = offset.selector()
        handler = ReceiverHandler(self, receiver, source, selector)
        self.clients.append(handler)
        return self

    def publish(self, sender, partition=None):
        """
        Registers a L{Sender} to publish L{EventData} objects to an Event Hub or one of its partitions.

        @param sender: sender to publish event data.

        @param partition: the id of the destination event hub partition. If not specified, events will
        be distributed across partitions based on the default distribution logic.
        """
        target = self.address.path
        if partition:
            target += "/Partitions/" + partition
        handler = sender.handler(self, target)
        self.clients.append(handler)
        return self

    def on_reactor_init(self, event):
        """ Handles reactor init event. """
        log.info("%s: on_reactor_init", self.container_id)
        if not self.connection:
            log.info("%s: client starts address=%s", self.container_id, self.address)
            properties = {}
            properties["product"] = "eventhubs.python"
            properties["version"] = __version__
            properties["framework"] = "Python %d.%d.%d" % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
            properties["platform"] = sys.platform
            self.connection = self.container.connect(self.address, reconnect=False, properties=properties)
            self.session_policy = SessionPolicy()
            self.connection.__setattr__("_session_policy", self.session_policy)
        for client in self.clients:
            client.start()

    def on_reactor_final(self, event):
        """ Handles reactor final event. """
        log.info("%s: reactor final", self.container_id)
        self.injector.pipe.close()

    def on_connection_local_open(self, event):
        """Handles on_connection_local_open event."""
        log.info("%s: connection local open", event.connection.container)

    def on_connection_remote_open(self, event):
        """Handles on_connection_remote_open event."""
        log.info("%s: connection remote open %s", self.container_id, event.connection.remote_container)

    def on_session_local_open(self, event):
        """Handles on_session_local_open event."""
        log.info("%s: session local open", self.container_id)

    def on_session_remote_open(self, event):
        """Handles on_session_remote_open event."""
        log.info("%s: session remote open", self.container_id)

    def on_connection_remote_close(self, event):
        """Handles on_connection_remote_close event."""
        if self.stopped or event.connection != self.connection:
            return DELEGATED
        if EndpointStateHandler.is_local_closed(event.connection):
            return DELEGATED
        condition = event.connection.remote_condition
        if condition:
            log.error("%s: connection closed by peer %s:%s %s",
                      self.container_id,
                      condition.name,
                      condition.description,
                      event.connection.remote_container)
        else:
            log.error("%s: connection closed by peer %s",
                      self.container_id,
                      event.connection.remote_container)
        self._close_clients()
        self._close_session()
        self._close_connection()
        self.container.schedule(1.0, self)

    def on_session_remote_close(self, event):
        """Handles on_session_remote_close event."""
        if EndpointStateHandler.is_local_closed(event.session):
            return DELEGATED
        condition = event.session.remote_condition
        if condition:
            log.error("%s: session close %s:%s %s",
                      self.container_id,
                      condition.name,
                      condition.description,
                      self.connection.remote_container)
        else:
            log.error("%s, session close %s",
                      self.container_id,
                      self.connection.remote_container)
        self._close_clients()
        self._close_session()
        self.container.schedule(1.0, self)

    def on_transport_closed(self, event):
        """ Handles on_transport_closed event. """
        if event.connection != self.connection:
            return DELEGATED
        if self.connection is None or EndpointStateHandler.is_local_closed(self.connection):
            return DELEGATED
        log.error("%s: transport close, condition %s", self.container_id, event.transport.condition)
        self._close_clients()
        self._close_session()
        self._close_connection()
        self.on_reactor_init(None)

    def on_timer_task(self, event):
        """ Handles on_timer_task event. """
        if not self.stopped:
            self.on_reactor_init(None)

    def on_stop_client(self, event):
        """ Handles on_stop_client event. """
        log.info("%s: on_stop_client", self.container_id)
        self.stopped = True
        self._close_clients()
        self._close_session()
        self._close_connection()

    def on_send(self, event):
        """ Called when messages are available to send for a sender. """
        event.subject.on_sendable(None)

    def _create_container(self, address, **kwargs):
        container = Container(self, **kwargs)
        container.container_id = self.container_id
        container.allow_insecure_mechs = True
        container.allowed_mechs = 'PLAIN MSCBS'
        container.selectable(self.injector)
        return container

    def _close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection.free()
            self.connection = None

    def _close_session(self):
        if self.session_policy:
            self.session_policy.reset()

    def _close_clients(self):
        for client in self.clients:
            client.stop()

class Entity(object):
    """
    The base class of a L{Sender} or L{Receiver}.
    """
    def on_start(self, link, iteration):
        """
        Called when the entity is started or restarted.
        """
        pass

    def on_stop(self, closed):
        """
        Called when the entity is stopped.
        """
        pass

class Sender(Entity):
    """
    Implements an L{EventData} sender.
    """
    def __init__(self):
        self._handler = None
        self._event = threading.Event()
        self._outcome = None

    def send(self, event_data, timeout=60):
        """
        Sends an event data.

        @param event_data: the L{EventData} to be sent.

        @param timeout: time in seconds to wait for the acknowledgement.
        """
        self._check()
        self._event.clear()
        self._handler.send(event_data.message, self.on_outcome, None)
        if not self._event.wait(timeout):
            raise EventHubError("Send operation timed out", timeout, self._handler.client.container_id)
        if self._outcome != Delivery.ACCEPTED:
            raise self._error(self._outcome)

    def transfer(self, event_data, callback):
        """
        Transfers an event data and notifies the callback when the operation is done.

        @param event_data: the L{EventData} to be transferred.

        @param callback: a function invoked when the operation is completed. The argument
        to the callback function is a tuple where the first item is the event data and the
        second item is the result (None on success, or a L{EventHubError} on failure).
        """
        self._check()
        self._handler.send(event_data.message,
                           lambda d, o: callback(d, Sender._error(o)),
                           event_data)

    def handler(self, client, target):
        """
        Creates a protocol handler for this sender.
        """
        self._handler = SenderHandler(client, self, target)
        return self._handler

    def on_outcome(self, state, outcome):
        """
        Called when the outcome is received for a delivery.
        """
        self._outcome = outcome
        self._event.set()

    def _check(self):
        if self._handler is None:
            raise EventHubError("Call publish to register the sender before using it.")

    @staticmethod
    def _error(outcome):
        return None if outcome == Delivery.ACCEPTED else EventHubError("Send failed", outcome)

class Receiver(Entity):
    """
    Implements an L{EventData} receiver.

    @param prefetch: the number of events that will be proactively prefetched
    by the library into a local buffer queue.

    """
    def __init__(self, prefetch=300):
        self.offset = None
        self.prefetch = prefetch

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

    PROP_SEQ_NUMBER = "x-opt-sequence-number"
    PROP_OFFSET = "x-opt-offset"
    PROP_PARTITION_KEY = "x-opt-partition-key"

    def __init__(self, body=None):
        """
        @param kwargs: name/value pairs in properties.
        """
        self.message = Message(body)

    @property
    def sequence_number(self):
        """
        Return the sequence number of the event data object.
        """
        return self.message.annotations[EventData.PROP_SEQ_NUMBER]

    @property
    def offset(self):
        """
        Return the offset of the event data object.
        """
        return self.message.annotations[EventData.PROP_OFFSET]

    def _get_partition_key(self):
        return self.message.annotations[EventData.PROP_PARTITION_KEY]

    def _set_partition_key(self, value):
        self.message.annotations[EventData.PROP_PARTITION_KEY] = value

    partition_key = property(_get_partition_key, _set_partition_key, doc="""
        Gets or sets the partition key of the event data object.
        """)

    @property
    def properties(self):
        """Application defined properties (dict)."""
        return self.message.properties

    @property
    def body(self):
        """Return the body of the event data object."""
        return self.message.body

    @classmethod
    def create(cls, message):
        """Creates an event data object from an AMQP message."""
        event_data = EventData()
        event_data.message = message
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
            return Selector(u"amqp.annotation.x-opt-enqueued-time > '" + str(milli_seconds) + "'")
        elif isinstance(self.value, timestamp):
            return Selector(u"amqp.annotation.x-opt-enqueued-time > '" + str(self.value) + "'")
        else:
            operator = ">=" if self.inclusive else ">"
            return Selector(u"amqp.annotation.x-opt-offset " + operator + " '" + utf82unicode(self.value) + "'")

class EventHubError(Exception):
    """
    Represents an error happened in the client.
    """
    pass
