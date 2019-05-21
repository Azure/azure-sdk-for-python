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

import json
import re
import types
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from requests import Request, Response

from msrest import Deserializer, Configuration
from msrest.service_client import ServiceClient
from msrest.exceptions import DeserializationError
from msrest.polling import async_poller

from msrestazure.azure_exceptions import CloudError
from msrestazure.polling.async_arm_polling import (
    AsyncARMPolling,
)
from msrestazure.polling.arm_polling import (
    LongRunningOperation,
    BadStatus
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

CLIENT = ServiceClient(None, Configuration("http://example.org"))
async def mock_send(client_self, request, *, stream):
    return TestArmPolling.mock_update(request.url)
CLIENT.async_send = types.MethodType(mock_send, CLIENT)


class TestArmPolling(object):

    convert = re.compile('([a-z0-9])([A-Z])')

    @staticmethod
    def mock_send(method, status, headers, body=None):
        response = mock.create_autospec(Response)
        response.request = mock.create_autospec(Request)
        response.request.method = method
        response.request.url = RESOURCE_URL
        response.request.headers = {
            'x-ms-client-request-id': '67f4dd4e-6262-45e1-8bed-5c45cf23b6d9'
        }
        response.status_code = status
        response.headers = headers
        response.headers.update({"content-type": "application/json; charset=utf8"})
        content = body if body is not None else RESPONSE_BODY
        response.text = json.dumps(content)
        response.json = lambda: json.loads(response.text)
        return response

    @staticmethod
    def mock_update(url, headers=None):
        response = mock.create_autospec(Response)
        response.request = mock.create_autospec(Request)
        response.request.method = 'GET'
        response.headers = headers or {}
        response.headers.update({"content-type": "application/json; charset=utf8"})

        if url == ASYNC_URL:
            response.request.url = url
            response.status_code = POLLING_STATUS
            response.text = ASYNC_BODY
            response.randomFieldFromPollAsyncOpHeader = None

        elif url == LOCATION_URL:
            response.request.url = url
            response.status_code = POLLING_STATUS
            response.text = LOCATION_BODY
            response.randomFieldFromPollLocationHeader = None

        elif url == ERROR:
            raise BadEndpointError("boom")

        elif url == RESOURCE_URL:
            response.request.url = url
            response.status_code = POLLING_STATUS
            response.text = RESOURCE_BODY

        else:
            raise Exception('URL does not match')
        response.json = lambda: json.loads(response.text)
        return response

    @staticmethod
    def mock_outputs(response):
        body = response.json()
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
            raise DeserializationError("Impossible to deserialize")
            resource = SimpleResource(**body)
        return resource

@pytest.mark.asyncio
async def test_long_running_put():
    #TODO: Test custom header field

    # Test throw on non LRO related status code
    response = TestArmPolling.mock_send('PUT', 1000, {})
    op = LongRunningOperation(response, lambda x:None)
    with pytest.raises(BadStatus):
        op.set_initial_status(response)
    with pytest.raises(CloudError):
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
    assert not hasattr(polling_method._response, 'randomFieldFromPollAsyncOpHeader')

    # Test polling from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'PUT', 201,
        {'azure-asyncoperation': ASYNC_URL})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert not hasattr(polling_method._response, 'randomFieldFromPollAsyncOpHeader')

    # Test polling location header
    response = TestArmPolling.mock_send(
        'PUT', 201,
        {'location': LOCATION_URL})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll.name == TEST_NAME
    assert polling_method._response.randomFieldFromPollLocationHeader is None

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
    assert polling_method._response.randomFieldFromPollLocationHeader is None

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
    assert polling_method._response.randomFieldFromPollLocationHeader is None

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
    assert not hasattr(polling_method._response, 'randomFieldFromPollAsyncOpHeader')

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
    assert polling_method._response.randomFieldFromPollLocationHeader is None

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
    assert not hasattr(polling_method._response, 'randomFieldFromPollAsyncOpHeader')

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
        TestArmPolling.mock_outputs,
        polling_method)
    assert poll is None
    assert polling_method._response.randomFieldFromPollAsyncOpHeader is None

@pytest.mark.asyncio
async def test_long_running_post():

    # Test throw on non LRO related status code
    response = TestArmPolling.mock_send('POST', 201, {})
    op = LongRunningOperation(response, lambda x:None)
    with pytest.raises(BadStatus):
        op.set_initial_status(response)
    with pytest.raises(CloudError):
        await async_poller(CLIENT, response,
            TestArmPolling.mock_outputs,
            AsyncARMPolling(0))

    # Test polling from azure-asyncoperation header
    response = TestArmPolling.mock_send(
        'POST', 202,
        {'azure-asyncoperation': ASYNC_URL},
        body={'properties':{'provisioningState': 'Succeeded'}})
    polling_method = AsyncARMPolling(0)
    poll = await async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        polling_method)
    #self.assertIsNone(poll)
    assert polling_method._response.randomFieldFromPollAsyncOpHeader is None

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
    assert polling_method._response.randomFieldFromPollLocationHeader is None

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
    with pytest.raises(DeserializationError):
        await poll

    LOCATION_BODY = '{\'"}'
    response = TestArmPolling.mock_send(
        'POST', 202,
        {'location': LOCATION_URL})
    poll = async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        AsyncARMPolling(0))
    with pytest.raises(DeserializationError):
        await poll

    LOCATION_BODY = '{'
    POLLING_STATUS = 203
    response = TestArmPolling.mock_send(
        'POST', 202,
        {'location': LOCATION_URL})
    poll = async_poller(CLIENT, response,
        TestArmPolling.mock_outputs,
        AsyncARMPolling(0))
    with pytest.raises(CloudError): # TODO: Node.js raises on deserialization
        await poll

    LOCATION_BODY = json.dumps({ 'name': TEST_NAME })
    POLLING_STATUS = 200

