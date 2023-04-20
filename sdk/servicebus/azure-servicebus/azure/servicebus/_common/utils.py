# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from __future__ import annotations
import sys
import datetime
import logging
import functools
import platform
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Type,
    TYPE_CHECKING,
    Union,
    Tuple,
    cast,
    Callable
)
from contextlib import contextmanager
from datetime import timezone

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from azure.core.settings import settings
from azure.core.tracing import SpanKind, Link

from .._version import VERSION
from .constants import (
    JWT_TOKEN_SCOPE,
    TOKEN_TYPE_JWT,
    TOKEN_TYPE_SASTOKEN,
    DEAD_LETTER_QUEUE_SUFFIX,
    TRANSFER_DEAD_LETTER_QUEUE_SUFFIX,
    USER_AGENT_PREFIX,
    SPAN_NAME_SEND,
    SPAN_NAME_MESSAGE,
    DIAGNOSTIC_ID_PROPERTY,
    TRACE_PARENT_PROPERTY,
    TRACE_STATE_PROPERTY,
    TRACE_NAMESPACE,
    TRACE_NAMESPACE_ATTRIBUTE,
    TRACE_COMPONENT_PROPERTY,
    TRACE_COMPONENT,
    TRACE_PROPERTY_ENCODING,
    TRACE_ENQUEUED_TIME_PROPERTY,
    TRACE_MESSAGING_SYSTEM_ATTRIBUTE,
    TRACE_MESSAGING_SYSTEM,
    TRACE_NET_PEER_NAME_ATTRIBUTE,
    TRACE_MESSAGING_OPERATION_ATTRIBUTE,
    TRACE_MESSAGING_BATCH_COUNT_ATTRIBUTE,
    TRACE_MESSAGING_DESTINATION_ATTRIBUTE,
    TRACE_MESSAGING_SOURCE_ATTRIBUTE,
    SPAN_ENQUEUED_TIME_PROPERTY,
    SPAN_NAME_RECEIVE,
    TraceOperationTypes
)
from ..amqp import AmqpAnnotatedMessage

if TYPE_CHECKING:
    try:
        # pylint:disable=unused-import
        from uamqp import (
            Message as uamqp_Message,
            types as uamqp_types
        )
        from uamqp.authentication import JWTTokenAuth as uamqp_JWTTokenAuth
    except ImportError:
        pass
    from .._pyamqp.message import Message as pyamqp_Message
    from .._pyamqp.authentication import JWTTokenAuth as pyamqp_JWTTokenAuth
    from .message import (
        ServiceBusReceivedMessage,
        ServiceBusMessage,
        ServiceBusMessageBatch
    )
    from azure.core.tracing import AbstractSpan
    from azure.core.credentials import AzureSasCredential
    from .._base_handler import BaseHandler
    from ..aio._base_handler_async import BaseHandler as BaseHandlerAsync
    from .._servicebus_receiver import ServiceBusReceiver
    from ..aio._servicebus_receiver_async import ServiceBusReceiver as ServiceBusReceiverAsync
    from .._servicebus_session import BaseSession
    from .._transport._base import AmqpTransport
    from ..aio._transport._base_async import AmqpTransportAsync

    MessagesType = Union[
        Mapping[str, Any],
        ServiceBusMessage,
        AmqpAnnotatedMessage,
        List[Union[Mapping[str, Any], ServiceBusMessage, AmqpAnnotatedMessage]],
    ]

    SingleMessageType = Union[
        Mapping[str, Any], ServiceBusMessage, AmqpAnnotatedMessage
    ]

_log = logging.getLogger(__name__)


def utc_from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=timezone.utc)


def utc_now():
    return datetime.datetime.now(timezone.utc)


def build_uri(address, entity):
    parsed = urlparse(address)
    if parsed.path:
        return address
    if not entity:
        raise ValueError("No Service Bus entity specified")
    address += "/" + str(entity)
    return address


