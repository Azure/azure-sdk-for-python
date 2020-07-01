# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
from collections import OrderedDict
from copy import deepcopy
from typing import Type, Dict
from msrest.serialization import Model

from ._generated.models import QueueDescription as InternalQueueDescription, \
    TopicDescription as InternalTopicDescription, \
    SubscriptionDescription as InternalSubscriptionDescription, \
    RuleDescription as InternalRuleDescription, \
    SqlRuleAction as InternalSqlRuleAction, \
    EmptyRuleAction as InternalEmptyRuleAction, \
    CorrelationFilter as InternalCorrelationFilter, \
    SqlFilter as InternalSqlFilter, TrueFilter as InternalTrueFilter, FalseFilter as InternalFalseFilter, \
    KeyValue

from ._model_workaround import adjust_attribute_map

adjust_attribute_map()


class QueueDescription(object):  # pylint:disable=too-many-instance-attributes
    """Description of a Service Bus queue resource.

    :param name: Name of the queue.
    :type name: str
    :keyword authorization_rules: Authorization rules for resource.
    :type authorization_rules: list[~azure.servicebus.management.AuthorizationRule]
    :keyword auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the queue is
     automatically deleted. The minimum duration is 5 minutes.
    :type auto_delete_on_idle: ~datetime.timedelta
    :keyword dead_lettering_on_message_expiration: A value that indicates whether this queue has dead
     letter support when a message expires.
    :type dead_lettering_on_message_expiration: bool
    :keyword default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :type default_message_time_to_live: ~datetime.timedelta
    :keyword duplicate_detection_history_time_window: ISO 8601 timeSpan structure that defines the
     duration of the duplicate detection history. The default value is 10 minutes.
    :type duplicate_detection_history_time_window: ~datetime.timedelta
    :keyword entity_availability_status: Availibility status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type entity_availability_status: str or
     ~azure.servicebus.management.EntityAvailabilityStatus
    :keyword enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :type enable_batched_operations: bool
    :keyword enable_express: A value that indicates whether Express Entities are enabled. An express
     queue holds a message in memory temporarily before writing it to persistent storage.
    :type enable_express: bool
    :keyword enable_partitioning: A value that indicates whether the queue is to be partitioned
     across multiple message brokers.
    :type enable_partitioning: bool
    :keyword is_anonymous_accessible: A value indicating if the resource can be accessed without
     authorization.
    :type is_anonymous_accessible: bool
    :keyword lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
     that the message is locked for other receivers. The maximum value for LockDuration is 5
     minutes; the default value is 1 minute.
    :type lock_duration: ~datetime.timedelta
    :keyword max_delivery_count: The maximum delivery count. A message is automatically deadlettered
     after this number of deliveries. Default value is 10.
    :type max_delivery_count: int
    :keyword max_size_in_megabytes: The maximum size of the queue in megabytes, which is the size of
     memory allocated for the queue.
    :type max_size_in_megabytes: int
    :keyword requires_duplicate_detection: A value indicating if this queue requires duplicate
     detection.
    :type requires_duplicate_detection: bool
    :keyword requires_session: A value that indicates whether the queue supports the concept of
     sessions.
    :type requires_session: bool
    :keyword status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :type status: str or ~azure.servicebus.management.EntityStatus
    :keyword forward_to: The name of the recipient entity to which all the messages sent to the queue
     are forwarded to.
    :type forward_to: str
    :keyword user_metadata: Custom metdata that user can associate with the description. Max length
     is 1024 chars.
    :type user_metadata: str
    :keyword support_ordering: A value that indicates whether the queue supports ordering.
    :type support_ordering: bool
    :keyword forward_dead_lettered_messages_to: The name of the recipient entity to which all the
     dead-lettered messages of this subscription are forwarded to.
    :type forward_dead_lettered_messages_to: str
    """

    def __init__(
        self,
        name,
        **kwargs
    ):
        self.name = name
        self._internal_qd = None

        self.authorization_rules = kwargs.get('authorization_rules', None)
        self.auto_delete_on_idle = kwargs.get('auto_delete_on_idle', None)
        self.dead_lettering_on_message_expiration = kwargs.get('dead_lettering_on_message_expiration', None)
        self.default_message_time_to_live = kwargs.get('default_message_time_to_live', None)
        self.duplicate_detection_history_time_window = kwargs.get('duplicate_detection_history_time_window', None)
        self.entity_availability_status = kwargs.get('entity_availability_status', None)
        self.enable_batched_operations = kwargs.get('enable_batched_operations', None)
        self.enable_express = kwargs.get('enable_express', None)
        self.enable_partitioning = kwargs.get('enable_partitioning', None)
        self.is_anonymous_accessible = kwargs.get('is_anonymous_accessible', None)
        self.lock_duration = kwargs.get('lock_duration', None)
        self.max_delivery_count = kwargs.get('max_delivery_count', None)
        self.max_size_in_megabytes = kwargs.get('max_size_in_megabytes', None)
        self.requires_duplicate_detection = kwargs.get('requires_duplicate_detection', None)
        self.requires_session = kwargs.get('requires_session', None)
        self.status = kwargs.get('status', None)
        self.support_ordering = kwargs.get('support_ordering', None)
        self.forward_to = kwargs.get('forward_to', None)
        self.user_metadata = kwargs.get('user_metadata', None)
        self.forward_dead_lettered_messages_to = kwargs.get('forward_dead_lettered_messages_to', None)


    @classmethod
    def _from_internal_entity(cls, name, internal_qd):
        # type: (str, InternalQueueDescription) -> QueueDescription
        qd = cls(name)
        qd._internal_qd = deepcopy(internal_qd)  # pylint:disable=protected-access

        qd.authorization_rules = internal_qd.authorization_rules
        qd.auto_delete_on_idle = internal_qd.auto_delete_on_idle
        qd.dead_lettering_on_message_expiration = internal_qd.dead_lettering_on_message_expiration
        qd.default_message_time_to_live = internal_qd.default_message_time_to_live
        qd.duplicate_detection_history_time_window = internal_qd.duplicate_detection_history_time_window
        qd.entity_availability_status = internal_qd.entity_availability_status
        qd.enable_batched_operations = internal_qd.enable_batched_operations
        qd.enable_express = internal_qd.enable_express
        qd.enable_partitioning = internal_qd.enable_partitioning
        qd.is_anonymous_accessible = internal_qd.is_anonymous_accessible
        qd.lock_duration = internal_qd.lock_duration
        qd.max_delivery_count = internal_qd.max_delivery_count
        qd.max_size_in_megabytes = internal_qd.max_size_in_megabytes
        qd.requires_duplicate_detection = internal_qd.requires_duplicate_detection
        qd.requires_session = internal_qd.requires_session
        qd.status = internal_qd.status
        qd.support_ordering = internal_qd.support_ordering
        qd.forward_to = internal_qd.forward_to
        qd.forward_dead_lettered_messages_to = internal_qd.forward_dead_lettered_messages_to
        qd.user_metadata = internal_qd.user_metadata

        return qd

    def _to_internal_entity(self):
        if not self._internal_qd:
            internal_qd = InternalQueueDescription()
            self._internal_qd = internal_qd

        self._internal_qd.authorization_rules = self.authorization_rules
        self._internal_qd.auto_delete_on_idle = self.auto_delete_on_idle
        self._internal_qd.dead_lettering_on_message_expiration = self.dead_lettering_on_message_expiration
        self._internal_qd.default_message_time_to_live = self.default_message_time_to_live
        self._internal_qd.duplicate_detection_history_time_window = self.duplicate_detection_history_time_window
        self._internal_qd.entity_availability_status = self.entity_availability_status
        self._internal_qd.enable_batched_operations = self.enable_batched_operations
        self._internal_qd.enable_express = self.enable_express
        self._internal_qd.enable_partitioning = self.enable_partitioning
        self._internal_qd.is_anonymous_accessible = self.is_anonymous_accessible
        self._internal_qd.lock_duration = self.lock_duration
        self._internal_qd.max_delivery_count = self.max_delivery_count
        self._internal_qd.max_size_in_megabytes = self.max_size_in_megabytes
        self._internal_qd.requires_duplicate_detection = self.requires_duplicate_detection
        self._internal_qd.requires_session = self.requires_session
        self._internal_qd.status = self.status
        self._internal_qd.support_ordering = self.support_ordering
        self._internal_qd.forward_to = self.forward_to
        self._internal_qd.forward_dead_lettered_messages_to = self.forward_dead_lettered_messages_to
        self._internal_qd.user_metadata = self.user_metadata

        return self._internal_qd


