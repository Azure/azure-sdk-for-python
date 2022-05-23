# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import uuid
import logging
import time
import threading
from typing import (
    Iterable,
    Union,
    Optional,
    Any,
    AnyStr,
    List,
    TYPE_CHECKING,
)  # pylint: disable=unused-import

from azure.core.tracing import AbstractSpan

from .exceptions import OperationTimeoutError
from ._common import EventData, EventDataBatch
from ._client_base import ConsumerProducerMixin
from ._utils import (
    create_properties,
    set_message_partition_key,
    trace_message,
    send_context_manager,
    transform_outbound_single_message,
)
from ._constants import (
    TIMEOUT_SYMBOL,
    NO_RETRY_ERRORS,
    CUSTOM_CONDITION_BACKOFF
)
from ._pyamqp import (
    error,
    utils as pyamqp_utils,
    SendClient
)

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from uamqp.authentication import JWTTokenAuth  # pylint: disable=ungrouped-imports
    from ._producer_client import EventHubProducerClient


def _set_partition_key(event_datas, partition_key):
    # type: (Iterable[EventData], AnyStr) -> Iterable[EventData]
    for ed in iter(event_datas):
        set_message_partition_key(ed.message, partition_key)
        yield ed


def _set_trace_message(event_datas, parent_span=None):
    # type: (Iterable[EventData], Optional[AbstractSpan]) -> Iterable[EventData]
    for ed in iter(event_datas):
        trace_message(ed, parent_span)
        yield ed