def create_properties(
    user_agent: Optional[str] = None, *, amqp_transport: "AmqpTransport"
) -> Union[Dict["uamqp_types.AMQPSymbol", str], Dict[str, str]]:
    """
    Format the properties with which to instantiate the connection.
    This acts like a user agent over HTTP.

    :param str user_agent: If specified,
    this will be added in front of the built-in user agent string.

    :rtype: dict
    """
    properties: Dict[Any, str] = {}
    properties[amqp_transport.PRODUCT_SYMBOL] = USER_AGENT_PREFIX
    properties[amqp_transport.VERSION_SYMBOL] = VERSION
    framework = f"Python/{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"
    properties[amqp_transport.FRAMEWORK_SYMBOL] = framework
    platform_str = platform.platform()
    properties[amqp_transport.PLATFORM_SYMBOL] = platform_str

    final_user_agent = (
        f"{USER_AGENT_PREFIX}/{VERSION} {amqp_transport.TRANSPORT_IDENTIFIER} "
        f"{framework} ({platform_str})"
    )
    if user_agent:
        final_user_agent = f"{user_agent} {final_user_agent}"

    properties[amqp_transport.USER_AGENT_SYMBOL] = final_user_agent
    return properties


def get_renewable_start_time(renewable):
    try:
        return renewable._received_timestamp_utc  # pylint: disable=protected-access
    except AttributeError:
        pass
    try:
        return renewable._session_start  # pylint: disable=protected-access
    except AttributeError:
        raise TypeError(
            "Registered object is not renewable, renewable must be"
            + "a ServiceBusReceivedMessage or a ServiceBusSession from a sessionful ServiceBusReceiver."
        )


def get_renewable_lock_duration(
    renewable: Union["ServiceBusReceivedMessage", "BaseSession"]
) -> datetime.timedelta:
    # pylint: disable=protected-access
    try:
        return max(
            renewable.locked_until_utc - utc_now(), datetime.timedelta(seconds=0)
        )
    except AttributeError:
        raise TypeError(
            "Registered object is not renewable, renewable must be"
            + "a ServiceBusReceivedMessage or a ServiceBusSession from a sessionful ServiceBusReceiver."
        )


def create_authentication(client) -> Union["uamqp_JWTTokenAuth", "pyamqp_JWTTokenAuth"]:
    # pylint: disable=protected-access
    try:
        # ignore mypy's warning because token_type is Optional
        token_type = client._credential.token_type  # type: ignore
    except AttributeError:
        token_type = TOKEN_TYPE_JWT
    if token_type == TOKEN_TYPE_SASTOKEN:
        return client._amqp_transport.create_token_auth(
            client._auth_uri,
            get_token=functools.partial(client._credential.get_token, client._auth_uri),
            token_type=token_type,
            config=client._config,
            update_token=True
        )
    return client._amqp_transport.create_token_auth(
            client._auth_uri,
            get_token=functools.partial(client._credential.get_token, JWT_TOKEN_SCOPE),
            token_type=token_type,
            config=client._config,
            update_token=False,
        )


def generate_dead_letter_entity_name(
    queue_name=None, topic_name=None, subscription_name=None, transfer_deadletter=False
):
    entity_name = (
        queue_name
        if queue_name
        else (topic_name + "/Subscriptions/" + subscription_name)
    )
    entity_name = (
        f"{entity_name}"
        f"{TRANSFER_DEAD_LETTER_QUEUE_SUFFIX if transfer_deadletter else DEAD_LETTER_QUEUE_SUFFIX}"
    )

    return entity_name


def _convert_to_single_service_bus_message(
    message: "SingleMessageType",
    message_type: Type["ServiceBusMessage"],
    to_outgoing_amqp_message: Callable
) -> "ServiceBusMessage":
    try:
        # ServiceBusMessage/ServiceBusReceivedMessage
        message = cast("ServiceBusMessage", message)
        # pylint: disable=protected-access
        message._message = to_outgoing_amqp_message(message.raw_amqp_message)
        return message
    except AttributeError:
        # AmqpAnnotatedMessage or Mapping representation
        pass
    try:
        message = cast(AmqpAnnotatedMessage, message)
        amqp_message = to_outgoing_amqp_message(message)
        return message_type(body=None, message=amqp_message, raw_amqp_message=message)
    except AttributeError:
        # Mapping representing
        pass
    try:
        # pylint: disable=protected-access
        message = message_type(**cast(Mapping[str, Any], message))
        message._message = to_outgoing_amqp_message(message.raw_amqp_message)
        return message
    except TypeError:
        raise TypeError(
            f"Only AmqpAnnotatedMessage, ServiceBusMessage instances or Mappings representing messages are supported. "
            f"Received instead: {message.__class__.__name__}"
        )