class QueueRuntimeInfo(object):
    """Service Bus queue metrics.

    :ivar name: Name of the queue.
    :type name: str
    :ivar accessed_at: Last time a message was sent, or the last time there was a receive request
     to this queue.
    :type accessed_at: ~datetime.datetime
    :ivar created_at: The exact time the queue was created.
    :type created_at: ~datetime.datetime
    :ivar updated_at: The exact time a message was updated in the queue.
    :type updated_at: ~datetime.datetime
    :ivar size_in_bytes: The size of the queue, in bytes.
    :type size_in_bytes: int
    :ivar message_count: The number of messages in the queue.
    :type message_count: int
    :ivar message_count_details: Details about the message counts in entity.
    :type message_count_details: ~azure.servicebus.management.MessageCountDetails
    """

    def __init__(
        self,
        name,
        **kwargs
    ):
        self.name = name
        self._internal_qr = None

        self.accessed_at = kwargs.get('accessed_at', None)
        self.created_at = kwargs.get('created_at', None)
        self.updated_at = kwargs.get('updated_at', None)
        self.size_in_bytes = kwargs.get('size_in_bytes', None)
        self.message_count = kwargs.get('message_count', None)
        self.message_count_details = kwargs.get('message_count_details', None)

    @classmethod
    def _from_internal_entity(cls, name, internal_qr):
        # type: (str, InternalQueueDescription) -> QueueRuntimeInfo
        qr = cls(name)
        qr._internal_qr = deepcopy(internal_qr)  # pylint:disable=protected-access

        qr.accessed_at = internal_qr.accessed_at
        qr.created_at = internal_qr.created_at
        qr.updated_at = internal_qr.updated_at
        qr.size_in_bytes = internal_qr.size_in_bytes
        qr.message_count = internal_qr.message_count
        qr.message_count_details = internal_qr.message_count_details

        return qr


