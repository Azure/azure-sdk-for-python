# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import datetime
import uuid
import functools
import requests
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from uamqp import types
from uamqp.constants import TransportType

from azure.servicebus.common import mgmt_handlers, mixins
from azure.servicebus.common.constants import (
    ReceiveSettleMode,
    REQUEST_RESPONSE_PEEK_OPERATION,
    REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
    REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
    REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION)
from azure.servicebus.common.message import Message
from azure.servicebus.common.utils import parse_conn_str, build_uri
from azure.servicebus.common.errors import ServiceBusConnectionError, ServiceBusResourceNotFound
from azure.servicebus.control_client import ServiceBusService, SERVICE_BUS_HOST_BASE, DEFAULT_HTTP_TIMEOUT
from azure.servicebus.control_client.models import AzureServiceBusResourceNotFound
from azure.servicebus.send_handler import Sender, SessionSender
from azure.servicebus.receive_handler import Receiver, SessionReceiver
from azure.servicebus.base_handler import BaseHandler


class ServiceBusClient(mixins.ServiceBusMixin):
    """A Service Bus client for a namespace with the specified SAS authentication settings.

    :param str service_namespace: Service Bus namespace, required for all operations.
    :param str host_base: Optional. Live host base URL. Defaults to Public Azure.
    :param str shared_access_key_name: SAS authentication key name.
    :param str shared_access_key_value: SAS authentication key value.
    :param transport_type: Optional. Underlying transport protocol type (Amqp or AmqpOverWebsocket)
     Default value is ~azure.servicebus.TransportType.Amqp
    :type transport_type: ~azure.servicebus.TransportType
    :param int http_request_timeout: Optional. Timeout for the HTTP request, in seconds.
     Default value is 65 seconds.
    :param http_request_session: Optional. Session object to use for HTTP requests.
    :type http_request_session: ~requests.Session
    :param bool debug: Whether to output AMQP network trace to the logger.

    .. admonition:: Example:
        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START create_servicebus_client]
            :end-before: [END create_servicebus_client]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the Service Bus client

    """

    def __init__(self, service_namespace=None, host_base=SERVICE_BUS_HOST_BASE,
                 shared_access_key_name=None, shared_access_key_value=None,
                 transport_type=TransportType.Amqp,
                 http_request_timeout=DEFAULT_HTTP_TIMEOUT, http_request_session=None, debug=False):

        self.service_namespace = service_namespace
        self.host_base = host_base
        self.shared_access_key_name = shared_access_key_name
        self.shared_access_key_value = shared_access_key_value
        self.transport_type = transport_type
        self.debug = debug
        self.mgmt_client = ServiceBusService(
            service_namespace=service_namespace,
            host_base=host_base,
            shared_access_key_name=shared_access_key_name,
            shared_access_key_value=shared_access_key_value,
            timeout=http_request_timeout,
            request_session=http_request_session)

    @classmethod
    def from_connection_string(cls, conn_str, **kwargs):
        """Create a Service Bus client from a connection string.

        :param conn_str: The connection string.
        :type conn_str: str

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START create_servicebus_client_connstr]
                :end-before: [END create_servicebus_client_connstr]
                :language: python
                :dedent: 4
                :caption: Create a ServiceBusClient via a connection string.

        """
        address, policy, key, _, transport_type = parse_conn_str(conn_str)
        parsed_namespace = urlparse(address)
        namespace, _, base = parsed_namespace.hostname.partition('.')
        return cls(
            namespace,
            shared_access_key_name=policy,
            shared_access_key_value=key,
            transport_type=transport_type,
            host_base='.' + base,
            **kwargs)

    def _get_host(self):
        return "sb://" + self.service_namespace + self.host_base

    def get_queue(self, queue_name):
        """Get a client for a queue entity.

        :param queue_name: The name of the queue.
        :type queue_name: str
        :rtype: ~azure.servicebus.servicebus_client.QueueClient
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the queue is not found.

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START get_queue_client]
                :end-before: [END get_queue_client]
                :language: python
                :dedent: 8
                :caption: Get the specific queue client from Service Bus client

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
            transport_type=self.transport_type,
            mgmt_client=self.mgmt_client,
            debug=self.debug)

    def list_queues(self):
        """Get clients for all queue entities in the namespace.

        :rtype: list[~azure.servicebus.servicebus_client.QueueClient]
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START list_queues]
                :end-before: [END list_queues]
                :language: python
                :dedent: 4
                :caption: List the queues from Service Bus client

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
                transport_type=self.transport_type,
                mgmt_client=self.mgmt_client,
                debug=self.debug))
        return queue_clients

    def get_topic(self, topic_name):
        """Get a client for a topic entity.

        :param topic_name: The name of the topic.
        :type topic_name: str
        :rtype: ~azure.servicebus.servicebus_client.TopicClient
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the topic is not found.

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START get_topic_client]
                :end-before: [END get_topic_client]
                :language: python
                :dedent: 8
                :caption: Get the specific topic client from Service Bus client

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
            transport_type=self.transport_type,
            debug=self.debug)

    def list_topics(self):
        """Get a client for all topic entities in the namespace.

        :rtype: list[~azure.servicebus.servicebus_client.TopicClient]
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START list_topics]
                :end-before: [END list_topics]
                :language: python
                :dedent: 4
                :caption: List the topics from Service Bus client

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
                transport_type=self.transport_type,
                debug=self.debug))
        return topic_clients

    def get_subscription(self, topic_name, subscription_name):
        """Get a client for a subscription entity.

        :param topic_name: The name of the topic.
        :type topic_name: str
        :param subscription_name: The name of the subscription.
        :type subscription_name: str
        :rtype: ~azure.servicebus.servicebus_client.SubscriptionClient
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the subscription is not found.

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START get_subscription_client]
                :end-before: [END get_subscription_client]
                :language: python
                :dedent: 8
                :caption: Get the specific subscription client from Service Bus client

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
            transport_type=self.transport_type,
            debug=self.debug)

    def list_subscriptions(self, topic_name):
        """Get a client for all subscription entities in the topic.

        :param topic_name: The topic to list subscriptions for.
        :type topic_name: str
        :rtype: list[~azure.servicebus.servicebus_client.SubscriptionClient]
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the topic is not found.

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START list_subscriptions]
                :end-before: [END list_subscriptions]
                :language: python
                :dedent: 4
                :caption: List the subscriptions from Service Bus client

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
                transport_type=self.transport_type,
                debug=self.debug))
        return sub_clients