def transform_outbound_messages(
    messages: "MessagesType",
    message_type: Type["ServiceBusMessage"],
    to_outgoing_amqp_message: Callable
) -> Union["ServiceBusMessage", List["ServiceBusMessage"]]:
    """
    This method serves multiple goals:
    1. convert dict representations of one or more messages to
    one or more ServiceBusMessage objects if needed
    2. update the messages to be sendable in the case that input messages are received or already-sent
    3. transform the AmqpAnnotatedMessage to be ServiceBusMessage

    :param Messages messages: A list or single instance of messages of type ServiceBusMessage or
        dict representations of type ServiceBusMessage.
    :param Type[ServiceBusMessage] message_type: The class type to return the messages as.
    :rtype: Union[ServiceBusMessage, List[ServiceBusMessage]]
    """
    if isinstance(messages, list):
        return [
            _convert_to_single_service_bus_message(m, message_type, to_outgoing_amqp_message) for m in messages
        ]
    return _convert_to_single_service_bus_message(messages, message_type, to_outgoing_amqp_message)


def strip_protocol_from_uri(uri: str) -> str:
    """Removes the protocol (e.g. http:// or sb://) from a URI, such as the FQDN."""
    left_slash_pos = uri.find("//")
    if left_slash_pos != -1:
        return uri[left_slash_pos + 2 :]
    return uri


def is_tracing_enabled():
    span_impl_type = settings.tracing_implementation()
    return span_impl_type is not None


@contextmanager
def send_trace_context_manager(span_name=SPAN_NAME_SEND, links=None):
    span_impl_type: Type[AbstractSpan] = settings.tracing_implementation()

    if span_impl_type is not None:
        with span_impl_type(name=span_name, kind=SpanKind.CLIENT, links=links) as child:
            yield child
    else:
        yield None


@contextmanager
def receive_trace_context_manager(
    receiver: Union[ServiceBusReceiver, ServiceBusReceiverAsync],
    span_name: str = SPAN_NAME_RECEIVE,
    links: Optional[List[Link]] = None,
    start_time: Optional[int] = None
) -> Iterator[None]:
    """Tracing"""
    span_impl_type: Type[AbstractSpan] = settings.tracing_implementation()
    if span_impl_type is None:
        yield
    else:
        receive_span = span_impl_type(name=span_name, kind=SpanKind.CLIENT, links=links, start_time=start_time)
        add_span_attributes(  # pylint: disable=protected-access
            receiver,
            receive_span,
            TraceOperationTypes.RECEIVE,
            message_count=len(links) if links else 0
        )

        with receive_span:
            yield


@contextmanager
def settle_trace_context_manager(
    receiver: Union[ServiceBusReceiver, ServiceBusReceiverAsync],
    operation: str,
    links: Optional[List[Link]] = None
):
    span_impl_type = settings.tracing_implementation()
    if span_impl_type is None:
        yield
    else:
        settle_span = span_impl_type(name=f"ServiceBus.{operation}", kind=SpanKind.CLIENT, links=links)
        add_span_attributes(receiver, settle_span, TraceOperationTypes.SETTLE)  # pylint: disable=protected-access

        with settle_span:
            yield


def trace_message(
    message: Union[uamqp_Message, pyamqp_Message],
    amqp_transport: Union[AmqpTransport, AmqpTransportAsync],
    additional_attributes: Optional[Dict[str, Union[str, int]]] = None,
    parent_span: Optional[AbstractSpan] = None
) -> Union["uamqp_Message", "pyamqp_Message"]:
    """Add tracing information to this message.

    Will open and close a "ServiceBus.message" span, and add tracing context to the app properties of the message.
    """
    try:
        span_impl_type: Type[AbstractSpan] = settings.tracing_implementation()
        if span_impl_type is not None:
            current_span = parent_span or span_impl_type(
                span_impl_type.get_current_span()
            )

            with current_span.span(name=SPAN_NAME_MESSAGE, kind=SpanKind.PRODUCER) as message_span:
                headers = message_span.to_header()

                if "traceparent" in headers:
                    message = amqp_transport.update_message_app_properties(
                        message,
                        DIAGNOSTIC_ID_PROPERTY,
                        headers["traceparent"]
                    )
                    message = amqp_transport.update_message_app_properties(
                        message,
                        TRACE_PARENT_PROPERTY,
                        headers["traceparent"]
                    )

                if "tracestate" in headers:
                    message = amqp_transport.update_message_app_properties(
                        message,
                        TRACE_STATE_PROPERTY,
                        headers["tracestate"]
                    )

                message_span.add_attribute(TRACE_NAMESPACE_ATTRIBUTE, TRACE_NAMESPACE)
                message_span.add_attribute(TRACE_MESSAGING_SYSTEM_ATTRIBUTE, TRACE_MESSAGING_SYSTEM)

                if additional_attributes:
                    for key, value in additional_attributes.items():
                        if value is not None:
                            message_span.add_attribute(key, value)

    except Exception as exp:  # pylint:disable=broad-except
        _log.warning("trace_message had an exception %r", exp)

    return message