class TopicDescription(object):  # pylint:disable=too-many-instance-attributes
    """Description of a Service Bus topic resource.

    :param name: Name of the topic.
    :type name: str
    :keyword default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :type default_message_time_to_live: ~datetime.timedelta
    :keyword max_size_in_megabytes: The maximum size of the topic in megabytes, which is the size of
     memory allocated for the topic.
    :type max_size_in_megabytes: long
    :keyword requires_duplicate_detection: A value indicating if this topic requires duplicate
     detection.
    :type requires_duplicate_detection: bool
    :keyword duplicate_detection_history_time_window: ISO 8601 timeSpan structure that defines the
     duration of the duplicate detection history. The default value is 10 minutes.
    :type duplicate_detection_history_time_window: ~datetime.timedelta
    :keyword enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :type enable_batched_operations: bool
    :keyword size_in_bytes: The size of the topic, in bytes.
    :type size_in_bytes: int
    :keyword filtering_messages_before_publishing: Filter messages before publishing.
    :type filtering_messages_before_publishing: bool
    :keyword is_anonymous_accessible: A value indicating if the resource can be accessed without
     authorization.
    :type is_anonymous_accessible: bool
    :keyword authorization_rules: Authorization rules for resource.
    :type authorization_rules:
     list[~azure.servicebus.management._generated.models.AuthorizationRule]
    :keyword status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :type status: str or ~azure.servicebus.management._generated.models.EntityStatus
    :keyword support_ordering: A value that indicates whether the topic supports ordering.
    :type support_ordering: bool
    :keyword auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the topic is
     automatically deleted. The minimum duration is 5 minutes.
    :type auto_delete_on_idle: ~datetime.timedelta
    :keyword enable_partitioning: A value that indicates whether the topic is to be partitioned
     across multiple message brokers.
    :type enable_partitioning: bool
    :keyword entity_availability_status: Availability status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type entity_availability_status: str or
     ~azure.servicebus.management._generated.models.EntityAvailabilityStatus
    :keyword enable_subscription_partitioning: A value that indicates whether the topic's
     subscription is to be partitioned.
    :type enable_subscription_partitioning: bool
    :keyword enable_express: A value that indicates whether Express Entities are enabled. An express
     queue holds a message in memory temporarily before writing it to persistent storage.
    :type enable_express: bool
    :keyword user_metadata: Metadata associated with the topic.
    :type user_metadata: str
    """
    def __init__(
        self,
        name,
        **kwargs
    ):
        self.name = name
        self._internal_td = None

        self.default_message_time_to_live = kwargs.get('default_message_time_to_live', None)
        self.max_size_in_megabytes = kwargs.get('max_size_in_megabytes', None)
        self.requires_duplicate_detection = kwargs.get('requires_duplicate_detection', None)
        self.duplicate_detection_history_time_window = kwargs.get('duplicate_detection_history_time_window', None)
        self.enable_batched_operations = kwargs.get('enable_batched_operations', None)
        self.size_in_bytes = kwargs.get('size_in_bytes', None)
        self.is_anonymous_accessible = kwargs.get('is_anonymous_accessible', None)
        self.authorization_rules = kwargs.get('authorization_rules', None)
        self.status = kwargs.get('status', None)
        self.support_ordering = kwargs.get('support_ordering', None)
        self.auto_delete_on_idle = kwargs.get('auto_delete_on_idle', None)
        self.enable_partitioning = kwargs.get('enable_partitioning', None)
        self.entity_availability_status = kwargs.get('entity_availability_status', None)
        self.enable_subscription_partitioning = kwargs.get('enable_subscription_partitioning', None)
        self.enable_express = kwargs.get('enable_express', None)
        self.user_metadata = kwargs.get('user_metadata', None)

    @classmethod
    def _from_internal_entity(cls, name, internal_td):
        # type: (str, InternalTopicDescription) -> TopicDescription
        qd = cls(name)
        qd._internal_td = deepcopy(internal_td)

        qd.default_message_time_to_live = internal_td.default_message_time_to_live
        qd.max_size_in_megabytes = internal_td.max_size_in_megabytes
        qd.requires_duplicate_detection = internal_td.requires_duplicate_detection
        qd.duplicate_detection_history_time_window = internal_td.duplicate_detection_history_time_window
        qd.enable_batched_operations = internal_td.enable_batched_operations
        qd.size_in_bytes = internal_td.size_in_bytes
        qd.is_anonymous_accessible = internal_td.is_anonymous_accessible
        qd.authorization_rules = internal_td.authorization_rules
        qd.status = internal_td.status
        qd.support_ordering = internal_td.support_ordering
        qd.auto_delete_on_idle = internal_td.auto_delete_on_idle
        qd.enable_partitioning = internal_td.enable_partitioning
        qd.entity_availability_status = internal_td.entity_availability_status
        qd.enable_subscription_partitioning = internal_td.enable_subscription_partitioning
        qd.enable_express = internal_td.enable_express
        qd.user_metadata = internal_td.user_metadata

        return qd

    def _to_internal_entity(self):
        # type: () -> InternalTopicDescription
        if not self._internal_td:
            self._internal_td = InternalTopicDescription()
        self._internal_td.default_message_time_to_live = self.default_message_time_to_live
        self._internal_td.max_size_in_megabytes = self.max_size_in_megabytes
        self._internal_td.requires_duplicate_detection = self.requires_duplicate_detection
        self._internal_td.duplicate_detection_history_time_window = self.duplicate_detection_history_time_window
        self._internal_td.enable_batched_operations = self.enable_batched_operations
        self._internal_td.size_in_bytes = self.size_in_bytes
        self._internal_td.is_anonymous_accessible = self.is_anonymous_accessible
        self._internal_td.authorization_rules = self.authorization_rules
        self._internal_td.status = self.status
        self._internal_td.support_ordering = self.support_ordering
        self._internal_td.auto_delete_on_idle = self.auto_delete_on_idle
        self._internal_td.enable_partitioning = self.enable_partitioning
        self._internal_td.entity_availability_status = self.entity_availability_status
        self._internal_td.enable_subscription_partitioning = self.enable_subscription_partitioning
        self._internal_td.enable_express = self.enable_express
        self._internal_td.user_metadata = self.user_metadata

        return self._internal_td


