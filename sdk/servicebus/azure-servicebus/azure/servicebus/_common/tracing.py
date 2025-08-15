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
    Any,
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
from azure.servicebus._version import VERSION

try:
    from azure.core.instrumentation import get_tracer
    TRACER = get_tracer(
        library_name="azure-servicebus",
        library_version=VERSION,
        schema_url="https://opentelemetry.io/schemas/1.23.1",
        attributes={
            "az.namespace": "Microsoft.ServiceBus",
        },
    )
except ImportError:
    TRACER = None

if TYPE_CHECKING:
    try:
        from uamqp import Message as uamqp_Message
    except ImportError:
        uamqp_Message = None
    from azure.core.tracing import AbstractSpan

    from .._pyamqp.message import Message as pyamqp_Message
    from .message import ServiceBusReceivedMessage, ServiceBusMessage, ServiceBusMessageBatch
    from .._base_handler import BaseHandler
    from ..aio._base_handler_async import BaseHandler as BaseHandlerAsync
    from .._servicebus_receiver import ServiceBusReceiver
    from ..aio._servicebus_receiver_async import ServiceBusReceiver as ServiceBusReceiverAsync
    from .._servicebus_sender import ServiceBusSender
    from ..aio._servicebus_sender_async import ServiceBusSender as ServiceBusSenderAsync
    from .._transport._base import AmqpTransport
    from ..aio._transport._base_async import AmqpTransportAsync

    ReceiveMessageTypes = Union[ServiceBusReceivedMessage, pyamqp_Message, uamqp_Message]

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


class TraceOperationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    PUBLISH = "publish"
    RECEIVE = "receive"
    SETTLE = "settle"


def is_tracing_enabled():
    if TRACER is None:
        # The version of azure-core installed does not support native tracing. Just check
        # for the plugin.
        span_impl_type = settings.tracing_implementation()
        return span_impl_type is not None
    # Otherwise, can just check the tracing setting.
    return settings.tracing_enabled()


@contextmanager
def send_trace_context_manager(
    sender: Union[ServiceBusSender, ServiceBusSenderAsync],
    span_name: str = SPAN_NAME_SEND,
    links: Optional[List[Link]] = None,
) -> Iterator[None]:
    """Tracing for sending messages.

    :param sender: The sender that is sending the message.
    :type sender: ~azure.servicebus.ServiceBusSender or ~azure.servicebus.aio.ServiceBusSenderAsync
    :param span_name: The name of the tracing span.
    :type span_name: str
    :param links: A list of links to include in the tracing span.
    :type links: list[~azure.core.tracing.Link] or None
    :return: A context manager that will yield when the message is sent.
    :rtype: iterator
    """
    span_impl_type: Optional[Type[AbstractSpan]] = settings.tracing_implementation()
    links = links or []

    if span_impl_type is not None:
        with span_impl_type(name=span_name, kind=SpanKind.CLIENT, links=links) as span:
            add_plugin_span_attributes(span, TraceOperationTypes.PUBLISH, sender, message_count=len(links))
            yield
    elif TRACER is not None:
        if settings.tracing_enabled():
            with TRACER.start_as_current_span(span_name, kind=SpanKind.CLIENT, links=links) as span:
                attributes = get_span_attributes(TraceOperationTypes.PUBLISH, sender, message_count=len(links))
                span.set_attributes(attributes)
                yield
        else:
            yield
    else:
        yield