class SendClientMixin(object):

    def send(self, messages, message_timeout=0, session=None, **kwargs):
        """Send one or more messages to the current entity.

        This operation will open a single-use connection, send the supplied messages, and close
        connection. If the entity requires sessions, a session ID must be either
        provided here, or set on each outgoing message.

        :param messages: One or more messages to be sent.
        :type messages: ~azure.servicebus.common.message.Message or list[~azure.servicebus.common.message.Message]
        :param message_timeout: The period in seconds during which the Message must be
         sent. If the send is not completed in this time it will return a failure result.
        :type message_timeout: int
        :param session: An optional session ID. If supplied this session ID will be
         applied to every outgoing message sent with this Sender.
         If an individual message already has a session ID, that will be
         used instead. If no session ID is supplied here, nor set on an outgoing
         message, a ValueError will be raised if the entity is sessionful.
        :type session: str or ~uuid.Guid
        :raises: ~azure.servicebus.common.errors.MessageSendFailed
        :returns: A list of the send results of all the messages. Each
         send result is a tuple with two values. The first is a boolean, indicating `True`
         if the message sent, or `False` if it failed. The second is an error if the message
         failed, otherwise it will be `None`.
        :rtype: list[tuple[bool, ~azure.servicebus.common.errors.MessageSendFailed]]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START send_message_service_bus]
                :end-before: [END send_message_service_bus]
                :language: python
                :dedent: 4
                :caption: Send a message to current entity via a single use connection

            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START send_message_service_bus_multiple]
                :end-before: [END send_message_service_bus_multiple]
                :language: python
                :dedent: 4
                :caption: Send messages to current entity via a single use connection

        """
        with self.get_sender(message_timeout=message_timeout, session=session, **kwargs) as sender:
            if isinstance(messages, Message):
                sender.queue_message(messages)
            else:
                try:
                    messages = list(messages)
                except TypeError:
                    raise TypeError("Value of messages must be a 'Message' object or an iterable of 'Message' objects.")

                for m in messages:
                    if not isinstance(m, Message):
                        raise TypeError("Item {} in iterator is not of type 'Message'.".format(m))
                    sender.queue_message(m)

            return sender.send_pending_messages()

    def get_sender(self, message_timeout=0, session=None, **kwargs):
        """Get a Sender for the Service Bus endpoint.

        A Sender represents a single open Connection with which multiple send operations can be made.

        :param message_timeout: The period in seconds during which messages sent with
         this Sender must be sent. If the send is not completed in this time it will fail.
        :type message_timeout: int
        :param session: An optional session ID. If supplied this session ID will be
         applied to every outgoing message sent with this Sender.
         If an individual message already has a session ID, that will be
         used instead. If no session ID is supplied here, nor set on an outgoing
         message, a ValueError will be raised if the entity is sessionful.
        :type session: str or ~uuid.Guid
        :returns: A Sender instance with an unopened connection.
        :rtype: ~azure.servicebus.send_handler.Sender

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START get_sender]
                :end-before: [END get_sender]
                :language: python
                :dedent: 4
                :caption: Get sender client from Service Bus client

        """
        handler_id = str(uuid.uuid4())
        if self.entity and self.requires_session:
            return SessionSender(
                handler_id,
                self.entity_uri,
                self.auth_config,
                session=session,
                debug=self.debug,
                msg_timeout=message_timeout,
                **kwargs)
        return Sender(
            handler_id,
            self.entity_uri,
            self.auth_config,
            session=session,
            debug=self.debug,
            msg_timeout=message_timeout,
            **kwargs)