class TopicRuntimeInfo(object):
    """Description of a Service Bus topic resource.

    :ivar str name:
    :ivar created_at: The exact time the queue was created.
    :type created_at: ~datetime.datetime
    :ivar updated_at: The exact time a message was updated in the queue.
    :type updated_at: ~datetime.datetime
    :ivar accessed_at: Last time a message was sent, or the last time there was a receive request
     to this queue.
    :type accessed_at: ~datetime.datetime
    :ivar message_count_details: Details about the message counts in queue.
    :type message_count_details: ~azure.servicebus.management._generated.models.MessageCountDetails
    :ivar subscription_count: The number of subscriptions in the topic.
    :type subscription_count: int
    """
    def __init__(
        self,
        name,
        **kwargs
    ):
        self.name = name
        self._internal_td = None
        self.created_at = kwargs.get('created_at', None)
        self.updated_at = kwargs.get('updated_at', None)
        self.accessed_at = kwargs.get('accessed_at', None)
        self.message_count_details = kwargs.get('message_count_details', None)
        self.subscription_count = kwargs.get('subscription_count', None)

    @classmethod
    def _from_internal_entity(cls, name, internal_td):
        # type: (str, InternalTopicDescription) -> TopicRuntimeInfo
        qd = cls(name)
        qd._internal_td = internal_td

        qd.created_at = internal_td.created_at
        qd.updated_at = internal_td.updated_at
        qd.accessed_at = internal_td.accessed_at
        qd.message_count_details = internal_td.message_count_details
        qd.subscription_count = internal_td.subscription_count

        return qd


