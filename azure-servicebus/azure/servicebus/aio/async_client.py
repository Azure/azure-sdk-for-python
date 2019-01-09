#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import uuid
import datetime
import functools
from urllib.parse import urlparse

import requests
from uamqp import types

from azure.servicebus.common import mgmt_handlers, mixins
from azure.servicebus.aio.async_base_handler import BaseHandler
from azure.servicebus.aio import DeferredMessage, Sender, SessionSender, Receiver, SessionReceiver
from azure.servicebus.control_client import ServiceBusService, SERVICE_BUS_HOST_BASE, DEFAULT_HTTP_TIMEOUT
from azure.servicebus.control_client.models import AzureServiceBusResourceNotFound
from azure.servicebus.common.utils import parse_conn_str, build_uri, get_running_loop
from azure.servicebus.common.errors import ServiceBusConnectionError, ServiceBusResourceNotFound
from azure.servicebus.common.constants import (
    REQUEST_RESPONSE_PEEK_OPERATION,
    REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
    REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
    REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
    ReceiveSettleMode)


class ServiceBusClient(mixins.ServiceBusMixin):

    def __init__(self, *, service_namespace=None, host_base=SERVICE_BUS_HOST_BASE,
                 shared_access_key_name=None, shared_access_key_value=None, loop=None,
                 http_request_timeout=DEFAULT_HTTP_TIMEOUT, http_request_session=None, debug=False):
        """Initializes the service bus service for a namespace with the specified
        authentication settings (SAS).

        :param str service_namespace: Service bus namespace, required for all operations.
        :param str host_base: Optional. Live host base url. Defaults to Azure url.
        :param str shared_access_key_name: SAS authentication key name.
        :param str shared_access_key_value: SAS authentication key value.
        :param loop: An async event loop.
        :param int http_request_timeout: Optional. Timeout for the http request, in seconds.
        :param http_request_session: Optional. Session object to use for http requests.
        :param bool debug: Whether to output AMQP network trace to the logger.
        """
        self.loop = loop or get_running_loop()
        self.service_namespace = service_namespace
        self.host_base = host_base
        self.shared_access_key_name = shared_access_key_name
        self.shared_access_key_value = shared_access_key_value
        self.debug = debug
        self.mgmt_client = ServiceBusService(
            service_namespace=service_namespace,
            host_base=host_base,
            shared_access_key_name=shared_access_key_name,
            shared_access_key_value=shared_access_key_value,
            timeout=http_request_timeout,
            request_session=http_request_session)

    @classmethod
    def from_connection_string(cls, conn_str, *, loop=None, **kwargs):
        """
        Create a QueueClient from a connection string.
        :param conn_str: The connection string.
        :type conn_str: str
        :param queue_name: The name of the Queue, if the EntityName is
         not included in the connection string.
        """
        address, policy, key, _ = parse_conn_str(conn_str)
        parsed_namespace = urlparse(address)
        namespace, _, base = parsed_namespace.hostname.partition('.')
        return cls(
            service_namespace=namespace,
            shared_access_key_name=policy,
            shared_access_key_value=key,
            host_base='.' + base,
            loop=loop,
            **kwargs)

    def get_queue(self, queue_name):
        """Get an async client for a queue entity.

        :param queue_name: The name of the queue.
        :type queue_name: str
        :returns: ~azure.servicebus.queue_client.QueueClient
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the queue is not found.
        """
        try:
            queue = self.mgmt_client.get_queue(queue_name)
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)
        except AzureServiceBusResourceNotFound:
            raise ServiceBusResourceNotFound("Specificed queue does not exist.")
        return QueueClient.from_entity(
            self._get_host(), queue,
            shared_access_key_name=self.shared_access_key_name,
            shared_access_key_value=self.shared_access_key_value,
            mgmt_client=self.mgmt_client,
            loop=self.loop,
            debug=self.debug)

    def list_queues(self):
        """Get a clients for all queue entities in the namespace.

        :returns: list[~azure.servicebus.queue_client.QueueClient]
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        """
        try:
            queues = self.mgmt_client.list_queues()
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)
        queue_clients = []
        for queue in queues:
            queue_clients.append(QueueClient.from_entity(
                self._get_host(), queue,
                shared_access_key_name=self.shared_access_key_name,
                shared_access_key_value=self.shared_access_key_value,
                mgmt_client=self.mgmt_client,
                loop=self.loop,
                debug=self.debug))
        return queue_clients

    def get_topic(self, topic_name):
        """Get a client for a topic entity.

        :param topic_name: The name of the topic.
        :type topic_name: str
        :returns: ~azure.servicebus.topic_client.TopicClient
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the topic is not found.
        """
        try:
            topic = self.mgmt_client.get_topic(topic_name)
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)
        except AzureServiceBusResourceNotFound:
            raise ServiceBusResourceNotFound("Specificed topic does not exist.")
        return TopicClient.from_entity(
            self._get_host(), topic,
            shared_access_key_name=self.shared_access_key_name,
            shared_access_key_value=self.shared_access_key_value,
            loop=self.loop,
            debug=self.debug)

    def list_topics(self):
        """Get an async client for all topic entities in the namespace.

        :returns: list[~azure.servicebus.topic_client.TopicClient]
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        """
        try:
            topics = self.mgmt_client.list_topics()
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)
        topic_clients = []
        for topic in topics:
            topic_clients.append(TopicClient.from_entity(
                self._get_host(), topic,
                shared_access_key_name=self.shared_access_key_name,
                shared_access_key_value=self.shared_access_key_value,
                loop=self.loop,
                debug=self.debug))
        return topic_clients

    def get_subscription(self, topic_name, subscription_name):
        """Get an async client for a subscription entity.

        :param topic_name: The name of the topic.
        :type topic_name: str
        :param subscription_name: The name of the subscription.
        :type subscription_name: str
        :returns: ~azure.servicebus.subscription_client.SubscriptionClient
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the subscription is not found.
        """
        try:
            subscription = self.mgmt_client.get_subscription(topic_name, subscription_name)
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)
        except AzureServiceBusResourceNotFound:
            raise ServiceBusResourceNotFound("Specificed subscription does not exist.")
        return SubscriptionClient.from_entity(
            self._get_host(), topic_name, subscription,
            shared_access_key_name=self.shared_access_key_name,
            shared_access_key_value=self.shared_access_key_value,
            loop=self.loop,
            debug=self.debug)

    def list_subscriptions(self, topic_name):
        """Get an async client for all subscription entities in the topic.

        :param topic_name: The topic to list subscriptions for.
        :type topic_name: str
        :returns: list[~azure.servicebus.subscription_client.SubscriptionClient]
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the topic is not found.
        """
        try:
            subs = self.mgmt_client.list_subscriptions(topic_name)
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)
        except AzureServiceBusResourceNotFound:
            raise ServiceBusResourceNotFound("Specificed topic does not exist.")
        sub_clients = []
        for sub in subs:
            sub_clients.append(SubscriptionClient.from_entity(
                self._get_host(), topic_name, sub,
                shared_access_key_name=self.shared_access_key_name,
                shared_access_key_value=self.shared_access_key_value,
                loop=self.loop,
                debug=self.debug))
        return sub_clients


