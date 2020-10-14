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

try:
    # python2
    from urlparse import urlparse  # type: ignore
except ImportError:
    # python3
    from urllib.parse import urlparse


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc: # if not a full url
        return value[0] == '/'  # if it's a partial url, still return True
    return True


class PagingAlgorithmABC(ABC):
    """Provides default logic for getting next links and prepares the parametrers
    needed for the next call
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

    @abc.abstractmethod
    def get_parameters(self):
        # type: () -> str
        """Return the next link
        """
        raise NotImplementedError()


class PagingAlgorithm(PagingAlgorithmABC):
    """Most stripped paging algorithm.

    Gets all of the information from the initial request.
    """
    def __init__(self, **kwargs):
        self._initial_request = None

    def get_next_link(self):
        return self._initial_request.url

    def set_initial_state(self, initial_pipeline_response):
        response = initial_pipeline_response.http_response
        self._initial_request = response.request

    def update_state(self, continuation_token):
        pass

    def can_page(self, continuation_token, **kwargs):
        return not _is_url(continuation_token)

    def get_parameters(self):
        query_parameters = self._initial_request.query
        header_parameters = self._initial_request.headers
        body_parameters = self._initial_request.body
        return {
            "params": query_parameters,
            "headers": header_parameters,
            "content": body_parameters
        }


class PagingAlgorithmContinuationTokenAsNextLink(PagingAlgorithmABC):
    """Most common paging algorithm

    This paging algorithm uses the continuation token as the next link to make URl calls.
    It gets the API parameters from the initial request.
    """
    def __init__(self, **kwargs):
        self._continuation_token = None
        self._initial_request = None

    def get_next_link(self):
        return self._continuation_token

    def set_initial_state(self, initial_pipeline_response):
        response = initial_pipeline_response.http_response
        self._initial_request = response.request

    def update_state(self, continuation_token):
        self._continuation_token = continuation_token

    def can_page(self, **kwargs):
        # return's True if continuation token from initial request 
        return _is_url(continuation_token)

    def get_parameters(self):
        query_parameters = self._initial_request.query
        header_parameters = self._initial_request.headers
        body_parameters = self._initial_request.body
        return {
            "params": query_parameters,
            "headers": header_parameters,
            "content": body_parameters
        }


class PagingAlgorithmIfSeparateNextOperation(PagingAlgorithmABC):
    """Paging algorithm if the next operation has a different endpoint than the inital request.

    Gets API parameters from either the next operation or the intiial request
    """
    def __init__(self, **kwargs):
        self._initial_request = None
        self._prepare_request_to_separate_next_operation = None
        self._next_request = None

    def get_next_link(self):
        return self._next_request.url

    def set_initial_state(self, initial_pipeline_response):
        response = initial_pipeline_response.http_response
        self._initial_request = response.request

    def update_state(self, continuation_token):
        self._next_request = self._prepare_request_to_separate_next_operation(continuation_token)

    def can_page(self, prepare_request_to_separate_next_operation):
        self._prepare_request_to_separate_next_operation = prepare_request_to_separate_next_operation
        return bool(request_to_separate_next_operation)

    def get_parameters(self):
        query_parameters = self._next_request.query or self._initial_request.query
        header_parameters = self._next_request.headers or self._initial_request.headers
        body_parameters =self._next_request.body or  self._initial_request.body
        return {
            "params": query_parameters,
            "headers": header_parameters,
            "content": body_parameters
        }
