# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Async APIs.
"""

import logging
import queue
import asyncio
from threading import Lock
from eventhubs import Sender, Receiver, EventData, EventHubError

log = logging.getLogger("eventhubs")

class AsyncSender(Sender):
    """
    Implements the async API of a L{Sender}.
    """
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()

    async def send(self, event_data):
        """
        Sends an event data.

        @param event_data: the L{EventData} to be sent.
        """
        self._check()
        task = self.loop.create_future()
        self._handler.send(event_data.message, self.on_result, task)
        error = await task
        if error:
            raise error

    def on_result(self, task, outcome, condition):
        """
        Called when the send task is completed.
        """
        self.loop.call_soon_threadsafe(task.set_result, self._error(outcome, condition))

class AsyncReceiver(Receiver):
    """
    Implements the async API of a L{Receiver}.
    """
    def __init__(self, prefetch=300, loop=None):
        super(AsyncReceiver, self).__init__(False)
        self.loop = loop or asyncio.get_event_loop()
        self.messages = queue.Queue()
        self.lock = Lock()
        self.link = None
        self.waiter = None
        self.prefetch = prefetch
        self.credit = 0
        self.delivered = 0
        self.closed = False

    def on_start(self, link, iteration):
        """
        Called when the receiver is started or restarted.
        """
        self.link = link
        self.credit = self.prefetch
        self.delivered = 0
        self.link.flow(self.credit)

    def on_stop(self, closed):
        """
        Called when the receiver is stopped.
        """
        self.closed = closed
        self.link = None
        while not self.messages.empty():
            self.messages.get()

    def on_message(self, event):
        """ Handle message received event """
        event_data = EventData.create(event.message)
        self.offset = event_data.offset
        waiter = None
        with self.lock:
            self.messages.put(event_data)
            self.credit -= 1
            self._check_flow()
            if self.credit == 0:
                # workaround before having an EventInjector
                event.reactor.schedule(0.1, self)
            if self.waiter is None:
                return
            waiter = self.waiter
            self.waiter = None
        self.loop.call_soon_threadsafe(waiter.set_result, None)

    def on_event_data(self, event_data):
        pass

    def on_timer_task(self, event):
        """ Handle timer event """
        with self.lock:
            self._check_flow()
            if self.waiter is None and self.messages.qsize() > 0:
                event.reactor.schedule(0.1, self)

    async def receive(self, count):
        """
        Receive events asynchronously.
        @param count: max number of events to receive. The result may be less.

        Returns a list of L{EventData} objects. An empty list means no data is
        available. None means the receiver is closed (eof).
        """
        waiter = None
        batch = []
        while not self.closed:
            with self.lock:
                size = self.messages.qsize()
                while size > 0 and count > 0:
                    batch.append(self.messages.get())
                    size -= 1
                    count -= 1
                    self.delivered += 1
                if batch:
                    return batch
                self.waiter = self.loop.create_future()
                waiter = self.waiter
            await waiter
        return None

    def _check_flow(self):
        if self.delivered >= 100 and self.link:
            self.link.flow(self.delivered)
            log.debug("%s: issue link credit %d", self.link.connection.container, self.delivered)
            self.credit += self.delivered
            self.delivered = 0
