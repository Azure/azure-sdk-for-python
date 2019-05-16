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
from .client_abstract import EventHubClientAbstract


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


class EventHubClient(EventHubClientAbstract):
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

    def _create_auth(self, username=None, password=None):
        """
        Create an ~uamqp.authentication.SASTokenAuth instance to authenticate
        the session.

        :param username: The name of the shared access policy.
        :type username: str
        :param password: The shared access key.
        :type password: str
        """
        http_proxy = self.config.http_proxy_policy.http_proxy
        transport_type = self.config.transport_type
        auth_timeout = self.config.auth_timeout
        if self.sas_token:
            token = self.sas_token() if callable(self.sas_token) else self.sas_token
            try:
                expiry = int(parse_sas_token(token)['se'])
            except (KeyError, TypeError, IndexError):
                raise ValueError("Supplied SAS token has no valid expiry value.")
            return authentication.SASTokenAuth(
                self.auth_uri, self.auth_uri, token,
                expires_at=expiry,
                timeout=auth_timeout,
                http_proxy=http_proxy,
                transport_type=transport_type)

        username = username or self._auth_config['username']
        password = password or self._auth_config['password']
        if "@sas.root" in username:
            return authentication.SASLPlain(
                self.address.hostname, username, password, http_proxy=http_proxy, transport_type=transport_type)
        return authentication.SASTokenAuth.from_shared_access_key(
            self.auth_uri, username, password, timeout=auth_timeout, http_proxy=http_proxy, transport_type=transport_type)

    def _close_clients(self):
        """
        Close all open Sender/Receiver clients.
        """
        for client in self.clients:
            client.close()

    def _start_clients(self):
        for client in self.clients:
            try:
                if not client.running:
                    client.open()
            except Exception as exp:  # pylint: disable=broad-except
                client.close(exception=exp)

    def _process_redirect_uri(self, redirect):
        redirect_uri = redirect.address.decode('utf-8')
        auth_uri, _, _ = redirect_uri.partition("/ConsumerGroups")
        self.address = urlparse(auth_uri)
        self.auth_uri = "sb://{}{}".format(self.address.hostname, self.address.path)
        self.eh_name = self.address.path.lstrip('/')
        self.mgmt_target = redirect_uri

    def _handle_redirect(self, redirects):
        if len(redirects) != len(self.clients):
            raise EventHubError("Some clients are attempting to redirect the connection.")
        if not all(r.hostname == redirects[0].hostname for r in redirects):
            raise EventHubError("Multiple clients attempting to redirect to different hosts.")
        self._process_redirect_uri(redirects[0])
        for client in self.clients:
            client.open()

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

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_run]
                :end-before: [END eventhub_client_run]
                :language: python
                :dedent: 4
                :caption: Run the EventHubClient in blocking mode.

        """
        log.info("%r: Starting %r clients", self.container_id, len(self.clients))
        try:
            self._start_clients()
            redirects = [c.redirected for c in self.clients if c.redirected]
            failed = [c.error for c in self.clients if c.error]
            if failed and len(failed) == len(self.clients):
                log.warning("%r: All clients failed to start.", self.container_id)
                raise failed[0]
            if failed:
                log.warning("%r: %r clients failed to start.", self.container_id, len(failed))
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

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_stop]
                :end-before: [END eventhub_client_stop]
                :language: python
                :dedent: 4
                :caption: Stop the EventHubClient and all its Sender/Receiver clients.

        """
        log.info("%r: Stopping %r clients", self.container_id, len(self.clients))
        self.stopped = True
        self._close_clients()

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
        alt_creds = {
            "username": self._auth_config.get("iot_username"),
            "password":self._auth_config.get("iot_password")}
        # TODO: add proxy?
        try:
            mgmt_auth = self._create_auth(**alt_creds)
            mgmt_client = uamqp.AMQPClient(self.mgmt_target, auth=mgmt_auth, debug=self.debug)
            mgmt_client.open()
            mgmt_msg = Message(application_properties={'name': self.eh_name})
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
        finally:
            mgmt_client.close()

    def add_receiver(
            self, consumer_group, partition, offset=None, epoch=None, prefetch=300,
            operation=None):
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

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START create_eventhub_client_receiver]
                :end-before: [END create_eventhub_client_receiver]
                :language: python
                :dedent: 4
                :caption: Add a receiver to the client for a particular consumer group and partition.

        """
        path = self.address.path + operation if operation else self.address.path
        source_url = "amqps://{}{}/ConsumerGroups/{}/Partitions/{}".format(
            self.address.hostname, path, consumer_group, partition)
        handler = Receiver(
            self, source_url, offset=offset, epoch=epoch, prefetch=prefetch)
        self.clients.append(handler)
        return handler

    def add_epoch_receiver(
            self, consumer_group, partition, epoch, prefetch=300,
            operation=None):
        return self.add_receiver(consumer_group, partition, epoch=epoch, prefetch=prefetch, operation=operation)

    def add_sender(self, partition=None, operation=None, send_timeout=60):
        """
        Add a sender to the client to send EventData object to an EventHub.

        :param partition: Optionally specify a particular partition to send to.
         If omitted, the events will be distributed to available partitions via
         round-robin.
        :type parition: str
        :operation: An optional operation to be appended to the hostname in the target URL.
         The value must start with `/` character.
        :type operation: str
        :param send_timeout: The timeout in seconds for an individual event to be sent from the time that it is
         queued. Default value is 60 seconds. If set to 0, there will be no timeout.
        :type send_timeout: int
        :param keep_alive: The time interval in seconds between pinging the connection to keep it alive during
         periods of inactivity. The default value is 30 seconds. If set to `None`, the connection will not
         be pinged.
        :type keep_alive: int
        :param auto_reconnect: Whether to automatically reconnect the sender if a retryable error occurs.
         Default value is `True`.
        :rtype: ~azure.eventhub.sender.Sender

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START create_eventhub_client_sender]
                :end-before: [END create_eventhub_client_sender]
                :language: python
                :dedent: 4
                :caption: Add a sender to the client to send EventData object to an EventHub.

        """
        target = "amqps://{}{}".format(self.address.hostname, self.address.path)
        if operation:
            target = target + operation
        handler = Sender(
            self, target, partition=partition, send_timeout=send_timeout)
        self.clients.append(handler)
        return handler

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
