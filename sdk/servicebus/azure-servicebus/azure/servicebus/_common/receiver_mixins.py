# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import uuid
from typing import TYPE_CHECKING

from ..exceptions import MessageAlreadySettled
from .constants import (
    NEXT_AVAILABLE_SESSION,
    MGMT_REQUEST_SESSION_ID,
    ServiceBusReceiveMode,
)

if TYPE_CHECKING:
    from .._transport._base import AmqpTransport

class ReceiverMixin(object):  # pylint: disable=too-many-instance-attributes
    def _populate_attributes(self, **kwargs):
        self._amqp_transport: "AmqpTransport"
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

        self._error_policy = self._amqp_transport.create_retry_policy(
            config=self._config,
            is_session=bool(self._session_id)
        )

        self._name = kwargs.get("client_identifier", "SBReceiver-{}".format(uuid.uuid4()))
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
        self._further_pull_receive_timeout = 0.2 * self._amqp_transport.TIMEOUT_FACTOR
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

    def _get_source(self):
        # pylint: disable=protected-access
        if self._session:
            session_filter = None if self._session_id == NEXT_AVAILABLE_SESSION else self._session_id
            return self._amqp_transport.create_source(self._entity_uri, session_filter)
        return self._entity_uri

    def _check_message_alive(self, message, action):
        # pylint: disable=no-member, protected-access
        if message._is_peeked_message:
            raise ValueError(
                f"The operation {action} is not supported for peeked messages."
                "Only messages received using receive methods in PEEK_LOCK mode can be settled."
            )

        if self._receive_mode == ServiceBusReceiveMode.RECEIVE_AND_DELETE:
            raise ValueError(
                f"The operation {action} is not supported in 'RECEIVE_AND_DELETE' receive mode."
            )

        if message._settled:
            raise MessageAlreadySettled(action=action)

        if not self._running:
            raise ValueError(
                f"Failed to {action} the message as the handler has already been shutdown."
                "Please use ServiceBusClient to create a new instance."
            )

    def _populate_message_properties(self, message):
        if self._session:
            message[MGMT_REQUEST_SESSION_ID] = self._session_id
