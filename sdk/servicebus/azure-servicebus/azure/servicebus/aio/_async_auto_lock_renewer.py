# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
import logging
import datetime
import functools
from typing import Optional, Iterable, Any

from ._servicebus_session_async import ServiceBusSession
from .._common.utils import renewable_start_time, utc_now
from ._async_utils import get_running_loop
from ..exceptions import AutoLockRenewTimeout, AutoLockRenewFailed, ServiceBusError

_log = logging.getLogger(__name__)


class AutoLockRenew:
    """Auto lock renew.

    An asynchronous AutoLockRenew handler for renewing the lock
    tokens of messages and/or sessions in the background.

    :param loop: An async event loop.
    :type loop: ~asyncio.BaseEventLoop

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

    def __init__(self, loop: Optional[asyncio.BaseEventLoop] = None) -> None:
        self._shutdown = asyncio.Event()
        self._futures = []
        self._loop = loop or get_running_loop()
        self.sleep_time = 1
        self.renew_period = 10

    async def __aenter__(self) -> "AutoLockRenew":
        if self._shutdown.is_set():
            raise ServiceBusError("The AutoLockRenew has already been shutdown. Please create a new instance for"
                                  " auto lock renewing.")
        return self

    async def __aexit__(self, *args: Iterable[Any]) -> None:
        await self.close()

    def _renewable(self, renewable: "Union[ReceivedMessage, ServiceBusSession]") -> bool:
        if self._shutdown.is_set():
            return False
        if hasattr(renewable, '_settled') and renewable._settled:
            return False
        if renewable._lock_expired:
            return False
        if not renewable._receiver._running:
            return False
        return True

    async def _auto_lock_renew(self,
                               renewable: "Union[ReceivedMessage, ServiceBusSession]",
                               starttime: datetime.datetime,
                               timeout: int,
                               on_lock_renew_failure: "Optional[Callable[[Union[ServiceBusSession, ReceivedMessage], Optional[Exception]], Awaitable[None]]]"=None) -> None:
        _log.debug("Running async lock auto-renew for %r seconds", timeout)
        error = None
        clean_shutdown = False # Only trigger the on_lock_renew_failure if halting was not expected (shutdown, etc)
        try:
            while self._renewable(renewable):
                if (utc_now() - starttime) >= datetime.timedelta(seconds=timeout):
                    _log.debug("Reached auto lock renew timeout - letting lock expire.")
                    raise AutoLockRenewTimeout("Auto-renew period ({} seconds) elapsed.".format(timeout))
                if (renewable.locked_until_utc - utc_now()) <= datetime.timedelta(seconds=self.renew_period):
                    _log.debug("%r seconds or less until lock expires - auto renewing.", self.renew_period)
                    await renewable.renew_lock()
                await asyncio.sleep(self.sleep_time)
            clean_shutdown = not renewable._lock_expired
        except AutoLockRenewTimeout as e:
            renewable.auto_renew_error = e
            clean_shutdown = not renewable._lock_expired
        except Exception as e:  # pylint: disable=broad-except
            _log.debug("Failed to auto-renew lock: %r. Closing thread.", e)
            error = AutoLockRenewFailed(
                "Failed to auto-renew lock",
                inner_exception=e)
            renewable.auto_renew_error = error
        finally:
            if on_lock_renew_failure and not clean_shutdown:
                await on_lock_renew_failure(renewable, error)

    def register(self,
                 renewable: "Union[ReceivedMessage, ServiceBusSession]",
                 timeout: float = 300,
                 on_lock_renew_failure: "Optional[Callable[[Union[ServiceBusSession, ReceivedMessage]], Awaitable[None]]]" = None) -> None:
        """Register a renewable entity for automatic lock renewal.

        :param renewable: A locked entity that needs to be renewed.
        :type renewable: Union[~azure.servicebus.aio.ReceivedMessage,~azure.servicebus.aio.ServiceBusSession]
        :param float timeout: A time in seconds that the lock should be maintained for.
         Default value is 300 (5 minutes).
        :param Optional[Callable[[Union[~azure.servicebus.aio.ServiceBusSession, ReceivedMessage]], Awaitable[None]]] on_lock_renew_failure: 
         A callback may be specified to be called when the lock is lost on the renewable that is being registered.
         Default value is None (no callback).
        """
        if self._shutdown.is_set():
            raise ServiceBusError("The AutoLockRenew has already been shutdown. Please create a new instance for"
                                  " auto lock renewing.")
        starttime = renewable_start_time(renewable)
        renew_future = asyncio.ensure_future(self._auto_lock_renew(renewable, starttime, timeout, on_lock_renew_failure), loop=self._loop)
        self._futures.append(renew_future)

    async def close(self) -> None:
        """Cease autorenewal by cancelling any remaining open lock renewal futures."""
        self._shutdown.set()
        await asyncio.wait(self._futures)
