# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
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


from azure.eventhub import __version__
from azure.eventhub.configuration import Configuration
from azure.eventhub import constants
from .common import SASTokenCredentials, SharedKeyCredentials, Address

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

    def __init__(self, host, event_hub_path, credentials, **kwargs):
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
        self.address = Address()
        self.address.hostname = host
        self.address.path = "/" + event_hub_path if event_hub_path else ""
        self._auth_config = {}
        self.credentials = credentials
        if isinstance(credentials, SASTokenCredentials):
            self.sas_token = credentials.token
        elif isinstance(credentials, SharedKeyCredentials):
            self.username = credentials.policy
            self.password = credentials.key
            self._auth_config['username'] = self.username
            self._auth_config['password'] = self.password
        else:
            self.aad_credential = credentials

        self.host = host
        #self.eh_name = self.address.path.lstrip('/')
        self.eh_name = event_hub_path
        # self.http_proxy = kwargs.get("http_proxy")
        self.keep_alive = kwargs.get("keep_alive", 30)
        self.auto_reconnect = kwargs.get("auto_reconnect", True)
        # self.mgmt_target = "amqps://{}/{}".format(self.address.hostname, self.eh_name)
        self.mgmt_target = "amqps://{}/{}".format(self.host, self.eh_name)
        # url_username = unquote_plus(self.address.username) if self.address.username else None
        # username = username or url_username
        # url_password = unquote_plus(self.address.password) if self.address.password else None
        # password = password or url_password
        self.auth_uri = "sb://{}{}".format(self.address.hostname, self.address.path)
        self.get_auth = functools.partial(self._create_auth)
        self.config = Configuration(**kwargs)
        self.debug = self.config.network_tracing

        log.info("%r: Created the Event Hub client", self.container_id)

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
        left_slash_pos = address.find("//")
        if left_slash_pos != -1:
            host = address[left_slash_pos + 2:]
        else:
            host = address
        return cls(host, entity, SharedKeyCredentials(policy, key), **kwargs)

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
        left_slash_pos = address.find("//")
        if left_slash_pos != -1:
            host = address[left_slash_pos + 2:]
        else:
            host = address
        client = cls(host, "", SharedKeyCredentials(username, password), **kwargs)
        client._auth_config = {  # pylint: disable=protected-access
            'iot_username': policy,
            'iot_password': key,
            'username': username,
            'password': password}
        return client

    @abstractmethod
    def _create_auth(self, username=None, password=None):
        pass

    def create_properties(self, user_agent=None):  # pylint: disable=no-self-use
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

        final_user_agent = 'azsdk-python-eventhub/{} ({}; {})'.format(
            __version__, properties["framework"], sys.platform)
        if user_agent:
            final_user_agent = '{}, {}'.format(final_user_agent, user_agent)

        if len(final_user_agent) > constants.MAX_USER_AGENT_LENGTH:
            raise ValueError("The user-agent string cannot be more than {} in length."
                             "Current user_agent string is: {} with length: {}".format(
                                constants.MAX_USER_AGENT_LENGTH, final_user_agent, len(final_user_agent)))

        properties["user-agent"] = final_user_agent
        return properties

    def _process_redirect_uri(self, redirect):
        redirect_uri = redirect.address.decode('utf-8')
        auth_uri, _, _ = redirect_uri.partition("/ConsumerGroups")
        self.address = urlparse(auth_uri)
        self.host = self.address.hostname
        self.auth_uri = "sb://{}{}".format(self.address.hostname, self.address.path)
        self.eh_name = self.address.path.lstrip('/')
        self.mgmt_target = redirect_uri

    @abstractmethod
    def create_receiver(
            self, consumer_group, partition, epoch=None, offset=None, prefetch=300,
            operation=None):
        pass

    @abstractmethod
    def create_sender(self, partition=None, operation=None, send_timeout=60):
        pass
