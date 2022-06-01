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

from ._generated.models import (
    QueueDescription as InternalQueueDescription,
    TopicDescription as InternalTopicDescription,
    SubscriptionDescription as InternalSubscriptionDescription,
    RuleDescription as InternalRuleDescription,
    SqlRuleAction as InternalSqlRuleAction,
    EmptyRuleAction as InternalEmptyRuleAction,
    CorrelationFilter as InternalCorrelationFilter,
    NamespaceProperties as InternalNamespaceProperties,
    SqlFilter as InternalSqlFilter,
    TrueFilter as InternalTrueFilter,
    FalseFilter as InternalFalseFilter,
    KeyValue,
    AuthorizationRule as InternalAuthorizationRule,
)

from ._model_workaround import (
    adjust_attribute_map,
    avoid_timedelta_overflow
)
from ._constants import RULE_SQL_COMPATIBILITY_LEVEL
from ._utils import _normalize_entity_path_to_full_path_if_needed

adjust_attribute_map()


# These helpers are to ensure that the Properties objects can't be constructed without all args present,
# as a compromise between our use of kwargs to flatten arg-lists and trying to de-incentivise manual instantiation
# while still trying to provide some guardrails.
def extract_kwarg_template(kwargs, extraction_missing_args, name):
    try:
        return kwargs[name]
    except KeyError:
        extraction_missing_args.append(name)


def validate_extraction_missing_args(extraction_missing_args):
    if extraction_missing_args:
        raise TypeError(
            "__init__() missing {} required keyword arguments: {}".format(
                len(extraction_missing_args),
                " and ".join(["'" + e + "'" for e in extraction_missing_args]),
            )
        )


