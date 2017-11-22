# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Internal implementations of protocol handlers. It should be implementing send/recv over AMQP
for general purposes. Keep any service/broker specifics out of this file.

"""

# pylint: disable=line-too-long
# pylint: disable=C0111
# pylint: disable=W0613
# pylint: disable=W0702

import logging
from proton import DELEGATED, generate_uuid
from proton.handlers import Handler, EndpointStateHandler
from proton.handlers import IncomingMessageHandler
from proton.handlers import CFlowController, OutgoingMessageHandler

try:
    import Queue
except:
    import queue as Queue

class ClientHandler(Handler):
    def __init__(self, prefix, client):
        super(ClientHandler, self).__init__()
        self.name = "%s-%s" % (prefix, str(generate_uuid())[:8])
        self.client = client
        self.link = None
        self.iteration = 0
        self.fatal_conditions = ["amqp:unauthorized-access", "amqp:not-found"]

    def start(self):
        self.iteration += 1
        self.on_start()

    def stop(self):
        self.on_stop()
        if self.link:
            self.link.close()
            self.link = None
        self.client = None

    def _get_link_name(self):
        return "%s:%d" % (self.name, self.iteration)

    def on_start(self):
        assert False, "Subclass must override this!"

    def on_stop(self):
        pass

    def on_link_remote_close(self, event):
        link = event.link
        if EndpointStateHandler.is_local_closed(link):
            return DELEGATED
        link.close()
        condition = link.remote_condition
        connection = event.connection
        if condition:
            logging.error("%s: link detached name:%s ref:%s %s:%s",
                          connection.container,
                          link.name,
                          condition.name,
                          connection.remote_container,
                          condition.description)
        else:
            logging.error("%s: link detached name=%s ref:%s",
                          connection.container,
                          link.name,
                          connection.remote_container)
        if condition and condition.name in self.fatal_conditions:
            connection.close()
        elif link.__eq__(self.link):
            self.link = None
            event.reactor.schedule(2.0, self)

    def on_timer_task(self, event):
        if self.link is None:
            self.start()

class ReceiverHandler(ClientHandler):
    def __init__(self, client, receiver, source, selector):
        super(ReceiverHandler, self).__init__("recv", client)
        self.receiver = receiver
        self.source = source
        self.selector = selector
        self.handlers = []
        if receiver.prefetch:
            self.handlers.append(CFlowController(receiver.prefetch))
        self.handlers.append(IncomingMessageHandler(True, self))

    def on_start(self):
        self.link = self.client.container.create_receiver(
            self.client.connection,
            self.source,
            name=self._get_link_name(),
            handler=self,
            options=self.receiver.selector(self.selector))
        self.receiver.on_start(self.link)

    def on_stop(self):
        self.receiver.on_stop()

    def on_message(self, event):
        self.receiver.on_message(event)

    def on_link_local_open(self, event):
        logging.info("%s: link local open. name=%s source=%s offset=%s",
                     event.connection.container,
                     event.link.name,
                     self.source,
                     self.selector.filter_set["selector"].value)

    def on_link_remote_open(self, event):
        logging.info("%s: link remote open. name=%s source=%s",
                     event.connection.container,
                     event.link.name,
                     self.source)

class SenderHandler(ClientHandler):
    class MessageTransfer(object):
        def __init__(self, message, handler):
            self.message = message
            self.handler = handler
            self.outcome = None

        def complete(self, outcome):
            if self.handler:
                self.handler.on_outcome(outcome)

    def __init__(self, client, sender, target):
        super(SenderHandler, self).__init__("send", client)
        self.sender = sender
        self.target = target
        self.handlers = [OutgoingMessageHandler(True, self)]
        self.transfers = Queue.Queue()
        self.deliveries = {}

    def send(self, message, handler=None):
        transfer = SenderHandler.MessageTransfer(message, handler)
        self.client.injector.trigger(self.on_transfer, transfer)

    def on_start(self):
        self.link = self.client.container.create_sender(
            self.client.connection,
            self.target,
            name=self._get_link_name(),
            handler=self)
        self.sender.on_start(self.link)

    def on_link_local_open(self, event):
        logging.info("%s: link local open. name=%s target=%s",
                     event.connection.container,
                     event.link.name,
                     self.target)

    def on_link_remote_open(self, event):
        logging.info("%s: link remote open. name=%s",
                     event.connection.container,
                     event.link.name)

    def on_transfer(self, transfer):
        self.transfers.put(transfer)
        self.on_sendable(None)

    def on_sendable(self, event):
        while self.link.credit and not self.transfers.empty():
            transfer = self.transfers.get(False)
            delivery = transfer.message.send(self.link)
            self.deliveries[delivery] = transfer

    def on_delivery(self, event):
        logging.info("on_delivery")
        dlv = event.delivery
        if dlv.updated:
            transfer = self.deliveries.pop(dlv, None)
            if transfer:
                transfer.complete(dlv.remote_state)
            dlv.settle()

class SessionPolicy(object):
    def __init__(self):
        self._session = None

    def session(self, context):
        if not self._session:
            self._session = context.session()
            self._session.open()
        return self._session

    def close(self):
        if self._session:
            self._session.close()
            self._session = None
