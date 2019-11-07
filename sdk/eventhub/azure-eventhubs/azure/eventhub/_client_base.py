# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
import sys
import platform
import datetime
import uuid
import time
import functools
import threading
from typing import Union, Any, TYPE_CHECKING

import uamqp  # type: ignore
from uamqp import Message  # type: ignore
from uamqp import authentication  # type: ignore
from uamqp import constants  # type: ignore

from uamqp import types  # type: ignore
from azure.eventhub import __version__
from .configuration import Configuration
from .common import EventHubSharedKeyCredential, EventHubSASTokenCredential, _Address, parse_sas_token
from .error import _handle_exception
from ._connection_manager import get_connection_manager

try:
    from urlparse import urlparse  # type: ignore
    from urllib import urlencode, quote_plus  # type: ignore
except ImportError:
    from urllib.parse import urlparse, urlencode, quote_plus

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)
MAX_USER_AGENT_LENGTH = 512


def _parse_conn_str(conn_str):
    endpoint = None
    shared_access_key_name = None
    shared_access_key = None
    entity_path = None
    for element in conn_str.split(';'):
        key, _, value = element.partition('=')
        if key.lower() == 'endpoint':
            endpoint = value.rstrip('/')
        elif key.lower() == 'hostname':
            endpoint = value.rstrip('/')
        elif key.lower() == 'sharedaccesskeyname':
            shared_access_key_name = value
        elif key.lower() == 'sharedaccesskey':
            shared_access_key = value
        elif key.lower() == 'entitypath':
            entity_path = value
    if not all([endpoint, shared_access_key_name, shared_access_key]):
        raise ValueError("Invalid connection string")
    return endpoint, shared_access_key_name, shared_access_key, entity_path


def _generate_sas_token(uri, policy, key, expiry=None):
    """Create a shared access signiture token as a string literal.
    :returns: SAS token as string literal.
    :rtype: str
    """
    from base64 import b64encode, b64decode
    from hashlib import sha256
    from hmac import HMAC
    if not expiry:
        expiry = time.time() + 3600  # Default to 1 hour.
    encoded_uri = quote_plus(uri)
    ttl = int(expiry)
    sign_key = '%s\n%d' % (encoded_uri, ttl)
    signature = b64encode(HMAC(b64decode(key), sign_key.encode('utf-8'), sha256).digest())
    result = {
        'sr': uri,
        'sig': signature,
        'se': str(ttl)}
    if policy:
        result['skn'] = policy
    return 'SharedAccessSignature ' + urlencode(result)


def _build_uri(address, entity):
    parsed = urlparse(address)
    if parsed.path:
        return address
    if not entity:
        raise ValueError("No EventHub specified")
    address += "/" + str(entity)
    return address