class ReceiveClientMixin(object):

    def peek(self, count=1, start_from=0, session=None, **kwargs):
        """Browse messages currently pending in the queue.

        Peeked messages are not removed from queue, nor are they locked. They cannot be completed,
        deferred or dead-lettered.

        :param count: The maximum number of messages to try and peek. The default
         value is 1.
        :type count: int
        :param start_from: A message sequence number from which to start browsing messages.
        :type start_from: int
        :param session: If the entity requires sessions, a session ID must be supplied
         in order that only messages from that session will be browsed. If the entity
         does not require sessions this value will be ignored.
        :type session: str
        :rtype: list[~azure.servicebus.common.message.PeekMessage]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START peek_messages_service_bus]
                :end-before: [END peek_messages_service_bus]
                :language: python
                :dedent: 4
                :caption: Look at specificied number of messages without removing them from queue

        """
        message = {'from-sequence-number': types.AMQPLong(start_from), 'message-count': int(count)}
        if self.entity and self.requires_session:
            if not session:
                raise ValueError("Sessions are required, please set session.")
            message['session-id'] = session

        with BaseHandler(self.entity_uri, self.auth_config, debug=self.debug, **kwargs) as handler:
            return handler._mgmt_request_response(  # pylint: disable=protected-access
                REQUEST_RESPONSE_PEEK_OPERATION,
                message,
                mgmt_handlers.peek_op)

    def list_sessions(self, updated_since=None, max_results=100, skip=0, **kwargs):
        """List session IDs.

        List the Session IDs with pending messages in the queue where the state of the session
        has been updated since the timestamp provided. If no timestamp is provided, all will be returned.
        If the state of a session has never been set, it will not be returned regardless of whether
        there are messages pending.

        :param updated_since: The UTC datetime from which to return updated pending Session IDs.
        :type updated_since: datetime.datetime
        :param max_results: The maximum number of Session IDs to return. Default value is 100.
        :type max_results: int
        :param skip: The page value to jump to. Default value is 0.
        :type skip: int
        :rtype: list[str]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START list_sessions_service_bus]
                :end-before: [END list_sessions_service_bus]
                :language: python
                :dedent: 4
                :caption: Get the Ids of session which have messages pending in the queue

        """
        if self.entity and not self.requires_session:
            raise ValueError("This is not a sessionful entity.")
        message = {
            'last-updated-time': updated_since or datetime.datetime.utcfromtimestamp(0),
            'skip': types.AMQPInt(skip),
            'top': types.AMQPInt(max_results),
        }
        with BaseHandler(self.entity_uri, self.auth_config, debug=self.debug, **kwargs) as handler:
            return handler._mgmt_request_response(  # pylint: disable=protected-access
                REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
                message,
                mgmt_handlers.list_sessions_op)

    def receive_deferred_messages(self, sequence_numbers, mode=ReceiveSettleMode.PeekLock, **kwargs):
        """Receive messages by sequence number that have been previously deferred.

        When receiving deferred messages from a partitioned entity, all of the supplied
        sequence numbers must be messages from the same partition.

        :param sequence_numbers: A list of the sequence numbers of messages that have been
         deferred.
        :type sequence_numbers: list[int]
        :param mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
        :rtype: list[~azure.servicebus.common.message.Message]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START receive_deferred_messages_service_bus]
                :end-before: [END receive_deferred_messages_service_bus]
                :language: python
                :dedent: 8
                :caption: Get the messages which were deferred using their sequence numbers

        """
        if (self.entity and self.requires_session) or kwargs.get('session'):
            raise ValueError("Sessionful deferred messages can only be received within a locked receive session.")
        if not sequence_numbers:
            raise ValueError("At least one sequence number must be specified.")
        try:
            receive_mode = mode.value.value
        except AttributeError:
            receive_mode = int(mode)
        message = {
            'sequence-numbers': types.AMQPArray([types.AMQPLong(s) for s in sequence_numbers]),
            'receiver-settle-mode': types.AMQPuInt(receive_mode)}
        mgmt_handler = functools.partial(mgmt_handlers.deferred_message_op, mode=receive_mode)
        with BaseHandler(self.entity_uri, self.auth_config, debug=self.debug, **kwargs) as handler:
            return handler._mgmt_request_response(  # pylint: disable=protected-access
                REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
                message,
                mgmt_handler)

    def settle_deferred_messages(self, settlement, messages, **kwargs):
        """Settle messages that have been previously deferred.

        :param settlement: How the messages are to be settled. This must be a string
         of one of the following values: 'completed', 'suspended', 'abandoned'.
        :type settlement: str
        :param messages: A list of deferred messages to be settled.
        :type messages: list[~azure.servicebus.common.message.DeferredMessage]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START settle_deferred_messages_service_bus]
                :end-before: [END settle_deferred_messages_service_bus]
                :language: python
                :dedent: 8
                :caption: Settle deferred messages.

        """
        if (self.entity and self.requires_session) or kwargs.get('session'):
            raise ValueError("Sessionful deferred messages can only be settled within a locked receive session.")
        if settlement.lower() not in ['completed', 'suspended', 'abandoned']:
            raise ValueError("Settlement must be one of: 'completed', 'suspended', 'abandoned'")
        if not messages:
            raise ValueError("At least one message must be specified.")
        message = {
            'disposition-status': settlement.lower(),
            'lock-tokens': types.AMQPArray([m.lock_token for m in messages])}

        with BaseHandler(self.entity_uri, self.auth_config, debug=self.debug, **kwargs) as handler:
            return handler._mgmt_request_response(  # pylint: disable=protected-access
                REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
                message,
                mgmt_handlers.default)

    def get_receiver(self, session=None, prefetch=0, mode=ReceiveSettleMode.PeekLock, idle_timeout=0, **kwargs):
        """Get a Receiver for the Service Bus endpoint.

        A Receiver represents a single open Connection with which multiple receive operations can be made.

        :param session: A specific session from which to receive. This must be specified for a
         sessionful entity, otherwise it must be None. In order to receive the next available
         session, set this to NEXT_AVAILABLE.
        :type session: str or ~azure.servicebus.common.constants.NEXT_AVAILABLE
        :param prefetch: The maximum number of messages to cache with each request to the service.
         The default value is 0, meaning messages will be received from the service and processed
         one at a time. Increasing this value will improve message throughput performance but increase
         the change that messages will expire while they are cached if they're not processed fast enough.
        :type prefetch: int
        :param mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
        :param idle_timeout: The timeout in seconds between received messages after which the receiver will
         automatically shutdown. The default value is 0, meaning no timeout.
        :type idle_timeout: int
        :returns: A Receiver instance with an unopened Connection.
        :rtype: ~azure.servicebus.receive_handler.Receiver
        :raises: If the current Service Bus entity requires sessions, a TypeError will
         be raised.

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START get_receiver]
                :end-before: [END get_receiver]
                :language: python
                :dedent: 4
                :caption: Get the receiver client from Service Bus client

        """
        if self.entity and not self.requires_session and session:
            raise ValueError("A session cannot be used with a non-sessionful entitiy.")
        if self.entity and self.requires_session and not session:
            raise ValueError("This entity requires a session.")
        if int(prefetch) < 0 or int(prefetch) > 50000:
            raise ValueError("Prefetch must be an integer between 0 and 50000 inclusive.")

        prefetch += 1
        handler_id = str(uuid.uuid4())
        if session:
            return SessionReceiver(
                handler_id,
                self.entity_uri,
                self.auth_config,
                session=session,
                debug=self.debug,
                timeout=int(idle_timeout * 1000),
                prefetch=prefetch,
                mode=mode,
                **kwargs)
        return Receiver(
            handler_id,
            self.entity_uri,
            self.auth_config,
            debug=self.debug,
            timeout=int(idle_timeout * 1000),
            prefetch=prefetch,
            mode=mode,
            **kwargs)

    def get_deadletter_receiver(
            self, transfer_deadletter=False, prefetch=0,
            mode=ReceiveSettleMode.PeekLock, idle_timeout=0, **kwargs):
        """Get a Receiver for the deadletter endpoint of the queue.

        A Receiver represents a single open Connection with which multiple receive operations can be made.

        :param transfer_deadletter: Whether to connect to the transfer deadletter queue, or the standard
         deadletter queue. Default is False, using the standard deadletter endpoint.
        :type transfer_deadletter: bool
        :param prefetch: The maximum number of messages to cache with each request to the service.
         The default value is 0, meaning messages will be received from the service and processed
         one at a time. Increasing this value will improve message throughput performance but increase
         the change that messages will expire while they are cached if they're not processed fast enough.
        :type prefetch: int
        :param mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
        :param idle_timeout: The timeout in seconds between received messages after which the receiver will
         automatically shutdown. The default value is 0, meaning no timeout.
        :type idle_timeout: int
        :returns: A Receiver instance with an unopened Connection.
        :rtype: ~azure.servicebus.receive_handler.Receiver

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START get_dead_letter_receiver]
                :end-before: [END get_dead_letter_receiver]
                :language: python
                :dedent: 4
                :caption: Get the dead lettered messages

        """
        if int(prefetch) < 0 or int(prefetch) > 50000:
            raise ValueError("Prefetch must be an integer between 0 and 50000 inclusive.")

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
            debug=self.debug,
            timeout=int(idle_timeout * 1000),
            prefetch=prefetch,
            mode=mode,
            **kwargs)


