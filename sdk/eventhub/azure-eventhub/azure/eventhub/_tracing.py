# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
from contextlib import contextmanager
from enum import Enum
import logging
from typing import (
    TYPE_CHECKING,
    Type,
    Optional,
    Dict,
    List,
    Union,
    Any,
    Iterable,
    Iterator
)

from azure.core import CaseInsensitiveEnumMeta
from azure.core.settings import settings
from azure.core.tracing import SpanKind, Link

from .amqp import AmqpAnnotatedMessage
from ._constants import PROP_TIMESTAMP

if TYPE_CHECKING:
    # pylint: disable=ungrouped-imports
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


class TraceAttributes:
    TRACE_NAMESPACE_ATTRIBUTE = "az.namespace"
    TRACE_NAMESPACE = "Microsoft.EventHub"

    TRACE_MESSAGING_SYSTEM_ATTRIBUTE = "messaging.system"
    TRACE_MESSAGING_SYSTEM = "eventhubs"

    TRACE_NET_PEER_NAME_ATTRIBUTE = "net.peer.name"
    TRACE_MESSAGING_DESTINATION_ATTRIBUTE = "messaging.destination.name"
    TRACE_MESSAGING_SOURCE_ATTRIBUTE = "messaging.source.name"
    TRACE_MESSAGING_OPERATION_ATTRIBUTE = "messaging.operation"
    TRACE_MESSAGING_BATCH_COUNT_ATTRIBUTE = "messaging.batch.message_count"

    LEGACY_TRACE_COMPONENT_ATTRIBUTE = "component"
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
    """Tracing for message sending."""
    span_impl_type: Type[AbstractSpan] = settings.tracing_implementation()
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
)  -> Iterator[None]:
    """Tracing for message receiving."""
    span_impl_type: Type[AbstractSpan] = settings.tracing_implementation()
    if span_impl_type is not None:
        links = links or []
        with span_impl_type(
            name="EventHubs.receive", kind=SpanKind.CLIENT, links=links, start_time=start_time
        ) as span:
            add_span_attributes(span, TraceOperationTypes.RECEIVE, client, message_count=len(links))
            yield
    else:
        yield


@contextmanager
def process_context_manager(client: Optional[ClientBase], links: Optional[List[Link]] = None) -> Iterator[None]:
    """Tracing for message processing."""
    span_impl_type: Type[AbstractSpan] = settings.tracing_implementation()
    if span_impl_type is not None:
        links = links or []
        with span_impl_type(name="EventHubs.process", kind=SpanKind.CONSUMER, links=links) as span:
            add_span_attributes(span, TraceOperationTypes.PROCESS, client, message_count=len(links))
            yield
    else:
        yield


