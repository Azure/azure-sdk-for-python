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
from ..exceptions import ARMError
from .arm_polling import (
    failed,
    BadStatus,
    BadResponse,
    OperationFailed,
    ARMPolling
)

__all__ = ["AsyncARMPolling"]

class AsyncARMPolling(ARMPolling):
    """A subclass or ARMPolling that redefine "run" as async.
    """

    async def run(self):
        try:
            await self._poll()
        except BadStatus as err:
            self._operation.status = 'Failed'
            raise ARMError(self._pipeline_response.http_response, error=err)

        except BadResponse as err:
            self._operation.status = 'Failed'
            raise ARMError(self._pipeline_response.http_response, message=str(err), error=err)

        except OperationFailed as err:
            raise ARMError(self._pipeline_response.http_response, error=err)

    async def _poll(self):
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :param callable update_cmd: The function to call to retrieve the
         latest status of the long running operation.
        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        while not self.finished():
            await self._delay()
            await self.update_status()

        if failed(self._operation.status):
            raise OperationFailed("Operation failed or canceled")

        elif self._operation.should_do_final_get():
            if self._operation.method == 'POST' and self._operation.location_url:
                final_get_url = self._operation.location_url
            else:
                final_get_url = self._operation.initial_response.http_response.request.url
            self._pipeline_response = await self.request_status(final_get_url)
            self._operation.parse_resource(self._pipeline_response)

    async def _sleep(self, delay):
        await self._transport.sleep(delay)

    async def _delay(self):
        """Check for a 'retry-after' header to set timeout,
        otherwise use configured timeout.
        """
        if self._pipeline_response is None:
            return
        response = self._pipeline_response.http_response
        if response.headers.get('retry-after'):
            await self._sleep(int(response.headers['retry-after']))
        else:
            await self._sleep(self._timeout)

    async def update_status(self):
        """Update the current status of the LRO.
        """
        if self._operation.async_url:
            self._pipeline_response = await self.request_status(self._operation.async_url)
            self._operation.set_async_url_if_present(self._pipeline_response.http_response)
            self._operation.get_status_from_async(self._pipeline_response)
        elif self._operation.location_url:
            self._pipeline_response = await self.request_status(self._operation.location_url)
            self._operation.set_async_url_if_present(self._pipeline_response.http_response)
            self._operation.get_status_from_location(self._pipeline_response)
        elif self._operation.method == "PUT":
            initial_url = self._operation.initial_response.http_response.request.url
            self._pipeline_response = await self.request_status(initial_url)
            self._operation.set_async_url_if_present(self._pipeline_response.http_response)
            self._operation.get_status_from_resource(self._pipeline_response)
        else:
            raise BadResponse("Unable to find status link for polling.")

    async def request_status(self, status_link):
        """Do a simple GET to this status link.

        This method re-inject 'x-ms-client-request-id'.

        :rtype: azure.core.pipeline.PipelineResponse
        """
        request = self._client.get(status_link)
        # ARM requires to re-inject 'x-ms-client-request-id' while polling
        if 'request_id' not in self._operation_config:
            self._operation_config['request_id'] = self._operation.initial_response.http_response.request.headers['x-ms-client-request-id']
        return (await self._client._pipeline.run(request, stream=False, **self._operation_config))
