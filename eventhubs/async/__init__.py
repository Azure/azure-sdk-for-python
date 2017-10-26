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
from eventhubs import Receiver

class AsyncReceiver(Receiver):
    """
    Implements the async API of a L{Receiver}.
    """
    def __init__(self):
        super(AsyncReceiver, self).__init__()
        self.loop = asyncio.get_event_loop()
        self.messages = queue.Queue()
        self.lock = Lock()
        self.waiter = None

    def on_event_data(self, event_data):
        _waiter = None
        with self.lock:
            if self.waiter is None:
                self.messages.put(event_data)
                return
            _waiter = self.waiter
            self.waiter = None
        self.loop.call_soon_threadsafe(_waiter.set_result, [event_data])

    async def receive(self, count):
        """
        Receive events asynchronously.

        @param count: max number of events to receive. The result may be less.

        """
        _waiter = None
        _list = []
        with self.lock:
            while not self.messages.empty() and count > 0:
                _list.append(self.messages.get())
                count = count - 1
            if _list:
                return _list
            self.waiter = self.loop.create_future()
            _waiter = self.waiter
        await _waiter
        return _waiter.result()