class SubscriptionDescription(object):  # pylint:disable=too-many-instance-attributes
    """Description of a Service Bus queue resource.

    :param name: Name of the subscription.
    :type name: str
    :keyword lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
     that the message is locked for other receivers. The maximum value for LockDuration is 5
     minutes; the default value is 1 minute.
    :type lock_duration: ~datetime.timedelta
    :keyword requires_session: A value that indicates whether the queue supports the concept of
     sessions.
    :type requires_session: bool
    :keyword default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :type default_message_time_to_live: ~datetime.timedelta
    :keyword dead_lettering_on_message_expiration: A value that indicates whether this subscription
     has dead letter support when a message expires.
    :type dead_lettering_on_message_expiration: bool
    :keyword dead_lettering_on_filter_evaluation_exceptions: A value that indicates whether this
     subscription has dead letter support when a message expires.
    :type dead_lettering_on_filter_evaluation_exceptions: bool
    :keyword max_delivery_count: The maximum delivery count. A message is automatically deadlettered
     after this number of deliveries. Default value is 10.
    :type max_delivery_count: int
    :keyword enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :type enable_batched_operations: bool
    :keyword status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :type status: str or ~azure.servicebus.management._generated.models.EntityStatus
    :keyword forward_to: The name of the recipient entity to which all the messages sent to the
     subscription are forwarded to.
    :type forward_to: str
    :keyword user_metadata: Metadata associated with the subscription. Maximum number of characters
     is 1024.
    :type user_metadata: str
    :keyword forward_dead_lettered_messages_to: The name of the recipient entity to which all the
     messages sent to the subscription are forwarded to.
    :type forward_dead_lettered_messages_to: str
    :keyword auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the subscription is
     automatically deleted. The minimum duration is 5 minutes.
    :type auto_delete_on_idle: ~datetime.timedelta
    :keyword entity_availability_status: Availability status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type entity_availability_status: str or
     ~azure.servicebus.management._generated.models.EntityAvailabilityStatus
    """
    def __init__(self, name, **kwargs):
        self.name = name
        self._internal_sd = None

        self.lock_duration = kwargs.get('lock_duration', None)
        self.requires_session = kwargs.get('requires_session', None)
        self.default_message_time_to_live = kwargs.get('default_message_time_to_live', None)
        self.dead_lettering_on_message_expiration = kwargs.get('dead_lettering_on_message_expiration', None)
        self.dead_lettering_on_filter_evaluation_exceptions = kwargs.get(
            'dead_lettering_on_filter_evaluation_exceptions', None)
        self.max_delivery_count = kwargs.get('max_delivery_count', None)
        self.enable_batched_operations = kwargs.get('enable_batched_operations', None)
        self.status = kwargs.get('status', None)
        self.forward_to = kwargs.get('forward_to', None)
        self.user_metadata = kwargs.get('user_metadata', None)
        self.forward_dead_lettered_messages_to = kwargs.get('forward_dead_lettered_messages_to', None)
        self.auto_delete_on_idle = kwargs.get('auto_delete_on_idle', None)
        self.entity_availability_status = kwargs.get('entity_availability_status', None)

    @classmethod
    def _from_internal_entity(cls, name, internal_subscription):
        # type: (str, InternalSubscriptionDescription) -> SubscriptionDescription
        subscription = cls(name)
        subscription._internal_sd = deepcopy(internal_subscription)
        subscription.lock_duration = internal_subscription.lock_duration
        subscription.requires_session = internal_subscription.requires_session
        subscription.default_message_time_to_live = internal_subscription.default_message_time_to_live
        subscription.dead_lettering_on_message_expiration = internal_subscription.dead_lettering_on_message_expiration
        subscription.dead_lettering_on_filter_evaluation_exceptions = \
            internal_subscription.dead_lettering_on_filter_evaluation_exceptions
        subscription.max_delivery_count = internal_subscription.max_delivery_count
        subscription.enable_batched_operations = internal_subscription.enable_batched_operations
        subscription.status = internal_subscription.status
        subscription.forward_to = internal_subscription.forward_to
        subscription.user_metadata = internal_subscription.user_metadata
        subscription.forward_dead_lettered_messages_to = internal_subscription.forward_dead_lettered_messages_to
        subscription.auto_delete_on_idle = internal_subscription.auto_delete_on_idle
        subscription.entity_availability_status = internal_subscription.entity_availability_status

        return subscription

    def _to_internal_entity(self):
        # type: () -> InternalSubscriptionDescription
        if not self._internal_sd:
            self._internal_sd = InternalSubscriptionDescription()
        self._internal_sd.lock_duration = self.lock_duration
        self._internal_sd.requires_session = self.requires_session
        self._internal_sd.default_message_time_to_live = self.default_message_time_to_live
        self._internal_sd.dead_lettering_on_message_expiration = self.dead_lettering_on_message_expiration
        self._internal_sd.dead_lettering_on_filter_evaluation_exceptions = \
            self.dead_lettering_on_filter_evaluation_exceptions
        self._internal_sd.max_delivery_count = self.max_delivery_count
        self._internal_sd.enable_batched_operations = self.enable_batched_operations
        self._internal_sd.status = self.status
        self._internal_sd.forward_to = self.forward_to
        self._internal_sd.user_metadata = self.user_metadata
        self._internal_sd.forward_dead_lettered_messages_to = self.forward_dead_lettered_messages_to
        self._internal_sd.auto_delete_on_idle = self.auto_delete_on_idle
        self._internal_sd.entity_availability_status = self.entity_availability_status

        return self._internal_sd


