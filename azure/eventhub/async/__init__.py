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
import time

from azure import eventhub
from azure.eventhub import (
    Sender,
    Receiver,
    EventHubClient,
    EventData,
    EventHubError)

from uamqp.async import SASTokenAsync
from uamqp.async import ConnectionAsync
from uamqp import Message, AMQPClientAsync, SendClientAsync, ReceiveClientAsync, Source
from uamqp import constants, types

log = logging.getLogger(__name__)


class EventHubClientAsync(EventHubClient):
    """
    The L{EventHubClient} class defines a high level interface for sending
    events to and receiving events from the Azure Event Hubs service.
    """
    def _create_auth(self, auth_uri, username, password):
        return SASTokenAsync.from_shared_access_key(auth_uri, username, password)

    def _create_connection_async(self):
        if not self.connection:
            log.info("{}: Creating connection with address={}".format(
                self.container_id, self.address.geturl()))
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
        log.info("{}: Starting {} clients".format(self.container_id, len(self.clients)))
        self._create_connection_async()
        for client in self.clients:
            await client.open_async(connection=self.connection)
        return self

    async def stop_async(self):
        """
        Stop the client.
        """
        log.info("{}: Stopping {} clients".format(self.container_id, len(self.clients)))
        self.stopped = True
        await self._close_clients_async()
        await self._close_connection_async()

    async def get_eventhub_info_async(self):
        eh_name = self.address.path.lstrip('/')
        target = "amqps://{}/{}".format(self.address.hostname, eh_name)
        async with AMQPClientAsync(target, auth=self.auth, debug=self.debug) as mgmt_client:
            mgmt_msg = Message(application_properties={'name': eh_name})
            response = await mgmt_client.mgmt_request_async(
                mgmt_msg,
                constants.READ_OPERATION,
                op_type=b'com.microsoft:eventhub',
                status_code_field=b'status-code',
                description_fields=b'status-description')
            return response.get_data()

    def add_async_receiver(self, consumer_group, partition, offset=None, prefetch=300, loop=None):
        """
        Registers a L{Receiver} to process L{EventData} objects received from an Event Hub partition.

        @param receiver: receiver to process the received event data. It must
        override the 'on_event_data' method to handle incoming events.

        @param consumer_group: the consumer group to which the receiver belongs.

        @param partition: the id of the event hub partition.

        @param offset: the initial L{Offset} to receive events.
        """
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, self.address.path, consumer_group, partition)
        source = Source(source_url)
        if offset is not None:
            source.set_filter(offset.selector())
        handler = AsyncReceiver(self, source, prefetch=prefetch, loop=loop)
        self.clients.append(handler._handler)
        return handler

    def add_async_epoch_receiver(self, consumer_group, partition, epoch, prefetch=300, loop=None):
        """
        Registers a L{Receiver} to process L{EventData} objects received from an Event Hub partition.

        @param receiver: receiver to process the received event data. It must
        override the 'on_event_data' method to handle incoming events.

        @param consumer_group: the consumer group to which the receiver belongs.

        @param partition: the id of the event hub partition.

        @param offset: the initial L{Offset} to receive events.
        """
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, self.address.path, consumer_group, partition)
        handler = AsyncReceiver(self, source_url, prefetch=prefetch, epoch=epoch, loop=loop)
        self.clients.append(handler._handler)
        return handler

    def add_async_sender(self, partition=None, loop=None):
        """
        Registers a L{Sender} to publish L{EventData} objects to an Event Hub or one of its partitions.

        @param sender: sender to publish event data.

        @param partition: the id of the destination event hub partition. If not specified, events will
        be distributed across partitions based on the default distribution logic.
        """
        target = "amqps://{}{}".format(self.address.hostname, self.address.path)
        if partition:
            target += "/Partitions/" + partition
        handler = AsyncSender(self, target, loop=loop)
        self.clients.append(handler._handler)
        return handler

class AsyncSender(Sender):
    """
    Implements the async API of a L{Sender}.
    """
    def __init__(self, client, target, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._handler = SendClientAsync(
            target,
            auth=client.auth,
            debug=client.debug,
            msg_timeout=Sender.TIMEOUT,
            loop=self.loop)
        self._outcome = None
        self._condition = None

    async def send(self, event_data):
        """
        Sends an event data.

        @param event_data: the L{EventData} to be sent.
        """
        event_data.message.on_send_complete = self.on_outcome
        await self._handler.send_message_async(event_data.message)
        if self._outcome != constants.MessageSendResult.Ok:
            raise Sender._error(self._outcome, self._condition)

    def on_result(self, outcome, condition):
        """
        Called when the send task is completed.
        """
        AsyncSender._error(outcome, condition)

class AsyncReceiver(Receiver):
    """
    Implements the async API of a L{Receiver}.
    """
    def __init__(self, client, source, prefetch=300, epoch=None, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.offset = None
        self._callback = None
        self.prefetch = prefetch
        self.epoch = epoch
        self.delivered = 0
        properties = None
        if epoch:
            properties = {types.AMQPSymbol(self._epoch): types.AMQPLong(int(epoch))}
        self._handler = ReceiveClientAsync(
            source,
            auth=client.auth,
            debug=client.debug,
            prefetch=self.prefetch,
            link_properties=properties,
            timeout=self.timeout,
            loop=self.loop)

    def on_message(self, event):
        """ Handle message received event """
        self.delivered += 1
        event_data = EventData.create(event)
        if self._callback:
            self._callback(event_data)
        self.offset = event_data.offset
        return event_data

    async def _receive_gen(self, batch_size, timeout):
        """
        Receive events asynchronously.
        @param count: max number of events to receive. The result may be less.

        Returns a list of L{EventData} objects. An empty list means no data is
        available. None means the receiver is closed (eof).
        """
        timeout_ms = 1000 * timeout if timeout else 0
        if batch_size:
            message_iter = await self._handler.receive_message_batch_async(
                batch_size=batch_size,
                on_message_received=self.on_message,
                timeout=timeout_ms)
            for event_data in message_iter:
                yield event_data
        else:
            receive_timeout = time.time() + timeout if timeout else None
            message_iter = await self._handler.receive_message_batch_async(
                on_message_received=self.on_message,
                timeout=timeout_ms)
            while message_iter and (not receive_timeout or time.time() < receive_timeout):
                for event_data in message_iter:
                    yield event_data
                if receive_timeout:
                    timeout_ms = int((receive_timeout - time.time()) * 1000)
                message_iter = await self._handler.receive_message_batch_async(
                    on_message_received=self.on_message,
                    timeout=timeout_ms)

    def receive(self, batch_size=None, callback=None, timeout=None):
        self._callback = callback
        return self._receive_gen(batch_size, timeout)