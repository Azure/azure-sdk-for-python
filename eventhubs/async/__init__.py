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
from threading import Lock, Event
import eventhubs
from eventhubs import Sender, Receiver, EventHubClient, EventData, EventHubError

from uamqp.async import SASTokenAsync
from uamqp.async import ConnectionAsync
from uamqp import SendClientAsync, ReceiveClientAsync
from uamqp import constants
log = logging.getLogger("eventhubs")


class EventHubClientAsync(EventHubClient):
    """
    The L{EventHubClient} class defines a high level interface for sending
    events to and receiving events from the Azure Event Hubs service.
    """
    def _create_auth(self, auth_uri, username, password):
        return SASTokenAsync.from_shared_access_key(auth_uri, username, password)

    def _create_connection_async(self):
        if not self.connection:
            log.info("%s: client starts address=%s", self.container_id, self.address)
            self.connection = ConnectionAsync(
                self.address.hostname,
                self.auth,
                container_id=self.container_id,
                properties=self._create_properties(),
                debug=self.debug)

    async def _close_connection_async(self):
        if self.connection:
            await self.connection.destroy_async()
            self.connection = None

    async def _close_clients_async(self):
        for client in self.clients:
            await client.close_async()

    async def run_async(self):
        log.info("%s: Starting", self.container_id)
        self._create_connection_async()
        for client in self.clients:
            await client.open_async(connection=self.connection)
        return self

    async def stop_async(self):
        """
        Stop the client.
        """
        log.info("%s: on_stop_client", self.container_id)
        self.stopped = True
        await self._close_clients_async()
        await self._close_connection_async()

    def add_async_receiver(self, consumer_group, partition, offset=None):
        """
        Registers a L{Receiver} to process L{EventData} objects received from an Event Hub partition.

        @param receiver: receiver to process the received event data. It must
        override the 'on_event_data' method to handle incoming events.

        @param consumer_group: the consumer group to which the receiver belongs.

        @param partition: the id of the event hub partition.

        @param offset: the initial L{Offset} to receive events.
        """
        source_url = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, self.address.path, consumer_group, partition)
        source = Source(source_url)
        if offset is not None:
            source.set_filter(offset.selector())
        handler = AsyncReceiver(self, source)
        self.clients.append(handler._handler)
        return handler

    def add_async_sender(self, loop=None, partition=None):
        """
        Registers a L{Sender} to publish L{EventData} objects to an Event Hub or one of its partitions.

        @param sender: sender to publish event data.

        @param partition: the id of the destination event hub partition. If not specified, events will
        be distributed across partitions based on the default distribution logic.
        """
        target = "amqps://{}/{}".format(self.address.hostname, self.address.path)
        if partition:
            target += "/Partitions/" + partition
        handler = AsyncSender(self, target)
        self.clients.append(handler._handler)
        return handler

class AsyncSender(Sender):
    """
    Implements the async API of a L{Sender}.
    """
    def __init__(self, client, target, loop=None):
        self._handler = SendClientAsync(target, auth=client.auth, debug=client.debug, msg_timeout=Sender.TIMEOUT)
        self._outcome = None
        self._condition = None
        self.loop = loop or asyncio.get_event_loop()

    async def send(self, event_data):
        """
        Sends an event data.

        @param event_data: the L{EventData} to be sent.
        """
        event_data.message.on_send_complete = self.on_outcome
        await self._handler.send_message_async(event_data.message)
        if self._outcome != constants.MessageSendResult.Ok:
            raise Sender._error(self._outcome, self._condition)

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
