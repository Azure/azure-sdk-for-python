# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from threading import Lock, Condition, Timer
from datetime import timedelta

from typing import (  # pylint: disable=unused-import
    cast,
    Tuple,
    Any
)
import six

from .utils import get_current_utc_as_int
from .utils import create_access_token


class CommunicationTokenCredential(object):
    """Credential type used for authenticating to an Azure Communication service.
    :param str token: The token used to authenticate to an Azure Communication service
    :keyword callable token_refresher: The async token refresher to provide capacity to fetch fresh token
    :keyword bool refresh_proactively: Whether to refresh the token proactively or not
    :keyword timedelta refresh_time_before_expiry: The time before the token expires to refresh the token
    :raises: TypeError
    """

    _ON_DEMAND_REFRESHING_INTERVAL_MINUTES = 2
    _DEFAULT_AUTOREFRESH_INTERVAL_MINUTES = 10

    def __init__(self,
                 token,  # type: str
                 **kwargs  # type: Any
                 ):
        if not isinstance(token, six.string_types):
            raise TypeError("Token must be a string.")
        self._token = create_access_token(token)
        self._token_refresher = kwargs.pop('token_refresher', None)
        self._refresh_proactively = kwargs.pop('refresh_proactively', False)
        self._refresh_time_before_expiry = kwargs.pop('refresh_time_before_expiry', timedelta(
            minutes=self._DEFAULT_AUTOREFRESH_INTERVAL_MINUTES))
        self._timer = None
        self._lock = Condition(Lock())
        self._some_thread_refreshing = False
        if self._refresh_proactively:
            self._schedule_refresh()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._timer is not None:
            self._timer.cancel()

    def get_token(self):
        # type () -> ~azure.core.credentials.AccessToken
        """The value of the configured token.
        :rtype: ~azure.core.credentials.AccessToken
        """

        if not self._token_refresher or not self._token_expiring():
            return self._token

        self._update_token_and_reschedule()
        return self._token

    def _update_token_and_reschedule(self):
        should_this_thread_refresh = False
        with self._lock:
            while self._token_expiring():
                if self._some_thread_refreshing:
                    if self._is_currenttoken_valid():
                        return self._token

                    self._wait_till_inprogress_thread_finish_refreshing()
                else:
                    should_this_thread_refresh = True
                    self._some_thread_refreshing = True
                    break

        if should_this_thread_refresh:
            try:
                newtoken = self._token_refresher()  # pylint:disable=not-callable

                with self._lock:
                    self._token = newtoken
                    self._some_thread_refreshing = False
                    self._lock.notify_all()
            except:
                with self._lock:
                    self._some_thread_refreshing = False
                    self._lock.notify_all()

                raise
        if self._refresh_proactively:
            self._schedule_refresh()
        return self._token

    def _schedule_refresh(self):
        if self._timer is not None:
            self._timer.cancel()

        timespan = self._token.expires_on - \
            get_current_utc_as_int() - self._refresh_time_before_expiry.total_seconds()
        self._timer = Timer(timespan, self._update_token_and_reschedule)
        self._timer.start()

    def _wait_till_inprogress_thread_finish_refreshing(self):
        self._lock.release()
        self._lock.acquire()

    def _token_expiring(self):
        if self._refresh_proactively:
            interval = self._refresh_time_before_expiry
        else:
            interval = timedelta(
                minutes=self._ON_DEMAND_REFRESHING_INTERVAL_MINUTES)
        return self._token.expires_on - get_current_utc_as_int() <\
            interval.total_seconds()

    def _is_currenttoken_valid(self):
        return get_current_utc_as_int() < self._token.expires_on