@contextmanager
def receive_trace_context_manager(
    receiver: Union[ServiceBusReceiver, ServiceBusReceiverAsync],
    span_name: str = SPAN_NAME_RECEIVE,
    links: Optional[List[Link]] = None,
    start_time: Optional[int] = None,
) -> Iterator[None]:
    """Tracing for receiving messages.

    :param receiver: The receiver that is receiving the message.
    :type receiver: ~azure.servicebus.ServiceBusReceiver or ~azure.servicebus.aio.ServiceBusReceiverAsync
    :param span_name: The name of the tracing span.
    :type span_name: str
    :param links: A list of links to include in the tracing span.
    :type links: list[~azure.core.tracing.Link] or None
    :param start_time: The time that the receive operation started.
    :type start_time: int or None
    :return: An iterator that yields the tracing span.
    :rtype: iterator
    """
    links = links or []
    span_impl_type: Optional[Type[AbstractSpan]] = settings.tracing_implementation()
    if span_impl_type is not None:
        with span_impl_type(name=span_name, kind=SpanKind.CLIENT, links=links, start_time=start_time) as span:
            add_plugin_span_attributes(span, TraceOperationTypes.RECEIVE, receiver, message_count=len(links))
            yield
    elif TRACER is not None:
        if settings.tracing_enabled():
            attributes = get_span_attributes(TraceOperationTypes.RECEIVE, receiver, message_count=len(links))
            # Depending on the azure-core version, start_as_current_span may or may not support start_time as a
            # keyword argument. Handle both cases.
            try:
                with TRACER.start_as_current_span(  # type: ignore[call-arg]  # pylint: disable=unexpected-keyword-arg
                    span_name, kind=SpanKind.CLIENT, start_time=start_time, links=links
                ) as span:
                    span.set_attributes(attributes)
                    yield
            except TypeError:
                # If start_time is not supported, just call without it.
                with TRACER.start_as_current_span(span_name, kind=SpanKind.CLIENT, links=links) as span:
                    span.set_attributes(attributes)
                    yield
        else:
            yield
    else:
        yield


@contextmanager
def settle_trace_context_manager(
    receiver: Union[ServiceBusReceiver, ServiceBusReceiverAsync], operation: str, links: Optional[List[Link]] = None
):
    """Tracing for settling messages.

    :param receiver: The receiver that is settling the message.
    :type receiver: ~azure.servicebus.ServiceBusReceiver or ~azure.servicebus.aio.ServiceBusReceiver
    :param operation: The operation that is being performed on the message.
    :type operation: str
    :param links: A list of links to include in the tracing span.
    :type links: list[~azure.core.tracing.Link] or None
    :return: An generator that yields the tracing span.
    :rtype: None
    """
    span_impl_type: Optional[Type[AbstractSpan]] = settings.tracing_implementation()
    if span_impl_type is not None:
        links = links or []
        with span_impl_type(name=f"ServiceBus.{operation}", kind=SpanKind.CLIENT, links=links) as span:
            add_plugin_span_attributes(span, TraceOperationTypes.SETTLE, receiver)
            yield
    elif TRACER is not None:
        if settings.tracing_enabled():
            with TRACER.start_as_current_span(f"ServiceBus.{operation}", kind=SpanKind.CLIENT, links=links) as span:
                attributes = get_span_attributes(TraceOperationTypes.SETTLE, receiver)
                span.set_attributes(attributes)
                yield
        else:
            yield
    else:
        yield


def _update_message_with_trace_context(message, amqp_transport, context):
    if "traceparent" in context:
        message = amqp_transport.update_message_app_properties(
            message, TRACE_DIAGNOSTIC_ID_PROPERTY, context["traceparent"]
        )
        message = amqp_transport.update_message_app_properties(message, TRACE_PARENT_PROPERTY, context["traceparent"])
    if "tracestate" in context:
        message = amqp_transport.update_message_app_properties(message, TRACE_STATE_PROPERTY, context["tracestate"])
    return message


