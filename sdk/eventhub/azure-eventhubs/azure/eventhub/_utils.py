# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import sys
import platform
import datetime
import calendar
import six

from uamqp import types  # type: ignore
from uamqp.message import MessageHeader  # type: ignore

from azure.core.settings import settings  # type: ignore

from ._version import VERSION
from ._constants import (
    PROP_PARTITION_KEY_AMQP_SYMBOL,
    MAX_USER_AGENT_LENGTH,
    USER_AGENT_PREFIX,
    PROP_LAST_ENQUEUED_SEQUENCE_NUMBER,
    PROP_LAST_ENQUEUED_TIME_UTC,
    PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC,
    PROP_LAST_ENQUEUED_OFFSET
)


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

    final_user_agent = '{}/{} {} ({})'.format(USER_AGENT_PREFIX, VERSION, framework, platform_str)
    if user_agent:
        final_user_agent = '{} {}'.format(final_user_agent, user_agent)

    if len(final_user_agent) > MAX_USER_AGENT_LENGTH:
        raise ValueError("The user-agent string cannot be more than {} in length."
                         "Current user_agent string is: {} with length: {}".format(
                         MAX_USER_AGENT_LENGTH, final_user_agent, len(final_user_agent)))
    properties[types.AMQPSymbol("user-agent")] = final_user_agent
    return properties


def set_message_partition_key(message, partition_key):
    """Set the partition key as an annotation on a uamqp message.

    :param ~uamqp.Message message: The message to update.
    :param str partition_key: The partition key value.
    :rtype: None
    """
    if partition_key:
        annotations = message.annotations
        if annotations is None:
            annotations = dict()
        annotations[PROP_PARTITION_KEY_AMQP_SYMBOL] = partition_key  # pylint:disable=protected-access
        header = MessageHeader()
        header.durable = True
        message.annotations = annotations
        message.header = header


def trace_message(message, parent_span=None):
    """Add tracing information to this message.

    Will open and close a "Azure.EventHubs.message" span, and
    add the "DiagnosticId" as app properties of the message.
    """
    span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
    if span_impl_type is not None:
        current_span = parent_span or span_impl_type(span_impl_type.get_current_span())
        message_span = current_span.span(name="Azure.EventHubs.message")
        message_span.start()
        app_prop = dict(message.properties) if message.properties else dict()
        app_prop.setdefault(b"Diagnostic-Id", message_span.get_trace_parent().encode('ascii'))
        message.properties = app_prop
        message_span.finish()


def trace_link_message(message, parent_span=None):
    """Link the current message to current span.

    Will extract DiagnosticId if available.
    """
    span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
    if span_impl_type is not None:
        current_span = parent_span or span_impl_type(span_impl_type.get_current_span())
        if current_span and message.application_properties:
            traceparent = message.application_properties.get(b"Diagnostic-Id", "").decode('ascii')
            if traceparent:
                current_span.link(traceparent)


def event_position_selector(value, inclusive=False):
    """
    Creates a selector expression of the offset.

    """
    operator = ">=" if inclusive else ">"
    if isinstance(value, datetime.datetime):  # pylint:disable=no-else-return
        timestamp = (calendar.timegm(value.utctimetuple()) * 1000) + (value.microsecond / 1000)
        return ("amqp.annotation.x-opt-enqueued-time {} '{}'".format(operator, int(timestamp))).encode('utf-8')
    elif isinstance(value, six.integer_types):
        return ("amqp.annotation.x-opt-sequence-number {} '{}'".format(operator, value)).encode('utf-8')
    return ("amqp.annotation.x-opt-offset {} '{}'".format(operator, value)).encode('utf-8')


def get_last_enqueued_event_properties(event_data):
    """Extracts the last enqueued event in from the received event delivery annotations.
    :rtype: Dict[str, Any]
    """
    # pylint: disable=protected-access
    if event_data._last_enqueued_event_properties:
        return event_data._last_enqueued_event_properties

    if event_data.message.delivery_annotations:
        sequence_number = event_data.message.delivery_annotations.get(PROP_LAST_ENQUEUED_SEQUENCE_NUMBER, None)
        enqueued_time_stamp = event_data.message.delivery_annotations.get(PROP_LAST_ENQUEUED_TIME_UTC, None)
        if enqueued_time_stamp:
            enqueued_time_stamp = utc_from_timestamp(float(enqueued_time_stamp)/1000)
        retrieval_time_stamp = event_data.message.delivery_annotations.get(PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC, None)
        if retrieval_time_stamp:
            retrieval_time_stamp = utc_from_timestamp(float(retrieval_time_stamp)/1000)
        offset_bytes = event_data.message.delivery_annotations.get(PROP_LAST_ENQUEUED_OFFSET, None)
        offset = offset_bytes.decode('UTF-8') if offset_bytes else None

        event_data._last_enqueued_event_properties = {
            "sequence_number": sequence_number,
            "offset": offset,
            "enqueued_time": enqueued_time_stamp,
            "retrieval_time": retrieval_time_stamp
        }
        return event_data._last_enqueued_event_properties
    return None