class EventHubProducer(
    ConsumerProducerMixin
):  # pylint:disable=too-many-instance-attributes
    """
    A producer responsible for transmitting EventData to a specific Event Hub,
    grouped together in batches. Depending on the options specified at creation, the producer may
    be created to allow event data to be automatically routed to an available partition or specific
    to a partition.

    Please use the method `create_producer` on `EventHubClient` for creating `EventHubProducer`.

    :param client: The parent EventHubProducerClient.
    :type client: ~azure.eventhub.EventHubProducerClient
    :param target: The URI of the EventHub to send to.
    :type target: str
    :keyword str partition: The specific partition ID to send to. Default is `None`, in which case the service
     will assign to all partitions using round-robin.
    :keyword float send_timeout: The timeout in seconds for an individual event to be sent from the time that it is
     queued. Default value is 60 seconds. If set to 0, there will be no timeout.
    :keyword int keep_alive: The time interval in seconds between pinging the connection to keep it alive during
     periods of inactivity. The default value is `None`, i.e. no keep alive pings.
    :keyword bool auto_reconnect: Whether to automatically reconnect the producer if a retryable error occurs.
     Default value is `True`.
    """

    def __init__(self, client, target, **kwargs):
        # type: (EventHubProducerClient, str, Any) -> None
        partition = kwargs.get("partition", None)
        send_timeout = kwargs.get("send_timeout", 60)
        keep_alive = kwargs.get("keep_alive", None)
        auto_reconnect = kwargs.get("auto_reconnect", True)
        idle_timeout = kwargs.get("idle_timeout", None)

        self.running = False
        self.closed = False

        self._max_message_size_on_link = None
        self._client = client
        self._target = target
        self._partition = partition
        self._timeout = send_timeout
        self._idle_timeout = idle_timeout if idle_timeout else None
        self._error = None
        self._keep_alive = keep_alive
        self._auto_reconnect = auto_reconnect
        self._retry_policy = error.RetryPolicy(
            retry_total=self._client._config.max_retries,  # pylint: disable=protected-access
            no_retry_condition=NO_RETRY_ERRORS,
            custom_condition_backoff=CUSTOM_CONDITION_BACKOFF
        )
        self._reconnect_backoff = 1
        self._name = "EHProducer-{}".format(uuid.uuid4())
        self._unsent_events = []  # type: List[Any]
        if partition:
            self._target += "/Partitions/" + partition
            self._name += "-partition{}".format(partition)
        self._handler = None  # type: Optional[SendClient]
        self._condition = None  # type: Optional[Exception]
        self._lock = threading.Lock()
        self._link_properties = {TIMEOUT_SYMBOL: pyamqp_utils.amqp_long_value(int(self._timeout * 1000))}


    def _create_handler(self, auth):
        # type: (JWTTokenAuth) -> None
        transport_type = self._client._config.transport_type   # pylint:disable=protected-access
        custom_endpoint_address = self._client._config.custom_endpoint_address # pylint: disable=protected-access
        hostname = self._client._address.hostname  # pylint: disable=protected-access
        if transport_type.name == 'AmqpOverWebsocket':
            hostname += '/$servicebus/websocket/'
            if custom_endpoint_address:
                custom_endpoint_address += '/$servicebus/websocket/' 
        self._handler = SendClient(
            hostname,
            self._target,
            auth=auth,
            idle_timeout=self._idle_timeout,
            network_trace=self._client._config.network_tracing, # pylint:disable=protected-access
            transport_type=transport_type,
            http_proxy=self._client._config.http_proxy, # pylint:disable=protected-access
            retry_policy=self._retry_policy,
            keep_alive_interval=self._keep_alive,
            client_name=self._name,
            link_properties=self._link_properties,
            properties=create_properties(self._client._config.user_agent),  # pylint: disable=protected-access
            custom_endpoint_address=custom_endpoint_address,
            connection_verify=self._client._config.connection_verify
        )

    def _open_with_retry(self):
        # type: () -> None
        return self._do_retryable_operation(self._open, operation_need_param=False)

    def _send_event_data(self, timeout_time=None):
        # type: (Optional[float]) -> None
        if self._unsent_events:
            self._open()
            timeout = timeout_time - time.time() if timeout_time else 0
            self._handler.send_message(self._unsent_events[0], timeout=timeout)
            self._unsent_events = None

    def _send_event_data_with_retry(self, timeout=None):
        # type: (Optional[float]) -> None
        return self._do_retryable_operation(self._send_event_data, timeout=timeout)

    @staticmethod
    def _wrap_eventdata(
        event_data,  # type: Union[EventData, EventDataBatch, Iterable[EventData]]
        span,  # type: Optional[AbstractSpan]
        partition_key,  # type: Optional[AnyStr]
    ):
        # type: (...) -> Union[EventData, EventDataBatch]
        if isinstance(event_data, EventData):
            outgoing_event_data = transform_outbound_single_message(event_data, EventData)
            if partition_key:
                set_message_partition_key(outgoing_event_data.message, partition_key)
            wrapper_event_data = outgoing_event_data
            trace_message(wrapper_event_data, span)
        else:
            if isinstance(
                event_data, EventDataBatch
            ):  # The partition_key in the param will be omitted.
                if (
                    partition_key and partition_key != event_data._partition_key  # pylint: disable=protected-access
                ):
                    raise ValueError(
                        "The partition_key does not match the one of the EventDataBatch"
                    )

                for event in event_data.message.data:  # pylint: disable=protected-access
                    trace_message(event, span)
                wrapper_event_data = event_data  # type:ignore
            else:
                if partition_key:
                    event_data = _set_partition_key(event_data, partition_key)
                event_data = _set_trace_message(event_data, span)
                wrapper_event_data = EventDataBatch._from_batch(event_data, partition_key)  # type: ignore  # pylint: disable=protected-access
        return wrapper_event_data

    def send(
        self,
        event_data,  # type: Union[EventData, EventDataBatch, Iterable[EventData]]
        partition_key=None,  # type: Optional[AnyStr]
        timeout=None,  # type: Optional[float]
    ):
        # type:(...) -> None
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        :param event_data: The event to be sent. It can be an EventData object, or iterable of EventData objects
        :type event_data: ~azure.eventhub.common.EventData, Iterator, Generator, list
        :param partition_key: With the given partition_key, event data will land to
         a particular partition of the Event Hub decided by the service. partition_key
         could be omitted if event_data is of type ~azure.eventhub.EventDataBatch.
        :type partition_key: str
        :param timeout: The maximum wait time to send the event data.
         If not specified, the default wait time specified when the producer was created will be used.
        :type timeout: float

        :raises: ~azure.eventhub.exceptions.AuthenticationError,
                 ~azure.eventhub.exceptions.ConnectError,
                 ~azure.eventhub.exceptions.ConnectionLostError,
                 ~azure.eventhub.exceptions.EventDataError,
                 ~azure.eventhub.exceptions.EventDataSendError,
                 ~azure.eventhub.exceptions.EventHubError
        :return: None
        :rtype: None
        """
        # Tracing code
        with self._lock:
            with send_context_manager() as child:
                self._check_closed()
                wrapper_event_data = self._wrap_eventdata(event_data, child, partition_key)
                if child:
                    self._client._add_span_request_attributes(  # pylint: disable=protected-access
                        child
                    )

                try:
                    self._open()
                    self._handler.send_message(wrapper_event_data.message, timeout=timeout)
                except TimeoutError as exception:
                    raise OperationTimeoutError(message=str(exception), details=exception)
                except Exception as exception:  # pylint:disable=broad-except
                    raise self._handle_exception(exception)

    def close(self):
        # type:() -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        with self._lock:
            super(EventHubProducer, self).close()
