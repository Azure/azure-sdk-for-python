# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
# pylint:disable=too-many-lines
import functools
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Type, Dict, Any, Union, Optional, List
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
from ._constants import RULE_SQL_COMPATIBILITY_LEVEL

adjust_attribute_map()


def extract_kwarg_template(kwargs, extraction_missing_args, name):
    try:
        return kwargs[name]
    except KeyError:
        extraction_missing_args.append(name)


def validate_extraction_missing_args(extraction_missing_args):
    if extraction_missing_args:
        raise TypeError('__init__() missing {} required keyword arguments: {}'.format(
            len(extraction_missing_args),
            ' and '.join(["'" + e + "'" for e in extraction_missing_args])))


class DictMixin(object):

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        self.__dict__[key] = None

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith('_')})

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith('_')]

    def values(self):
        return [v for k, v in self.__dict__.items() if not k.startswith('_')]

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class QueueProperties(DictMixin):  # pylint:disable=too-many-instance-attributes
    """Properties of a Service Bus queue resource.

    :ivar name: Name of the queue.
    :type name: str
    :ivar authorization_rules: Authorization rules for resource.
    :type authorization_rules: list[~azure.servicebus.management.AuthorizationRule]
    :ivar auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the queue is
     automatically deleted. The minimum duration is 5 minutes.
    :type auto_delete_on_idle: ~datetime.timedelta
    :ivar dead_lettering_on_message_expiration: A value that indicates whether this queue has dead
     letter support when a message expires.
    :type dead_lettering_on_message_expiration: bool
    :ivar default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :type default_message_time_to_live: ~datetime.timedelta
    :ivar duplicate_detection_history_time_window: ISO 8601 timeSpan structure that defines the
     duration of the duplicate detection history. The default value is 10 minutes.
    :type duplicate_detection_history_time_window: ~datetime.timedelta
    :ivar entity_availability_status: Availibility status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type entity_availability_status: str or
     ~azure.servicebus.management.EntityAvailabilityStatus
    :ivar enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :type enable_batched_operations: bool
    :ivar enable_express: A value that indicates whether Express Entities are enabled. An express
     queue holds a message in memory temporarily before writing it to persistent storage.
    :type enable_express: bool
    :ivar enable_partitioning: A value that indicates whether the queue is to be partitioned
     across multiple message brokers.
    :type enable_partitioning: bool
    :ivar is_anonymous_accessible: A value indicating if the resource can be accessed without
     authorization.
    :type is_anonymous_accessible: bool
    :ivar lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
     that the message is locked for other receivers. The maximum value for LockDuration is 5
     minutes; the default value is 1 minute.
    :type lock_duration: ~datetime.timedelta
    :ivar max_delivery_count: The maximum delivery count. A message is automatically deadlettered
     after this number of deliveries. Default value is 10.
    :type max_delivery_count: int
    :ivar max_size_in_megabytes: The maximum size of the queue in megabytes, which is the size of
     memory allocated for the queue.
    :type max_size_in_megabytes: int
    :ivar requires_duplicate_detection: A value indicating if this queue requires duplicate
     detection.
    :type requires_duplicate_detection: bool
    :ivar requires_session: A value that indicates whether the queue supports the concept of
     sessions.
    :type requires_session: bool
    :ivar status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :type status: str or ~azure.servicebus.management.EntityStatus
    :ivar forward_to: The name of the recipient entity to which all the messages sent to the queue
     are forwarded to.
    :type forward_to: str
    :ivar user_metadata: Custom metdata that user can associate with the description. Max length
     is 1024 chars.
    :type user_metadata: str
    :ivar support_ordering: A value that indicates whether the queue supports ordering.
    :type support_ordering: bool
    :ivar forward_dead_lettered_messages_to: The name of the recipient entity to which all the
     dead-lettered messages of this subscription are forwarded to.
    :type forward_dead_lettered_messages_to: str
    """

    def __init__(
        self,
        name,
        **kwargs
    ):
        # type: (str, Any) -> None
        self.name = name
        self._internal_qd = None  # type: Optional[InternalQueueDescription]

        extraction_missing_args = []  # type: List[str]
        extract_kwarg = functools.partial(extract_kwarg_template, kwargs, extraction_missing_args)

        self.authorization_rules = extract_kwarg('authorization_rules')
        self.auto_delete_on_idle = extract_kwarg('auto_delete_on_idle')
        self.dead_lettering_on_message_expiration = extract_kwarg('dead_lettering_on_message_expiration')
        self.default_message_time_to_live = extract_kwarg('default_message_time_to_live')
        self.duplicate_detection_history_time_window = extract_kwarg('duplicate_detection_history_time_window')
        self.entity_availability_status = extract_kwarg('entity_availability_status')
        self.enable_batched_operations = extract_kwarg('enable_batched_operations')
        self.enable_express = extract_kwarg('enable_express')
        self.enable_partitioning = extract_kwarg('enable_partitioning')
        self.is_anonymous_accessible = extract_kwarg('is_anonymous_accessible')
        self.lock_duration = extract_kwarg('lock_duration')
        self.max_delivery_count = extract_kwarg('max_delivery_count')
        self.max_size_in_megabytes = extract_kwarg('max_size_in_megabytes')
        self.requires_duplicate_detection = extract_kwarg('requires_duplicate_detection')
        self.requires_session = extract_kwarg('requires_session')
        self.status = extract_kwarg('status')
        self.support_ordering = extract_kwarg('support_ordering')
        self.forward_to = extract_kwarg('forward_to')
        self.user_metadata = extract_kwarg('user_metadata')
        self.forward_dead_lettered_messages_to = extract_kwarg('forward_dead_lettered_messages_to')

        validate_extraction_missing_args(extraction_missing_args)


    @classmethod
    def _from_internal_entity(cls, name, internal_qd):
        # type: (str, InternalQueueDescription) -> QueueProperties
        qd = cls(
            name,
            authorization_rules=internal_qd.authorization_rules,
            auto_delete_on_idle=internal_qd.auto_delete_on_idle,
            dead_lettering_on_message_expiration=internal_qd.dead_lettering_on_message_expiration,
            default_message_time_to_live=internal_qd.default_message_time_to_live,
            duplicate_detection_history_time_window=internal_qd.duplicate_detection_history_time_window,
            entity_availability_status=internal_qd.entity_availability_status,
            enable_batched_operations=internal_qd.enable_batched_operations,
            enable_express=internal_qd.enable_express,
            enable_partitioning=internal_qd.enable_partitioning,
            is_anonymous_accessible=internal_qd.is_anonymous_accessible,
            lock_duration=internal_qd.lock_duration,
            max_delivery_count=internal_qd.max_delivery_count,
            max_size_in_megabytes=internal_qd.max_size_in_megabytes,
            requires_duplicate_detection=internal_qd.requires_duplicate_detection,
            requires_session=internal_qd.requires_session,
            status=internal_qd.status,
            support_ordering=internal_qd.support_ordering,
            forward_to=internal_qd.forward_to,
            forward_dead_lettered_messages_to=internal_qd.forward_dead_lettered_messages_to,
            user_metadata=internal_qd.user_metadata
        )
        qd._internal_qd = deepcopy(internal_qd)  # pylint:disable=protected-access
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


