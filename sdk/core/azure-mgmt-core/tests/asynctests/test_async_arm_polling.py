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
import types
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from requests import Request, Response

from msrest import Deserializer

from azure.core.polling import async_poller
from azure.core.exceptions import DecodeError, HttpResponseError
from azure.core import AsyncPipelineClient
from azure.core.pipeline import PipelineResponse, AsyncPipeline
from azure.core.pipeline.transport import AsyncioRequestsTransportResponse, AsyncHttpTransport

from azure.core.polling.base_polling import (
    LongRunningOperation,
    BadStatus,
    LocationPolling
)
from azure.mgmt.core.polling.async_arm_polling import (
    AsyncARMPolling,
)


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
async def mock_run(client_self, request, **kwargs):
    return TestArmPolling.mock_update(request.url)
CLIENT._pipeline.run = types.MethodType(mock_run, CLIENT)


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


@pytest.mark.asyncio
async def test_post(async_pipeline_client_builder, deserialization_cb):

        # Test POST LRO with both Location and Azure-AsyncOperation

        # The initial response contains both Location and Azure-AsyncOperation, a 202 and no Body
        initial_response = TestArmPolling.mock_send(
            'POST',
            202,
            {
                'location': 'http://example.org/location',
                'azure-asyncoperation': 'http://example.org/async_monitor',
            },
            ''
        )

        async def send(request, **kwargs):
            assert request.method == 'GET'

            if request.url == 'http://example.org/location':
                return TestArmPolling.mock_send(
                    'GET',
                    200,
                    body={'location_result': True}
                ).http_response
            elif request.url == 'http://example.org/async_monitor':
                return TestArmPolling.mock_send(
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
            AsyncARMPolling(0, lro_options={"final-state-via": "location"}))
        result = await poll
        assert result['location_result'] == True

        # Test 2, LRO options with Azure-AsyncOperation final state
        poll = async_poller(
            client,
            initial_response,
            deserialization_cb,
            AsyncARMPolling(0, lro_options={"final-state-via": "azure-async-operation"}))
        result = await poll
        assert result['status'] == 'Succeeded'

        # Test 3, "do the right thing" and use Location by default
        poll = async_poller(
            client,
            initial_response,
            deserialization_cb,
            AsyncARMPolling(0))
        result = await poll
        assert result['location_result'] == True

        # Test 4, location has no body

        async def send(request, **kwargs):
            assert request.method == 'GET'

            if request.url == 'http://example.org/location':
                return TestArmPolling.mock_send(
                    'GET',
                    200,
                    body=None
                ).http_response
            elif request.url == 'http://example.org/async_monitor':
                return TestArmPolling.mock_send(
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
            AsyncARMPolling(0, lro_options={"final-state-via": "location"}))
        result = await poll
        assert result is None


class TestArmPolling(object):

    convert = re.compile('([a-z0-9])([A-Z])')

    @staticmethod
    def mock_send(method, status, headers=None, body=RESPONSE_BODY):
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

        request = CLIENT._request(
            response.request.method,
            response.request.url,
            None,  # params
            response.request.headers,
            body,
            None,  # form_content
            None  # stream_content
        )

        return PipelineResponse(
            request,
            AsyncioRequestsTransportResponse(
                request,
                response,
            ),
            None  # context
        )

    @staticmethod
    def mock_update(url, headers=None):
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

        request = CLIENT._request(
            response.request.method,
            response.request.url,
            None,  # params
            {}, # request has no headers
            None, # Request has no body
            None,  # form_content
            None  # stream_content
        )

        return PipelineResponse(
            request,
            AsyncioRequestsTransportResponse(
                request,
                response,
            ),
            None  # context
        )

    @staticmethod
    def mock_outputs(pipeline_response):
        response = pipeline_response.http_response
        try:
            body = json.loads(response.text())
        except ValueError:
            raise DecodeError("Impossible to deserialize")

        body = {TestArmPolling.convert.sub(r'\1_\2', k).lower(): v
                for k, v in body.items()}
        properties = body.setdefault('properties', {})
        if 'name' in body:
            properties['name'] = body['name']
        if properties:
            properties = {TestArmPolling.convert.sub(r'\1_\2', k).lower(): v
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
async def test_long_running_put():
    #TODO: Test custom header field

    # Test throw on non LRO related status code
    response = TestArmPolling.mock_send('PUT', 1000, {})
    with pytest.raises(HttpResponseError):
        await async_poller(CLIENT, response,
            TestArmPolling.mock_outputs,
            AsyncARMPolling(0))

    # Test with no polling necessary
    response_body = {
        'properties':{'provisioningState': 'Succeeded'},
        'name': TEST_NAME
    }
    response = TestArmPolling.mock_send(
        'PUT', 201,
        {}, response_body
    )
    def no_update_allowed(url, headers=None):
        raise ValueError("Should not try to update")
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method
    )
    assert poll.name == TEST_NAME
    assert not hasattr(polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

    # Test polling from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'PUT', 201,
        {'azure-asyncoperation': ASYNC_URL})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert not hasattr(polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

    # Test polling location header
    response = TestArmPolling.mock_send(
        'PUT', 201,
        {'location': LOCATION_URL})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

    # Test polling initial payload invalid (SQLDb)
    response_body = {}  # Empty will raise
    response = TestArmPolling.mock_send(
        'PUT', 201,
        {'location': LOCATION_URL}, response_body)
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

    # Test fail to poll from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'PUT', 201,
        {'azure-asyncoperation': ERROR})
    with pytest.raises(BadEndpointError):
        poll = await async_poller(CLIENT, response,
            TestArmPolling.mock_outputs,
            AsyncARMPolling(0))

    # Test fail to poll from location header
    response = TestArmPolling.mock_send(
        'PUT', 201,
        {'location': ERROR})
    with pytest.raises(BadEndpointError):
        poll = await async_poller(CLIENT, response,
            TestArmPolling.mock_outputs,
            AsyncARMPolling(0))

