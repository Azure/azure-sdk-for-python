# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import datetime
from typing import TYPE_CHECKING, Union, Optional
import six

from ._common.utils import utc_from_timestamp, utc_now
from ._common.constants import (
    REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION,
    REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
    REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
    MGMT_RESPONSE_SESSION_STATE,
    MGMT_RESPONSE_RECEIVER_EXPIRATION,
    MGMT_REQUEST_SESSION_ID,
    MGMT_REQUEST_SESSION_STATE,
)
from .exceptions import SessionLockExpired
from ._common import mgmt_handlers

if TYPE_CHECKING:
    from ._servicebus_session_receiver import ServiceBusSessionReceiver
    from .aio._servicebus_session_receiver_async import ServiceBusSessionReceiver as ServiceBusSessionReceiverAsync

_LOGGER = logging.getLogger(__name__)


class BaseSession(object):
    def __init__(self, session_id, receiver, encoding="UTF-8"):
        # type: (str, Union[ServiceBusSessionReceiver, ServiceBusSessionReceiverAsync], str) -> None
        self._id = session_id
        self._receiver = receiver
        self._encoding = encoding
        self._session_start = None
        self._locked_until_utc = None  # type: Optional[datetime.datetime]
        self.auto_renew_error = None

    def _check_live(self):
        if self._lock_expired:
            raise SessionLockExpired(inner_exception=self.auto_renew_error)

    @property
    def _lock_expired(self):
        # type: () -> bool
        """Whether the receivers lock on a particular session has expired.

        :rtype: bool
        """
        return bool(self._locked_until_utc and self._locked_until_utc <= utc_now())

    @property
    def session_id(self):
        # type: () -> str
        """
        Session id of the current session.

        :rtype: str
        """
        return self._id

    @property
    def locked_until_utc(self):
        # type: () -> Optional[datetime.datetime]
        """The time at which this session's lock will expire.

        :rtype: datetime.datetime
        """
        return self._locked_until_utc


class ServiceBusSession(BaseSession):
    """
    The ServiceBusSession is used for manage session states and lock renewal.

    **Please use the instance variable `session` on the ServiceBusReceiver to get the corresponding ServiceBusSession
    object linked with the receiver instead of instantiating a ServiceBusSession object directly.**

    :ivar auto_renew_error: Error when AutoLockRenew is used and it fails to renew the session lock.
    :vartype auto_renew_error: ~azure.servicebus.AutoLockRenewTimeout or ~azure.servicebus.AutoLockRenewFailed

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START get_session_sync]
            :end-before: [END get_session_sync]
            :language: python
            :dedent: 4
            :caption: Get session from a receiver
    """

    def get_state(self):
        # type: () -> str
        """Get the session state.

        Returns None if no state has been set.

        :rtype: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START get_session_state_sync]
                :end-before: [END get_session_state_sync]
                :language: python
                :dedent: 4
                :caption: Get the session state
        """
        self._check_live()
        response = self._receiver._mgmt_request_response_with_retry(  # pylint: disable=protected-access
            REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION,
            {MGMT_REQUEST_SESSION_ID: self._id},
            mgmt_handlers.default
        )
        session_state = response.get(MGMT_RESPONSE_SESSION_STATE)
        if isinstance(session_state, six.binary_type):
            session_state = session_state.decode(self._encoding)
        return session_state

    def set_state(self, state):
        # type: (Union[str, bytes, bytearray]) -> None
        """Set the session state.

        :param state: The state value.
        :type state: Union[str, bytes, bytearray]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START set_session_state_sync]
                :end-before: [END set_session_state_sync]
                :language: python
                :dedent: 4
                :caption: Set the session state
        """
        self._check_live()
        state = state.encode(self._encoding) if isinstance(state, six.text_type) else state
        return self._receiver._mgmt_request_response_with_retry(  # pylint: disable=protected-access
            REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
            {MGMT_REQUEST_SESSION_ID: self._id, MGMT_REQUEST_SESSION_STATE: bytearray(state)},
            mgmt_handlers.default
        )

    def renew_lock(self):
        # type: () -> datetime.datetime
        """Renew the session lock.

        This operation must be performed periodically in order to retain a lock on the
        session to continue message processing.

        Once the lock is lost the connection will be closed; an expired lock cannot be renewed.

        This operation can also be performed as a threaded background task by registering the session
        with an `azure.servicebus.AutoLockRenew` instance.

        :returns: The utc datetime the lock is set to expire at.
        :rtype: datetime.datetime

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START session_renew_lock_sync]
                :end-before: [END session_renew_lock_sync]
                :language: python
                :dedent: 4
                :caption: Renew the session lock before it expires
        """
        self._check_live()
        expiry = self._receiver._mgmt_request_response_with_retry(  # pylint: disable=protected-access
            REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
            {MGMT_REQUEST_SESSION_ID: self._id},
            mgmt_handlers.default
        )
        expiry_timestamp = expiry[MGMT_RESPONSE_RECEIVER_EXPIRATION]/1000.0
        self._locked_until_utc = utc_from_timestamp(expiry_timestamp) # type: datetime.datetime

        return self._locked_until_utc
