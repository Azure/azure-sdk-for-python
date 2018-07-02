# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import asyncio
import time
import datetime

from uamqp import constants, types, errors
from uamqp.authentication import SASTokenAsync
from uamqp import (
    Message,
    Source,
    ConnectionAsync,
    AMQPClientAsync,
    SendClientAsync,
    ReceiveClientAsync)

from azure.eventhub import (
    Sender,
    Receiver,
    EventHubClient,
    EventData,
    EventHubError)

from .sender_async import AsyncSender
from .receiver_async import AsyncReceiver


log = logging.getLogger(__name__)


class EventHubClientAsync(EventHubClient):
    """
    The EventHubClient class defines a high level interface for asynchronously
    sending events to and receiving events from the Azure Event Hubs service.
    """

    def _create_auth(self, auth_uri, username, password):  # pylint: disable=no-self-use
        """
        Create an ~uamqp.authentication.cbs_auth_async.SASTokenAuthAsync instance to authenticate
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
        Create a new ~uamqp._async.connection_async.ConnectionAsync instance that will be shared between all
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

        :rtype: ~azure.eventhub._async.EventHubClientAsync
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

        :rtype: dict
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
            eh_info = response.get_data()
            output = {}
            if eh_info:
                output['name'] = eh_info[b'name'].decode('utf-8')
                output['type'] = eh_info[b'type'].decode('utf-8')
                output['created_at'] = datetime.datetime.fromtimestamp(float(eh_info[b'created_at'])/1000)
                output['partition_count'] = eh_info[b'partition_count']
                output['partition_ids'] = [p.decode('utf-8') for p in eh_info[b'partition_ids']]
            return output

    def add_async_receiver(self, consumer_group, partition, offset=None, prefetch=300, loop=None):
        """
        Add an async receiver to the client for a particular consumer group and partition.

        :param consumer_group: The name of the consumer group.
        :type consumer_group: str
        :param partition: The ID of the partition.
        :type partition: str
        :param offset: The offset from which to start receiving.
        :type offset: ~azure.eventhub.common.Offset
        :param prefetch: The message prefetch count of the receiver. Default is 300.
        :type prefetch: int
        :rtype: ~azure.eventhub._async.receiver_async.ReceiverAsync
        """
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, self.address.path, consumer_group, partition)
        source = Source(source_url)
        if offset is not None:
            source.set_filter(offset.selector())
        handler = AsyncReceiver(self, source, prefetch=prefetch, loop=loop)
        self.clients.append(handler._handler)  # pylint: disable=protected-access
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
        :rtype: ~azure.eventhub._async.receiver_async.ReceiverAsync
        """
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, self.address.path, consumer_group, partition)
        handler = AsyncReceiver(self, source_url, prefetch=prefetch, epoch=epoch, loop=loop)
        self.clients.append(handler._handler)  # pylint: disable=protected-access
        return handler

    def add_async_sender(self, partition=None, loop=None):
        """
        Add an async sender to the client to send ~azure.eventhub.common.EventData object
        to an EventHub.

        :param partition: Optionally specify a particular partition to send to.
         If omitted, the events will be distributed to available partitions via
         round-robin.
        :type partition: str
        :rtype: ~azure.eventhub._async.sender_async.SenderAsync
        """
        target = "amqps://{}{}".format(self.address.hostname, self.address.path)
        handler = AsyncSender(self, target, partition=partition, loop=loop)
        self.clients.append(handler._handler)  # pylint: disable=protected-access
        return handler
