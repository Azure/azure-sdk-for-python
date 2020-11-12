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

from .exceptions import (
    HttpResponseError, ClientAuthenticationError, ResourceExistsError, ResourceNotFoundError, map_error
)
from .paging import _LegacyPagingMethod
from .paging_method import PagingMethodABC, BasicPagingMethod, DifferentNextOperationPagingMethod

class AsyncPagingMethodABC(PagingMethodABC):

    # making requests

    async def get_page(self, continuation_token: str):
        """Gets next page
        """
        raise NotImplementedError("This method needs to be implemented")


class AsyncBasicPagingMethod(BasicPagingMethod):
    """This is the most common paging method. It uses the continuation token
    as the next link
    """


    async def get_page(self, continuation_token):
        if not self._did_a_call_already:
            request = self._initial_request
            self._did_a_call_already = True
        else:
            request = self.get_next_request(continuation_token)
        response = await self._client._pipeline.run(request, stream=False)

        http_response = response.http_response
        if not (200 <= http_response.status_code < 300):
            map_error(status_code=http_response.status_code, response=http_response, error_map=self._error_map)
            raise HttpResponseError(response=http_response)

        return response


class AsyncDifferentNextOperationPagingMethod(AsyncBasicPagingMethod):
    """Use this paging method if the swagger defines a different next operation
    """

    def __init__(self):
        super(AsyncDifferentNextOperationPagingMethod, self).__init__()
        self._prepare_next_request = None

    def initialize(self, client, deserialize_output, prepare_next_request, **kwargs):
        super(AsyncDifferentNextOperationPagingMethod, self).initialize(
            client, deserialize_output, **kwargs
        )
        self._prepare_next_request = prepare_next_request

    def get_next_request(self, continuation_token: str):
        """Next request partial functions will either take in the token or not
        (we're not able to pass in multiple tokens). in the generated code, we
        make sure that the token input param is the first in the list, so all we
        have to do is pass in the token to the next request partial function.

        However, next calls don't have to take the token, which is why we call
        the next request in a try-catch error.
        """
        # different next operations either take in the token or not
        # in generated code, we make sure the parameter that takes in the
        # token is the first one, so all we have to do is pass in the token to the call
        #
        try:
            return self._prepare_next_request(continuation_token)
        except TypeError:
            return self._prepare_next_request()