class DictMixin(object):
    def __setitem__(self, key, item):
        # type: (Any, Any) -> None
        self.__dict__[key] = item

    def __getitem__(self, key):
        # type: (Any) -> Any
        return self.__dict__[key]

    def __repr__(self):
        # type: () -> str
        return str(self)

    def __len__(self):
        # type: () -> int
        return len(self.keys())

    def __delitem__(self, key):
        # type: (Any) -> None
        self.__dict__[key] = None

    def __eq__(self, other):
        # type: (Any) -> bool
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        # type: (Any) -> bool
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        # type: () -> str
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})

    def has_key(self, k):
        # type: (Any) -> bool
        return k in self.__dict__

    def update(self, *args, **kwargs):
        # type: (Any, Any) -> None
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        # type: () -> list
        return [k for k in self.__dict__ if not k.startswith("_")]

    def values(self):
        # type: () -> list
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]

    def items(self):
        # type: () -> list
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]

    def get(self, key, default=None):
        # type: (Any, Optional[Any]) -> Any
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class NamespaceProperties(DictMixin):
    """The metadata related to a Service Bus namespace.

    :ivar alias: Alias for the geo-disaster recovery Service Bus namespace.
    :type alias: str
    :ivar created_at_utc: The exact time the namespace was created.
    :type created_at_utc: ~datetime.datetime
    :ivar messaging_sku: The SKU for the messaging entity. Possible values include: "Basic",
     "Standard", "Premium".
    :type messaging_sku: str or ~azure.servicebus.management._generated.models.MessagingSku
    :ivar messaging_units: The number of messaging units allocated to the namespace.
    :type messaging_units: int
    :ivar modified_at_utc: The exact time the namespace was last modified.
    :type modified_at_utc: ~datetime.datetime
    :ivar name: Name of the namespace.
    :type name: str
    """

    def __init__(self, name, **kwargs):
        # type: (str, Any) -> None
        self.name = name

        extraction_missing_args = []  # type: List[str]
        extract_kwarg = functools.partial(
            extract_kwarg_template, kwargs, extraction_missing_args
        )

        self.name = name
        self.alias = extract_kwarg("alias")
        self.created_at_utc = extract_kwarg("created_at_utc")
        self.messaging_sku = extract_kwarg("messaging_sku")
        self.messaging_units = extract_kwarg("messaging_units")
        self.modified_at_utc = extract_kwarg("modified_at_utc")
        self.namespace_type = extract_kwarg("namespace_type")

        validate_extraction_missing_args(extraction_missing_args)

    @classmethod
    def _from_internal_entity(cls, name, internal_entity):
        # type: (str, InternalNamespaceProperties) -> NamespaceProperties
        namespace_properties = cls(
            name,
            alias=internal_entity.alias,
            created_at_utc=internal_entity.created_time,
            messaging_sku=internal_entity.messaging_sku,
            messaging_units=internal_entity.messaging_units,
            modified_at_utc=internal_entity.modified_time,
            namespace_type=internal_entity.namespace_type,
        )
        return namespace_properties

    def _to_internal_entity(self):
        internal_entity = InternalNamespaceProperties()
        internal_entity.alias = self.alias
        internal_entity.created_time = self.created_at_utc
        internal_entity.messaging_sku = self.messaging_sku
        internal_entity.messaging_units = self.messaging_units
        internal_entity.modified_time = self.modified_at_utc
        internal_entity.namespace_type = self.namespace_type

        return internal_entity


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
    :ivar availability_status: Availibility status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type availability_status: str or
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
    :ivar forward_dead_lettered_messages_to: The name of the recipient entity to which all the
     dead-lettered messages of this subscription are forwarded to.
    :type forward_dead_lettered_messages_to: str
    :ivar max_message_size_in_kilobytes: The maximum size in kilobytes of message payload that
     can be accepted by the queue. This feature is only available when using a Premium namespace
     and Service Bus API version "2021-05" or higher.
    :type max_message_size_in_kilobytes: int
    """

    def __init__(self, name, **kwargs):
        # type: (str, Any) -> None
        self.name = name
        self._internal_qd = None  # type: Optional[InternalQueueDescription]

        extraction_missing_args = []  # type: List[str]
        extract_kwarg = functools.partial(
            extract_kwarg_template, kwargs, extraction_missing_args
        )

        self.authorization_rules = extract_kwarg("authorization_rules")
        self.auto_delete_on_idle = extract_kwarg("auto_delete_on_idle")
        self.dead_lettering_on_message_expiration = extract_kwarg(
            "dead_lettering_on_message_expiration"
        )
        self.default_message_time_to_live = extract_kwarg(
            "default_message_time_to_live"
        )
        self.duplicate_detection_history_time_window = extract_kwarg(
            "duplicate_detection_history_time_window"
        )
        self.availability_status = extract_kwarg("availability_status")
        self.enable_batched_operations = extract_kwarg("enable_batched_operations")
        self.enable_express = extract_kwarg("enable_express")
        self.enable_partitioning = extract_kwarg("enable_partitioning")
        self.lock_duration = extract_kwarg("lock_duration")
        self.max_delivery_count = extract_kwarg("max_delivery_count")
        self.max_size_in_megabytes = extract_kwarg("max_size_in_megabytes")
        self.requires_duplicate_detection = extract_kwarg(
            "requires_duplicate_detection"
        )
        self.requires_session = extract_kwarg("requires_session")
        self.status = extract_kwarg("status")
        self.forward_to = extract_kwarg("forward_to")
        self.user_metadata = extract_kwarg("user_metadata")
        self.forward_dead_lettered_messages_to = extract_kwarg(
            "forward_dead_lettered_messages_to"
        )
        self.max_message_size_in_kilobytes = extract_kwarg("max_message_size_in_kilobytes")

        validate_extraction_missing_args(extraction_missing_args)

    @classmethod
    def _from_internal_entity(cls, name, internal_qd):
        # type: (str, InternalQueueDescription) -> QueueProperties
        qd = cls(
            name,
            authorization_rules=[
                AuthorizationRule._from_internal_entity(r)
                for r in internal_qd.authorization_rules
            ]
            if internal_qd.authorization_rules
            else (internal_qd.authorization_rules or []),
            auto_delete_on_idle=internal_qd.auto_delete_on_idle,
            dead_lettering_on_message_expiration=internal_qd.dead_lettering_on_message_expiration,
            default_message_time_to_live=internal_qd.default_message_time_to_live,
            duplicate_detection_history_time_window=internal_qd.duplicate_detection_history_time_window,
            availability_status=internal_qd.entity_availability_status,
            enable_batched_operations=internal_qd.enable_batched_operations,
            enable_express=internal_qd.enable_express,
            enable_partitioning=internal_qd.enable_partitioning,
            lock_duration=internal_qd.lock_duration,
            max_delivery_count=internal_qd.max_delivery_count,
            max_size_in_megabytes=internal_qd.max_size_in_megabytes,
            requires_duplicate_detection=internal_qd.requires_duplicate_detection,
            requires_session=internal_qd.requires_session,
            status=internal_qd.status,
            forward_to=internal_qd.forward_to,
            forward_dead_lettered_messages_to=internal_qd.forward_dead_lettered_messages_to,
            user_metadata=internal_qd.user_metadata,
            max_message_size_in_kilobytes=internal_qd.max_message_size_in_kilobytes
        )

        qd._internal_qd = deepcopy(internal_qd)  # pylint:disable=protected-access
        return qd

    def _to_internal_entity(self, fully_qualified_namespace, kwargs=None):
        # type: (str, Optional[Dict]) -> InternalQueueDescription
        kwargs = kwargs or {}

        if not self._internal_qd:
            internal_qd = InternalQueueDescription()
            self._internal_qd = internal_qd

        authorization_rules = kwargs.pop("authorization_rules", self.authorization_rules)
        self._internal_qd.authorization_rules = (
            [r._to_internal_entity() for r in authorization_rules]
            if authorization_rules
            else authorization_rules
        )

        self._internal_qd.auto_delete_on_idle = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("auto_delete_on_idle", self.auto_delete_on_idle)
        )
        self._internal_qd.dead_lettering_on_message_expiration = (
            kwargs.pop("dead_lettering_on_message_expiration", self.dead_lettering_on_message_expiration)
        )
        self._internal_qd.default_message_time_to_live = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("default_message_time_to_live", self.default_message_time_to_live)
        )
        self._internal_qd.duplicate_detection_history_time_window = (
            kwargs.pop("duplicate_detection_history_time_window", self.duplicate_detection_history_time_window)
        )
        self._internal_qd.entity_availability_status = kwargs.pop("availability_status", self.availability_status)
        self._internal_qd.enable_batched_operations = (
            kwargs.pop("enable_batched_operations", self.enable_batched_operations)
        )
        self._internal_qd.enable_express = kwargs.pop("enable_express", self.enable_express)
        self._internal_qd.enable_partitioning = kwargs.pop("enable_partitioning", self.enable_partitioning)
        self._internal_qd.lock_duration = kwargs.pop("lock_duration", self.lock_duration)
        self._internal_qd.max_delivery_count = kwargs.pop("max_delivery_count", self.max_delivery_count)
        self._internal_qd.max_size_in_megabytes = kwargs.pop("max_size_in_megabytes", self.max_size_in_megabytes)
        self._internal_qd.requires_duplicate_detection = (
            kwargs.pop("requires_duplicate_detection", self.requires_duplicate_detection)
        )
        self._internal_qd.requires_session = kwargs.pop("requires_session", self.requires_session)
        self._internal_qd.status = kwargs.pop("status", self.status)

        forward_to = kwargs.pop("forward_to", self.forward_to)
        self._internal_qd.forward_to = _normalize_entity_path_to_full_path_if_needed(
            forward_to,
            fully_qualified_namespace
        )

        forward_dead_lettered_messages_to = (
            kwargs.pop("forward_dead_lettered_messages_to", self.forward_dead_lettered_messages_to)
        )
        self._internal_qd.forward_dead_lettered_messages_to = _normalize_entity_path_to_full_path_if_needed(
            forward_dead_lettered_messages_to,
            fully_qualified_namespace
        )

        self._internal_qd.user_metadata = kwargs.pop("user_metadata", self.user_metadata)
        self._internal_qd.max_message_size_in_kilobytes = kwargs.pop(
            "max_message_size_in_kilobytes",
            self.max_message_size_in_kilobytes
        )

        return self._internal_qd


class QueueRuntimeProperties(object):
    """Service Bus queue runtime properties."""

    def __init__(
        self,
    ):
        # type: () -> None
        self._name = None  # type: Optional[str]
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
    def accessed_at_utc(self):
        """Last time a message was sent, or the last time there was a receive request to this queue.

        :rtype:  ~datetime.datetime
        """
        return self._internal_qr.accessed_at

    @property
    def created_at_utc(self):
        """The exact time the queue was created.

        :rtype: ~datetime.datetime
        """
        return self._internal_qr.created_at

    @property
    def updated_at_utc(self):
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
        return (
            self._internal_qr.message_count_details.transfer_dead_letter_message_count
        )

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
    :ivar availability_status: Availability status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type availability_status: str or
     ~azure.servicebus.management.EntityAvailabilityStatus
    :ivar enable_express: A value that indicates whether Express Entities are enabled. An express
     queue holds a message in memory temporarily before writing it to persistent storage.
    :type enable_express: bool
    :ivar user_metadata: Metadata associated with the topic.
    :type user_metadata: str
    :ivar max_message_size_in_kilobytes: The maximum size in kilobytes of message payload that
     can be accepted by the topic. This feature is only available when using a Premium namespace
     and Service Bus API version "2021-05" or higher.
    :type max_message_size_in_kilobytes: int
    """

    def __init__(self, name, **kwargs):
        # type: (str, Any) -> None
        self.name = name
        self._internal_td = None  # type: Optional[InternalTopicDescription]

        extraction_missing_args = []  # type: List[str]
        extract_kwarg = functools.partial(
            extract_kwarg_template, kwargs, extraction_missing_args
        )

        self.default_message_time_to_live = extract_kwarg(
            "default_message_time_to_live"
        )
        self.max_size_in_megabytes = extract_kwarg("max_size_in_megabytes")
        self.requires_duplicate_detection = extract_kwarg(
            "requires_duplicate_detection"
        )
        self.duplicate_detection_history_time_window = extract_kwarg(
            "duplicate_detection_history_time_window"
        )
        self.enable_batched_operations = extract_kwarg("enable_batched_operations")
        self.size_in_bytes = extract_kwarg("size_in_bytes")
        self.authorization_rules = extract_kwarg("authorization_rules")
        self.status = extract_kwarg("status")
        self.support_ordering = extract_kwarg("support_ordering")
        self.auto_delete_on_idle = extract_kwarg("auto_delete_on_idle")
        self.enable_partitioning = extract_kwarg("enable_partitioning")
        self.availability_status = extract_kwarg("availability_status")
        self.enable_express = extract_kwarg("enable_express")
        self.user_metadata = extract_kwarg("user_metadata")
        self.max_message_size_in_kilobytes = extract_kwarg("max_message_size_in_kilobytes")

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
            authorization_rules=[
                AuthorizationRule._from_internal_entity(r)
                for r in internal_td.authorization_rules
            ]
            if internal_td.authorization_rules
            else internal_td.authorization_rules,
            status=internal_td.status,
            support_ordering=internal_td.support_ordering,
            auto_delete_on_idle=internal_td.auto_delete_on_idle,
            enable_partitioning=internal_td.enable_partitioning,
            availability_status=internal_td.entity_availability_status,
            enable_express=internal_td.enable_express,
            user_metadata=internal_td.user_metadata,
            max_message_size_in_kilobytes=internal_td.max_message_size_in_kilobytes
        )
        td._internal_td = deepcopy(internal_td)
        return td

    def _to_internal_entity(self, kwargs=None):
        # type: (Optional[Dict]) -> InternalTopicDescription
        kwargs = kwargs or {}

        if not self._internal_td:
            self._internal_td = InternalTopicDescription()
        self._internal_td.default_message_time_to_live = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("default_message_time_to_live", self.default_message_time_to_live)
        )
        self._internal_td.max_size_in_megabytes = kwargs.pop("max_size_in_megabytes", self.max_size_in_megabytes)
        self._internal_td.requires_duplicate_detection = (
            kwargs.pop("requires_duplicate_detection", self.requires_duplicate_detection)
        )
        self._internal_td.duplicate_detection_history_time_window = (
            kwargs.pop("duplicate_detection_history_time_window", self.duplicate_detection_history_time_window)
        )
        self._internal_td.enable_batched_operations = (
            kwargs.pop("enable_batched_operations", self.enable_batched_operations)
        )
        self._internal_td.size_in_bytes = kwargs.pop("size_in_bytes", self.size_in_bytes)

        authorization_rules = kwargs.pop("authorization_rules", self.authorization_rules)
        self._internal_td.authorization_rules = (
            [r._to_internal_entity() for r in authorization_rules]
            if authorization_rules
            else authorization_rules
        )
        self._internal_td.status = kwargs.pop("status", self.status)
        self._internal_td.support_ordering = kwargs.pop("support_ordering", self.support_ordering)
        self._internal_td.auto_delete_on_idle = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("auto_delete_on_idle", self.auto_delete_on_idle)
        )
        self._internal_td.enable_partitioning = kwargs.pop("enable_partitioning", self.enable_partitioning)
        self._internal_td.entity_availability_status = kwargs.pop("availability_status", self.availability_status)
        self._internal_td.enable_express = kwargs.pop("enable_express", self.enable_express)
        self._internal_td.user_metadata = kwargs.pop("user_metadata", self.user_metadata)
        self._internal_td.max_message_size_in_kilobytes = kwargs.pop(
            "max_message_size_in_kilobytes",
            self.max_message_size_in_kilobytes
        )

        return self._internal_td


