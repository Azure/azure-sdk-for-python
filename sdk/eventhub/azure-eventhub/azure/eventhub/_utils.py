# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import sys
import platform
import datetime
import calendar
import logging
from typing import TYPE_CHECKING, cast, Type, Optional, Dict, Union, Any, Iterable, Tuple, Mapping, Callable
from datetime import timezone
from .amqp import AmqpAnnotatedMessage, AmqpMessageHeader
from ._version import VERSION
from ._constants import (
    MAX_USER_AGENT_LENGTH,
    USER_AGENT_PREFIX,
    PROP_LAST_ENQUEUED_SEQUENCE_NUMBER,
    PROP_LAST_ENQUEUED_TIME_UTC,
    PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC,
    PROP_LAST_ENQUEUED_OFFSET,
)

if TYPE_CHECKING:
    from ._transport._base import AmqpTransport
    from ._pyamqp.message import Message as pyamqp_Message

    try:
        from uamqp import types as uamqp_types
        from uamqp import Message as uamqp_Message
    except ImportError:
        uamqp_types = None
    from azure.core.credentials import AzureSasCredential
    from ._common import EventData

    MessagesType = Union[
        AmqpAnnotatedMessage,
        EventData,
        Iterable[Union[AmqpAnnotatedMessage, EventData]],
    ]

_LOGGER = logging.getLogger(__name__)


TZ_UTC: timezone = timezone.utc
# Number of seconds between the Unix epoch (1/1/1970) and year 1 CE.
# This is the lowest value that can be represented by an AMQP timestamp.
CE_ZERO_SECONDS: int = -62_135_596_800


def utc_from_timestamp(timestamp: float) -> datetime.datetime:
    """
    :param float timestamp: Timestamp in seconds to be converted to datetime.
    :rtype: datetime.datetime
    :returns: A datetime object representing the timestamp in UTC.
    """
    # The AMQP timestamp is the number of seconds since the Unix epoch.
    # AMQP brokers represent the lowest value as -62_135_596_800 (the
    # number of seconds between the Unix epoch (1/1/1970) and year 1 CE) as
    # a sentinel for a time which is not set.
    if timestamp == CE_ZERO_SECONDS:
        return datetime.datetime.min.replace(tzinfo=TZ_UTC)
    return datetime.datetime.fromtimestamp(timestamp, tz=TZ_UTC)


def create_properties(
    user_agent: Optional[str] = None, *, amqp_transport: AmqpTransport
) -> Union[Dict[uamqp_types.AMQPSymbol, str], Dict[str, str]]:
    """
    Format the properties with which to instantiate the connection.
    This acts like a user agent over HTTP.

    :param str or None user_agent: The user agent string.
    :keyword ~azure.eventhub._transport._base.AmqpTransport amqp_transport: The AMQP transport.
    :rtype: dict
    :return: The properties.
    """
    properties: Dict[Any, str] = {}
    properties[amqp_transport.PRODUCT_SYMBOL] = USER_AGENT_PREFIX
    properties[amqp_transport.VERSION_SYMBOL] = VERSION
    framework = f"Python/{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"
    properties[amqp_transport.FRAMEWORK_SYMBOL] = framework
    platform_str = platform.platform()
    properties[amqp_transport.PLATFORM_SYMBOL] = platform_str

    final_user_agent = f"{USER_AGENT_PREFIX}/{VERSION} {amqp_transport.TRANSPORT_IDENTIFIER} {framework} ({platform_str})"  # pylint: disable=line-too-long
    if user_agent:
        final_user_agent = f"{user_agent} {final_user_agent}"

    if len(final_user_agent) > MAX_USER_AGENT_LENGTH:
        raise ValueError(
            f"The user-agent string cannot be more than {MAX_USER_AGENT_LENGTH} in length."
            f"Current user_agent string is: {final_user_agent} with length: {len(final_user_agent)}"
        )
    properties[amqp_transport.USER_AGENT_SYMBOL] = final_user_agent
    return properties


def set_event_partition_key(
    event: Union[AmqpAnnotatedMessage, EventData],
    partition_key: Optional[Union[bytes, str]],
    amqp_transport: AmqpTransport,
) -> None:
    if not partition_key:
        return

    try:
        raw_message = event.raw_amqp_message  # type: ignore
    except AttributeError:
        raw_message = event

    annotations = raw_message.annotations
    if annotations is None:
        annotations = {}
    annotations[amqp_transport.PROP_PARTITION_KEY_AMQP_SYMBOL] = partition_key
    if not raw_message.header:
        raw_message.header = AmqpMessageHeader(header=True)
    else:
        raw_message.header.durable = True


