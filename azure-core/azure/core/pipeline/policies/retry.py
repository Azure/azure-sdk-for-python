# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""
This module is the requests implementation of Pipeline ABC
"""
from __future__ import absolute_import  # we have a "requests" module that conflicts with "requests" on Py2.7
import contextlib
import logging
import threading
from typing import TYPE_CHECKING, List, Callable, Iterator, Any, Union, Dict, Optional  # pylint: disable=unused-import
import warnings

from azure.core.exceptions import (
    MaxRetryError,
    TokenExpiredError,
    TokenInvalidError,
    AuthenticationError,
    ClientRequestError,
    raise_with_traceback
)

from .base import HTTPPolicy, RequestHistory


_LOGGER = logging.getLogger(__name__)


class RetryPolicy(HTTPPolicy):

    #: Maximum backoff time.
    BACKOFF_MAX = 120

    def __init__(self, **kwargs):
        safe_codes = [i for i in range(500) if i != 408] + [501, 505]
        retry_codes = [i for i in range(999) if i not in safe_codes]
        status_codes = kwargs.pop('retry_on_status_codes', [])
        self.retry_on_status_codes = set(status_codes + retry_codes)

        self.total_retries = kwargs.pop('retry_count_total', 10)
        self.connect_retries = kwargs.pop('retry_count_connect', 3)
        self.read_retries = kwargs.pop('retry_count_read', 3)
        self.status_retries = kwargs.pop('retry_count_status', 3)
        self.backoff_factor = kwargs.pop('retry_backoff_factor', 0.8)
        self.backoff_max = kwargs.pop('retry_backoff_max', self.BACKOFF_MAX)

        self.history = []

        self.status_forcelist = set()
        self.method_whitelist = frozenset(['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'])
        self.raise_on_status = True
        self.respect_retry_after_header = True

    @classmethod
    def no_retries(cls):
        return cls(retry_count_total=False)

    def get_backoff_time(self):
        """ Formula for computing the current backoff

        :rtype: float
        """
        # We want to consider only the last consecutive errors sequence (Ignore redirects).
        consecutive_errors_len = len(self.history)
        if consecutive_errors_len <= 1:
            return 0

        backoff_value = self.backoff_factor * (2 ** (consecutive_errors_len - 1))
        return min(self.BACKOFF_MAX, backoff_value)

    def parse_retry_after(self, retry_after):
        # Whitespace: https://tools.ietf.org/html/rfc7230#section-3.2.4
        if re.match(r"^\s*[0-9]+\s*$", retry_after):
            seconds = int(retry_after)
        else:
            retry_date_tuple = email.utils.parsedate(retry_after)
            if retry_date_tuple is None:
                raise InvalidHeader("Invalid Retry-After header: %s" % retry_after)
            retry_date = time.mktime(retry_date_tuple)
            seconds = retry_date - time.time()

        if seconds < 0:
            seconds = 0

        return seconds

    def get_retry_after(self, response):
        """ Get the value of Retry-After in seconds. """

        retry_after = response.http_response.headers.get("Retry-After")

        if retry_after is None:
            return None

        return self.parse_retry_after(retry_after)

    def sleep_for_retry(self, response):
        retry_after = self.get_retry_after(response)
        if retry_after:
            time.sleep(retry_after)
            return True

        return False

    def _sleep_backoff(self):
        backoff = self.get_backoff_time()
        if backoff <= 0:
            return
        time.sleep(backoff)

    def sleep(self, response=None):
        """ Sleep between retry attempts.

        This method will respect a server's ``Retry-After`` response header
        and sleep the duration of the time requested. If that is not present, it
        will use an exponential backoff. By default, the backoff factor is 0 and
        this method will return immediately.
        """

        if response:
            slept = self.sleep_for_retry(response)
            if slept:
                return

        self._sleep_backoff()

    def _is_connection_error(self, err):
        """ Errors when we're fairly sure that the server did not receive the
        request, so it should be safe to retry.
        """
        return isinstance(err, ConnectionError)

    def _is_read_error(self, err):
        """ Errors that occur after the request has been started, so we should
        assume that the server began processing it.
        """
        return isinstance(err, ConnectionReadError)

    def _is_method_retryable(self, method):
        """ Checks if a given HTTP method should be retried upon, depending if
        it is included on the method whitelist.
        """
        if self.method_whitelist and method.upper() not in self.method_whitelist:
            return False

        return True

    def is_retry(self, response):
        """ Is this method/status code retryable? (Based on whitelists and control
        variables such as the number of total retries to allow, whether to
        respect the Retry-After header, whether this header is present, and
        whether the returned status code is on the list of status codes to
        be retried upon on the presence of the aforementioned header)
        """
        has_retry_after = bool(response.http_response.headers.get("Retry-After"))

        if not self._is_method_retryable(response.http_request.method):
            return False

        if self.status_forcelist and response.http_response.status_code in self.status_forcelist:
            return True

        return (self.total_retries and self.respect_retry_after_header and
                has_retry_after and (response.http_response.status_code in self.retry_on_status_codes))

    def is_exhausted(self):
        """ Are we out of retries? """
        retry_counts = (self.total_retries, self.connect_retries, self.read_retries, self.status_retries)
        retry_counts = list(filter(None, retry_counts))
        if not retry_counts:
            return False

        return min(retry_counts) < 0

    def increment(self, response=None, error=None):
        """ Return a new Retry object with incremented retry counters.

        :param response: A response object, or None, if the server did not
            return a response.
        :type response: :class:`~urllib3.response.HTTPResponse`
        :param Exception error: An error encountered during the request, or
            None if the response was received successfully.

        :return: A new ``Retry`` object.
        """
        if self.total_retries is False and error:
            # Disabled, indicate to re-raise the error.
            raise_with_traceback(error)

        if self.total_retries is not None:
            self.total_retries -= 1

        if error and self._is_connection_error(error):
            # Connect retry?
            if self.connect_retries is False:
                raise_with_traceback(error)
            elif self.connect_retries is not None:
                self.connect_retries -= 1
            self.history.append(RequestHistory(response.http_request, error=error))

        #elif error and self._is_read_error(error):
        #    # Read retry?
        #    if self.read is False or not self._is_method_retryable(method):
        #        raise_with_traceback(error)
        #    elif self.read is not None:
        #        self.read -= 1
        #    self.history.append(RequestHistory(response.http_request, error=error))

        else:
            # Incrementing because of a server error like a 500 in
            # status_forcelist and a the given method is in the whitelist
            if response:
                if self.status_retries is not None:
                    self.status_retries -= 1
                self.history.append(RequestHistory(response.http_request, http_response=response.http_response))

        return not self.is_exhausted()

    def send(self, request, **kwargs):
        retryable = True
        response = None
        while retryable:
            try:
                response = self.next.send(request, **kwargs)
                if self.is_retry(response):
                    retryable = self.increment(response=response)
                    if retryable or self.raise_on_status:
                        continue
                response.history = self.history
                return response
            except AuthenticationError:
                raise
            except ClientRequestError as err:
                #if retryable:
                #    retryable = self.increment(error=err)
                #    if retryable:
                #        self.sleep()
                #    continue
                raise

        raise MaxRetryError(response, self.history)