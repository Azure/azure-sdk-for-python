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
    _ContinueWithNextLink,
    _ContinueWithRequestHeader,
    _ContinueWithCallback,
    PageIterator,
    ReturnType,
)
from azure.core.paging._paging_method_handler import _PagingMethodHandler
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.core.pipeline import PipelineRequest, PipelineResponse, PipelineContext
from azure.core.exceptions import HttpResponseError, AzureError

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
    initial_response = ProductResult(next_link="page2", value=['value1.0', 'value1.1'])
    def _deserialize_output(pipeline_response):
        first_call_check = (
            pipeline_response.http_request.url == "http://firstURL.com" and
            not pipeline_response.http_request.headers.get("x-ms-header", None)
        )

        if first_call_check:
            return initial_response
        return ProductResult(next_link=None, value=['value2.0', 'value2.1'])
    return _deserialize_output

@pytest.fixture
def http_request():
    http_request = HttpRequest('GET', "http://firstURL.com")
    http_request.headers['x-ms-client-request-id'] = '0'
    return http_request

@pytest.fixture
def pipeline_response(http_request):
    # not including body in response bc I can't set the content attribute of a Response
    http_response = HttpResponse(http_request, None)
    http_response.status_code = 200
    response = PipelineResponse(http_request, http_response, context=None)
    return response

def _get_custom_pipeline_response(headers=None):
    http_request = HttpRequest('GET', "http://firstURL.com")
    http_request.headers['x-ms-client-request-id'] = '0'
    http_response = HttpResponse(http_request, None)
    http_response.status_code = 200
    if headers:
        http_response.headers = headers
    return PipelineResponse(http_request, http_response, context=None)

@pytest.fixture
def paging_method_handler(pipeline_response):
    class _MyPagingMethodHandler(_PagingMethodHandler):
        def __init__(
            self,
            _paging_method,
            _deserialize_output,
            _client,
            _initial_state,
            validate_next_request=None,
            raise_on_second_call=False,
            **kwargs
        ):
            super(_MyPagingMethodHandler, self).__init__(
                _paging_method,
                _deserialize_output,
                _client,
                _initial_state,
                **kwargs
            )
            self._num_calls = 0
            self._validate_next_request = validate_next_request
            self._raise_on_second_call = raise_on_second_call

        def _make_call(self, request):
            self._num_calls += 1
            if self._num_calls > 1:
                if self._validate_next_request:
                    self._validate_next_request(request)
                if self._raise_on_second_call:
                    pipeline_response.http_response.status_code = 400

            pipeline_response.http_request = request
            return pipeline_response

        def get_next(self, continuation_token):
            response = super(_MyPagingMethodHandler, self).get_next(continuation_token)
            return response

        def extract_data(self, pipeline_response):
            return super(_MyPagingMethodHandler, self).extract_data(pipeline_response)

    return _MyPagingMethodHandler

@pytest.fixture
def page_iterator(paging_method_handler):
    class _TwoCallPageIterator(PageIterator):
        def __init__(
            self,
            get_next=None,
            extract_data=None,
            continuation_token=None,
            **kwargs
        ):
            super(_TwoCallPageIterator, self).__init__(
                get_next, extract_data, continuation_token, **kwargs
            )
            handler = paging_method_handler(**kwargs)
            self._extract_data = handler.extract_data
            self._get_next = handler.get_next

    return _TwoCallPageIterator

def _get_custom_pipeline_response(headers=None):
    http_request = HttpRequest('GET', "http://firstURL.com")
    http_request.headers['x-ms-client-request-id'] = '0'
    http_response = HttpResponse(http_request, None)
    http_response.status_code = 200
    if headers:
        http_response.headers = headers
    return PipelineResponse(http_request, http_response, context=None)


