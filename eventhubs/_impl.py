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
import time
import os
from proton import PN_PYREF, DELEGATED, generate_uuid
from proton import Delivery, EventBase, Condition
from proton.handlers import Handler, EndpointStateHandler
from proton.handlers import IncomingMessageHandler
from proton.handlers import CFlowController, OutgoingMessageHandler
from proton.reactor import EventType, EventInjector

try:
    import Queue
except:
    import queue as Queue

log = logging.getLogger("eventhubs")


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

    def stop(self, condition):
        self.on_stop(condition)
        if self.link:
            self.link.close()
            self.link.free()
            self.link = None

    def _get_link_name(self):
        return "%s:%d" % (self.name, self.iteration)

    def on_start(self):
        assert False, "Subclass must override this!"


    def on_link_remote_close(self, event):
        link = event.link
        if EndpointStateHandler.is_local_closed(link):
            return DELEGATED
        link.close()
        link.free()
        condition = link.remote_condition
        connection = event.connection
        if condition:
            log.error("%s: link detached name:%s ref:%s %s:%s",
                          connection.container,
                          link.name,
                          condition.name,
                          connection.remote_container,
                          condition.description)
        else:
            log.error("%s: link detached name=%s ref:%s",
                          connection.container,
                          link.name,
                          connection.remote_container)
        self.on_link_closed(condition)
        if condition and condition.name in self.fatal_conditions:
            connection.close()
        elif link == self.link:
            self.link = None
            event.reactor.schedule(1.0, self)