class TopicRuntimeProperties(object):
    """Runtime properties of a Service Bus topic resource."""

    def __init__(
        self,
    ):
        # type: () -> None
        self._name = None  # type: Optional[str]
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
    def accessed_at_utc(self):
        """Last time a message was sent, or the last time there was a receive request

        :rtype: ~datetime.datetime
        """
        return self._internal_td.accessed_at

    @property
    def created_at_utc(self):
        """The exact time the queue was created.

        :rtype: ~datetime.datetime
        """
        return self._internal_td.created_at

    @property
    def updated_at_utc(self):
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
    :ivar availability_status: Availability status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type availability_status: str or
     ~azure.servicebus.management.EntityAvailabilityStatus
    """

    def __init__(self, name, **kwargs):
        # type: (str, Any) -> None
        self.name = name
        self._internal_sd = None  # type: Optional[InternalSubscriptionDescription]

        extraction_missing_args = []  # type: List[str]
        extract_kwarg = functools.partial(
            extract_kwarg_template, kwargs, extraction_missing_args
        )

        self.lock_duration = extract_kwarg("lock_duration")
        self.requires_session = extract_kwarg("requires_session")
        self.default_message_time_to_live = extract_kwarg(
            "default_message_time_to_live"
        )
        self.dead_lettering_on_message_expiration = extract_kwarg(
            "dead_lettering_on_message_expiration"
        )
        self.dead_lettering_on_filter_evaluation_exceptions = extract_kwarg(
            "dead_lettering_on_filter_evaluation_exceptions"
        )
        self.max_delivery_count = extract_kwarg("max_delivery_count")
        self.enable_batched_operations = extract_kwarg("enable_batched_operations")
        self.status = extract_kwarg("status")
        self.forward_to = extract_kwarg("forward_to")
        self.user_metadata = extract_kwarg("user_metadata")
        self.forward_dead_lettered_messages_to = extract_kwarg(
            "forward_dead_lettered_messages_to"
        )
        self.auto_delete_on_idle = extract_kwarg("auto_delete_on_idle")
        self.availability_status = extract_kwarg("availability_status")

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
            availability_status=internal_subscription.entity_availability_status,
        )
        subscription._internal_sd = deepcopy(internal_subscription)
        return subscription

    def _to_internal_entity(self, fully_qualified_namespace, kwargs=None):
        # type: (str, Optional[Dict]) -> InternalSubscriptionDescription
        kwargs = kwargs or {}

        if not self._internal_sd:
            self._internal_sd = InternalSubscriptionDescription()
        self._internal_sd.lock_duration = kwargs.pop("lock_duration", self.lock_duration)
        self._internal_sd.requires_session = kwargs.pop("requires_session", self.requires_session)
        self._internal_sd.default_message_time_to_live = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("default_message_time_to_live", self.default_message_time_to_live)
        )
        self._internal_sd.dead_lettering_on_message_expiration = (
            kwargs.pop("dead_lettering_on_message_expiration", self.dead_lettering_on_message_expiration)
        )
        self._internal_sd.dead_lettering_on_filter_evaluation_exceptions = (
            kwargs.pop(
                "dead_lettering_on_filter_evaluation_exceptions",
                self.dead_lettering_on_filter_evaluation_exceptions
            )
        )
        self._internal_sd.max_delivery_count = kwargs.pop("max_delivery_count", self.max_delivery_count)
        self._internal_sd.enable_batched_operations = (
            kwargs.pop("enable_batched_operations", self.enable_batched_operations)
        )
        self._internal_sd.status = kwargs.pop("status", self.status)

        forward_to = kwargs.pop("forward_to", self.forward_to)
        self._internal_sd.forward_to = _normalize_entity_path_to_full_path_if_needed(
            forward_to,
            fully_qualified_namespace
        )

        forward_dead_lettered_messages_to = (
            kwargs.pop("forward_dead_lettered_messages_to", self.forward_dead_lettered_messages_to)
        )
        self._internal_sd.forward_dead_lettered_messages_to = _normalize_entity_path_to_full_path_if_needed(
            forward_dead_lettered_messages_to,
            fully_qualified_namespace
        )

        self._internal_sd.user_metadata = kwargs.pop("user_metadata", self.user_metadata)
        self._internal_sd.auto_delete_on_idle = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("auto_delete_on_idle", self.auto_delete_on_idle)
        )
        self._internal_sd.entity_availability_status = kwargs.pop("availability_status", self.availability_status)

        return self._internal_sd


class SubscriptionRuntimeProperties(object):
    """Runtime properties of a Service Bus topic subscription resource."""

    def __init__(self):
        # type: () -> None
        self._internal_sd = None  # type: Optional[InternalSubscriptionDescription]
        self._name = None  # type: Optional[str]

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
    def accessed_at_utc(self):
        """Last time a message was sent, or the last time there was a receive request

        :rtype: ~datetime.datetime
        """
        return self._internal_sd.accessed_at

    @property
    def created_at_utc(self):
        """The exact time the subscription was created.

        :rtype: ~datetime.datetime
        """
        return self._internal_sd.created_at

    @property
    def updated_at_utc(self):
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
        return (
            self._internal_sd.message_count_details.transfer_dead_letter_message_count
        )

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
    :ivar created_at_utc: The exact time the rule was created.
    :type created_at_utc: ~datetime.datetime
    """

    def __init__(self, name, **kwargs):
        # type: (str, Any) -> None

        self.name = name
        self._internal_rule = None  # type: Optional[InternalRuleDescription]

        extraction_missing_args = []  # type: List[str]
        extract_kwarg = functools.partial(
            extract_kwarg_template, kwargs, extraction_missing_args
        )

        self.filter = extract_kwarg("filter")
        self.action = extract_kwarg("action")
        self.created_at_utc = extract_kwarg("created_at_utc")

        validate_extraction_missing_args(extraction_missing_args)

    @classmethod
    def _from_internal_entity(cls, name, internal_rule):
        # type: (str, InternalRuleDescription) -> RuleProperties
        rule = cls(
            name,
            filter=RULE_CLASS_MAPPING[type(internal_rule.filter)]._from_internal_entity(
                internal_rule.filter
            )
            if internal_rule.filter
            and isinstance(internal_rule.filter, tuple(RULE_CLASS_MAPPING.keys()))
            else None,
            action=RULE_CLASS_MAPPING[type(internal_rule.action)]._from_internal_entity(
                internal_rule.action
            )
            if internal_rule.action
            and isinstance(internal_rule.action, tuple(RULE_CLASS_MAPPING.keys()))
            else None,
            created_at_utc=internal_rule.created_at,
        )
        rule._internal_rule = deepcopy(internal_rule)
        return rule

    def _to_internal_entity(self, kwargs=None):
        # type: (Optional[Dict]) -> InternalRuleDescription
        kwargs = kwargs or {}
        if not self._internal_rule:
            self._internal_rule = InternalRuleDescription()

        rule_filter = kwargs.pop("filter", self.filter)
        self._internal_rule.filter = rule_filter._to_internal_entity() if rule_filter else TRUE_FILTER  # type: ignore

        action = kwargs.pop("action", self.action)
        self._internal_rule.action = (
            action._to_internal_entity() if action else EMPTY_RULE_ACTION
        )

        self._internal_rule.created_at = kwargs.pop("created_at_utc", self.created_at_utc)
        self._internal_rule.name = kwargs.pop("name", self.name)

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
        self.correlation_id = kwargs.get("correlation_id", None)
        self.message_id = kwargs.get("message_id", None)
        self.to = kwargs.get("to", None)
        self.reply_to = kwargs.get("reply_to", None)
        self.label = kwargs.get("label", None)
        self.session_id = kwargs.get("session_id", None)
        self.reply_to_session_id = kwargs.get("reply_to_session_id", None)
        self.content_type = kwargs.get("content_type", None)
        self.properties = kwargs.get("properties", None)

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
        correlation_filter.reply_to_session_id = (
            internal_correlation_filter.reply_to_session_id
        )
        correlation_filter.content_type = internal_correlation_filter.content_type
        correlation_filter.properties = (
            OrderedDict(
                (kv.key, kv.value) for kv in internal_correlation_filter.properties
            )
            if internal_correlation_filter.properties
            else OrderedDict()
        )

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
        internal_entity.properties = (
            [KeyValue(key=key, value=value) for key, value in self.properties.items()]
            if self.properties
            else None
        )

        return internal_entity


