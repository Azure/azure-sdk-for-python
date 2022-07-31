# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from concurrent.futures import ThreadPoolExecutor
import logging
import threading
import time
from typing import (
    Any,
    Union,
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Callable,
    cast,
    overload,
)
from typing_extensions import Literal

from .exceptions import ConnectError, EventHubError
from .amqp import AmqpAnnotatedMessage
from ._client_base import ClientBase
from ._producer import EventHubProducer
from ._constants import ALL_PARTITIONS, MAX_MESSAGE_LENGTH_BYTES
from ._common import EventDataBatch, EventData
from ._constants import ALL_PARTITIONS
from ._producer import EventHubProducer
from ._buffered_producer import BufferedProducerDispatcher
from ._utils import set_event_partition_key
from .amqp import AmqpAnnotatedMessage
from .exceptions import ConnectError, EventHubError

if TYPE_CHECKING:
    from ._client_base import CredentialTypes

SendEventTypes = List[Union[EventData, AmqpAnnotatedMessage]]

_LOGGER = logging.getLogger(__name__)


class EventHubProducerClient(
    ClientBase
):  # pylint: disable=client-accepts-api-version-keyword
    # pylint: disable=too-many-instance-attributes
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
    :keyword bool buffered_mode: If True, the producer client will collect events in a buffer, efficiently batch,
     then publish. Default is False.
    :keyword buffer_concurrency: The ThreadPoolExecutor to be used for publishing events
     or the number of workers for the ThreadPoolExecutor. Default is None and a ThreadPoolExecutor
     with the default number of workers will be created per
     https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
    :paramtype buffer_concurrency: ThreadPoolExecutor or int or None
    :keyword on_success: The callback to be called once a batch has been successfully published.
     The callback takes two parameters:
        - `events`: The list of events that have been successfully published
        - `partition_id`: The partition id that the events in the list have been published to.
     The callback function should be defined like: `on_success(events, partition_id)`.
     It is required when `buffered_mode` is True while optional if `buffered_mode` is False.
    :paramtype on_success: Optional[Callable[[SendEventTypes, Optional[str]], None]]
    :keyword on_error: The callback to be called once a batch has failed to be published.
     The callback function should be defined like: `on_error(events, partition_id, error)`, where:
        - `events`: The list of events that failed to be published,
        - `partition_id`: The partition id that the events in the list have been tried to be published to and
        - `error`: The exception related to the sending failure.
     If `buffered_mode` is False, `on_error` callback is optional and errors will be handled as follows:
        - If an `on_error` callback is passed during the producer client instantiation,
            then error information will be passed to the `on_error` callback, which will then be called.
        - If an `on_error` callback is not passed in during client instantiation,
            then the error will be raised by default.
     If `buffered_mode` is True, `on_error` callback is required and errors will be handled as follows:
        - If events fail to enqueue within the given timeout, then an error will be directly raised.
        - If events fail to send after enqueuing successfully, the `on_error` callback will be called.
    :paramtype on_error: Optional[Callable[[SendEventTypes, Optional[str], Exception], None]]
    :keyword int max_buffer_length: Buffered mode only.
     The total number of events per partition that can be buffered before a flush will be triggered.
     The default value is 1500 in buffered mode.
    :keyword Optional[float] max_wait_time: Buffered mode only.
     The amount of time to wait for a batch to be built with events in the buffer before publishing.
     The default value is 1 in buffered mode.
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

    @overload
    def __init__(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        credential: "CredentialTypes",
        *,
        buffered_mode: Literal[False] = False,
        **kwargs: Any
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        credential: "CredentialTypes",
        *,
        buffered_mode: Literal[True],
        buffer_concurrency: Optional[Union[ThreadPoolExecutor, int]] = None,
        on_error: Callable[[SendEventTypes, Optional[str], Exception], None],
        on_success: Callable[[SendEventTypes, Optional[str]], None],
        max_buffer_length: int = 1500,
        max_wait_time: float = 1,
        **kwargs: Any
    ) -> None:
        ...

    def __init__(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        credential: "CredentialTypes",
        *,
        buffered_mode: bool = False,
        on_error: Optional[
            Callable[[SendEventTypes, Optional[str], Exception], None]
        ] = None,
        on_success: Optional[Callable[[SendEventTypes, Optional[str]], None]] = None,
        max_buffer_length: Optional[int] = None,
        max_wait_time: Optional[float] = None,
        **kwargs: Any
    ) -> None:
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
        self._buffered_mode = buffered_mode
        self._on_success = on_success
        self._on_error = on_error
        self._buffered_producer_dispatcher = None
        self._max_wait_time = max_wait_time
        self._max_buffer_length = max_buffer_length
        self._executor = kwargs.get("buffer_concurrency")

        if self._buffered_mode:
            setattr(self, "send_batch", self._buffered_send_batch)
            setattr(self, "send_event", self._buffered_send_event)
            if not self._on_error:
                raise TypeError(
                    "EventHubProducerClient in buffered mode missing 1 required keyword argument: 'on_error'"
                )
            if not self._on_success:
                raise TypeError(
                    "EventHubProducerClient in buffered mode missing 1 required keyword argument: 'on_success'"
                )
            if self._max_wait_time is None:
                self._max_wait_time = 1
            if self._max_wait_time <= 0:
                raise ValueError(
                    "'max_wait_time' must be a float greater than 0 in buffered mode"
                )
            if self._max_buffer_length is None:
                self._max_buffer_length = 1500
            if self._max_buffer_length <= 0:
                raise ValueError(
                    "'max_buffer_length' must be an integer greater than 0 in buffered mode"
                )
            if isinstance(self._executor, int) and self._executor <= 0:
                raise ValueError(
                    "'buffer_concurrency' must be an integer greater than 0 in buffered mode"
                )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _buffered_send(self, events, **kwargs):
        try:
            self._buffered_producer_dispatcher.enqueue_events(events, **kwargs)
        except AttributeError:
            self._get_partitions()
            self._get_max_message_size()
            self._buffered_producer_dispatcher = BufferedProducerDispatcher(
                self._partition_ids,
                self._on_success,
                self._on_error,
                self._create_producer,
                self.eventhub_name,
                self._max_message_size_on_link,
                max_wait_time=self._max_wait_time,
                max_buffer_length=self._max_buffer_length,
                executor=self._executor,
                amqp_transport=self._amqp_transport
            )
            self._buffered_producer_dispatcher.enqueue_events(events, **kwargs)

    def _batch_preparer(self, event_data_batch, **kwargs):
        partition_id = kwargs.pop("partition_id", None)
        partition_key = kwargs.pop("partition_key", None)

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
            to_send_batch._load_events( # pylint:disable=protected-access
                event_data_batch
            )

        return (
            to_send_batch,
            to_send_batch._partition_id,    # pylint:disable=protected-access
            partition_key,
        )

    def _buffered_send_batch(self, event_data_batch, **kwargs):
        batch, pid, pkey = self._batch_preparer(event_data_batch, **kwargs)

        if len(batch) == 0:
            return

        timeout = kwargs.get("timeout")
        timeout_time = time.time() + timeout if timeout else None

        self._buffered_send(
            event_data_batch,
            partition_id=pid,
            partition_key=pkey,
            timeout_time=timeout_time,
        )

    def _buffered_send_event(self, event, **kwargs):
        partition_key = kwargs.get("partition_key")
        set_event_partition_key(event, partition_key)
        timeout = kwargs.get("timeout")
        timeout_time = time.time() + timeout if timeout else None
        self._buffered_send(
            event,
            partition_id=kwargs.get("partition_id"),
            partition_key=partition_key,
            timeout_time=timeout_time,
        )

    def _get_partitions(self):
        # type: () -> None
        if not self._partition_ids:
            self._partition_ids = self.get_partition_ids()  # type: ignore
            for p_id in cast(List[str], self._partition_ids):
                self._producers[p_id] = None

    def _get_max_message_size(self):
        # type: () -> None
        # pylint: disable=protected-access,line-too-long
        with self._lock:
            if not self._max_message_size_on_link:
                cast(
                    EventHubProducer, self._producers[ALL_PARTITIONS]
                )._open_with_retry()
                self._max_message_size_on_link = (
                    self._amqp_transport.get_remote_max_message_size(
                        self._producers[ALL_PARTITIONS]._handler  # type: ignore
                    )
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
            amqp_transport=self._amqp_transport,
        )
        return handler

    @classmethod
    @overload
    def from_connection_string(
        cls,
        conn_str: str,
        *,
        eventhub_name: Optional[str] = None,
        buffered_mode: Literal[False] = False,
        **kwargs: Any
    ) -> "EventHubProducerClient":
        ...

    @classmethod
    @overload
    def from_connection_string(
        cls,
        conn_str: str,
        *,
        eventhub_name: Optional[str] = None,
        buffered_mode: Literal[True],
        buffer_concurrency: Optional[Union[ThreadPoolExecutor, int]] = None,
        on_error: Callable[[SendEventTypes, Optional[str], Exception], None],
        on_success: Callable[[SendEventTypes, Optional[str]], None],
        max_buffer_length: int = 1500,
        max_wait_time: float = 1,
        **kwargs: Any
    ) -> "EventHubProducerClient":
        ...

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        *,
        eventhub_name: Optional[str] = None,
        buffered_mode: bool = False,
        on_error: Optional[
            Callable[[SendEventTypes, Optional[str], Exception], None]
        ] = None,
        on_success: Optional[Callable[[SendEventTypes, Optional[str]], None]] = None,
        max_buffer_length: Optional[int] = None,
        max_wait_time: Optional[float] = None,
        **kwargs: Any
    ) -> "EventHubProducerClient":
        """Create an EventHubProducerClient from a connection string.

        :param str conn_str: The connection string of an Event Hub.
        :keyword str eventhub_name: The path of the specific Event Hub to connect the client to.
        :keyword bool buffered_mode: If True, the producer client will collect events in a buffer, efficiently batch,
         then publish. Default is False.
        :keyword buffer_concurrency: The ThreadPoolExecutor to be used for publishing events
         or the number of workers for the ThreadPoolExecutor. Default is None and a ThreadPoolExecutor
         with the default number of workers will be created per
         https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
        :paramtype buffer_concurrency: ThreadPoolExecutor or int or None
        :keyword on_success: The callback to be called once a batch has been successfully published.
         The callback takes two parameters:
            - `events`: The list of events that have been successfully published
            - `partition_id`: The partition id that the events in the list have been published to.
         The callback function should be defined like: `on_success(events, partition_id)`.
         Required when `buffered_mode` is True while optional if `buffered_mode` is False.
        :paramtype on_success: Optional[Callable[[SendEventTypes, Optional[str]], None]]
        :keyword on_error: The callback to be called once a batch has failed to be published.
         Required when in `buffered_mode` is True while optional if `buffered_mode` is False.
         The callback function should be defined like: `on_error(events, partition_id, error)`, where:
            - `events`: The list of events that failed to be published,
            - `partition_id`: The partition id that the events in the list have been tried to be published to and
            - `error`: The exception related to the sending failure.
         If `buffered_mode` is False, `on_error` callback is optional and errors will be handled as follows:
            - If an `on_error` callback is passed during the producer client instantiation,
                then error information will be passed to the `on_error` callback, which will then be called.
            - If an `on_error` callback is not passed in during client instantiation,
                then the error will be raised by default.
         If `buffered_mode` is True, `on_error` callback is required and errors will be handled as follows:
            - If events fail to enqueue within the given timeout, then an error will be directly raised.
            - If events fail to send after enqueuing successfully, the `on_error` callback will be called.
        :paramtype on_error: Optional[Callable[[SendEventTypes, Optional[str], Exception], None]]
        :keyword int max_buffer_length: Buffered mode only.
         The total number of events per partition that can be buffered before a flush will be triggered.
         The default value is 1500 in buffered mode.
        :keyword Optional[float] max_wait_time: Buffered mode only.
         The amount of time to wait for a batch to be built with events in the buffer before publishing.
         The default value is 1 in buffered mode.
        :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
        :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
         Additionally the following keys may also be present: `'username', 'password'`.
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
        constructor_args = cls._from_connection_string(
            conn_str,
            eventhub_name=eventhub_name,
            buffered_mode=buffered_mode,
            on_success=on_success,
            on_error=on_error,
            max_buffer_length=max_buffer_length,
            max_wait_time=max_wait_time,
            **kwargs
        )
        return cls(**constructor_args)

    def send_event(self, event_data, **kwargs):
        # type: (Union[EventData, AmqpAnnotatedMessage], Any) -> None
        """
        Sends an event data.
        By default, the method will block until acknowledgement is received or operation times out.
        If the `EventHubProducerClient` is configured to run in buffered mode, the method will try enqueuing
        the events into buffer within the given time if specified and return.
        The producer will do automatic sending in the background in buffered mode.

         If `buffered_mode` is False, `on_error` callback is optional and errors will be handled as follows:
            - If an `on_error` callback is passed during the producer client instantiation,
                then error information will be passed to the `on_error` callback, which will then be called.
            - If an `on_error` callback is not passed in during client instantiation,
                then the error will be raised by default.

         If `buffered_mode` is True, `on_error` callback is required and errors will be handled as follows:
            - If events fail to enqueue within the given timeout, then an error will be directly raised.
            - If events fail to send after enqueuing successfully, the `on_error` callback will be called.

        :param event_data: The `EventData` object to be sent.
        :type event_data: Union[~azure.eventhub.EventData, ~azure.eventhub.amqp.AmqpAnnotatedMessage]
        :keyword float timeout: The maximum wait time to send the event data in non-buffered mode or the
         maximum wait time to enqueue the event data into the buffer in buffered mode.
         In non-buffered mode, the default wait time specified when the producer
         was created will be used. In buffered mode, the default wait time is None.
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
        :raises OperationTimeoutError: If the value specified by the timeout parameter elapses before the event can be
         sent in non-buffered mode or the events can be enqueued into the buffered in buffered mode.
        """
        input_pid = kwargs.get("partition_id")
        pid = input_pid or ALL_PARTITIONS
        partition_key = kwargs.get("partition_key")
        send_timeout = kwargs.get("timeout")
        try:
            try:
                cast(EventHubProducer, self._producers[pid]).send(
                    event_data, partition_key=partition_key, timeout=send_timeout
                )
            except (KeyError, AttributeError, EventHubError):
                self._start_producer(pid, send_timeout)
                cast(EventHubProducer, self._producers[pid]).send(
                    event_data, partition_key=partition_key, timeout=send_timeout
                )
            if self._on_success:
                self._on_success([event_data], input_pid)
        except Exception as exc:  # pylint: disable=broad-except
            if self._on_error:
                self._on_error([event_data], input_pid, exc)
            else:
                raise

    def send_batch(self, event_data_batch, **kwargs):
        # type: (Union[EventDataBatch, SendEventTypes], Any) -> None
        # pylint: disable=protected-access
        """
        Sends a batch of event data.
        By default, the method will block until acknowledgement is received or operation times out.
        If the `EventHubProducerClient` is configured to run in buffered mode, the method will try enqueuing
        the events into buffer within the given time if specified and return.
        The producer will do automatic sending in the background in buffered mode.

        If `buffered_mode` is False, `on_error` callback is optional and errors will be handled as follows:
           - If an `on_error` callback is passed during the producer client instantiation,
               then error information will be passed to the `on_error` callback, which will then be called.
           - If an `on_error` callback is not passed in during client instantiation,
               then the error will be raised by default.

        If `buffered_mode` is True, `on_error` callback is required and errors will be handled as follows:
           - If events fail to enqueue within the given timeout, then an error will be directly raised.
           - If events fail to send after enqueuing successfully, the `on_error` callback will be called.

        In buffered mode, sending a batch will remain intact and sent as a single unit.
        The batch will not be rearranged. This may result in inefficiency of sending events.

        If you're sending a finite list of `EventData` or `AmqpAnnotatedMessage` and you know it's within the
        event hub frame size limit, you can send them with a `send_batch` call. Otherwise, use :meth:`create_batch`
        to create `EventDataBatch` and add either `EventData` or `AmqpAnnotatedMessage` into the batch one by one
        until the size limit, and then call this method to send out the batch.

        :param event_data_batch: The `EventDataBatch` object to be sent or a list of `EventData` to be sent in a batch.
         All `EventData` or `AmqpAnnotatedMessage` in the list or `EventDataBatch` will land on the same partition.
        :type event_data_batch: Union[~azure.eventhub.EventDataBatch, List[Union[~azure.eventhub.EventData,
            ~azure.eventhub.amqp.AmqpAnnotatedMessage]]
        :keyword float timeout: The maximum wait time to send the event data in non-buffered mode or the
         maximum wait time to enqueue the event data into the buffer in buffered mode.
         In non-buffered mode, the default wait time specified when the producer
         was created will be used. In buffered mode, the default wait time is None.
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
        :raises OperationTimeoutError: If the value specified by the timeout parameter elapses before the event can be
         sent in non-buffered mode or the events can not be enqueued into the buffered in buffered mode.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
                :start-after: [START eventhub_producer_client_send_sync]
                :end-before: [END eventhub_producer_client_send_sync]
                :language: python
                :dedent: 4
                :caption: Sends event data

        """
        batch, pid, pkey = self._batch_preparer(event_data_batch, **kwargs)

        if len(batch) == 0:
            return

        partition_id = pid or ALL_PARTITIONS
        send_timeout = kwargs.pop("timeout", None)

        try:
            try:
                cast(EventHubProducer, self._producers[partition_id]).send(
                    batch, partition_key=pkey, timeout=send_timeout
                )
                if self._on_success:
                    self._on_success(batch._internal_events, pid)
            except (KeyError, AttributeError, EventHubError):
                self._start_producer(partition_id, send_timeout)
                cast(EventHubProducer, self._producers[partition_id]).send(
                    batch, partition_key=pkey, timeout=send_timeout
                )
                if self._on_success:
                    self._on_success(batch._internal_events, pid)
        except Exception as exc:  # pylint: disable=broad-except
            if self._on_error:
                self._on_error(batch._internal_events, pid, exc)
            else:
                raise

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
            self._get_max_message_size()

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
            amqp_transport=self._amqp_transport,
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

    def flush(self, **kwargs: Any) -> None:
        """
        Buffered mode only.
        Flush events in the buffer to be sent immediately if the client is working in buffered mode.

        :keyword Optional[float] timeout: Timeout to flush the buffered events, default is None which means no timeout.
        :rtype: None
        :raises EventDataSendError: If the producer fails to flush the buffer within the given timeout
         in buffered mode.
        """
        with self._lock:
            if self._buffered_mode and self._buffered_producer_dispatcher:
                timeout = kwargs.get("timeout")
                timeout_time = time.time() + timeout if timeout else None
                self._buffered_producer_dispatcher.flush(timeout_time=timeout_time)

    def close(self, *, flush: bool = True, **kwargs: Any) -> None:
        """Close the Producer client underlying AMQP connection and links.

        :keyword bool flush: Buffered mode only. If set to True, events in the buffer will be sent
         immediately. Default is True.
        :keyword Optional[float] timeout: Buffered mode only. Timeout to close the producer.
         Default is None which means no timeout.
        :rtype: None
        :raises EventHubError: If an error occurred when flushing the buffer if `flush` is set to True or closing the
         underlying AMQP connections in buffered mode.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
                :start-after: [START eventhub_producer_client_close_sync]
                :end-before: [END eventhub_producer_client_close_sync]
                :language: python
                :dedent: 4
                :caption: Close down the client.

        """
        with self._lock:
            if self._buffered_mode and self._buffered_producer_dispatcher:
                timeout = kwargs.get("timeout")
                timeout_time = time.time() + timeout if timeout else None
                self._buffered_producer_dispatcher.close(
                    flush=flush, timeout_time=timeout_time, raise_error=True
                )
                self._buffered_producer_dispatcher = None

            for pid in self._producers:
                if self._producers[pid]:
                    self._producers[pid].close()  # type: ignore
                self._producers[pid] = None
        super(EventHubProducerClient, self)._close()

    def get_buffered_event_count(self, partition_id: str) -> Optional[int]:
        """
        The number of events that are buffered and waiting to be published for a given partition.
         Returns None in non-buffered mode. **NOTE: The event buffer is processed in a background
         thread, therefore the number of events in the buffer reported by this API should be
         considered only an approximation and is only recommend for use in debugging. For a
         partition ID that has no events buffered, 0 will be returned regardless of whether that
         partition ID actually exists within the Event Hub.**


        :param str partition_id: The target partition ID.
        :rtype: int or None
        """
        if not self._buffered_mode:
            return None

        try:
            return cast(
                BufferedProducerDispatcher, self._buffered_producer_dispatcher
            ).get_buffered_event_count(partition_id)
        except AttributeError:
            return 0

    @property
    def total_buffered_event_count(self) -> Optional[int]:
        """
        The total number of events that are currently buffered and waiting to be published,
         across all partitions. Returns None in non-buffered mode. **NOTE: The event buffer
         is processed in a background thread, therefore the number of events in the buffer
         reported by this API should be considered only an approximation and is only recommend
         for use in debugging.**

        :rtype: int or None
        """
        if not self._buffered_mode:
            return None

        try:
            return cast(
                BufferedProducerDispatcher, self._buffered_producer_dispatcher
            ).total_buffered_event_count
        except AttributeError:
            return 0
