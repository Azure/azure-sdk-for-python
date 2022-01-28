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
import base64
import json
import pickle
import re
from utils import HTTP_REQUESTS
from azure.core.pipeline._tools import is_rest
import types
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from requests import Request, Response

from msrest import Deserializer

from azure.core.polling import async_poller, AsyncLROPoller
from azure.core.exceptions import DecodeError, HttpResponseError
from azure.core import AsyncPipelineClient
from azure.core.pipeline import PipelineResponse, AsyncPipeline, PipelineContext
from azure.core.pipeline.transport import AsyncioRequestsTransportResponse, AsyncHttpTransport

from azure.core.polling.async_base_polling import (
    AsyncLROBasePolling,
)
from utils import ASYNCIO_REQUESTS_TRANSPORT_RESPONSES, request_and_responses_product, create_transport_response
from rest_client_async import AsyncTestRestClient

class SimpleResource:
    """An implementation of Python 3 SimpleNamespace.
    Used to deserialize resource objects from response bodies where
    no particular object type has been specified.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class BadEndpointError(Exception):
    pass

TEST_NAME = 'foo'
RESPONSE_BODY = {'properties':{'provisioningState': 'InProgress'}}
ASYNC_BODY = json.dumps({ 'status': 'Succeeded' })
ASYNC_URL = 'http://dummyurlFromAzureAsyncOPHeader_Return200'
LOCATION_BODY = json.dumps({ 'name': TEST_NAME })
LOCATION_URL = 'http://dummyurlurlFromLocationHeader_Return200'
RESOURCE_BODY = json.dumps({ 'name': TEST_NAME })
RESOURCE_URL = 'http://subscriptions/sub1/resourcegroups/g1/resourcetype1/resource1'
ERROR = 'http://dummyurl_ReturnError'
POLLING_STATUS = 200

CLIENT = AsyncPipelineClient("http://example.org")
CLIENT.http_request_type = None
CLIENT.http_response_type = None
async def mock_run(client_self, request, **kwargs):
    return TestBasePolling.mock_update(client_self.http_request_type, client_self.http_response_type, request.url)
CLIENT._pipeline.run = types.MethodType(mock_run, CLIENT)


@pytest.fixture
def client():
    # The poller itself don't use it, so we don't need something functionnal
    return AsyncPipelineClient("https://baseurl")


@pytest.fixture
def async_pipeline_client_builder():
    """Build a client that use the "send" callback as final transport layer

    send will receive "request" and kwargs as any transport layer
    """
    def create_client(send_cb):
        class TestHttpTransport(AsyncHttpTransport):
            async def open(self): pass
            async def close(self): pass
            async def __aexit__(self, *args, **kwargs): pass

            async def send(self, request, **kwargs):
                return await send_cb(request, **kwargs)

        return AsyncPipelineClient(
            'http://example.org/',
            pipeline=AsyncPipeline(
                transport=TestHttpTransport()
            )
        )
    return create_client


@pytest.fixture
def deserialization_cb():
    def cb(pipeline_response):
        return json.loads(pipeline_response.http_response.text())
    return cb


@pytest.fixture
def polling_response():
    polling = AsyncLROBasePolling()
    headers = {}

    response = Response()
    response.headers = headers
    response.status_code = 200

    polling._pipeline_response = PipelineResponse(
        None,
        AsyncioRequestsTransportResponse(
            None,
            response,
        ),
        PipelineContext(None)
    )
    polling._initial_response = polling._pipeline_response
    return polling, headers


def test_base_polling_continuation_token(client, polling_response):
    polling, _ = polling_response

    continuation_token = polling.get_continuation_token()
    assert isinstance(continuation_token, str)

    polling_args = AsyncLROBasePolling.from_continuation_token(
        continuation_token,
        deserialization_callback="deserialization_callback",
        client=client,
    )
    new_polling = AsyncLROBasePolling()
    new_polling.initialize(*polling_args)


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(ASYNCIO_REQUESTS_TRANSPORT_RESPONSES))
async def test_post(async_pipeline_client_builder, deserialization_cb, http_request, http_response):

        # Test POST LRO with both Location and Operation-Location

        # The initial response contains both Location and Operation-Location, a 202 and no Body
        initial_response = TestBasePolling.mock_send(
            http_request,
            http_response,
            'POST',
            202,
            {
                'location': 'http://example.org/location',
                'operation-location': 'http://example.org/async_monitor',
            },
            ''
        )

        async def send(request, **kwargs):
            assert request.method == 'GET'

            if request.url == 'http://example.org/location':
                return TestBasePolling.mock_send(
                    http_request,
                    http_response,
                    'GET',
                    200,
                    body={'location_result': True}
                ).http_response
            elif request.url == 'http://example.org/async_monitor':
                return TestBasePolling.mock_send(
                    http_request,
                    http_response,
                    'GET',
                    200,
                    body={'status': 'Succeeded'}
                ).http_response
            else:
                pytest.fail("No other query allowed")

        client = async_pipeline_client_builder(send)

        # LRO options with Location final state
        poll = async_poller(
            client,
            initial_response,
            deserialization_cb,
            AsyncLROBasePolling(0))
        result = await poll
        assert result['location_result'] == True

        # Location has no body

        async def send(request, **kwargs):
            assert request.method == 'GET'

            if request.url == 'http://example.org/location':
                return TestBasePolling.mock_send(
                    http_request,
                    http_response,
                    'GET',
                    200,
                    body=None
                ).http_response
            elif request.url == 'http://example.org/async_monitor':
                return TestBasePolling.mock_send(
                    http_request,
                    http_response,
                    'GET',
                    200,
                    body={'status': 'Succeeded'}
                ).http_response
            else:
                pytest.fail("No other query allowed")

        client = async_pipeline_client_builder(send)

        poll = async_poller(
            client,
            initial_response,
            deserialization_cb,
            AsyncLROBasePolling(0))
        result = await poll
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(ASYNCIO_REQUESTS_TRANSPORT_RESPONSES))
async def test_post_resource_location(async_pipeline_client_builder, deserialization_cb, http_request, http_response):

        # ResourceLocation

        # The initial response contains both Location and Operation-Location, a 202 and no Body
        initial_response = TestBasePolling.mock_send(
            http_request,
            http_response,
            'POST',
            202,
            {
                'operation-location': 'http://example.org/async_monitor',
            },
            ''
        )

        async def send(request, **kwargs):
            assert request.method == 'GET'

            if request.url == 'http://example.org/resource_location':
                return TestBasePolling.mock_send(
                    http_request,
                    http_response,
                    'GET',
                    200,
                    body={'location_result': True}
                ).http_response
            elif request.url == 'http://example.org/async_monitor':
                return TestBasePolling.mock_send(
                    http_request,
                    http_response,
                    'GET',
                    200,
                    body={'status': 'Succeeded', 'resourceLocation': 'http://example.org/resource_location'}
                ).http_response
            else:
                pytest.fail("No other query allowed")

        client = async_pipeline_client_builder(send)

        poll = async_poller(
            client,
            initial_response,
            deserialization_cb,
            AsyncLROBasePolling(0))
        result = await poll
        assert result['location_result'] == True

class TestBasePolling(object):

    convert = re.compile('([a-z0-9])([A-Z])')

    @staticmethod
    def mock_send(http_request, http_response, method, status, headers=None, body=RESPONSE_BODY):
        if headers is None:
            headers = {}
        response = Response()
        response._content_consumed = True
        response._content = json.dumps(body).encode('ascii') if body is not None else None
        response.request = Request()
        response.request.method = method
        response.request.url = RESOURCE_URL
        response.request.headers = {
            'x-ms-client-request-id': '67f4dd4e-6262-45e1-8bed-5c45cf23b6d9'
        }
        response.status_code = status
        response.headers = headers
        response.headers.update({"content-type": "application/json; charset=utf8"})
        response.reason = "OK"

        if is_rest(http_request):
            request = http_request(
                response.request.method,
                response.request.url,
                headers=response.request.headers,
                content=body,
            )
        else:
            request = CLIENT._request(
                response.request.method,
                response.request.url,
                None,  # params
                response.request.headers,
                body,
                None,  # form_content
                None  # stream_content
            )
        response = create_transport_response(http_response, request, response)
        if is_rest(http_response):
            response.body()
        return PipelineResponse(
            request,
            response,
            None  # context
        )

    @staticmethod
    def mock_update(http_request, http_response, url, headers=None):
        response = Response()
        response._content_consumed = True
        response.request = mock.create_autospec(Request)
        response.request.method = 'GET'
        response.headers = headers or {}
        response.headers.update({"content-type": "application/json; charset=utf8"})
        response.reason = "OK"

        if url == ASYNC_URL:
            response.request.url = url
            response.status_code = POLLING_STATUS
            response._content = ASYNC_BODY.encode('ascii')
            response.randomFieldFromPollAsyncOpHeader = None

        elif url == LOCATION_URL:
            response.request.url = url
            response.status_code = POLLING_STATUS
            response._content = LOCATION_BODY.encode('ascii')
            response.randomFieldFromPollLocationHeader = None

        elif url == ERROR:
            raise BadEndpointError("boom")

        elif url == RESOURCE_URL:
            response.request.url = url
            response.status_code = POLLING_STATUS
            response._content = RESOURCE_BODY.encode('ascii')

        else:
            raise Exception('URL does not match')

        request = http_request(
            response.request.method,
            response.request.url,
        )

        response = create_transport_response(http_response, request, response)
        if is_rest(http_response):
            response.body()

        return PipelineResponse(
            request,
            response,
            None  # context
        )

    @staticmethod
    def mock_outputs(pipeline_response):
        response = pipeline_response.http_response
        try:
            body = json.loads(response.text())
        except ValueError:
            raise DecodeError("Impossible to deserialize")

        body = {TestBasePolling.convert.sub(r'\1_\2', k).lower(): v
                for k, v in body.items()}
        properties = body.setdefault('properties', {})
        if 'name' in body:
            properties['name'] = body['name']
        if properties:
            properties = {TestBasePolling.convert.sub(r'\1_\2', k).lower(): v
                          for k, v in properties.items()}
            del body['properties']
            body.update(properties)
            resource = SimpleResource(**body)
        else:
            raise DecodeError("Impossible to deserialize")
            resource = SimpleResource(**body)
        return resource

    @staticmethod
    def mock_deserialization_no_body(pipeline_response):
        """Use this mock when you don't expect a return (last body irrelevant)
        """
        return None

@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(ASYNCIO_REQUESTS_TRANSPORT_RESPONSES))
async def test_long_running_put(http_request, http_response):
    #TODO: Test custom header field
    CLIENT.http_request_type = http_request
    CLIENT.http_response_type = http_response
    # Test throw on non LRO related status code
    response = TestBasePolling.mock_send(
        http_request, http_response, 'PUT', 1000, {}
    )
    with pytest.raises(HttpResponseError):
        await async_poller(CLIENT, response,
            TestBasePolling.mock_outputs,
            AsyncLROBasePolling(0))

    # Test with no polling necessary
    response_body = {
        'properties':{'provisioningState': 'Succeeded'},
        'name': TEST_NAME
    }
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PUT', 201,
        {}, response_body
    )
    def no_update_allowed(url, headers=None):
        raise ValueError("Should not try to update")
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        polling_method
    )
    assert poll.name == TEST_NAME
    assert not hasattr(polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

    # Test polling from operation-location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PUT', 201,
        {'operation-location': ASYNC_URL})
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert not hasattr(polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

    # Test polling location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PUT', 201,
        {'location': LOCATION_URL})
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

    # Test polling initial payload invalid (SQLDb)
    response_body = {}  # Empty will raise
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PUT', 201,
        {'location': LOCATION_URL}, response_body)
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

    # Test fail to poll from operation-location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PUT', 201,
        {'operation-location': ERROR})
    with pytest.raises(BadEndpointError):
        poll = await async_poller(CLIENT, response,
            TestBasePolling.mock_outputs,
            AsyncLROBasePolling(0))

    # Test fail to poll from location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PUT', 201,
        {'location': ERROR})
    with pytest.raises(BadEndpointError):
        poll = await async_poller(CLIENT, response,
            TestBasePolling.mock_outputs,
            AsyncLROBasePolling(0))

@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(ASYNCIO_REQUESTS_TRANSPORT_RESPONSES))
async def test_long_running_patch(http_request, http_response):
    CLIENT.http_request_type = http_request
    CLIENT.http_response_type = http_response
    # Test polling from location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PATCH', 202,
        {'location': LOCATION_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

    # Test polling from operation-location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PATCH', 202,
        {'operation-location': ASYNC_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert not hasattr(polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

    # Test polling from location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PATCH', 200,
        {'location': LOCATION_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

    # Test polling from operation-location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PATCH', 200,
        {'operation-location': ASYNC_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert not hasattr(polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

    # Test fail to poll from operation-location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PATCH', 202,
        {'operation-location': ERROR})
    with pytest.raises(BadEndpointError):
        poll = await async_poller(CLIENT, response,
            TestBasePolling.mock_outputs,
            AsyncLROBasePolling(0))

    # Test fail to poll from location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'PATCH', 202,
        {'location': ERROR})
    with pytest.raises(BadEndpointError):
        poll = await async_poller(CLIENT, response,
            TestBasePolling.mock_outputs,
            AsyncLROBasePolling(0))

@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(ASYNCIO_REQUESTS_TRANSPORT_RESPONSES))
async def test_long_running_delete(http_request, http_response):
    # Test polling from operation-location header
    CLIENT.http_request_type = http_request
    CLIENT.http_response_type = http_response
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'DELETE', 202,
        {'operation-location': ASYNC_URL},
        body=""
    )
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_deserialization_no_body,
        polling_method)
    assert poll is None
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollAsyncOpHeader is None

@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(ASYNCIO_REQUESTS_TRANSPORT_RESPONSES))
async def test_long_running_post(http_request, http_response):
    CLIENT.http_request_type = http_request
    CLIENT.http_response_type = http_response
    # Test polling from operation-location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'POST', 201,
        {'operation-location': ASYNC_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_deserialization_no_body,
        polling_method)
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollAsyncOpHeader is None

    # Test polling from operation-location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'POST', 202,
        {'operation-location': ASYNC_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_deserialization_no_body,
        polling_method)
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollAsyncOpHeader is None

    # Test polling from location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'POST', 202,
        {'location': LOCATION_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncLROBasePolling(0)
    poll = await async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

    # Test fail to poll from operation-location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'POST', 202,
        {'operation-location': ERROR})
    with pytest.raises(BadEndpointError):
        await async_poller(CLIENT, response,
            TestBasePolling.mock_outputs,
            AsyncLROBasePolling(0))

    # Test fail to poll from location header
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'POST', 202,
        {'location': ERROR})
    with pytest.raises(BadEndpointError):
        await async_poller(CLIENT, response,
            TestBasePolling.mock_outputs,
            AsyncLROBasePolling(0))

@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(ASYNCIO_REQUESTS_TRANSPORT_RESPONSES))
async def test_long_running_negative(http_request, http_response):
    global LOCATION_BODY
    global POLLING_STATUS
    CLIENT.http_request_type = http_request
    CLIENT.http_response_type = http_response
    # Test LRO PUT throws for invalid json
    LOCATION_BODY = '{'
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'POST', 202,
        {'location': LOCATION_URL})
    poll = async_poller(
        CLIENT,
        response,
        TestBasePolling.mock_outputs,
        AsyncLROBasePolling(0)
    )
    with pytest.raises(DecodeError):
        await poll

    LOCATION_BODY = '{\'"}'
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'POST', 202,
        {'location': LOCATION_URL})
    poll = async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        AsyncLROBasePolling(0))
    with pytest.raises(DecodeError):
        await poll

    LOCATION_BODY = '{'
    POLLING_STATUS = 203
    response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'POST', 202,
        {'location': LOCATION_URL})
    poll = async_poller(CLIENT, response,
        TestBasePolling.mock_outputs,
        AsyncLROBasePolling(0))
    with pytest.raises(HttpResponseError) as error: # TODO: Node.js raises on deserialization
        await poll
    assert error.value.continuation_token == base64.b64encode(pickle.dumps(response)).decode('ascii')

    LOCATION_BODY = json.dumps({ 'name': TEST_NAME })
    POLLING_STATUS = 200

@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(ASYNCIO_REQUESTS_TRANSPORT_RESPONSES))
async def test_post_final_state_via(async_pipeline_client_builder, deserialization_cb, http_request, http_response):
    # Test POST LRO with both Location and Operation-Location
    CLIENT.http_request_type = http_request
    CLIENT.http_response_type = http_response
    # The initial response contains both Location and Operation-Location, a 202 and no Body
    initial_response = TestBasePolling.mock_send(
        http_request,
        http_response,
        'POST',
        202,
        {
            'location': 'http://example.org/location',
            'operation-location': 'http://example.org/async_monitor',
        },
        ''
    )

    async def send(request, **kwargs):
        assert request.method == 'GET'

        if request.url == 'http://example.org/location':
            return TestBasePolling.mock_send(
                http_request,
                http_response,
                'GET',
                200,
                body={'location_result': True}
            ).http_response
        elif request.url == 'http://example.org/async_monitor':
            return TestBasePolling.mock_send(
                http_request,
                http_response,
                'GET',
                200,
                body={'status': 'Succeeded'}
            ).http_response
        else:
            pytest.fail("No other query allowed")

    client = async_pipeline_client_builder(send)

    # Test 1, LRO options with Location final state
    poll = async_poller(
        client,
        initial_response,
        deserialization_cb,
        AsyncLROBasePolling(0, lro_options={"final-state-via": "location"}))
    result = await poll
    assert result['location_result'] == True

    # Test 2, LRO options with Operation-Location final state
    poll = async_poller(
        client,
        initial_response,
        deserialization_cb,
        AsyncLROBasePolling(0, lro_options={"final-state-via": "operation-location"}))
    result = await poll
    assert result['status'] == 'Succeeded'

    # Test 3, "do the right thing" and use Location by default
    poll = async_poller(
        client,
        initial_response,
        deserialization_cb,
        AsyncLROBasePolling(0))
    result = await poll
    assert result['location_result'] == True

    # Test 4, location has no body

    async def send(request, **kwargs):
        assert request.method == 'GET'

        if request.url == 'http://example.org/location':
            return TestBasePolling.mock_send(
                http_request,
                http_response,
                'GET',
                200,
                body=None
            ).http_response
        elif request.url == 'http://example.org/async_monitor':
            return TestBasePolling.mock_send(
                http_request,
                http_response,
                'GET',
                200,
                body={'status': 'Succeeded'}
            ).http_response
        else:
            pytest.fail("No other query allowed")

    client = async_pipeline_client_builder(send)

    poll = async_poller(
        client,
        initial_response,
        deserialization_cb,
        AsyncLROBasePolling(0, lro_options={"final-state-via": "location"}))
    result = await poll
    assert result is None

@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_final_get_via_location(port, http_request, deserialization_cb):
    client = AsyncTestRestClient(port)
    request = http_request(
        "PUT",
        "http://localhost:{}/polling/polling-with-options".format(port),
    )
    request.set_json_body({"hello": "world!"})
    initial_response = await client._client._pipeline.run(request)
    poller = AsyncLROPoller(
        client._client,
        initial_response,
        deserialization_cb,
        AsyncLROBasePolling(0, lro_options={"final-state-via": "location"}),
    )
    result = await poller.result()
    assert result == {"returnedFrom": "locationHeaderUrl"}
