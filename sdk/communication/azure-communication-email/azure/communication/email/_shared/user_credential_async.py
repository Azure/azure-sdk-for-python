# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from asyncio import Condition, Lock, Event
from datetime import timedelta
from typing import Any
import sys

from .utils import get_current_utc_as_int
from .utils import create_access_token
from .utils_async import AsyncTimer


class CommunicationTokenCredential(object):
    """Credential type used for authenticating to an Azure Communication service.
    :param str token: The token used to authenticate to an Azure Communication service.
    :keyword token_refresher: The async token refresher to provide capacity to fetch a fresh token.
     The returned token must be valid (expiration date must be in the future).
    :paramtype token_refresher: Callable[[], Awaitable[AccessToken]]
    :keyword bool proactive_refresh: Whether to refresh the token proactively or not.
     If the proactive refreshing is enabled ('proactive_refresh' is true), the credential will use
     a background thread to attempt to refresh the token within 10 minutes before the cached token expires,
     the proactive refresh will request a new token by calling the 'token_refresher' callback.
     When 'proactive_refresh is enabled', the Credential object must be either run within a context manager
     or the 'close' method must be called once the object usage has been finished.
    :raises: TypeError if paramater 'token' is not a string
    :raises: ValueError if the 'proactive_refresh' is enabled without providing the 'token_refresher' function.
    """

    _ON_DEMAND_REFRESHING_INTERVAL_MINUTES = 2
    _DEFAULT_AUTOREFRESH_INTERVAL_MINUTES = 10

    def __init__(self, token: str, **kwargs: Any):
        if not isinstance(token, str):
            raise TypeError("Token must be a string.")
        self._token = create_access_token(token)
        self._token_refresher = kwargs.pop("token_refresher", None)
        self._proactive_refresh = kwargs.pop("proactive_refresh", False)
        if self._proactive_refresh and self._token_refresher is None:
            raise ValueError(
                "When 'proactive_refresh' is True, 'token_refresher' must not be None."
            )
        self._timer = None
        self._async_mutex = Lock()
        if sys.version_info[:3] == (3, 10, 0):
            # Workaround for Python 3.10 bug(https://bugs.python.org/issue45416):
            getattr(self._async_mutex, "_get_loop", lambda: None)()
        self._lock = Condition(self._async_mutex)
        self._some_thread_refreshing = False
        self._is_closed = Event()

    async def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        # type (*str, **Any) -> AccessToken
        """The value of the configured token.
        :param any scopes: Scopes to be added to the token.
        :return: AccessToken
        :rtype: ~azure.core.credentials.AccessToken
        """
        if self._proactive_refresh and self._is_closed.is_set():
            raise RuntimeError(
                "An instance of CommunicationTokenCredential cannot be reused once it has been closed."
            )

        if not self._token_refresher or not self._is_token_expiring_soon(self._token):
            return self._token
        await self._update_token_and_reschedule()
        return self._token

    async def _update_token_and_reschedule(self):
        should_this_thread_refresh = False
        async with self._lock:
            while self._is_token_expiring_soon(self._token):
                if self._some_thread_refreshing:
                    if self._is_token_valid(self._token):
                        return self._token
                    await self._wait_till_lock_owner_finishes_refreshing()
                else:
                    should_this_thread_refresh = True
                    self._some_thread_refreshing = True
                    break

        if should_this_thread_refresh:
            try:
                new_token = await self._token_refresher()
                if not self._is_token_valid(new_token):
                    raise ValueError(
                        "The token returned from the token_refresher is expired."
                    )
                async with self._lock:
                    self._token = new_token
                    self._some_thread_refreshing = False
                    self._lock.notify_all()
            except:
                async with self._lock:
                    self._some_thread_refreshing = False
                    self._lock.notify_all()
                raise
        if self._proactive_refresh:
            self._schedule_refresh()
        return self._token

    def _schedule_refresh(self):
        if self._is_closed.is_set():
            return
        if self._timer is not None:
            self._timer.cancel()

        token_ttl = self._token.expires_on - get_current_utc_as_int()

        if self._is_token_expiring_soon(self._token):
            # Schedule the next refresh for when it reaches a certain percentage of the remaining lifetime.
            timespan = token_ttl // 2
        else:
            # Schedule the next refresh for when it gets in to the soon-to-expire window.
            timespan = (
                token_ttl
                - timedelta(
                    minutes=self._DEFAULT_AUTOREFRESH_INTERVAL_MINUTES
                ).total_seconds()
            )

        self._timer = AsyncTimer(timespan, self._update_token_and_reschedule)
        self._timer.start()

    async def _wait_till_lock_owner_finishes_refreshing(self):
        self._lock.release()
        await self._lock.acquire()

    def _is_token_expiring_soon(self, token):
        if self._proactive_refresh:
            interval = timedelta(minutes=self._DEFAULT_AUTOREFRESH_INTERVAL_MINUTES)
        else:
            interval = timedelta(minutes=self._ON_DEMAND_REFRESHING_INTERVAL_MINUTES)
        return (token.expires_on - get_current_utc_as_int()) < interval.total_seconds()

    @classmethod
    def _is_token_valid(cls, token):
        return get_current_utc_as_int() < token.expires_on

    async def __aenter__(self):
        if self._proactive_refresh:
            if self._is_closed.is_set():
                raise RuntimeError(
                    "An instance of CommunicationTokenCredential cannot be reused once it has been closed."
                )
            self._schedule_refresh()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
        self._timer = None
        self._is_closed.set()
