# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
from contextlib import contextmanager
from enum import Enum
import logging
from typing import TYPE_CHECKING, Type, Optional, Dict, List, Union, Any, Iterable, Iterator

from azure.core import CaseInsensitiveEnumMeta
from azure.core.settings import settings
from azure.core.tracing import SpanKind, Link

from .amqp import AmqpAnnotatedMessage
from ._constants import PROP_TIMESTAMP

if TYPE_CHECKING:
    from ._transport._base import AmqpTransport

    try:
        from uamqp import Message as uamqp_Message
    except ImportError:
        uamqp_Message = None
    from ._pyamqp.message import Message
    from azure.core.tracing import AbstractSpan
    from ._client_base import ClientBase
    from ._common import EventData, EventDataBatch


_LOGGER = logging.getLogger(__name__)


TRACE_DIAGNOSTIC_ID_PROPERTY = b"Diagnostic-Id"
TRACE_PARENT_PROPERTY = b"traceparent"
TRACE_STATE_PROPERTY = b"tracestate"
TRACE_PROPERTY_ENCODING = "ascii"


class TraceAttributes:
    TRACE_NAMESPACE_ATTRIBUTE = "az.namespace"
    TRACE_NAMESPACE = "Microsoft.EventHub"

    TRACE_MESSAGING_SYSTEM_ATTRIBUTE = "messaging.system"
    TRACE_MESSAGING_SYSTEM = "eventhubs"

    TRACE_NET_PEER_NAME_ATTRIBUTE = "net.peer.name"
    TRACE_MESSAGING_DESTINATION_ATTRIBUTE = "messaging.destination.name"
    TRACE_MESSAGING_OPERATION_ATTRIBUTE = "messaging.operation"
    TRACE_MESSAGING_BATCH_COUNT_ATTRIBUTE = "messaging.batch.message_count"

    LEGACY_TRACE_MESSAGE_BUS_DESTINATION_ATTRIBUTE = "message_bus.destination"
    LEGACY_TRACE_PEER_ADDRESS_ATTRIBUTE = "peer.address"


class TraceOperationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    PUBLISH = "publish"
    RECEIVE = "receive"
    PROCESS = "process"


def is_tracing_enabled():
    span_impl_type = settings.tracing_implementation()
    return span_impl_type is not None


@contextmanager
def send_context_manager(client: Optional[ClientBase], links: Optional[List[Link]] = None) -> Iterator[None]:
    """Tracing for message sending.

    :param ~azure.eventhub._client_base.ClientBase or None client: The client that is sending the message.
    :param list[~azure.core.tracing.Link] or None links: A list of links to add to the span.
    :return: A context manager that will start and end the span.
    :rtype: iterator[None]
    """
    span_impl_type: Optional[Type[AbstractSpan]] = settings.tracing_implementation()
    if span_impl_type is not None:
        links = links or []
        with span_impl_type(name="EventHubs.send", kind=SpanKind.CLIENT, links=links) as span:
            add_span_attributes(span, TraceOperationTypes.PUBLISH, client, message_count=len(links))
            yield
    else:
        yield


@contextmanager
def receive_context_manager(
    client: Optional[ClientBase], links: Optional[List[Link]] = None, start_time: Optional[int] = None
) -> Iterator[None]:
    """Tracing for message receiving.

    :param ~azure.eventhub._client_base.ClientBase or None client: The client that is receiving the message.
    :param list[~azure.core.tracing.Link] or None links: A list of links to add to the span.
    :param int or None start_time: The time the receive operation started.
    :return: A context manager that will start and end the span.
    :rtype: iterator[None]
    """
    span_impl_type: Optional[Type[AbstractSpan]] = settings.tracing_implementation()
    if span_impl_type is not None:
        links = links or []
        with span_impl_type(name="EventHubs.receive", kind=SpanKind.CLIENT, links=links, start_time=start_time) as span:
            add_span_attributes(span, TraceOperationTypes.RECEIVE, client, message_count=len(links))
            yield
    else:
        yield


