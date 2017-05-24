# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
The module provides a client to connect to Azure Event Hubs.

"""

import logging
import datetime
from proton import dispatch, Url, generate_uuid, DELEGATED
from proton.reactor import Container, Selector
from proton.handlers import Handler, EndpointStateHandler
from proton.handlers import CFlowController, IncomingMessageHandler

# pylint: disable=line-too-long
# pylint: disable=C0111
# pylint: disable=W0613

class EventHubClient(Container):
    """
    The client to access the Event Hubs service.
    """
    def __init__(self, address=None, *handlers, **kwargs):
        if not address:
            super(EventHubClient, self).__init__(**kwargs)
        else:
            super(EventHubClient, self).__init__(self, **kwargs)
            self.address = Url(address)
            self.receivers = []
            self.shared_connection = None
            self.shared_session = None

    def subscribe(self, handler, consumer_group, partition, position=None, prefetch=300):
        """
        Subscribes to an Event Hub partition to receive events.

        @param handler: handler to process the received event data. It must
        define an 'on_event_data' method. The event data object is an AMQP
        message (proton.Message). Besides the APIs from proton, the module
        provides utility methods in EventData class to access Event Hubs specific
        properties of the message.

        @param consumer_group: the consumer group the receiver belongs to

        @param partition: the id of the event hub partition

        @param position: the start point to read events. It can be None, a datetime
        or a string object.
        string: specifies the offset of an event after which events are returned.
        Besides an actual offset, it can also be '-1' (beginning of the event stream)
        or '@latest' (end of the stream).
        datetime: specifies the enqueued time of the first event that should be
        returned.
        None: no filter will be sent. This is the same as '-1'.

        @param prefetch: the number of events that will be proactively prefetched
        by the library into a local buffer queue

        """
        source = "%s/ConsumerGroups/%s/Partitions/%s" % (self.address.path, consumer_group, partition)
        receiver = PartitionReceiver(handler, source, position, prefetch)
        self.receivers.append(receiver)
        return self

    def session(self, context):
        if not self.shared_session:
            self.shared_session = context.session()
            self.shared_session.open()
        return self.shared_session

    def on_reactor_init(self, event):
        if not self.shared_connection:
            logging.info("Client starts address=%s", self.address)
            self.shared_connection = self.connect(self.address, handler=self)
            self.shared_connection.__setattr__("_session_policy", self)
        for receiver in self.receivers:
            receiver.start(self)

    def on_connection_local_open(self, event):
        logging.info("Connection local open host=%s", event.connection.hostname)

    def on_connection_remote_open(self, event):
        logging.info("Connection remote open host=%s remote=%s", event.connection.hostname, event.connection.remote_container)

    def on_session_local_open(self, event):
        logging.info("Session starts host=%s", event.connection.hostname)

    def on_session_remote_open(self, event):
        logging.info("Session opened host=%s", event.connection.hostname)

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
            self.shared_session.free()
            self.shared_session = None
        event.connection.close()
        self.shared_connection.free()
        self.shared_connection = None
        self.schedule(3.0, self)

    def on_session_remote_close(self, event):
        if EndpointStateHandler.is_local_closed(event.session):
            return DELEGATED
        event.session.close()
        event.session.free()
        self.shared_session = None
        condition = event.session.remote_condition
        if condition:
            logging.error("Session close %s:%s %s", condition.name, condition.description, event.connection.remote_container)
        else:
            logging.error("Session close %s", event.connection.remote_container)
        self.schedule(3.0, self)

    def on_timer_task(self, event):
        self.on_reactor_init(None)

class PartitionReceiver(Handler):
    """
    The receiver to read events from an Event Hub partition.
    """
    def __init__(self, delegate, source, position, prefetch):
        super(PartitionReceiver, self).__init__()
        self.handlers = []
        if prefetch:
            self.handlers.append(CFlowController(prefetch))
        self.handlers.append(IncomingMessageHandler(True, self))
        self.fatal_conditions = ["amqp:unauthorized-access", "amqp:not-found"]
        self.delegate = delegate
        self.source = source
        self.position = position
        self.name = str(generate_uuid())[:8]
        self.iteration = 0
        self.client = None

    def start(self, client):
        self.client = client
        self.iteration += 1
        link_name = "py-receiver-%s-%d" % (self.name, self.iteration)
        selector = None
        if isinstance(self.position, datetime.datetime):
            _epoch = datetime.datetime.utcfromtimestamp(0)
            _timestamp = long((self.position - _epoch).total_seconds() * 1000.0)
            selector = Selector(u"amqp.annotation.x-opt-enqueued-time > '" + str(_timestamp) + "'")
        elif self.position:
            selector = Selector(u"amqp.annotation.x-opt-offset > '" + self.position + "'")
        client.create_receiver(client.shared_connection, self.source, name=link_name, handler=self, options=selector)

    def on_message(self, event):
        _message = event.message
        if self.delegate:
            dispatch(self.delegate, "on_event_data", _message)
        self.position = EventData.offset(_message)

    def on_link_local_open(self, event):
        logging.info("Link starts. entity=%s offset=%s", self.source, self.position)

    def on_link_remote_open(self, event):
        logging.info("Link Opened. entity=%s offset=%s", self.source, self.position)

    def on_link_remote_close(self, event):
        if EndpointStateHandler.is_local_closed(event.link):
            return DELEGATED
        event.link.close()
        event.link.free()
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
            self.client.schedule(3.0, self)

    def on_timer_task(self, event):
        self.start(self.client)

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
