# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

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
from uamqp import constants, types, errors

log = logging.getLogger(__name__)


class EventHubClientAsync(EventHubClient):
    """
    The EventHubClient class defines a high level interface for asynchronously
    sending events to and receiving events from the Azure Event Hubs service.
    """

    def _create_auth(self, auth_uri, username, password):
        """
        Create an ~uamqp.authentication.SASTokenAuthAsync instance to authenticate
        the session.

        :param auth_uri: The URI to authenticate against.
        :type auth_uri: str
        :param username: The name of the shared access policy.
        :type username: str
        :param password: The shared access key.
        :type password: str
        """
        return SASTokenAsync.from_shared_access_key(auth_uri, username, password)

    def _create_connection_async(self):
        """
        Create a new ~uamqp.ConnectionAsync instance that will be shared between all
        AsyncSender/AsyncReceiver clients.
        """
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
        """
        Close and destroy the connection async.
        """
        if self.connection:
            await self.connection.destroy_async()
            self.connection = None

    async def _close_clients_async(self):
        """
        Close all open AsyncSender/AsyncReceiver clients.
        """
        for client in self.clients:
            await client.close_async()

    async def run_async(self):
        """
        Run the EventHubClient asynchronously.
        Opens the connection and starts running all AsyncSender/AsyncReceiver clients.

        :returns: ~azure.eventhub.EventHubClientAsync
        """
        log.info("{}: Starting {} clients".format(self.container_id, len(self.clients)))
        self._create_connection_async()
        for client in self.clients:
            await client.open_async(connection=self.connection)
        return self

    async def stop_async(self):
        """
        Stop the EventHubClient and all its Sender/Receiver clients.
        """
        log.info("{}: Stopping {} clients".format(self.container_id, len(self.clients)))
        self.stopped = True
        await self._close_clients_async()
        await self._close_connection_async()

    async def get_eventhub_info_async(self):
        """
        Get details on the specified EventHub async.
        :returns: dict
        """
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
        Add an async receiver to the client for a particular consumer group and partition.
        :param consumer_group: The name of the consumer group.
        :type consumer_group: str
        :param partition: The ID of the partition.
        :type partition: str
        :param offset: The offset from which to start receiving.
        :type offset: ~azure.eventhub.Offset
        :param prefetch: The message prefetch count of the receiver. Default is 300.
        :type prefetch: int
        :returns: ~azure.eventhub.ReceiverAsync
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
        Add an async receiver to the client with an epoch value. Only a single epoch receiver
        can connect to a partition at any given time - additional epoch receivers must have
        a higher epoch value or they will be rejected. If a 2nd epoch receiver has
        connected, the first will be closed.
        :param consumer_group: The name of the consumer group.
        :type consumer_group: str
        :param partition: The ID of the partition.
        :type partition: str
        :param epoch: The epoch value for the receiver.
        :type epoch: int
        :param prefetch: The message prefetch count of the receiver. Default is 300.
        :type prefetch: int
        :returns: ~azure.eventhub.ReceiverAsync
        """
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, self.address.path, consumer_group, partition)
        handler = AsyncReceiver(self, source_url, prefetch=prefetch, epoch=epoch, loop=loop)
        self.clients.append(handler._handler)
        return handler

    def add_async_sender(self, partition=None, loop=None):
        """
        Add an async sender to the client to send ~azure.eventhub.EventData object
        to an EventHub.
        :param partition: Optionally specify a particular partition to send to.
         If omitted, the events will be distributed to available partitions via
         round-robin
        :type partition: str
        :returns: ~azure.eventhub.SenderAsync
        """
        target = "amqps://{}{}".format(self.address.hostname, self.address.path)
        handler = AsyncSender(self, target, partition=partition, loop=loop)
        self.clients.append(handler._handler)
        return handler

class AsyncSender(Sender):
    """
    Implements the async API of a Sender.
    """

    def __init__(self, client, target, partition=None, loop=None):
        """
        Instantiate an EventHub event SenderAsync client.
        :param client: The parent EventHubClient.
        :type client: ~azure.eventhub.EventHubClient.
        :param target: The URI of the EventHub to send to.
        :type target: str
        :param loop: An event loop.
        """
        self.partition = partition
        if partition:
            target += "/Partitions/" + partition
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
        Sends an event data and asynchronously waits until 
        acknowledgement is received or operation times out.
        :param event_data: The event to be sent.
        :type event_data: ~azure.eventhub.EventData
        :raises: ~azure.eventhub.EventHubError if the message fails to
         send.
        """
        if event_data.partition_key and self.partition:
            raise ValueError("EventData partition key cannot be used with a partition sender.")
        event_data.message.on_send_complete = self._on_outcome
        try:
            await self._handler.send_message_async(event_data.message)
            if self._outcome != constants.MessageSendResult.Ok:
                raise Sender._error(self._outcome, self._condition)
        except Exception as e:
            raise EventHubError("Send failed: {}".format(e))


class AsyncReceiver(Receiver):
    """
    Implements the async API of a Receiver.
    """

    def __init__(self, client, source, prefetch=300, epoch=None, loop=None):
        """
        Instantiate an async receiver.
        :param client: The parent EventHubClient.
        :type client: ~azure.eventhub.EventHubClient
        :param source: The source EventHub from which to receive events.
        :type source: ~uamqp.Source
        :param prefetch: The number of events to prefetch from the service
         for processing. Default is 300.
        :type prefetch: int
        :param epoch: An optional epoch value.
        :type epoch: int
        :param loop: An event loop.
        """
        self.loop = loop or asyncio.get_event_loop()
        self.offset = None
        self._callback = None
        self.prefetch = prefetch
        self.epoch = epoch
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

    async def receive(self, max_batch_size=None, callback=None, timeout=None):
        """
        Receive events asynchronously from the EventHub.
        :param max_batch_size: Receive a batch of events. Batch size will
         be up to the maximum specified, but will return as soon as service
         returns no new events. If combined with a timeout and no events are
         retrieve before the time, the result will be empty. If no batch
         size is supplied, the prefetch size will be the maximum.
        :type max_batch_size: int
        :param callback: A callback to be run for each received event. This must
         be a function that accepts a single argument - the event data. This callback
         will be run before the message is returned in the result generator.
        :type callback: func[~azure.eventhub.EventData]
        :returns: list[~azure.eventhub.EventData]
        """
        try:
            self._callback = callback
            timeout_ms = 1000 * timeout if timeout else 0
            batch = await self._handler.receive_message_batch_async(
                max_batch_size=max_batch_size,
                on_message_received=self.on_message,
                timeout=timeout_ms)
            return batch
        except errors.AMQPConnectionError as e:
            message = "Failed to open receiver: {}".format(e)
            message += "\nPlease check that the partition key is valid "
            if self.epoch:
                message += "and that a higher epoch receiver is " \
                           "not already running for this partition."
            else:
                message += "and whether an epoch receiver is " \
                           "already running for this partition."
            raise EventHubError(message)
        except Exception as e:
            raise EventHubError("Receive failed: {}".format(e))