@contextmanager
def process_context_manager(
    client: Optional[ClientBase], links: Optional[List[Link]] = None, is_batch: bool = False
) -> Iterator[None]:
    """Tracing for message processing.

    :param ~azure.eventhub._client_base.ClientBase or None client: The client that is processing the message.
    :param list[~azure.core.tracing.Link] or None links: A list of links to add to the span.
    :param bool is_batch: Whether the processing is done in a batch.
    :return: A context manager that will start and end the span.
    :rtype: iterator[None]
    """
    span_impl_type: Optional[Type[AbstractSpan]] = settings.tracing_implementation()
    if span_impl_type is not None:
        context = None
        links = links or []

        # If the processing callback is called per single message, the processing span should be a child of the
        # context of the message (as opposed to messages being links in the processing span).
        if not is_batch and links:
            context = links[0].headers
            links = []
        with span_impl_type(name="EventHubs.process", kind=SpanKind.CONSUMER, links=links, context=context) as span:
            add_span_attributes(span, TraceOperationTypes.PROCESS, client, message_count=len(links))
            yield
    else:
        yield


def trace_message(
    message: Union[uamqp_Message, Message],
    amqp_transport: AmqpTransport,
    additional_attributes: Optional[Dict[str, Any]] = None,
) -> Union[uamqp_Message, Message]:
    """Add tracing information to the message and return the updated message.

    Will open and close an message span, and add trace context to the app properties of the message.

    :param uamqp.Message or ~azure.eventhub._pyamqp.message.Message message: The message to trace.
    :param ~azure.eventhub._transport._base.AmqpTransport amqp_transport: The transport to use for tracing.
    :param dict[str,any] or None additional_attributes: Additional attributes to add to the span.
    :rtype: uamqp.Message or ~azure.eventhub._pyamqp.message.Message
    :return: The message with tracing information added.
    """
    try:
        span_impl_type: Optional[Type[AbstractSpan]] = settings.tracing_implementation()
        if span_impl_type is not None:
            with span_impl_type(name="EventHubs.message", kind=SpanKind.PRODUCER) as message_span:
                headers = message_span.to_header()

                if "traceparent" in headers:
                    message = amqp_transport.update_message_app_properties(
                        message, TRACE_DIAGNOSTIC_ID_PROPERTY, headers["traceparent"]
                    )
                    message = amqp_transport.update_message_app_properties(
                        message, TRACE_PARENT_PROPERTY, headers["traceparent"]
                    )
                if "tracestate" in headers:
                    message = amqp_transport.update_message_app_properties(
                        message, TRACE_STATE_PROPERTY, headers["tracestate"]
                    )

                message_span.add_attribute(TraceAttributes.TRACE_NAMESPACE_ATTRIBUTE, TraceAttributes.TRACE_NAMESPACE)
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


def get_span_links_from_received_events(events: Union[EventData, Iterable[EventData]]) -> List[Link]:
    """Create span links from received events.

    This will extract the traceparent and tracestate from the event properties and create span links
    based on these values. The time the event was enqueued is also added as a link attribute.

    :param ~azure.eventhub.EventData or iterable[~azure.eventhub.EventData] events: The received events.
    :rtype: list[~azure.core.tracing.Link]
    :return: A list of span links.
    """
    trace_events = events if isinstance(events, Iterable) else (events,)
    links = []
    try:
        for event in trace_events:
            headers = {}
            if event.properties:
                traceparent = event.properties.get(TRACE_PARENT_PROPERTY, b"") or event.properties.get(
                    TRACE_DIAGNOSTIC_ID_PROPERTY, b""
                )
                if hasattr(traceparent, "decode"):
                    traceparent = traceparent.decode(TRACE_PROPERTY_ENCODING)
                if traceparent:
                    headers["traceparent"] = traceparent

                tracestate = event.properties.get(TRACE_STATE_PROPERTY, b"")
                if hasattr(tracestate, "decode"):
                    tracestate = tracestate.decode(TRACE_PROPERTY_ENCODING)
                if tracestate:
                    headers["tracestate"] = tracestate

            enqueued_time = event.system_properties.get(PROP_TIMESTAMP)
            attributes = {"enqueuedTime": enqueued_time} if enqueued_time else None
            links.append(Link(headers, attributes=attributes))
    except AttributeError:
        pass
    return links


