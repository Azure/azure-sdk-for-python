# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
import logging
import datetime
from typing import Optional, Iterable, Any, Union, Callable, Awaitable, List

from .._common.message import ServiceBusReceivedMessage
from ._servicebus_session_async import ServiceBusSession
from ._servicebus_receiver_async import ServiceBusReceiver
from .._common.utils import (
    get_renewable_start_time,
    utc_now,
    get_renewable_lock_duration,
)
from .._common.auto_lock_renewer import SHORT_RENEW_OFFSET, SHORT_RENEW_SCALING_FACTOR
from ._async_utils import get_dict_with_loop_if_needed
from ..exceptions import AutoLockRenewTimeout, AutoLockRenewFailed, ServiceBusError

Renewable = Union[ServiceBusSession, ServiceBusReceivedMessage]
AsyncLockRenewFailureCallback = Callable[
    [Renewable, Optional[Exception]], Awaitable[None]
]

_log = logging.getLogger(__name__)


class AutoLockRenewer:
    """Auto lock renew.

    An asynchronous AutoLockRenewer handler for renewing the lock
    tokens of messages and/or sessions in the background.

    :param max_lock_renewal_duration: A time in seconds that locks registered to this renewer
      should be maintained for. Default value is 300 (5 minutes).
    :type max_lock_renewal_duration: float
    :param on_lock_renew_failure: A callback may be specified to be called when the lock is lost on the renewable
     that is being registered. Default value is None (no callback).
    :type on_lock_renew_failure: Optional[LockRenewFailureCallback]

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
            :start-after: [START auto_lock_renew_message_async]
            :end-before: [END auto_lock_renew_message_async]
            :language: python
            :dedent: 4
            :caption: Automatically renew a message lock

        .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
            :start-after: [START auto_lock_renew_session_async]
            :end-before: [END auto_lock_renew_session_async]
            :language: python
            :dedent: 4
            :caption: Automatically renew a session lock

    """

    def __init__(
        self,
        max_lock_renewal_duration: float = 300,
        on_lock_renew_failure: Optional[AsyncLockRenewFailureCallback] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._internal_kwargs = get_dict_with_loop_if_needed(loop)
        self._shutdown = asyncio.Event()
        self._futures = []  # type: List[asyncio.Future]
        self._sleep_time = 1
        self._renew_period = 10
        self._on_lock_renew_failure = on_lock_renew_failure
        self._max_lock_renewal_duration = max_lock_renewal_duration

    async def __aenter__(self) -> "AutoLockRenewer":
        if self._shutdown.is_set():
            raise ServiceBusError(
                "The AutoLockRenewer has already been shutdown. Please create a new instance for"
                " auto lock renewing."
            )
        return self

    async def __aexit__(self, *args: Iterable[Any]) -> None:
        await self.close()

    def _renewable(
        self, renewable: Union[ServiceBusReceivedMessage, ServiceBusSession]
    ) -> bool:
        # pylint: disable=protected-access
        if self._shutdown.is_set():
            return False
        if hasattr(renewable, "_settled") and renewable._settled:  # type: ignore
            return False
        if renewable._lock_expired:
            return False
        try:
            if not renewable._receiver._running:  # type: ignore
                return False
        except AttributeError:  # If for whatever reason the renewable isn't hooked up to a receiver
            raise ServiceBusError(
                "Cannot renew an entity without an associated receiver.  "
                "ServiceBusReceivedMessage and active ServiceBusReceiver.Session objects are expected."
            )
        return True

    async def _auto_lock_renew(
        self,
        receiver: ServiceBusReceiver,
        renewable: Renewable,
        starttime: datetime.datetime,
        max_lock_renewal_duration: float,
        on_lock_renew_failure: Optional[AsyncLockRenewFailureCallback] = None,
        renew_period_override: float = None,
    ) -> None:
        # pylint: disable=protected-access
        _log.debug(
            "Running async lock auto-renew for %r seconds", max_lock_renewal_duration
        )
        error = None  # type: Optional[Exception]
        clean_shutdown = False  # Only trigger the on_lock_renew_failure if halting was not expected (shutdown, etc)
        renew_period = renew_period_override or self._renew_period
        try:
            while self._renewable(renewable):
                if (utc_now() - starttime) >= datetime.timedelta(
                    seconds=max_lock_renewal_duration
                ):
                    _log.debug(
                        "Reached max auto lock renew duration - letting lock expire."
                    )
                    raise AutoLockRenewTimeout(
                        "Auto-renew period ({} seconds) elapsed.".format(
                            max_lock_renewal_duration
                        )
                    )
                if (renewable.locked_until_utc - utc_now()) <= datetime.timedelta(
                    seconds=renew_period
                ):
                    _log.debug(
                        "%r seconds or less until lock expires - auto renewing.",
                        renew_period,
                    )
                    try:
                        # Renewable is a session
                        await renewable.renew_lock()  # type: ignore
                    except AttributeError:
                        # Renewable is a message
                        await receiver.renew_message_lock(renewable)  # type: ignore
                await asyncio.sleep(self._sleep_time)
            clean_shutdown = not renewable._lock_expired
        except AutoLockRenewTimeout as e:
            error = e
            renewable.auto_renew_error = e
            clean_shutdown = not renewable._lock_expired
        except Exception as e:  # pylint: disable=broad-except
            _log.debug("Failed to auto-renew lock: %r. Closing thread.", e)
            error = AutoLockRenewFailed("Failed to auto-renew lock", error=e)
            renewable.auto_renew_error = error
        finally:
            if on_lock_renew_failure and not clean_shutdown:
                await on_lock_renew_failure(renewable, error)

    def register(
        self,
        receiver: ServiceBusReceiver,
        renewable: Union[ServiceBusReceivedMessage, ServiceBusSession],
        max_lock_renewal_duration: Optional[float] = None,
        on_lock_renew_failure: Optional[AsyncLockRenewFailureCallback] = None,
    ) -> None:
        """Register a renewable entity for automatic lock renewal.

        :param receiver: The ServiceBusReceiver instance that is associated with the message or the session to
         be auto-lock-renewed.
        :type receiver: ~azure.servicebus.aio.ServiceBusReceiver
        :param renewable: A locked entity that needs to be renewed.
        :type renewable: Union[~azure.servicebus.aio.ServiceBusReceivedMessage,~azure.servicebus.aio.ServiceBusSession]
        :param max_lock_renewal_duration: A time in seconds that the lock should be maintained for.
         Default value is None. If specified, this value will override the default value specified at the constructor.
        :type max_lock_renewal_duration: Optional[float]
        :param Optional[AsyncLockRenewFailureCallback] on_lock_renew_failure:
         An async callback may be specified to be called when the lock is lost on the renewable being registered.
         Default value is None (no callback).
         :rtype: None
        """
        if not isinstance(renewable, (ServiceBusReceivedMessage, ServiceBusSession)):
            raise TypeError(
                "AutoLockRenewer only supports registration of types "
                "azure.servicebus.ServiceBusReceivedMessage (via a receiver's receive methods) and "
                "azure.servicebus.aio.ServiceBusSession "
                "(via a session receiver's property receiver.session)."
            )
        if self._shutdown.is_set():
            raise ServiceBusError(
                "The AutoLockRenewer has already been shutdown. Please create a new instance for"
                " auto lock renewing."
            )
        if renewable.locked_until_utc is None:
            raise ValueError(
                "Only azure.servicebus.ServiceBusReceivedMessage objects in PEEK_LOCK receive mode may"
                "be lock-renewed.  (E.g. only messages received via receive() or the receiver iterator,"
                "not using RECEIVE_AND_DELETE receive mode, and not returned from Peek)"
            )

        starttime = get_renewable_start_time(renewable)

        # This is a heuristic to compensate if it appears the user has a lock duration less than our base renew period
        time_until_expiry = get_renewable_lock_duration(renewable)
        renew_period_override = None
        # Default is 10 seconds, but let's leave ourselves a small margin of error because clock skew is a real problem
        if time_until_expiry <= datetime.timedelta(
            seconds=self._renew_period + SHORT_RENEW_OFFSET
        ):
            renew_period_override = (
                time_until_expiry.seconds * SHORT_RENEW_SCALING_FACTOR
            )

        renew_future = asyncio.ensure_future(
            self._auto_lock_renew(
                receiver,
                renewable,
                starttime,
                max_lock_renewal_duration or self._max_lock_renewal_duration,
                on_lock_renew_failure or self._on_lock_renew_failure,
                renew_period_override,
            ),
            **self._internal_kwargs
        )
        self._futures.append(renew_future)

    async def close(self) -> None:
        """Cease autorenewal by cancelling any remaining open lock renewal futures."""
        self._shutdown.set()
        if self._futures:
            await asyncio.wait(self._futures)