class QueueRuntimeProperties(object):
    """Service Bus queue runtime properties.
    """
    def __init__(
        self,
    ):
        self._name = None
        self._internal_qr = None  # type: Optional[InternalQueueDescription]

    @classmethod
    def _from_internal_entity(cls, name, internal_qr):
        # type: (str, InternalQueueDescription) -> QueueRuntimeProperties
        qr = cls()
        qr._name = name
        qr._internal_qr = deepcopy(internal_qr)  # pylint:disable=protected-access
        return qr

    @property
    def name(self):
        """Name of the queue.

        :rtype: str
        """
        return self._name

    @property
    def accessed_at(self):
        """Last time a message was sent, or the last time there was a receive request to this queue.

        :rtype:  ~datetime.datetime
        """
        return self._internal_qr.accessed_at

    @property
    def created_at(self):
        """The exact time the queue was created.

        :rtype: ~datetime.datetime
        """
        return self._internal_qr.created_at

    @property
    def updated_at(self):
        """The exact the entity was updated.

        :rtype: ~datetime.datetime
        """
        return self._internal_qr.updated_at

    @property
    def size_in_bytes(self):
        """The size of the queue, in bytes.

        :rtype: int
        """
        return self._internal_qr.size_in_bytes

    @property
    def total_message_count(self):
        """Total number of messages.

        :rtype: int
        """
        return self._internal_qr.message_count

    @property
    def active_message_count(self):
        """Number of active messages in the queue, topic, or subscription.

        :rtype: int
        """
        return self._internal_qr.message_count_details.active_message_count

    @property
    def dead_letter_message_count(self):
        """Number of messages that are dead lettered.

        :rtype: int
        """
        return self._internal_qr.message_count_details.dead_letter_message_count

    @property
    def scheduled_message_count(self):
        """Number of scheduled messages.

        :rtype: int
        """
        return self._internal_qr.message_count_details.scheduled_message_count

    @property
    def transfer_dead_letter_message_count(self):
        """Number of messages transferred into dead letters.

        :rtype: int
        """
        return self._internal_qr.message_count_details.transfer_dead_letter_message_count

    @property
    def transfer_message_count(self):
        """Number of messages transferred to another queue, topic, or subscription.

        :rtype: int
        """
        return self._internal_qr.message_count_details.transfer_message_count


