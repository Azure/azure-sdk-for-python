#pylint: disable=no-self-use
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
import logging
import time
import email
from typing import TYPE_CHECKING, List, Callable, Iterator, Any, Union, Dict, Optional  # pylint: disable=unused-import
from azure.core.pipeline import PipelineResponse
from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    ServiceResponseError,
    ServiceRequestError
)

from .base import HTTPPolicy, RequestHistory


_LOGGER = logging.getLogger(__name__)


class RetryPolicy(HTTPPolicy):
    """A retry policy.

    The retry policy in the pipeline can be configured directly, or tweaked on a per-call basis.

    **Keyword arguments:**

    *retry_total (int)* - Total number of retries to allow. Takes precedence over other counts.
    Default value is 10.

    *retry_connect (int)* - How many connection-related errors to retry on.
    These are errors raised before the request is sent to the remote server,
    which we assume has not triggered the server to process the request. Default value is 3.

    *retry_read (int)* - How many times to retry on read errors.
    These errors are raised after the request was sent to the server, so the
    request may have side-effects. Default value is 3.

    *retry_status (int)* - How many times to retry on bad status codes. Default value is 3.

    *retry_backoff_factor (float)* - A backoff factor to apply between attempts after the second try
    (most errors are resolved immediately by a second try without a delay).
    Retry policy will sleep for: `{backoff factor} * (2 ** ({number of total retries} - 1))`
    seconds. If the backoff_factor is 0.1, then the retry will sleep
    for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.

    *retry_backoff_max (int)* - The maximum back off time. Default value is 120 seconds (2 minutes).

    .. admonition:: Example:

        .. literalinclude:: ../examples/test_example_sync.py
            :start-after: [START retry_policy]
            :end-before: [END retry_policy]
            :language: python
            :dedent: 4
            :caption: Configuring a retry policy.
    """

    #: Maximum backoff time.
    BACKOFF_MAX = 120

    def __init__(self, **kwargs):
        self.total_retries = kwargs.pop('retry_total', 10)
        self.connect_retries = kwargs.pop('retry_connect', 3)
        self.read_retries = kwargs.pop('retry_read', 3)
        self.status_retries = kwargs.pop('retry_status', 3)
        self.backoff_factor = kwargs.pop('retry_backoff_factor', 0.8)
        self.backoff_max = kwargs.pop('retry_backoff_max', self.BACKOFF_MAX)

        safe_codes = [i for i in range(500) if i != 408] + [501, 505]
        retry_codes = [i for i in range(999) if i not in safe_codes]
        status_codes = kwargs.pop('retry_on_status_codes', [])
        self._retry_on_status_codes = set(status_codes + retry_codes)
        self._method_whitelist = frozenset(['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'])
        self._respect_retry_after_header = True
        super(RetryPolicy, self).__init__()

    @classmethod
    def no_retries(cls):
        """Disable retries.
        """
        return cls(retry_total=0)

    def configure_retries(self, options):
        """Configures the retry settings.

        :param options: keyword arguments from context.
        :return: A dict containing settings and history for retries.
        :rtype: dict
        """
        return {
            'total': options.pop("retry_total", self.total_retries),
            'connect': options.pop("retry_connect", self.connect_retries),
            'read': options.pop("retry_read", self.read_retries),
            'status': options.pop("retry_status", self.status_retries),
            'backoff': options.pop("retry_backoff_factor", self.backoff_factor),
            'max_backoff': options.pop("retry_backoff_max", self.BACKOFF_MAX),
            'methods': options.pop("retry_on_methods", self._method_whitelist),
            'history': []
        }

    def get_backoff_time(self, settings):
        """Returns the current backoff time.

        :param dict settings: The retry settings.
        :return: The current backoff value.
        :rtype: float
        """
        # We want to consider only the last consecutive errors sequence (Ignore redirects).
        consecutive_errors_len = len(settings['history'])
        if consecutive_errors_len <= 1:
            return 0

        backoff_value = settings['backoff'] * (2 ** (consecutive_errors_len - 1))
        return min(settings['max_backoff'], backoff_value)

    def parse_retry_after(self, retry_after):
        """Helper to parse Retry-After and get value in seconds.

        :param str retry_after: Retry-After header
        :rtype: int
        """
        try:
            seconds = int(retry_after)
        except TypeError:
            retry_date_tuple = email.utils.parsedate(retry_after)
            if retry_date_tuple is None:
                return None
            retry_date = time.mktime(retry_date_tuple)
            seconds = retry_date - time.time()

        if seconds < 0:
            seconds = 0
        return seconds

    def get_retry_after(self, response):
        """Get the value of Retry-After in seconds.

        :param response: The PipelineResponse object
        :type response: ~azure.core.pipeline.PipelineResponse
        :return: Value of Retry-After in seconds.
        :rtype: int
        """
        retry_after = response.http_response.headers.get("Retry-After")
        if retry_after is None:
            return None
        return self.parse_retry_after(retry_after)

    def _sleep_for_retry(self, response, transport):
        """Sleep based on the Retry-After response header value.

        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        :param transport: The HTTP transport type.
        """
        retry_after = self.get_retry_after(response)
        if retry_after:
            transport.sleep(retry_after)
            return True
        return False

    def _sleep_backoff(self, settings, transport):
        """Sleep using exponential backoff. Immediately returns if backoff is 0.

        :param dict settings: The retry settings.
        :param transport: The HTTP transport type.
        """
        backoff = self.get_backoff_time(settings)
        if backoff <= 0:
            return
        transport.sleep(backoff)

    def sleep(self, settings, transport, response=None):
        """Sleep between retry attempts.

        This method will respect a server's ``Retry-After`` response header
        and sleep the duration of the time requested. If that is not present, it
        will use an exponential backoff. By default, the backoff factor is 0 and
        this method will return immediately.

        :param dict settings: The retry settings.
        :param transport: The HTTP transport type.
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        """
        if response:
            slept = self._sleep_for_retry(response, transport)
            if slept:
                return
        self._sleep_backoff(settings, transport)

    def _is_connection_error(self, err):
        """Errors when we're fairly sure that the server did not receive the
        request, so it should be safe to retry.
        """
        return isinstance(err, ServiceRequestError)

    def _is_read_error(self, err):
        """Errors that occur after the request has been started, so we should
        assume that the server began processing it.
        """
        return isinstance(err, ServiceResponseError)

    def _is_method_retryable(self, settings, request, response=None):
        """Checks if a given HTTP method should be retried upon, depending if
        it is included on the method whitelist.

        :param dict settings: The retry settings.
        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        :return: True if method should be retried upon. False if not in method whitelist.
        :rtype: bool
        """
        if response and request.method.upper() in ['POST', 'PATCH'] and \
                response.status_code in [500, 503, 504]:
            return True
        if request.method.upper() not in settings['methods']:
            return False

        return True

    def is_retry(self, settings, response):
        """Checks if method/status code is retryable.

        Based on whitelists and control variables such as the number of
        total retries to allow, whether to respect the Retry-After header,
        whether this header is present, and whether the returned status
        code is on the list of status codes to be retried upon on the
        presence of the aforementioned header.

        :param dict settings: The retry settings.
        :param response: The PipelineResponse object
        :type response: ~azure.core.pipeline.PipelineResponse
        :return: True if method/status code is retryable. False if not retryable.
        :rtype: bool
        """
        has_retry_after = bool(response.http_response.headers.get("Retry-After"))
        if has_retry_after and self._respect_retry_after_header:
            return True
        if not self._is_method_retryable(settings, response.http_request, response=response.http_response):
            return False
        return settings['total'] and response.http_response.status_code in self._retry_on_status_codes

    def is_exhausted(self, settings):
        """Checks if any retries left.

        :param dict settings: the retry settings
        :return: False if have more retries. True if retries exhausted.
        :rtype: bool
        """
        retry_counts = (settings['total'], settings['connect'], settings['read'], settings['status'])
        retry_counts = list(filter(None, retry_counts))
        if not retry_counts:
            return False

        return min(retry_counts) < 0

    def increment(self, settings, response=None, error=None):
        """Increment the retry counters.

        :param settings: The retry settings.
        :param response: A pipeline response object.
        :type response: ~azure.core.pipeline.PipelineResponse
        :param error: An error encountered during the request, or
         None if the response was received successfully.
        :return: Whether the retry attempts are exhausted.
         False if exhausted; True if more retry attempts available.
        :rtype: bool
        """
        settings['total'] -= 1

        if isinstance(response, PipelineResponse) and response.http_response.status_code == 202:
            return False

        if error and self._is_connection_error(error):
            # Connect retry?
            settings['connect'] -= 1
            settings['history'].append(RequestHistory(response.http_request, error=error))

        elif error and self._is_read_error(error):
            # Read retry?
            settings['read'] -= 1
            settings['history'].append(RequestHistory(response.http_request, error=error))

        else:
            # Incrementing because of a server error like a 500 in
            # status_forcelist and a the given method is in the whitelist
            if response:
                settings['status'] -= 1
                settings['history'].append(RequestHistory(response.http_request, http_response=response.http_response))

        return not self.is_exhausted(settings)

    def update_context(self, context, retry_settings):
        """Updates retry history in pipeline context.

        :param context: The pipeline context.
        :type context: ~azure.core.pipeline.PipelineContext
        :param retry_settings: The retry settings.
        :type retry_settings: dict
        """
        if retry_settings['history']:
            context['history'] = retry_settings['history']

    def send(self, request):
        """Sends the PipelineRequest object to the next policy. Uses retry settings if necessary.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: Returns the PipelineResponse or raises error if maximum retries exceeded.
        :rtype: ~azure.core.pipeline.PipelineResponse
        :raises: ~azure.core.exceptions.AzureError if maximum retries exceeded.
        :raises: ~azure.core.exceptions.ClientAuthenticationError if authentication
        """
        retry_active = True
        response = None
        retry_settings = self.configure_retries(request.context.options)
        while retry_active:
            try:
                response = self.next.send(request)
                if self.is_retry(retry_settings, response):
                    retry_active = self.increment(retry_settings, response=response)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport, response=response)
                        continue
                break
            except ClientAuthenticationError:  # pylint:disable=try-except-raise
                # the authentication policy failed such that the client's request can't
                # succeed--we'll never have a response to it, so propagate the exception
                raise
            except AzureError as err:
                if self._is_method_retryable(retry_settings, request.http_request):
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport)
                        continue
                raise err

        self.update_context(response.context, retry_settings)
        return response
