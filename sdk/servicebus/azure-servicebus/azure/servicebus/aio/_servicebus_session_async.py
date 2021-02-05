# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import datetime
from typing import Union, Any
import six

from .._servicebus_session import BaseSession
from .._common.constants import (
    REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION,
    REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
    REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
    MGMT_RESPONSE_SESSION_STATE,
    MGMT_RESPONSE_RECEIVER_EXPIRATION,
    MGMT_REQUEST_SESSION_ID,
    MGMT_REQUEST_SESSION_STATE,
)
from .._common import mgmt_handlers
from .._common.utils import utc_from_timestamp

_LOGGER = logging.getLogger(__name__)


class ServiceBusSession(BaseSession):
    """
    The ServiceBusSession is used for manage session states and lock renewal.

    **Please use the property `session` on the ServiceBusReceiver to get the corresponding ServiceBusSession
    object linked with the receiver instead of instantiating a ServiceBusSession object directly.**

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
            :start-after: [START get_session_async]
            :end-before: [END get_session_async]
            :language: python
            :dedent: 4
            :caption: Get session from a receiver
    """

    async def get_state(self, **kwargs: Any) -> bytes:
        """Get the session state.

        Returns None if no state has been set.

        :keyword Optional[float] timeout: The total operation timeout in seconds including all the retries.
         The value must be greater than 0 if specified. The default value is None, meaning no timeout.
        :rtype: str

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
                :start-after: [START get_session_state_async]
                :end-before: [END get_session_state_async]
                :language: python
                :dedent: 4
                :caption: Get the session state
        """
        self._receiver._check_live()  # pylint: disable=protected-access
        timeout = kwargs.pop("timeout", None)
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")
        response = await self._receiver._mgmt_request_response_with_retry(  # pylint: disable=protected-access
            REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION,
            {MGMT_REQUEST_SESSION_ID: self._session_id},
            mgmt_handlers.default,
            timeout=timeout,
        )
        session_state = response.get(MGMT_RESPONSE_SESSION_STATE)
        return session_state

    async def set_state(
        self, state: Union[str, bytes, bytearray], **kwargs: Any
    ) -> None:
        """Set the session state.

        :param state: The state value.
        :type state: Union[str, bytes, bytearray]
        :keyword Optional[float] timeout: The total operation timeout in seconds including all the retries.
         The value must be greater than 0 if specified. The default value is None, meaning no timeout.
        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
                :start-after: [START set_session_state_async]
                :end-before: [END set_session_state_async]
                :language: python
                :dedent: 4
                :caption: Set the session state
        """
        self._receiver._check_live()  # pylint: disable=protected-access
        timeout = kwargs.pop("timeout", None)
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")
        state = (
            state.encode(self._encoding) if isinstance(state, six.text_type) else state
        )
        return await self._receiver._mgmt_request_response_with_retry(  # pylint: disable=protected-access
            REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
            {
                MGMT_REQUEST_SESSION_ID: self._session_id,
                MGMT_REQUEST_SESSION_STATE: bytearray(state),
            },
            mgmt_handlers.default,
            timeout=timeout,
        )

    async def renew_lock(self, **kwargs: Any) -> datetime.datetime:
        """Renew the session lock.

        This operation must be performed periodically in order to retain a lock on the
        session to continue message processing.

        Once the lock is lost the connection will be closed; an expired lock cannot be renewed.

        This operation can also be performed as a threaded background task by registering the session
        with an `azure.servicebus.aio.AutoLockRenewer` instance.

        :keyword Optional[float] timeout: The total operation timeout in seconds including all the retries.
         The value must be greater than 0 if specified. The default value is None, meaning no timeout.
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
        self._receiver._check_live()  # pylint: disable=protected-access
        timeout = kwargs.pop("timeout", None)
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")
        expiry = await self._receiver._mgmt_request_response_with_retry(  # pylint: disable=protected-access
            REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
            {MGMT_REQUEST_SESSION_ID: self._session_id},
            mgmt_handlers.session_lock_renew_op,
            timeout=timeout,
        )
        expiry_timestamp = expiry[MGMT_RESPONSE_RECEIVER_EXPIRATION] / 1000.0
        self._locked_until_utc = utc_from_timestamp(
            expiry_timestamp
        )  # type: datetime.datetime

        return self._locked_until_utc
