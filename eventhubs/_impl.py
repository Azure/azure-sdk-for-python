# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Internal implementations.

"""

# pylint: disable=line-too-long
# pylint: disable=C0111
# pylint: disable=W0613
# pylint: disable=W0702

import logging

import datetime
from proton import DELEGATED, generate_uuid, timestamp, utf82unicode
from proton.reactor import EventInjector, ApplicationEvent, Selector
from proton.handlers import Handler, EndpointStateHandler
from proton.handlers import IncomingMessageHandler
from proton.handlers import CFlowController, OutgoingMessageHandler

try:
    import Queue
except:
    import queue as Queue

class ClientHandler(Handler):
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
        self.on_stop()
        if self.link:
            self.link.close()
            self.link.free()
            self.link = None

    def _get_link_name(self):
        return "%s:%d" % (self.name, self.iteration)

    def on_start(self):
        assert False, "Subclass must override this!"

    def on_stop(self):
        pass

    def on_link_remote_close(self, event):
        _link = event.link
        if EndpointStateHandler.is_local_closed(_link):
            return DELEGATED
        _link.close()
        _condition = _link.remote_condition
        _connection = event.connection
        if _condition:
            logging.error("%s: link detached name:%s ref:%s %s:%s",
                          _connection.container,
                          _link.name,
                          _condition.name,
                          _connection.remote_container,
                          _condition.description)
        else:
            logging.error("%s: link detached name=%s ref:%s",
                          _connection.container,
                          _link.name,
                          _connection.remote_container)
        _link.free()
        if _condition and _condition.name in self.fatal_conditions:
            _connection.close()
        elif _link.__eq__(self.link):
            self.link = None
            event.reactor.schedule(2.0, self)

    def on_timer_task(self, event):
        if self.link is None:
            self.start(self.container)

class ReceiverHandler(ClientHandler):
    def __init__(self, handler, source, factory, selector=None, prefetch=300):
        super(ReceiverHandler, self).__init__("recv")
        self.handler = handler
        self.source = source
        self.factory = factory
        self.selector = selector
        self.offset = None
        self.handlers = []
        if prefetch:
            self.handlers.append(CFlowController(prefetch))
        self.handlers.append(IncomingMessageHandler(True, self))

    def on_start(self):
        if self.offset:
            self.selector = OffsetUtil.selector(self.offset)
        self.link = self.container.create_receiver(
            self.container.shared_connection,
            self.source,
            name=self._get_link_name(),
            handler=self,
            options=self.selector)

    def on_message(self, event):
        _message = event.message
        _event = self.factory(_message)
        self.handler.on_event_data(_event)
        self.offset = _message.annotations["x-opt-offset"]

    def on_link_local_open(self, event):
        logging.info("%s: link local open. name=%s entity=%s offset=%s",
                     event.connection.container,
                     event.link.name,
                     self.source,
                     self.selector.filter_set["selector"].value)

    def on_link_remote_open(self, event):
        logging.info("%s: link remote open. name=%s entity=%s",
                     event.connection.container,
                     event.link.name,
                     self.source)

class SenderHandler(ClientHandler):
    def __init__(self, partition=None):
        super(SenderHandler, self).__init__("send")
        self.partition = partition
        self.handlers = [OutgoingMessageHandler(False, self)]
        self.messages = Queue.Queue()
        self.count = 0
        self.injector = None

    def _get_target(self):
        _target = self.container.address.path
        if self.partition:
            _target += "/Partitions/" + self.partition
        return _target

    def send(self, message):
        self.injector.trigger(ClientEvent(self, "message", subject=message))

    def on_start(self):
        if self.injector is None:
            self.injector = EventInjector()
            self.container.selectable(self.injector)
        self.link = self.container.create_sender(
            self.container.shared_connection,
            self._get_target(),
            name=self._get_link_name(),
            handler=self)

    def on_stop(self):
        if self.injector is not None:
            self.injector.close()

    def on_link_local_open(self, event):
        logging.info("%s: link local open. entity=%s", event.connection.container, self._get_target())

    def on_link_remote_open(self, event):
        logging.info("%s: link remote open. entity=%s", event.connection.container, self._get_target())

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

class OffsetUtil(object):
    @classmethod
    def selector(cls, value, inclusive=False):
        if isinstance(value, datetime.datetime):
            _epoch = datetime.datetime.utcfromtimestamp(0)
            _ms = timestamp((value - _epoch).total_seconds() * 1000.0)
            return Selector(u"amqp.annotation.x-opt-enqueued-time > '" + str(_ms) + "'")
        elif isinstance(value, timestamp):
            return Selector(u"amqp.annotation.x-opt-enqueued-time > '" + str(value) + "'")
        else:
            _op = ">=" if inclusive else ">"
            return Selector(u"amqp.annotation.x-opt-offset " + _op + " '" + utf82unicode(value) + "'")


class ClientEvent(ApplicationEvent):
    def __init__(self, client, typename, subject=None):
        super(ClientEvent, self).__init__("client_event", subject=subject)
        self.typename = typename
        self.client = client
