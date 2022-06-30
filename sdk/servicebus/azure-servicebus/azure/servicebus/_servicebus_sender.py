# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import time
import uuid
import datetime
import warnings
from typing import Any, TYPE_CHECKING, Union, List, Optional, Mapping, cast

import uamqp
from uamqp import SendClient, types
from uamqp.authentication.common import AMQPAuth

from ._base_handler import BaseHandler
from ._common import mgmt_handlers
from ._common.message import (
    ServiceBusMessage,
    ServiceBusMessageBatch,
)
from .amqp import AmqpAnnotatedMessage
from .exceptions import (
    OperationTimeoutError,
    _ServiceBusErrorPolicy,
)
from ._common.utils import (
    create_authentication,
    transform_messages_if_needed,
    send_trace_context_manager,
    trace_message,
)
from ._common.constants import (
    REQUEST_RESPONSE_CANCEL_SCHEDULED_MESSAGE_OPERATION,
    REQUEST_RESPONSE_SCHEDULE_MESSAGE_OPERATION,
    MGMT_REQUEST_SEQUENCE_NUMBERS,
    MGMT_REQUEST_SESSION_ID,
    MGMT_REQUEST_MESSAGE,
    MGMT_REQUEST_MESSAGES,
    MGMT_REQUEST_MESSAGE_ID,
    MGMT_REQUEST_PARTITION_KEY,
    SPAN_NAME_SCHEDULE,
)

if TYPE_CHECKING:
    from azure.core.credentials import (
        TokenCredential,
        AzureSasCredential,
        AzureNamedKeyCredential,
    )
    MessageTypes = Union[
        Mapping[str, Any],
        ServiceBusMessage,
        AmqpAnnotatedMessage,
        List[Union[Mapping[str, Any], ServiceBusMessage, AmqpAnnotatedMessage]],
    ]
    MessageObjTypes = Union[
        ServiceBusMessage,
        AmqpAnnotatedMessage,
        ServiceBusMessageBatch,
        List[Union[ServiceBusMessage, AmqpAnnotatedMessage]],
    ]

_LOGGER = logging.getLogger(__name__)


class SenderMixin(object):
    def _create_attribute(self, **kwargs):
        self._auth_uri = "sb://{}/{}".format(
            self.fully_qualified_namespace, self._entity_name
        )
        self._entity_uri = "amqps://{}/{}".format(
            self.fully_qualified_namespace, self._entity_name
        )
        self._error_policy = _ServiceBusErrorPolicy(
            max_retries=self._config.retry_total
        )
        self._name = kwargs.get("client_identifier","SBSender-{}".format(uuid.uuid4()))
        self._max_message_size_on_link = 0
        self.entity_name = self._entity_name

    def _set_msg_timeout(self, timeout=None, last_exception=None):
        # pylint: disable=protected-access
        if not timeout:
            self._handler._msg_timeout = 0
            return
        if timeout <= 0.0:
            if last_exception:
                error = last_exception
            else:
                error = OperationTimeoutError(message="Send operation timed out")
            _LOGGER.info("%r send operation timed out. (%r)", self._name, error)
            raise error
        self._handler._msg_timeout = timeout * 1000  # type: ignore

    @classmethod
    def _build_schedule_request(cls, schedule_time_utc, send_span, *messages):
        request_body = {MGMT_REQUEST_MESSAGES: []}
        for message in messages:
            if not isinstance(message, ServiceBusMessage):
                raise ValueError(
                    "Scheduling batch messages only supports iterables containing "
                    "ServiceBusMessage Objects. Received instead: {}".format(
                        message.__class__.__name__
                    )
                )
            message.scheduled_enqueue_time_utc = schedule_time_utc
            message = transform_messages_if_needed(message, ServiceBusMessage)
            trace_message(message, send_span)
            message_data = {}
            message_data[MGMT_REQUEST_MESSAGE_ID] = message.message_id
            if message.session_id:
                message_data[MGMT_REQUEST_SESSION_ID] = message.session_id
            if message.partition_key:
                message_data[MGMT_REQUEST_PARTITION_KEY] = message.partition_key
            message_data[MGMT_REQUEST_MESSAGE] = bytearray(
                message.message.encode_message()
            )
            request_body[MGMT_REQUEST_MESSAGES].append(message_data)
        return request_body