class SubscriptionRuntimeInfo(object):
    """Description of a Service Bus queue resource.

    :ivar str name:
    :ivar created_at: The exact time the queue was created.
    :type created_at: ~datetime.datetime
    :ivar updated_at: The exact time a message was updated in the queue.
    :type updated_at: ~datetime.datetime
    :ivar accessed_at: Last time a message was sent, or the last time there was a receive request
     to this queue.
    :type accessed_at: ~datetime.datetime
    :ivar message_count: The number of messages in the subscription.
    :type message_count: int
    :ivar message_count_details: Details about the message counts in queue.
    :type message_count_details: ~azure.servicebus.management._generated.models.MessageCountDetails

    """
    def __init__(self, name, **kwargs):
        self._internal_sd = None
        self.name = name

        self.message_count = kwargs.get('message_count', None)
        self.created_at = kwargs.get('created_at', None)
        self.updated_at = kwargs.get('updated_at', None)
        self.accessed_at = kwargs.get('accessed_at', None)
        self.message_count_details = kwargs.get('message_count_details', None)

    @classmethod
    def _from_internal_entity(cls, name, internal_subscription):
        # type: (str, InternalSubscriptionDescription) -> SubscriptionRuntimeInfo
        subscription = cls(name)
        subscription._internal_sd = internal_subscription
        subscription.message_count = internal_subscription.message_count
        subscription.created_at = internal_subscription.created_at
        subscription.updated_at = internal_subscription.updated_at
        subscription.accessed_at = internal_subscription.accessed_at
        subscription.message_count_details = internal_subscription.message_count_details

        return subscription


