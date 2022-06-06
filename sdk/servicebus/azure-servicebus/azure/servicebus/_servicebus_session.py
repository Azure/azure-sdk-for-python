# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import datetime
import warnings
from typing import TYPE_CHECKING, Any, Union, Optional
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
from ._common import mgmt_handlers

if TYPE_CHECKING:
    from ._servicebus_receiver import ServiceBusReceiver
    from .aio._servicebus_receiver_async import (
        ServiceBusReceiver as ServiceBusReceiverAsync,
    )

_LOGGER = logging.getLogger(__name__)


class BaseSession(object):
    def __init__(self, session_id, receiver):
        # type: (str, Union[ServiceBusReceiver, ServiceBusReceiverAsync]) -> None
        self._session_id = session_id
        self._receiver = receiver
        self._encoding = "UTF-8"
        self._session_start = None
        self._locked_until_utc = None  # type: Optional[datetime.datetime]
        self._lock_lost = False
        self.auto_renew_error = None

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
        return self._session_id

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

    **Please use the property `session` on the ServiceBusReceiver to get the corresponding ServiceBusSession
    object linked with the receiver instead of instantiating a ServiceBusSession object directly.**

    :ivar auto_renew_error: Error when AutoLockRenewer is used and it fails to renew the session lock.
    :vartype auto_renew_error: ~azure.servicebus.AutoLockRenewTimeout or ~azure.servicebus.AutoLockRenewFailed

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START get_session_sync]
            :end-before: [END get_session_sync]
            :language: python
            :dedent: 4
            :caption: Get session from a receiver
    """

    def get_state(self, *, timeout: Optional[float] = None, **kwargs: Any) -> bytes:
        # pylint: disable=protected-access
        """Get the session state.

        Returns None if no state has been set.

        :keyword float timeout: The total operation timeout in seconds including all the retries. The value must be
         greater than 0 if specified. The default value is None, meaning no timeout.
        :rtype: bytes

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START get_session_state_sync]
                :end-before: [END get_session_state_sync]
                :language: python
                :dedent: 4
                :caption: Get the session state
        """
        if kwargs:
            warnings.warn(f"Unsupported keyword args: {kwargs}")
        self._receiver._check_live()  # pylint: disable=protected-access
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")
        response = self._receiver._mgmt_request_response_with_retry(
            REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION,
            {MGMT_REQUEST_SESSION_ID: self._session_id},
            mgmt_handlers.default,
            timeout=timeout,
        )
        session_state = response.get(MGMT_RESPONSE_SESSION_STATE)  # type: ignore
        return session_state

    def set_state(
        self,
        state: Union[str, bytes, bytearray],
        *,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        # pylint: disable=protected-access
        """Set the session state.

        :param state: The state value.
        :type state: Union[str, bytes, bytearray]
        :keyword float timeout: The total operation timeout in seconds including all the retries. The value must be
         greater than 0 if specified. The default value is None, meaning no timeout.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START set_session_state_sync]
                :end-before: [END set_session_state_sync]
                :language: python
                :dedent: 4
                :caption: Set the session state
        """
        if kwargs:
            warnings.warn(f"Unsupported keyword args: {kwargs}")
        self._receiver._check_live()  # pylint: disable=protected-access
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")
        state = (
            state.encode(self._encoding) if isinstance(state, six.text_type) else state
        )
        return self._receiver._mgmt_request_response_with_retry(  # type: ignore
            REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
            {
                MGMT_REQUEST_SESSION_ID: self._session_id,
                MGMT_REQUEST_SESSION_STATE: bytearray(state),
            },
            mgmt_handlers.default,
            timeout=timeout,
        )

    def renew_lock(
        self, *, timeout: Optional[float] = None, **kwargs: Any
    ) -> datetime.datetime:
        # pylint: disable=protected-access
        """Renew the session lock.

        This operation must be performed periodically in order to retain a lock on the
        session to continue message processing.

        Once the lock is lost the connection will be closed; an expired lock cannot be renewed.

        This operation can also be performed as a threaded background task by registering the session
        with an `azure.servicebus.AutoLockRenewer` instance.

        :keyword float timeout: The total operation timeout in seconds including all the retries. The value must be
         greater than 0 if specified. The default value is None, meaning no timeout.
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
        if kwargs:
            warnings.warn(f"Unsupported keyword args: {kwargs}")
        self._receiver._check_live()  # pylint: disable=protected-access
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")
        expiry = self._receiver._mgmt_request_response_with_retry(
            REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
            {MGMT_REQUEST_SESSION_ID: self._session_id},
            mgmt_handlers.session_lock_renew_op,
            timeout=timeout,
        )
        expiry_timestamp = expiry[MGMT_RESPONSE_RECEIVER_EXPIRATION] / 1000.0  # type: ignore
        self._locked_until_utc = utc_from_timestamp(
            expiry_timestamp
        )  # type: datetime.datetime

        return self._locked_until_utc