def trace_message(
    message: Union[uamqp_Message, Message],
    amqp_transport: AmqpTransport,
    additional_attributes: Optional[Dict[str, Any]] = None,
    parent_span: Optional[AbstractSpan] = None
) -> Union[uamqp_Message, Message]:
    """Add tracing information to the message and return the updated message.

    Will open and close an message span, and add trace context to the app properties of the message.
    """
    try:
        span_impl_type: Type[AbstractSpan] = settings.tracing_implementation()
        if span_impl_type is not None:
            current_span = parent_span or span_impl_type(
                span_impl_type.get_current_span()
            )

            with current_span.span(name="EventHubs.message", kind=SpanKind.PRODUCER) as message_span:
                headers = message_span.to_header()

                if "traceparent" in headers:
                    message = amqp_transport.update_message_app_properties(
                        message,
                        b"Diagnostic-Id",
                        headers["traceparent"].encode("ascii")
                    )
                    message = amqp_transport.update_message_app_properties(
                        message,
                        b"traceparent",
                        headers["traceparent"].encode("ascii")
                    )
                if "tracestate" in headers:
                    message = amqp_transport.update_message_app_properties(
                        message,
                        b"tracestate",
                        headers["tracestate"].encode("ascii")
                    )

                message_span.add_attribute(
                    TraceAttributes.TRACE_NAMESPACE_ATTRIBUTE, TraceAttributes.TRACE_NAMESPACE)
                message_span.add_attribute(
                    TraceAttributes.TRACE_MESSAGING_SYSTEM_ATTRIBUTE, TraceAttributes.TRACE_MESSAGING_SYSTEM)

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
    """
    # pylint:disable=isinstance-second-argument-not-valid-type
    trace_events = events if isinstance(events, Iterable) else (events,)
    links = []
    try:
        for event in trace_events:
            if event.properties:
                headers = {}
                traceparent = event.properties.get(b"traceparent", b"").decode("ascii")

                if traceparent:
                    headers["traceparent"] = traceparent

                tracestate = event.properties.get(b"tracestate", b"").decode("ascii")
                if tracestate:
                    headers["tracestate"] = tracestate

                enqueued_time = event.system_properties.get(PROP_TIMESTAMP)
                attributes = {'enqueued_time': enqueued_time} if enqueued_time else None
                links.append(Link(headers, attributes=attributes))
    except AttributeError:
        pass
    return links


def get_span_links_from_batch(batch: EventDataBatch) -> List[Link]:
    """Create span links from a batch of events."""
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
    """
    headers = {}
    try:
        if message.application_properties:
            traceparent = message.application_properties.get(b"traceparent", b"").decode("ascii")
            if traceparent:
                headers["traceparent"] = traceparent

            tracestate = message.application_properties.get(b"tracestate", b"").decode("ascii")
            if tracestate:
                headers["tracestate"] = tracestate
    except AttributeError:
        return None
    return Link(headers) if headers else None


def add_span_attributes(
        span: AbstractSpan,
        operation_type: TraceOperationTypes,
        client: Optional[ClientBase],
        message_count: int = 0
) -> None:
    """Add attributes to span based on the operation type."""

    span.add_attribute(TraceAttributes.TRACE_NAMESPACE_ATTRIBUTE, TraceAttributes.TRACE_NAMESPACE)
    span.add_attribute(TraceAttributes.TRACE_MESSAGING_SYSTEM_ATTRIBUTE, TraceAttributes.TRACE_MESSAGING_SYSTEM)
    span.add_attribute(TraceAttributes.TRACE_MESSAGING_OPERATION_ATTRIBUTE, operation_type)

    if message_count > 1:
        span.add_attribute(TraceAttributes.TRACE_MESSAGING_BATCH_COUNT_ATTRIBUTE, message_count)

    if operation_type == TraceOperationTypes.PUBLISH:
        # Maintain legacy attributes for backwards compatibility.
        span.add_attribute(TraceAttributes.LEGACY_TRACE_COMPONENT_ATTRIBUTE, TraceAttributes.TRACE_MESSAGING_SYSTEM)
        if client:
            span.add_attribute(TraceAttributes.LEGACY_TRACE_MESSAGE_BUS_DESTINATION_ATTRIBUTE, client._address.path)  # pylint: disable=protected-access
            span.add_attribute(TraceAttributes.LEGACY_TRACE_PEER_ADDRESS_ATTRIBUTE, client._address.hostname)  # pylint: disable=protected-access

    elif operation_type == TraceOperationTypes.PROCESS:
        # Maintain legacy attributes for backwards compatibility.
        span.add_attribute(TraceAttributes.LEGACY_TRACE_COMPONENT_ATTRIBUTE, TraceAttributes.TRACE_MESSAGING_SYSTEM)
        if client:
            span.add_attribute(TraceAttributes.LEGACY_TRACE_PEER_ADDRESS_ATTRIBUTE, client._address.hostname)  # pylint: disable=protected-access
            span.add_attribute(TraceAttributes.TRACE_MESSAGING_SOURCE_ATTRIBUTE, client._address.path)  # pylint: disable=protected-access

    elif operation_type == TraceOperationTypes.RECEIVE:
        if client:
            span.add_attribute(TraceAttributes.TRACE_NET_PEER_NAME_ATTRIBUTE, client._address.hostname)  # pylint: disable=protected-access
            span.add_attribute(TraceAttributes.TRACE_MESSAGING_SOURCE_ATTRIBUTE, client._address.path)  # pylint: disable=protected-access