class RuleDescription(object):
    """Description of a topic subscription rule.

    :param name: Name of the rule.
    :type name: str
    :keyword filter: The filter of the rule.
    :type filter: Union[~azure.servicebus.management.models.CorrelationRuleFilter,
     ~azure.servicebus.management.models.SqlRuleFilter]
    :keyword action: The action of the rule.
    :type action: Optional[~azure.servicebus.management.models.SqlRuleAction]
    :keyword created_at: The exact time the rule was created.
    :type created_at: ~datetime.datetime
    """

    def __init__(self, name, **kwargs):
        self.filter = kwargs.get('filter', None)
        self.action = kwargs.get('action', None)
        self.created_at = kwargs.get('created_at', None)
        self.name = name

        self._internal_rule = None

    @classmethod
    def _from_internal_entity(cls, name, internal_rule):
        # type: (str, InternalRuleDescription) -> RuleDescription
        rule = cls(name)
        rule._internal_rule = deepcopy(internal_rule)

        rule.filter = RULE_CLASS_MAPPING[type(internal_rule.filter)]._from_internal_entity(internal_rule.filter) \
            if internal_rule.filter and isinstance(internal_rule.filter, tuple(RULE_CLASS_MAPPING.keys())) else None
        rule.action = RULE_CLASS_MAPPING[type(internal_rule.action)]._from_internal_entity(internal_rule.action) \
            if internal_rule.action and isinstance(internal_rule.action, tuple(RULE_CLASS_MAPPING.keys())) else None
        rule.created_at = internal_rule.created_at
        rule.name = internal_rule.name

        return rule

    def _to_internal_entity(self):
        # type: () -> InternalRuleDescription
        if not self._internal_rule:
            self._internal_rule = InternalRuleDescription()
        self._internal_rule.filter = self.filter._to_internal_entity() if self.filter else TRUE_FILTER
        self._internal_rule.action = self.action._to_internal_entity() if self.action else EMPTY_RULE_ACTION
        self._internal_rule.created_at = self.created_at
        self._internal_rule.name = self.name

        return self._internal_rule


