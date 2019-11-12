# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import datetime
import time
import functools
import asyncio

from typing import Any, List, Dict, Union, TYPE_CHECKING

from uamqp import authentication, constants  # type: ignore
from uamqp import Message, AMQPClientAsync  # type: ignore

from ..common import parse_sas_token, EventPosition, \
    EventHubSharedKeyCredential, EventHubSASTokenCredential
from ..client_abstract import EventHubClientAbstract

from .producer_async import EventHubProducer
from .consumer_async import EventHubConsumer
from ._connection_manager_async import get_connection_manager
from .error_async import _handle_exception

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)


class EventHubClient(EventHubClientAbstract):
    """
    The EventHubClient class defines a high level interface for asynchronously
    sending events to and receiving events from the Azure Event Hubs service.

    """

    def __init__(self, host, event_hub_path, credential, **kwargs):
        # type:(str, str, Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential], Any) -> None
        super(EventHubClient, self).__init__(host=host, event_hub_path=event_hub_path, credential=credential, **kwargs)
        self._lock = asyncio.Lock()
        self._conn_manager = get_connection_manager(**kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _create_auth(self):
        """
        Create an ~uamqp.authentication.cbs_auth_async.SASTokenAuthAsync instance to authenticate
        the session.

        """
        http_proxy = self._config.http_proxy
        transport_type = self._config.transport_type
        auth_timeout = self._config.auth_timeout

        if isinstance(self._credential, EventHubSharedKeyCredential):  # pylint:disable=no-else-return
            username = self._credential.policy
            password = self._credential.key
            if "@sas.root" in username:
                return authentication.SASLPlain(
                    self._host, username, password, http_proxy=http_proxy, transport_type=transport_type)
            return authentication.SASTokenAsync.from_shared_access_key(
                self._auth_uri, username, password, timeout=auth_timeout, http_proxy=http_proxy,
                transport_type=transport_type)

        elif isinstance(self._credential, EventHubSASTokenCredential):
            token = self._credential.get_sas_token()
            try:
                expiry = int(parse_sas_token(token)['se'])
            except (KeyError, TypeError, IndexError):
                raise ValueError("Supplied SAS token has no valid expiry value.")
            return authentication.SASTokenAsync(
                self._auth_uri, self._auth_uri, token,
                expires_at=expiry,
                timeout=auth_timeout,
                http_proxy=http_proxy,
                transport_type=transport_type)

        else:
            get_jwt_token = functools.partial(self._credential.get_token, 'https://eventhubs.azure.net//.default')
            return authentication.JWTTokenAsync(self._auth_uri, self._auth_uri,
                                                get_jwt_token, http_proxy=http_proxy,
                                                transport_type=transport_type)

    async def _close_connection(self):
        await self._conn_manager.reset_connection_if_broken()

    async def _try_delay(self, retried_times, last_exception, timeout_time=None, entity_name=None):
        entity_name = entity_name or self._container_id
        backoff = self._config.backoff_factor * 2 ** retried_times
        if backoff <= self._config.backoff_max and (
                timeout_time is None or time.time() + backoff <= timeout_time):  # pylint:disable=no-else-return
            await asyncio.sleep(backoff)
            log.info("%r has an exception (%r). Retrying...", format(entity_name), last_exception)
        else:
            log.info("%r operation has timed out. Last exception before timeout is (%r)",
                     entity_name, last_exception)
            raise last_exception

    async def _management_request(self, mgmt_msg, op_type):
        retried_times = 0
        last_exception = None
        while retried_times <= self._config.max_retries:
            mgmt_auth = self._create_auth()
            mgmt_client = AMQPClientAsync(self._mgmt_target, auth=mgmt_auth, debug=self._config.network_tracing)
            try:
                conn = await self._conn_manager.get_connection(self._host, mgmt_auth)
                await mgmt_client.open_async(connection=conn)
                response = await mgmt_client.mgmt_request_async(
                    mgmt_msg,
                    constants.READ_OPERATION,
                    op_type=op_type,
                    status_code_field=b'status-code',
                    description_fields=b'status-description')
                return response
            except Exception as exception:  # pylint:disable=broad-except
                last_exception = await _handle_exception(exception, self)
                await self._try_delay(retried_times=retried_times, last_exception=last_exception)
                retried_times += 1
            finally:
                await mgmt_client.close_async()
        log.info("%r returns an exception %r", self._container_id, last_exception)  # pylint:disable=specify-parameter-names-in-call
        raise last_exception

    async def get_properties(self):
        # type:() -> Dict[str, Any]
        """
        Get properties of the specified EventHub async.
        Keys in the details dictionary include:

            - path
            - created_at
            - partition_ids

        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        mgmt_msg = Message(application_properties={'name': self.eh_name})
        response = await self._management_request(mgmt_msg, op_type=b'com.microsoft:eventhub')
        output = {}
        eh_info = response.get_data()
        if eh_info:
            output['path'] = eh_info[b'name'].decode('utf-8')
            output['created_at'] = datetime.datetime.utcfromtimestamp(float(eh_info[b'created_at']) / 1000)
            output['partition_ids'] = [p.decode('utf-8') for p in eh_info[b'partition_ids']]
        return output

    async def get_partition_ids(self):
        # type:() -> List[str]
        """
        Get partition ids of the specified EventHub async.

        :rtype: list[str]
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        return (await self.get_properties())['partition_ids']

    async def get_partition_properties(self, partition):
        # type:(str) -> Dict[str, str]
        """
        Get properties of the specified partition async.
        Keys in the details dictionary include:

            - event_hub_path
            - id
            - beginning_sequence_number
            - last_enqueued_sequence_number
            - last_enqueued_offset
            - last_enqueued_time_utc
            - is_empty

        :param partition: The target partition id.
        :type partition: str
        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        mgmt_msg = Message(application_properties={'name': self.eh_name,
                                                   'partition': partition})
        response = await self._management_request(mgmt_msg, op_type=b'com.microsoft:partition')
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

    def _create_consumer(
            self,
            consumer_group: str,
            partition_id: str,
            event_position: EventPosition, **kwargs
    ) -> EventHubConsumer:
        """
        Create an async consumer to the client for a particular consumer group and partition.

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
        :param loop: An event loop. If not specified the default event loop will be used.
        :rtype: ~azure.eventhub.aio.consumer_async.EventHubConsumer
        """
        owner_level = kwargs.get("owner_level")
        prefetch = kwargs.get("prefetch") or self._config.prefetch
        track_last_enqueued_event_properties = kwargs.get("track_last_enqueued_event_properties", False)
        loop = kwargs.get("loop")

        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self._address.hostname, self._address.path, consumer_group, partition_id)
        handler = EventHubConsumer(
            self, source_url, event_position=event_position, owner_level=owner_level,
            prefetch=prefetch,
            track_last_enqueued_event_properties=track_last_enqueued_event_properties, loop=loop)
        return handler

    def _create_producer(
            self, *,
            partition_id: str = None,
            send_timeout: float = None,
            loop: asyncio.AbstractEventLoop = None
    ) -> EventHubProducer:
        """
        Create an async producer to send EventData object to an EventHub.

        :param partition_id: Optionally specify a particular partition to send to.
         If omitted, the events will be distributed to available partitions via
         round-robin.
        :type partition_id: str
        :param send_timeout: The timeout in seconds for an individual event to be sent from the time that it is
         queued. Default value is 60 seconds. If set to 0, there will be no timeout.
        :type send_timeout: float
        :param loop: An event loop. If not specified the default event loop will be used.
        :rtype: ~azure.eventhub.aio.producer_async.EventHubProducer
        """

        target = "amqps://{}{}".format(self._address.hostname, self._address.path)
        send_timeout = self._config.send_timeout if send_timeout is None else send_timeout

        handler = EventHubProducer(
            self, target, partition=partition_id, send_timeout=send_timeout, loop=loop)
        return handler

    async def close(self):
        # type: () -> None
        await self._conn_manager.close_connection()
