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

from .base import HTTPPolicy
from .base_async import AsyncHTTPPolicy
from .retry import RetryPolicy

from azure.core.exceptions import AzureError

_LOGGER = logging.getLogger(__name__)



class AsyncRetryPolicy(RetryPolicy, AsyncHTTPPolicy):


    async def _sleep_for_retry(self, response, transport):
        retry_after = self.get_retry_after(response)
        if retry_after:
            await transport.sleep(retry_after)
            return True
        return False

    async def _sleep_backoff(self, settings, transport):
        backoff = self.get_backoff_time(settings)
        if backoff <= 0:
            return
        await transport.sleep(backoff)

    async def sleep(self, settings, transport, response=None):
        """ Sleep between retry attempts.

        This method will respect a server's ``Retry-After`` response header
        and sleep the duration of the time requested. If that is not present, it
        will use an exponential backoff. By default, the backoff factor is 0 and
        this method will return immediately.
        """
        if response:
            slept = await self._sleep_for_retry(response, transport)
            if slept:
                return
        await self._sleep_backoff(settings, transport)

    async def send(self, request):
        retries_remaining = True
        response = None
        retry_settings = self.configure_retries(request.context.options)
        while retries_remaining:
            try:
                response = await self.next.send(request)
                if self.is_retry(retry_settings, response):
                    retries_remaining = self.increment(retry_settings, response=response)
                    if retries_remaining:
                        await self.sleep(retry_settings, request.context.transport, response=response)
                        continue
                return response
            except AzureError as err:
                if self._is_method_retryable(retry_settings, request.http_request):
                    retries_remaining = self.increment(retry_settings, response=request, error=err)
                    if retries_remaining:
                        await self.sleep(retry_settings, request.context.transport)
                        continue
                raise err
        return response