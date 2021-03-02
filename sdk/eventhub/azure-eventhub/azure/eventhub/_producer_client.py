# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import threading

from typing import Any, Union, TYPE_CHECKING, Dict, List, Optional, cast

from uamqp import constants

from .exceptions import ConnectError, EventHubError
from ._client_base import ClientBase
from ._producer import EventHubProducer
from ._constants import ALL_PARTITIONS
from ._common import EventDataBatch, EventData
from ._configuration import PartitionPublishingConfiguration
from ._utils import validate_producer_client_partition_config

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    PartitionPublishingConfigType = Optional[Union[PartitionPublishingConfiguration, dict]]

_LOGGER = logging.getLogger(__name__)


def validate_outgoing_event_data(
    event_data_batch,
    partition_id=None,
    partition_key=None,
    is_idempotent_publishing=False
):
    # type: (Union[EventDataBatch, List[EventData]], Optional[str], Optional[str], bool) -> None
    # Validate the input of EventHubProducerClient.send_batch
    # pylint:disable=protected-access
    if isinstance(event_data_batch, EventDataBatch):
        if is_idempotent_publishing:
            if event_data_batch._partition_id is None:
                raise ValueError("The EventDataBatch object must have the partition_id set when performing "
                                 "idempotent publishing. Please create an EventDataBatch object with partition_id.")
            if event_data_batch.starting_published_sequence_number is not None:
                raise ValueError("EventDataBatch object that has already been published by idempotent producer"
                                 "cannot be published again. Please create a new object.")
        if partition_id or partition_key:
            raise TypeError("partition_id and partition_key should be None when sending an EventDataBatch "
                            "because type EventDataBatch itself may have partition_id or partition_key")
    else:  # list of EventData
        if is_idempotent_publishing:
            if partition_id is None:
                raise ValueError("The partition_id must be set when performing idempotent publishing.")
            if [event for event in event_data_batch if event.published_sequence_number is not None]:
                raise ValueError("EventData object that has already been published by "
                                 "idempotent producer cannot be published again.")


