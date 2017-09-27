# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
The module provides a client to connect to Azure Event Hubs.

"""

try:
    import Queue
except:
    import queue as Queue

import logging
import datetime

from proton import DELEGATED, Url, timestamp, generate_uuid
from proton.reactor import dispatch, Container, Selector
from proton.reactor import EventInjector, ApplicationEvent
from proton.handlers import Handler, EndpointStateHandler
from proton.handlers import IncomingMessageHandler
from proton.handlers import CFlowController, OutgoingMessageHandler

# pylint: disable=line-too-long
# pylint: disable=C0111
# pylint: disable=W0613

class EventHubClient(Container):
    """
    The container for all client objects.
    """
    def __init__(self, address=None, *handlers, **kwargs):
        if not address:
            super(EventHubClient, self).__init__(**kwargs)
        else:
            super(EventHubClient, self).__init__(self, **kwargs)
            self.allow_insecure_mechs = False
            self.allowed_mechs = 'PLAIN MSCBS'
            self.address = Url(address)
            self.shared_connection = None
            self.shared_session = None
            self.clients = []
            for handler in handlers:
                self.clients.append(handler)

    def session(self, context):
        if not self.shared_session:
            self.shared_session = context.session()
            self.shared_session.open()
        return self.shared_session

    def on_reactor_init(self, event):
        if not self.shared_connection:
            logging.info("Client starts address=%s", self.address)
            self.shared_connection = self.connect(self.address, reconnect=False, handler=self)
            self.shared_connection.__setattr__("_session_policy", self)
        for client in self.clients:
            client.start(self)

    def on_client_event(self, event):
        dispatch(event.client, event.typename, event.subject)

    def on_connection_local_open(self, event):
        logging.info("Connection local open host=%s", event.connection.hostname)

    def on_connection_remote_open(self, event):
        logging.info("Connection remote open host=%s remote=%s", event.connection.hostname, event.connection.remote_container)

    def on_session_local_open(self, event):
        logging.info("Session local open host=%s", event.connection.hostname)

    def on_session_remote_open(self, event):
        logging.info("Session remote open host=%s", event.connection.hostname)

    def on_connection_remote_close(self, event):
        if EndpointStateHandler.is_local_closed(event.connection):
            return DELEGATED
        condition = event.connection.remote_condition
        if condition:
            logging.error("Connection closed by peer %s:%s %s", condition.name, condition.description, event.connection.remote_container)
        else:
            logging.error("Connection closed by peer %s", event.connection.remote_container)
        if self.shared_session:
            self.shared_session.close()
            self.shared_session = None
        event.connection.close()
        self.shared_connection = None
        self.schedule(3.0, self)

    def on_session_remote_close(self, event):
        if EndpointStateHandler.is_local_closed(event.session):
            return DELEGATED
        event.session.close()
        self.shared_session = None
        condition = event.session.remote_condition
        if condition:
            logging.error("Session close %s:%s %s", condition.name, condition.description, event.connection.remote_container)
        else:
            logging.error("Session close %s", event.connection.remote_container)
        self.schedule(3.0, self)

    #def on_transport_closed(self, event):
    #    pass

    def on_timer_task(self, event):
        self.on_reactor_init(None)

class EventData(object):
    """
    A utility to read EventData properties from an AMQP message
    """
    @classmethod
    def sequence_number(cls, message):
        """
        Return the sequence number of the event data object.
        """
        return message.annotations["x-opt-sequence-number"]

    @classmethod
    def offset(cls, message):
        """
        Return the offset of the event data object.
        """
        return message.annotations["x-opt-offset"]

    @classmethod
    def partition_key(cls, message):
        """
        Return the partition key of the event data object.
        """
        return message.annotations["x-opt-partition-key"]

class ClientHandler(Handler):
    """
    The base class of a sender or a receiver.
    """
    def __init__(self, prefix):
        super(ClientHandler, self).__init__()
        self.name = "%s-%s" % (prefix, str(generate_uuid())[:8])
        self.container = None
        self.link = None
        self.iteration = 0
        self.fatal_conditions = ["amqp:unauthorized-access", "amqp:not-found"]

    def start(self, container):
        self.container = container
        self.iteration += 1
        self.on_start()

    def stop(self):
        if self.link:
            self.link.close()
        self.on_stop()

    def _get_link_name(self):
        return "%s-%d" % (self.name, self.iteration)

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def on_link_remote_close(self, event):
        if EndpointStateHandler.is_local_closed(event.link):
            return DELEGATED
        event.link.close()
        condition = event.link.remote_condition
        if condition:
            logging.error("Link detached %s:%s ref:%s",
                          condition.name,
                          condition.description,
                          event.connection.remote_container)
        else:
            logging.error("Link detached ref:%s", event.connection.remote_container)
        if condition and condition.name in self.fatal_conditions:
            event.connection.close()
        else:
            event.reactor.schedule(3.0, self)

    def on_timer_task(self, event):
        self.start(self.container)

class Sender(ClientHandler):
    """
    Creates a sender to send events to an Event Hub, or
    to a partition directly.

    @param partition: if not None, specifies the partition to send events.
    If None, the events are sent to the event hub and are distributed to
    partition(s) according to the Event Hubs service partitioning logic.

    """
    def __init__(self, partition=None):
        super(Sender, self).__init__("sender")
        self.partition = partition
        self.handlers = [OutgoingMessageHandler(False, self)]
        self.messages = Queue.Queue()
        self.count = 0
        self.injector = None

    def _get_target(self):
        target = self.container.address.path
        if self.partition:
            target += "/Partitions/" + self.partition
        return target

    def send(self, message):
        self.injector.trigger(ClientEvent(self, "message", subject=message))

    def on_start(self):
        if not self.injector:
            self.injector = EventInjector()
            self.container.selectable(self.injector)
        self.link = self.container.create_sender(
            self.container.shared_connection,
            self._get_target(),
            name=self._get_link_name(),
            handler=self)

    def on_stop(self):
        if self.injector:
            self.injector.close()

    def on_link_local_open(self, event):
        logging.info("Link local open. entity=%s", self._get_target())

    def on_link_remote_open(self, event):
        logging.info("Link remote open. entity=%s", self._get_target())

    def on_message(self, event):
        self.messages.append(event.subject)
        self.on_sendable(None)

    def on_sendable(self, event):
        while self.link.credit and not self.messages.empty():
            message = self.messages.get(False)
            self.link.send(message, tag=str(self.count))
            self.count += 1

    def on_accepted(self, event):
        pass

    def on_released(self, event):
        pass

    def on_rejected(self, event):
        pass

class Receiver(ClientHandler):
    """
    Creates a receiver handler for reading events from an Event Hub partition.

    @param handler: handler to process the received event data. It must
    define an 'on_event_data' method. The event data object is an AMQP
    message (proton.Message). Besides the APIs from proton, the module
    provides the EventData utility to access Event Hubs specific
    properties of the message.

    @param consumer_group: the consumer group the receiver belongs to.

    @param partition: the id of the destination partition.

    @param position: the start point to read events. It can be None, a datetime
    a proton.timestamp or a string object.
    string: specifies the offset of an event after which events are returned.
    Besides an actual offset, it can also be '-1' (beginning of the event stream)
    or '@latest' (end of the stream).
    datetime: specifies the enqueued time of the first event that should be
    returned.
    timestamp: same as datetime except that the value is an AMQP timestamp.
    None: no filter will be sent. This is the same as '-1'.

    @param prefetch: the number of events that will be proactively prefetched
    by the library into a local buffer queue.

    """
    def __init__(self, consumer_group, partition, position=None, prefetch=300):
        super(Receiver, self).__init__("receiver")
        self.consumer_group = consumer_group
        self.partition = partition
        self.position = position
        self.handlers = []
        if prefetch:
            self.handlers.append(CFlowController(prefetch))
        self.handlers.append(IncomingMessageHandler(True, self))

    def _get_source(self):
        return "%s/ConsumerGroups/%s/Partitions/%s" % (self.container.address.path, self.consumer_group, self.partition)

    def on_start(self):
        selector = None
        if isinstance(self.position, datetime.datetime):
            _epoch = datetime.datetime.utcfromtimestamp(0)
            _timestamp = long((self.position - _epoch).total_seconds() * 1000.0)
            selector = Selector(u"amqp.annotation.x-opt-enqueued-time > '" + str(_timestamp) + "'")
        elif isinstance(self.position, timestamp):
            selector = Selector(u"amqp.annotation.x-opt-enqueued-time > '" + str(self.position) + "'")
        elif self.position:
            selector = Selector(u"amqp.annotation.x-opt-offset > '" + self.position + "'")
        self.link = self.container.create_receiver(
            self.container.shared_connection,
            self._get_source(),
            name=self._get_link_name(),
            handler=self,
            options=selector)

    def on_event_data(self, message):
        pass

    def on_message(self, event):
        _message = event.message
        self.on_event_data(_message)
        self.position = EventData.offset(_message)

    def on_link_local_open(self, event):
        logging.info("Link local open. entity=%s offset=%s", self._get_source(), self.position)

    def on_link_remote_open(self, event):
        logging.info("Link remote open. entity=%s offset=%s", self._get_source(), self.position)

class ClientEvent(ApplicationEvent):
    """
    Client defined event, to be dispatched by the container to a
    client (Sender or Receiver)
    """
    def __init__(self, client, typename, subject=None):
        super(ClientEvent, self).__init__("client_event", subject=subject)
        self.typename = typename
        self.client = client
