# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
# pylint:disable=too-many-lines
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Type, Dict, Any, Union, Optional, List, Tuple, TYPE_CHECKING, cast
from ._generated._serialization import Model

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
    KeyObjectValue,
    AuthorizationRule as InternalAuthorizationRule,
)
from ._model_workaround import adjust_attribute_map, avoid_timedelta_overflow
from ._constants import RULE_SQL_COMPATIBILITY_LEVEL
from ._utils import _normalize_entity_path_to_full_path_if_needed

if TYPE_CHECKING:
    from ._generated.models import (
        MessagingSku,
        NamespaceType,
        EntityAvailabilityStatus,
        EntityStatus,
        AccessRights,
        MessageCountDetails,
    )

adjust_attribute_map()


class DictMixin(object):
    def __setitem__(self, key: str, item: Any) -> None:
        self.__dict__[key] = item

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self.keys())

    def __delitem__(self, key: str) -> None:
        self.__dict__[key] = None

    def __eq__(self, other: Any) -> bool:
        """Compare objects by comparing all attributes.
        :param any other: The object to compare with
        :return: `True` if `self` and `other` are equal, `False` otherwise.
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other: Any) -> bool:
        """Compare objects by comparing all attributes.
        :param any other: The object to compare with
        :return: `True` if `self` and `other` are not equal, `False` otherwise.
        :rtype: bool
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

    def has_key(self, k: str) -> bool:
        return k in self.__dict__

    def update(self, *args: Any, **kwargs: Any) -> None:
        return self.__dict__.update(*args, **kwargs)

    def keys(self) -> List[str]:
        return [k for k in self.__dict__ if not k.startswith("_")]

    def values(self) -> List[Any]:
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]

    def items(self) -> List[Tuple[str, Any]]:
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class NamespaceProperties(DictMixin):
    """The metadata related to a Service Bus namespace.

    **Please use the `get_namespace_properties` on the ServiceBusAdministrationClient to get a
    `NamespaceProperties` instance  instead of instantiating a `NamespaceProperties` object directly.**

    :param name: Name of the namespace.
    :type name: str
    :keyword alias: Alias for the geo-disaster recovery Service Bus namespace.
    :paramtype alias: str
    :keyword created_at_utc: The exact time the namespace was created.
    :paramtype created_at_utc: ~datetime.datetime
    :keyword messaging_sku: The SKU for the messaging entity. Possible values include: "Basic",
     "Standard", "Premium".
    :paramtype messaging_sku: str or ~azure.servicebus.management.MessagingSku
    :keyword messaging_units: The number of messaging units allocated to the namespace.
    :paramtype messaging_units: int
    :keyword modified_at_utc: The exact time the namespace was last modified.
    :paramtype modified_at_utc: ~datetime.datetime
    :keyword namespace_type: The type of entities the namespace can contain. Known values are:
     "Messaging", "NotificationHub", "Mixed", "EventHub", and "Relay".
    :paramtype namespace_type: str or ~azure.servicebus.management.NamespaceType

    :ivar alias: Alias for the geo-disaster recovery Service Bus namespace.
    :vartype alias: str
    :ivar created_at_utc: The exact time the namespace was created.
    :vartype created_at_utc: ~datetime.datetime
    :ivar messaging_sku: The SKU for the messaging entity. Possible values include: "Basic",
     "Standard", "Premium".
    :vartype messaging_sku: str or ~azure.servicebus.management.MessagingSku
    :ivar messaging_units: The number of messaging units allocated to the namespace.
    :vartype messaging_units: int
    :ivar modified_at_utc: The exact time the namespace was last modified.
    :vartype modified_at_utc: ~datetime.datetime
    :ivar name: Name of the namespace.
    :vartype name: str
    :ivar namespace_type: The type of entities the namespace can contain. Known values are:
     "Messaging", "NotificationHub", "Mixed", "EventHub", and "Relay".
    :vartype namespace_type: str or ~azure.servicebus.management._generated.models.NamespaceType
    """

    def __init__(
        self,
        name: str,
        *,
        alias: Optional[str],
        created_at_utc: Optional[datetime],
        messaging_sku: Optional[Union[str, "MessagingSku"]],
        messaging_units: Optional[int],
        modified_at_utc: Optional[datetime],
        namespace_type: Optional[Union[str, "NamespaceType"]],
    ) -> None:
        self.name = name
        self.alias = alias
        self.created_at_utc = created_at_utc
        self.messaging_sku = messaging_sku
        self.messaging_units = messaging_units
        self.modified_at_utc = modified_at_utc
        self.namespace_type = namespace_type

    @classmethod
    def _from_internal_entity(cls, name: str, internal_entity: InternalNamespaceProperties) -> "NamespaceProperties":
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

    def _to_internal_entity(self) -> InternalNamespaceProperties:
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

    **Please use `get_queue`, `create_queue`, or `list_queues` on the ServiceBusAdministrationClient
    to get a `QueueProperties` instance instead of instantiating a `QueueProperties` object directly.**

    :param name: Name of the queue.
    :type name: str
    :keyword authorization_rules: Authorization rules for resource.
    :paramtype authorization_rules: list[~azure.servicebus.management.AuthorizationRule] or None
    :keyword auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the queue is
     automatically deleted. The minimum duration is 5 minutes.
    :paramtype auto_delete_on_idle: ~datetime.timedelta or str or None
    :keyword dead_lettering_on_message_expiration: A value that indicates whether this queue has dead
     letter support when a message expires.
    :paramtype dead_lettering_on_message_expiration: bool or None
    :keyword default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :paramtype default_message_time_to_live: ~datetime.timedelta or str or None
    :keyword duplicate_detection_history_time_window: ISO 8601 timeSpan structure that defines the
     duration of the duplicate detection history. The default value is 10 minutes.
    :paramtype duplicate_detection_history_time_window: ~datetime.timedelta or str or None
    :keyword availability_status: Availibility status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :paramtype availability_status: str or None or
     ~azure.servicebus.management.EntityAvailabilityStatus
    :keyword enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :paramtype enable_batched_operations: bool or None
    :keyword enable_express: A value that indicates whether Express Entities are enabled. An express
     queue holds a message in memory temporarily before writing it to persistent storage.
    :paramtype enable_express: bool or None
    :keyword enable_partitioning: A value that indicates whether the queue is to be partitioned
     across multiple message brokers.
    :paramtype enable_partitioning: bool or None
    :keyword lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
     that the message is locked for other receivers. The maximum value for LockDuration is 5
     minutes; the default value is 1 minute.
    :paramtype lock_duration: ~datetime.timedelt or Nonea
    :keyword max_delivery_count: The maximum delivery count. A message is automatically deadlettered
     after this number of deliveries. Default value is 10.
    :paramtype max_delivery_count: int or None
    :keyword max_size_in_megabytes: The maximum size of the queue in megabytes, which is the size of
     memory allocated for the queue.
    :paramtype max_size_in_megabytes: int or None
    :keyword requires_duplicate_detection: A value indicating if this queue requires duplicate
     detection.
    :paramtype requires_duplicate_detection: bool or None
    :keyword requires_session: A value that indicates whether the queue supports the concept of
     sessions.
    :paramtype requires_session: bool or None
    :keyword status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :paramtype status: str or ~azure.servicebus.management.EntityStatus
    :keyword forward_to: The name of the recipient entity to which all the messages sent to the queue
     are forwarded to.
    :paramtype forward_to: str or None
    :keyword user_metadata: Custom metdata that user can associate with the description. Max length
     is 1024 chars.
    :paramtype user_metadata: str or None
    :keyword forward_dead_lettered_messages_to: The name of the recipient entity to which all the
     dead-lettered messages of this subscription are forwarded to.
    :paramtype forward_dead_lettered_messages_to: str or None
    :keyword max_message_size_in_kilobytes: The maximum size in kilobytes of message payload that
     can be accepted by the queue. This feature is only available when using a Premium namespace
     and Service Bus API version "2021-05" or higher.
    :paramtype max_message_size_in_kilobytes: int or None

    :ivar name: Name of the queue.
    :vartype name: str or None
    :ivar authorization_rules: Authorization rules for resource.
    :vartype authorization_rules: list[~azure.servicebus.management.AuthorizationRule]
    :ivar auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the queue is
     automatically deleted. The minimum duration is 5 minutes.
    :vartype auto_delete_on_idle: ~datetime.timedelta or str or None
    :ivar dead_lettering_on_message_expiration: A value that indicates whether this queue has dead
     letter support when a message expires.
    :vartype dead_lettering_on_message_expiration: bool or None
    :ivar default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :vartype default_message_time_to_live: ~datetime.timedelta or str or None
    :ivar duplicate_detection_history_time_window: ISO 8601 timeSpan structure that defines the
     duration of the duplicate detection history. The default value is 10 minutes.
    :vartype duplicate_detection_history_time_window: ~datetime.timedelta or str or None
    :ivar availability_status: Availibility status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :vartype availability_status: str or None or
     ~azure.servicebus.management.EntityAvailabilityStatus
    :ivar enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :vartype enable_batched_operations: bool or None
    :ivar enable_express: A value that indicates whether Express Entities are enabled. An express
     queue holds a message in memory temporarily before writing it to persistent storage.
    :vartype enable_express: bool or None
    :ivar enable_partitioning: A value that indicates whether the queue is to be partitioned
     across multiple message brokers.
    :vartype enable_partitioning: bool or None
    :ivar lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
     that the message is locked for other receivers. The maximum value for LockDuration is 5
     minutes; the default value is 1 minute.
    :vartype lock_duration: ~datetime.timedelta or str or None
    :ivar max_delivery_count: The maximum delivery count. A message is automatically deadlettered
     after this number of deliveries. Default value is 10.
    :vartype max_delivery_count: int or None
    :ivar max_size_in_megabytes: The maximum size of the queue in megabytes, which is the size of
     memory allocated for the queue.
    :vartype max_size_in_megabytes: int or None
    :ivar requires_duplicate_detection: A value indicating if this queue requires duplicate
     detection.
    :vartype requires_duplicate_detection: bool or None
    :ivar requires_session: A value that indicates whether the queue supports the concept of
     sessions.
    :vartype requires_session: bool or None
    :ivar status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :vartype status: str or ~azure.servicebus.management.EntityStatus or None
    :ivar forward_to: The name of the recipient entity to which all the messages sent to the queue
     are forwarded to.
    :vartype forward_to: str or None
    :ivar user_metadata: Custom metdata that user can associate with the description. Max length
     is 1024 chars.
    :vartype user_metadata: str or None
    :ivar forward_dead_lettered_messages_to: The name of the recipient entity to which all the
     dead-lettered messages of this subscription are forwarded to.
    :vartype forward_dead_lettered_messages_to: str or None
    :ivar max_message_size_in_kilobytes: The maximum size in kilobytes of message payload that
     can be accepted by the queue. This feature is only available when using a Premium namespace
     and Service Bus API version "2021-05" or higher.
    :vartype max_message_size_in_kilobytes: int or None
    """

    def __init__(
        self,
        name: str,
        *,
        authorization_rules: Optional[List["AuthorizationRule"]],
        auto_delete_on_idle: Optional[Union[timedelta, str]],
        dead_lettering_on_message_expiration: Optional[bool],
        default_message_time_to_live: Optional[Union[timedelta, str]],
        duplicate_detection_history_time_window: Optional[Union[timedelta, str]],
        availability_status: Optional[Union[str, "EntityAvailabilityStatus"]],
        enable_batched_operations: Optional[bool],
        enable_express: Optional[bool],
        enable_partitioning: Optional[bool],
        lock_duration: Optional[Union[timedelta, str]],
        max_delivery_count: Optional[int],
        max_size_in_megabytes: Optional[int],
        requires_duplicate_detection: Optional[bool],
        requires_session: Optional[bool],
        status: Optional[Union[str, "EntityStatus"]],
        forward_to: Optional[str],
        user_metadata: Optional[str],
        forward_dead_lettered_messages_to: Optional[str],
        max_message_size_in_kilobytes: Optional[int],
    ) -> None:
        self.name = name
        self._internal_qd: InternalQueueDescription

        self.authorization_rules = authorization_rules
        self.auto_delete_on_idle = auto_delete_on_idle
        self.dead_lettering_on_message_expiration = dead_lettering_on_message_expiration
        self.default_message_time_to_live = default_message_time_to_live
        self.duplicate_detection_history_time_window = duplicate_detection_history_time_window
        self.availability_status = availability_status
        self.enable_batched_operations = enable_batched_operations
        self.enable_express = enable_express
        self.enable_partitioning = enable_partitioning
        self.lock_duration = lock_duration
        self.max_delivery_count = max_delivery_count
        self.max_size_in_megabytes = max_size_in_megabytes
        self.requires_duplicate_detection = requires_duplicate_detection
        self.requires_session = requires_session
        self.status = status
        self.forward_to = forward_to
        self.user_metadata = user_metadata
        self.forward_dead_lettered_messages_to = forward_dead_lettered_messages_to
        self.max_message_size_in_kilobytes = max_message_size_in_kilobytes

    @classmethod
    def _from_internal_entity(cls, name: str, internal_qd: InternalQueueDescription) -> "QueueProperties":
        qd = cls(
            name,
            authorization_rules=(
                [AuthorizationRule._from_internal_entity(r) for r in internal_qd.authorization_rules]
                if internal_qd.authorization_rules
                else None
            ),
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
            max_message_size_in_kilobytes=internal_qd.max_message_size_in_kilobytes,
        )

        qd._internal_qd = deepcopy(internal_qd)
        return qd

    def _to_internal_entity(
        self, fully_qualified_namespace: str, kwargs: Optional[Dict] = None
    ) -> InternalQueueDescription:
        kwargs = kwargs or {}

        if not hasattr(self, "_internal_qd"):
            internal_qd = InternalQueueDescription()
            self._internal_qd = internal_qd

        authorization_rules = kwargs.pop("authorization_rules", self.authorization_rules)
        self._internal_qd.authorization_rules = (
            [r._to_internal_entity() for r in authorization_rules] if authorization_rules else authorization_rules
        )

        self._internal_qd.auto_delete_on_idle = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("auto_delete_on_idle", self.auto_delete_on_idle)
        )
        self._internal_qd.dead_lettering_on_message_expiration = kwargs.pop(
            "dead_lettering_on_message_expiration",
            self.dead_lettering_on_message_expiration,
        )
        self._internal_qd.default_message_time_to_live = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("default_message_time_to_live", self.default_message_time_to_live)
        )
        self._internal_qd.duplicate_detection_history_time_window = kwargs.pop(
            "duplicate_detection_history_time_window",
            self.duplicate_detection_history_time_window,
        )
        self._internal_qd.entity_availability_status = kwargs.pop("availability_status", self.availability_status)
        self._internal_qd.enable_batched_operations = kwargs.pop(
            "enable_batched_operations", self.enable_batched_operations
        )
        self._internal_qd.enable_express = kwargs.pop("enable_express", self.enable_express)
        self._internal_qd.enable_partitioning = kwargs.pop("enable_partitioning", self.enable_partitioning)
        self._internal_qd.lock_duration = kwargs.pop("lock_duration", self.lock_duration)
        self._internal_qd.max_delivery_count = kwargs.pop("max_delivery_count", self.max_delivery_count)
        self._internal_qd.max_size_in_megabytes = kwargs.pop("max_size_in_megabytes", self.max_size_in_megabytes)
        self._internal_qd.requires_duplicate_detection = kwargs.pop(
            "requires_duplicate_detection", self.requires_duplicate_detection
        )
        self._internal_qd.requires_session = kwargs.pop("requires_session", self.requires_session)
        self._internal_qd.status = kwargs.pop("status", self.status)

        forward_to = kwargs.pop("forward_to", self.forward_to)
        self._internal_qd.forward_to = _normalize_entity_path_to_full_path_if_needed(
            forward_to, fully_qualified_namespace
        )

        forward_dead_lettered_messages_to = kwargs.pop(
            "forward_dead_lettered_messages_to", self.forward_dead_lettered_messages_to
        )
        self._internal_qd.forward_dead_lettered_messages_to = _normalize_entity_path_to_full_path_if_needed(
            forward_dead_lettered_messages_to, fully_qualified_namespace
        )

        self._internal_qd.user_metadata = kwargs.pop("user_metadata", self.user_metadata)
        self._internal_qd.max_message_size_in_kilobytes = kwargs.pop(
            "max_message_size_in_kilobytes", self.max_message_size_in_kilobytes
        )

        return self._internal_qd


class QueueRuntimeProperties(object):
    """Service Bus queue runtime properties."""

    def __init__(self) -> None:
        self._name: str
        self._internal_qr: InternalQueueDescription

    @classmethod
    def _from_internal_entity(cls, name: str, internal_qr: InternalQueueDescription) -> "QueueRuntimeProperties":
        qr = cls()
        qr._name = name
        qr._internal_qr = deepcopy(internal_qr)
        return qr

    @property
    def name(self) -> str:
        """Name of the queue.

        :rtype: str
        """
        return self._name

    @property
    def accessed_at_utc(self) -> Optional[datetime]:
        """Last time a message was sent, or the last time there was a receive request to this queue.

        :rtype:  ~datetime.datetime or None
        """
        return self._internal_qr.accessed_at

    @property
    def created_at_utc(self) -> Optional[datetime]:
        """The exact time the queue was created.

        :rtype: ~datetime.datetime or None
        """
        return self._internal_qr.created_at

    @property
    def updated_at_utc(self) -> Optional[datetime]:
        """The exact the entity was updated.

        :rtype: ~datetime.datetime or None
        """
        return self._internal_qr.updated_at

    @property
    def size_in_bytes(self) -> Optional[int]:
        """The size of the queue, in bytes.

        :rtype: int or None
        """
        return self._internal_qr.size_in_bytes

    @property
    def total_message_count(self) -> Optional[int]:
        """Total number of messages.

        :rtype: int or None
        """
        return self._internal_qr.message_count

    @property
    def active_message_count(self) -> Optional[int]:
        """Number of active messages in the queue, topic, or subscription.

        :rtype: int or None
        """
        return cast("MessageCountDetails", self._internal_qr.message_count_details).active_message_count

    @property
    def dead_letter_message_count(self) -> Optional[int]:
        """Number of messages that are dead lettered.

        :rtype: int or None
        """
        return cast("MessageCountDetails", self._internal_qr.message_count_details).dead_letter_message_count

    @property
    def scheduled_message_count(self) -> Optional[int]:
        """Number of scheduled messages.

        :rtype: int or None
        """
        return cast("MessageCountDetails", self._internal_qr.message_count_details).scheduled_message_count

    @property
    def transfer_dead_letter_message_count(self) -> Optional[int]:
        """Number of messages transferred into dead letters.

        :rtype: int or None
        """
        return cast("MessageCountDetails", self._internal_qr.message_count_details).transfer_dead_letter_message_count

    @property
    def transfer_message_count(self) -> Optional[int]:
        """Number of messages transferred to another queue, topic, or subscription.

        :rtype: int or None
        """
        return cast("MessageCountDetails", self._internal_qr.message_count_details).transfer_message_count


class TopicProperties(DictMixin):  # pylint:disable=too-many-instance-attributes
    """Properties of a Service Bus topic resource.

    **Please use `get_topic`, `create_topic`, or `list_topics` on the ServiceBusAdministrationClient
    to get a `TopicProperties` instance instead of instantiating a `TopicProperties` object directly.**

    :ivar name: Name of the topic.
    :type name: str
    :ivar default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :type default_message_time_to_live: ~datetime.timedelta or str or None
    :ivar max_size_in_megabytes: The maximum size of the topic in megabytes, which is the size of
     memory allocated for the topic.
    :type max_size_in_megabytes: float or None
    :ivar requires_duplicate_detection: A value indicating if this topic requires duplicate
     detection.
    :type requires_duplicate_detection: bool or None
    :ivar duplicate_detection_history_time_window: ISO 8601 timeSpan structure that defines the
     duration of the duplicate detection history. The default value is 10 minutes.
    :type duplicate_detection_history_time_window: ~datetime.timedelta or str or None
    :ivar enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :type enable_batched_operations: bool or None
    :ivar size_in_bytes: The size of the topic, in bytes.
    :type size_in_bytes: int or None
    :ivar filtering_messages_before_publishing: Filter messages before publishing.
    :type filtering_messages_before_publishing: bool or None
    :ivar authorization_rules: Authorization rules for resource.
    :type authorization_rules:
     list[~azure.servicebus.management.AuthorizationRule] or None
    :ivar status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :type status: str or ~azure.servicebus.management.EntityStatus or None
    :ivar support_ordering: A value that indicates whether the topic supports ordering.
    :type support_ordering: bool or None
    :ivar auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the topic is
     automatically deleted. The minimum duration is 5 minutes.
    :type auto_delete_on_idle: ~datetime.timedelta or str or None
    :ivar enable_partitioning: A value that indicates whether the topic is to be partitioned
     across multiple message brokers.
    :type enable_partitioning: bool or None
    :ivar availability_status: Availability status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type availability_status: str or None or
     ~azure.servicebus.management.EntityAvailabilityStatus
    :ivar enable_express: A value that indicates whether Express Entities are enabled. An express
     queue holds a message in memory temporarily before writing it to persistent storage.
    :type enable_express: bool or None
    :ivar user_metadata: Metadata associated with the topic.
    :type user_metadata: str or None
    :ivar max_message_size_in_kilobytes: The maximum size in kilobytes of message payload that
     can be accepted by the topic. This feature is only available when using a Premium namespace
     and Service Bus API version "2021-05" or higher.
    :type max_message_size_in_kilobytes: int or None
    """

    def __init__(
        self,
        name: str,
        *,
        default_message_time_to_live: Optional[Union[timedelta, str]],
        max_size_in_megabytes: Optional[int],
        requires_duplicate_detection: Optional[bool],
        duplicate_detection_history_time_window: Optional[Union[timedelta, str]],
        enable_batched_operations: Optional[bool],
        size_in_bytes: Optional[int],
        filtering_messages_before_publishing: Optional[bool],
        authorization_rules: Optional[List["AuthorizationRule"]],
        status: Optional[Union[str, "EntityStatus"]],
        support_ordering: Optional[bool],
        auto_delete_on_idle: Optional[Union[timedelta, str]],
        enable_partitioning: Optional[bool],
        availability_status: Optional[Union[str, "EntityAvailabilityStatus"]],
        enable_express: Optional[bool],
        user_metadata: Optional[str],
        max_message_size_in_kilobytes: Optional[int],
    ) -> None:
        self.name = name
        self._internal_td: InternalTopicDescription

        self.default_message_time_to_live = default_message_time_to_live
        self.max_size_in_megabytes = max_size_in_megabytes
        self.requires_duplicate_detection = requires_duplicate_detection
        self.duplicate_detection_history_time_window = duplicate_detection_history_time_window
        self.enable_batched_operations = enable_batched_operations
        self.size_in_bytes = size_in_bytes
        self.filtering_messages_before_publishing = filtering_messages_before_publishing
        self.authorization_rules = authorization_rules
        self.status = status
        self.support_ordering = support_ordering
        self.auto_delete_on_idle = auto_delete_on_idle
        self.enable_partitioning = enable_partitioning
        self.availability_status = availability_status
        self.enable_express = enable_express
        self.user_metadata = user_metadata
        self.max_message_size_in_kilobytes = max_message_size_in_kilobytes

    @classmethod
    def _from_internal_entity(cls, name: str, internal_td: InternalTopicDescription) -> "TopicProperties":
        td = cls(
            name,
            default_message_time_to_live=internal_td.default_message_time_to_live,
            max_size_in_megabytes=internal_td.max_size_in_megabytes,
            requires_duplicate_detection=internal_td.requires_duplicate_detection,
            duplicate_detection_history_time_window=internal_td.duplicate_detection_history_time_window,
            enable_batched_operations=internal_td.enable_batched_operations,
            size_in_bytes=internal_td.size_in_bytes,
            filtering_messages_before_publishing=internal_td.filtering_messages_before_publishing,
            authorization_rules=(
                [AuthorizationRule._from_internal_entity(r) for r in internal_td.authorization_rules]
                if internal_td.authorization_rules
                else None
            ),
            status=internal_td.status,
            support_ordering=internal_td.support_ordering,
            auto_delete_on_idle=internal_td.auto_delete_on_idle,
            enable_partitioning=internal_td.enable_partitioning,
            availability_status=internal_td.entity_availability_status,
            enable_express=internal_td.enable_express,
            user_metadata=internal_td.user_metadata,
            max_message_size_in_kilobytes=internal_td.max_message_size_in_kilobytes,
        )
        td._internal_td = deepcopy(internal_td)
        return td

    def _to_internal_entity(self, kwargs: Optional[Dict] = None) -> InternalTopicDescription:
        kwargs = kwargs or {}

        if not hasattr(self, "_internal_td"):
            self._internal_td = InternalTopicDescription()
        self._internal_td.default_message_time_to_live = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("default_message_time_to_live", self.default_message_time_to_live)
        )
        self._internal_td.max_size_in_megabytes = kwargs.pop("max_size_in_megabytes", self.max_size_in_megabytes)
        self._internal_td.requires_duplicate_detection = kwargs.pop(
            "requires_duplicate_detection", self.requires_duplicate_detection
        )
        self._internal_td.duplicate_detection_history_time_window = kwargs.pop(
            "duplicate_detection_history_time_window",
            self.duplicate_detection_history_time_window,
        )
        self._internal_td.enable_batched_operations = kwargs.pop(
            "enable_batched_operations", self.enable_batched_operations
        )
        self._internal_td.size_in_bytes = kwargs.pop("size_in_bytes", self.size_in_bytes)

        authorization_rules = kwargs.pop("authorization_rules", self.authorization_rules)
        self._internal_td.authorization_rules = (
            [r._to_internal_entity() for r in authorization_rules] if authorization_rules else authorization_rules
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
            "max_message_size_in_kilobytes", self.max_message_size_in_kilobytes
        )

        return self._internal_td


class TopicRuntimeProperties(object):
    """Runtime properties of a Service Bus topic resource."""

    def __init__(self) -> None:
        self._name: str
        self._internal_td: InternalTopicDescription

    @classmethod
    def _from_internal_entity(cls, name: str, internal_td: InternalTopicDescription) -> "TopicRuntimeProperties":
        qd = cls()
        qd._name = name
        qd._internal_td = internal_td
        return qd

    @property
    def name(self) -> str:
        """The name of the topic.

        :rtype: str
        """
        return self._name

    @property
    def accessed_at_utc(self) -> Optional[datetime]:
        """Last time a message was sent, or the last time there was a receive request

        :rtype: ~datetime.datetime or None
        """
        return self._internal_td.accessed_at

    @property
    def created_at_utc(self) -> Optional[datetime]:
        """The exact time the queue was created.

        :rtype: ~datetime.datetime or None
        """
        return self._internal_td.created_at

    @property
    def updated_at_utc(self) -> Optional[datetime]:
        """The exact time the entity was updated.

        :rtype: ~datetime.datetime or None
        """
        return self._internal_td.updated_at

    @property
    def size_in_bytes(self) -> Optional[int]:
        """The current size of the entity in bytes.

        :rtype: int or None
        """
        return self._internal_td.size_in_bytes

    @property
    def subscription_count(self) -> Optional[int]:
        """The number of subscriptions in the topic.

        :rtype: int or None
        """
        return self._internal_td.subscription_count

    @property
    def scheduled_message_count(self) -> Optional[int]:
        """Number of scheduled messages.

        :rtype: int or None
        """
        return cast("MessageCountDetails", self._internal_td.message_count_details).scheduled_message_count


class SubscriptionProperties(DictMixin):  # pylint:disable=too-many-instance-attributes
    """Properties of a Service Bus topic subscription resource.

    **Please use `get_subscription`, `create_subscription`, or `list_subscriptions` on the
    ServiceBusAdministrationClient to get a `SubscriptionProperties` instance instead of
    instantiating a `SubscriptionProperties` object directly.**

    :param name: Name of the subscription.
    :type name: str
    :keyword lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
     that the message is locked for other receivers. The maximum value for LockDuration is 5
     minutes; the default value is 1 minute.
    :paramtype lock_duration: ~datetime.timedelta or str or None
    :keyword requires_session: A value that indicates whether the queue supports the concept of
     sessions.
    :paramtype requires_session: bool or None
    :keyword default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :paramtype default_message_time_to_live: ~datetime.timedelta or str or None
    :keyword dead_lettering_on_message_expiration: A value that indicates whether this subscription
     has dead letter support when a message expires.
    :paramtype dead_lettering_on_message_expiration: bool or None
    :keyword dead_lettering_on_filter_evaluation_exceptions: A value that indicates whether this
     subscription has dead letter support when a message expires.
    :paramtype dead_lettering_on_filter_evaluation_exceptions: bool or None
    :keyword max_delivery_count: The maximum delivery count. A message is automatically deadlettered
     after this number of deliveries. Default value is 10.
    :paramtype max_delivery_count: int or None
    :keyword enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :paramtype enable_batched_operations: bool or None
    :keyword status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :paramtype status: str or ~azure.servicebus.management.EntityStatus or None
    :keyword forward_to: The name of the recipient entity to which all the messages sent to the
     subscription are forwarded to.
    :paramtype forward_to: str or None
    :keyword user_metadata: Metadata associated with the subscription. Maximum number of characters
     is 1024.
    :paramtype user_metadata: str or None
    :keyword forward_dead_lettered_messages_to: The name of the recipient entity to which all the
     messages sent to the subscription are forwarded to.
    :paramtype forward_dead_lettered_messages_to: str or None
    :keyword auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the subscription is
     automatically deleted. The minimum duration is 5 minutes.
    :paramtype auto_delete_on_idle: ~datetime.timedelta or str or None
    :keyword availability_status: Availability status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :paramtype availability_status: str or None or
     ~azure.servicebus.management.EntityAvailabilityStatus

    :ivar name: Name of the subscription.
    :vartype name: str
    :ivar lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
     that the message is locked for other receivers. The maximum value for LockDuration is 5
     minutes; the default value is 1 minute.
    :vartype lock_duration: ~datetime.timedelta or str or None
    :ivar requires_session: A value that indicates whether the queue supports the concept of
     sessions.
    :vartype requires_session: bool or None
    :ivar default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :vartype default_message_time_to_live: ~datetime.timedelta or str or None
    :ivar dead_lettering_on_message_expiration: A value that indicates whether this subscription
     has dead letter support when a message expires.
    :vartype dead_lettering_on_message_expiration: bool or None
    :ivar dead_lettering_on_filter_evaluation_exceptions: A value that indicates whether this
     subscription has dead letter support when a message expires.
    :vartype dead_lettering_on_filter_evaluation_exceptions: bool or None
    :ivar max_delivery_count: The maximum delivery count. A message is automatically deadlettered
     after this number of deliveries. Default value is 10.
    :vartype max_delivery_count: int or None
    :ivar enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :vartype enable_batched_operations: bool or None
    :ivar status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :vartype status: str or ~azure.servicebus.management.EntityStatus or None
    :ivar forward_to: The name of the recipient entity to which all the messages sent to the
     subscription are forwarded to.
    :vartype forward_to: str or None
    :ivar user_metadata: Metadata associated with the subscription. Maximum number of characters
     is 1024.
    :vartype user_metadata: str or None
    :ivar forward_dead_lettered_messages_to: The name of the recipient entity to which all the
     messages sent to the subscription are forwarded to.
    :vartype forward_dead_lettered_messages_to: str or None
    :ivar auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the subscription is
     automatically deleted. The minimum duration is 5 minutes.
    :vartype auto_delete_on_idle: ~datetime.timedelta or str or None
    :ivar availability_status: Availability status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :vartype availability_status: str or None or
     ~azure.servicebus.management.EntityAvailabilityStatus
    """

    def __init__(
        self,
        name: str,
        *,
        lock_duration: Optional[Union[timedelta, str]],
        requires_session: Optional[bool],
        default_message_time_to_live: Optional[Union[timedelta, str]],
        dead_lettering_on_message_expiration: Optional[bool],
        dead_lettering_on_filter_evaluation_exceptions: Optional[bool],
        max_delivery_count: Optional[int],
        enable_batched_operations: Optional[bool],
        status: Optional[Union[str, "EntityStatus"]],
        forward_to: Optional[str],
        user_metadata: Optional[str],
        forward_dead_lettered_messages_to: Optional[str],
        auto_delete_on_idle: Optional[Union[timedelta, str]],
        availability_status: Optional[Union[str, "EntityAvailabilityStatus"]],
    ) -> None:
        self.name = name
        self._internal_sd: InternalSubscriptionDescription

        self.lock_duration = lock_duration
        self.requires_session = requires_session
        self.default_message_time_to_live = default_message_time_to_live
        self.dead_lettering_on_message_expiration = dead_lettering_on_message_expiration
        self.dead_lettering_on_filter_evaluation_exceptions = dead_lettering_on_filter_evaluation_exceptions
        self.max_delivery_count = max_delivery_count
        self.enable_batched_operations = enable_batched_operations
        self.status = status
        self.forward_to = forward_to
        self.user_metadata = user_metadata
        self.forward_dead_lettered_messages_to = forward_dead_lettered_messages_to
        self.auto_delete_on_idle = auto_delete_on_idle
        self.availability_status = availability_status

    @classmethod
    def _from_internal_entity(
        cls, name: str, internal_subscription: InternalSubscriptionDescription
    ) -> "SubscriptionProperties":
        # pylint: disable=line-too-long
        subscription = cls(
            name,
            lock_duration=internal_subscription.lock_duration,
            requires_session=internal_subscription.requires_session,
            default_message_time_to_live=internal_subscription.default_message_time_to_live,
            dead_lettering_on_message_expiration=internal_subscription.dead_lettering_on_message_expiration,
            dead_lettering_on_filter_evaluation_exceptions=internal_subscription.dead_lettering_on_filter_evaluation_exceptions,
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

    def _to_internal_entity(
        self, fully_qualified_namespace: str, kwargs: Optional[Dict] = None
    ) -> InternalSubscriptionDescription:
        kwargs = kwargs or {}

        if not hasattr(self, "_internal_sd"):
            self._internal_sd = InternalSubscriptionDescription()
        self._internal_sd.lock_duration = kwargs.pop("lock_duration", self.lock_duration)
        self._internal_sd.requires_session = kwargs.pop("requires_session", self.requires_session)
        self._internal_sd.default_message_time_to_live = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("default_message_time_to_live", self.default_message_time_to_live)
        )
        self._internal_sd.dead_lettering_on_message_expiration = kwargs.pop(
            "dead_lettering_on_message_expiration",
            self.dead_lettering_on_message_expiration,
        )
        self._internal_sd.dead_lettering_on_filter_evaluation_exceptions = kwargs.pop(
            "dead_lettering_on_filter_evaluation_exceptions",
            self.dead_lettering_on_filter_evaluation_exceptions,
        )
        self._internal_sd.max_delivery_count = kwargs.pop("max_delivery_count", self.max_delivery_count)
        self._internal_sd.enable_batched_operations = kwargs.pop(
            "enable_batched_operations", self.enable_batched_operations
        )
        self._internal_sd.status = kwargs.pop("status", self.status)

        forward_to = kwargs.pop("forward_to", self.forward_to)
        self._internal_sd.forward_to = _normalize_entity_path_to_full_path_if_needed(
            forward_to, fully_qualified_namespace
        )

        forward_dead_lettered_messages_to = kwargs.pop(
            "forward_dead_lettered_messages_to", self.forward_dead_lettered_messages_to
        )
        self._internal_sd.forward_dead_lettered_messages_to = _normalize_entity_path_to_full_path_if_needed(
            forward_dead_lettered_messages_to, fully_qualified_namespace
        )

        self._internal_sd.user_metadata = kwargs.pop("user_metadata", self.user_metadata)
        self._internal_sd.auto_delete_on_idle = avoid_timedelta_overflow(  # type: ignore
            kwargs.pop("auto_delete_on_idle", self.auto_delete_on_idle)
        )
        self._internal_sd.entity_availability_status = kwargs.pop("availability_status", self.availability_status)

        return self._internal_sd


class SubscriptionRuntimeProperties(object):
    """Runtime properties of a Service Bus topic subscription resource."""

    def __init__(self) -> None:
        self._internal_sd: InternalSubscriptionDescription
        self._name: str

    @classmethod
    def _from_internal_entity(
        cls, name: str, internal_subscription: InternalSubscriptionDescription
    ) -> "SubscriptionRuntimeProperties":
        subscription = cls()
        subscription._name = name
        subscription._internal_sd = internal_subscription

        return subscription

    @property
    def name(self) -> str:
        """Name of subscription

        :rtype: str
        """
        return self._name

    @property
    def accessed_at_utc(self) -> Optional[datetime]:
        """Last time a message was sent, or the last time there was a receive request

        :rtype: ~datetime.datetime or None
        """
        return self._internal_sd.accessed_at

    @property
    def created_at_utc(self) -> Optional[datetime]:
        """The exact time the subscription was created.

        :rtype: ~datetime.datetime or None
        """
        return self._internal_sd.created_at

    @property
    def updated_at_utc(self) -> Optional[datetime]:
        """The exact time the entity is updated.

        :rtype: ~datetime.datetime or None
        """
        return self._internal_sd.updated_at

    @property
    def total_message_count(self) -> Optional[int]:
        """The number of messages in the subscription.

        :rtype: int or None
        """
        return self._internal_sd.message_count

    @property
    def active_message_count(self) -> Optional[int]:
        """Number of active messages in the subscription.

        :rtype: int or None
        """
        return cast("MessageCountDetails", self._internal_sd.message_count_details).active_message_count

    @property
    def dead_letter_message_count(self) -> Optional[int]:
        """Number of messages that are dead lettered.

        :rtype: int or None
        """
        return cast("MessageCountDetails", self._internal_sd.message_count_details).dead_letter_message_count

    @property
    def transfer_dead_letter_message_count(self) -> Optional[int]:
        """Number of messages transferred into dead letters.

        :rtype: int or None
        """
        return cast("MessageCountDetails", self._internal_sd.message_count_details).transfer_dead_letter_message_count

    @property
    def transfer_message_count(self) -> Optional[int]:
        """Number of messages transferred to another queue, topic, or subscription.

        :rtype: int or None
        """
        return cast("MessageCountDetails", self._internal_sd.message_count_details).transfer_message_count


class RuleProperties(DictMixin):
    """Properties of a topic subscription rule.

    **Please use `get_rule`, `create_rule`, or `list_rules` on the
    ServiceBusAdministrationClient to get a `RuleProperties` instance instead of
    instantiating a `RuleProperties` object directly.**

    :param name: Name of the rule.
    :type name: str
    :keyword filter: The filter of the rule.
    :paramtype filter: ~azure.servicebus.management.CorrelationRuleFilter or
     ~azure.servicebus.management.SqlRuleFilter or None
    :keyword action: The action of the rule.
    :paramtype action: ~azure.servicebus.management.SqlRuleAction or None
    :keyword created_at_utc: The exact time the rule was created.
    :paramtype created_at_utc: ~datetime.datetime or None

    :ivar name: Name of the rule.
    :vartype name: str
    :ivar filter: The filter of the rule.
    :vartype filter: ~azure.servicebus.management.CorrelationRuleFilter or
     ~azure.servicebus.management.SqlRuleFilter or None
    :ivar action: The action of the rule.
    :vartype action: ~azure.servicebus.management.SqlRuleAction or None
    :ivar created_at_utc: The exact time the rule was created.
    :vartype created_at_utc: ~datetime.datetime or None
    """

    def __init__(
        self,
        name: str,
        *,
        filter: Optional[Union["CorrelationRuleFilter", "SqlRuleFilter"]],
        action: Optional["SqlRuleAction"],
        created_at_utc: Optional[datetime],
    ) -> None:

        self.name = name
        self._internal_rule: InternalRuleDescription

        self.filter = filter
        self.action = action
        self.created_at_utc = created_at_utc

    @classmethod
    def _from_internal_entity(cls, name: str, internal_rule: InternalRuleDescription) -> "RuleProperties":
        rule = cls(
            name,
            filter=(
                RULE_CLASS_MAPPING[type(internal_rule.filter)]._from_internal_entity(internal_rule.filter)
                if internal_rule.filter and isinstance(internal_rule.filter, tuple(RULE_CLASS_MAPPING.keys()))
                else None
            ),
            action=(
                RULE_CLASS_MAPPING[type(internal_rule.action)]._from_internal_entity(internal_rule.action)
                if internal_rule.action and isinstance(internal_rule.action, tuple(RULE_CLASS_MAPPING.keys()))
                else None
            ),
            created_at_utc=internal_rule.created_at,
        )
        rule._internal_rule = deepcopy(internal_rule)
        return rule

    def _to_internal_entity(self, kwargs: Optional[Dict] = None) -> InternalRuleDescription:
        kwargs = kwargs or {}
        if not hasattr(self, "_internal_rule"):
            self._internal_rule = InternalRuleDescription()

        rule_filter = kwargs.pop("filter", self.filter)
        self._internal_rule.filter = rule_filter._to_internal_entity() if rule_filter else TRUE_FILTER  # type: ignore

        action = kwargs.pop("action", self.action)
        self._internal_rule.action = action._to_internal_entity() if action else EMPTY_RULE_ACTION

        self._internal_rule.created_at = kwargs.pop("created_at_utc", self.created_at_utc)
        self._internal_rule.name = kwargs.pop("name", self.name)

        return self._internal_rule


class CorrelationRuleFilter(object):
    """Represents the correlation filter expression.

    :keyword correlation_id: Identifier of the correlation.
    :paramtype correlation_id: str or None
    :keyword message_id: Identifier of the message.
    :paramtype message_id: str or None
    :keyword to: Address to send to.
    :paramtype to: str or None
    :keyword reply_to: Address of the queue to reply to.
    :paramtype reply_to: str or None
    :keyword label: Application specific label.
    :paramtype label: str or None
    :keyword session_id: Session identifier.
    :paramtype session_id: str or None
    :keyword reply_to_session_id: Session identifier to reply to.
    :paramtype reply_to_session_id: str or None
    :keyword content_type: Content type of the message.
    :paramtype content_type: str or None
    :keyword properties: dictionary object for custom filters
    :paramtype properties: dict[str, Union[str, int, float, bool, datetime, timedelta]] or None
    """

    def __init__(
        self,
        *,
        correlation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        to: Optional[str] = None,
        reply_to: Optional[str] = None,
        label: Optional[str] = None,
        session_id: Optional[str] = None,
        reply_to_session_id: Optional[str] = None,
        content_type: Optional[str] = None,
        properties: Optional[Dict[str, Union[str, int, float, bool, datetime, timedelta]]] = None,
    ) -> None:
        self.correlation_id = correlation_id
        self.message_id = message_id
        self.to = to
        self.reply_to = reply_to
        self.label = label
        self.session_id = session_id
        self.reply_to_session_id = reply_to_session_id
        self.content_type = content_type
        self.properties = properties

    @classmethod
    def _from_internal_entity(cls, internal_correlation_filter: InternalCorrelationFilter) -> "CorrelationRuleFilter":
        correlation_filter = cls()
        correlation_filter.correlation_id = internal_correlation_filter.correlation_id
        correlation_filter.message_id = internal_correlation_filter.message_id
        correlation_filter.to = internal_correlation_filter.to
        correlation_filter.reply_to = internal_correlation_filter.reply_to
        correlation_filter.label = internal_correlation_filter.label
        correlation_filter.session_id = internal_correlation_filter.session_id
        correlation_filter.reply_to_session_id = internal_correlation_filter.reply_to_session_id
        correlation_filter.content_type = internal_correlation_filter.content_type
        correlation_filter.properties = (
            OrderedDict((kv.key, kv.value) for kv in internal_correlation_filter.properties)
            if internal_correlation_filter.properties
            else OrderedDict()
        )

        return correlation_filter

    def _to_internal_entity(self) -> InternalCorrelationFilter:
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
            [KeyObjectValue(key=key, value=value) for key, value in self.properties.items()]
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

    def __init__(
        self,
        sql_expression: Optional[str] = None,
        parameters: Optional[Dict[str, Union[str, int, float, bool, datetime, timedelta]]] = None,
    ) -> None:
        self.sql_expression = sql_expression
        self.parameters = parameters
        self.requires_preprocessing = True

    @classmethod
    def _from_internal_entity(cls, internal_sql_rule_filter):
        sql_rule_filter = cls()
        sql_rule_filter.sql_expression = internal_sql_rule_filter.sql_expression
        sql_rule_filter.parameters = (
            OrderedDict((kv.key, kv.value) for kv in internal_sql_rule_filter.parameters)
            if internal_sql_rule_filter.parameters
            else OrderedDict()
        )
        sql_rule_filter.requires_preprocessing = internal_sql_rule_filter.requires_preprocessing
        return sql_rule_filter

    def _to_internal_entity(self) -> InternalSqlFilter:
        internal_entity = InternalSqlFilter(sql_expression=self.sql_expression)
        internal_entity.parameters = (
            [KeyValue(key=key, value=value) for key, value in self.parameters.items()]  # type: ignore
            if self.parameters
            else None
        )
        internal_entity.compatibility_level = RULE_SQL_COMPATIBILITY_LEVEL
        internal_entity.requires_preprocessing = self.requires_preprocessing
        return internal_entity


class TrueRuleFilter(SqlRuleFilter):
    """A sql filter with a sql expression that is always True"""

    def __init__(self) -> None:
        super(TrueRuleFilter, self).__init__("1=1", None)

    def _to_internal_entity(self):
        internal_entity = InternalTrueFilter()
        internal_entity.sql_expression = self.sql_expression
        internal_entity.requires_preprocessing = True
        internal_entity.compatibility_level = RULE_SQL_COMPATIBILITY_LEVEL

        return internal_entity


class FalseRuleFilter(SqlRuleFilter):
    """A sql filter with a sql expression that is always True"""

    def __init__(self) -> None:
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
    """

    def __init__(
        self,
        sql_expression: Optional[str] = None,
        parameters: Optional[Dict[str, Union[str, int, float, bool, datetime, timedelta]]] = None,
    ) -> None:
        self.sql_expression = sql_expression
        self.parameters = parameters
        self.requires_preprocessing = True

    @classmethod
    def _from_internal_entity(cls, internal_sql_rule_action):
        sql_rule_action = cls()
        sql_rule_action.sql_expression = internal_sql_rule_action.sql_expression
        sql_rule_action.parameters = (
            OrderedDict((kv.key, kv.value) for kv in internal_sql_rule_action.parameters)
            if internal_sql_rule_action.parameters
            else OrderedDict()
        )
        sql_rule_action.requires_preprocessing = internal_sql_rule_action.requires_preprocessing
        return sql_rule_action

    def _to_internal_entity(self):
        internal_entity = InternalSqlRuleAction(sql_expression=self.sql_expression)
        internal_entity.parameters = (
            [KeyValue(key=key, value=value) for key, value in self.parameters.items()] if self.parameters else None
        )
        internal_entity.compatibility_level = RULE_SQL_COMPATIBILITY_LEVEL
        internal_entity.requires_preprocessing = self.requires_preprocessing
        return internal_entity