class ClientBase(object):
    def __init__(self, host, event_hub_path, credential, **kwargs):
        self.eh_name = event_hub_path
        self._host = host
        self._container_id = "eventhub.pysdk-" + str(uuid.uuid4())[:8]
        self._address = _Address()
        self._address.hostname = host
        self._address.path = "/" + event_hub_path if event_hub_path else ""
        self._credential = credential
        self._keep_alive = kwargs.get("keep_alive", 30)
        self._auto_reconnect = kwargs.get("auto_reconnect", True)
        self._mgmt_target = "amqps://{}/{}".format(self._host, self.eh_name)
        self._auth_uri = "sb://{}{}".format(self._address.hostname, self._address.path)
        self._config = Configuration(**kwargs)
        self._debug = self._config.network_tracing
        self._conn_manager = get_connection_manager(**kwargs)
        self._lock = threading.RLock()
        log.info("%r: Created the Event Hub client", self._container_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _create_auth(self):
        """
        Create an ~uamqp.authentication.SASTokenAuth instance to authenticate
        the session.
        """
        http_proxy = self._config.http_proxy
        transport_type = self._config.transport_type
        auth_timeout = self._config.auth_timeout

        # TODO: the following code can be refactored to create auth from classes directly instead of using if-else
        if isinstance(self._credential, EventHubSharedKeyCredential):  # pylint:disable=no-else-return
            username = self._credential.policy
            password = self._credential.key
            if "@sas.root" in username:
                return authentication.SASLPlain(
                    self._host, username, password, http_proxy=http_proxy, transport_type=transport_type)
            return authentication.SASTokenAuth.from_shared_access_key(
                self._auth_uri, username, password, timeout=auth_timeout, http_proxy=http_proxy,
                transport_type=transport_type)

        elif isinstance(self._credential, EventHubSASTokenCredential):
            token = self._credential.get_sas_token()
            try:
                expiry = int(parse_sas_token(token)['se'])
            except (KeyError, TypeError, IndexError):
                raise ValueError("Supplied SAS token has no valid expiry value.")
            return authentication.SASTokenAuth(
                self._auth_uri, self._auth_uri, token,
                expires_at=expiry,
                timeout=auth_timeout,
                http_proxy=http_proxy,
                transport_type=transport_type)

        else:  # Azure credential
            get_jwt_token = functools.partial(self._credential.get_token,
                                              'https://eventhubs.azure.net//.default')
            return authentication.JWTTokenAuth(self._auth_uri, self._auth_uri,
                                               get_jwt_token, http_proxy=http_proxy,
                                               transport_type=transport_type)

    @classmethod
    def _create_properties(cls, user_agent=None):  # pylint: disable=no-self-use
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

    def _close_connection(self):
        self._conn_manager.reset_connection_if_broken()

    def _try_delay(self, retried_times, last_exception, timeout_time=None, entity_name=None):
        entity_name = entity_name or self._container_id
        backoff = self._config.backoff_factor * 2 ** retried_times
        if backoff <= self._config.backoff_max and (
                timeout_time is None or time.time() + backoff <= timeout_time):  # pylint:disable=no-else-return
            time.sleep(backoff)
            log.info("%r has an exception (%r). Retrying...", format(entity_name), last_exception)
        else:
            log.info("%r operation has timed out. Last exception before timeout is (%r)",
                     entity_name, last_exception)
            raise last_exception

    def _management_request(self, mgmt_msg, op_type):
        retried_times = 0
        last_exception = None
        while retried_times <= self._config.max_retries:
            mgmt_auth = self._create_auth()
            mgmt_client = uamqp.AMQPClient(self._mgmt_target)
            try:
                conn = self._conn_manager.get_connection(self._host, mgmt_auth)  #pylint:disable=assignment-from-none
                mgmt_client.open(connection=conn)
                response = mgmt_client.mgmt_request(
                    mgmt_msg,
                    constants.READ_OPERATION,
                    op_type=op_type,
                    status_code_field=b'status-code',
                    description_fields=b'status-description')
                return response
            except Exception as exception:  # pylint: disable=broad-except
                last_exception = _handle_exception(exception, self)
                self._try_delay(retried_times=retried_times, last_exception=last_exception)
                retried_times += 1
            finally:
                mgmt_client.close()
        log.info("%r returns an exception %r", self._container_id, last_exception)  # pylint:disable=specify-parameter-names-in-call
        raise last_exception

    def _add_span_request_attributes(self, span):
        span.add_attribute("component", "eventhubs")
        span.add_attribute("message_bus.destination", self._address.path)
        span.add_attribute("peer.address", self._address.hostname)

    @classmethod
    def from_connection_string(cls, conn_str, **kwargs):
        event_hub_path = kwargs.pop("event_hub_path", None)
        address, policy, key, entity = _parse_conn_str(conn_str)
        entity = event_hub_path or entity
        left_slash_pos = address.find("//")
        if left_slash_pos != -1:
            host = address[left_slash_pos + 2:]
        else:
            host = address
        return cls(host, entity, EventHubSharedKeyCredential(policy, key), **kwargs)

    def get_properties(self):
        # type:() -> Dict[str, Any]
        """
        Get properties of the specified EventHub async.
        Keys in the details dictionary include:

            - path
            - created_at
            - partition_ids

        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        mgmt_msg = Message(application_properties={'name': self.eh_name})
        response = self._management_request(mgmt_msg, op_type=b'com.microsoft:eventhub')
        output = {}
        eh_info = response.get_data()
        if eh_info:
            output['path'] = eh_info[b'name'].decode('utf-8')
            output['created_at'] = datetime.datetime.utcfromtimestamp(float(eh_info[b'created_at']) / 1000)
            output['partition_ids'] = [p.decode('utf-8') for p in eh_info[b'partition_ids']]
        return output

    def get_partition_ids(self):
        # type:() -> List[str]
        """
        Get partition ids of the specified EventHub.

        :rtype: list[str]
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        return self.get_properties()['partition_ids']

    def get_partition_properties(self, partition):
        # type:(str) -> Dict[str, Any]
        """
        Get properties of the specified partition async.
        Keys in the details dictionary include:

            - event_hub_path
            - id
            - beginning_sequence_number
            - last_enqueued_sequence_number
            - last_enqueued_offset
            - last_enqueued_time_utc
            - is_empty

        :param partition: The target partition id.
        :type partition: str
        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        mgmt_msg = Message(application_properties={'name': self.eh_name,
                                                   'partition': partition})
        response = self._management_request(mgmt_msg, op_type=b'com.microsoft:partition')
        partition_info = response.get_data()
        output = {}
        if partition_info:
            output['event_hub_path'] = partition_info[b'name'].decode('utf-8')
            output['id'] = partition_info[b'partition'].decode('utf-8')
            output['beginning_sequence_number'] = partition_info[b'begin_sequence_number']
            output['last_enqueued_sequence_number'] = partition_info[b'last_enqueued_sequence_number']
            output['last_enqueued_offset'] = partition_info[b'last_enqueued_offset'].decode('utf-8')
            output['last_enqueued_time_utc'] = datetime.datetime.utcfromtimestamp(
                float(partition_info[b'last_enqueued_time_utc'] / 1000))
            output['is_empty'] = partition_info[b'is_partition_empty']
        return output

    def close(self):
        # type:() -> None
        self._conn_manager.close_connection()