class ServiceBusSender(BaseHandler, SenderMixin):
    """The ServiceBusSender class defines a high level interface for
    sending messages to the Azure Service Bus Queue or Topic.

    **Please use the `get_<queue/topic>_sender` method of ~azure.servicebus.ServiceBusClient to create a
    ServiceBusSender instance.**

    :ivar fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
     The namespace format is: `<yournamespace>.servicebus.windows.net`.
    :vartype fully_qualified_namespace: str
    :ivar entity_name: The name of the entity that the client connects to.
    :vartype entity_name: str

    :param str fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
     The namespace format is: `<yournamespace>.servicebus.windows.net`.
    :param credential: The credential object used for authentication which
     implements a particular interface for getting tokens. It accepts
     credential objects generated by the azure-identity library and objects that implement the
     `get_token(self, *scopes)` method, or alternatively, an AzureSasCredential can be provided too.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureSasCredential
     or ~azure.core.credentials.AzureNamedKeyCredential
    :keyword str queue_name: The path of specific Service Bus Queue the client connects to.
    :keyword str topic_name: The path of specific Service Bus Topic the client connects to.
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the Service Bus service. Default is `TransportType.Amqp`.
    :paramtype transport_type: ~azure.servicebus.TransportType
    :keyword Dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :keyword str user_agent: If specified, this will be added in front of the built-in user agent string.
    :keyword str client_identifier: A string-based identifier to uniquely identify the client instance.
     Service Bus will associate it with some error messages for easier correlation of errors.
     If not specified, a unique id will be generated.
    """

    def __init__(
        self,
        fully_qualified_namespace: str,
        credential: Union["TokenCredential", "AzureSasCredential", "AzureNamedKeyCredential"],
        *,
        queue_name: Optional[str] = None,
        topic_name: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        if kwargs.get("entity_name"):
            super(ServiceBusSender, self).__init__(
                fully_qualified_namespace=fully_qualified_namespace,
                credential=credential,
                **kwargs
            )
        else:
            if queue_name and topic_name:
                raise ValueError(
                    "Queue/Topic name can not be specified simultaneously."
                )
            entity_name = queue_name or topic_name
            if not entity_name:
                raise ValueError(
                    "Queue/Topic name is missing. Please specify queue_name/topic_name."
                )
            super(ServiceBusSender, self).__init__(
                fully_qualified_namespace=fully_qualified_namespace,
                credential=credential,
                entity_name=str(entity_name),
                queue_name=queue_name,
                topic_name=topic_name,
                **kwargs
            )

        self._max_message_size_on_link = 0
        self._create_attribute(**kwargs)
        self._connection = kwargs.get("connection")

    @classmethod
    def _from_connection_string(cls, conn_str, **kwargs):
        # type: (str, Any) -> ServiceBusSender
        """Create a ServiceBusSender from a connection string.

        :param conn_str: The connection string of a Service Bus.
        :type conn_str: str
        :keyword str queue_name: The path of specific Service Bus Queue the client connects to.
         Only one of queue_name or topic_name can be provided.
        :keyword str topic_name: The path of specific Service Bus Topic the client connects to.
         Only one of queue_name or topic_name can be provided.
        :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
        :keyword transport_type: The type of transport protocol that will be used for communicating with
         the Service Bus service. Default is `TransportType.Amqp`.
        :paramtype transport_type: ~azure.servicebus.TransportType
        :keyword Dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
         Additionally the following keys may also be present: `'username', 'password'`.
        :keyword str user_agent: If specified, this will be added in front of the built-in user agent string.

        :rtype: ~azure.servicebus.ServiceBusSender

        :raises ~azure.servicebus.ServiceBusAuthenticationError: Indicates an issue in token/identity validity.
        :raises ~azure.servicebus.ServiceBusAuthorizationError: Indicates an access/rights related failure.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_servicebus_sender_from_conn_str_sync]
                :end-before: [END create_servicebus_sender_from_conn_str_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusSender from connection string.

        """
        constructor_args = cls._convert_connection_string_to_kwargs(conn_str, **kwargs)
        return cls(**constructor_args)

    def _create_handler(self, auth):
        # type: (AMQPAuth) -> None
        self._handler = SendClient(
            self._entity_uri,
            auth=auth,
            debug=self._config.logging_enable,
            properties=self._properties,
            error_policy=self._error_policy,
            client_name=self._name,
            keep_alive_interval=self._config.keep_alive,
            encoding=self._config.encoding,
        )

    def _open(self):
        # pylint: disable=protected-access
        if self._running:
            return
        if self._handler:
            self._handler.close()

        auth = None if self._connection else create_authentication(self)
        self._create_handler(auth)
        try:
            self._handler.open(connection=self._connection)
            while not self._handler.client_ready():
                time.sleep(0.05)
            self._running = True
            self._max_message_size_on_link = (
                self._handler.message_handler._link.peer_max_message_size
                or uamqp.constants.MAX_MESSAGE_LENGTH_BYTES
            )
        except:
            self._close_handler()
            raise

    def _send(self, message, timeout=None, last_exception=None):
        # type: (Union[ServiceBusMessage, ServiceBusMessageBatch], Optional[float], Exception) -> None
        self._open()
        default_timeout = self._handler._msg_timeout  # pylint: disable=protected-access
        try:
            self._set_msg_timeout(timeout, last_exception)
            self._handler.send_message(message.message)
        finally:  # reset the timeout of the handler back to the default value
            self._set_msg_timeout(default_timeout, None)

    def schedule_messages(
        self,
        messages: "MessageTypes",
        schedule_time_utc: datetime.datetime,
        *,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> List[int]:
        """Send Message or multiple Messages to be enqueued at a specific time.
        Returns a list of the sequence numbers of the enqueued messages.

        :param messages: The message or list of messages to schedule.
        :type messages: Union[~azure.servicebus.ServiceBusMessage, ~azure.servicebus.amqp.AmqpAnnotatedMessage,
         List[Union[~azure.servicebus.ServiceBusMessage, ~azure.servicebus.amqp.AmqpAnnotatedMessage]]]
        :param schedule_time_utc: The utc date and time to enqueue the messages.
        :type schedule_time_utc: ~datetime.datetime
        :keyword float timeout: The total operation timeout in seconds including all the retries. The value must be
         greater than 0 if specified. The default value is None, meaning no timeout.
        :rtype: List[int]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START scheduling_messages]
                :end-before: [END scheduling_messages]
                :language: python
                :dedent: 4
                :caption: Schedule a message to be sent in future
        """
        if kwargs:
            warnings.warn(f"Unsupported keyword args: {kwargs}")
        # pylint: disable=protected-access

        self._check_live()
        obj_messages = transform_messages_if_needed(messages, ServiceBusMessage)
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")

        with send_trace_context_manager(span_name=SPAN_NAME_SCHEDULE) as send_span:
            if isinstance(obj_messages, ServiceBusMessage):
                request_body = self._build_schedule_request(
                    schedule_time_utc, send_span, obj_messages
                )
            else:
                if len(obj_messages) == 0:
                    return []  # No-op on empty list.
                request_body = self._build_schedule_request(
                    schedule_time_utc, send_span, *obj_messages
                )
            if send_span:
                self._add_span_request_attributes(send_span)
            return self._mgmt_request_response_with_retry(
                REQUEST_RESPONSE_SCHEDULE_MESSAGE_OPERATION,
                request_body,
                mgmt_handlers.schedule_op,
                timeout=timeout,
            )

    def cancel_scheduled_messages(
        self,
        sequence_numbers: Union[int, List[int]],
        *,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> None:
        """
        Cancel one or more messages that have previously been scheduled and are still pending.

        :param sequence_numbers: The sequence numbers of the scheduled messages.
        :type sequence_numbers: int or list[int]
        :keyword float timeout: The total operation timeout in seconds including all the retries. The value must be
         greater than 0 if specified. The default value is None, meaning no timeout.
        :rtype: None
        :raises: ~azure.servicebus.exceptions.ServiceBusError if messages cancellation failed due to message already
         cancelled or enqueued.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START cancel_scheduled_messages]
                :end-before: [END cancel_scheduled_messages]
                :language: python
                :dedent: 4
                :caption: Cancelling messages scheduled to be sent in future
        """
        if kwargs:
            warnings.warn(f"Unsupported keyword args: {kwargs}")
        self._check_live()
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")
        if isinstance(sequence_numbers, int):
            numbers = [types.AMQPLong(sequence_numbers)]
        else:
            numbers = [types.AMQPLong(s) for s in sequence_numbers]
        if len(numbers) == 0:
            return None  # no-op on empty list.
        request_body = {MGMT_REQUEST_SEQUENCE_NUMBERS: types.AMQPArray(numbers)}
        return self._mgmt_request_response_with_retry(
            REQUEST_RESPONSE_CANCEL_SCHEDULED_MESSAGE_OPERATION,
            request_body,
            mgmt_handlers.default,
            timeout=timeout,
        )

    def send_messages(
        self,
        message: Union["MessageTypes", ServiceBusMessageBatch],
        *,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> None:
        """Sends message and blocks until acknowledgement is received or operation times out.

        If a list of messages was provided, attempts to send them as a single batch, throwing a
        `ValueError` if they cannot fit in a single batch.

        :param message: The ServiceBus message to be sent.
        :type message: Union[~azure.servicebus.ServiceBusMessage, ~azure.servicebus.ServiceBusMessageBatch,
         ~azure.servicebus.amqp.AmqpAnnotatedMessage, List[Union[~azure.servicebus.ServiceBusMessage,
         ~azure.servicebus.amqp.AmqpAnnotatedMessage]]]
        :keyword Optional[float] timeout: The total operation timeout in seconds including all the retries.
         The value must be greater than 0 if specified. The default value is None, meaning no timeout.
        :rtype: None
        :raises:
                :class: ~azure.servicebus.exceptions.OperationTimeoutError if sending times out.
                :class: ~azure.servicebus.exceptions.MessageSizeExceededError if the size of the message is over
                  service bus frame size limit.
                :class: ~azure.servicebus.exceptions.ServiceBusError when other errors happen such as connection
                 error, authentication error, and any unexpected errors.
                 It's also the top-level root class of above errors.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START send_sync]
                :end-before: [END send_sync]
                :language: python
                :dedent: 4
                :caption: Send message.

        """
        if kwargs:
            warnings.warn(f"Unsupported keyword args: {kwargs}")
        self._check_live()
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")

        with send_trace_context_manager() as send_span:
            if isinstance(message, ServiceBusMessageBatch):
                obj_message = message  # type: MessageObjTypes
            else:
                obj_message = transform_messages_if_needed(  # type: ignore
                    message, ServiceBusMessage
                )
                try:
                    batch = self.create_message_batch()
                    batch._from_list(obj_message, send_span)  # type: ignore # pylint: disable=protected-access
                    obj_message = batch
                except TypeError:  # Message was not a list or generator. Do needed tracing.
                    trace_message(cast(ServiceBusMessage, obj_message), send_span)

            if (
                isinstance(obj_message, ServiceBusMessageBatch)
                and len(obj_message) == 0
            ):  # pylint: disable=len-as-condition
                return  # Short circuit noop if an empty list or batch is provided.

            if send_span:
                self._add_span_request_attributes(send_span)

            self._do_retryable_operation(
                self._send,
                message=obj_message,
                timeout=timeout,
                operation_requires_timeout=True,
                require_last_exception=True,
            )

    def create_message_batch(
        self,
        max_size_in_bytes: Optional[int] = None
    ) -> ServiceBusMessageBatch:
        """Create a ServiceBusMessageBatch object with the max size of all content being constrained by
        max_size_in_bytes. The max_size should be no greater than the max allowed message size defined by the service.

        :param Optional[int] max_size_in_bytes: The maximum size of bytes data that a ServiceBusMessageBatch object can
         hold. By default, the value is determined by your Service Bus tier.
        :rtype: ~azure.servicebus.ServiceBusMessageBatch

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_batch_sync]
                :end-before: [END create_batch_sync]
                :language: python
                :dedent: 4
                :caption: Create ServiceBusMessageBatch object within limited size

        """
        self._check_live()
        if not self._max_message_size_on_link:
            self._open_with_retry()

        if max_size_in_bytes and max_size_in_bytes > self._max_message_size_on_link:
            raise ValueError(
                "Max message size: {} is too large, acceptable max batch size is: {} bytes.".format(
                    max_size_in_bytes, self._max_message_size_on_link
                )
            )

        return ServiceBusMessageBatch(
            max_size_in_bytes=(max_size_in_bytes or self._max_message_size_on_link)
        )

    @property
    def client_identifier(self) -> str:
        """
        Get the ServiceBusSender client_identifier associated with the sender instance.

        :rtype: str
        """
        return self._name

    def __str__(self) -> str:
        return f"ServicebusSender client identifier: {self.client_identifier} for entity: {self.entity_name}"