class TopicProperties(DictMixin):  # pylint:disable=too-many-instance-attributes
    """Properties of a Service Bus topic resource.

    :ivar name: Name of the topic.
    :type name: str
    :ivar default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :type default_message_time_to_live: ~datetime.timedelta
    :ivar max_size_in_megabytes: The maximum size of the topic in megabytes, which is the size of
     memory allocated for the topic.
    :type max_size_in_megabytes: long
    :ivar requires_duplicate_detection: A value indicating if this topic requires duplicate
     detection.
    :type requires_duplicate_detection: bool
    :ivar duplicate_detection_history_time_window: ISO 8601 timeSpan structure that defines the
     duration of the duplicate detection history. The default value is 10 minutes.
    :type duplicate_detection_history_time_window: ~datetime.timedelta
    :ivar enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :type enable_batched_operations: bool
    :ivar size_in_bytes: The size of the topic, in bytes.
    :type size_in_bytes: int
    :ivar filtering_messages_before_publishing: Filter messages before publishing.
    :type filtering_messages_before_publishing: bool
    :ivar is_anonymous_accessible: A value indicating if the resource can be accessed without
     authorization.
    :type is_anonymous_accessible: bool
    :ivar authorization_rules: Authorization rules for resource.
    :type authorization_rules:
     list[~azure.servicebus.management.AuthorizationRule]
    :ivar status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :type status: str or ~azure.servicebus.management.EntityStatus
    :ivar support_ordering: A value that indicates whether the topic supports ordering.
    :type support_ordering: bool
    :ivar auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the topic is
     automatically deleted. The minimum duration is 5 minutes.
    :type auto_delete_on_idle: ~datetime.timedelta
    :ivar enable_partitioning: A value that indicates whether the topic is to be partitioned
     across multiple message brokers.
    :type enable_partitioning: bool
    :ivar entity_availability_status: Availability status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type entity_availability_status: str or
     ~azure.servicebus.management.EntityAvailabilityStatus
    :ivar enable_subscription_partitioning: A value that indicates whether the topic's
     subscription is to be partitioned.
    :type enable_subscription_partitioning: bool
    :ivar enable_express: A value that indicates whether Express Entities are enabled. An express
     queue holds a message in memory temporarily before writing it to persistent storage.
    :type enable_express: bool
    :ivar user_metadata: Metadata associated with the topic.
    :type user_metadata: str
    """
    def __init__(
        self,
        name,
        **kwargs
    ):
        # type: (str, Any) -> None
        self.name = name
        self._internal_td = None  # type: Optional[InternalTopicDescription]

        extraction_missing_args = []  # type: List[str]
        extract_kwarg = functools.partial(extract_kwarg_template, kwargs, extraction_missing_args)

        self.default_message_time_to_live = extract_kwarg('default_message_time_to_live')
        self.max_size_in_megabytes = extract_kwarg('max_size_in_megabytes')
        self.requires_duplicate_detection = extract_kwarg('requires_duplicate_detection')
        self.duplicate_detection_history_time_window = extract_kwarg('duplicate_detection_history_time_window')
        self.enable_batched_operations = extract_kwarg('enable_batched_operations')
        self.size_in_bytes = extract_kwarg('size_in_bytes')
        self.is_anonymous_accessible = extract_kwarg('is_anonymous_accessible')
        self.authorization_rules = extract_kwarg('authorization_rules')
        self.status = extract_kwarg('status')
        self.support_ordering = extract_kwarg('support_ordering')
        self.auto_delete_on_idle = extract_kwarg('auto_delete_on_idle')
        self.enable_partitioning = extract_kwarg('enable_partitioning')
        self.entity_availability_status = extract_kwarg('entity_availability_status')
        self.enable_subscription_partitioning = extract_kwarg('enable_subscription_partitioning')
        self.enable_express = extract_kwarg('enable_express')
        self.user_metadata = extract_kwarg('user_metadata')

        validate_extraction_missing_args(extraction_missing_args)

    @classmethod
    def _from_internal_entity(cls, name, internal_td):
        # type: (str, InternalTopicDescription) -> TopicProperties
        td = cls(
            name,
            default_message_time_to_live=internal_td.default_message_time_to_live,
            max_size_in_megabytes=internal_td.max_size_in_megabytes,
            requires_duplicate_detection=internal_td.requires_duplicate_detection,
            duplicate_detection_history_time_window=internal_td.duplicate_detection_history_time_window,
            enable_batched_operations=internal_td.enable_batched_operations,
            size_in_bytes=internal_td.size_in_bytes,
            is_anonymous_accessible=internal_td.is_anonymous_accessible,
            authorization_rules=internal_td.authorization_rules,
            status=internal_td.status,
            support_ordering=internal_td.support_ordering,
            auto_delete_on_idle=internal_td.auto_delete_on_idle,
            enable_partitioning=internal_td.enable_partitioning,
            entity_availability_status=internal_td.entity_availability_status,
            enable_subscription_partitioning=internal_td.enable_subscription_partitioning,
            enable_express=internal_td.enable_express,
            user_metadata=internal_td.user_metadata
        )
        td._internal_td = deepcopy(internal_td)
        return td

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


