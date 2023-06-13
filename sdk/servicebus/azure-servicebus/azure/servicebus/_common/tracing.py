# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from __future__ import annotations
from contextlib import contextmanager
from enum import Enum
import logging
from typing import (
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Type,
    TYPE_CHECKING,
    Union,
    cast,
)

from azure.core import CaseInsensitiveEnumMeta
from azure.core.settings import settings
from azure.core.tracing import SpanKind, Link

if TYPE_CHECKING:
    try:
        # pylint:disable=unused-import
        from uamqp import Message as uamqp_Message
    except ImportError:
        uamqp_Message = None
    from azure.core.tracing import AbstractSpan

    from .._pyamqp.message import Message as pyamqp_Message
    from .message import (
        ServiceBusReceivedMessage,
        ServiceBusMessage,
        ServiceBusMessageBatch
    )
    from .._base_handler import BaseHandler
    from ..aio._base_handler_async import BaseHandler as BaseHandlerAsync
    from .._servicebus_receiver import ServiceBusReceiver
    from ..aio._servicebus_receiver_async import ServiceBusReceiver as ServiceBusReceiverAsync
    from .._servicebus_sender import ServiceBusSender
    from ..aio._servicebus_sender_async import ServiceBusSender as ServiceBusSenderAsync
    from .._transport._base import AmqpTransport
    from ..aio._transport._base_async import AmqpTransportAsync

    ReceiveMessageTypes = Union[
        ServiceBusReceivedMessage,
        pyamqp_Message,
        uamqp_Message
    ]

TRACE_DIAGNOSTIC_ID_PROPERTY = b"Diagnostic-Id"
TRACE_ENQUEUED_TIME_PROPERTY = b"x-opt-enqueued-time"
TRACE_PARENT_PROPERTY = b"traceparent"
TRACE_STATE_PROPERTY = b"tracestate"
TRACE_PROPERTY_ENCODING = "ascii"

SPAN_ENQUEUED_TIME_PROPERTY = "enqueuedTime"

SPAN_NAME_RECEIVE = "ServiceBus.receive"
SPAN_NAME_RECEIVE_DEFERRED = "ServiceBus.receive_deferred"
SPAN_NAME_PEEK = "ServiceBus.peek"
SPAN_NAME_SEND = "ServiceBus.send"
SPAN_NAME_SCHEDULE = "ServiceBus.schedule"
SPAN_NAME_MESSAGE = "ServiceBus.message"


_LOGGER = logging.getLogger(__name__)


class TraceAttributes:
    TRACE_NAMESPACE_ATTRIBUTE = "az.namespace"
    TRACE_NAMESPACE = "Microsoft.ServiceBus"

    TRACE_MESSAGING_SYSTEM_ATTRIBUTE = "messaging.system"
    TRACE_MESSAGING_SYSTEM = "servicebus"

    TRACE_NET_PEER_NAME_ATTRIBUTE = "net.peer.name"
    TRACE_MESSAGING_DESTINATION_ATTRIBUTE = "messaging.destination.name"
    TRACE_MESSAGING_OPERATION_ATTRIBUTE = "messaging.operation"
    TRACE_MESSAGING_BATCH_COUNT_ATTRIBUTE = "messaging.batch.message_count"

    LEGACY_TRACE_MESSAGE_BUS_DESTINATION_ATTRIBUTE = "message_bus.destination"
    LEGACY_TRACE_PEER_ADDRESS_ATTRIBUTE = "peer.address"


class TraceOperationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    PUBLISH = "publish"
    RECEIVE = "receive"
    SETTLE = "settle"


def is_tracing_enabled():
    span_impl_type = settings.tracing_implementation()
    return span_impl_type is not None


@contextmanager
def send_trace_context_manager(
    sender: Union[ServiceBusSender, ServiceBusSenderAsync],
    span_name: str = SPAN_NAME_SEND,
    links: Optional[List[Link]] = None
) -> Iterator[None]:
    """Tracing for sending messages."""
    span_impl_type: Type[AbstractSpan] = settings.tracing_implementation()

    if span_impl_type is not None:
        links = links or []
        with span_impl_type(name=span_name, kind=SpanKind.CLIENT, links=links) as span:
            add_span_attributes(span, TraceOperationTypes.PUBLISH, sender, message_count=len(links))
            yield
    else:
        yield


@contextmanager
def receive_trace_context_manager(
    receiver: Union[ServiceBusReceiver, ServiceBusReceiverAsync],
    span_name: str = SPAN_NAME_RECEIVE,
    links: Optional[List[Link]] = None,
    start_time: Optional[int] = None
) -> Iterator[None]:
    """Tracing for receiving messages."""
    span_impl_type: Type[AbstractSpan] = settings.tracing_implementation()
    if span_impl_type is not None:
        links = links or []
        with span_impl_type(name=span_name, kind=SpanKind.CLIENT, links=links, start_time=start_time) as span:
            add_span_attributes(span, TraceOperationTypes.RECEIVE, receiver, message_count=len(links))
            yield
    else:
        yield


