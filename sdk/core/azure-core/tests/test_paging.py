#--------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#--------------------------------------------------------------------------

from azure.core import PipelineClient
from azure.core.paging import (
    ItemPaged,
    ContinueWithNextLink,
    ContinueWithRequestHeader,
    ContinueWithCallback,
    PageIterator,
)
from azure.core.paging._paging_method_handler import _PagingMethodHandler
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.core.pipeline import PipelineRequest, PipelineResponse, PipelineContext
from azure.core.exceptions import HttpResponseError

import pytest

class ProductResult(object):
    def __init__(self, next_link, value):
        self.next_link = next_link
        self.value = value

@pytest.fixture
def client():
    return PipelineClient("https://baseurl")

@pytest.fixture
def deserialize_output():
    def _deserialize_output(pipeline_response):
        return None
    return _deserialize_output

@pytest.fixture
def http_request():
    http_request = HttpRequest('GET', "http://doesNotMatter.com")
    http_request.headers['x-ms-client-request-id'] = '0'
    return http_request

@pytest.fixture
def pipeline_response(http_request):
    # not including body in response bc I can't create a Response
    http_response = HttpResponse(http_request, None)
    http_response.status_code = 200
    request = PipelineRequest(http_request, PipelineContext(None))
    response = PipelineResponse(request, http_response, request.context)
    return response

@pytest.fixture
def paging_method_handler(pipeline_response):
    class _MyPagingMethodHandler(_PagingMethodHandler):
        def __init__(
            self,
            paging_method,
            deserialize_output,
            client,
            initial_state,
            validate_next_request,
            **kwargs
        ):
            super(_MyPagingMethodHandler, self).__init__(
                paging_method,
                deserialize_output,
                client,
                initial_state,
                **kwargs
            )
            self._num_calls = 0
            self.validate_next_request = validate_next_request

        def get_next(self, continuation_token):
            self._num_calls += 1
            if not continuation_token:
                if isinstance(self._initial_state, PipelineResponse):
                    response = self._initial_state
                return pipeline_response
            else:
                request = self._paging_method.get_next_request(continuation_token, self._initial_request, self._client)
                self.validate_next_request(request)
                response = pipeline_response  # don't actually want to make network call with my dummy url
            return self._handle_response(continuation_token, response)

        def extract_data(self, pipeline_response):
            if self._num_calls == 1:
                deserialized = ProductResult(next_link="/page2", value=['value1.0', 'value1.1'])
            else:
                deserialized = ProductResult(next_link=None, value=['value2.0', 'value2.1'])
            list_of_elem = self._paging_method.get_list_elements(pipeline_response, deserialized, self._item_name)
            list_of_elem = self._paging_method.mutate_list(pipeline_response, list_of_elem, self._cls)
            continuation_token = self._paging_method.get_continuation_token(
                pipeline_response, deserialized, self._continuation_token_location
            )
            return continuation_token, list_of_elem

    return _MyPagingMethodHandler

@pytest.fixture
def page_iterator(paging_method_handler):
    class _MyPageIterator(PageIterator):
        def __init__(
            self,
            get_next=None,
            extract_data=None,
            continuation_token=None,
            paging_method=None,
            **kwargs
        ):
            super(_MyPageIterator, self).__init__(
                get_next, extract_data, continuation_token, paging_method, **kwargs
            )
            handler = paging_method_handler(paging_method, **kwargs)
            self._extract_data = handler.extract_data
            self._get_next = handler.get_next

    return _MyPageIterator

@pytest.fixture
def item_paged(client, deserialize_output, page_iterator):
    return ItemPaged(
        deserialize_output=deserialize_output,
        client=client,
        page_iterator_class=page_iterator,
    )

