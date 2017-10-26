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
    def __init__(self):
        super(AsyncReceiver, self).__init__(False)
        self.loop = asyncio.get_event_loop()
        self.messages = queue.Queue()
        self.lock = Lock()
        self.link = None
        self.waiter = None
        self.delivered = 0

    def on_start(self, link):
        self.link = link
        self.link.flow(300)

    def on_message(self, event):
        """ Handle message received event """
        _message = event.message
        _event = EventData.create(_message)
        _waiter = None
        with self.lock:
            if self.waiter is None:
                self.messages.put(_event)
                return
            _waiter = self.waiter
            self.waiter = None
            self._on_delivered(1)
        self.offset = _event.offset
        self.loop.call_soon_threadsafe(_waiter.set_result, [_event])

    def on_event_data(self, event_data):
        pass

    async def receive(self, count):
        """
        Receive events asynchronously.

        @param count: max number of events to receive. The result may be less.

        """
        _waiter = None
        _list = []
        with self.lock:
            _deq = 0
            while not self.messages.empty() and _deq < count:
                _list.append(self.messages.get())
                _deq = _deq + 1
            if _list:
                self._on_delivered(_deq)
                return _list
            self.waiter = self.loop.create_future()
            _waiter = self.waiter
        await _waiter
        return _waiter.result()

    def _on_delivered(self, count):
        self.delivered = self.delivered + count
        if self.delivered >= 100:
            self.link.flow(self.delivered)
            self.delivered = 0
