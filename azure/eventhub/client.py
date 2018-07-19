# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import datetime
import sys
import uuid
import time
try:
    from urllib import urlparse, unquote_plus, urlencode, quote_plus
except ImportError:
    from urllib.parse import urlparse, unquote_plus, urlencode, quote_plus

import uamqp
from uamqp import Connection
from uamqp import Message
from uamqp import Source
from uamqp import authentication
from uamqp import constants

from azure.eventhub import __version__
from azure.eventhub.sender import Sender
from azure.eventhub.receiver import Receiver
from azure.eventhub.common import EventHubError

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


class EventHubClient(object):
    """
    The EventHubClient class defines a high level interface for sending
    events to and receiving events from the Azure Event Hubs service.
    """

    def __init__(self, address, username=None, password=None, debug=False):
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
        """
        self.container_id = "eventhub.pysdk-" + str(uuid.uuid4())[:8]
        self.address = urlparse(address)
        self.mgmt_node = b"$management"
        url_username = unquote_plus(self.address.username) if self.address.username else None
        username = username or url_username
        url_password = unquote_plus(self.address.password) if self.address.password else None
        password = password or url_password
        if not username or not password:
            raise ValueError("Missing username and/or password.")
        auth_uri = "sb://{}{}".format(self.address.hostname, self.address.path)
        self.auth = self._create_auth(auth_uri, username, password)
        self._auth_config = None
        self.connection = None
        self.debug = debug

        self.clients = []
        self.stopped = False
        log.info("{}: Created the Event Hub client".format(self.container_id))

    @classmethod
    def from_connection_string(cls, conn_str, eventhub=None, **kwargs):
        """
        Create an EventHubClient from a connection string.

        :param conn_str: The connection string.
        :type conn_str: str
        :param eventhub: The name of the EventHub, if the EntityName is
         not included in the connection string.
        """
        address, policy, key, entity = _parse_conn_str(conn_str)
        entity = eventhub or entity
        address = _build_uri(address, entity)
        return cls(address, username=policy, password=key, **kwargs)

    @classmethod
    def from_iothub_connection_string(cls, conn_str, **kwargs):
        address, policy, key, _ = _parse_conn_str(conn_str)
        hub_name = address.split('.')[0]
        username = "{}@sas.root.{}".format(policy, hub_name)
        password = _generate_sas_token(address, policy, key)
        client = cls("amqps://" + address, username=username, password=password, **kwargs)
        client._auth_config = {'username': policy, 'password': key}  # pylint: disable=protected-access
        client.mgmt_node = ("amqps://" + address + ":5671/pyot/$management").encode('UTF-8')
        return client

    def _create_auth(self, auth_uri, username, password):  # pylint: disable=no-self-use
        """
        Create an ~uamqp.authentication.SASTokenAuth instance to authenticate
        the session.

        :param auth_uri: The URI to authenticate against.
        :type auth_uri: str
        :param username: The name of the shared access policy.
        :type username: str
        :param password: The shared access key.
        :type password: str
        """
        if "@sas.root" in username:
            return authentication.SASLPlain(self.address.hostname, username, password)
        return authentication.SASTokenAuth.from_shared_access_key(auth_uri, username, password, timeout=60)

    def _create_properties(self):  # pylint: disable=no-self-use
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

    def _create_connection(self):
        """
        Create a new ~uamqp.connection.Connection instance that will be shared between all
        Sender/Receiver clients.
        """
        if not self.connection:
            log.info("{}: Creating connection with address={}".format(
                self.container_id, self.address.geturl()))
            self.connection = Connection(
                self.address.hostname,
                self.auth,
                container_id=self.container_id,
                properties=self._create_properties(),
                debug=self.debug)

    def _close_connection(self):
        """
        Close and destroy the connection.
        """
        if self.connection:
            self.connection.destroy()
            self.connection = None

    def _close_clients(self):
        """
        Close all open Sender/Receiver clients.
        """
        for client in self.clients:
            client.close()

    def _start_clients(self):
        for client in self.clients:
            try:
                client.open(self.connection)
                while not client.has_started():
                    self.connection.work()
            except Exception as exp:  # pylint: disable=broad-except
                client.close(exception=exp)

    def _handle_redirect(self, redirects):
        if len(redirects) != len(self.clients):
            raise EventHubError("Some clients are attempting to redirect the connection.")
        if not all(r.hostname == redirects[0].hostname for r in redirects):
            raise EventHubError("Multiple clients attempting to redirect to different hosts.")
        self.auth = self._create_auth(redirects[0].address.decode('utf-8'), **self._auth_config)
        self.connection.redirect(redirects[0], self.auth)
        for client in self.clients:
            client.open(self.connection)

    def run(self):
        """
        Run the EventHubClient in blocking mode.
        Opens the connection and starts running all Sender/Receiver clients.
        Returns a list of the start up results. For a succcesful client start the
        result will be `None`, otherwise the exception raised.
        If all clients failed to start, then run will fail, shut down the connection
        and raise an exception.
        If at least one client starts up successfully the run command will succeed.

        :rtype: list[~azure.eventhub.common.EventHubError]
        """
        log.info("{}: Starting {} clients".format(self.container_id, len(self.clients)))
        self._create_connection()
        try:
            self._start_clients()
            redirects = [c.redirected for c in self.clients if c.redirected]
            failed = [c.error for c in self.clients if c.error]
            if failed and len(failed) == len(self.clients):
                log.warning("{}: All clients failed to start.".format(self.container_id))
                raise failed[0]
            elif failed:
                log.warning("{}: {} clients failed to start.".format(self.container_id, len(failed)))
            elif redirects:
                self._handle_redirect(redirects)
        except EventHubError:
            self.stop()
            raise
        except Exception as e:
            self.stop()
            raise EventHubError(str(e))
        return failed

    def stop(self):
        """
        Stop the EventHubClient and all its Sender/Receiver clients.
        """
        log.info("{}: Stopping {} clients".format(self.container_id, len(self.clients)))
        self.stopped = True
        self._close_clients()
        self._close_connection()

    def get_eventhub_info(self):
        """
        Get details on the specified EventHub.
        Keys in the details dictionary include:
         -'name'
         -'type'
         -'created_at'
         -'partition_count'
         -'partition_ids'

        :rtype: dict
        """
        self._create_connection()
        eh_name = self.address.path.lstrip('/')
        target = "amqps://{}/{}".format(self.address.hostname, eh_name)
        mgmt_client = uamqp.AMQPClient(target, auth=self.auth, debug=self.debug)
        mgmt_client.open(self.connection)
        try:
            mgmt_msg = Message(application_properties={'name': eh_name})
            response = mgmt_client.mgmt_request(
                mgmt_msg,
                constants.READ_OPERATION,
                op_type=b'com.microsoft:eventhub',
                status_code_field=b'status-code',
                description_fields=b'status-description')
            eh_info = response.get_data()
            output = {}
            if eh_info:
                output['name'] = eh_info[b'name'].decode('utf-8')
                output['type'] = eh_info[b'type'].decode('utf-8')
                output['created_at'] = datetime.datetime.fromtimestamp(float(eh_info[b'created_at'])/1000)
                output['partition_count'] = eh_info[b'partition_count']
                output['partition_ids'] = [p.decode('utf-8') for p in eh_info[b'partition_ids']]
            return output
        except:
            raise
        finally:
            mgmt_client.close()

    def add_receiver(self, consumer_group, partition, offset=None, prefetch=300, operation=None):
        """
        Add a receiver to the client for a particular consumer group and partition.

        :param consumer_group: The name of the consumer group.
        :type consumer_group: str
        :param partition: The ID of the partition.
        :type partition: str
        :param offset: The offset from which to start receiving.
        :type offset: ~azure.eventhub.common.Offset
        :param prefetch: The message prefetch count of the receiver. Default is 300.
        :type prefetch: int
        :operation: An optional operation to be appended to the hostname in the source URL.
         The value must start with `/` character.
        :type operation: str
        :rtype: ~azure.eventhub.receiver.Receiver
        """
        path = self.address.path + operation if operation else self.address.path
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, path, consumer_group, partition)
        source = Source(source_url)
        if offset is not None:
            source.set_filter(offset.selector())
        handler = Receiver(self, source, prefetch=prefetch)
        self.clients.append(handler)
        return handler

    def add_epoch_receiver(self, consumer_group, partition, epoch, prefetch=300, operation=None):
        """
        Add a receiver to the client with an epoch value. Only a single epoch receiver
        can connect to a partition at any given time - additional epoch receivers must have
        a higher epoch value or they will be rejected. If a 2nd epoch receiver has
        connected, the first will be closed.

        :param consumer_group: The name of the consumer group.
        :type consumer_group: str
        :param partition: The ID of the partition.
        :type partition: str
        :param epoch: The epoch value for the receiver.
        :type epoch: int
        :param prefetch: The message prefetch count of the receiver. Default is 300.
        :type prefetch: int
        :operation: An optional operation to be appended to the hostname in the source URL.
         The value must start with `/` character.
        :type operation: str
        :rtype: ~azure.eventhub.receiver.Receiver
        """
        path = self.address.path + operation if operation else self.address.path
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, path, consumer_group, partition)
        handler = Receiver(self, source_url, prefetch=prefetch, epoch=epoch)
        self.clients.append(handler)
        return handler

    def add_sender(self, partition=None, operation=None):
        """
        Add a sender to the client to send ~azure.eventhub.common.EventData object
        to an EventHub.

        :param partition: Optionally specify a particular partition to send to.
         If omitted, the events will be distributed to available partitions via
         round-robin.
        :type parition: str
        :operation: An optional operation to be appended to the hostname in the target URL.
         The value must start with `/` character.
        :type operation: str
        :rtype: ~azure.eventhub.sender.Sender
        """
        target = "amqps://{}{}".format(self.address.hostname, self.address.path)
        if operation:
            target = target + operation
        handler = Sender(self, target, partition=partition)
        self.clients.append(handler)
        return handler
