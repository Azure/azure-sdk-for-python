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

from azure.core.polling import LROPoller
from azure.core.exceptions import DecodeError, HttpResponseError
from azure.core import PipelineClient
from azure.core.pipeline import PipelineResponse, Pipeline
from azure.core.pipeline.transport import RequestsTransportResponse, HttpTransport

from azure.core.polling.base_polling import (
    LongRunningOperation,
    BadStatus,
    LocationPolling
)
from azure.mgmt.core.polling.arm_polling import (
    ARMPolling,
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

CLIENT = PipelineClient("http://example.org")
def mock_run(client_self, request, **kwargs):
    return TestArmPolling.mock_update(request.url, request.headers)
CLIENT._pipeline.run = types.MethodType(mock_run, CLIENT)


@pytest.fixture
def pipeline_client_builder():
    """Build a client that use the "send" callback as final transport layer

    send will receive "request" and kwargs as any transport layer
    """
    def create_client(send_cb):
        class TestHttpTransport(HttpTransport):
            def open(self): pass
            def close(self): pass
            def __exit__(self, *args, **kwargs): pass

            def send(self, request, **kwargs):
                return send_cb(request, **kwargs)

        return PipelineClient(
            'http://example.org/',
            pipeline=Pipeline(
                transport=TestHttpTransport()
            )
        )
    return create_client


@pytest.fixture
def deserialization_cb():
    def cb(pipeline_response):
        return json.loads(pipeline_response.http_response.text())
    return cb


def test_post(pipeline_client_builder, deserialization_cb):

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

        def send(request, **kwargs):
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

        client = pipeline_client_builder(send)

        # Test 1, LRO options with Location final state
        poll = LROPoller(
            client,
            initial_response,
            deserialization_cb,
            ARMPolling(0, lro_options={"final-state-via": "location"}))
        result = poll.result()
        assert result['location_result'] == True

        # Test 2, LRO options with Azure-AsyncOperation final state
        poll = LROPoller(
            client,
            initial_response,
            deserialization_cb,
            ARMPolling(0, lro_options={"final-state-via": "azure-async-operation"}))
        result = poll.result()
        assert result['status'] == 'Succeeded'

        # Test 3, "do the right thing" and use Location by default
        poll = LROPoller(
            client,
            initial_response,
            deserialization_cb,
            ARMPolling(0))
        result = poll.result()
        assert result['location_result'] == True

        # Test 4, location has no body

        def send(request, **kwargs):
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

        client = pipeline_client_builder(send)

        poll = LROPoller(
            client,
            initial_response,
            deserialization_cb,
            ARMPolling(0, lro_options={"final-state-via": "location"}))
        result = poll.result()
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
            RequestsTransportResponse(
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
            RequestsTransportResponse(
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

        body = json.loads(response.text())
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

    def test_long_running_put(self):
        #TODO: Test custom header field

        # Test throw on non LRO related status code
        response = TestArmPolling.mock_send('PUT', 1000, {})
        with pytest.raises(HttpResponseError):
            LROPoller(CLIENT, response,
                TestArmPolling.mock_outputs,
                ARMPolling(0)).result()

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
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0)
        )
        assert poll.result().name == TEST_NAME
        assert not hasattr(poll._polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

        # Test polling from azure-asyncoperation header
        response = TestArmPolling.mock_send(
            'PUT', 201,
            {'azure-asyncoperation': ASYNC_URL})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        assert poll.result().name == TEST_NAME
        assert not hasattr(poll._polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

        # Test polling location header
        response = TestArmPolling.mock_send(
            'PUT', 201,
            {'location': LOCATION_URL})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        assert poll.result().name == TEST_NAME
        assert poll._polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

        # Test polling initial payload invalid (SQLDb)
        response_body = {}  # Empty will raise
        response = TestArmPolling.mock_send(
            'PUT', 201,
            {'location': LOCATION_URL}, response_body)
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        assert poll.result().name == TEST_NAME
        assert poll._polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

        # Test fail to poll from azure-asyncoperation header
        response = TestArmPolling.mock_send(
            'PUT', 201,
            {'azure-asyncoperation': ERROR})
        with pytest.raises(BadEndpointError):
            poll = LROPoller(CLIENT, response,
                TestArmPolling.mock_outputs,
                ARMPolling(0)).result()

        # Test fail to poll from location header
        response = TestArmPolling.mock_send(
            'PUT', 201,
            {'location': ERROR})
        with pytest.raises(BadEndpointError):
            poll = LROPoller(CLIENT, response,
                TestArmPolling.mock_outputs,
                ARMPolling(0)).result()

    def test_long_running_patch(self):

        # Test polling from location header
        response = TestArmPolling.mock_send(
            'PATCH', 202,
            {'location': LOCATION_URL},
            body={'properties':{'provisioningState': 'Succeeded'}})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        assert poll.result().name == TEST_NAME
        assert poll._polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

        # Test polling from azure-asyncoperation header
        response = TestArmPolling.mock_send(
            'PATCH', 202,
            {'azure-asyncoperation': ASYNC_URL},
            body={'properties':{'provisioningState': 'Succeeded'}})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        assert poll.result().name == TEST_NAME
        assert not hasattr(poll._polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

        # Test polling from location header
        response = TestArmPolling.mock_send(
            'PATCH', 200,
            {'location': LOCATION_URL},
            body={'properties':{'provisioningState': 'Succeeded'}})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        assert poll.result().name == TEST_NAME
        assert poll._polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

        # Test polling from azure-asyncoperation header
        response = TestArmPolling.mock_send(
            'PATCH', 200,
            {'azure-asyncoperation': ASYNC_URL},
            body={'properties':{'provisioningState': 'Succeeded'}})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        assert poll.result().name == TEST_NAME
        assert not hasattr(poll._polling_method._pipeline_response, 'randomFieldFromPollAsyncOpHeader')

        # Test fail to poll from azure-asyncoperation header
        response = TestArmPolling.mock_send(
            'PATCH', 202,
            {'azure-asyncoperation': ERROR})
        with pytest.raises(BadEndpointError):
            poll = LROPoller(CLIENT, response,
                TestArmPolling.mock_outputs,
                ARMPolling(0)).result()

        # Test fail to poll from location header
        response = TestArmPolling.mock_send(
            'PATCH', 202,
            {'location': ERROR})
        with pytest.raises(BadEndpointError):
            poll = LROPoller(CLIENT, response,
                TestArmPolling.mock_outputs,
                ARMPolling(0)).result()

    def test_long_running_delete(self):
        # Test polling from azure-asyncoperation header
        response = TestArmPolling.mock_send(
            'DELETE', 202,
            {'azure-asyncoperation': ASYNC_URL},
            body=""
        )
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        poll.wait()
        assert poll._polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollAsyncOpHeader is None

    def test_long_running_post_legacy(self):
        # Former oooooold tests to refactor one day to something more readble

        # Test polling from azure-asyncoperation header
        response = TestArmPolling.mock_send(
            'POST', 201,
            {'azure-asyncoperation': ASYNC_URL},
            body={'properties':{'provisioningState': 'Succeeded'}})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_deserialization_no_body,
            ARMPolling(0))
        poll.wait()
        assert poll._polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollAsyncOpHeader is None

        # Test polling from azure-asyncoperation header
        response = TestArmPolling.mock_send(
            'POST', 202,
            {'azure-asyncoperation': ASYNC_URL},
            body={'properties':{'provisioningState': 'Succeeded'}})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_deserialization_no_body,
            ARMPolling(0))
        poll.wait()
        assert poll._polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollAsyncOpHeader is None

        # Test polling from location header
        response = TestArmPolling.mock_send(
            'POST', 202,
            {'location': LOCATION_URL},
            body={'properties':{'provisioningState': 'Succeeded'}})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        assert poll.result().name == TEST_NAME
        assert poll._polling_method._pipeline_response.http_response.internal_response.randomFieldFromPollLocationHeader is None

        # Test fail to poll from azure-asyncoperation header
        response = TestArmPolling.mock_send(
            'POST', 202,
            {'azure-asyncoperation': ERROR})
        with pytest.raises(BadEndpointError):
            poll = LROPoller(CLIENT, response,
                TestArmPolling.mock_outputs,
                ARMPolling(0)).result()

        # Test fail to poll from location header
        response = TestArmPolling.mock_send(
            'POST', 202,
            {'location': ERROR})
        with pytest.raises(BadEndpointError):
            poll = LROPoller(CLIENT, response,
                TestArmPolling.mock_outputs,
                ARMPolling(0)).result()

    def test_long_running_negative(self):
        global LOCATION_BODY
        global POLLING_STATUS

        # Test LRO PUT throws for invalid json
        LOCATION_BODY = '{'
        response = TestArmPolling.mock_send(
            'POST', 202,
            {'location': LOCATION_URL})
        poll = LROPoller(
            CLIENT,
            response,
            TestArmPolling.mock_outputs,
            ARMPolling(0)
        )
        with pytest.raises(DecodeError):
            poll.result()

        LOCATION_BODY = '{\'"}'
        response = TestArmPolling.mock_send(
            'POST', 202,
            {'location': LOCATION_URL})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        with pytest.raises(DecodeError):
            poll.result()

        LOCATION_BODY = '{'
        POLLING_STATUS = 203
        response = TestArmPolling.mock_send(
            'POST', 202,
            {'location': LOCATION_URL})
        poll = LROPoller(CLIENT, response,
            TestArmPolling.mock_outputs,
            ARMPolling(0))
        with pytest.raises(HttpResponseError) as error: # TODO: Node.js raises on deserialization
            poll.result()
        assert error.value.continuation_token == base64.b64encode(pickle.dumps(response)).decode('ascii')

        LOCATION_BODY = json.dumps({ 'name': TEST_NAME })
        POLLING_STATUS = 200

    def test_polling_with_path_format_arguments(self):
        method = ARMPolling(
            timeout=0,
            path_format_arguments={"host": "host:3000", "accountName": "local"}
        )
        client = PipelineClient(base_url="http://{accountName}{host}")

        method._operation = LocationPolling()
        method._operation._location_url = "/results/1"
        method._client = client
        assert "http://localhost:3000/results/1" == method._client.format_url(method._operation.get_polling_url(), **method._path_format_arguments)