@pytest.mark.asyncio
async def test_long_running_patch():

    # Test polling from location header
    response = TestArmPolling.mock_send(
        'PATCH', 202,
        {'location': LOCATION_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

    # Test polling from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'PATCH', 202,
        {'azure-asyncoperation': ASYNC_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert not hasattr(polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

    # Test polling from location header
    response = TestArmPolling.mock_send(
        'PATCH', 200,
        {'location': LOCATION_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

    # Test polling from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'PATCH', 200,
        {'azure-asyncoperation': ASYNC_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert not hasattr(polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

    # Test fail to poll from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'PATCH', 202,
        {'azure-asyncoperation': ERROR})
    with pytest.raises(BadEndpointError):
        poll = await async_poller(CLIENT, response,
            TestArmPolling.mock_outputs,
            AsyncARMPolling(0))

    # Test fail to poll from location header
    response = TestArmPolling.mock_send(
        'PATCH', 202,
        {'location': ERROR})
    with pytest.raises(BadEndpointError):
        poll = await async_poller(CLIENT, response,
            TestArmPolling.mock_outputs,
            AsyncARMPolling(0))

@pytest.mark.asyncio
async def test_long_running_delete():
    # Test polling from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'DELETE', 202,
        {'azure-asyncoperation': ASYNC_URL},
        body=""
    )
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_deserialization_no_body,
        polling_method)
    assert poll is None
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollAsyncOpHeader is None

@pytest.mark.asyncio
async def test_long_running_post():

    # Test polling from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'POST', 201,
        {'azure-asyncoperation': ASYNC_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_deserialization_no_body,
        polling_method)
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollAsyncOpHeader is None

    # Test polling from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'POST', 202,
        {'azure-asyncoperation': ASYNC_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_deserialization_no_body,
        polling_method)
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollAsyncOpHeader is None

    # Test polling from location header
    response = TestArmPolling.mock_send(
        'POST', 202,
        {'location': LOCATION_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

    # Test fail to poll from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'POST', 202,
        {'azure-asyncoperation': ERROR})
    with pytest.raises(BadEndpointError):
        await async_poller(CLIENT, response,
            TestArmPolling.mock_outputs,
            AsyncARMPolling(0))

    # Test fail to poll from location header
    response = TestArmPolling.mock_send(
        'POST', 202,
        {'location': ERROR})
    with pytest.raises(BadEndpointError):
        await async_poller(CLIENT, response,
            TestArmPolling.mock_outputs,
            AsyncARMPolling(0))

@pytest.mark.asyncio
async def test_long_running_negative():
    global LOCATION_BODY
    global POLLING_STATUS

    # Test LRO PUT throws for invalid json
    LOCATION_BODY = '{'
    response = TestArmPolling.mock_send(
        'POST', 202,
        {'location': LOCATION_URL})
    poll = async_poller(
        CLIENT,
        response,
        TestArmPolling.mock_outputs,
        AsyncARMPolling(0)
    )
    with pytest.raises(DecodeError):
        await poll

    LOCATION_BODY = '{\'"}'
    response = TestArmPolling.mock_send(
        'POST', 202,
        {'location': LOCATION_URL})
    poll = async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        AsyncARMPolling(0))
    with pytest.raises(DecodeError):
        await poll

    LOCATION_BODY = '{'
    POLLING_STATUS = 203
    response = TestArmPolling.mock_send(
        'POST', 202,
        {'location': LOCATION_URL})
    poll = async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        AsyncARMPolling(0))
    with pytest.raises(HttpResponseError) as error: # TODO: Node.js raises on deserialization
        await poll
    assert error.value.continuation_token == base64.b64encode(pickle.dumps(response)).decode('ascii')

    LOCATION_BODY = json.dumps({ 'name': TEST_NAME })
    POLLING_STATUS = 200

def test_polling_with_path_format_arguments():
    method = AsyncARMPolling(
        timeout=0,
        path_format_arguments={"host": "host:3000", "accountName": "local"}
    )
    client = AsyncPipelineClient(base_url="http://{accountName}{host}")

    method._operation = LocationPolling()
    method._operation._location_url = "/results/1"
    method._client = client
    assert "http://localhost:3000/results/1" == method._client.format_url(method._operation.get_polling_url(), **method._path_format_arguments)