class SqlRuleFilter(object):
    """Represents a filter which is a composition of an expression and an action
    that is executed in the pub/sub pipeline.

    .. admonition:: Example:

        .. code-block:: python
            :caption: Create SqlRuleFilter.

            sql_filter = SqlRuleFilter("property1 = 'value'")
            sql_filter_parametrized = SqlRuleFilter(
                "property1 = @param1 AND property2 = @param2",
                parameters={
                    "@param1": "value",
                    "@param2" : 1
                }
            )

    :param sql_expression: The SQL expression. e.g. MyProperty='ABC'
    :type sql_expression: str
    :param parameters: Sets the value of the sql expression parameters if any.
    :type parameters: Dict[str, Union[str, int, float, bool, datetime, timedelta]]
    """

    def __init__(self, sql_expression=None, parameters=None):
        # type: (Optional[str], Optional[Dict[str, Union[str, int, float, bool, datetime, timedelta]]]) -> None
        self.sql_expression = sql_expression
        self.parameters = parameters
        self.requires_preprocessing = True

    @classmethod
    def _from_internal_entity(cls, internal_sql_rule_filter):
        sql_rule_filter = cls()
        sql_rule_filter.sql_expression = internal_sql_rule_filter.sql_expression
        sql_rule_filter.parameters = (
            OrderedDict(
                (kv.key, kv.value) for kv in internal_sql_rule_filter.parameters
            )
            if internal_sql_rule_filter.parameters
            else OrderedDict()
        )
        sql_rule_filter.requires_preprocessing = (
            internal_sql_rule_filter.requires_preprocessing
        )
        return sql_rule_filter

    def _to_internal_entity(self):
        # type: () -> InternalSqlFilter
        internal_entity = InternalSqlFilter(sql_expression=self.sql_expression)
        internal_entity.parameters = (
            [
                KeyValue(key=key, value=value) for key, value in self.parameters.items()  # type: ignore
            ]
            if self.parameters
            else None
        )
        internal_entity.compatibility_level = RULE_SQL_COMPATIBILITY_LEVEL
        internal_entity.requires_preprocessing = self.requires_preprocessing
        return internal_entity