class TopicRuntimeProperties(object):
    """Runtime properties of a Service Bus topic resource.
    """
    def __init__(
        self,
    ):
        self._name = None
        self._internal_td = None  # type: Optional[InternalTopicDescription]

    @classmethod
    def _from_internal_entity(cls, name, internal_td):
        # type: (str, InternalTopicDescription) -> TopicRuntimeProperties
        qd = cls()
        qd._name = name
        qd._internal_td = internal_td
        return qd

    @property
    def name(self):
        """The name of the topic.

        :rtype: str
        """
        return self._name

    @property
    def accessed_at(self):
        """Last time a message was sent, or the last time there was a receive request

        :rtype: ~datetime.datetime
        """
        return self._internal_td.accessed_at

    @property
    def created_at(self):
        """The exact time the queue was created.

        :rtype: ~datetime.datetime
        """
        return self._internal_td.created_at

    @property
    def updated_at(self):
        """The exact time the entity was updated.

        :rtype: ~datetime.datetime
        """
        return self._internal_td.updated_at

    @property
    def size_in_bytes(self):
        """The current size of the entity in bytes.

        :rtype: int
        """
        return self._internal_td.size_in_bytes

    @property
    def subscription_count(self):
        """The number of subscriptions in the topic.

        :rtype: int
        """
        return self._internal_td.subscription_count

    @property
    def scheduled_message_count(self):
        """Number of scheduled messages.

        :rtype: int
        """
        return self._internal_td.message_count_details.scheduled_message_count