class SendClientMixin:

    async def send(self, messages, message_timeout=0, session=None, **kwargs):
        """Send one or more messages to the current entity. This operation
        will open a single-use connection, send the supplied messages, and close
        connection. If the entity requires sessions, a Session ID must be set
        on each outgoing message.
        This operation is only available on Python 3.5 and above.

        :param messages: One or more messages to be sent.
        :type messages: ~azure.servicebus.aio.async_message.Message
        :param message_timeout: The period in seconds during which the Message must be
         sent. If the send in not completed in this time it will fail.
        :type message_timeout: int
        :param session: An optional Session ID. If supplied, and the ServiceBus endpoint
         is sessionful, this Session ID will be applied to every outgoing message sent with
         this Sender. If an individual message already has a Session ID, that will be
         used instead. If no Session ID is supplied here, nor set on an outgoing
         message, a ValueError will be raised.
        :type session: str or ~uuid.Guid
        :raises: ~azure.servicebus.common.errors.MessageSendFailed
        """
        async with self.get_sender(message_timeout=message_timeout, session=session, **kwargs) as sender:
            if isinstance(messages, list):
                for m in messages:
                    sender.queue_message(m)
            else:
                sender.queue_message(messages)
            return await sender.send_pending_messages()

    def get_sender(self, message_timeout=0, session=None, **kwargs):
        """Get a Sender for the ServiceBus endpoint. A Sender represents
        a single open Connection with which multiple send operations can be made.
        This operation is only available on Python 3.5 and above.

        :param message_timeout: The period in seconds during which the Message must be
         sent. If the send in not completed in this time it will fail.
        :type message_timeout: int
        :param session: An optional Session ID. If supplied, and the ServiceBus endpoint
         is sessionful, this Session ID will be applied to every outgoing message sent with
         this Sender. If an individual message already has a Session ID, that will be
         used instead. If no Session ID is supplied here, nor set on an outgoing
         message, a ValueError will be raised.
        :type session: str or ~uuid.Guid
        :returns: A Sender instance with an unopened Connection.
        :rtype: ~azure.servicebus.send_handler.Sender
        :raises: If the current Service Bus entity requires sessions, a TypeError will
         be raised.
        """
        handler_id = str(uuid.uuid4())
        if self.entity and self.requires_session:
            return SessionSender(
                handler_id,
                self.entity_uri,
                self.auth_config,
                session=session,
                loop=self.loop,
                debug=self.debug,
                msg_timeout=message_timeout,
                **kwargs)
        return Sender(
            handler_id,
            self.entity_uri,
            self.auth_config,
            session=session,
            loop=self.loop,
            debug=self.debug,
            msg_timeout=message_timeout,
            **kwargs)