class TestPaging(object):
    def test_basic_next_link_from_request(self, http_request, item_paged):

        def _validate_next_request_paging_method(request):
            assert request.url == 'https://baseurl/page2'

        item_paged._kwargs.update(
            {
                "initial_state": http_request,
                "paging_method": ContinueWithNextLink(),
                "continuation_token_location": "next_link",
                "validate_next_request": _validate_next_request_paging_method,
            }
        )

        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_basic_next_link_from_response(self, pipeline_response, item_paged):

        def _validate_next_request_paging_method(request):
            assert request.url == 'https://baseurl/page2'

        item_paged._kwargs.update(
            {
                "initial_state": pipeline_response,
                "paging_method": ContinueWithNextLink(),
                "continuation_token_location": "next_link",
            }
        )
        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_basic_header_from_request(self, http_request, item_paged):
        def _validate_header_paging_method(request):
            assert request.headers['x-ms-header'] == '/page2'

        item_paged._kwargs.update(
            {
                "initial_state": http_request,
                "paging_method": ContinueWithRequestHeader(header_name="x-ms-header"),
                "continuation_token_location": "next_link",
                "validate_next_request": _validate_header_paging_method,
            }
        )
        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_basic_callback_from_request(self, http_request, item_paged):

        def _callback(continuation_token):
            request = http_request
            request.headers['x-ms-header'] = 'headerCont'
            request.url = 'http://nextLinkCont.com'
            return request

        def _validate_callback_paging_method(request):
            assert request.headers['x-ms-header'] == 'headerCont'
            assert request.url == 'http://nextLinkCont.com'

        item_paged._kwargs.update(
            {
                "initial_state": http_request,
                "paging_method": ContinueWithCallback(next_request_callback=_callback),
                "continuation_token_location": "next_link",
                "validate_next_request": _validate_callback_paging_method,
            }
        )
        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_by_page_paging(self):

        def get_next(continuation_token=None):
            """Simplify my life and return JSON and not response, but should be response.
            """
            if not continuation_token:
                return {
                    'nextLink': 'page2',
                    'value': ['value1.0', 'value1.1']
                }
            else:
                return {
                    'nextLink': None,
                    'value': ['value2.0', 'value2.1']
                }

        def extract_data(response):
            return response['nextLink'], iter(response['value'])

        pager = ItemPaged(get_next, extract_data).by_page()
        page1 = next(pager)
        assert list(page1) == ['value1.0', 'value1.1']

        page2 = next(pager)
        assert list(page2) == ['value2.0', 'value2.1']

        with pytest.raises(StopIteration):
            next(pager)

    def test_advance_paging(self):

        def get_next(continuation_token=None):
            """Simplify my life and return JSON and not response, but should be response.
            """
            if not continuation_token:
                return {
                    'nextLink': 'page2',
                    'value': ['value1.0', 'value1.1']
                }
            else:
                return {
                    'nextLink': None,
                    'value': ['value2.0', 'value2.1']
                }

        def extract_data(response):
            return response['nextLink'], iter(response['value'])

        pager = ItemPaged(get_next, extract_data)
        page1 = next(pager)
        assert page1 == 'value1.0'
        page1 = next(pager)
        assert page1 == 'value1.1'

        page2 = next(pager)
        assert page2 == 'value2.0'
        page2 = next(pager)
        assert page2 == 'value2.1'

        with pytest.raises(StopIteration):
            next(pager)

    def test_none_value(self):
        def get_next(continuation_token=None):
            return {
                'nextLink': None,
                'value': None
            }
        def extract_data(response):
            return response['nextLink'], iter(response['value'] or [])

        pager = ItemPaged(get_next, extract_data)
        result_iterated = list(pager)
        assert len(result_iterated) == 0

    def test_print(self):
        def get_next(continuation_token=None):
            return {
                'nextLink': None,
                'value': None
            }
        def extract_data(response):
            return response['nextLink'], iter(response['value'] or [])

        pager = ItemPaged(get_next, extract_data)
        output = repr(pager)
        assert output.startswith('<iterator object azure.core.paging.ItemPaged at')

    def test_paging_continue_on_error(self):
        def get_next(continuation_token=None):
            if not continuation_token:
                return {
                    'nextLink': 'foo',
                    'value': ['bar']
                }
            else:
                raise HttpResponseError()
        def extract_data(response):
            return response['nextLink'], iter(response['value'] or [])

        pager = ItemPaged(get_next, extract_data)
        assert next(pager) == 'bar'
        with pytest.raises(HttpResponseError) as err:
            next(pager)
        assert err.value.continuation_token == 'foo'
