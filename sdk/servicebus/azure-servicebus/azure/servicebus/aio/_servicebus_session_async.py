# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import datetime
from typing import Union
import six

from .._servicebus_session import BaseSession
from .._common.constants import (
    REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION,
    REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
    REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
    MGMT_RESPONSE_SESSION_STATE,
    MGMT_RESPONSE_RECEIVER_EXPIRATION,
    MGMT_REQUEST_SESSION_ID,
    MGMT_REQUEST_SESSION_STATE
)
from .._common import mgmt_handlers
from .._common.utils import utc_from_timestamp

_LOGGER = logging.getLogger(__name__)


class ServiceBusSession(BaseSession):
    """
    The ServiceBusSession is used for manage session states and lock renewal.

    **Please use the instance variable `session` on the ServiceBusReceiver to get the corresponding ServiceBusSession
    object linked with the receiver instead of instantiating a ServiceBusSession object directly.**

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
            :start-after: [START get_session_async]
            :end-before: [END get_session_async]
            :language: python
            :dedent: 4
            :caption: Get session from a receiver
    """

    async def get_state(self):
        # type: () -> str
        """Get the session state.

        Returns None if no state has been set.

        :rtype: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
                :start-after: [START get_session_state_async]
                :end-before: [END get_session_state_async]
                :language: python
                :dedent: 4
                :caption: Get the session state
        """
        self._check_live()
        response = await self._receiver._mgmt_request_response_with_retry(  # pylint: disable=protected-access
            REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION,
            {MGMT_REQUEST_SESSION_ID: self._id},
            mgmt_handlers.default
        )
        session_state = response.get(MGMT_RESPONSE_SESSION_STATE)
        if isinstance(session_state, six.binary_type):
            session_state = session_state.decode('UTF-8')
        return session_state

    async def set_state(self, state):
        # type: (Union[str, bytes, bytearray]) -> None
        """Set the session state.

        :param state: The state value.
        :type state: Union[str, bytes, bytearray]
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
                :start-after: [START set_session_state_async]
                :end-before: [END set_session_state_async]
                :language: python
                :dedent: 4
                :caption: Set the session state
        """
        self._check_live()
        state = state.encode(self._encoding) if isinstance(state, six.text_type) else state
        return await self._receiver._mgmt_request_response_with_retry(  # pylint: disable=protected-access
            REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
            {MGMT_REQUEST_SESSION_ID: self._id, MGMT_REQUEST_SESSION_STATE: bytearray(state)},
            mgmt_handlers.default
        )

    async def renew_lock(self):
        # type: () -> datetime.datetime
        """Renew the session lock.

        This operation must be performed periodically in order to retain a lock on the
        session to continue message processing.

        Once the lock is lost the connection will be closed; an expired lock cannot be renewed.

        This operation can also be performed as a threaded background task by registering the session
        with an `azure.servicebus.aio.AutoLockRenew` instance.

        :returns: The utc datetime the lock is set to expire at.
        :rtype: datetime

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
                :start-after: [START session_renew_lock_async]
                :end-before: [END session_renew_lock_async]
                :language: python
                :dedent: 4
                :caption: Renew the session lock before it expires
        """
        self._check_live()
        expiry = await self._receiver._mgmt_request_response_with_retry(  # pylint: disable=protected-access
            REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
            {MGMT_REQUEST_SESSION_ID: self._id},
            mgmt_handlers.default
        )
        expiry_timestamp = expiry[MGMT_RESPONSE_RECEIVER_EXPIRATION]/1000.0
        self._locked_until_utc = utc_from_timestamp(expiry_timestamp) # type: datetime.datetime

        return self._locked_until_utc