RULE_CLASS_MAPPING: Dict[Type[Model], Type] = {
    InternalSqlRuleAction: SqlRuleAction,
    # InternalEmptyRuleAction: None,
    InternalCorrelationFilter: CorrelationRuleFilter,
    InternalSqlFilter: SqlRuleFilter,
    InternalTrueFilter: TrueRuleFilter,
    InternalFalseFilter: FalseRuleFilter,
}
EMPTY_RULE_ACTION = InternalEmptyRuleAction()
TRUE_FILTER = TrueRuleFilter()


class AuthorizationRule(object):
    """Authorization rule of an entity.

    :keyword type: The authorization type.
    :paramtype type: str
    :keyword claim_type: The claim type.
    :paramtype claim_type: str
    :keyword claim_value: The claim value.
    :paramtype claim_value: str
    :keyword rights: Access rights of the entity. Values are 'Send', 'Listen', or 'Manage'.
    :paramtype rights: list[AccessRights]
    :keyword created_at_utc: The date and time when the authorization rule was created.
    :paramtype created_at_utc: ~datetime.datetime
    :keyword modified_at_utc: The date and time when the authorization rule was modified.
    :paramtype modified_at_utc: ~datetime.datetime
    :keyword key_name: The authorization rule key name.
    :paramtype key_name: str
    :keyword primary_key: The primary key of the authorization rule.
    :paramtype primary_key: str
    :keyword secondary_key: The primary key of the authorization rule.
    :paramtype secondary_key: str
    """

    def __init__(
        self,
        *,
        type: Optional[str] = None,
        claim_type: Optional[str] = None,
        claim_value: Optional[str] = None,
        rights: Optional[List[Union[str, "AccessRights"]]] = None,
        created_at_utc: Optional[datetime] = None,
        modified_at_utc: Optional[datetime] = None,
        key_name: Optional[str] = None,
        primary_key: Optional[str] = None,
        secondary_key: Optional[str] = None,
    ) -> None:
        self.type = type
        self.claim_type = claim_type
        self.claim_value = claim_value
        self.rights = rights
        self.created_at_utc = created_at_utc
        self.modified_at_utc = modified_at_utc
        self.key_name = key_name
        self.primary_key = primary_key
        self.secondary_key = secondary_key

    @classmethod
    def _from_internal_entity(cls, internal_authorization_rule: InternalAuthorizationRule) -> "AuthorizationRule":
        authorization_rule = cls()
        authorization_rule.type = internal_authorization_rule.type
        authorization_rule.claim_type = internal_authorization_rule.claim_type
        authorization_rule.claim_value = internal_authorization_rule.claim_value
        authorization_rule.rights = internal_authorization_rule.rights
        authorization_rule.created_at_utc = internal_authorization_rule.created_time
        authorization_rule.modified_at_utc = internal_authorization_rule.modified_time
        authorization_rule.key_name = internal_authorization_rule.key_name
        authorization_rule.primary_key = internal_authorization_rule.primary_key
        authorization_rule.secondary_key = internal_authorization_rule.secondary_key

        return authorization_rule

    def _to_internal_entity(self) -> InternalAuthorizationRule:
        internal_entity = InternalAuthorizationRule()
        internal_entity.type = self.type
        internal_entity.claim_type = self.claim_type
        internal_entity.claim_value = self.claim_value
        internal_entity.rights = self.rights
        internal_entity.created_time = self.created_at_utc
        internal_entity.modified_time = self.modified_at_utc
        internal_entity.key_name = self.key_name
        internal_entity.primary_key = self.primary_key
        internal_entity.secondary_key = self.secondary_key
        return internal_entity
