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
import abc

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore


class PagingAlgorithmABC(ABC):
    """Provides default logic for getting next links
    """

    @abc.abstractmethod
    def get_next_link(self):
        # type: () -> str
        """Return the next link
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def set_initial_state(self, initial_pipeline_response):
        # type: (PipelineResponseType) -> str
        """Set initial state after first call.

        :param azure.core.pipeline.PipelineResponse response: initial REST call response.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def can_page(self):
        # type: (PipelineResponseType) -> str
        """Can this paging operation be used in this case.
        """
        raise NotImplementedError()

    @abc.abstractproperty
    def operation_config(self):
        # type () -> Any
        """Any additional configurations specific to your paging operation
        """
        raise NotImplementedError()


class PagingAlgorithmDefault(PagingAlgorithmABC):
    def __init__(self, **kwargs):
        self._initial_request = None
        self._next_link = None

    def get_next_link(self):
        return self._next_link

    def set_initial_state(self, initial_pipeline_response):
        response = initial_pipeline_response.http_response
        self._initial_request = response.request

    def update_state(self, next_link):
        self._next_link = next_link

    def can_page(self, **kwargss):
        return True

    @property
    def operation_config(self):
        # we add headers, query, and body parameters here

        query_params = self._initial_request.query
        headers = self._initial_request.headers
        body = self._initial_request.body

        return {
            'params': query_params,
            'headers': headers,
            'body': body
        }


class PagingAlgorithmIfSeparateNextOperation(PagingAlgorithmABC):
    def __init__(self, **kwargs):
        self._next_link_operation_url = kwargs.pop("next_link_operation_url", None)
        self._initial_request = response.request
        self._operation_config = kwargs

    def get_next_link(self):
        return self._next_link_operation_url

    def set_initial_state(self, initial_pipeline_response):
        response = initial_pipeline_response.http_response
        self._initial_request = response.request

    def update_state(self, next_link):
        # Here we just return the next operation URL defined in the next operation swagger
        # If there is a path form argument for next link in the next operation URL, that is
        # handled by the page iterator
        pass

    def can_page(self, **kwargs):
        return bool(kwargs.get("next_link_operation_url", None))

    @property
    def operation_config(self):
        # we add headers, query, and body parameters here

        query_params = self._operation_config.get("next_operation_query_params", None) or self._initial_request.query
        headers = self._operation_config.get("next_operation_header_params", None) or self._initial_request.headers
        body = self._operation_config.get("next_operation_body_params", None) or self._initial_request.body

        return {
            'params': query_params,
            'headers': headers,
            'body': body
        }

class PagingAlgorithmForTokenPaging(PagingAlgorithmABC):

    def can_page(self, **kwargs):
        return

    @property
    def operation_config(self):
        # we add headers, query, and body parameters here

        query_params = self._operation_config.get("next_operation_query_params", None) or self._initial_request.query
        headers = self._operation_config.get("next_operation_header_params", None) or self._initial_request.headers
        body = self._operation_config.get("next_operation_body_params", None) or self._initial_request.body

        return {
            'params': query_params,
            'headers': headers,
            'body': body
        }
