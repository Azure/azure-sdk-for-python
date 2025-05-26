# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=C4763
from asyncio import Condition, Lock, Event
from datetime import timedelta
from typing import Any, Optional
import sys

from .utils import get_current_utc_as_int
from .utils import create_access_token
from .utils_async import AsyncTimer
from azure.core.credentials import AccessToken
from entra_token_exchange_async import EntraTokenExchangeClientAsync
from entra_communication_token_credential_options import EntraCommunicationTokenCredentialOptions
from typing import List, Optional
from azure.core.credentials import TokenCredential

class EntraCommunicationTokenCredentialOptions:
    """Options for EntraCommunicationTokenCredential.

    :param str resource_endpoint: The Azure Communication Service resource endpoint URL,
        e.g. https://myResource.communication.azure.com.
    :param ~azure.core.credentials.AsyncTokenCredential token_credential: The Entra ID token credential.
    :param list[str] scopes: The scopes for retrieving the Entra ID access token.
    """

    def __init__(
        self,
        resource_endpoint: str,
        token_credential: AsyncTokenCredential,
        scopes: Optional[List[str]] = None,
    ) -> None:
       
        if not resource_endpoint:
            raise ValueError("resource_endpoint cannot be empty")
        if not token_credential:
            raise ValueError("token_credential cannot be None")
            
        self.resource_endpoint = resource_endpoint
        self.token_credential = token_credential
        self.scopes = scopes or ["https://communication.azure.com/clients/.default"]

class EntraTokenCredential(object):
    """Credential type used for authenticating to an Azure Communication service via Entra ID.
    The provided token will be exchanged for another token used for authentication.
    :param str token: The token to be exchanged.
    :keyword token_refresher: The async token refresher to provide capacity to fetch a fresh token.
    :paramtype token_refresher: Callable[[], Awaitable[AccessToken]]
    :keyword bool proactive_refresh: Whether to refresh the token proactively or not.
    """

    _ON_DEMAND_REFRESHING_INTERVAL_MINUTES = 2
    _DEFAULT_AUTOREFRESH_INTERVAL_MINUTES = 10

    def __init__(self, options: EntraCommunicationTokenCredentialOptions, **kwargs: Any):
        if options is None:
            raise ValueError("Options must be provided.")
        self._token_refresher = kwargs.pop("token_refresher", None)
        self._proactive_refresh = kwargs.pop("proactive_refresh", False)
        if self._proactive_refresh and self._token_refresher is None:
            raise ValueError("When 'proactive_refresh' is True, 'token_refresher' must not be None.")
        self._timer = None
        self._async_mutex = Lock()
        if sys.version_info[:3] == (3, 10, 0):
            # Workaround for Python 3.10 bug(https://bugs.python.org/issue45416):
            getattr(self._async_mutex, "_get_loop", lambda: None)()
        self._lock = Condition(self._async_mutex)
        self._some_thread_refreshing = False
        self._is_closed = Event()
        self._token: AccessToken  # This will be set after exchange
        self._original_token: str = None

    async def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        """Returns the exchanged token."""
        if self._proactive_refresh and self._is_closed.is_set():
            raise RuntimeError("An instance of EntraTokenCredential cannot be reused once it has been closed.")

        if self._token is None:
            self._original_token = await self._get_entra_token(options.token_credential, options.scopes)
            self._token = await self._exchange_token(self._original_token)

        if not self._token_refresher or not self._is_token_expiring_soon(self._token):
            return self._token
        await self._update_token_and_reschedule()
        return self._token

    async def _get_entra_token(self, token_credential, scopes):
        """
        Helper method to get a token from the provided token_credential and scopes.
        """
        token = await token_credential.get_token(*scopes)
        return token.token

    async def _exchange_token(self, original_token):
        """Exchanges the original token for a new token using EntraTokenExchangeClientAsync."""

        # Instantiate the async client with the endpoint and original token
        endpoint = ""  # TO BE DONE

        client = EntraTokenExchangeClientAsync(endpoint, original_token)
        # Optionally, you can pass additional payload via kwargs if needed
        token = await client.exchange_token()
        return AccessToken(token.token, token.expires_on)

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
                new_options = await self._token_refresher()
                new_entra_token = await self._get_entra_token(new_options.token_credential, new_options.scopes)
                new_token = await self._exchange_token(new_entra_token)

                if not self._is_token_valid(new_token):
                    raise ValueError("The token returned from the token_refresher is expired.")
                async with self._lock:
                    self._original_token = new_entra_token
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
            timespan = token_ttl - timedelta(minutes=self._DEFAULT_AUTOREFRESH_INTERVAL_MINUTES).total_seconds()

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
                    "An instance of EntraTokenCredential cannot be reused once it has been closed."
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
