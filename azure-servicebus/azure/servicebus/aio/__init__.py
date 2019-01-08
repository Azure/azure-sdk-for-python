#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
import datetime
import logging

from azure.servicebus.common.errors import (
    ServiceBusError,
    ServiceBusResourceNotFound,
    ServiceBusConnectionError,
    ServiceBusAuthorizationError,
    InvalidHandlerState,
    NoActiveSession,
    MessageAlreadySettled,
    MessageSettleFailed,
    MessageSendFailed,
    MessageLockExpired,
    SessionLockExpired,
    AutoLockRenewFailed,
    AutoLockRenewTimeout)
from azure.servicebus.common.constants import ReceiveSettleMode, NEXT_AVAILABLE
from azure.servicebus.common.message import BatchMessage, PeekMessage
from azure.servicebus.common.utils import renewable_start_time
from .async_message import Message, DeferredMessage
from .async_send_handler import Sender, SessionSender
from .async_receive_handler import Receiver, SessionReceiver
from .async_client import ServiceBusClient, QueueClient, TopicClient, SubscriptionClient


log = logging.getLogger(__name__)


class AutoLockRenew:

    def __init__(self, loop):
        self._shutdown = asyncio.Event()
        self._futures = []
        self.loop = loop
        self.sleep_time = 1
        self.renew_period = 10

    def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.shutdown()

    def _renewable(self, renewable):
        if self._shutdown.is_set():
            return False
        if hasattr(renewable, 'settled') and renewable.settled:
            return False
        if renewable.expired:
            return False
        return True

    async def _auto_lock_renew(self, renewable, starttime, timeout):
        log.debug("Running async lock auto-renew for %r seconds", timeout)
        try:
            while self._renewable(renewable):
                if (datetime.datetime.now() - starttime) >= datetime.timedelta(seconds=timeout):
                    log.debug("Reached auto lock renew timeout - letting lock expire.")
                    raise AutoLockRenewTimeout("Auto-renew period ({} seconds) elapsed.".format(timeout))
                if (renewable.locked_until - datetime.datetime.now()) <= datetime.timedelta(seconds=self.renew_period):
                    log.debug("%r seconds or less until lock expires - auto renewing.", self.renew_period)
                    await renewable.renew_lock()
                await asyncio.sleep(self.sleep_time)
        except AutoLockRenewTimeout as e:
            renewable.auto_renew_error = e
        except Exception as e:  # pylint: disable=broad-except
            log.debug("Failed to auto-renew lock: %r. Closing thread.", e)
            error = AutoLockRenewFailed(
                "Failed to auto-renew lock",
                inner_exception=e)
            renewable.auto_renew_error = error

    def register(self, renewable, timeout=300):
        starttime = renewable_start_time(renewable)
        renew_future = asyncio.ensure_future(self._auto_lock_renew(renewable, starttime, timeout), loop=self.loop)
        self._futures.append(renew_future)

    async def shutdown(self, wait=True):
        self._shutdown.set()
        if wait:
            await asyncio.wait(self._futures)
