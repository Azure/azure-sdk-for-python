# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import uuid
from uamqp import Source
from .message import ReceivedMessage
from .constants import (
    NEXT_AVAILABLE,
    SESSION_FILTER,
    SESSION_LOCKED_UNTIL,
    DATETIMEOFFSET_EPOCH,
    MGMT_REQUEST_SESSION_ID,
    ReceiveMode
)
from ..exceptions import (
    _ServiceBusErrorPolicy,
    SessionLockExpired
)
from .utils import utc_from_timestamp, utc_now


class ReceiverMixin(object):  # pylint: disable=too-many-instance-attributes
    def _populate_attributes(self, **kwargs):
        if kwargs.get("subscription_name"):
            self._subscription_name = kwargs.get("subscription_name")
            self._is_subscription = True
            self.entity_path = self._entity_name + "/Subscriptions/" + self._subscription_name
        else:
            self.entity_path = self._entity_name

        self._auth_uri = "sb://{}/{}".format(self.fully_qualified_namespace, self.entity_path)
        self._entity_uri = "amqps://{}/{}".format(self.fully_qualified_namespace, self.entity_path)
        self._receive_mode = kwargs.get("receive_mode", ReceiveMode.PeekLock)
        self._error_policy = _ServiceBusErrorPolicy(
            max_retries=self._config.retry_total
        )
        self._name = "SBReceiver-{}".format(uuid.uuid4())
        self._last_received_sequenced_number = None
        self._message_iter = None
        self._connection = kwargs.get("connection")
        prefetch_count = kwargs.get("prefetch_count", 0)
        if int(prefetch_count) < 0 or int(prefetch_count) > 50000:
            raise ValueError("prefetch_count must be an integer between 0 and 50000 inclusive.")
        self._prefetch_count = prefetch_count + 1
        # The relationship between the amount can be received and the time interval is linear: amount ~= perf * interval
        # In large max_message_count case, like 5000, the pull receive would always return hundreds of messages limited
        # by the perf and time.
        self._further_pull_receive_timeout_ms = 200
        self._max_wait_time = kwargs.get("max_wait_time", None)

    def _build_message(self, received, message_type=ReceivedMessage):
        message = message_type(message=received, receive_mode=self._receive_mode, receiver=self)
        self._last_received_sequenced_number = message.sequence_number
        return message

    def _check_live(self):
        """check whether the receiver is alive"""

    def _get_source(self):
        return self._entity_uri

    def _on_attach(self, source, target, properties, error):
        pass

    def _populate_message_properties(self, message):
        pass


class SessionReceiverMixin(ReceiverMixin):
    def _get_source(self):
        source = Source(self._entity_uri)
        session_filter = None if self._session_id == NEXT_AVAILABLE else self._session_id
        source.set_filter(session_filter, name=SESSION_FILTER, descriptor=None)
        return source

    def _on_attach(self, source, target, properties, error):  # pylint: disable=unused-argument
        # pylint: disable=protected-access
        if str(source) == self._entity_uri:
            # This has to live on the session object so that autorenew has access to it.
            self._session._session_start = utc_now()
            expiry_in_seconds = properties.get(SESSION_LOCKED_UNTIL)
            if expiry_in_seconds:
                expiry_in_seconds = (expiry_in_seconds - DATETIMEOFFSET_EPOCH)/10000000
                self._session._locked_until_utc = utc_from_timestamp(expiry_in_seconds)
            session_filter = source.get_filter(name=SESSION_FILTER)
            self._session_id = session_filter.decode(self._config.encoding)
            self._session._session_id = self._session_id

    def _check_live(self):
        if self._session and self._session._lock_expired:  # pylint: disable=protected-access
            raise SessionLockExpired(inner_exception=self._session.auto_renew_error)

    def _populate_session_attributes(self, **kwargs):
        self._session_id = kwargs.get("session_id") or NEXT_AVAILABLE
        self._error_policy = _ServiceBusErrorPolicy(
            max_retries=self._config.retry_total,
            is_session=bool(self._session_id)
        )

    def _populate_message_properties(self, message):
        message[MGMT_REQUEST_SESSION_ID] = self._session_id
