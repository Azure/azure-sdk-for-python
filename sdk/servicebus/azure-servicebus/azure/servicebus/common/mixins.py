# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import datetime
import uuid
import requests
try:
    from urlparse import urlparse
    from urllib import unquote_plus
except ImportError:
    from urllib.parse import urlparse
    from urllib.parse import unquote_plus

from uamqp import Source
from uamqp.constants import TransportType

import azure.common
import azure.servicebus
from azure.servicebus.common.constants import (
    NEXT_AVAILABLE,
    SESSION_LOCKED_UNTIL,
    DATETIMEOFFSET_EPOCH,
    SESSION_FILTER)
from azure.servicebus.common.utils import parse_conn_str, build_uri
from azure.servicebus.common.errors import (
    ServiceBusConnectionError,
    ServiceBusResourceNotFound)
from azure.servicebus.control_client import ServiceBusService
from azure.servicebus.control_client.models import AzureServiceBusResourceNotFound, Queue, Subscription, Topic


class ServiceBusMixin(object):

    def _get_host(self):
        return "sb://" + self.service_namespace + self.host_base

    def create_queue(
            self, queue_name,
            lock_duration=30, max_size_in_megabytes=None,
            requires_duplicate_detection=False,
            requires_session=False,
            default_message_time_to_live=None,
            dead_lettering_on_message_expiration=False,
            duplicate_detection_history_time_window=None,
            max_delivery_count=None, enable_batched_operations=None):
        """Create a queue entity.

        :param queue_name: The name of the new queue.
        :type queue_name: str
        :param lock_duration: The lock durection in seconds for each message in the queue.
        :type lock_duration: int
        :param max_size_in_megabytes: The max size to allow the queue to grow to.
        :type max_size_in_megabytes: int
        :param requires_duplicate_detection: Whether the queue will require every message with
         a specified time frame to have a unique ID. Non-unique messages will be discarded.
         Default value is False.
        :type requires_duplicate_detection: bool
        :param requires_session: Whether the queue will be sessionful, and therefore require all
         message to have a Session ID and be received by a sessionful receiver.
         Default value is False.
        :type requires_session: bool
        :param default_message_time_to_live: The length of time a message will remain in the queue
         before it is either discarded or moved to the dead letter queue.
        :type default_message_time_to_live: ~datetime.timedelta
        :param dead_lettering_on_message_expiration: Whether to move expired messages to the
         dead letter queue. Default value is False.
        :type dead_lettering_on_message_expiration: bool
        :param duplicate_detection_history_time_window: The period within which all incoming messages
         must have a unique message ID.
        :type duplicate_detection_history_time_window: ~datetime.timedelta
        :param max_delivery_count: The maximum number of times a message will attempt to be delivered
         before it is moved to the dead letter queue.
        :type max_delivery_count: int
        :param enable_batched_operations:
        :type: enable_batched_operations: bool
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.common.AzureConflictHttpError if a queue of the same name already exists.
        """
        queue_properties = Queue(
            lock_duration="PT{}S".format(int(lock_duration)),
            max_size_in_megabytes=max_size_in_megabytes,
            requires_duplicate_detection=requires_duplicate_detection,
            requires_session=requires_session,
            default_message_time_to_live=default_message_time_to_live,
            dead_lettering_on_message_expiration=dead_lettering_on_message_expiration,
            duplicate_detection_history_time_window=duplicate_detection_history_time_window,
            max_delivery_count=max_delivery_count,
            enable_batched_operations=enable_batched_operations)
        try:
            return self.mgmt_client.create_queue(queue_name, queue=queue_properties, fail_on_exist=True)
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)

    def delete_queue(self, queue_name, fail_not_exist=False):
        """Delete a queue entity.

        :param queue_name: The name of the queue to delete.
        :type queue_name: str
        :param fail_not_exist: Whether to raise an exception if the named queue is not
         found. If set to True, a ServiceBusResourceNotFound will be raised.
         Default value is False.
        :type fail_not_exist: bool
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namesapce is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the queue is not found
         and `fail_not_exist` is set to True.
        """
        try:
            return self.mgmt_client.delete_queue(queue_name, fail_not_exist=fail_not_exist)
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)
        except azure.common.AzureMissingResourceHttpError as e:
            raise ServiceBusResourceNotFound("Specificed queue '{}' does not exist.".format(queue_name), e)

    def create_topic(
            self, topic_name,
            default_message_time_to_live=None,
            max_size_in_megabytes=None, requires_duplicate_detection=None,
            duplicate_detection_history_time_window=None,
            enable_batched_operations=None):
        """Create a topic entity.

        :param topic_name: The name of the new topic.
        :type topic_name: str
        :param max_size_in_megabytes: The max size to allow the topic to grow to.
        :type max_size_in_megabytes: int
        :param requires_duplicate_detection: Whether the topic will require every message with
         a specified time frame to have a unique ID. Non-unique messages will be discarded.
         Default value is False.
        :type requires_duplicate_detection: bool
        :param default_message_time_to_live: The length of time a message will remain in the topic
         before it is either discarded or moved to the dead letter queue.
        :type default_message_time_to_live: ~datetime.timedelta
        :param duplicate_detection_history_time_window: The period within which all incoming messages
         must have a unique message ID.
        :type duplicate_detection_history_time_window: ~datetime.timedelta
        :param enable_batched_operations:
        :type: enable_batched_operations: bool
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.common.AzureConflictHttpError if a topic of the same name already exists.
        """
        topic_properties = Topic(
            max_size_in_megabytes=max_size_in_megabytes,
            requires_duplicate_detection=requires_duplicate_detection,
            default_message_time_to_live=default_message_time_to_live,
            duplicate_detection_history_time_window=duplicate_detection_history_time_window,
            enable_batched_operations=enable_batched_operations)
        try:
            return self.mgmt_client.create_topic(topic_name, topic=topic_properties, fail_on_exist=True)
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)

    def delete_topic(self, topic_name, fail_not_exist=False):
        """Delete a topic entity.

        :param topic_name: The name of the topic to delete.
        :type topic_name: str
        :param fail_not_exist: Whether to raise an exception if the named topic is not
         found. If set to True, a ServiceBusResourceNotFound will be raised.
         Default value is False.
        :type fail_not_exist: bool
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namesapce is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the topic is not found
         and `fail_not_exist` is set to True.
        """
        try:
            return self.mgmt_client.delete_topic(topic_name, fail_not_exist=fail_not_exist)
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)
        except azure.common.AzureMissingResourceHttpError as e:
            raise ServiceBusResourceNotFound("Specificed queue does not exist.", e)

    def create_subscription(
            self, topic_name, subscription_name,
            lock_duration=30, requires_session=None,
            default_message_time_to_live=None,
            dead_lettering_on_message_expiration=None,
            dead_lettering_on_filter_evaluation_exceptions=None,
            enable_batched_operations=None, max_delivery_count=None):
        """Create a subscription entity.

        :param topic_name: The name of the topic under which to create the subscription.
        :param subscription_name: The name of the new subscription.
        :type subscription_name: str
        :param lock_duration: The lock durection in seconds for each message in the subscription.
        :type lock_duration: int
        :param requires_session: Whether the subscription will be sessionful, and therefore require all
         message to have a Session ID and be received by a sessionful receiver.
         Default value is False.
        :type requires_session: bool
        :param default_message_time_to_live: The length of time a message will remain in the subscription
         before it is either discarded or moved to the dead letter queue.
        :type default_message_time_to_live: ~datetime.timedelta
        :param dead_lettering_on_message_expiration: Whether to move expired messages to the
         dead letter queue. Default value is False.
        :type dead_lettering_on_message_expiration: bool
        :param dead_lettering_on_filter_evaluation_exceptions: Whether to move messages that error on
         filtering into the dead letter queue. Default is False, and the messages will be discarded.
        :type dead_lettering_on_filter_evaluation_exceptions: bool
        :param max_delivery_count: The maximum number of times a message will attempt to be delivered
         before it is moved to the dead letter queue.
        :type max_delivery_count: int
        :param enable_batched_operations:
        :type: enable_batched_operations: bool
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namespace is not found.
        :raises: ~azure.common.AzureConflictHttpError if a queue of the same name already exists.
        """
        sub_properties = Subscription(
            lock_duration="PT{}S".format(int(lock_duration)),
            requires_session=requires_session,
            default_message_time_to_live=default_message_time_to_live,
            dead_lettering_on_message_expiration=dead_lettering_on_message_expiration,
            dead_lettering_on_filter_evaluation_exceptions=dead_lettering_on_filter_evaluation_exceptions,
            max_delivery_count=max_delivery_count,
            enable_batched_operations=enable_batched_operations)
        try:
            return self.mgmt_client.create_subscription(
                topic_name, subscription_name,
                subscription=sub_properties, fail_on_exist=True)
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)

    def delete_subscription(self, topic_name, subscription_name, fail_not_exist=False):
        """Delete a subscription entity.

        :param topic_name: The name of the topic where the subscription is.
        :type topic_name: str
        :param subscription_name: The name of the subscription to delete.
        :type subscription_name: str
        :param fail_not_exist: Whether to raise an exception if the named subscription or
         topic is not found. If set to True, a ServiceBusResourceNotFound will be raised.
         Default value is False.
        :type fail_not_exist: bool
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the namesapce is not found.
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the entity is not found
         and `fail_not_exist` is set to True.
        """
        try:
            return self.mgmt_client.delete_subscription(
                topic_name, subscription_name, fail_not_exist=fail_not_exist)
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace: {} not found".format(self.service_namespace), e)
        except azure.common.AzureMissingResourceHttpError as e:
            raise ServiceBusResourceNotFound("Specificed queue does not exist.", e)


