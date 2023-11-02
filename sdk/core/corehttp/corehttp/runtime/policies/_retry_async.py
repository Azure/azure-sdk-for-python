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
from __future__ import annotations
from typing import Dict, Any, Optional, cast, TYPE_CHECKING
import logging
import time

from ...transport import AsyncHttpTransport
from ...rest import AsyncHttpResponse, HttpRequest
from ...exceptions import (
    BaseError,
    ClientAuthenticationError,
    ServiceRequestError,
)
from ._base_async import AsyncHTTPPolicy
from ._retry import RetryPolicyBase

if TYPE_CHECKING:
    from ...runtime.pipeline import PipelineRequest, PipelineResponse

_LOGGER = logging.getLogger(__name__)


class AsyncRetryPolicy(RetryPolicyBase, AsyncHTTPPolicy[HttpRequest, AsyncHttpResponse]):
    """Async flavor of the retry policy.

    The async retry policy in the pipeline can be configured directly, or tweaked on a per-call basis.

    :keyword int retry_total: Total number of retries to allow. Takes precedence over other counts.
     Default value is 10.

    :keyword int retry_connect: How many connection-related errors to retry on.
     These are errors raised before the request is sent to the remote server,
     which we assume has not triggered the server to process the request. Default value is 3.

    :keyword int retry_read: How many times to retry on read errors.
     These errors are raised after the request was sent to the server, so the
     request may have side-effects. Default value is 3.

    :keyword int retry_status: How many times to retry on bad status codes. Default value is 3.

    :keyword float retry_backoff_factor: A backoff factor to apply between attempts after the second try
     (most errors are resolved immediately by a second try without a delay).
     Retry policy will sleep for: `{backoff factor} * (2 ** ({number of total retries} - 1))`
     seconds. If the backoff_factor is 0.1, then the retry will sleep
     for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.

    :keyword int retry_backoff_max: The maximum back off time. Default value is 120 seconds (2 minutes).
    """

    async def _sleep_for_retry(
        self,
        response: PipelineResponse[HttpRequest, AsyncHttpResponse],
        transport: AsyncHttpTransport[HttpRequest, AsyncHttpResponse],
    ) -> bool:
        """Sleep based on the Retry-After response header value.

        :param response: The PipelineResponse object.
        :type response: ~corehttp.runtime.pipeline.PipelineResponse
        :param transport: The HTTP transport type.
        :type transport: ~corehttp.transport.AsyncHttpTransport
        :return: Whether the retry-after value was found.
        :rtype: bool
        """
        retry_after = self.get_retry_after(response)
        if retry_after:
            await transport.sleep(retry_after)
            return True
        return False

    async def _sleep_backoff(
        self, settings: Dict[str, Any], transport: AsyncHttpTransport[HttpRequest, AsyncHttpResponse]
    ) -> None:
        """Sleep using exponential backoff. Immediately returns if backoff is 0.

        :param dict settings: The retry settings.
        :param transport: The HTTP transport type.
        :type transport: ~corehttp.transport.AsyncHttpTransport
        """
        backoff = self.get_backoff_time(settings)
        if backoff <= 0:
            return
        await transport.sleep(backoff)

    async def sleep(
        self,
        settings: Dict[str, Any],
        transport: AsyncHttpTransport[HttpRequest, AsyncHttpResponse],
        response: Optional[PipelineResponse[HttpRequest, AsyncHttpResponse]] = None,
    ) -> None:
        """Sleep between retry attempts.

        This method will respect a server's ``Retry-After`` response header
        and sleep the duration of the time requested. If that is not present, it
        will use an exponential backoff. By default, the backoff factor is 0 and
        this method will return immediately.

        :param dict settings: The retry settings.
        :param transport: The HTTP transport type.
        :type transport: ~corehttp.transport.AsyncHttpTransport
        :param response: The PipelineResponse object.
        :type response: ~corehttp.runtime.pipeline.PipelineResponse
        """
        if response:
            slept = await self._sleep_for_retry(response, transport)
            if slept:
                return
        await self._sleep_backoff(settings, transport)

    async def send(self, request: PipelineRequest[HttpRequest]) -> PipelineResponse[HttpRequest, AsyncHttpResponse]:
        """Uses the configured retry policy to send the request to the next policy in the pipeline.

        :param request: The PipelineRequest object
        :type request: ~corehttp.runtime.pipeline.PipelineRequest
        :return: Returns the PipelineResponse or raises error if maximum retries exceeded.
        :rtype: ~corehttp.runtime.pipeline.PipelineResponse
        :raise: ~corehttp.exceptions.BaseError if maximum retries exceeded.
        :raise: ~corehttp.exceptions.ClientAuthenticationError if authentication fails
        """
        retry_active = True
        response = None
        retry_settings = self.configure_retries(request.context.options)
        self._configure_positions(request, retry_settings)

        absolute_timeout = retry_settings["timeout"]
        is_response_error = True

        while retry_active:
            start_time = time.time()
            # PipelineContext types transport as a Union of HttpTransport and AsyncHttpTransport, but
            # here we know that this is an AsyncHttpTransport.
            # The correct fix is to make PipelineContext generic, but that's a breaking change and a lot of
            # generic to update in Pipeline, PipelineClient, PipelineRequest, PipelineResponse, etc.
            transport: AsyncHttpTransport[HttpRequest, AsyncHttpResponse] = cast(
                AsyncHttpTransport[HttpRequest, AsyncHttpResponse], request.context.transport
            )
            try:
                self._configure_timeout(request, absolute_timeout, is_response_error)
                response = await self.next.send(request)
                if self.is_retry(retry_settings, response):
                    retry_active = self.increment(retry_settings, response=response)
                    if retry_active:
                        await self.sleep(
                            retry_settings,
                            transport,
                            response=response,
                        )
                        is_response_error = True
                        continue
                break
            except ClientAuthenticationError:  # pylint:disable=try-except-raise
                # the authentication policy failed such that the client's request can't
                # succeed--we'll never have a response to it, so propagate the exception
                raise
            except BaseError as err:
                if absolute_timeout > 0 and self._is_method_retryable(retry_settings, request.http_request):
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        await self.sleep(retry_settings, transport)
                        if isinstance(err, ServiceRequestError):
                            is_response_error = False
                        else:
                            is_response_error = True
                        continue
                raise err
            finally:
                end_time = time.time()
                if absolute_timeout:
                    absolute_timeout -= end_time - start_time
        if not response:
            raise BaseError("Maximum retries exceeded.")

        self.update_context(response.context, retry_settings)
        return response
