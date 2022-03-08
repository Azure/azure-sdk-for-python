# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from threading import Lock, Condition, Timer, TIMEOUT_MAX
from datetime import timedelta
from typing import Any
import six
from .utils import get_current_utc_as_int
from .utils import create_access_token


class CommunicationTokenCredential(object):
    """Credential type used for authenticating to an Azure Communication service.
    :param str token: The token used to authenticate to an Azure Communication service.
    :keyword token_refresher: The sync token refresher to provide capacity to fetch a fresh token.
     The returned token must be valid (expiration date must be in the future).
    :paramtype token_refresher: Callable[[], AccessToken]
    :keyword bool proactive_refresh: Whether to refresh the token proactively or not.
    :raises: TypeError if paramater 'token' is not a string
    :raises: ValueError if the 'proactive_refresh' is enabled without providing the 'token_refresher' callable.
    """

    _ON_DEMAND_REFRESHING_INTERVAL_MINUTES = 2
    _DEFAULT_AUTOREFRESH_INTERVAL_MINUTES = 10

    def __init__(self, token: str, **kwargs: Any):
        if not isinstance(token, six.string_types):
            raise TypeError("Token must be a string.")
        self._token = create_access_token(token)
        self._token_refresher = kwargs.pop('token_refresher', None)
        self._proactive_refresh = kwargs.pop('proactive_refresh', False)
        if(self._proactive_refresh and self._token_refresher is None):
            raise ValueError("'token_refresher' must not be None.")
        self._timer = None
        self._lock = Condition(Lock())
        self._some_thread_refreshing = False

    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        # type (*str, **Any) -> AccessToken
        """The value of the configured token.
        :rtype: ~azure.core.credentials.AccessToken
        """

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
                    raise ValueError(
                        "The token returned from the token_refresher is expired.")
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
        if self._timer is not None:
            self._timer.cancel()

        token_ttl = self._token.expires_on - get_current_utc_as_int()

        if self._is_token_expiring_soon(self._token):
            # Schedule the next refresh for when it reaches a certain percentage of the remaining lifetime.
            timespan = token_ttl // 2
        else:
            # Schedule the next refresh for when it gets in to the soon-to-expire window.
            timespan = token_ttl - timedelta(
                minutes=self._DEFAULT_AUTOREFRESH_INTERVAL_MINUTES).total_seconds()
        if timespan <= TIMEOUT_MAX:
            self._timer = Timer(timespan, self._update_token_and_reschedule)
            self._timer.start()

    def _wait_till_lock_owner_finishes_refreshing(self):
        self._lock.release()
        self._lock.acquire()

    def _is_token_expiring_soon(self, token):
        if self._proactive_refresh:
            interval = timedelta(
                minutes=self._DEFAULT_AUTOREFRESH_INTERVAL_MINUTES)
        else:
            interval = timedelta(
                minutes=self._ON_DEMAND_REFRESHING_INTERVAL_MINUTES)
        return ((token.expires_on - get_current_utc_as_int())
            < interval.total_seconds())

    @classmethod
    def _is_token_valid(cls, token):
        return get_current_utc_as_int() < token.expires_on

    def __enter__(self):
        if self._proactive_refresh:
            self._schedule_refresh()
        return self

    def __exit__(self, *args):
        self.close()

    def close(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
        self._timer = None