def trace_message(
    message: Union[uamqp_Message, pyamqp_Message],
    amqp_transport: Union[AmqpTransport, AmqpTransportAsync],
    additional_attributes: Optional[Dict[str, Union[str, int]]] = None,
) -> Union["uamqp_Message", "pyamqp_Message"]:
    """Adds tracing information to the message and returns the updated message.

    Will open and close a message span, and add tracing context to the app properties of the message.
    :param message: The message to trace.
    :type message: ~uamqp.Message or ~pyamqp.message.Message
    :param amqp_transport: The AMQP transport to use for tracing.
    :type amqp_transport: ~azure.servicebus._transport._base.AmqpTransport
     or ~azure.servicebus.aio._transport._base_async.AmqpTransportAsync
    :param additional_attributes: Additional attributes to add to the message span.
    :type additional_attributes: dict[str, str or int] or None
    :return: The message with tracing information added.
    :rtype: ~uamqp.Message or ~pyamqp.message.Message
    """
    try:
        span_impl_type: Optional[Type[AbstractSpan]] = settings.tracing_implementation()
        if span_impl_type is not None:
            with span_impl_type(name=SPAN_NAME_MESSAGE, kind=SpanKind.PRODUCER) as message_span:
                context = message_span.to_header()
                message = _update_message_with_trace_context(message, amqp_transport, context)

                message_span.add_attribute(TraceAttributes.TRACE_NAMESPACE_ATTRIBUTE, TraceAttributes.TRACE_NAMESPACE)
                message_span.add_attribute(
                    TraceAttributes.TRACE_MESSAGING_SYSTEM_ATTRIBUTE, TraceAttributes.TRACE_MESSAGING_SYSTEM
                )

                if additional_attributes:
                    for key, value in additional_attributes.items():
                        if value is not None:
                            message_span.add_attribute(key, value)
        elif TRACER is not None:
            if settings.tracing_enabled():
                with TRACER.start_as_current_span(SPAN_NAME_MESSAGE, kind=SpanKind.PRODUCER) as message_span:
                    trace_context = TRACER.get_trace_context()
                    message = _update_message_with_trace_context(message, amqp_transport, trace_context)
                    attributes = {
                        TraceAttributes.TRACE_NAMESPACE_ATTRIBUTE: TraceAttributes.TRACE_NAMESPACE,
                        TraceAttributes.TRACE_MESSAGING_SYSTEM_ATTRIBUTE: TraceAttributes.TRACE_MESSAGING_SYSTEM,
                        **(additional_attributes or {}),
                    }
                    message_span.set_attributes(attributes)

    except Exception as exp:  # pylint:disable=broad-except
        _LOGGER.warning("trace_message had an exception %r", exp)

    return message


def get_receive_links(messages: Union[ServiceBusReceivedMessage, Iterable[ServiceBusReceivedMessage]]) -> List[Link]:
    if not is_tracing_enabled():
        return []

    trace_messages = messages if isinstance(messages, Iterable) else (messages,)

    links = []
    try:
        for message in trace_messages:
            headers = {}
            if message.application_properties:
                traceparent = message.application_properties.get(
                    TRACE_PARENT_PROPERTY, b""
                ) or message.application_properties.get(TRACE_DIAGNOSTIC_ID_PROPERTY, b"")
                if hasattr(traceparent, "decode"):
                    traceparent = traceparent.decode(TRACE_PROPERTY_ENCODING)
                if traceparent:
                    headers["traceparent"] = cast(str, traceparent)

                tracestate = message.application_properties.get(TRACE_STATE_PROPERTY, b"")
                if hasattr(tracestate, "decode"):
                    tracestate = tracestate.decode(TRACE_PROPERTY_ENCODING)
                if tracestate:
                    headers["tracestate"] = cast(str, tracestate)

            enqueued_time = (
                message.raw_amqp_message.annotations.get(TRACE_ENQUEUED_TIME_PROPERTY)
                if message.raw_amqp_message.annotations
                else None
            )
            attributes = {SPAN_ENQUEUED_TIME_PROPERTY: enqueued_time} if enqueued_time else None
            links.append(Link(headers, attributes=attributes))
    except AttributeError:
        pass
    return links


