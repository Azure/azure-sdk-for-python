# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
import uuid
import time
import functools
import collections
from base64 import b64encode, b64decode
from hashlib import sha256
from hmac import HMAC
from typing import Any, TYPE_CHECKING
try:
    from urlparse import urlparse  # type: ignore
    from urllib import urlencode, quote_plus  # type: ignore
except ImportError:
    from urllib.parse import urlparse, urlencode, quote_plus

from uamqp import (
    AMQPClient,
    Message,
    authentication,
    constants,
    errors,
    compat
)

from .exceptions import _handle_exception, ClientClosedError
from ._configuration import Configuration
from ._utils import parse_sas_token, utc_from_timestamp
from ._common import EventHubSharedKeyCredential, EventHubSASTokenCredential
from ._connection_manager import get_connection_manager
from ._constants import (
    CONTAINER_PREFIX,
    JWT_TOKEN_SCOPE,
    MGMT_OPERATION,
    MGMT_PARTITION_OPERATION
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

_LOGGER = logging.getLogger(__name__)


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
        raise ValueError(
            "Invalid connection string. Should be in the format: "
            "Endpoint=sb://<FQDN>/;SharedAccessKeyName=<KeyName>;SharedAccessKey=<KeyValue>")
    return endpoint, shared_access_key_name, shared_access_key, entity_path


def _generate_sas_token(uri, policy, key, expiry=None):
    """Create a shared access signiture token as a string literal.
    :returns: SAS token as string literal.
    :rtype: str
    """
    if not expiry:
        expiry = time.time() + 3600  # Default to 1 hour.
    encoded_uri = quote_plus(uri)
    ttl = int(expiry)
    sign_key = '{}\n{}'.format(encoded_uri, ttl)
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


_Address = collections.namedtuple('Address', 'hostname path')


class ClientBase(object):  # pylint:disable=too-many-instance-attributes
    def __init__(self, fully_qualified_namespace, eventhub_name, credential, **kwargs):
        self.eventhub_name = eventhub_name
        path = "/" + eventhub_name if eventhub_name else ""
        self._address = _Address(hostname=fully_qualified_namespace, path=path)
        self._container_id = CONTAINER_PREFIX + str(uuid.uuid4())[:8]
        self._credential = credential
        self._keep_alive = kwargs.get("keep_alive", 30)
        self._auto_reconnect = kwargs.get("auto_reconnect", True)
        self._mgmt_target = "amqps://{}/{}".format(self._address.hostname, self.eventhub_name)
        self._auth_uri = "sb://{}{}".format(self._address.hostname, self._address.path)
        self._config = Configuration(**kwargs)
        self._debug = self._config.network_tracing
        self._conn_manager = get_connection_manager(**kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @classmethod
    def from_connection_string(cls, conn_str, **kwargs):
        eventhub_name = kwargs.pop("eventhub_name", None)
        address, policy, key, entity = _parse_conn_str(conn_str)
        entity = eventhub_name or entity
        left_slash_pos = address.find("//")
        if left_slash_pos != -1:
            host = address[left_slash_pos + 2:]
        else:
            host = address
        return cls(host, entity, EventHubSharedKeyCredential(policy, key), **kwargs)

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
                    self._address.hostname, username, password, http_proxy=http_proxy, transport_type=transport_type)
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
            get_jwt_token = functools.partial(self._credential.get_token, JWT_TOKEN_SCOPE)
            return authentication.JWTTokenAuth(self._auth_uri, self._auth_uri,
                                               get_jwt_token, http_proxy=http_proxy,
                                               transport_type=transport_type)

    def _close_connection(self):
        self._conn_manager.reset_connection_if_broken()

    def _backoff(self, retried_times, last_exception, timeout_time=None, entity_name=None):
        entity_name = entity_name or self._container_id
        backoff = self._config.backoff_factor * 2 ** retried_times
        if backoff <= self._config.backoff_max and (
                timeout_time is None or time.time() + backoff <= timeout_time):  # pylint:disable=no-else-return
            time.sleep(backoff)
            _LOGGER.info("%r has an exception (%r). Retrying...", format(entity_name), last_exception)
        else:
            _LOGGER.info("%r operation has timed out. Last exception before timeout is (%r)",
                     entity_name, last_exception)
            raise last_exception

    def _management_request(self, mgmt_msg, op_type):
        retried_times = 0
        last_exception = None
        while retried_times <= self._config.max_retries:
            mgmt_auth = self._create_auth()
            mgmt_client = AMQPClient(self._mgmt_target)
            try:
                conn = self._conn_manager.get_connection(self._address.hostname, mgmt_auth)  #pylint:disable=assignment-from-none
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
                self._backoff(retried_times=retried_times, last_exception=last_exception)
                retried_times += 1
                if retried_times > self._config.max_retries:
                    _LOGGER.info("%r returns an exception %r", self._container_id, last_exception)
                    raise last_exception
            finally:
                mgmt_client.close()

    def _add_span_request_attributes(self, span):
        span.add_attribute("component", "eventhubs")
        span.add_attribute("message_bus.destination", self._address.path)
        span.add_attribute("peer.address", self._address.hostname)

    def get_properties(self):
        # type:() -> Dict[str, Any]
        """Get properties of the EventHub.

        Keys in the returned dictionary include:

            - path
            - created_at
            - partition_ids

        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        mgmt_msg = Message(application_properties={'name': self.eventhub_name})
        response = self._management_request(mgmt_msg, op_type=MGMT_OPERATION)
        output = {}
        eh_info = response.get_data()
        if eh_info:
            output['path'] = eh_info[b'name'].decode('utf-8')
            output['created_at'] = utc_from_timestamp(float(eh_info[b'created_at']) / 1000)
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

    def get_partition_properties(self, partition_id):
        # type:(str) -> Dict[str, Any]
        """Get properties of the specified partition.

        Keys in the details dictionary include:

            - eventhub_name
            - id
            - beginning_sequence_number
            - last_enqueued_sequence_number
            - last_enqueued_offset
            - last_enqueued_time_utc
            - is_empty

        :param partition_id: The target partition id.
        :type partition_id: str
        :rtype: dict
        :raises: :class:`EventHubError<azure.eventhub.EventHubError>`
        """
        mgmt_msg = Message(application_properties={'name': self.eventhub_name,
                                                   'partition': partition_id})
        response = self._management_request(mgmt_msg, op_type=MGMT_PARTITION_OPERATION)
        partition_info = response.get_data()
        output = {}
        if partition_info:
            output['eventhub_name'] = partition_info[b'name'].decode('utf-8')
            output['id'] = partition_info[b'partition'].decode('utf-8')
            output['beginning_sequence_number'] = partition_info[b'begin_sequence_number']
            output['last_enqueued_sequence_number'] = partition_info[b'last_enqueued_sequence_number']
            output['last_enqueued_offset'] = partition_info[b'last_enqueued_offset'].decode('utf-8')
            output['is_empty'] = partition_info[b'is_partition_empty']
            output['last_enqueued_time_utc'] = utc_from_timestamp(
                float(partition_info[b'last_enqueued_time_utc'] / 1000)
            )
        return output

    def close(self):
        # type:() -> None
        self._conn_manager.close_connection()


class ConsumerProducerMixin(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _check_closed(self):
        if self.closed:
            raise ClientClosedError(
                "{} has been closed. Please create a new one to handle event data.".format(self._name)
            )

    def _open(self):
        """Open the EventHubConsumer/EventHubProducer using the supplied connection.

        """
        # pylint: disable=protected-access
        if not self.running:
            if self._handler:
                self._handler.close()
            self._create_handler()
            self._handler.open(connection=self._client._conn_manager.get_connection(  # pylint: disable=protected-access
                self._client._address.hostname,
                self._client._create_auth()
            ))
            while not self._handler.client_ready():
                time.sleep(0.05)
            self._max_message_size_on_link = self._handler.message_handler._link.peer_max_message_size \
                                             or constants.MAX_MESSAGE_LENGTH_BYTES  # pylint: disable=protected-access
            self.running = True

    def _close_handler(self):
        if self._handler:
            self._handler.close()  # close the link (sharing connection) or connection (not sharing)
        self.running = False

    def _close_connection(self):
        self._close_handler()
        self._client._conn_manager.reset_connection_if_broken()  # pylint: disable=protected-access

    def _handle_exception(self, exception):
        if not self.running and isinstance(exception, compat.TimeoutException):
            exception = errors.AuthenticationException("Authorization timeout.")
        return _handle_exception(exception, self)

    def _do_retryable_operation(self, operation, timeout=None, **kwargs):
        # pylint:disable=protected-access
        timeout_time = (time.time() + timeout) if timeout else None
        retried_times = 0
        last_exception = kwargs.pop('last_exception', None)
        operation_need_param = kwargs.pop('operation_need_param', True)
        max_retries = self._client._config.max_retries  # pylint:disable=protected-access

        while retried_times <= max_retries:
            try:
                if operation_need_param:
                    return operation(timeout_time=timeout_time, last_exception=last_exception, **kwargs)
                return operation()
            except Exception as exception:  # pylint:disable=broad-except
                last_exception = self._handle_exception(exception)
                self._client._backoff(
                    retried_times=retried_times,
                    last_exception=last_exception,
                    timeout_time=timeout_time,
                    entity_name=self._name
                )
                retried_times += 1
                if retried_times > max_retries:
                    _LOGGER.info("%r operation has exhausted retry. Last exception: %r.", self._name, last_exception)
                    raise last_exception

    def close(self):
        # type:() -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        self._close_handler()
        self.closed = True