class SubscriptionProperties(DictMixin):  # pylint:disable=too-many-instance-attributes
    """Properties of a Service Bus topic subscription resource.

    :ivar name: Name of the subscription.
    :type name: str
    :ivar lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
     that the message is locked for other receivers. The maximum value for LockDuration is 5
     minutes; the default value is 1 minute.
    :type lock_duration: ~datetime.timedelta
    :ivar requires_session: A value that indicates whether the queue supports the concept of
     sessions.
    :type requires_session: bool
    :ivar default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :type default_message_time_to_live: ~datetime.timedelta
    :ivar dead_lettering_on_message_expiration: A value that indicates whether this subscription
     has dead letter support when a message expires.
    :type dead_lettering_on_message_expiration: bool
    :ivar dead_lettering_on_filter_evaluation_exceptions: A value that indicates whether this
     subscription has dead letter support when a message expires.
    :type dead_lettering_on_filter_evaluation_exceptions: bool
    :ivar max_delivery_count: The maximum delivery count. A message is automatically deadlettered
     after this number of deliveries. Default value is 10.
    :type max_delivery_count: int
    :ivar enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :type enable_batched_operations: bool
    :ivar status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :type status: str or ~azure.servicebus.management.EntityStatus
    :ivar forward_to: The name of the recipient entity to which all the messages sent to the
     subscription are forwarded to.
    :type forward_to: str
    :ivar user_metadata: Metadata associated with the subscription. Maximum number of characters
     is 1024.
    :type user_metadata: str
    :ivar forward_dead_lettered_messages_to: The name of the recipient entity to which all the
     messages sent to the subscription are forwarded to.
    :type forward_dead_lettered_messages_to: str
    :ivar auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the subscription is
     automatically deleted. The minimum duration is 5 minutes.
    :type auto_delete_on_idle: ~datetime.timedelta
    :ivar entity_availability_status: Availability status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type entity_availability_status: str or
     ~azure.servicebus.management.EntityAvailabilityStatus
    """
    def __init__(self, name, **kwargs):
        # type: (str, Any) -> None
        self.name = name
        self._internal_sd = None  # type: Optional[InternalSubscriptionDescription]

        extraction_missing_args = []  # type: List[str]
        extract_kwarg = functools.partial(extract_kwarg_template, kwargs, extraction_missing_args)

        self.lock_duration = extract_kwarg('lock_duration')
        self.requires_session = extract_kwarg('requires_session')
        self.default_message_time_to_live = extract_kwarg('default_message_time_to_live')
        self.dead_lettering_on_message_expiration = extract_kwarg('dead_lettering_on_message_expiration')
        self.dead_lettering_on_filter_evaluation_exceptions = extract_kwarg(
            'dead_lettering_on_filter_evaluation_exceptions')
        self.max_delivery_count = extract_kwarg('max_delivery_count')
        self.enable_batched_operations = extract_kwarg('enable_batched_operations')
        self.status = extract_kwarg('status')
        self.forward_to = extract_kwarg('forward_to')
        self.user_metadata = extract_kwarg('user_metadata')
        self.forward_dead_lettered_messages_to = extract_kwarg('forward_dead_lettered_messages_to')
        self.auto_delete_on_idle = extract_kwarg('auto_delete_on_idle')
        self.entity_availability_status = extract_kwarg('entity_availability_status')

        validate_extraction_missing_args(extraction_missing_args)

    @classmethod
    def _from_internal_entity(cls, name, internal_subscription):
        # type: (str, InternalSubscriptionDescription) -> SubscriptionProperties
        subscription = cls(
            name,
            lock_duration=internal_subscription.lock_duration,
            requires_session=internal_subscription.requires_session,
            default_message_time_to_live=internal_subscription.default_message_time_to_live,
            dead_lettering_on_message_expiration=internal_subscription.dead_lettering_on_message_expiration,
            dead_lettering_on_filter_evaluation_exceptions=
            internal_subscription.dead_lettering_on_filter_evaluation_exceptions,
            max_delivery_count=internal_subscription.max_delivery_count,
            enable_batched_operations=internal_subscription.enable_batched_operations,
            status=internal_subscription.status,
            forward_to=internal_subscription.forward_to,
            user_metadata=internal_subscription.user_metadata,
            forward_dead_lettered_messages_to=internal_subscription.forward_dead_lettered_messages_to,
            auto_delete_on_idle=internal_subscription.auto_delete_on_idle,
            entity_availability_status=internal_subscription.entity_availability_status
        )
        subscription._internal_sd = deepcopy(internal_subscription)
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


class SubscriptionRuntimeProperties(object):
    """Runtime properties of a Service Bus topic subscription resource.

    """
    def __init__(self):
        self._internal_sd = None  # type: Optional[InternalSubscriptionDescription]
        self._name = None

    @classmethod
    def _from_internal_entity(cls, name, internal_subscription):
        # type: (str, InternalSubscriptionDescription) -> SubscriptionRuntimeProperties
        subscription = cls()
        subscription._name = name
        subscription._internal_sd = internal_subscription

        return subscription

    @property
    def name(self):
        """Name of subscription

        :rtype: str
        """
        return self._name

    @property
    def accessed_at(self):
        """Last time a message was sent, or the last time there was a receive request

        :rtype: ~datetime.datetime
        """
        return self._internal_sd.accessed_at

    @property
    def created_at(self):
        """The exact time the subscription was created.

        :rtype: ~datetime.datetime
        """
        return self._internal_sd.created_at

    @property
    def updated_at(self):
        """The exact time the entity is updated.

        :rtype: ~datetime.datetime
        """
        return self._internal_sd.updated_at

    @property
    def total_message_count(self):
        """The number of messages in the subscription.

        :rtype: int
        """
        return self._internal_sd.message_count

    @property
    def active_message_count(self):
        """Number of active messages in the subscription.

        :rtype: int
        """
        return self._internal_sd.message_count_details.active_message_count

    @property
    def dead_letter_message_count(self):
        """Number of messages that are dead lettered.

        :rtype: int
        """
        return self._internal_sd.message_count_details.dead_letter_message_count

    @property
    def transfer_dead_letter_message_count(self):
        """Number of messages transferred into dead letters.

        :rtype: int
        """
        return self._internal_sd.message_count_details.transfer_dead_letter_message_count

    @property
    def transfer_message_count(self):
        """Number of messages transferred to another queue, topic, or subscription.

        :rtype: int
        """
        return self._internal_sd.message_count_details.transfer_message_count