class CorrelationRuleFilter(object):
    def __init__(self, **kwargs):
        self.correlation_id = kwargs.get('correlation_id', None)
        self.message_id = kwargs.get('message_id', None)
        self.to = kwargs.get('to', None)
        self.reply_to = kwargs.get('reply_to', None)
        self.label = kwargs.get('label', None)
        self.session_id = kwargs.get('session_id', None)
        self.reply_to_session_id = kwargs.get('reply_to_session_id', None)
        self.content_type = kwargs.get('content_type', None)
        self.properties = kwargs.get('properties', None)

    @classmethod
    def _from_internal_entity(cls, internal_correlation_filter):
        # type: (InternalCorrelationFilter) -> CorrelationRuleFilter
        correlation_filter = cls()
        correlation_filter.correlation_id = internal_correlation_filter.correlation_id
        correlation_filter.message_id = internal_correlation_filter.message_id
        correlation_filter.to = internal_correlation_filter.to
        correlation_filter.reply_to = internal_correlation_filter.reply_to
        correlation_filter.label = internal_correlation_filter.label
        correlation_filter.session_id = internal_correlation_filter.session_id
        correlation_filter.reply_to_session_id = internal_correlation_filter.reply_to_session_id
        correlation_filter.content_type = internal_correlation_filter.content_type
        correlation_filter.properties = \
            OrderedDict((kv.key, kv.value) for kv in internal_correlation_filter.properties) \
            if internal_correlation_filter.properties else OrderedDict()

        return correlation_filter

    def _to_internal_entity(self):
        internal_entity = InternalCorrelationFilter()
        internal_entity.correlation_id = self.correlation_id

        internal_entity.message_id = self.message_id
        internal_entity.to = self.to
        internal_entity.reply_to = self.reply_to
        internal_entity.label = self.label
        internal_entity.session_id = self.session_id
        internal_entity.reply_to_session_id = self.reply_to_session_id
        internal_entity.content_type = self.content_type
        internal_entity.properties = [KeyValue(key=key, value=value) for key, value in self.properties.items()] \
            if self.properties else None

        return internal_entity


class SqlRuleFilter(object):
    def __init__(self, sql_expression=None):
        self.sql_expression = sql_expression

    @classmethod
    def _from_internal_entity(cls, internal_sql_rule_filter):
        sql_rule_filter = cls()
        sql_rule_filter.sql_expression = internal_sql_rule_filter.sql_expression
        return sql_rule_filter

    def _to_internal_entity(self):
        internal_entity = InternalSqlFilter(sql_expression=self.sql_expression)
        return internal_entity


class TrueRuleFilter(SqlRuleFilter):
    def __init__(self):
        super(TrueRuleFilter, self).__init__("1=1")

    def _to_internal_entity(self):
        internal_entity = InternalTrueFilter()
        return internal_entity


class FalseRuleFilter(SqlRuleFilter):
    def __init__(self):
        super(FalseRuleFilter, self).__init__("1>1")

    def _to_internal_entity(self):
        internal_entity = InternalFalseFilter()
        return internal_entity


class SqlRuleAction(object):
    def __init__(self, sql_expression=None):
        self.sql_expression = sql_expression

    @classmethod
    def _from_internal_entity(cls, internal_sql_rule_action):
        sql_rule_filter = cls(internal_sql_rule_action.sql_expression)
        return sql_rule_filter

    def _to_internal_entity(self):
        return InternalSqlRuleAction(sql_expression=self.sql_expression)


RULE_CLASS_MAPPING = {
    InternalSqlRuleAction: SqlRuleAction,
    # InternalEmptyRuleAction: None,
    InternalCorrelationFilter: CorrelationRuleFilter,
    InternalSqlFilter: SqlRuleFilter,
    InternalTrueFilter: TrueRuleFilter,
    InternalFalseFilter: FalseRuleFilter,
}  # type: Dict[Type[Model], Type]
EMPTY_RULE_ACTION = InternalEmptyRuleAction()
TRUE_FILTER = TrueRuleFilter()