class QueueClient(SendClientMixin, ReceiveClientMixin, mixins.BaseClient):
    """A queue client.

    The QueueClient class defines a high level interface for sending
    messages to and receiving messages from an Azure Service Bus queue.
    If you do not wish to perform management operations, a QueueClient can be
    instantiated directly to perform send and receive operations to a Queue.
    However if a QueueClient is created directly, a `get_properties` operation will
    need to be completed in order to retrieve the properties of this queue (for example,
    whether it is sessionful).

    :param address: The full URI of the Service Bus namespace. This can optionally
        include URL-encoded access name and key.
    :type address: str
    :param name: The name of the queue to which the Client will connect.
    :type name: str
    :param shared_access_key_name: The name of the shared access policy. This must be supplied
     if not encoded into the address.
    :type shared_access_key_name: str
    :param shared_access_key_value: The shared access key. This must be supplied if not encoded
     into the address.
    :type shared_access_key_value: str
    :param debug: Whether to output network trace logs to the logger. Default is `False`.
    :type debug: bool

    .. admonition:: Example:
        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START create_queue_client_directly]
            :end-before: [END create_queue_client_directly]
            :language: python
            :dedent: 8
            :caption: Create a QueueClient.

    """

    def _get_entity(self):
        return self.mgmt_client.get_queue(self.name)