class RuleProperties(DictMixin):
    """Properties of a topic subscription rule.

    :param name: Name of the rule.
    :type name: str
    :ivar filter: The filter of the rule.
    :type filter: Union[~azure.servicebus.management.CorrelationRuleFilter,
     ~azure.servicebus.management.SqlRuleFilter]
    :ivar action: The action of the rule.
    :type action: Optional[~azure.servicebus.management.SqlRuleAction]
    :ivar created_at: The exact time the rule was created.
    :type created_at: ~datetime.datetime
    """

    def __init__(self, name, **kwargs):
        # type: (str, Any) -> None

        self.name = name
        self._internal_rule = None  # type: Optional[InternalRuleDescription]

        extraction_missing_args = []  # type: List[str]
        extract_kwarg = functools.partial(extract_kwarg_template, kwargs, extraction_missing_args)

        self.filter = extract_kwarg('filter')
        self.action = extract_kwarg('action')
        self.created_at = extract_kwarg('created_at')

        validate_extraction_missing_args(extraction_missing_args)

    @classmethod
    def _from_internal_entity(cls, name, internal_rule):
        # type: (str, InternalRuleDescription) -> RuleProperties
        rule = cls(
            name,
            filter=RULE_CLASS_MAPPING[type(internal_rule.filter)]._from_internal_entity(internal_rule.filter)
            if internal_rule.filter and isinstance(internal_rule.filter, tuple(RULE_CLASS_MAPPING.keys())) else None,
            action=RULE_CLASS_MAPPING[type(internal_rule.action)]._from_internal_entity(internal_rule.action)
            if internal_rule.action and isinstance(internal_rule.action, tuple(RULE_CLASS_MAPPING.keys())) else None,
            created_at=internal_rule.created_at
        )
        rule._internal_rule = deepcopy(internal_rule)
        return rule

    def _to_internal_entity(self):
        # type: () -> InternalRuleDescription
        if not self._internal_rule:
            self._internal_rule = InternalRuleDescription()
        self._internal_rule.filter = self.filter._to_internal_entity() if self.filter else TRUE_FILTER  # type: ignore
        self._internal_rule.action = self.action._to_internal_entity() if self.action else EMPTY_RULE_ACTION
        self._internal_rule.created_at = self.created_at
        self._internal_rule.name = self.name

        return self._internal_rule


