# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import asyncio
import time
import datetime
import functools

from uamqp import authentication, constants, types, errors
from uamqp import (
    Message,
    AMQPClientAsync,
)

from azure.eventhub.common import parse_sas_token, EventPosition, EventHubSharedKeyCredential, EventHubSASTokenCredential
from azure.eventhub import (
    EventHubError)
from ..client_abstract import EventHubClientAbstract

from .sender_async import EventHubProducer
from .receiver_async import EventHubConsumer


log = logging.getLogger(__name__)


class EventHubClient(EventHubClientAbstract):
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
        http_proxy = self.config.http_proxy
        transport_type = self.config.transport_type
        auth_timeout = self.config.auth_timeout

        if isinstance(self.credential, EventHubSharedKeyCredential):
            username = username or self._auth_config['username']
            password = password or self._auth_config['password']
            if "@sas.root" in username:
                return authentication.SASLPlain(
                    self.host, username, password, http_proxy=http_proxy, transport_type=transport_type)
            return authentication.SASTokenAsync.from_shared_access_key(
                self.auth_uri, username, password, timeout=auth_timeout, http_proxy=http_proxy,
                transport_type=transport_type)

        elif isinstance(self.credential, EventHubSASTokenCredential):
            token = self.credential.get_sas_token()
            try:
                expiry = int(parse_sas_token(token)['se'])
            except (KeyError, TypeError, IndexError):
                raise ValueError("Supplied SAS token has no valid expiry value.")
            return authentication.SASTokenAsync(
                self.auth_uri, self.auth_uri, token,
                expires_at=expiry,
                timeout=auth_timeout,
                http_proxy=http_proxy,
                transport_type=transport_type)

        else:
            get_jwt_token = functools.partial(self.credential.get_token, 'https://eventhubs.azure.net//.default')
            return authentication.JWTTokenAsync(self.auth_uri, self.auth_uri,
                                                get_jwt_token, http_proxy=http_proxy,
                                                transport_type=transport_type)

    async def get_properties(self):
        """
        Get properties of the specified EventHub async.
        Keys in the details dictionary include:

            -'path'
            -'created_at'
            -'partition_ids'

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
                output['path'] = eh_info[b'name'].decode('utf-8')
                output['created_at'] = datetime.datetime.utcfromtimestamp(float(eh_info[b'created_at'])/1000)
                output['partition_ids'] = [p.decode('utf-8') for p in eh_info[b'partition_ids']]
            return output
        finally:
            await mgmt_client.close_async()
    
    async def get_partition_ids(self):
        """
        Get partition ids of the specified EventHub async.

        :rtype: list[str]
        """
        return (await self.get_properties())['partition_ids']

    async def get_partition_properties(self, partition):
        """
        Get properties of the specified partition async.
        Keys in the details dictionary include:

            -'event_hub_path'
            -'id'
            -'beginning_sequence_number'
            -'last_enqueued_sequence_number'
            -'last_enqueued_offset'
            -'last_enqueued_time_utc'
            -'is_empty'

        :param partition: The target partition id.
        :type partition: str
        :rtype: dict
        """
        alt_creds = {
            "username": self._auth_config.get("iot_username"),
            "password": self._auth_config.get("iot_password")}
        try:
            mgmt_auth = self._create_auth(**alt_creds)
            mgmt_client = AMQPClientAsync(self.mgmt_target, auth=mgmt_auth, debug=self.debug)
            await mgmt_client.open_async()
            mgmt_msg = Message(application_properties={'name': self.eh_name,
                                                       'partition': partition})
            response = await mgmt_client.mgmt_request_async(
                mgmt_msg,
                constants.READ_OPERATION,
                op_type=b'com.microsoft:partition',
                status_code_field=b'status-code',
                description_fields=b'status-description')
            partition_info = response.get_data()
            output = {}
            if partition_info:
                output['event_hub_path'] = partition_info[b'name'].decode('utf-8')
                output['id'] = partition_info[b'partition'].decode('utf-8')
                output['beginning_sequence_number'] = partition_info[b'begin_sequence_number']
                output['last_enqueued_sequence_number'] = partition_info[b'last_enqueued_sequence_number']
                output['last_enqueued_offset'] = partition_info[b'last_enqueued_offset'].decode('utf-8')
                output['last_enqueued_time_utc'] = datetime.datetime.utcfromtimestamp(
                    float(partition_info[b'last_enqueued_time_utc'] / 1000))
                output['is_empty'] = partition_info[b'is_partition_empty']
            return output
        finally:
            await mgmt_client.close_async()

    def create_consumer(
            self, consumer_group, partition_id, event_position, owner_level=None,
            operation=None, prefetch=None, loop=None):
        """
        Create an async receiver to the client for a particular consumer group and partition.

        :param consumer_group: The name of the consumer group. Default value is `$Default`.
        :type consumer_group: str
        :param partition_id: The ID of the partition.
        :type partition_id: str
        :param event_position: The position from which to start receiving.
        :type event_position: ~azure.eventhub.common.EventPosition
        :param owner_level: The priority of the exclusive receiver. The client will create an exclusive
         receiver if owner_level is set.
        :type owner_level: int
        :param operation: An optional operation to be appended to the hostname in the source URL.
         The value must start with `/` character.
        :type operation: str
        :param prefetch: The message prefetch count of the receiver. Default is 300.
        :type prefetch: int
        :param loop: An event loop. If not specified the default event loop will be used.
        :rtype: ~azure.eventhub.aio.receiver_async.EventHubConsumer

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START create_eventhub_client_async_receiver]
                :end-before: [END create_eventhub_client_async_receiver]
                :language: python
                :dedent: 4
                :caption: Add an async receiver to the client for a particular consumer group and partition.

        """
        prefetch = self.config.prefetch if prefetch is None else prefetch

        path = self.address.path + operation if operation else self.address.path
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, path, consumer_group, partition_id)
        handler = EventHubConsumer(
            self, source_url, event_position=event_position, owner_level=owner_level,
            prefetch=prefetch, loop=loop)
        return handler

    def create_producer(
            self, partition_id=None, operation=None, send_timeout=None, loop=None):
        """
        Create an async sender to the client to send ~azure.eventhub.common.EventData object
        to an EventHub.

        :param partition_id: Optionally specify a particular partition to send to.
         If omitted, the events will be distributed to available partitions via
         round-robin.
        :type partition_id: str
        :param operation: An optional operation to be appended to the hostname in the target URL.
         The value must start with `/` character.
        :type operation: str
        :param send_timeout: The timeout in seconds for an individual event to be sent from the time that it is
         queued. Default value is 60 seconds. If set to 0, there will be no timeout.
        :type send_timeout: float
        :param loop: An event loop. If not specified the default event loop will be used.
        :rtype ~azure.eventhub.aio.sender_async.EventHubProducer


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
        send_timeout = self.config.send_timeout if send_timeout is None else send_timeout

        handler = EventHubProducer(
            self, target, partition=partition_id, send_timeout=send_timeout, loop=loop)
        return handler
