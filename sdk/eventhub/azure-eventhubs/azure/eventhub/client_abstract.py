# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
import datetime
import sys
import uuid
import time
import functools
from abc import abstractmethod
try:
    from urlparse import urlparse
    from urllib import unquote_plus, urlencode, quote_plus
except ImportError:
    from urllib.parse import urlparse, unquote_plus, urlencode, quote_plus

import uamqp
from uamqp import Message
from uamqp import authentication
from uamqp import constants

from azure.eventhub import __version__
from azure.eventhub.sender import Sender
from azure.eventhub.receiver import Receiver
from azure.eventhub.common import EventHubError, parse_sas_token
from azure.eventhub.configuration import Configuration

log = logging.getLogger(__name__)


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


class EventHubClientAbstract(object):
    """
    The EventHubClient class defines a high level interface for sending
    events to and receiving events from the Azure Event Hubs service.

    Example:
        .. literalinclude:: ../examples/test_examples_eventhub.py
            :start-after: [START create_eventhub_client]
            :end-before: [END create_eventhub_client]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the Event Hub client

    """

    def __init__(
            self, address, username=None, password=None, sas_token=None, aad_credential=None, **kwargs):
        """
        Constructs a new EventHubClient with the given address URL.

        :param address: The full URI string of the Event Hub. This can optionally
         include URL-encoded access name and key.
        :type address: str
        :param username: The name of the shared access policy. This must be supplied
         if not encoded into the address.
        :type username: str
        :param password: The shared access key. This must be supplied if not encoded
         into the address.
        :type password: str
        :param debug: Whether to output network trace logs to the logger. Default
         is `False`.
        :type debug: bool
        :param http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: 'proxy_hostname' (str value) and 'proxy_port' (int value).
         Additionally the following keys may also be present: 'username', 'password'.
        :type http_proxy: dict[str, Any]
        :param auth_timeout: The time in seconds to wait for a token to be authorized by the service.
         The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
        :type auth_timeout: int
        :param sas_token: A SAS token or function that returns a SAS token. If a function is supplied,
         it will be used to retrieve subsequent tokens in the case of token expiry. The function should
         take no arguments.
        :type sas_token: str or callable
        """
        self.container_id = "eventhub.pysdk-" + str(uuid.uuid4())[:8]
        self.sas_token = sas_token
        self.address = urlparse(address)
        self.aad_credential = aad_credential
        self.eh_name = self.address.path.lstrip('/')
        # self.http_proxy = kwargs.get("http_proxy")
        self.keep_alive = kwargs.get("keep_alive", 30)
        self.auto_reconnect = kwargs.get("auto_reconnect", True)
        self.mgmt_target = "amqps://{}/{}".format(self.address.hostname, self.eh_name)
        url_username = unquote_plus(self.address.username) if self.address.username else None
        username = username or url_username
        url_password = unquote_plus(self.address.password) if self.address.password else None
        password = password or url_password
        if (not username or not password) and not sas_token and not aad_credential:
            raise ValueError("Please supply any of username and password, or a SAS token, or an AAD credential")
        self.auth_uri = "sb://{}{}".format(self.address.hostname, self.address.path)
        self._auth_config = {'username': username, 'password': password}
        self.get_auth = functools.partial(self._create_auth)
        # self.debug = kwargs.get("debug", False)  # debug
        #self.auth_timeout = auth_timeout

        self.stopped = False
        self.config = Configuration(**kwargs)
        self.debug = self.config.network_tracing

        log.info("%r: Created the Event Hub client", self.container_id)

    @classmethod
    def from_sas_token(cls, address, sas_token, eventhub=None, **kwargs):
        """Create an EventHubClient from an existing auth token or token generator.

        :param address: The Event Hub address URL
        :type address: str
        :param sas_token: A SAS token or function that returns a SAS token. If a function is supplied,
         it will be used to retrieve subsequent tokens in the case of token expiry. The function should
         take no arguments.
        :type sas_token: str or callable
        :param eventhub: The name of the EventHub, if not already included in the address URL.
        :type eventhub: str
        :param debug: Whether to output network trace logs to the logger. Default
         is `False`.
        :type debug: bool
        :param http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: 'proxy_hostname' (str value) and 'proxy_port' (int value).
         Additionally the following keys may also be present: 'username', 'password'.
        :type http_proxy: dict[str, Any]
        :param auth_timeout: The time in seconds to wait for a token to be authorized by the service.
         The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
        :type auth_timeout: int

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START create_eventhub_client_sas_token]
                :end-before: [END create_eventhub_client_sas_token]
                :language: python
                :dedent: 4
                :caption: Create an EventHubClient from an existing auth token or token generator.

        """
        address = _build_uri(address, eventhub)
        return cls(address, sas_token=sas_token, **kwargs)

    @classmethod
    def from_connection_string(cls, conn_str, eventhub=None, **kwargs):
        """Create an EventHubClient from a connection string.

        :param conn_str: The connection string.
        :type conn_str: str
        :param eventhub: The name of the EventHub, if the EntityName is
         not included in the connection string.
        :type eventhub: str
        :param debug: Whether to output network trace logs to the logger. Default
         is `False`.
        :type debug: bool
        :param http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: 'proxy_hostname' (str value) and 'proxy_port' (int value).
         Additionally the following keys may also be present: 'username', 'password'.
        :type http_proxy: dict[str, Any]
        :param auth_timeout: The time in seconds to wait for a token to be authorized by the service.
         The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
        :type auth_timeout: int

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START create_eventhub_client_connstr]
                :end-before: [END create_eventhub_client_connstr]
                :language: python
                :dedent: 4
                :caption: Create an EventHubClient from a connection string.

        """
        address, policy, key, entity = _parse_conn_str(conn_str)
        entity = eventhub or entity
        address = _build_uri(address, entity)
        return cls(address, username=policy, password=key, **kwargs)

    @classmethod
    def from_iothub_connection_string(cls, conn_str, **kwargs):
        """
        Create an EventHubClient from an IoTHub connection string.

        :param conn_str: The connection string.
        :type conn_str: str
        :param debug: Whether to output network trace logs to the logger. Default
         is `False`.
        :type debug: bool
        :param http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: 'proxy_hostname' (str value) and 'proxy_port' (int value).
         Additionally the following keys may also be present: 'username', 'password'.
        :type http_proxy: dict[str, Any]
        :param auth_timeout: The time in seconds to wait for a token to be authorized by the service.
         The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
        :type auth_timeout: int

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START create_eventhub_client_iot_connstr]
                :end-before: [END create_eventhub_client_iot_connstr]
                :language: python
                :dedent: 4
                :caption: Create an EventHubClient from an IoTHub connection string.

        """
        address, policy, key, _ = _parse_conn_str(conn_str)
        hub_name = address.split('.')[0]
        username = "{}@sas.root.{}".format(policy, hub_name)
        password = _generate_sas_token(address, policy, key)
        client = cls("amqps://" + address, username=username, password=password, **kwargs)
        client._auth_config = {  # pylint: disable=protected-access
            'iot_username': policy,
            'iot_password': key,
            'username': username,
            'password': password}
        return client

    @classmethod
    def from_azure_identity(cls, address, aad_credential, eventhub=None, **kwargs):
        address = _build_uri(address, eventhub)
        return cls(address, aad_credential=aad_credential, **kwargs)

    @abstractmethod
    def _create_auth(self, username=None, password=None):
        pass

    def create_properties(self):  # pylint: disable=no-self-use
        """
        Format the properties with which to instantiate the connection.
        This acts like a user agent over HTTP.

        :rtype: dict
        """
        properties = {}
        properties["product"] = "eventhub.python"
        properties["version"] = __version__
        properties["framework"] = "Python {}.{}.{}".format(*sys.version_info[0:3])
        properties["platform"] = sys.platform
        return properties

    def _process_redirect_uri(self, redirect):
        redirect_uri = redirect.address.decode('utf-8')
        auth_uri, _, _ = redirect_uri.partition("/ConsumerGroups")
        self.address = urlparse(auth_uri)
        self.auth_uri = "sb://{}{}".format(self.address.hostname, self.address.path)
        self.eh_name = self.address.path.lstrip('/')
        self.mgmt_target = redirect_uri

    @abstractmethod
    def get_eventhub_information(self):
        pass

    @abstractmethod
    def create_receiver(
            self, consumer_group, partition, epoch=None, offset=None, prefetch=300,
            operation=None):
        pass

    @abstractmethod
    def create_sender(self, partition=None, operation=None, send_timeout=60):
        pass
