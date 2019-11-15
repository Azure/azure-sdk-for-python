# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import sys
import platform

from uamqp import types  # type: ignore
from uamqp.message import MessageHeader  # type: ignore

from azure.core.settings import settings # type: ignore

from azure.eventhub import __version__
from ._constants import PROP_PARTITION_KEY_AMQP_SYMBOL, MAX_USER_AGENT_LENGTH


def create_properties(user_agent=None):
    """
    Format the properties with which to instantiate the connection.
    This acts like a user agent over HTTP.

    :rtype: dict
    """
    properties = {}
    product = "azsdk-python-eventhubs"
    properties[types.AMQPSymbol("product")] = product
    properties[types.AMQPSymbol("version")] = __version__
    framework = "Python {}.{}.{}, {}".format(
        sys.version_info[0], sys.version_info[1], sys.version_info[2], platform.python_implementation()
    )
    properties[types.AMQPSymbol("framework")] = framework
    platform_str = platform.platform()
    properties[types.AMQPSymbol("platform")] = platform_str

    final_user_agent = '{}/{} ({}, {})'.format(product, __version__, framework, platform_str)
    if user_agent:
        final_user_agent = '{}, {}'.format(final_user_agent, user_agent)

    if len(final_user_agent) > MAX_USER_AGENT_LENGTH:
        raise ValueError("The user-agent string cannot be more than {} in length."
                         "Current user_agent string is: {} with length: {}".format(
                         MAX_USER_AGENT_LENGTH, final_user_agent, len(final_user_agent)))
    properties[types.AMQPSymbol("user-agent")] = final_user_agent
    return properties


def parse_sas_token(sas_token):
    """Parse a SAS token into its components.

    :param sas_token: The SAS token.
    :type sas_token: str
    :rtype: dict[str, str]
    """
    sas_data = {}
    token = sas_token.partition(' ')[2]
    fields = token.split('&')
    for field in fields:
        key, value = field.split('=', 1)
        sas_data[key.lower()] = value
    return sas_data


def set_message_partition_key(message, partition_key):
    """Set the partition key as an annotation on a uamqp message.

    :param ~uamqp.Message message: The message to update.
    :param bytes partition_key: The partition key value.
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
        app_prop = dict(message.application_properties) if message.application_properties else dict()
        app_prop.setdefault(b"Diagnostic-Id", message_span.get_trace_parent().encode('ascii'))
        message.application_properties = app_prop
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