class ReceiveClientMixin:

    async def peek(self, count=1, start_from=0, session=None, **kwargs):
        """Browse messages currently pending in the queue. Peeked messages
        are not removed from queue, nor are they locked. The cannot be completed,
        deferred or dead-lettered.
        This operation is only available on Python 3.5 and above.

        :param count: Maximum number of messages to attempt to browse. The default
         value is 1.
        :type count: int
        :start_from: The starting message sequence number from which to browse. The
         default value is 0, i.e. start browsing from the first available message.
        :param session: If the entity requires sessions, a session ID must be supplied
         in order that only messages from that session will be browsed. If the entity
         does not require sessions this value will be ignored.
        :type session: str
        :returns: list[~azure.servicebus.common.message.PeekMessage]
        """
        message = {
            'from-sequence-number': types.AMQPLong(start_from),
            'message-count': int(count)}
        if self.entity and self.requires_session:
            if not session:
                raise ValueError("Sessions are required, please set session.")
            message['session-id'] = session

        async with BaseHandler(
                self.entity_uri, self.auth_config, loop=self.loop, debug=self.debug, **kwargs) as handler:
            return await handler._mgmt_request_response(  # pylint: disable=protected-access
                REQUEST_RESPONSE_PEEK_OPERATION,
                message,
                mgmt_handlers.peek_op)

    async def receive_deferred_messages(self, sequence_numbers, mode=ReceiveSettleMode.PeekLock, **kwargs):
        """Receive messages by sequence number that have been previously deffered.
        This operation is only available on Python 3.5 and above.

        :param sequence_numbers: A list of the sequence numbers of messages that have been
         deferred.
        :type sequence_numbers: list[int]
        :param mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode or str
        :returns: list[~azure.servicebus.aio.async_message.Message]
        """
        if (self.entity and self.requires_session) or kwargs.get('session'):
            raise ValueError("Sessionful deferred messages can only be received within a locked receive session.")
        try:
            receive_mode = mode.value.value
        except AttributeError:
            receive_mode = int(mode)
        message = {
            'sequence-numbers': types.AMQPArray([types.AMQPLong(s) for s in sequence_numbers]),
            'receiver-settle-mode': types.AMQPuInt(receive_mode)}

        mgmt_handler = functools.partial(
            mgmt_handlers.deferred_message_op, mode=receive_mode, message_type=DeferredMessage)
        async with BaseHandler(
                self.entity_uri, self.auth_config, loop=self.loop, debug=self.debug, **kwargs) as handler:
            return await handler._mgmt_request_response(  # pylint: disable=protected-access
                REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
                message,
                mgmt_handler)

    async def settle_deferred_messages(self, settlement, *messages, **kwargs):
        """Settle messages that have been previously deffered.
        This operation is only available on Python 3.5 and above.

        :param sequence_numbers: A list of the sequence numbers of messages that have been
         deferred.
        :type sequence_numbers: list[str]
        :param mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode or str
        :returns: list[~azure.servicebus.aio.async_message.Message]
        """
        if (self.entity and self.requires_session) or kwargs.get('session'):
            raise ValueError("Sessionful deferred messages can only be settled within a locked receive session.")
        if settlement.lower() not in ['completed', 'suspended', 'abandoned']:
            raise ValueError("Settlement must be one of: 'completed', 'suspended', 'abandoned'")
        message = {
            'disposition-status': settlement.lower(),
            'lock-tokens': types.AMQPArray([m.lock_token for m in messages])}

        async with BaseHandler(
                self.entity_uri, self.auth_config, loop=self.loop, debug=self.debug, **kwargs) as handler:
            return await handler._mgmt_request_response(  # pylint: disable=protected-access
                REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
                message,
                mgmt_handlers.default)

    async def list_sessions(self, updated_since=None, max_results=100, skip=0, **kwargs):
        """List the Session IDs with pending messages in the queue where the 'State' of the session
        has been updated since the timestamp provided. If no timestamp is provided, all will be returned.
        If the state of a Session has never been set, it will not be returned regardless of whether
        there are messages pending.
        This operation is only available on Python 3.5 and above.

        :param updated_since: The UTC datetime from which to return updated pending Session IDs.
        :type updated_since: datetime.datetime
        :param max_results: The maximum number of Session IDs to return. Default value is 100.
        :type max_results: int
        :param skip: The page value to jump to. Default value is 0.
        :type skip: int
        :returns: list[str]
        """
        if self.entity and not self.requires_session:
            raise ValueError("This is not a sessionful entity.")
        message = {
            'last-updated-time': updated_since or datetime.datetime.utcfromtimestamp(0),
            'skip': types.AMQPInt(skip),
            'top': types.AMQPInt(max_results),
        }
        async with BaseHandler(
                self.entity_uri, self.auth_config, loop=self.loop, debug=self.debug, **kwargs) as handler:
            return await handler._mgmt_request_response(  # pylint: disable=protected-access
                REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
                message,
                mgmt_handlers.list_sessions_op)

    def get_receiver(self, session=None, prefetch=0, mode=ReceiveSettleMode.PeekLock, idle_timeout=0, **kwargs):
        """Get a Receiver for the ServiceBus endpoint. A Receiver represents
        a single open Connection with which multiple receive operations can be made.
        This operation is only available on Python 3.5 and above.

        :param session: A specific session from which to receive. This must be specified for a
         sessionful entity, otherwise it must be None. In order to receive the next available
         session, set this to NEXT_AVAILABLE.
        :type session: str or ~azure.servicebus.NEXT_AVAILABLE
        :param prefetch: The maximum number of messages to cache with each request to the service.
         The default value is 0, i.e. messages will be received from the service and processed
         one at a time. Increasing this value will improve message through-put performance but increase
         the change that messages will expire while they are cached if they're not processed fast enough.
        :type prefetch: int
        :param mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode or str
        :param idle_timeout: The timeout in seconds between received messages after which the receiver will
         automatically shutdown. The default value is 0, i.e. no timeout.
        :type idle_timeout: int
        :returns: A Receiver instance with an unopened Connection.
        :rtype: ~azure.servicebus.receive_handler.Receiver
        :raises: If the current Service Bus entity requires sessions, a TypeError will
         be raised.
        """
        if self.entity and not self.requires_session and session:
            raise ValueError("A session cannot be used with a non-sessionful entitiy.")
        if self.entity and self.requires_session and not session:
            raise ValueError("This entity requires a session.")
        assert prefetch >= 0, "Prefetch must be an integer between 0 and 50000 inclusive."
        prefetch += 1
        handler_id = str(uuid.uuid4())
        if session:
            return SessionReceiver(
                handler_id,
                self.entity_uri,
                self.auth_config,
                session=session,
                loop=self.loop,
                debug=self.debug,
                timeout=int(idle_timeout * 1000),
                prefetch=prefetch,
                mode=mode,
                **kwargs)
        return Receiver(
            handler_id,
            self.entity_uri,
            self.auth_config,
            loop=self.loop,
            debug=self.debug,
            timeout=int(idle_timeout * 1000),
            prefetch=prefetch,
            mode=mode,
            **kwargs)

    def get_deadletter_receiver(
            self, transfer_deadletter=False, prefetch=0,
            mode=ReceiveSettleMode.PeekLock, idle_timeout=0, **kwargs):
        """Get a Receiver for the deadletter endpoint of the queue. A Receiver represents
        a single open Connection with which multiple receive operations can be made.
        This operation is only available on Python 3.5 and above.

        :param transfer_deadletter: Whether to connect to the transfer deadletter queue, or the standard
         deadletter queue. Default is False, i.e. the standard deadletter endpoint.
        :type transfer_deadletter: bool
        :param prefetch: The maximum number of messages to cache with each request to the service.
         The default value is 0, i.e. messages will be received from the service and processed
         one at a time. Increasing this value will improve message through-put performance but increase
         the change that messages will expire while they are cached if they're not processed fast enough.
        :type prefetch: int
        :param mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode or str
        :param idle_timeout: The timeout in seconds between received messages after which the receiver will
         automatically shutdown. The default value is 0, i.e. no timeout.
        :type idle_timeout: int
        :returns: A Receiver instance with an unopened Connection.
        :rtype: ~azure.servicebus.receive_handler.Receiver
        """
        assert prefetch >= 0, "Prefetch must be an integer between 0 and 50000 inclusive."
        prefetch += 1
        handler_id = str(uuid.uuid4())
        if transfer_deadletter:
            entity_uri = self.mgmt_client.format_transfer_dead_letter_queue_name(self.entity_uri)
        else:
            entity_uri = self.mgmt_client.format_dead_letter_queue_name(self.entity_uri)
        return Receiver(
            handler_id,
            entity_uri,
            self.auth_config,
            loop=self.loop,
            debug=self.debug,
            timeout=int(idle_timeout * 1000),
            prefetch=prefetch,
            mode=mode,
            **kwargs)


