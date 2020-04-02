# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
import logging
import datetime
import functools

from uamqp import authentication

from .._common.utils import renewable_start_time, get_running_loop, utc_now
from ..exceptions import AutoLockRenewTimeout, AutoLockRenewFailed
from .._common.constants import (
    JWT_TOKEN_SCOPE,
    TOKEN_TYPE_JWT,
    TOKEN_TYPE_SASTOKEN
)


_log = logging.getLogger(__name__)


async def create_authentication(client):
    # pylint: disable=protected-access
    try:
        # ignore mypy's warning because token_type is Optional
        token_type = client._credential.token_type  # type: ignore
    except AttributeError:
        token_type = TOKEN_TYPE_JWT
    if token_type == TOKEN_TYPE_SASTOKEN:
        auth = authentication.JWTTokenAsync(
            client._auth_uri,
            client._auth_uri,
            functools.partial(client._credential.get_token, client._auth_uri),
            token_type=token_type,
            timeout=client._config.auth_timeout,
            http_proxy=client._config.http_proxy,
            transport_type=client._config.transport_type,
        )
        await auth.update_token()
        return auth
    return authentication.JWTTokenAsync(
        client._auth_uri,
        client._auth_uri,
        functools.partial(client._credential.get_token, JWT_TOKEN_SCOPE),
        token_type=token_type,
        timeout=client._config.auth_timeout,
        http_proxy=client._config.http_proxy,
        transport_type=client._config.transport_type,
    )


class AutoLockRenew:
    """Auto lock renew.

    An asynchronous AutoLockRenew handler for renewing the lock
    tokens of messages and/or sessions in the background.

    :param loop: An async event loop.
    :type loop: ~asyncio.EventLoop

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

    def __init__(self, loop=None):
        self._shutdown = asyncio.Event()
        self._futures = []
        self.loop = loop or get_running_loop()
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
        _log.debug("Running async lock auto-renew for %r seconds", timeout)
        try:
            while self._renewable(renewable):
                if (utc_now() - starttime) >= datetime.timedelta(seconds=timeout):
                    _log.debug("Reached auto lock renew timeout - letting lock expire.")
                    raise AutoLockRenewTimeout("Auto-renew period ({} seconds) elapsed.".format(timeout))
                if (renewable.locked_until_utc - utc_now()) <= datetime.timedelta(seconds=self.renew_period):
                    _log.debug("%r seconds or less until lock expires - auto renewing.", self.renew_period)
                    await renewable.renew_lock()
                await asyncio.sleep(self.sleep_time)
        except AutoLockRenewTimeout as e:
            renewable.auto_renew_error = e
        except Exception as e:  # pylint: disable=broad-except
            _log.debug("Failed to auto-renew lock: %r. Closing thread.", e)
            error = AutoLockRenewFailed(
                "Failed to auto-renew lock",
                inner_exception=e)
            renewable.auto_renew_error = error

    def register(self, renewable, timeout=300):
        """Register a renewable entity for automatic lock renewal.

        :param renewable: A locked entity that needs to be renewed.
        :type renewable: ~azure.servicebus.aio.ReceivedMessage or
         ~azure.servicebus.aio.Session
        :param float timeout: A time in seconds that the lock should be maintained for.
         Default value is 300 (5 minutes).
        """
        starttime = renewable_start_time(renewable)
        renew_future = asyncio.ensure_future(self._auto_lock_renew(renewable, starttime, timeout), loop=self.loop)
        self._futures.append(renew_future)

    async def shutdown(self):
        """Cancel remaining open lock renewal futures."""
        self._shutdown.set()
        await asyncio.wait(self._futures)