class TestPaging(object):
    def test_basic_next_link_from_request(self, client, deserialize_output, page_iterator, http_request):

        def _validate_next_request_paging_method(request):
            assert request.url == 'https://baseurl/page2'

        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=http_request,
            _paging_method=_ContinueWithNextLink(),
            _continuation_token_location="next_link",
            validate_next_request = _validate_next_request_paging_method  # arg added for testing purposes
        )

        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_basic_next_link_from_response(self, client, deserialize_output, page_iterator, pipeline_response):

        def _validate_next_request_paging_method(request):
            assert request.url == 'https://baseurl/page2'

        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=pipeline_response,
            _paging_method=_ContinueWithNextLink(),
            _continuation_token_location="next_link",
            validate_next_request = _validate_next_request_paging_method  # arg added for testing purposes
        )
        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_basic_header_from_request(self, client, deserialize_output, page_iterator, http_request):
        def _validate_header_paging_method(request):
            assert request.headers['x-ms-header'] == 'page2'

        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=http_request,
            _paging_method=_ContinueWithRequestHeader(header_name="x-ms-header"),
            _continuation_token_location="next_link",
            validate_next_request = _validate_header_paging_method  # arg added for testing purposes
        )

        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_basic_callback_from_request(self, client, deserialize_output, page_iterator, http_request):

        def _callback(continuation_token):
            request = http_request
            request.headers['x-ms-header'] = 'headerCont'
            request.url = 'http://nextLinkCont.com'
            return request

        def _validate_callback_paging_method(request):
            assert request.headers['x-ms-header'] == 'headerCont'
            assert request.url == 'http://nextLinkCont.com'

        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=http_request,
            _paging_method=_ContinueWithCallback(next_request_callback=_callback),
            _continuation_token_location="next_link",
            validate_next_request = _validate_callback_paging_method  # arg added for testing purposes
        )
        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_by_page_paging(self, client, deserialize_output, page_iterator, http_request):

        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=http_request,
            _paging_method=_ContinueWithNextLink(),
            _continuation_token_location="next_link",
        )

        pager = item_paged.by_page()
        page1 = next(pager)
        assert list(page1) == ['value1.0', 'value1.1']

        page2 = next(pager)
        assert list(page2) == ['value2.0', 'value2.1']

        with pytest.raises(StopIteration):
            next(pager)

    def test_none_value(self, client, page_iterator, http_request):
        def deserialize_output(pipeline_response):
            return ProductResult(next_link=None, value=[])

        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=http_request,
            _paging_method=_ContinueWithRequestHeader(header_name="x-ms-header"),
            _continuation_token_location="next_link",
        )

        # ProductResult(next_link=None, value=None)
        result_iterated = list(item_paged)
        assert len(result_iterated) == 0

    def test_print(self, client, deserialize_output, page_iterator, http_request):
        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=http_request,
            _paging_method=_ContinueWithRequestHeader(header_name="x-ms-header"),
            _continuation_token_location="next_link",
        )
        output = repr(item_paged)
        assert output.startswith('<iterator object azure.core.paging.ItemPaged at')

    def test_paging_continue_on_error(self, client, deserialize_output, page_iterator, http_request):
        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=http_request,
            _paging_method=_ContinueWithRequestHeader(header_name="x-ms-header"),
            _continuation_token_location="next_link",
            raise_on_second_call=True,  # arg added for testing purposes
        )

        assert next(item_paged) == 'value1.0'
        assert next(item_paged) == 'value1.1'
        with pytest.raises(HttpResponseError) as err:
            next(item_paged)
        assert err.value.continuation_token == 'page2'

    def test_next_link_in_response_headers(self, client, deserialize_output, page_iterator, pipeline_response):

        def _validate_next_request_paging_method(request):
            assert request.url == 'https://baseurl/responseToken'

        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=_get_custom_pipeline_response(headers={'x-ms-token': 'responseToken'}),
            _paging_method=_ContinueWithNextLink(),
            _continuation_token_location="x-ms-token",
            validate_next_request=_validate_next_request_paging_method,  # arg added for testing purposes
        )

        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_continuation_token_in_response_headers(self, client, deserialize_output, page_iterator, pipeline_response):

        def _validate_header_paging_method(request):
            assert request.headers['x-ms-header'] == 'responseToken'

        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=_get_custom_pipeline_response(headers={'x-ms-token': 'responseToken'}),
            _paging_method=_ContinueWithRequestHeader(header_name='x-ms-header'),
            _continuation_token_location="x-ms-token",
            validate_next_request=_validate_header_paging_method,  # arg added for testing purposes
        )
        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_token_with_metadata(self, client, page_iterator, http_request):
        def deserialize_output(pipeline_response):
            if not pipeline_response.http_request.headers.get("x-ms-header", None):
                return ProductResult(next_link="responseToken;2", value=['value1.0', 'value1.1'])
            return ProductResult(next_link=None, value=['value2.0', 'value2.1'])

        class MyPagingMethod(_ContinueWithRequestHeader):
            def __init__(self, header_name):
                super(MyPagingMethod, self).__init__(header_name=header_name)
                self._count = None

            def get_continuation_token(self, pipeline_response, deserialized, continuation_token_location=None):
                token = deserialized.next_link
                if not token:
                    return None
                split_token = token.split(";")
                self._count = int(split_token[1])
                return split_token[0]

        class PagerWithMetadata(ItemPaged[ReturnType]):
            def __init__(self, *args, **kwargs):
                super(PagerWithMetadata, self).__init__(*args, **kwargs)
                self._paging_method = kwargs.pop("_paging_method")

            def get_count(self):
                # type: () -> float
                return self._paging_method._count

        def _validate_token_paging_method(request):
            assert request.headers['x-ms-header'] == 'responseToken'

        item_paged = PagerWithMetadata(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=http_request,
            _paging_method=MyPagingMethod(header_name='x-ms-header'),
            _continuation_token_location="next_link",
            validate_next_request = _validate_token_paging_method,  # arg added for testing purposes
        )

        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)


    def test_next_link_and_continuation_token(self, client,deserialize_output, page_iterator, http_request):
        def deserialize_output(pipeline_response):
            if not pipeline_response.http_request.headers.get("x-ms-header", None):
                return ProductResult(next_link="headerToken,nextLink", value=['value1.0', 'value1.1'])
            return ProductResult(next_link=None, value=['value2.0', 'value2.1'])

        class ContinueWithRequestHeaderAndNextLink(_ContinueWithNextLink):
            def __init__(self, header_name):
                super(ContinueWithRequestHeaderAndNextLink, self).__init__()
                self._header_name = header_name

            def get_next_request(self, continuation_token, initial_request, client):
                split_token = continuation_token.split(",")
                token_to_pass_to_headers = split_token[0]
                next_link = split_token[1]
                request = super(ContinueWithRequestHeaderAndNextLink, self).get_next_request(next_link, initial_request, client=client)
                request.headers[self._header_name] = split_token[0]
                return request

        def _validate_next_link_and_header_paging_method(request):
            assert request.headers['x-ms-header'] == 'headerToken'
            assert request.url == "https://baseurl/nextLink"

        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=_get_custom_pipeline_response(headers={'x-ms-token': 'responseToken'}),
            _paging_method=ContinueWithRequestHeaderAndNextLink(header_name='x-ms-header'),
            _continuation_token_location="next_link",
            validate_next_request=_validate_next_link_and_header_paging_method,  # arg added for testing purposes
        )

        assert ['value1.0', 'value1.1', 'value2.0', 'value2.1'] == list(item_paged)

    def test_cls(self, client, deserialize_output, page_iterator, http_request):
        def cls(list_of_obj):

            return ["changedByCls"] * len(list_of_obj)

        item_paged = ItemPaged(
            _deserialize_output=deserialize_output,
            _client=client,
            page_iterator_class=page_iterator,  # have to add this arg since I'm overriding PageIterator (vast majority won't use this param)
            _initial_state=http_request,
            _paging_method=_ContinueWithNextLink(),
            _continuation_token_location="next_link",
            _cls=cls,
        )
        assert all(obj == "changedByCls" for obj in item_paged)