def get_span_links_from_batch(batch: EventDataBatch) -> List[Link]:
    """Create span links from a batch of events.

    :param ~azure.eventhub.EventDataBatch batch: The batch of events to extract the span links from.
    :rtype: list[~azure.core.tracing.Link]
    :return: A list of span links.
    """
    links = []
    try:
        for event in batch._internal_events:  # pylint: disable=protected-access
            # pylint: disable=protected-access
            msg = event if isinstance(event, AmqpAnnotatedMessage) else event._message
            link = get_span_link_from_message(msg)
            if link:
                links.append(link)
    except AttributeError:
        pass
    return links


def get_span_link_from_message(message: Union[AmqpAnnotatedMessage, Message]) -> Optional[Link]:
    """Create a span link from a message.

    This will extract the traceparent and tracestate from the message application properties and create span links
    based on these values.

    :param message: The message to extract the traceparent and tracestate from.
    :type message: ~azure.eventhub.amqp.AmqpAnnotatedMessage
     or ~azure.eventhub._pyamqp.message.Message or ~uamqp.Message
    :rtype: ~azure.core.tracing.Link
    :return: A span link.
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
                headers["traceparent"] = traceparent

            tracestate = message.application_properties.get(TRACE_STATE_PROPERTY, b"")
            if hasattr(tracestate, "decode"):
                tracestate = tracestate.decode(TRACE_PROPERTY_ENCODING)
            if tracestate:
                headers["tracestate"] = tracestate
    except AttributeError:
        return None
    return Link(headers)


def add_span_attributes(
    span: AbstractSpan, operation_type: TraceOperationTypes, client: Optional[ClientBase], message_count: int = 0
) -> None:
    """Add attributes to span based on the operation type.

    :param ~azure.core.tracing.AbstractSpan span: The span to add attributes to.
    :param TraceOperationTypes operation_type: The type of operation to add attributes for.
    :param ~azure.eventhub._client_base.ClientBase or None client: The client that is performing the operation.
    :param int message_count: The number of messages being processed.
    """
    # pylint: disable=protected-access
    span.add_attribute(TraceAttributes.TRACE_NAMESPACE_ATTRIBUTE, TraceAttributes.TRACE_NAMESPACE)
    span.add_attribute(TraceAttributes.TRACE_MESSAGING_SYSTEM_ATTRIBUTE, TraceAttributes.TRACE_MESSAGING_SYSTEM)
    span.add_attribute(TraceAttributes.TRACE_MESSAGING_OPERATION_ATTRIBUTE, operation_type)

    if message_count > 1:
        span.add_attribute(TraceAttributes.TRACE_MESSAGING_BATCH_COUNT_ATTRIBUTE, message_count)

    if operation_type in (TraceOperationTypes.PUBLISH, TraceOperationTypes.PROCESS):
        # Maintain legacy attributes for backwards compatibility.
        if client:
            span.add_attribute(TraceAttributes.LEGACY_TRACE_MESSAGE_BUS_DESTINATION_ATTRIBUTE, client._address.path)
            span.add_attribute(TraceAttributes.LEGACY_TRACE_PEER_ADDRESS_ATTRIBUTE, client._address.hostname)

    elif operation_type == TraceOperationTypes.RECEIVE:
        if client:
            span.add_attribute(TraceAttributes.TRACE_NET_PEER_NAME_ATTRIBUTE, client._address.hostname)
            span.add_attribute(TraceAttributes.TRACE_MESSAGING_DESTINATION_ATTRIBUTE, client._address.path)
