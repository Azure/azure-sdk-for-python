# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import threading

from typing import Any, Union, TYPE_CHECKING, Dict, List, Optional, cast

from .exceptions import ConnectError, EventHubError
from .amqp import AmqpAnnotatedMessage
from ._client_base import ClientBase
from ._producer import EventHubProducer
from ._constants import ALL_PARTITIONS, MAX_MESSAGE_LENGTH_BYTES
from ._common import EventDataBatch, EventData

if TYPE_CHECKING:
    from azure.core.credentials import (
        TokenCredential,
        AzureSasCredential,
        AzureNamedKeyCredential,
    )

SendEventTypes = List[Union[EventData, AmqpAnnotatedMessage]]

_LOGGER = logging.getLogger(__name__)


class EventHubProducerClient(ClientBase):
    """The EventHubProducerClient class defines a high level interface for
    sending events to the Azure Event Hubs service.

    :param str fully_qualified_namespace: The fully qualified host name for the Event Hubs namespace.
     This is likely to be similar to <yournamespace>.servicebus.windows.net
    :param str eventhub_name: The path of the specific Event Hub to connect the client to.
    :param credential: The credential object used for authentication which
     implements a particular interface for getting tokens. It accepts
     :class:`EventHubSharedKeyCredential<azure.eventhub.EventHubSharedKeyCredential>`, or credential objects generated
     by the azure-identity library and objects that implement the `get_token(self, *scopes)` method.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureSasCredential
     or ~azure.core.credentials.AzureNamedKeyCredential
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword float auth_timeout: The time in seconds to wait for a token to be authorized by the service.
     The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
    :keyword str user_agent: If specified, this will be added in front of the user agent string.
    :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs. Default
     value is 3.
    :keyword float retry_backoff_factor: A backoff factor to apply between attempts after the second try
     (most errors are resolved immediately by a second try without a delay).
     In fixed mode, retry policy will always sleep for {backoff factor}.
     In 'exponential' mode, retry policy will sleep for: `{backoff factor} * (2 ** ({number of total retries} - 1))`
     seconds. If the backoff_factor is 0.1, then the retry will sleep
     for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.
    :keyword float retry_backoff_max: The maximum back off time. Default value is 120 seconds (2 minutes).
    :keyword retry_mode: The delay behavior between retry attempts. Supported values are 'fixed' or 'exponential',
     where default is 'exponential'.
    :paramtype retry_mode: str
    :keyword float idle_timeout: Timeout, in seconds, after which this client will close the underlying connection
     if there is no activity. By default the value is None, meaning that the client will not shutdown due to inactivity
     unless initiated by the service.
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the Event Hubs service. Default is `TransportType.Amqp` in which case port 5671 is used.
     If the port 5671 is unavailable/blocked in the network environment, `TransportType.AmqpOverWebsocket` could
     be used instead which uses port 443 for communication.
    :paramtype transport_type: ~azure.eventhub.TransportType
    :keyword Dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
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
        credential,  # type: Union[AzureSasCredential, TokenCredential, AzureNamedKeyCredential]
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
        self._lock = threading.Lock()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _get_partitions(self):
        # type: () -> None
        if not self._partition_ids:
            _LOGGER.info("Populating partition IDs so producers can be started.")
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
                    ]._handler._link.remote_max_message_size
                    or MAX_MESSAGE_LENGTH_BYTES
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
                self._producers[partition_id] = self._create_producer(
                    partition_id=(
                        None if partition_id == ALL_PARTITIONS else partition_id
                    ),
                    send_timeout=send_timeout,
                )

    def _create_producer(self, partition_id=None, send_timeout=None):
        # type: (Optional[str], Optional[Union[int, float]]) -> EventHubProducer
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
        )
        return handler

    @classmethod
    def from_connection_string(cls, conn_str, **kwargs):
        # type: (str, Any) -> EventHubProducerClient
        """Create an EventHubProducerClient from a connection string.

        :param str conn_str: The connection string of an Event Hub.
        :keyword str eventhub_name: The path of the specific Event Hub to connect the client to.
        :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
        :keyword float auth_timeout: The time in seconds to wait for a token to be authorized by the service.
         The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
        :keyword str user_agent: If specified, this will be added in front of the user agent string.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :keyword float retry_backoff_factor: A backoff factor to apply between attempts after the second try
         (most errors are resolved immediately by a second try without a delay).
         In fixed mode, retry policy will always sleep for {backoff factor}.
         In 'exponential' mode, retry policy will sleep for: `{backoff factor} * (2 ** ({number of total retries} - 1))`
         seconds. If the backoff_factor is 0.1, then the retry will sleep
         for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.
        :keyword float retry_backoff_max: The maximum back off time. Default value is 120 seconds (2 minutes).
        :keyword retry_mode: The delay behavior between retry attempts. Supported values are 'fixed' or 'exponential',
         where default is 'exponential'.
        :paramtype retry_mode: str
        :keyword float idle_timeout: Timeout, in seconds, after which this client will close the underlying connection
         if there is no activity. By default the value is None, meaning that the client will not shutdown due to
         inactivity unless initiated by the service.
        :keyword transport_type: The type of transport protocol that will be used for communicating with
         the Event Hubs service. Default is `TransportType.Amqp` in which case port 5671 is used.
         If the port 5671 is unavailable/blocked in the network environment, `TransportType.AmqpOverWebsocket` could
         be used instead which uses port 443 for communication.
        :paramtype transport_type: ~azure.eventhub.TransportType
        :keyword Dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
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
        # type: (Union[EventDataBatch, SendEventTypes], Any) -> None
        """Sends event data and blocks until acknowledgement is received or operation times out.

        If you're sending a finite list of `EventData` or `AmqpAnnotatedMessage` and you know it's within the
        event hub frame size limit, you can send them with a `send_batch` call. Otherwise, use :meth:`create_batch`
        to create `EventDataBatch` and add either `EventData` or `AmqpAnnotatedMessage` into the batch one by one
        until the size limit, and then call this method to send out the batch.

        :param event_data_batch: The `EventDataBatch` object to be sent or a list of `EventData` to be sent in a batch.
         All `EventData` or `AmqpAnnotatedMessage` in the list or `EventDataBatch` will land on the same partition.
        :type event_data_batch: Union[~azure.eventhub.EventDataBatch, List[Union[~azure.eventhub.EventData,
            ~azure.eventhub.amqp.AmqpAnnotatedMessage]]
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
         **WARNING: Setting partition_key of non-string value on the events to be sent is discouraged
         as the partition_key will be ignored by the Event Hub service and events will be assigned
         to all partitions using round-robin. Furthermore, there are SDKs for consuming events which expect
         partition_key to only be string type, they might fail to parse the non-string value.**
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
        partition_id = kwargs.get("partition_id")
        partition_key = kwargs.get("partition_key")

        if isinstance(event_data_batch, EventDataBatch):
            if partition_id or partition_key:
                raise TypeError(
                    "partition_id and partition_key should be None when sending an EventDataBatch "
                    "because type EventDataBatch itself may have partition_id or partition_key"
                )
            to_send_batch = event_data_batch
        else:
            to_send_batch = self.create_batch(
                partition_id=partition_id, partition_key=partition_key
            )
            to_send_batch._load_events(  # pylint:disable=protected-access
                event_data_batch
            )
        partition_id = (
            to_send_batch._partition_id  # pylint:disable=protected-access
            or ALL_PARTITIONS
        )

        if len(to_send_batch) == 0:
            return

        send_timeout = kwargs.pop("timeout", None)
        try:
            cast(EventHubProducer, self._producers[partition_id]).send(
                to_send_batch, timeout=send_timeout
            )
        except (KeyError, AttributeError, EventHubError) as e:
            _LOGGER.info(
                "Producer for partition ID '{}' not available: {}. Rebuilding new producer.".format(partition_id, e))
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
         **WARNING: Setting partition_key of non-string value on the events to be sent is discouraged
         as the partition_key will be ignored by the Event Hub service and events will be assigned
         to all partitions using round-robin. Furthermore, there are SDKs for consuming events which expect
         partition_key to only be string type, they might fail to parse the non-string value.**
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
        if not self._max_message_size_on_link:
            self._get_max_mesage_size()

        max_size_in_bytes = kwargs.get("max_size_in_bytes", None)
        partition_id = kwargs.get("partition_id", None)
        partition_key = kwargs.get("partition_key", None)

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
        )

        return event_data_batch

    def get_eventhub_properties(self):
        # type:() -> Dict[str, Any]
        """Get properties of the Event Hub.

        Keys in the returned dictionary include:

            - `eventhub_name` (str)
            - `created_at` (UTC datetime.datetime)
            - `partition_ids` (list[str])

        :rtype: Dict[str, Any]
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
        :rtype: Dict[str, Any]
        :raises: :class:`EventHubError<azure.eventhub.exceptions.EventHubError>`
        """
        return super(EventHubProducerClient, self)._get_partition_properties(
            partition_id
        )

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
        _LOGGER.info("Closing ProducerClient")
        with self._lock:
            for pid in self._producers:
                if self._producers[pid]:
                    self._producers[pid].close()  # type: ignore
                self._producers[pid] = None
        super(EventHubProducerClient, self)._close()
