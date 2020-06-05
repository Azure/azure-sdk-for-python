# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._generated.models import QueueDescription as InternalQueueDescription


class AuthorizationRule:
    """Authorization rule of an entity.

    :param claim_type:
    :type claim_type: str
    :param created_time:
    :type created_time: ~datetime.datetime
    :param key_name:
    :type key_name: str
    :param modified_time:
    :type modified_time: ~datetime.datetime
    :param rights: Access rights of the entity.
    :type rights: list[str]
    """
    def __init__(
        self,
        **kwargs
    ):
        super(AuthorizationRule, self).__init__(**kwargs)
        self.claim_type = kwargs.get('claim_type', None)
        self.created_time = kwargs.get('created_time', None)
        self.key_name = kwargs.get('key_name', None)
        self.modified_time = kwargs.get('modified_time', None)
        self.rights = kwargs.get('rights', None)


class MessageCountDetails(object):
    """Details about the message counts in queue.

    :param active_message_count: Number of active messages in the queue, topic, or subscription.
    :type active_message_count: int
    :param dead_letter_message_count: Number of messages that are dead lettered.
    :type dead_letter_message_count: int
    :param scheduled_message_count: Number of scheduled messages.
    :type scheduled_message_count: int
    :param transfer_dead_letter_message_count: Number of messages transferred into dead letters.
    :type transfer_dead_letter_message_count: int
    :param transfer_message_count: Number of messages transferred to another queue, topic, or
     subscription.
    :type transfer_message_count: int
    """

    def __init__(
        self,
        **kwargs
    ):
        super(MessageCountDetails, self).__init__(**kwargs)
        self.active_message_count = kwargs.get('active_message_count', None)
        self.dead_letter_message_count = kwargs.get('dead_letter_message_count', None)
        self.scheduled_message_count = kwargs.get('scheduled_message_count', None)
        self.transfer_dead_letter_message_count = kwargs.get('transfer_dead_letter_message_count', None)
        self.transfer_message_count = kwargs.get('transfer_message_count', None)


class QueueDescription(object):  # pylint:disable=too-many-instance-attributes
    """Description of a Service Bus queue resource.

    :param queue_name: Name of the queue.
    :type queue_name: str
    :param authorization_rules: Authorization rules for resource.
    :type authorization_rules: list[~azure.service._control_client2.models.AuthorizationRule]
    :param auto_delete_on_idle: ISO 8601 timeSpan idle interval after which the queue is
     automatically deleted. The minimum duration is 5 minutes.
    :type auto_delete_on_idle: ~datetime.timedelta
    :param dead_lettering_on_message_expiration: A value that indicates whether this queue has dead
     letter support when a message expires.
    :type dead_lettering_on_message_expiration: bool
    :param default_message_time_to_live: ISO 8601 default message timespan to live value. This is
     the duration after which the message expires, starting from when the message is sent to Service
     Bus. This is the default value used when TimeToLive is not set on a message itself.
    :type default_message_time_to_live: ~datetime.timedelta
    :param duplicate_detection_history_time_window: ISO 8601 timeSpan structure that defines the
     duration of the duplicate detection history. The default value is 10 minutes.
    :type duplicate_detection_history_time_window: ~datetime.timedelta
    :param entity_availability_status: Availibility status of the entity. Possible values include:
     "Available", "Limited", "Renaming", "Restoring", "Unknown".
    :type entity_availability_status: str or
     ~azure.service._control_client2.models.EntityAvailabilityStatus
    :param enable_batched_operations: Value that indicates whether server-side batched operations
     are enabled.
    :type enable_batched_operations: bool
    :param enable_express: A value that indicates whether Express Entities are enabled. An express
     queue holds a message in memory temporarily before writing it to persistent storage.
    :type enable_express: bool
    :param enable_partitioning: A value that indicates whether the queue is to be partitioned
     across multiple message brokers.
    :type enable_partitioning: bool
    :param is_anonymous_accessible: A value indicating if the resource can be accessed without
     authorization.
    :type is_anonymous_accessible: bool
    :param lock_duration: ISO 8601 timespan duration of a peek-lock; that is, the amount of time
     that the message is locked for other receivers. The maximum value for LockDuration is 5
     minutes; the default value is 1 minute.
    :type lock_duration: ~datetime.timedelta
    :param max_delivery_count: The maximum delivery count. A message is automatically deadlettered
     after this number of deliveries. Default value is 10.
    :type max_delivery_count: int
    :param max_size_in_megabytes: The maximum size of the queue in megabytes, which is the size of
     memory allocated for the queue.
    :type max_size_in_megabytes: int
    :param requires_duplicate_detection: A value indicating if this queue requires duplicate
     detection.
    :type requires_duplicate_detection: bool
    :param requires_session: A value that indicates whether the queue supports the concept of
     sessions.
    :type requires_session: bool
    :param status: Status of a Service Bus resource. Possible values include: "Active", "Creating",
     "Deleting", "Disabled", "ReceiveDisabled", "Renaming", "Restoring", "SendDisabled", "Unknown".
    :type status: str or ~azure.service._control_client2.models.EntityStatus
    :param support_ordering: A value that indicates whether the queue supports ordering.
    :type support_ordering: bool
    """

    def __init__(
        self,
        **kwargs
    ):
        self.queue_name = kwargs.get('queue_name', None)
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
        self.created_at = kwargs.get('created_at', None)

    @classmethod
    def _from_internal_entity(cls, internal_qd):
        # type: (InternalQueueDescription) -> QueueDescription
        qd = cls()
        qd._internal_qd = internal_qd  # pylint:disable=protected-access

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
        qd.created_at = internal_qd.created_at

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
        self._internal_qd.created_at = self.created_at

        return self._internal_qd


class QueueRuntimeInfo(object):
    """Service Bus queue metrics.

    :param queue_name: Name of the queue.
    :type queue_name: str
    :param accessed_at: Last time a message was sent, or the last time there was a receive request
     to this queue.
    :type accessed_at: ~datetime.datetime
    :param created_at: The exact time the queue was created.
    :type created_at: ~datetime.datetime
    :param updated_at: The exact time a message was updated in the queue.
    :type updated_at: ~datetime.datetime
    :param size_in_bytes: The size of the queue, in bytes.
    :type size_in_bytes: int
    :param message_count: The number of messages in the queue.
    :type message_count: int
    :param message_count_details: Details about the message counts in queue.
    :type message_count_details: ~azure.service._control_client2.models.MessageCountDetails
    """

    def __init__(
        self,
        **kwargs
    ):
        self.queue_name = kwargs.get('queue_name', None)
        self._internal_qr = None

        self.accessed_at = kwargs.get('accessed_at', None)
        self.created_at = kwargs.get('created_at', None)
        self.updated_at = kwargs.get('updated_at', None)
        self.size_in_bytes = kwargs.get('size_in_bytes', None)
        self.message_count = kwargs.get('message_count', None)
        self.message_count_details = kwargs.get('message_count_details', None)

    @classmethod
    def _from_internal_entity(cls, internal_qr):
        # type: (InternalQueueDescription) -> QueueRuntimeInfo
        qr = cls()
        qr._internal_qr = internal_qr  # pylint:disable=protected-access

        qr.accessed_at = internal_qr.accessed_at
        qr.created_at = internal_qr.created_at
        qr.updated_at = internal_qr.updated_at
        qr.size_in_bytes = internal_qr.size_in_bytes
        qr.message_count = internal_qr.message_count
        qr.message_count_details = internal_qr.message_count_details

        return qr
