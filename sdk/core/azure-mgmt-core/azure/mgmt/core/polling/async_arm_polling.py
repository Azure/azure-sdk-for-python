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
import asyncio

from ..azure_exceptions import CloudError
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
        except BadStatus:
            self._operation.status = 'Failed'
            raise CloudError(self._response)

        except BadResponse as err:
            self._operation.status = 'Failed'
            raise CloudError(self._response, str(err))

        except OperationFailed:
            raise CloudError(self._response)

    async def _poll(self):
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :param callable update_cmd: The function to call to retrieve the
         latest status of the long running operation.
        :raises: OperationFailed if operation status 'Failed' or 'Cancelled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        while not self.finished():
            await self._delay()
            await self.update_status()

        if failed(self._operation.status):
            raise OperationFailed("Operation failed or cancelled")

        elif self._operation.should_do_final_get():
            if self._operation.method == 'POST' and self._operation.location_url:
                final_get_url = self._operation.location_url
            else:
                final_get_url = self._operation.initial_response.request.url
            self._response = await self.request_status(final_get_url)
            self._operation.get_status_from_resource(self._response)

    async def _delay(self):
        """Check for a 'retry-after' header to set timeout,
        otherwise use configured timeout.
        """
        if self._response is None:
            await asyncio.sleep(0)
        if self._response.headers.get('retry-after'):
            await asyncio.sleep(int(self._response.headers['retry-after']))
        else:
            await asyncio.sleep(self._timeout)

    async def update_status(self):
        """Update the current status of the LRO.
        """
        if self._operation.async_url:
            self._response = await self.request_status(self._operation.async_url)
            self._operation.set_async_url_if_present(self._response)
            self._operation.get_status_from_async(self._response)
        elif self._operation.location_url:
            self._response = await self.request_status(self._operation.location_url)
            self._operation.set_async_url_if_present(self._response)
            self._operation.get_status_from_location(self._response)
        elif self._operation.method == "PUT":
            initial_url = self._operation.initial_response.request.url
            self._response = await self.request_status(initial_url)
            self._operation.set_async_url_if_present(self._response)
            self._operation.get_status_from_resource(self._response)
        else:
            raise BadResponse("Unable to find status link for polling.")

    async def request_status(self, status_link):
        """Do a simple GET to this status link.

        This method re-inject 'x-ms-client-request-id'.

        :rtype: requests.Response
        """
        # ARM requires to re-inject 'x-ms-client-request-id' while polling
        header_parameters = {
            'x-ms-client-request-id': self._operation.initial_response.request.headers['x-ms-client-request-id']
        }
        request = self._client.get(status_link, headers=header_parameters)
        return await self._client.async_send(request, stream=False, **self._operation_config)
