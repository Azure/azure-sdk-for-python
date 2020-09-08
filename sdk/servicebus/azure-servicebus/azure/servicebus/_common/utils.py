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
import time
from typing import Optional, Dict, Tuple
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from uamqp import authentication, types

from ..exceptions import ServiceBusError
from .._version import VERSION
from .constants import (
    JWT_TOKEN_SCOPE,
    TOKEN_TYPE_JWT,
    TOKEN_TYPE_SASTOKEN,
    DEAD_LETTER_QUEUE_SUFFIX,
    TRANSFER_DEAD_LETTER_QUEUE_SUFFIX,
    USER_AGENT_PREFIX
)

_log = logging.getLogger(__name__)


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


def utc_now():
    return datetime.datetime.now(tz=TZ_UTC)


# This parse_conn_str is used for mgmt, the other in base_handler for handlers.  Should be unified.
def parse_conn_str(conn_str):
    # type: (str) -> Tuple[str, Optional[str], Optional[str], str, Optional[str], Optional[int]]
    endpoint = ''
    shared_access_key_name = None # type: Optional[str]
    shared_access_key = None # type: Optional[str]
    entity_path = ''
    shared_access_signature = None  # type: Optional[str]
    shared_access_signature_expiry = None # type: Optional[int]
    for element in conn_str.split(';'):
        key, _, value = element.partition('=')
        if key.lower() == 'endpoint':
            endpoint = value.rstrip('/')
        elif key.lower() == 'sharedaccesskeyname':
            shared_access_key_name = value
        elif key.lower() == 'sharedaccesskey':
            shared_access_key = value
        elif key.lower() == 'entitypath':
            entity_path = value
        elif key.lower() == "sharedaccesssignature":
            shared_access_signature = value
            try:
                # Expiry can be stored in the "se=<timestamp>" clause of the token. ('&'-separated key-value pairs)
                # type: ignore
                shared_access_signature_expiry = int(shared_access_signature.split('se=')[1].split('&')[0])
            except (IndexError, TypeError, ValueError): # Fallback since technically expiry is optional.
                # An arbitrary, absurdly large number, since you can't renew.
                shared_access_signature_expiry = int(time.time() * 2)
    if not (all((endpoint, shared_access_key_name, shared_access_key)) or all((endpoint, shared_access_signature))) \
        or all((shared_access_key_name, shared_access_signature)): # this latter clause since we don't accept both
        raise ValueError(
            "Invalid connection string. Should be in the format: "
            "Endpoint=sb://<FQDN>/;SharedAccessKeyName=<KeyName>;SharedAccessKey=<KeyValue>"
            "\nWith alternate option of providing SharedAccessSignature instead of SharedAccessKeyName and Key"
        )
    return (endpoint,
            str(shared_access_key_name) if shared_access_key_name else None,
            str(shared_access_key) if shared_access_key else None,
            entity_path,
            str(shared_access_signature) if shared_access_signature else None,
            shared_access_signature_expiry)


def build_uri(address, entity):
    parsed = urlparse(address)
    if parsed.path:
        return address
    if not entity:
        raise ValueError("No Service Bus entity specified")
    address += "/" + str(entity)
    return address


def create_properties(user_agent=None):
    # type: (Optional[str]) -> Dict[types.AMQPSymbol, str]
    """
    Format the properties with which to instantiate the connection.
    This acts like a user agent over HTTP.

    :param str user_agent: If specified, this will be added in front of the built-in user agent string.

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

    properties[types.AMQPSymbol("user-agent")] = final_user_agent
    return properties


def renewable_start_time(renewable):
    try:
        return renewable._received_timestamp_utc  # pylint: disable=protected-access
    except AttributeError:
        pass
    try:
        return renewable._session_start  # pylint: disable=protected-access
    except AttributeError:
        raise TypeError("Registered object is not renewable.")


def create_authentication(client):
    # pylint: disable=protected-access
    try:
        # ignore mypy's warning because token_type is Optional
        token_type = client._credential.token_type  # type: ignore
    except AttributeError:
        token_type = TOKEN_TYPE_JWT
    if token_type == TOKEN_TYPE_SASTOKEN:
        auth = authentication.JWTTokenAuth(
            client._auth_uri,
            client._auth_uri,
            functools.partial(client._credential.get_token, client._auth_uri),
            token_type=token_type,
            timeout=client._config.auth_timeout,
            http_proxy=client._config.http_proxy,
            transport_type=client._config.transport_type,
        )
        auth.update_token()
        return auth
    return authentication.JWTTokenAuth(
        client._auth_uri,
        client._auth_uri,
        functools.partial(client._credential.get_token, JWT_TOKEN_SCOPE),
        token_type=token_type,
        timeout=client._config.auth_timeout,
        http_proxy=client._config.http_proxy,
        transport_type=client._config.transport_type,
    )


def generate_dead_letter_entity_name(
        queue_name=None,
        topic_name=None,
        subscription_name=None,
        transfer_deadletter=False
):
    entity_name = queue_name if queue_name else (topic_name + "/Subscriptions/" + subscription_name)
    entity_name = "{}{}".format(
        entity_name,
        TRANSFER_DEAD_LETTER_QUEUE_SUFFIX if transfer_deadletter else DEAD_LETTER_QUEUE_SUFFIX
    )

    return entity_name


def transform_messages_to_sendable_if_needed(messages):
    """
    This method is to convert single/multiple received messages to sendable messages to enable message resending.
    """
    # pylint: disable=protected-access
    try:
        msgs_to_return = []
        for each in messages:
            try:
                msgs_to_return.append(each._to_outgoing_message())
            except AttributeError:
                msgs_to_return.append(each)
        return msgs_to_return
    except TypeError:
        try:
            return messages._to_outgoing_message()
        except AttributeError:
            return messages
