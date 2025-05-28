# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import sys
import datetime
import logging
import functools
import platform
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Type,
    TYPE_CHECKING,
    Union,
    Tuple,
    cast,
    Callable,
    Iterable,
)
from datetime import timezone

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from .._version import VERSION
from .constants import (
    JWT_TOKEN_SCOPE,
    TOKEN_TYPE_JWT,
    TOKEN_TYPE_SASTOKEN,
    DEAD_LETTER_QUEUE_SUFFIX,
    TRANSFER_DEAD_LETTER_QUEUE_SUFFIX,
    USER_AGENT_PREFIX,
)
from ..amqp import AmqpAnnotatedMessage

if TYPE_CHECKING:
    try:
        from uamqp import types as uamqp_types
        from uamqp.authentication import JWTTokenAuth as uamqp_JWTTokenAuth
    except ImportError:
        pass
    from .._pyamqp.authentication import JWTTokenAuth as pyamqp_JWTTokenAuth
    from .message import ServiceBusReceivedMessage, ServiceBusMessage
    from azure.core.credentials import AzureSasCredential
    from .._servicebus_session import BaseSession
    from .._transport._base import AmqpTransport

    MessagesType = Union[
        Mapping[str, Any],
        ServiceBusMessage,
        AmqpAnnotatedMessage,
        Iterable[Mapping[str, Any]],
        Iterable[ServiceBusMessage],
        Iterable[AmqpAnnotatedMessage],
    ]

    SingleMessageType = Union[Mapping[str, Any], ServiceBusMessage, AmqpAnnotatedMessage]

_log = logging.getLogger(__name__)

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

    :keyword amqp_transport: The AMQP transport type.
    :paramtype amqp_transport: ~azure.servicebus._transport._base.AmqpTransport

    :return: The properties to add to the connection.
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
        f"{USER_AGENT_PREFIX}/{VERSION} {amqp_transport.TRANSPORT_IDENTIFIER} " f"{framework} ({platform_str})"
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
        ) from None


def get_renewable_lock_duration(renewable: Union["ServiceBusReceivedMessage", "BaseSession"]) -> datetime.timedelta:
    try:
        return max(renewable.locked_until_utc - utc_now(), datetime.timedelta(seconds=0))
    except AttributeError:
        raise TypeError(
            "Registered object is not renewable, renewable must be"
            + "a ServiceBusReceivedMessage or a ServiceBusSession from a sessionful ServiceBusReceiver."
        ) from None


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
            update_token=True,
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
    entity_name = queue_name if queue_name else (topic_name + "/Subscriptions/" + subscription_name)
    entity_name = (
        f"{entity_name}" f"{TRANSFER_DEAD_LETTER_QUEUE_SUFFIX if transfer_deadletter else DEAD_LETTER_QUEUE_SUFFIX}"
    )

    return entity_name


def _convert_to_single_service_bus_message(
    message: "SingleMessageType", message_type: Type["ServiceBusMessage"], to_outgoing_amqp_message: Callable
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
        ) from None


def transform_outbound_messages(
    messages: "MessagesType", message_type: Type["ServiceBusMessage"], to_outgoing_amqp_message: Callable
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
    :param callable to_outgoing_amqp_message: A function that converts the input message to an AMQP message.
    :return: A list of ServiceBusMessage or a single ServiceBusMessage transformed.
    :rtype: ~azure.servicebus.ServiceBusMessage or list[~azure.servicebus.ServiceBusMessage]
    """
    if isinstance(messages, Iterable) and not isinstance(messages, Mapping):
        return [_convert_to_single_service_bus_message(m, message_type, to_outgoing_amqp_message) for m in messages]
    return _convert_to_single_service_bus_message(messages, message_type, to_outgoing_amqp_message)


def strip_protocol_from_uri(uri: str) -> str:
    """Removes the protocol (e.g. http:// or sb://) from a URI, such as the FQDN.
    :param str uri: The URI to modify.
    :return: The URI without the protocol.
    :rtype: str
    """
    left_slash_pos = uri.find("//")
    if left_slash_pos != -1:
        return uri[left_slash_pos + 2 :]
    return uri


def parse_sas_credential(credential: "AzureSasCredential") -> Tuple:
    sas = credential.signature
    parsed_sas = sas.split("&")
    expiry = None
    for item in parsed_sas:
        if item.startswith("se="):
            expiry = int(item[3:])
    return (sas, expiry)
