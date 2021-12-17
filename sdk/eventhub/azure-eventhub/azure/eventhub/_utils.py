# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

from contextlib import contextmanager
import sys
import platform
import datetime
import calendar
import logging
from typing import TYPE_CHECKING, Type, Optional, Dict, Union, Any, Iterable, Tuple, Mapping

import six

from uamqp import types
from uamqp.message import MessageHeader

from azure.core.settings import settings
from azure.core.tracing import SpanKind, Link

from .amqp import AmqpAnnotatedMessage
from ._version import VERSION
from ._constants import (
    PROP_PARTITION_KEY_AMQP_SYMBOL,
    MAX_USER_AGENT_LENGTH,
    USER_AGENT_PREFIX,
    PROP_LAST_ENQUEUED_SEQUENCE_NUMBER,
    PROP_LAST_ENQUEUED_TIME_UTC,
    PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC,
    PROP_LAST_ENQUEUED_OFFSET,
    PROP_TIMESTAMP,
)

if TYPE_CHECKING:
    # pylint: disable=ungrouped-imports
    from uamqp import Message
    from azure.core.tracing import AbstractSpan
    from azure.core.credentials import AzureSasCredential
    from ._common import EventData

    MessagesType = Union[
        AmqpAnnotatedMessage,
        EventData,
        Iterable[Union[AmqpAnnotatedMessage, EventData]],
    ]

_LOGGER = logging.getLogger(__name__)


class UTC(datetime.tzinfo):
    """Time Zone info for handling UTC"""

    def utcoffset(self, dt):
        """UTF offset for UTC is 0."""
        return datetime.timedelta(0)

    def tzname(self, dt):
        """Timestamp representation."""
        return "Z"

    def dst(self, dt):
        """No daylight saving for UTC."""
        return datetime.timedelta(hours=1)


try:
    from datetime import timezone  # pylint: disable=ungrouped-imports

    TZ_UTC = timezone.utc  # type: ignore
except ImportError:
    TZ_UTC = UTC()  # type: ignore


def utc_from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=TZ_UTC)


def create_properties(user_agent=None):
    # type: (Optional[str]) -> Dict[types.AMQPSymbol, str]
    """
    Format the properties with which to instantiate the connection.
    This acts like a user agent over HTTP.

    :rtype: dict
    """
    properties = {}
    properties[types.AMQPSymbol("product")] = USER_AGENT_PREFIX
    properties[types.AMQPSymbol("version")] = VERSION
    framework = "Python/{}.{}.{}".format(
        sys.version_info[0], sys.version_info[1], sys.version_info[2]
    )
    properties[types.AMQPSymbol("framework")] = framework
    platform_str = platform.platform()
    properties[types.AMQPSymbol("platform")] = platform_str

    final_user_agent = "{}/{} {} ({})".format(
        USER_AGENT_PREFIX, VERSION, framework, platform_str
    )
    if user_agent:
        final_user_agent = "{} {}".format(user_agent, final_user_agent)

    if len(final_user_agent) > MAX_USER_AGENT_LENGTH:
        raise ValueError(
            "The user-agent string cannot be more than {} in length."
            "Current user_agent string is: {} with length: {}".format(
                MAX_USER_AGENT_LENGTH, final_user_agent, len(final_user_agent)
            )
        )
    properties[types.AMQPSymbol("user-agent")] = final_user_agent
    return properties


def set_message_partition_key(message, partition_key):
    # type: (Message, Optional[Union[bytes, str]]) -> None
    """Set the partition key as an annotation on a uamqp message.

    :param ~uamqp.Message message: The message to update.
    :param str partition_key: The partition key value.
    :rtype: None
    """
    if partition_key:
        annotations = message.annotations
        if annotations is None:
            annotations = dict()
        annotations[
            PROP_PARTITION_KEY_AMQP_SYMBOL
        ] = partition_key  # pylint:disable=protected-access
        header = MessageHeader()
        header.durable = True
        message.annotations = annotations
        message.header = header


@contextmanager
def send_context_manager():
    span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]

    if span_impl_type is not None:
        with span_impl_type(name="Azure.EventHubs.send", kind=SpanKind.CLIENT) as child:
            yield child
    else:
        yield None


def trace_message(event, parent_span=None):
    # type: (EventData, Optional[AbstractSpan]) -> None
    """Add tracing information to this event.

    Will open and close a "Azure.EventHubs.message" span, and
    add the "DiagnosticId" as app properties of the event.
    """
    try:
        span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
        if span_impl_type is not None:
            current_span = parent_span or span_impl_type(
                span_impl_type.get_current_span()
            )
            link = Link({"traceparent": current_span.get_trace_parent()})
            with current_span.span(
                name="Azure.EventHubs.message", kind=SpanKind.PRODUCER, links=[link]
            ) as message_span:
                message_span.add_attribute("az.namespace", "Microsoft.EventHub")
                if not event.properties:
                    event.properties = dict()
                event.properties.setdefault(
                    b"Diagnostic-Id", message_span.get_trace_parent().encode("ascii")
                )
    except Exception as exp:  # pylint:disable=broad-except
        _LOGGER.warning("trace_message had an exception %r", exp)


