# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from threading import Lock, Condition, Timer, TIMEOUT_MAX, Event
from datetime import timedelta
from typing import Any, Optional, overload, Callable
from azure.core.credentials import TokenCredential, AccessToken
from .utils import get_current_utc_as_int
from .utils import create_access_token
from .token_exchange import TokenExchangeClient


class CommunicationTokenCredential(object):
    """Credential type used for authenticating to an Azure Communication service.

    :param str token: The token used to authenticate to an Azure Communication service.
    :keyword token_refresher: The sync token refresher to provide capacity to fetch a fresh token.
     The returned token must be valid (expiration date must be in the future).
    :paramtype token_refresher: Callable[[], AccessToken]
    :keyword bool proactive_refresh: Whether to refresh the token proactively or not.
     If the proactive refreshing is enabled ('proactive_refresh' is true), the credential will use
     a background thread to attempt to refresh the token within 10 minutes before the cached token expires.
     The proactive refresh will request a new token by calling the 'token_refresher' callback.
     When 'proactive_refresh' is enabled, the Credential object must be either run within a context manager
     or the 'close' method must be called once the object usage has been finished.
    :keyword str resource_endpoint: The endpoint URL of the resource to authenticate against.
    :keyword token_credential: The credential to use for token exchange.
    :paramtype token_credential: ~azure.core.credentials.TokenCredential
    :keyword list[str] scopes: The scopes to request during the token exchange. If not provided,
     a default value will be used: https://communication.azure.com/clients/.default

    :raises: TypeError if parameter 'token' is not a string
    :raises: ValueError if the 'proactive_refresh' is enabled without providing the 'token_refresher' callable.
    """

    _ON_DEMAND_REFRESHING_INTERVAL_MINUTES = 2
    _DEFAULT_AUTOREFRESH_INTERVAL_MINUTES = 10

    @overload
    def __init__(
        self,
        token: str,
        *,
        token_refresher: Optional[Callable[[], AccessToken]] = None,
        proactive_refresh: bool = False,
        **kwargs: Any
    ):
        """
        Initializes the CommunicationTokenCredential.

        :param str token: The token used to authenticate to an Azure Communication service.
        :param token_refresher: Optional callable to refresh the token.
        :param proactive_refresh: Whether to refresh the token proactively.
        :param kwargs: Additional keyword arguments.
        """

    @overload
    def __init__(
        self,
        *,
        resource_endpoint: str,
        token_credential: TokenCredential,
        scopes: Optional[list[str]] = None,
        **kwargs: Any
    ):
        """
        Initializes the CommunicationTokenCredential using token exchange.

        :param resource_endpoint: The endpoint URL of the resource to authenticate against.
        :param token_credential: The credential to use for token exchange.
        :param scopes: The scopes to request during the token exchange.
        :param kwargs: Additional keyword arguments.
        """

    def __init__(self, token: Optional[str] = None, **kwargs: Any):
        resource_endpoint = kwargs.pop("resource_endpoint", None)
        token_credential = kwargs.pop("token_credential", None)
        scopes = kwargs.pop("scopes", None)

        # Check if at least one field exists but not all fields exist when token is None
        fields_present = [resource_endpoint, token_credential]
        fields_exist = [field is not None for field in fields_present]

        if token is None and not all(fields_exist):
            missing_fields = []
            if resource_endpoint is None:
                missing_fields.append("resource_endpoint")
            if token_credential is None:
                missing_fields.append("token_credential")
            raise ValueError(
            "When using token exchange, resource_endpoint and token_credential must be provided. "
            f"Missing: {', '.join(missing_fields)}")

        self._token_exchange_client = None
        if resource_endpoint and token_credential:
            self._token_exchange_client = TokenExchangeClient(
                resource_endpoint,
                token_credential,
                scopes)
            self._token_refresher = self._token_exchange_client.exchange_entra_token
            self._proactive_refresh = False
            self._token = self._token_exchange_client.exchange_entra_token()
        else:
            if not isinstance(token, str):
                raise TypeError("Token must be a string.")
            self._token = create_access_token(token)
            self._token_refresher = kwargs.pop("token_refresher", None)
            self._proactive_refresh = kwargs.pop("proactive_refresh", False)
            if self._proactive_refresh and self._token_refresher is None:
                raise ValueError("When 'proactive_refresh' is True, 'token_refresher' must not be None.")
        self._timer = None
        self._lock = Condition(Lock())
        self._some_thread_refreshing = False
        self._is_closed = Event()

    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        # type (*str, **Any) -> AccessToken
        """The value of the configured token.
        :param any scopes: Scopes to be added to the token.
        :return: AccessToken
        :rtype: ~azure.core.credentials.AccessToken
        """
        if self._proactive_refresh and self._is_closed.is_set():
            raise RuntimeError("An instance of CommunicationTokenCredential cannot be reused once it has been closed.")

        if not self._token_refresher or not self._is_token_expiring_soon(self._token):
            return self._token
        self._update_token_and_reschedule()
        return self._token

    def _update_token_and_reschedule(self):
        should_this_thread_refresh = False
        with self._lock:
            while self._is_token_expiring_soon(self._token):
                if self._some_thread_refreshing:
                    if self._is_token_valid(self._token):
                        return self._token
                    self._wait_till_lock_owner_finishes_refreshing()
                else:
                    should_this_thread_refresh = True
                    self._some_thread_refreshing = True
                    break

        if should_this_thread_refresh:
            try:
                new_token = self._token_refresher()
                if not self._is_token_valid(new_token):
                    raise ValueError("The token returned from the token_refresher is expired.")
                with self._lock:
                    self._token = new_token
                    self._some_thread_refreshing = False
                    self._lock.notify_all()
            except:
                with self._lock:
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
        if timespan <= TIMEOUT_MAX:
            self._timer = Timer(timespan, self._update_token_and_reschedule)
            self._timer.daemon = True
            self._timer.start()

    def _wait_till_lock_owner_finishes_refreshing(self):
        self._lock.release()
        self._lock.acquire()

    def _is_token_expiring_soon(self, token):
        if self._proactive_refresh:
            interval = timedelta(minutes=self._DEFAULT_AUTOREFRESH_INTERVAL_MINUTES)
        else:
            interval = timedelta(minutes=self._ON_DEMAND_REFRESHING_INTERVAL_MINUTES)
        return (token.expires_on - get_current_utc_as_int()) < interval.total_seconds()

    @classmethod
    def _is_token_valid(cls, token):
        return get_current_utc_as_int() < token.expires_on

    def __enter__(self):
        if self._proactive_refresh:
            if self._is_closed.is_set():
                raise RuntimeError(
                    "An instance of CommunicationTokenCredential cannot be reused once it has been closed."
                )
            self._schedule_refresh()
        return self

    def __exit__(self, *args):
        self.close()

    def close(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
        self._timer = None
        self._is_closed.set()
