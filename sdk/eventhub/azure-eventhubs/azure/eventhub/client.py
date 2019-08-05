# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
import datetime
import functools
try:
    from urlparse import urlparse
    from urllib import unquote_plus, urlencode, quote_plus
except ImportError:
    from urllib.parse import urlparse, unquote_plus, urlencode, quote_plus
from typing import Any, List, Dict

import uamqp
from uamqp import Message
from uamqp import authentication
from uamqp import constants

from azure.eventhub.producer import EventHubProducer
from azure.eventhub.consumer import EventHubConsumer
from azure.eventhub.common import parse_sas_token, EventPosition
from .client_abstract import EventHubClientAbstract
from .common import EventHubSASTokenCredential, EventHubSharedKeyCredential
from ._connection_manager import get_connection_manager
from .error import _handle_exception


log = logging.getLogger(__name__)


class EventHubClient(EventHubClientAbstract):
    """
    The EventHubClient class defines a high level interface for sending
    events to and receiving events from the Azure Event Hubs service.

    Example:
        .. literalinclude:: ../examples/test_examples_eventhub.py
            :start-after: [START create_eventhub_client]
            :end-before: [END create_eventhub_client]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the Event Hub client

    """

    def __init__(self, host, event_hub_path, credential, **kwargs):
        super(EventHubClient, self).__init__(host, event_hub_path, credential, **kwargs)
        self._conn_manager = get_connection_manager(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _create_auth(self, username=None, password=None):
        """
        Create an ~uamqp.authentication.SASTokenAuth instance to authenticate
        the session.

        :param username: The name of the shared access policy.
        :type username: str
        :param password: The shared access key.
        :type password: str
        """
        http_proxy = self.config.http_proxy
        transport_type = self.config.transport_type
        auth_timeout = self.config.auth_timeout

        # TODO: the following code can be refactored to create auth from classes directly instead of using if-else
        if isinstance(self.credential, EventHubSharedKeyCredential):
            username = username or self._auth_config['username']
            password = password or self._auth_config['password']
            if "@sas.root" in username:
                return authentication.SASLPlain(
                    self.host, username, password, http_proxy=http_proxy, transport_type=transport_type)
            return authentication.SASTokenAuth.from_shared_access_key(
                self.auth_uri, username, password, timeout=auth_timeout, http_proxy=http_proxy,
                transport_type=transport_type)

        elif isinstance(self.credential, EventHubSASTokenCredential):
            token = self.credential.get_sas_token()
            try:
                expiry = int(parse_sas_token(token)['se'])
            except (KeyError, TypeError, IndexError):
                raise ValueError("Supplied SAS token has no valid expiry value.")
            return authentication.SASTokenAuth(
                self.auth_uri, self.auth_uri, token,
                expires_at=expiry,
                timeout=auth_timeout,
                http_proxy=http_proxy,
                transport_type=transport_type)

        else:  # Azure credential
            get_jwt_token = functools.partial(self.credential.get_token,
                                              'https://eventhubs.azure.net//.default')
            return authentication.JWTTokenAuth(self.auth_uri, self.auth_uri,
                                               get_jwt_token, http_proxy=http_proxy,
                                               transport_type=transport_type)

    def _handle_exception(self, exception, retry_count, max_retries):
        _handle_exception(exception, retry_count, max_retries, self)

    def _close_connection(self):
        self._conn_manager.reset_connection_if_broken()

    def _management_request(self, mgmt_msg, op_type):
        max_retries = self.config.max_retries
        retry_count = 0
        while retry_count <= self.config.max_retries:
            mgmt_auth = self._create_auth()
            mgmt_client = uamqp.AMQPClient(self.mgmt_target)
            try:
                conn = self._conn_manager.get_connection(self.host, mgmt_auth)
                mgmt_client.open(connection=conn)
                response = mgmt_client.mgmt_request(
                    mgmt_msg,
                    constants.READ_OPERATION,
                    op_type=op_type,
                    status_code_field=b'status-code',
                    description_fields=b'status-description')
                return response
            except Exception as exception:
                self._handle_exception(exception, retry_count, max_retries)
                retry_count += 1
            finally:
                mgmt_client.close()

    def get_properties(self):
        # type:() -> Dict[str, Any]
        """
        Get properties of the specified EventHub.
        Keys in the details dictionary include:

            -'path'
            -'created_at'
            -'partition_ids'

        :rtype: dict
        :raises: ~azure.eventhub.ConnectError
        """
        mgmt_msg = Message(application_properties={'name': self.eh_name})
        response = self._management_request(mgmt_msg, op_type=b'com.microsoft:eventhub')
        output = {}
        eh_info = response.get_data()
        if eh_info:
            output['path'] = eh_info[b'name'].decode('utf-8')
            output['created_at'] = datetime.datetime.utcfromtimestamp(float(eh_info[b'created_at']) / 1000)
            output['partition_ids'] = [p.decode('utf-8') for p in eh_info[b'partition_ids']]
        return output

    def get_partition_ids(self):
        # type:() -> List[str]
        """
        Get partition ids of the specified EventHub.

        :rtype: list[str]
        :raises: ~azure.eventhub.ConnectError
        """
        return self.get_properties()['partition_ids']

    def get_partition_properties(self, partition):
        # type:(str) -> Dict[str, Any]
        """
        Get properties of the specified partition.
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
        :raises: ~azure.eventhub.ConnectError
        """
        mgmt_msg = Message(application_properties={'name': self.eh_name,
                                                   'partition': partition})
        response = self._management_request(mgmt_msg, op_type=b'com.microsoft:partition')
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

    def create_consumer(self, consumer_group, partition_id, event_position, **kwargs):
        # type: (str, str, EventPosition, Any) -> EventHubConsumer
        """
        Create a consumer to the client for a particular consumer group and partition.

        :param consumer_group: The name of the consumer group this consumer is associated with.
         Events are read in the context of this group. The default consumer_group for an event hub is "$Default".
        :type consumer_group: str
        :param partition_id: The identifier of the Event Hub partition from which events will be received.
        :type partition_id: str
        :param event_position: The position within the partition where the consumer should begin reading events.
        :type event_position: ~azure.eventhub.common.EventPosition
        :param owner_level: The priority of the exclusive consumer. The client will create an exclusive
         consumer if owner_level is set.
        :type owner_level: int
        :param operation: An optional operation to be appended to the hostname in the source URL.
         The value must start with `/` character.
        :type operation: str
        :param prefetch: The message prefetch count of the consumer. Default is 300.
        :type prefetch: int
        :rtype: ~azure.eventhub.consumer.EventHubConsumer

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START create_eventhub_client_receiver]
                :end-before: [END create_eventhub_client_receiver]
                :language: python
                :dedent: 4
                :caption: Add a consumer to the client for a particular consumer group and partition.

        """
        owner_level = kwargs.get("owner_level", None)
        operation = kwargs.get("operation", None)
        prefetch = kwargs.get("prefetch", None)

        prefetch = prefetch or self.config.prefetch
        path = self.address.path + operation if operation else self.address.path
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, path, consumer_group, partition_id)
        handler = EventHubConsumer(
            self, source_url, event_position=event_position, owner_level=owner_level,
            prefetch=prefetch)
        return handler

    def create_producer(self, partition_id=None, operation=None, send_timeout=None):
        # type: (str, str, float) -> EventHubProducer
        """
        Create an producer to send EventData object to an EventHub.

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
        :rtype: ~azure.eventhub.producer.EventHubProducer

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START create_eventhub_client_sender]
                :end-before: [END create_eventhub_client_sender]
                :language: python
                :dedent: 4
                :caption: Add a producer to the client to send EventData.

        """

        target = "amqps://{}{}".format(self.address.hostname, self.address.path)
        if operation:
            target = target + operation
        send_timeout = self.config.send_timeout if send_timeout is None else send_timeout

        handler = EventHubProducer(
            self, target, partition=partition_id, send_timeout=send_timeout)
        return handler

    def close(self):
        self._conn_manager.close_connection()