def get_receive_links(messages):
    if not is_tracing_enabled():
        return []

    trace_messages = (
        messages if isinstance(messages, Iterable)  # pylint:disable=isinstance-second-argument-not-valid-type
        else (messages,)
    )

    links = []
    try:
        for message in trace_messages:
            if message.application_properties:
                headers = {}

                traceparent = message.application_properties.get(TRACE_PARENT_PROPERTY, b"")
                if hasattr(traceparent, "decode"):
                    traceparent = traceparent.decode(TRACE_PROPERTY_ENCODING)
                if traceparent:
                    headers["traceparent"] = cast(str, traceparent)

                tracestate = message.application_properties.get(TRACE_STATE_PROPERTY, b"")
                if hasattr(tracestate, "decode"):
                    tracestate = tracestate.decode(TRACE_PROPERTY_ENCODING)
                if tracestate:
                    headers["tracestate"] = cast(str, tracestate)

                enqueued_time = message.raw_amqp_message.annotations.get(TRACE_ENQUEUED_TIME_PROPERTY)
                attributes = {SPAN_ENQUEUED_TIME_PROPERTY: enqueued_time} if enqueued_time else None

                if headers:
                    links.append(Link(headers, attributes=attributes))
    except AttributeError:
        pass
    return links


def get_span_links_from_batch(batch: ServiceBusMessageBatch) -> List[Link]:
    """Create span links from a batch of messages."""
    links = []
    for message in batch._messages:  # pylint: disable=protected-access
        links.extend(get_span_links_from_message(message._message))  # pylint: disable=protected-access
    return links


def get_span_links_from_message(message: Union[uamqp_Message, pyamqp_Message, ServiceBusMessage]) -> List[Link]:
    """Create a span link from a message.

    This will extract the traceparent and tracestate from the message application properties and create span links
    based on these values.
    """
    headers = {}
    try:
        if message.application_properties:
            traceparent = message.application_properties.get(TRACE_PARENT_PROPERTY, b"")
            if hasattr(traceparent, "decode"):
                traceparent = traceparent.decode(TRACE_PROPERTY_ENCODING)
            if traceparent:
                headers["traceparent"] = cast(str, traceparent)

            tracestate = message.application_properties.get(TRACE_STATE_PROPERTY, b"")
            if hasattr(tracestate, "decode"):
                tracestate = tracestate.decode(TRACE_PROPERTY_ENCODING)
            if tracestate:
                headers["tracestate"] = cast(str, tracestate)
    except AttributeError :
        return []
    return [Link(headers)] if headers else []


def add_span_attributes(
        handler: Union[BaseHandler, BaseHandlerAsync],
        span: AbstractSpan,
        operation_type: TraceOperationTypes,
        message_count: int = 0
) -> None:
    """Add attributes to span based on the operation type."""

    span.add_attribute(TRACE_NAMESPACE_ATTRIBUTE, TRACE_NAMESPACE)
    span.add_attribute(TRACE_NET_PEER_NAME_ATTRIBUTE, handler.fully_qualified_namespace)
    span.add_attribute(TRACE_MESSAGING_SYSTEM_ATTRIBUTE, TRACE_MESSAGING_SYSTEM)
    span.add_attribute(TRACE_MESSAGING_OPERATION_ATTRIBUTE, operation_type)

    if message_count > 1:
        span.add_attribute(TRACE_MESSAGING_BATCH_COUNT_ATTRIBUTE, message_count)

    if operation_type == TraceOperationTypes.PUBLISH:
        span.add_attribute(TRACE_COMPONENT_PROPERTY, TRACE_COMPONENT)
        span.add_attribute(TRACE_MESSAGING_DESTINATION_ATTRIBUTE, handler._entity_name)  # pylint: disable=protected-access
    else:
        span.add_attribute(TRACE_MESSAGING_SOURCE_ATTRIBUTE, handler._entity_name)  # pylint: disable=protected-access


def parse_sas_credential(credential: "AzureSasCredential") -> Tuple:
    sas = credential.signature
    parsed_sas = sas.split('&')
    expiry = None
    for item in parsed_sas:
        if item.startswith('se='):
            expiry = int(item[3:])
    return (sas, expiry)