def event_position_selector(value: Union[str, int, datetime.datetime], inclusive: bool = False) -> bytes:
    """Creates a selector expression of the offset.

    :param int or str or datetime.datetime value: The offset value to use for the offset.
    :param bool inclusive: Whether to include the value in the range.
    :rtype: bytes
    :return: The selector filter expression.
    """
    operator = ">=" if inclusive else ">"
    if isinstance(value, datetime.datetime):  # pylint:disable=no-else-return
        timestamp = (calendar.timegm(value.utctimetuple()) * 1000) + (value.microsecond / 1000)
        return (f"amqp.annotation.x-opt-enqueued-time {operator} '{int(timestamp)}'").encode("utf-8")
    elif isinstance(value, int):
        return (f"amqp.annotation.x-opt-sequence-number {operator} '{value}'").encode("utf-8")
    return (f"amqp.annotation.x-opt-offset {operator} '{value}'").encode("utf-8")


def get_last_enqueued_event_properties(event_data: EventData) -> Optional[Dict[str, Any]]:
    """Extracts the last enqueued event in from the received event delivery annotations.

    :param ~azure.eventhub.EventData event_data: The received Event Data.
    :rtype: dict[str, any] or None
    :return: The enqueued event properties dictionary.
    """
    # pylint: disable=protected-access
    if event_data._last_enqueued_event_properties:
        return event_data._last_enqueued_event_properties

    if event_data._message.delivery_annotations:
        sequence_number = event_data._message.delivery_annotations.get(PROP_LAST_ENQUEUED_SEQUENCE_NUMBER, None)
        enqueued_time_stamp = event_data._message.delivery_annotations.get(PROP_LAST_ENQUEUED_TIME_UTC, None)
        if enqueued_time_stamp:
            enqueued_time_stamp = utc_from_timestamp(float(enqueued_time_stamp) / 1000)
        retrieval_time_stamp = event_data._message.delivery_annotations.get(PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC, None)
        if retrieval_time_stamp:
            retrieval_time_stamp = utc_from_timestamp(float(retrieval_time_stamp) / 1000)
        offset_bytes = event_data._message.delivery_annotations.get(PROP_LAST_ENQUEUED_OFFSET, None)
        offset = offset_bytes.decode("UTF-8") if offset_bytes else None

        event_data._last_enqueued_event_properties = {
            "sequence_number": sequence_number,
            "offset": offset,
            "enqueued_time": enqueued_time_stamp,
            "retrieval_time": retrieval_time_stamp,
        }
        return event_data._last_enqueued_event_properties
    return None


def parse_sas_credential(credential: AzureSasCredential) -> Tuple[str, Optional[int]]:
    sas = credential.signature
    parsed_sas = sas.split("&")
    expiry = None
    for item in parsed_sas:
        if item.startswith("se="):
            expiry = int(item[3:])
    return (sas, expiry)


def transform_outbound_single_message(
    message: Union[AmqpAnnotatedMessage, EventData],
    message_type: Type[EventData],
    to_outgoing_amqp_message: Callable[[AmqpAnnotatedMessage], Union[uamqp_Message, pyamqp_Message]],
) -> EventData:
    """
    This method serves multiple goals:
    1. update the internal message to reflect any updates to settable properties on EventData
    2. transform the AmqpAnnotatedMessage to be EventData
    :param message: A single instance of message of type EventData
        or AmqpAnnotatedMessage.
    :type message: ~azure.eventhub.EventData or ~azure.eventhub.amqp.AmqpAnnotatedMessage
    :param type[~azure.eventhub.EventData] message_type: The class type to return the messages as.
    :param callable to_outgoing_amqp_message: A function to transform the message
    :rtype:  ~azure.eventhub.EventData
    :return: The transformed message.
    """
    try:
        # pylint: disable=protected-access
        # If EventData, set EventData._message to uamqp/pyamqp.Message right before sending.
        message = cast("EventData", message)
        message._message = to_outgoing_amqp_message(message.raw_amqp_message)
        return message  # type: ignore
    except AttributeError:
        # pylint: disable=protected-access
        # If AmqpAnnotatedMessage, create EventData object with _from_message.
        # event_data._message will be set to outgoing uamqp/pyamqp.Message.
        # event_data.raw_amqp_message will be set to AmqpAnnotatedMessage.
        message = cast(AmqpAnnotatedMessage, message)
        amqp_message = to_outgoing_amqp_message(message)
        return message_type._from_message(message=amqp_message, raw_amqp_message=message)  # type: ignore


def decode_with_recurse(data: Any, encoding: str = "UTF-8") -> Any:
    """
    If data is of a compatible type, iterates through nested structure and decodes all binary
        strings with provided encoding.
    :param any data: The data object which, if compatible, will be iterated through to decode binary string.
    :param str encoding: The encoding to use for decoding data.
        Default is 'UTF-8'
    :rtype: any
    :return: The decoded data object.
    """

    if isinstance(data, str):
        return data
    if isinstance(data, bytes):
        return data.decode(encoding)
    if isinstance(data, Mapping):
        decoded_mapping = {}
        for k, v in data.items():
            decoded_key = decode_with_recurse(k, encoding)
            decoded_val = decode_with_recurse(v, encoding)
            decoded_mapping[decoded_key] = decoded_val
        return decoded_mapping
    if isinstance(data, Iterable):
        decoded_list = []
        for d in data:
            decoded_list.append(decode_with_recurse(d, encoding))
        return decoded_list

    return data