class EventHubProducerClient(ClientBase):
    """The EventHubProducerClient class defines a high level interface for
    sending events to the Azure Event Hubs service.

    :param str fully_qualified_namespace: The fully qualified host name for the Event Hubs namespace.
     This is likely to be similar to <yournamespace>.servicebus.windows.net
    :param str eventhub_name: The path of the specific Event Hub to connect the client to.
    :param ~azure.core.credentials.TokenCredential credential: The credential object used for authentication which
     implements a particular interface for getting tokens. It accepts
     :class:`EventHubSharedKeyCredential<azure.eventhub.EventHubSharedKeyCredential>`, or credential objects generated
     by the azure-identity library and objects that implement the `get_token(self, *scopes)` method.
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword float auth_timeout: The time in seconds to wait for a token to be authorized by the service.
     The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
    :keyword str user_agent: The user agent that should be appended to the built-in user agent string.
    :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs. Default
     value is 3.
    :keyword float idle_timeout: Timeout, in seconds, after which this client will close the underlying connection
     if there is no activity. By default the value is None, meaning that the client will not shutdown due to inactivity
     unless initiated by the service.
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the Event Hubs service. Default is `TransportType.Amqp`.
    :paramtype transport_type: ~azure.eventhub.TransportType
    :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :keyword str custom_endpoint_address: The custom endpoint address to use for establishing a connection to
     the Event Hubs service, allowing network requests to be routed through any application gateways or
     other paths needed for the host environment. Default is None.
     The format would be like "sb://<custom_endpoint_hostname>:<custom_endpoint_port>".
     If port is not specified in the `custom_endpoint_address`, by default port 443 will be used.
    :keyword str connection_verify: Path to the custom CA_BUNDLE file of the SSL certificate which is used to
     authenticate the identity of the connection endpoint.
     Default is None in which case `certifi.where()` will be used.
    :keyword bool enable_idempotent_partitions: Indicates whether or not the producer should enable idempotent
     publishing to the Event Hub partitions. If enabled, the producer will only be able to publish directly
     to partitions; it will not be able to publish to the Event Hubs gateway for automatic partition routing
     nor will it be able to use a partition key. Default is False.
    :keyword partition_config: The set of configurations that can be specified to influence publishing behavior
     specific to the configured Event Hub partition. These configurations are not necessary in the majority of
     scenarios and are intended for use with specialized scenarios, such as when recovering the state used for
     idempotent publishing.
     It is highly recommended that these configurations only be specified if there is a proven need to do so;
     Incorrectly configuring these values may result in an `EventHubProducerClient` instance that is unable to
     publish to the Event Hubs. These configurations are ignored when publishing to the Event Hubs gateway for
     automatic routing or when using a partition key.
     If a dict is provided as the value instead of a PartitionPublishingConfiguration object, it may contain the
     optional keys: `'producer_group_id'` (int value), `'owner_level'` (int value) and
     `'starting_sequence_number'` (int value).
    :paramtype partition_config: dict[str, Union[~azure.eventhub.PartitionPublishingConfiguration, dict]]

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
            :start-after: [START create_eventhub_producer_client_sync]
            :end-before: [END create_eventhub_producer_client_sync]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the EventHubProducerClient.

    """

    def __init__(
        self,
        fully_qualified_namespace,  # type: str
        eventhub_name,  # type: str
        credential,  # type: TokenCredential
        **kwargs  # type: Any
    ):
        # type:(...) -> None
        super(EventHubProducerClient, self).__init__(
            fully_qualified_namespace=fully_qualified_namespace,
            eventhub_name=eventhub_name,
            credential=credential,
            network_tracing=kwargs.get("logging_enable"),
            **kwargs
        )
        self._producers = {
            ALL_PARTITIONS: self._create_producer()
        }  # type: Dict[str, Optional[EventHubProducer]]
        self._max_message_size_on_link = 0
        self._partition_ids = None  # Optional[List[str]]
        self._partition_config = kwargs.get("partition_config") or {}
        self._lock = threading.Lock()
        for _, each_partition_config in self._partition_config.items():
            validate_producer_client_partition_config(each_partition_config)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _get_partitions(self):
        # type: () -> None
        if not self._partition_ids:
            self._partition_ids = self.get_partition_ids()  # type: ignore
            for p_id in cast(List[str], self._partition_ids):
                self._producers[p_id] = None

    def _get_max_mesage_size(self):
        # type: () -> None
        # pylint: disable=protected-access,line-too-long
        with self._lock:
            if not self._max_message_size_on_link:
                cast(
                    EventHubProducer, self._producers[ALL_PARTITIONS]
                )._open_with_retry()
                self._max_message_size_on_link = (
                    self._producers[  # type: ignore
                        ALL_PARTITIONS
                    ]._handler.message_handler._link.peer_max_message_size
                    or constants.MAX_MESSAGE_LENGTH_BYTES
                )

    def _start_producer(self, partition_id, send_timeout):
        # type: (str, Optional[Union[int, float]]) -> None
        with self._lock:
            self._get_partitions()
            if (
                partition_id not in cast(List[str], self._partition_ids)
                and partition_id != ALL_PARTITIONS
            ):
                raise ConnectError(
                    "Invalid partition {} for the event hub {}".format(
                        partition_id, self.eventhub_name
                    )
                )

            if (
                not self._producers[partition_id]
                or cast(EventHubProducer, self._producers[partition_id]).closed
            ):
                partition_config = self._partition_config.get(partition_id)
                self._producers[partition_id] = self._create_producer(
                    partition_id=partition_id,
                    send_timeout=send_timeout,
                    enable_idempotent_partitions=self._config.enable_idempotent_partitions,
                    partition_config=partition_config
                )

    def _create_producer(
        self,
        partition_id=None,
        send_timeout=None,
        enable_idempotent_partitions=False,
        partition_config=None
    ):
        # type: (Optional[str], Optional[Union[int, float]], bool, PartitionPublishingConfigType) -> EventHubProducer
        target = "amqps://{}{}".format(self._address.hostname, self._address.path)
        send_timeout = (
            self._config.send_timeout if send_timeout is None else send_timeout
        )

        handler = EventHubProducer(
            self,
            target,
            partition=partition_id,
            send_timeout=send_timeout,
            idle_timeout=self._idle_timeout,
            enable_idempotent_partitions=enable_idempotent_partitions,
            partition_config=partition_config
        )
        return handler

    @classmethod
    def from_connection_string(cls, conn_str, **kwargs):
        # type: (str, Any) -> EventHubProducerClient
        """Create an EventHubProducerClient from a connection string.

        :param str conn_str: The connection string of an Event Hub.
        :keyword str eventhub_name: The path of the specific Event Hub to connect the client to.
        :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
        :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
         Additionally the following keys may also be present: `'username', 'password'`.
        :keyword float auth_timeout: The time in seconds to wait for a token to be authorized by the service.
         The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
        :keyword str user_agent: The user agent that should be appended to the built-in user agent string.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :keyword float idle_timeout: Timeout, in seconds, after which this client will close the underlying connection
         if there is no activity. By default the value is None, meaning that the client will not shutdown due to
         inactivity unless initiated by the service.
        :keyword transport_type: The type of transport protocol that will be used for communicating with
         the Event Hubs service. Default is `TransportType.Amqp`.
        :paramtype transport_type: ~azure.eventhub.TransportType
        :keyword str custom_endpoint_address: The custom endpoint address to use for establishing a connection to
         the Event Hubs service, allowing network requests to be routed through any application gateways or
         other paths needed for the host environment. Default is None.
         The format would be like "sb://<custom_endpoint_hostname>:<custom_endpoint_port>".
         If port is not specified in the `custom_endpoint_address`, by default port 443 will be used.
        :keyword str connection_verify: Path to the custom CA_BUNDLE file of the SSL certificate which is used to
         authenticate the identity of the connection endpoint.
         Default is None in which case `certifi.where()` will be used.
        :keyword bool enable_idempotent_partitions: Indicates whether or not the producer should enable idempotent
         publishing to the Event Hub partitions. If enabled, the producer will only be able to publish directly
         to partitions; it will not be able to publish to the Event Hubs gateway for automatic partition routing
         nor will it be able to use a partition key. Default is False.
        :keyword partition_config: The set of configurations that can be specified to influence publishing behavior
         specific to the configured Event Hub partition. These configurations are not necessary in the majority of
         scenarios and are intended for use with specialized scenarios, such as when recovering the state used for
         idempotent publishing.
         It is highly recommended that these configurations only be specified if there is a proven need to do so;
         Incorrectly configuring these values may result in an `EventHubProducerClient` instance that is unable to
         publish to the Event Hubs. These configurations are ignored when publishing to the Event Hubs gateway for
         automatic routing or when using a partition key.
         If a dict is provided as the value instead of a PartitionPublishingConfiguration object, it may contain the
         optional keys: `'producer_group_id'` (int value), `'owner_level'` (int value) and
         `'starting_sequence_number'` (int value).
        :paramtype partition_config: dict[str, Union[~azure.eventhub.PartitionPublishingConfiguration, dict]]
        :rtype: ~azure.eventhub.EventHubProducerClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
                :start-after: [START create_eventhub_producer_client_from_conn_str_sync]
                :end-before: [END create_eventhub_producer_client_from_conn_str_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the EventHubProducerClient from connection string.
        """
        constructor_args = cls._from_connection_string(conn_str, **kwargs)
        return cls(**constructor_args)

    def send_batch(self, event_data_batch, **kwargs):
        # type: (Union[EventDataBatch, List[EventData]], Any) -> None
        """Sends event data and blocks until acknowledgement is received or operation times out.

        If you're sending a finite list of `EventData` and you know it's within the event hub
        frame size limit, you can send them with a `send_batch` call. Otherwise, use :meth:`create_batch`
        to create `EventDataBatch` and add `EventData` into the batch one by one until the size limit,
        and then call this method to send out the batch.

        :param event_data_batch: The `EventDataBatch` object to be sent or a list of `EventData` to be sent
         in a batch. All `EventData` in the list or `EventDataBatch` will land on the same partition.
        :type event_data_batch: Union[~azure.eventhub.EventDataBatch, List[~azure.eventhub.EventData]]
        :keyword float timeout: The maximum wait time to send the event data.
         If not specified, the default wait time specified when the producer was created will be used.
        :keyword str partition_id: The specific partition ID to send to. Default is None, in which case the service
         will assign to all partitions using round-robin.
         A `TypeError` will be raised if partition_id is specified and event_data_batch is an `EventDataBatch` because
         `EventDataBatch` itself has partition_id.
        :keyword str partition_key: With the given partition_key, event data will be sent to
         a particular partition of the Event Hub decided by the service.
         A `TypeError` will be raised if partition_key is specified and event_data_batch is an `EventDataBatch` because
         `EventDataBatch` itself has partition_key.
         If both partition_id and partition_key are provided, the partition_id will take precedence.
         **WARNING: Please DO NOT pass a partition_key of non-string type. The Event Hub service ignores partition_key
         of non-string type, in which case events will be assigned to all partitions using round-robin.**
        :rtype: None
        :raises: :class:`AuthenticationError<azure.eventhub.exceptions.AuthenticationError>`
         :class:`ConnectError<azure.eventhub.exceptions.ConnectError>`
         :class:`ConnectionLostError<azure.eventhub.exceptions.ConnectionLostError>`
         :class:`EventDataError<azure.eventhub.exceptions.EventDataError>`
         :class:`EventDataSendError<azure.eventhub.exceptions.EventDataSendError>`
         :class:`EventHubError<azure.eventhub.exceptions.EventHubError>`
         :class:`ValueError`
         :class:`TypeError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
                :start-after: [START eventhub_producer_client_send_sync]
                :end-before: [END eventhub_producer_client_send_sync]
                :language: python
                :dedent: 4
                :caption: Sends event data

        """
        # pylint:disable=protected-access
        partition_id = kwargs.get("partition_id")
        partition_key = kwargs.get("partition_key")

        validate_outgoing_event_data(
            event_data_batch,
            partition_id,
            partition_key,
            self._config.enable_idempotent_partitions
        )

        if isinstance(event_data_batch, EventDataBatch):
            to_send_batch = event_data_batch
        else:
            to_send_batch = self.create_batch(partition_id=partition_id, partition_key=partition_key)
            to_send_batch._load_events(event_data_batch)
        partition_id = (
            to_send_batch._partition_id or ALL_PARTITIONS
        )

        if len(to_send_batch) == 0:
            return

        send_timeout = kwargs.pop("timeout", None)
        try:
            cast(EventHubProducer, self._producers[partition_id]).send(
                to_send_batch, timeout=send_timeout
            )
        except (KeyError, AttributeError, EventHubError):
            self._start_producer(partition_id, send_timeout)
            cast(EventHubProducer, self._producers[partition_id]).send(
                to_send_batch, timeout=send_timeout
            )

    def create_batch(self, **kwargs):
        # type:(Any) -> EventDataBatch
        """Create an EventDataBatch object with the max size of all content being constrained by max_size_in_bytes.

        The max_size_in_bytes should be no greater than the max allowed message size defined by the service.

        :keyword str partition_id: The specific partition ID to send to. Default is None, in which case the service
         will assign to all partitions using round-robin.
        :keyword str partition_key: With the given partition_key, event data will be sent to
         a particular partition of the Event Hub decided by the service.
         If both partition_id and partition_key are provided, the partition_id will take precedence.
         **WARNING: Please DO NOT pass a partition_key of non-string type. The Event Hub service ignores partition_key
         of non-string type, in which case events will be assigned to all partitions using round-robin.**
        :keyword int max_size_in_bytes: The maximum size of bytes data that an EventDataBatch object can hold. By
         default, the value is determined by your Event Hubs tier.
        :rtype: ~azure.eventhub.EventDataBatch

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
                :start-after: [START eventhub_producer_client_create_batch_sync]
                :end-before: [END eventhub_producer_client_create_batch_sync]
                :language: python
                :dedent: 4
                :caption: Create EventDataBatch object within limited size

        """
        max_size_in_bytes = kwargs.get("max_size_in_bytes", None)
        partition_id = kwargs.get("partition_id", None)
        partition_key = kwargs.get("partition_key", None)

        if self._config.enable_idempotent_partitions and partition_id is None:
            raise ValueError("The EventDataBatch object must have the partition_id set when performing "
                             "idempotent publishing. Please create an EventDataBatch object with partition_id.")

        if not self._max_message_size_on_link:
            self._get_max_mesage_size()

        if max_size_in_bytes and max_size_in_bytes > self._max_message_size_on_link:
            raise ValueError(
                "Max message size: {} is too large, acceptable max batch size is: {} bytes.".format(
                    max_size_in_bytes, self._max_message_size_on_link
                )
            )

        event_data_batch = EventDataBatch(
            max_size_in_bytes=(max_size_in_bytes or self._max_message_size_on_link),
            partition_id=partition_id,
            partition_key=partition_key,
            is_idempotent_batch=self._config.enable_idempotent_partitions
        )

        return event_data_batch

    def get_eventhub_properties(self):
        # type:() -> Dict[str, Any]
        """Get properties of the Event Hub.

        Keys in the returned dictionary include:

            - `eventhub_name` (str)
            - `created_at` (UTC datetime.datetime)
            - `partition_ids` (list[str])

        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.exceptions.EventHubError>`
        """
        return super(EventHubProducerClient, self)._get_eventhub_properties()

    def get_partition_ids(self):
        # type:() -> List[str]
        """Get partition IDs of the Event Hub.

        :rtype: list[str]
        :raises: :class:`EventHubError<azure.eventhub.exceptions.EventHubError>`
        """
        return super(EventHubProducerClient, self)._get_partition_ids()

    def get_partition_properties(self, partition_id):
        # type:(str) -> Dict[str, Any]
        """Get properties of the specified partition.

        Keys in the properties dictionary include:

            - `eventhub_name` (str)
            - `id` (str)
            - `beginning_sequence_number` (int)
            - `last_enqueued_sequence_number` (int)
            - `last_enqueued_offset` (str)
            - `last_enqueued_time_utc` (UTC datetime.datetime)
            - `is_empty` (bool)

        :param partition_id: The target partition ID.
        :type partition_id: str
        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.exceptions.EventHubError>`
        """
        return super(EventHubProducerClient, self)._get_partition_properties(
            partition_id
        )

    def get_partition_publishing_properties(self, partition_id):
        # type: (str) -> dict
        """Get the information about the state of publishing for a partition as observed by
        the `EventHubProducerClient`. This data can always be read, but will only be populated with
        information relevant to the active features for the producer client.

            - `enable_idempotent_publishing` (bool)
            - `partition_id` (str)
            - `last_published_sequence_number` (Optional[int])
            - `producer_group_id` (Optional[int])
            - `owner_level` (Optional[int]

        :param partition_id: The target partition ID.
        :type partition_id: str
        :rtype: dict
        """
        # pylint:disable=protected-access
        output = {
            'enable_idempotent_publishing': self._config.enable_idempotent_partitions,
            'partition_id': partition_id,
            'last_published_sequence_number': None,
            'producer_group_id': None,
            'owner_level': None
        }
        try:
            producer = cast(EventHubProducer, self._producers[partition_id])
            output['last_published_sequence_number'] = producer._last_published_sequence_number
            output['producer_group_id'] = producer._producer_group_id
            output['owner_level'] = producer._owner_level
        except (KeyError, AttributeError):
            pass

        return output

    def close(self):
        # type: () -> None
        """Close the Producer client underlying AMQP connection and links.

        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
                :start-after: [START eventhub_producer_client_close_sync]
                :end-before: [END eventhub_producer_client_close_sync]
                :language: python
                :dedent: 4
                :caption: Close down the client.

        """
        with self._lock:
            for producer in self._producers.values():
                if producer:
                    producer.close()
            self._producers = {}
        super(EventHubProducerClient, self)._close()
