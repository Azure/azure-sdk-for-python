# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import uuid
from typing import Optional, Callable

from .._pyamqp.endpoints import Source
from .._pyamqp.error import AMQPError

from .message import ServiceBusReceivedMessage
from ..exceptions import _ServiceBusErrorPolicy, MessageAlreadySettled
from .constants import (
    NEXT_AVAILABLE_SESSION,
    SESSION_FILTER,
    SESSION_LOCKED_UNTIL,
    DATETIMEOFFSET_EPOCH,
    MGMT_REQUEST_SESSION_ID,
    ServiceBusReceiveMode,
    DEADLETTERNAME,
    RECEIVER_LINK_DEAD_LETTER_REASON,
    RECEIVER_LINK_DEAD_LETTER_ERROR_DESCRIPTION,
    MESSAGE_COMPLETE,
    MESSAGE_DEAD_LETTER,
    MESSAGE_ABANDON,
    MESSAGE_DEFER,
)
from .utils import utc_from_timestamp, utc_now


class ReceiverMixin(object):  # pylint: disable=too-many-instance-attributes
    def _populate_attributes(self, **kwargs):
        if kwargs.get("subscription_name"):
            self._subscription_name = kwargs.get("subscription_name")
            self._is_subscription = True
            self.entity_path = (
                self._entity_name + "/Subscriptions/" + self._subscription_name
            )
        else:
            self.entity_path = self._entity_name

        self._auth_uri = "sb://{}/{}".format(
            self.fully_qualified_namespace, self.entity_path
        )
        self._entity_uri = "amqps://{}/{}".format(
            self.fully_qualified_namespace, self.entity_path
        )
        self._receive_mode = ServiceBusReceiveMode(
            kwargs.get("receive_mode", ServiceBusReceiveMode.PEEK_LOCK)
        )

        self._session_id = kwargs.get("session_id")

        # TODO: What's the retry overlap between servicebus and pyamqp?
        self._error_policy = _ServiceBusErrorPolicy(
            is_session=bool(self._session_id),
            retry_total=self._config.retry_total,
            retry_mode = self._config.retry_mode,
            retry_backoff_factor = self._config.retry_backoff_factor,
            retry_backoff_max = self._config.retry_backoff_max
        )

        self._name = "SBReceiver-{}".format(uuid.uuid4())
        self._last_received_sequenced_number = None
        self._message_iter = None
        self._connection = kwargs.get("connection")
        prefetch_count = kwargs.get("prefetch_count", 0)
        if int(prefetch_count) < 0 or int(prefetch_count) > 50000:
            raise ValueError(
                "prefetch_count must be an integer between 0 and 50000 inclusive."
            )
        self._prefetch_count = prefetch_count + 1
        # The relationship between the amount can be received and the time interval is linear: amount ~= perf * interval
        # In large max_message_count case, like 5000, the pull receive would always return hundreds of messages limited
        # by the perf and time.
        self._further_pull_receive_timeout_ms = 200
        max_wait_time = kwargs.get("max_wait_time", None)
        if max_wait_time is not None and max_wait_time <= 0:
            raise ValueError("The max_wait_time must be greater than 0.")
        self._max_wait_time = max_wait_time

        self._auto_lock_renewer = kwargs.get("auto_lock_renewer", None)
        if (
            self._auto_lock_renewer
            and self._receive_mode == ServiceBusReceiveMode.RECEIVE_AND_DELETE
            and self._session_id is None
        ):
            raise ValueError(
                "Messages received in RECEIVE_AND_DELETE receive mode cannot have their locks removed "
                "as they have been deleted, providing an AutoLockRenewer in this mode is invalid."
            )

    def _build_message(self, received, message_type=ServiceBusReceivedMessage):
        message = message_type(
            message=received[1], receive_mode=self._receive_mode, receiver=self, frame=received[0]
        )
        self._last_received_sequenced_number = message.sequence_number
        return message

    def _get_source(self):
        # pylint: disable=protected-access
        if self._session:
            session_filter = None if self._session_id == NEXT_AVAILABLE_SESSION else self._session_id
            filter_map = {SESSION_FILTER: session_filter}
            source = Source(
                address=self._entity_uri,
                filters=filter_map
            )
            return source
        return self._entity_uri

    def _check_message_alive(self, message, action):
        # pylint: disable=no-member, protected-access
        if message._is_peeked_message:
            raise ValueError(
                "The operation {} is not supported for peeked messages."
                "Only messages received using receive methods in PEEK_LOCK mode can be settled.".format(
                    action
                )
            )

        if self._receive_mode == ServiceBusReceiveMode.RECEIVE_AND_DELETE:
            raise ValueError(
                "The operation {} is not supported in 'RECEIVE_AND_DELETE' receive mode.".format(
                    action
                )
            )

        if message._settled:
            raise MessageAlreadySettled(action=action)

        if not self._running:
            raise ValueError(
                "Failed to {} the message as the handler has already been shutdown."
                "Please use ServiceBusClient to create a new instance.".format(action)
            )

    def _settle_message_via_receiver_link(
        self,
        message,
        settle_operation,
        dead_letter_reason=None,
        dead_letter_error_description=None,
    ):
        # type: (ServiceBusReceivedMessage, str, Optional[str], Optional[str]) -> None
        if settle_operation == MESSAGE_COMPLETE:
            return self._handler.settle_messages(message.delivery_id, 'accepted')
        if settle_operation == MESSAGE_ABANDON:
            return self._handler.settle_messages(
                message.delivery_id,
                'modified',
                delivery_failed=True,
                undeliverable_here=False
            )
        if settle_operation == MESSAGE_DEAD_LETTER:
            return self._handler.settle_messages(
                message.delivery_id,
                'rejected',
                error=AMQPError(
                    condition=DEADLETTERNAME,
                    description=dead_letter_error_description,
                    info={
                        RECEIVER_LINK_DEAD_LETTER_REASON: dead_letter_reason,
                        RECEIVER_LINK_DEAD_LETTER_ERROR_DESCRIPTION: dead_letter_error_description,
                    }
                )
            )
        if settle_operation == MESSAGE_DEFER:
            return self._handler.settle_messages(
                message.delivery_id,
                'modified',
                delivery_failed=True,
                undeliverable_here=True
            )
        raise ValueError(
            "Unsupported settle operation type: {}".format(settle_operation)
        )

    def _on_attach(self, attach_frame):
        # pylint: disable=protected-access, unused-argument
        if self._session and attach_frame.source.address.decode(self._config.encoding) == self._entity_uri:
            # This has to live on the session object so that autorenew has access to it.
            self._session._session_start = utc_now()
            expiry_in_seconds = attach_frame.properties.get(SESSION_LOCKED_UNTIL)
            if expiry_in_seconds:
                expiry_in_seconds = (
                    expiry_in_seconds - DATETIMEOFFSET_EPOCH
                ) / 10000000
                self._session._locked_until_utc = utc_from_timestamp(expiry_in_seconds)
            session_filter = attach_frame.source.filters[SESSION_FILTER]
            self._session_id = session_filter.decode(self._config.encoding)
            self._session._session_id = self._session_id

    def _populate_message_properties(self, message):
        if self._session:
            message[MGMT_REQUEST_SESSION_ID] = self._session_id

    def _enhanced_message_received(self, frame, message):
        # pylint: disable=protected-access
        self._handler._was_message_received = True
        if self._receive_context.is_set():
            self._handler._received_messages.put((frame, message))
        else:
            self._handler.settle_messages(frame[1], 'released')