class CorrelationRuleFilter(object):
    """Represents the correlation filter expression.

    :param correlation_id: Identifier of the correlation.
    :type correlation_id: str
    :param message_id: Identifier of the message.
    :type message_id: str
    :param to: Address to send to.
    :type to: str
    :param reply_to: Address of the queue to reply to.
    :type reply_to: str
    :param label: Application specific label.
    :type label: str
    :param session_id: Session identifier.
    :type session_id: str
    :param reply_to_session_id: Session identifier to reply to.
    :type reply_to_session_id: str
    :param content_type: Content type of the message.
    :type content_type: str
    :param properties: dictionary object for custom filters
    :type properties: dict[str, Union[str, int, float, bool, datetime, timedelta]]
    """
    def __init__(self, **kwargs):
        # type: (Any) -> None
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
        # type: () -> InternalCorrelationFilter
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
    """Represents a filter which is a composition of an expression and an action
    that is executed in the pub/sub pipeline.

    :param sql_expression: The SQL expression. e.g. MyProperty='ABC'
    :type sql_expression: str
    :param parameters: Sets the value of the sql expression parameters if any.
    :type parameters: dict[str, Union[str, int, float, bool, datetime, timedelta]]
    :param requires_preprocessing: Value that indicates whether the rule
     filter requires preprocessing. Default value: True .
    :type requires_preprocessing: bool
    """
    def __init__(self, sql_expression=None, parameters=None, requires_preprocessing=True):
        # type: (Optional[str], Optional[Dict[str, Union[str, int, float, bool, datetime, timedelta]]], bool) -> None
        self.sql_expression = sql_expression
        self.parameters = parameters
        self.requires_preprocessing = requires_preprocessing

    @classmethod
    def _from_internal_entity(cls, internal_sql_rule_filter):
        sql_rule_filter = cls()
        sql_rule_filter.sql_expression = internal_sql_rule_filter.sql_expression
        sql_rule_filter.parameters = OrderedDict((kv.key, kv.value) for kv in internal_sql_rule_filter.parameters) \
            if internal_sql_rule_filter.parameters else OrderedDict()
        sql_rule_filter.requires_preprocessing = internal_sql_rule_filter.requires_preprocessing
        return sql_rule_filter

    def _to_internal_entity(self):
        # type: () -> InternalSqlFilter
        internal_entity = InternalSqlFilter(sql_expression=self.sql_expression)
        internal_entity.parameters = [
            KeyValue(key=key, value=value) for key, value in self.parameters.items()  # type: ignore
        ] if self.parameters else None
        internal_entity.compatibility_level = RULE_SQL_COMPATIBILITY_LEVEL
        internal_entity.requires_preprocessing = self.requires_preprocessing
        return internal_entity


class TrueRuleFilter(SqlRuleFilter):
    """A sql filter with a sql expression that is always True
    """
    def __init__(self):
        super(TrueRuleFilter, self).__init__("1=1", None, True)

    def _to_internal_entity(self):
        internal_entity = InternalTrueFilter()
        internal_entity.sql_expression = self.sql_expression
        internal_entity.requires_preprocessing = True
        internal_entity.compatibility_level = RULE_SQL_COMPATIBILITY_LEVEL

        return internal_entity


class FalseRuleFilter(SqlRuleFilter):
    """A sql filter with a sql expression that is always True
    """
    def __init__(self):
        super(FalseRuleFilter, self).__init__("1>1", None, True)

    def _to_internal_entity(self):
        internal_entity = InternalFalseFilter()
        internal_entity.sql_expression = self.sql_expression
        internal_entity.requires_preprocessing = True
        internal_entity.compatibility_level = RULE_SQL_COMPATIBILITY_LEVEL
        return internal_entity


class SqlRuleAction(object):
    """Represents set of actions written in SQL language-based syntax that is
    performed against a ServiceBus.Messaging.BrokeredMessage .

    :param sql_expression: SQL expression. e.g. MyProperty='ABC'
    :type sql_expression: str
    :param parameters: Sets the value of the sql expression parameters if any.
    :type parameters: dict[str, Union[str, int, float, bool, datetime, timedelta]]
    :param requires_preprocessing: Value that indicates whether the rule
     action requires preprocessing. Default value: True .
    :type requires_preprocessing: bool
    """
    def __init__(self, sql_expression=None, parameters=None, requires_preprocessing=True):
        # type: (Optional[str], Optional[Dict[str, Union[str, int, float, bool, datetime, timedelta]]], bool) -> None
        self.sql_expression = sql_expression
        self.parameters = parameters
        self.requires_preprocessing = requires_preprocessing

    @classmethod
    def _from_internal_entity(cls, internal_sql_rule_action):
        sql_rule_action = cls()
        sql_rule_action.sql_expression = internal_sql_rule_action.sql_expression
        sql_rule_action.parameters = OrderedDict((kv.key, kv.value) for kv in internal_sql_rule_action.parameters) \
            if internal_sql_rule_action.parameters else OrderedDict()
        sql_rule_action.requires_preprocessing = internal_sql_rule_action.requires_preprocessing
        return sql_rule_action

    def _to_internal_entity(self):
        internal_entity = InternalSqlRuleAction(sql_expression=self.sql_expression)
        internal_entity.parameters = [KeyValue(key=key, value=value) for key, value in self.parameters.items()] \
            if self.parameters else None
        internal_entity.compatibility_level = RULE_SQL_COMPATIBILITY_LEVEL
        internal_entity.requires_preprocessing = self.requires_preprocessing
        return internal_entity


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