class TopicClient(SendClientMixin, mixins.BaseClient):
    """A topic client.

    The TopicClient class defines a high level interface for sending
    messages to an Azure Service Bus Topic.
    If you do not wish to perform management operations, a TopicClient can be
    instantiated directly to perform send operations to a Topic.

    :param address: The full URI of the Service Bus namespace. This can optionally
        include URL-encoded access name and key.
    :type address: str
    :param name: The name of the topic to which the Client will connect.
    :type name: str
    :param shared_access_key_name: The name of the shared access policy. This must be supplied
     if not encoded into the address.
    :type shared_access_key_name: str
    :param shared_access_key_value: The shared access key. This must be supplied if not encoded
     into the address.
    :type shared_access_key_value: str
    :param debug: Whether to output network trace logs to the logger. Default is `False`.
    :type debug: bool

    .. admonition:: Example:
        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START create_topic_client_directly]
            :end-before: [END create_topic_client_directly]
            :language: python
            :dedent: 8
            :caption: Create a TopicClient.

    """

    def _get_entity(self):
        return self.mgmt_client.get_topic(self.name)


class SubscriptionClient(ReceiveClientMixin, mixins.BaseClient):
    """A subscription client.

    The SubscriptionClient class defines a high level interface for receiving
    messages to an Azure Service Bus Subscription.
    If you do not wish to perform management operations, a SubscriptionClient can be
    instantiated directly to perform receive operations from a Subscription.

    :param address: The full URI of the Service Bus namespace. This can optionally
        include URL-encoded access name and key.
    :type address: str
    :param name: The name of the topic to which the Client will connect.
    :type name: str
    :param shared_access_key_name: The name of the shared access policy. This must be supplied
     if not encoded into the address.
    :type shared_access_key_name: str
    :param shared_access_key_value: The shared access key. This must be supplied if not encoded
     into the address.
    :type shared_access_key_value: str
    :param debug: Whether to output network trace logs to the logger. Default is `False`.
    :type debug: bool

    .. admonition:: Example:
        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START create_sub_client_directly]
            :end-before: [END create_sub_client_directly]
            :language: python
            :dedent: 8
            :caption: Create a SubscriptionClient.

    """

    def __init__(self, address, name, shared_access_key_name=None,
                 shared_access_key_value=None, debug=False, **kwargs):

        super(SubscriptionClient, self).__init__(
            address, name, shared_access_key_name=shared_access_key_name,
            shared_access_key_value=shared_access_key_value, debug=debug, **kwargs)
        self.topic_name = self.address.path.split("/")[1]

    @classmethod
    def from_connection_string(cls, conn_str, name, topic=None, **kwargs):  # pylint: disable=arguments-differ
        """Create a SubscriptionClient from a connection string.

        :param conn_str: The connection string.
        :type conn_str: str
        :param name: The name of the Subscription.
        :type name: str
        :param topic: The name of the Topic, if the EntityName is
         not included in the connection string.
        :type topic: str
        """
        address, policy, key, entity, transport_type = parse_conn_str(conn_str)
        entity = topic or entity
        address = build_uri(address, entity)
        address += "/Subscriptions/" + name
        return cls(address, name, shared_access_key_name=policy, shared_access_key_value=key, transport_type=transport_type, **kwargs)

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
