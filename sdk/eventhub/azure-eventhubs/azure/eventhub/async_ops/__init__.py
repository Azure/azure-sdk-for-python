# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import asyncio
import time
import datetime
from urllib.parse import urlparse, unquote_plus, urlencode, quote_plus

from uamqp import authentication, constants, types, errors
from uamqp import (
    Message,
    ConnectionAsync,
    AMQPClientAsync,
    SendClientAsync,
    ReceiveClientAsync)

from azure.eventhub.common import parse_sas_token
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

    Example:
        .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
            :start-after: [START create_eventhub_client_async]
            :end-before: [END create_eventhub_client_async]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the Event Hub client async.

    """

    def _create_auth(self, username=None, password=None):
        """
        Create an ~uamqp.authentication.cbs_auth_async.SASTokenAuthAsync instance to authenticate
        the session.

        :param username: The name of the shared access policy.
        :type username: str
        :param password: The shared access key.
        :type password: str
        """
        if self.sas_token:
            token = self.sas_token() if callable(self.sas_token) else self.sas_token
            try:
                expiry = int(parse_sas_token(token)['se'])
            except (KeyError, TypeError, IndexError):
                raise ValueError("Supplied SAS token has no valid expiry value.")
            return authentication.SASTokenAsync(
                self.auth_uri, self.auth_uri, token,
                expires_at=expiry,
                timeout=self.auth_timeout,
                http_proxy=self.http_proxy)

        username = username or self._auth_config['username']
        password = password or self._auth_config['password']
        if "@sas.root" in username:
            return authentication.SASLPlain(
                self.address.hostname, username, password, http_proxy=self.http_proxy)
        return authentication.SASTokenAsync.from_shared_access_key(
            self.auth_uri, username, password, timeout=self.auth_timeout, http_proxy=self.http_proxy)

    async def _close_clients_async(self):
        """
        Close all open AsyncSender/AsyncReceiver clients.
        """
        await asyncio.gather(*[c.close_async() for c in self.clients])

    async def _wait_for_client(self, client):
        try:
            while client.get_handler_state().value == 2:
                await client._handler._connection.work_async()  # pylint: disable=protected-access
        except Exception as exp:  # pylint: disable=broad-except
            await client.close_async(exception=exp)

    async def _start_client_async(self, client):
        try:
            if not client.running:
                await client.open_async()
        except Exception as exp:  # pylint: disable=broad-except
            log.info("Encountered error while starting handler: %r", exp)
            await client.close_async(exception=exp)
            log.info("Finished closing failed handler")

    async def _handle_redirect(self, redirects):
        if len(redirects) != len(self.clients):
            not_redirected = [c for c in self.clients if not c.redirected]
            _, timeout = await asyncio.wait([self._wait_for_client(c) for c in not_redirected], timeout=5)
            if timeout:
                raise EventHubError("Some clients are attempting to redirect the connection.")
            redirects = [c.redirected for c in self.clients if c.redirected]
        if not all(r.hostname == redirects[0].hostname for r in redirects):
            raise EventHubError("Multiple clients attempting to redirect to different hosts.")
        self._process_redirect_uri(redirects[0])
        await asyncio.gather(*[c.open_async() for c in self.clients])

    async def run_async(self):
        """
        Run the EventHubClient asynchronously.
        Opens the connection and starts running all AsyncSender/AsyncReceiver clients.
        Returns a list of the start up results. For a succcesful client start the
        result will be `None`, otherwise the exception raised.
        If all clients failed to start, then run will fail, shut down the connection
        and raise an exception.
        If at least one client starts up successfully the run command will succeed.

        :rtype: list[~azure.eventhub.common.EventHubError]

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_run_async]
                :end-before: [END eventhub_client_run_async]
                :language: python
                :dedent: 4
                :caption: Run the EventHubClient asynchronously.

        """
        log.info("%r: Starting %r clients", self.container_id, len(self.clients))
        tasks = [self._start_client_async(c) for c in self.clients]
        try:
            await asyncio.gather(*tasks)
            redirects = [c.redirected for c in self.clients if c.redirected]
            failed = [c.error for c in self.clients if c.error]
            if failed and len(failed) == len(self.clients):
                log.warning("%r: All clients failed to start.", self.container_id)
                raise failed[0]
            if failed:
                log.warning("%r: %r clients failed to start.", self.container_id, len(failed))
            elif redirects:
                await self._handle_redirect(redirects)
        except EventHubError:
            await self.stop_async()
            raise
        except Exception as exp:
            await self.stop_async()
            raise EventHubError(str(exp))
        return failed

    async def stop_async(self):
        """
        Stop the EventHubClient and all its Sender/Receiver clients.

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_stop]
                :end-before: [END eventhub_client_async_stop]
                :language: python
                :dedent: 4
                :caption: Stop the EventHubClient and all its Sender/Receiver clients.

        """
        log.info("%r: Stopping %r clients", self.container_id, len(self.clients))
        self.stopped = True
        await self._close_clients_async()

    async def get_eventhub_info_async(self):
        """
        Get details on the specified EventHub async.

        :rtype: dict
        """
        alt_creds = {
            "username": self._auth_config.get("iot_username"),
            "password":self._auth_config.get("iot_password")}
        try:
            mgmt_auth = self._create_auth(**alt_creds)
            mgmt_client = AMQPClientAsync(self.mgmt_target, auth=mgmt_auth, debug=self.debug)
            await mgmt_client.open_async()
            mgmt_msg = Message(application_properties={'name': self.eh_name})
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
        finally:
            await mgmt_client.close_async()

    def add_async_receiver(
            self, consumer_group, partition, offset=None, prefetch=300,
            operation=None, keep_alive=30, auto_reconnect=True, loop=None):
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
        :operation: An optional operation to be appended to the hostname in the source URL.
         The value must start with `/` character.
        :type operation: str
        :rtype: ~azure.eventhub.async_ops.receiver_async.ReceiverAsync

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START create_eventhub_client_async_receiver]
                :end-before: [END create_eventhub_client_async_receiver]
                :language: python
                :dedent: 4
                :caption: Add an async receiver to the client for a particular consumer group and partition.

        """
        path = self.address.path + operation if operation else self.address.path
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, path, consumer_group, partition)
        handler = AsyncReceiver(
            self, source_url, offset=offset, prefetch=prefetch,
            keep_alive=keep_alive, auto_reconnect=auto_reconnect, loop=loop)
        self.clients.append(handler)
        return handler

    def add_async_epoch_receiver(
            self, consumer_group, partition, epoch, prefetch=300,
            operation=None, keep_alive=30, auto_reconnect=True, loop=None):
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
        :operation: An optional operation to be appended to the hostname in the source URL.
         The value must start with `/` character.
        :type operation: str
        :rtype: ~azure.eventhub.async_ops.receiver_async.ReceiverAsync

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START create_eventhub_client_async_epoch_receiver]
                :end-before: [END create_eventhub_client_async_epoch_receiver]
                :language: python
                :dedent: 4
                :caption: Add an async receiver to the client with an epoch value.

        """
        path = self.address.path + operation if operation else self.address.path
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, path, consumer_group, partition)
        handler = AsyncReceiver(
            self, source_url, prefetch=prefetch, epoch=epoch,
            keep_alive=keep_alive, auto_reconnect=auto_reconnect, loop=loop)
        self.clients.append(handler)
        return handler

    def add_async_sender(
            self, partition=None, operation=None, send_timeout=60,
            keep_alive=30, auto_reconnect=True, loop=None):
        """
        Add an async sender to the client to send ~azure.eventhub.common.EventData object
        to an EventHub.

        :param partition: Optionally specify a particular partition to send to.
         If omitted, the events will be distributed to available partitions via
         round-robin.
        :type partition: str
        :operation: An optional operation to be appended to the hostname in the target URL.
         The value must start with `/` character.
        :type operation: str
        :param send_timeout: The timeout in seconds for an individual event to be sent from the time that it is
         queued. Default value is 60 seconds. If set to 0, there will be no timeout.
        :type send_timeout: int
        :param keep_alive: The time interval in seconds between pinging the connection to keep it alive during
         periods of inactivity. The default value is 30 seconds. If set to `None`, the connection will not
         be pinged.
        :type keep_alive: int
        :param auto_reconnect: Whether to automatically reconnect the sender if a retryable error occurs.
         Default value is `True`.
        :type auto_reconnect: bool
        :rtype: ~azure.eventhub.async_ops.sender_async.SenderAsync

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START create_eventhub_client_async_sender]
                :end-before: [END create_eventhub_client_async_sender]
                :language: python
                :dedent: 4
                :caption: Add an async sender to the client to
                 send ~azure.eventhub.common.EventData object to an EventHub.

        """
        target = "amqps://{}{}".format(self.address.hostname, self.address.path)
        if operation:
            target = target + operation
        handler = AsyncSender(
            self, target, partition=partition, send_timeout=send_timeout, keep_alive=keep_alive,
            auto_reconnect=auto_reconnect, loop=loop)
        self.clients.append(handler)
        return handler