def get_event_links(events):
    # pylint:disable=isinstance-second-argument-not-valid-type
    trace_events = (
        events if isinstance(events, Iterable) else (events,)
    )
    links = []
    try:
        for event in trace_events:  # type: ignore
            if event.properties:
                traceparent = event.properties.get(b"Diagnostic-Id", "").decode("ascii")
                if traceparent:
                    links.append(
                        Link(
                            {"traceparent": traceparent},
                            attributes={
                                "enqueuedTime": event.message.annotations.get(
                                    PROP_TIMESTAMP
                                )
                            },
                        )
                    )
    except AttributeError:
        pass
    return links


def event_position_selector(value, inclusive=False):
    # type: (Union[int, str, datetime.datetime], bool) -> bytes
    """Creates a selector expression of the offset."""
    operator = ">=" if inclusive else ">"
    if isinstance(value, datetime.datetime):  # pylint:disable=no-else-return
        timestamp = (calendar.timegm(value.utctimetuple()) * 1000) + (
            value.microsecond / 1000
        )
        return (
            "amqp.annotation.x-opt-enqueued-time {} '{}'".format(
                operator, int(timestamp)
            )
        ).encode("utf-8")
    elif isinstance(value, six.integer_types):
        return (
            "amqp.annotation.x-opt-sequence-number {} '{}'".format(operator, value)
        ).encode("utf-8")
    return ("amqp.annotation.x-opt-offset {} '{}'".format(operator, value)).encode(
        "utf-8"
    )


def get_last_enqueued_event_properties(event_data):
    # type: (EventData) -> Optional[Dict[str, Any]]
    """Extracts the last enqueued event in from the received event delivery annotations.

    :rtype: Dict[str, Any]
    """
    # pylint: disable=protected-access
    if event_data._last_enqueued_event_properties:
        return event_data._last_enqueued_event_properties

    if event_data.message.delivery_annotations:
        sequence_number = event_data.message.delivery_annotations.get(
            PROP_LAST_ENQUEUED_SEQUENCE_NUMBER, None
        )
        enqueued_time_stamp = event_data.message.delivery_annotations.get(
            PROP_LAST_ENQUEUED_TIME_UTC, None
        )
        if enqueued_time_stamp:
            enqueued_time_stamp = utc_from_timestamp(float(enqueued_time_stamp) / 1000)
        retrieval_time_stamp = event_data.message.delivery_annotations.get(
            PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC, None
        )
        if retrieval_time_stamp:
            retrieval_time_stamp = utc_from_timestamp(
                float(retrieval_time_stamp) / 1000
            )
        offset_bytes = event_data.message.delivery_annotations.get(
            PROP_LAST_ENQUEUED_OFFSET, None
        )
        offset = offset_bytes.decode("UTF-8") if offset_bytes else None

        event_data._last_enqueued_event_properties = {
            "sequence_number": sequence_number,
            "offset": offset,
            "enqueued_time": enqueued_time_stamp,
            "retrieval_time": retrieval_time_stamp,
        }
        return event_data._last_enqueued_event_properties
    return None


def parse_sas_credential(credential):
    # type: (AzureSasCredential) -> Tuple
    sas = credential.signature
    parsed_sas = sas.split("&")
    expiry = None
    for item in parsed_sas:
        if item.startswith("se="):
            expiry = int(item[3:])
    return (sas, expiry)


def transform_outbound_single_message(message, message_type):
    # type: (Union[AmqpAnnotatedMessage, EventData], Type[EventData]) -> EventData
    """
    This method serves multiple goals:
    1. update the internal message to reflect any updates to settable properties on EventData
    2. transform the AmqpAnnotatedMessage to be EventData
    :param message: A single instance of message of type EventData
        or AmqpAnnotatedMessage.
    :type message: ~azure.eventhub.common.EventData, ~azure.eventhub.amqp.AmqpAnnotatedMessage
    :param Type[EventData] message_type: The class type to return the messages as.
    :rtype: EventData
    """
    try:
        # EventData
        # pylint: disable=protected-access
        return message._to_outgoing_message()  # type: ignore
    except AttributeError:
        # AmqpAnnotatedMessage
        # pylint: disable=protected-access
        return message_type._from_message(
            message=message._to_outgoing_amqp_message(), raw_amqp_message=message  # type: ignore
        )


def decode_with_recurse(data, encoding="UTF-8"):
    # type: (Any, str) -> Any
    # pylint:disable=isinstance-second-argument-not-valid-type
    """
    If data is of a compatible type, iterates through nested structure and decodes all binary
        strings with provided encoding.
    :param Any data: The data object which, if compatible, will be iterated through to decode binary string.
    :param encoding: The encoding to use for decoding data.
        Default is 'UTF-8'
    :rtype: Any
    """

    if isinstance(data, str):
        return data
    if isinstance(data, six.binary_type):
        return data.decode(encoding)
    if isinstance(data, Mapping): # pylint:disable=isinstance-second-argument-not-valid-type
        decoded_mapping = {}
        for k, v in data.items():
            decoded_key = decode_with_recurse(k, encoding)
            decoded_val = decode_with_recurse(v, encoding)
            decoded_mapping[decoded_key] = decoded_val
        return decoded_mapping
    if isinstance(data, Iterable): # pylint:disable=isinstance-second-argument-not-valid-type
        decoded_list = []
        for d in data:
            decoded_list.append(decode_with_recurse(d, encoding))
        return decoded_list

    return data