class BaseClient(object):  # pylint: disable=too-many-instance-attributes

    def __init__(self, address, name, shared_access_key_name=None,
                 shared_access_key_value=None, debug=False, **kwargs):
        """Construct a new Client to interact with the named Service Bus entity.

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
        self.container_id = "servicebus.pysdk-" + str(uuid.uuid4())[:8]
        self.address = urlparse(address)
        self.name = name
        self.debug = debug
        self.encoding = 'UTF-8'
        self.connection = None
        self.entity = kwargs.get('validated_entity')
        self.properties = dict(self.entity) if self.entity else {}
        self.requires_session = self.properties.get('requires_session', False)

        namespace, _, host_base = self.address.hostname.partition('.')
        url_username = unquote_plus(self.address.username) if self.address.username else None
        shared_access_key_name = shared_access_key_name or url_username
        url_password = unquote_plus(self.address.password) if self.address.password else None
        shared_access_key_value = shared_access_key_value or url_password
        if not shared_access_key_name or not shared_access_key_value:
            raise ValueError("Missing shared access key name and/or value.")
        self.entity_uri = "amqps://{}{}".format(self.address.hostname, self.address.path)
        self.auth_config = {
            'uri': "sb://{}{}".format(self.address.hostname, self.address.path),
            'key_name': shared_access_key_name,
            'shared_access_key': shared_access_key_value}

        self.auth_config['transport_type'] = kwargs.get('transport_type') or TransportType.Amqp

        self.mgmt_client = kwargs.get('mgmt_client') or ServiceBusService(
            service_namespace=namespace,
            shared_access_key_name=shared_access_key_name,
            shared_access_key_value=shared_access_key_value,
            host_base="." + host_base)

    @classmethod
    def from_entity(cls, address, entity, **kwargs):
        client = cls(
            address + "/" + entity.name,
            entity.name,
            validated_entity=entity,
            **kwargs)
        return client

    @classmethod
    def from_connection_string(cls, conn_str, name=None, **kwargs):
        """Create a Client from a Service Bus connection string.

        :param conn_str: The connection string.
        :type conn_str: str
        :param name: The name of the entity, if the 'EntityName' property is
         not included in the connection string.
        """
        address, policy, key, entity, transport_type = parse_conn_str(conn_str)
        entity = name or entity
        address = build_uri(address, entity)
        name = address.split('/')[-1]
        return cls(address, name, shared_access_key_name=policy, shared_access_key_value=key, transport_type=transport_type, **kwargs)

    def _get_entity(self):
        raise NotImplementedError("Must be implemented by child class.")

    def get_properties(self):
        """Perform an operation to update the properties of the entity.

        :returns: The properties of the entity as a dictionary.
        :rtype: dict[str, Any]
        :raises: ~azure.servicebus.common.errors.ServiceBusResourceNotFound if the entity does not exist.
        :raises: ~azure.servicebus.common.errors.ServiceBusConnectionError if the endpoint cannot be reached.
        :raises: ~azure.common.AzureHTTPError if the credentials are invalid.
        """
        try:
            self.entity = self._get_entity()
            self.properties = dict(self.entity)
            if hasattr(self.entity, 'requires_session'):
                self.requires_session = self.entity.requires_session
            return self.properties
        except AzureServiceBusResourceNotFound:
            raise ServiceBusResourceNotFound("Specificed queue does not exist.")
        except azure.common.AzureHttpError:
            self.entity = None
            self.properties = {}
            self.requires_session = False
        except requests.exceptions.ConnectionError as e:
            raise ServiceBusConnectionError("Namespace not found", e)


class SessionMixin(object):  # pylint: disable=too-few-public-methods

    def _get_source(self):
        source = Source(self.endpoint)
        session_filter = None if self.session_filter == NEXT_AVAILABLE else self.session_filter
        source.set_filter(session_filter, name=SESSION_FILTER, descriptor=None)
        return source

    def _on_attach(self, source, target, properties, error):  # pylint: disable=unused-argument
        if str(source) == self.endpoint:
            self.session_start = datetime.datetime.now()
            expiry_in_seconds = properties.get(SESSION_LOCKED_UNTIL)
            if expiry_in_seconds:
                expiry_in_seconds = (expiry_in_seconds - DATETIMEOFFSET_EPOCH)/10000000
                self.locked_until = datetime.datetime.fromtimestamp(expiry_in_seconds)
            session_filter = source.get_filter(name=SESSION_FILTER)
            self.session_id = session_filter.decode(self.encoding)

    @property
    def expired(self):
        """Whether the receivers lock on a particular session has expired.

        :rtype: bool
        """
        if self.locked_until and self.locked_until <= datetime.datetime.now():
            return True
        return False


class SenderMixin(object):  # pylint: disable=too-few-public-methods

    def _build_schedule_request(self, schedule_time, *messages):
        request_body = {'messages': []}
        for message in messages:
            message.schedule(schedule_time)
            if self.session_id and not message.properties.group_id:
                message.properties.group_id = self.session_id
            message_data = {}
            message_data['message-id'] = message.properties.message_id
            if message.properties.group_id:
                message_data['session-id'] = message.properties.group_id
            if message.partition_key:
                message_data['partition-key'] = message.partition_key
            if message.via_partition_key:
                message_data['via-partition-key'] = message.via_partition_key
            message_data['message'] = bytearray(message.message.encode_message())
            request_body['messages'].append(message_data)
        return request_body

    def queue_message(self, message):
        """Queue a message to be sent later.

        This operation should be followed up with send_pending_messages.

        :param message: The message to be sent.
        :type message: ~azure.servicebus.common.message.Message

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START queue_and_send_messages]
                :end-before: [END queue_and_send_messages]
                :language: python
                :dedent: 4
                :caption: Send the queued messages
                :name: sender_queue

        """
        if not self.running:
            self.open()
        if self.session_id and not message.properties.group_id:
            message.properties.group_id = self.session_id
        self._handler.queue_message(message.message)
