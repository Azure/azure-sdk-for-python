# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Async APIs.
"""

import queue
import asyncio
from threading import Lock
from eventhubs import Receiver, EventData
class AsyncReceiver(Receiver):
    """
    Implements the async API of a L{Receiver}.
    """
    def __init__(self, event_loop=None, prefetch=300):
        super(AsyncReceiver, self).__init__(False)
        self.loop = event_loop or asyncio.get_event_loop()
        self.messages = queue.Queue()
        self.lock = Lock()
        self.link = None
        self.waiter = None
        self.credit = prefetch
        self.delivered = 0

    def on_start(self, link):
        self.link = link
        self.link.flow(300)

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
        """
        waiter = None
        batch = []
        while True:
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

    def _check_flow(self):
        if self.delivered >= 100:
            self.link.flow(self.delivered)
            self.credit += self.delivered
            self.delivered = 0