@contextmanager
def settle_trace_context_manager(
    receiver: Union[ServiceBusReceiver, ServiceBusReceiverAsync],
    operation: str,
    links: Optional[List[Link]] = None
):
    """Tracing for settling messages."""
    span_impl_type = settings.tracing_implementation()
    if span_impl_type is not None:
        links = links or []
        with span_impl_type(name=f"ServiceBus.{operation}", kind=SpanKind.CLIENT, links=links) as span:
            add_span_attributes(span, TraceOperationTypes.SETTLE, receiver)
            yield
    else:
        yield


def trace_message(
    message: Union[uamqp_Message, pyamqp_Message],
    amqp_transport: Union[AmqpTransport, AmqpTransportAsync],
    additional_attributes: Optional[Dict[str, Union[str, int]]] = None
) -> Union["uamqp_Message", "pyamqp_Message"]:
    """Adds tracing information to the message and returns the updated message.

    Will open and close a message span, and add tracing context to the app properties of the message.
    """
    try:
        span_impl_type: Type[AbstractSpan] = settings.tracing_implementation()
        if span_impl_type is not None:
            with span_impl_type(name=SPAN_NAME_MESSAGE, kind=SpanKind.PRODUCER) as message_span:
                headers = message_span.to_header()

                if "traceparent" in headers:
                    message = amqp_transport.update_message_app_properties(
                        message,
                        TRACE_DIAGNOSTIC_ID_PROPERTY,
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

                message_span.add_attribute(
                    TraceAttributes.TRACE_NAMESPACE_ATTRIBUTE, TraceAttributes.TRACE_NAMESPACE
                )
                message_span.add_attribute(
                    TraceAttributes.TRACE_MESSAGING_SYSTEM_ATTRIBUTE, TraceAttributes.TRACE_MESSAGING_SYSTEM
                )

                if additional_attributes:
                    for key, value in additional_attributes.items():
                        if value is not None:
                            message_span.add_attribute(key, value)

    except Exception as exp:  # pylint:disable=broad-except
        _LOGGER.warning("trace_message had an exception %r", exp)

    return message


def get_receive_links(messages: Union[ReceiveMessageTypes, Iterable[ReceiveMessageTypes]]) -> List[Link]:
    if not is_tracing_enabled():
        return []

    trace_messages = (
        messages if isinstance(messages, Iterable)  # pylint:disable=isinstance-second-argument-not-valid-type
        else (messages,)
    )

    links = []
    try:
        for message in trace_messages:
            headers = {}
            if message.application_properties:
                traceparent = (message.application_properties.get(TRACE_PARENT_PROPERTY, b"") or
                               message.application_properties.get(TRACE_DIAGNOSTIC_ID_PROPERTY, b""))
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
            links.append(Link(headers, attributes=attributes))
    except AttributeError:
        pass
    return links


def get_span_links_from_batch(batch: ServiceBusMessageBatch) -> List[Link]:
    """Create span links from a batch of messages."""
    links = []
    for message in batch._messages:  # pylint: disable=protected-access
        link = get_span_link_from_message(message._message)  # pylint: disable=protected-access
        if link:
            links.append(link)
    return links


def get_span_link_from_message(message: Union[uamqp_Message, pyamqp_Message, ServiceBusMessage]) -> Optional[Link]:
    """Create a span link from a message.

    This will extract the traceparent and tracestate from the message application properties and create span links
    based on these values.
    """
    headers = {}
    try:
        if message.application_properties:
            traceparent = (message.application_properties.get(TRACE_PARENT_PROPERTY, b"") or
                           message.application_properties.get(TRACE_DIAGNOSTIC_ID_PROPERTY, b""))
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
        return None
    return Link(headers)


def add_span_attributes(
        span: AbstractSpan,
        operation_type: TraceOperationTypes,
        handler: Union[BaseHandler, BaseHandlerAsync],
        message_count: int = 0
) -> None:
    """Add attributes to span based on the operation type."""

    span.add_attribute(TraceAttributes.TRACE_NAMESPACE_ATTRIBUTE, TraceAttributes.TRACE_NAMESPACE)
    span.add_attribute(TraceAttributes.TRACE_MESSAGING_SYSTEM_ATTRIBUTE, TraceAttributes.TRACE_MESSAGING_SYSTEM)
    span.add_attribute(TraceAttributes.TRACE_MESSAGING_OPERATION_ATTRIBUTE, operation_type)

    if message_count > 1:
        span.add_attribute(TraceAttributes.TRACE_MESSAGING_BATCH_COUNT_ATTRIBUTE, message_count)

    if operation_type in (TraceOperationTypes.PUBLISH, TraceOperationTypes.RECEIVE):
        # Maintain legacy attributes for backwards compatibility.
        span.add_attribute(TraceAttributes.LEGACY_TRACE_MESSAGE_BUS_DESTINATION_ATTRIBUTE, handler._entity_name)  # pylint: disable=protected-access
        span.add_attribute(TraceAttributes.LEGACY_TRACE_PEER_ADDRESS_ATTRIBUTE, handler.fully_qualified_namespace)

    elif operation_type == TraceOperationTypes.SETTLE:
        span.add_attribute(TraceAttributes.TRACE_NET_PEER_NAME_ATTRIBUTE, handler.fully_qualified_namespace)
        span.add_attribute(TraceAttributes.TRACE_MESSAGING_DESTINATION_ATTRIBUTE, handler._entity_name)  # pylint: disable=protected-access