class BaseClient(mixins.BaseClient):

    def __init__(self, address, name, *, shared_access_key_name=None,
                 shared_access_key_value=None, loop=None, debug=False, **kwargs):
        """
        Constructs a new Client to interact with the named ServiceBus entity.

        :param address: The full URI of the Service Bus namespace. This can optionally
         include URL-encoded access name and key.
        :type address: str
        :param name: The name of the entity to which the Client will connect.
        :type name: str
        :param shared_access_key_name: The name of the shared access policy. This must be supplied
         if not encoded into the address.
        :type shared_access_key_name: str
        :param shared_access_key_value: The shared access key. This must be supplied if not encoded
         into the address.
        :type shared_access_key_value: str
        :param debug: Whether to output network trace logs to the logger. Default is `False`.
        :type debug: bool
        """
        self.loop = loop or get_running_loop()
        super(BaseClient, self).__init__(
            address, name, shared_access_key_name=shared_access_key_name,
            shared_access_key_value=shared_access_key_value, debug=debug, **kwargs)

    def _get_entity(self):
        raise NotImplementedError("Must be implemented by child class.")


class QueueClient(SendClientMixin, ReceiveClientMixin, BaseClient):
    """
    The QueueClient class defines a high level interface for sending
    messages to and receiving messages from the Azure ServiceBus service.
    """

    def _get_entity(self):
        return self.mgmt_client.get_queue(self.name)