def get_span_links_from_batch(batch: ServiceBusMessageBatch) -> List[Link]:
    """Create span links from a batch of messages.
    :param ~azure.servicebus.ServiceBusMessageBatch batch: The batch of messages to extract the span links from.
    :return: A list of span links created from the batch.
    :rtype: list[~azure.core.tracing.Link]
    """
    links = []
    for message in batch._messages:  # pylint: disable=protected-access
        link = get_span_link_from_message(message._message)  # pylint: disable=protected-access
        if link:
            links.append(link)
    return links


def get_span_link_from_message(message: Any) -> Optional[Link]:
    """Create a span link from a message.

    This will extract the traceparent and tracestate from the message application properties and create span links
    based on these values.

    :param message: The message to extract the span link from.
    :type message: ~uamqp.Message or ~pyamqp.message.Message or ~azure.servicebus.ServiceBusMessage]
    :return: A span link created from the message.
    :rtype: ~azure.core.tracing.Link or None
    """
    headers = {}
    try:
        if message.application_properties:
            traceparent = message.application_properties.get(
                TRACE_PARENT_PROPERTY, b""
            ) or message.application_properties.get(TRACE_DIAGNOSTIC_ID_PROPERTY, b"")
            if hasattr(traceparent, "decode"):
                traceparent = traceparent.decode(TRACE_PROPERTY_ENCODING)
            if traceparent:
                headers["traceparent"] = cast(str, traceparent)

            tracestate = message.application_properties.get(TRACE_STATE_PROPERTY, b"")
            if hasattr(tracestate, "decode"):
                tracestate = tracestate.decode(TRACE_PROPERTY_ENCODING)
            if tracestate:
                headers["tracestate"] = cast(str, tracestate)
    except AttributeError:
        return None
    return Link(headers)


def add_plugin_span_attributes(
    span: AbstractSpan,
    operation_type: TraceOperationTypes,
    handler: Union[BaseHandler, BaseHandlerAsync],
    message_count: int = 0,
) -> None:
    """Add attributes to span based on the operation type.
    :param ~azure.core.tracing.AbstractSpan span: The span to add attributes to.
    :param TraceOperationTypes operation_type: The operation type.
    :param ~azure.servicebus._base_handler.BaseHandler or
     ~azure.servicebus.aio._base_handler_async.BaseHandlerAsync handler: The handler that is performing the operation.
    :param int message_count: The number of messages being sent or received.
    """
    attributes = get_span_attributes(operation_type, handler, message_count)
    for key, value in attributes.items():
        if value is not None:
            span.add_attribute(key, value)


def get_span_attributes(
    operation_type: TraceOperationTypes,
    handler: Union[BaseHandler, BaseHandlerAsync],
    message_count: int = 0,
) -> dict:
    """Return a dict of attributes for a span based on the operation type.

    :param TraceOperationTypes operation_type: The operation type.
    :param ~azure.servicebus._base_handler.BaseHandler or
     ~azure.servicebus.aio._base_handler_async.BaseHandlerAsync handler: The handler that is performing the operation.
    :param int message_count: The number of messages being sent or received.
    :return: Dictionary of span attributes.
    :rtype: dict
    """
    attributes: Dict[str, Any] = {
        TraceAttributes.TRACE_NAMESPACE_ATTRIBUTE: TraceAttributes.TRACE_NAMESPACE,
        TraceAttributes.TRACE_MESSAGING_SYSTEM_ATTRIBUTE: TraceAttributes.TRACE_MESSAGING_SYSTEM,
        TraceAttributes.TRACE_MESSAGING_OPERATION_ATTRIBUTE: operation_type,
    }
    if message_count > 1:
        attributes[TraceAttributes.TRACE_MESSAGING_BATCH_COUNT_ATTRIBUTE] = message_count
    attributes[TraceAttributes.TRACE_NET_PEER_NAME_ATTRIBUTE] = handler.fully_qualified_namespace
    attributes[TraceAttributes.TRACE_MESSAGING_DESTINATION_ATTRIBUTE] = (
        handler._entity_name  # pylint: disable=protected-access
    )
    return attributes