class TrueRuleFilter(SqlRuleFilter):
    """A sql filter with a sql expression that is always True"""

    def __init__(self):
        # type: () -> None
        super(TrueRuleFilter, self).__init__("1=1", None)

    def _to_internal_entity(self):
        internal_entity = InternalTrueFilter()
        internal_entity.sql_expression = self.sql_expression
        internal_entity.requires_preprocessing = True
        internal_entity.compatibility_level = RULE_SQL_COMPATIBILITY_LEVEL

        return internal_entity


class FalseRuleFilter(SqlRuleFilter):
    """A sql filter with a sql expression that is always True"""

    def __init__(self):
        # type: () -> None
        super(FalseRuleFilter, self).__init__("1>1", None)

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
    :type parameters: Dict[str, Union[str, int, float, bool, datetime, timedelta]]
    :type requires_preprocessing: bool
    """

    def __init__(self, sql_expression=None, parameters=None):
        # type: (Optional[str], Optional[Dict[str, Union[str, int, float, bool, datetime, timedelta]]]) -> None
        self.sql_expression = sql_expression
        self.parameters = parameters
        self.requires_preprocessing = True

    @classmethod
    def _from_internal_entity(cls, internal_sql_rule_action):
        sql_rule_action = cls()
        sql_rule_action.sql_expression = internal_sql_rule_action.sql_expression
        sql_rule_action.parameters = (
            OrderedDict(
                (kv.key, kv.value) for kv in internal_sql_rule_action.parameters
            )
            if internal_sql_rule_action.parameters
            else OrderedDict()
        )
        sql_rule_action.requires_preprocessing = (
            internal_sql_rule_action.requires_preprocessing
        )
        return sql_rule_action

    def _to_internal_entity(self):
        internal_entity = InternalSqlRuleAction(sql_expression=self.sql_expression)
        internal_entity.parameters = (
            [KeyValue(key=key, value=value) for key, value in self.parameters.items()]
            if self.parameters
            else None
        )
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


class AuthorizationRule(object):
    """Authorization rule of an entity.

    :param type: The authorization type.
    :type type: str
    :param claim_type: The claim type.
    :type claim_type: str
    :param claim_value: The claim value.
    :type claim_value: str
    :param rights: Access rights of the entity. Values are 'Send', 'Listen', or 'Manage'.
    :type rights: list[AccessRights]
    :param created_at_utc: The date and time when the authorization rule was created.
    :type created_at_utc: ~datetime.datetime
    :param modified_at_utc: The date and time when the authorization rule was modified.
    :type modified_at_utc: ~datetime.datetime
    :param key_name: The authorization rule key name.
    :type key_name: str
    :param primary_key: The primary key of the authorization rule.
    :type primary_key: str
    :param secondary_key: The primary key of the authorization rule.
    :type secondary_key: str
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.type = kwargs.get("type", None)
        self.claim_type = kwargs.get("claim_type", None)
        self.claim_value = kwargs.get("claim_value", None)
        self.rights = kwargs.get("rights", None)
        self.created_at_utc = kwargs.get("created_at_utc", None)
        self.modified_at_utc = kwargs.get("modified_at_utc", None)
        self.key_name = kwargs.get("key_name", None)
        self.primary_key = kwargs.get("primary_key", None)
        self.secondary_key = kwargs.get("secondary_key", None)

    @classmethod
    def _from_internal_entity(cls, internal_authorization_rule):
        authorization_rule = cls()
        authorization_rule.claim_type = internal_authorization_rule.claim_type
        authorization_rule.claim_value = internal_authorization_rule.claim_value
        authorization_rule.rights = internal_authorization_rule.rights
        authorization_rule.created_at_utc = internal_authorization_rule.created_time
        authorization_rule.modified_at_utc = internal_authorization_rule.modified_time
        authorization_rule.key_name = internal_authorization_rule.key_name
        authorization_rule.primary_key = internal_authorization_rule.primary_key
        authorization_rule.secondary_key = internal_authorization_rule.secondary_key

        return authorization_rule

    def _to_internal_entity(self):
        # type: () -> InternalAuthorizationRule
        internal_entity = InternalAuthorizationRule()
        internal_entity.claim_type = self.claim_type
        internal_entity.claim_value = self.claim_value
        internal_entity.rights = self.rights
        internal_entity.created_time = self.created_at_utc
        internal_entity.modified_time = self.modified_at_utc
        internal_entity.key_name = self.key_name
        internal_entity.primary_key = self.primary_key
        internal_entity.secondary_key = self.secondary_key
        return internal_entity