class TopicClient(SendClientMixin, BaseClient):
    """
    The TopicClient class defines a high level interface for sending
    messages to an Azure ServiceBus Topic.
    """

    def _get_entity(self):
        return self.mgmt_client.get_topic(self.name)


class SubscriptionClient(ReceiveClientMixin, BaseClient):
    """
    The SubscriptionClient class defines a high level interface for receiving
    messages from an Azure ServiceBus Subscription.
    """

    def __init__(self, address, name, *, shared_access_key_name=None,
                 shared_access_key_value=None, loop=None, debug=False, **kwargs):
        """
        Constructs a new Client to interact with the named ServiceBus entity.

        :param address: The full URI of the Service Bus namespace. This can optionally
         include URL-encoded access name and key.
        :type address: str
        :param name: The name of the entity to which the Client will connect.
        :type name: str
        :param shared_access_key_name: The name of the shared access policy. This must be supplied
         if not encoded into the address.
        :type shared_access_key_name: str
        :param shared_access_key_value: The shared access key. This must be supplied if not encoded
         into the address.
        :type shared_access_key_value: str
        :param debug: Whether to output network trace logs to the logger. Default is `False`.
        :type debug: bool
        """
        super(SubscriptionClient, self).__init__(
            address, name,
            shared_access_key_name=shared_access_key_name,
            shared_access_key_value=shared_access_key_value,
            loop=loop, debug=debug, **kwargs)
        self.topic_name = self.address.path.split("/")[1]

    @classmethod
    def from_connection_string(cls, conn_str, name, topic=None, **kwargs):  # pylint: disable=arguments-differ
        """
        Create a QueueClient from a connection string.

        :param conn_str: The connection string.
        :type conn_str: str
        :param name: The name of the Subscription.
        :type name: str
        :param topic: The name of the Topic, if the EntityName is
         not included in the connection string.
        :type topic: str
        """
        address, policy, key, entity = parse_conn_str(conn_str)
        entity = topic or entity
        address = build_uri(address, entity)
        address += "/Subscriptions/" + name
        return cls(address, name, shared_access_key_name=policy, shared_access_key_value=key, **kwargs)

    @classmethod
    def from_entity(cls, address, topic, entity, **kwargs):  # pylint: disable=arguments-differ
        client = cls(
            address + "/" + topic + "/Subscriptions/" + entity.name,
            entity.name,
            validated_entity=entity,
            **kwargs)
        return client

    def _get_entity(self):
        return self.mgmt_client.get_subscription(self.topic_name, self.name)
