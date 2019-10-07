# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
import datetime
import time
import functools
import threading

from typing import Any, List, Dict, Union, TYPE_CHECKING

import uamqp  # type: ignore
from uamqp import Message  # type: ignore
from uamqp import authentication  # type: ignore
from uamqp import constants  # type: ignore

from azure.eventhub.producer import EventHubProducer
from azure.eventhub.consumer import EventHubConsumer
from azure.eventhub.common import parse_sas_token, EventPosition
from .client_abstract import EventHubClientAbstract
from .common import EventHubSASTokenCredential, EventHubSharedKeyCredential
from ._connection_manager import get_connection_manager
from .error import _handle_exception

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

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
        # type:(str, str, Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential], Any) -> None
        super(EventHubClient, self).__init__(host=host, event_hub_path=event_hub_path, credential=credential, **kwargs)
        self._lock = threading.RLock()
        self._conn_manager = get_connection_manager(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _create_auth(self):
        """
        Create an ~uamqp.authentication.SASTokenAuth instance to authenticate
        the session.

        :param username: The name of the shared access policy.
        :type username: str
        :param password: The shared access key.
        :type password: str
        """
        http_proxy = self._config.http_proxy
        transport_type = self._config.transport_type
        auth_timeout = self._config.auth_timeout

        # TODO: the following code can be refactored to create auth from classes directly instead of using if-else
        if isinstance(self._credential, EventHubSharedKeyCredential):  # pylint:disable=no-else-return
            username = self._credential.policy
            password = self._credential.key
            if "@sas.root" in username:
                return authentication.SASLPlain(
                    self._host, username, password, http_proxy=http_proxy, transport_type=transport_type)
            return authentication.SASTokenAuth.from_shared_access_key(
                self._auth_uri, username, password, timeout=auth_timeout, http_proxy=http_proxy,
                transport_type=transport_type)

        elif isinstance(self._credential, EventHubSASTokenCredential):
            token = self._credential.get_sas_token()
            try:
                expiry = int(parse_sas_token(token)['se'])
            except (KeyError, TypeError, IndexError):
                raise ValueError("Supplied SAS token has no valid expiry value.")
            return authentication.SASTokenAuth(
                self._auth_uri, self._auth_uri, token,
                expires_at=expiry,
                timeout=auth_timeout,
                http_proxy=http_proxy,
                transport_type=transport_type)

        else:  # Azure credential
            get_jwt_token = functools.partial(self._credential.get_token,
                                              'https://eventhubs.azure.net//.default')
            return authentication.JWTTokenAuth(self._auth_uri, self._auth_uri,
                                               get_jwt_token, http_proxy=http_proxy,
                                               transport_type=transport_type)

    def _close_connection(self):
        self._conn_manager.reset_connection_if_broken()

    def _try_delay(self, retried_times, last_exception, timeout_time=None, entity_name=None):
        entity_name = entity_name or self._container_id
        backoff = self._config.backoff_factor * 2 ** retried_times
        if backoff <= self._config.backoff_max and (
                timeout_time is None or time.time() + backoff <= timeout_time):  # pylint:disable=no-else-return
            time.sleep(backoff)
            log.info("%r has an exception (%r). Retrying...", format(entity_name), last_exception)
        else:
            log.info("%r operation has timed out. Last exception before timeout is (%r)",
                     entity_name, last_exception)
            raise last_exception

    def _management_request(self, mgmt_msg, op_type):
        retried_times = 0
        last_exception = None
        while retried_times <= self._config.max_retries:
            mgmt_auth = self._create_auth()
            mgmt_client = uamqp.AMQPClient(self._mgmt_target)
            try:
                conn = self._conn_manager.get_connection(self._host, mgmt_auth)  #pylint:disable=assignment-from-none
                mgmt_client.open(connection=conn)
                response = mgmt_client.mgmt_request(
                    mgmt_msg,
                    constants.READ_OPERATION,
                    op_type=op_type,
                    status_code_field=b'status-code',
                    description_fields=b'status-description')
                return response
            except Exception as exception:  # pylint: disable=broad-except
                last_exception = _handle_exception(exception, self)
                self._try_delay(retried_times=retried_times, last_exception=last_exception)
                retried_times += 1
            finally:
                mgmt_client.close()
        log.info("%r returns an exception %r", self._container_id, last_exception)  # pylint:disable=specify-parameter-names-in-call
        raise last_exception


    def get_properties(self):
        # type:() -> Dict[str, Any]
        """
        Get properties of the specified EventHub.
        Keys in the details dictionary include:

            -'path'
            -'created_at'
            -'partition_ids'

        :rtype: dict
        :raises: ~azure.eventhub.EventHubError
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
        :raises: ~azure.eventhub.EventHubError
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
        :param prefetch: The message prefetch count of the consumer. Default is 300.
        :type prefetch: int
        :param track_last_enqueued_event_properties: Indicates whether or not the consumer should request information
         on the last enqueued event on its associated partition, and track that information as events are received.
         When information about the partition's last enqueued event is being tracked, each event received from the
         Event Hubs service will carry metadata about the partition. This results in a small amount of additional
         network bandwidth consumption that is generally a favorable trade-off when considered against periodically
         making requests for partition properties using the Event Hub client.
         It is set to `False` by default.
        :type track_last_enqueued_event_properties: bool
        :rtype: ~azure.eventhub.consumer.EventHubConsumer

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START create_eventhub_client_receiver]
                :end-before: [END create_eventhub_client_receiver]
                :language: python
                :dedent: 4
                :caption: Add a consumer to the client for a particular consumer group and partition.

        """
        owner_level = kwargs.get("owner_level")
        prefetch = kwargs.get("prefetch") or self._config.prefetch
        track_last_enqueued_event_properties = kwargs.get("track_last_enqueued_event_properties", False)

        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self._address.hostname, self._address.path, consumer_group, partition_id)
        handler = EventHubConsumer(
            self, source_url, event_position=event_position, owner_level=owner_level,
            prefetch=prefetch,
            track_last_enqueued_event_properties=track_last_enqueued_event_properties)
        return handler

    def create_producer(self, partition_id=None, send_timeout=None):
        # type: (str, float) -> EventHubProducer
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

        target = "amqps://{}{}".format(self._address.hostname, self._address.path)
        send_timeout = self._config.send_timeout if send_timeout is None else send_timeout

        handler = EventHubProducer(
            self, target, partition=partition_id, send_timeout=send_timeout)
        return handler

    def close(self):
        # type:() -> None
        self._conn_manager.close_connection()
