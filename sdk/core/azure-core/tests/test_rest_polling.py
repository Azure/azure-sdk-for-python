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
import pytest
from azure.core.exceptions import ServiceRequestError
from azure.core.rest import HttpRequest
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling

@pytest.fixture
def deserialization_callback():
    def _callback(response):
        return response.http_response.json()
    return _callback

@pytest.fixture
def lro_poller(client, deserialization_callback):
    def _callback(request, **kwargs):
        initial_response = client.send_request(
            request=request,
            _return_pipeline_response=True
        )
        return LROPoller(
            client._client,
            initial_response,
            deserialization_callback,
            LROBasePolling(0, **kwargs),
        )
    return _callback

def test_post_with_location_and_operation_location_headers(lro_poller):
    poller = lro_poller(HttpRequest("POST", "/polling/post/location-and-operation-location"))
    result = poller.result()
    assert result == {'location_result': True}

def test_post_with_location_and_operation_location_headers_no_body(lro_poller):
    poller = lro_poller(HttpRequest("POST", "/polling/post/location-and-operation-location-no-body"))
    result = poller.result()
    assert result is None

def test_post_resource_location(lro_poller):
    poller = lro_poller(HttpRequest("POST", "/polling/post/resource-location"))
    result = poller.result()
    assert result == {'location_result': True}

def test_put_no_polling(lro_poller):
    result = lro_poller(HttpRequest("PUT", "/polling/no-polling")).result()
    assert result['properties']['provisioningState'] == 'Succeeded'

def test_put_location(lro_poller):
    result = lro_poller(HttpRequest("PUT", "/polling/location")).result()
    assert result['location_result']

def test_put_initial_response_body_invalid(lro_poller):
    # initial body is invalid
    result = lro_poller(HttpRequest("PUT", "/polling/initial-body-invalid")).result()
    assert result['location_result']

def test_put_operation_location_polling_fail(lro_poller):
    with pytest.raises(ServiceRequestError):
        lro_poller(HttpRequest("PUT", "/polling/bad-operation-location"), retry_total=0).result()

def test_put_location_polling_fail(lro_poller):
    with pytest.raises(ServiceRequestError):
        lro_poller(HttpRequest("PUT", "/polling/bad-location"), retry_total=0).result()

def test_patch_location(lro_poller):
    result = lro_poller(HttpRequest("PATCH", "/polling/location")).result()
    assert result['location_result']

def test_patch_operation_location_polling_fail(lro_poller):
    with pytest.raises(ServiceRequestError):
        lro_poller(HttpRequest("PUT", "/polling/bad-operation-location"), retry_total=0).result()

def test_patch_location_polling_fail(lro_poller):
    with pytest.raises(ServiceRequestError):
        lro_poller(HttpRequest("PUT", "/polling/bad-location"), retry_total=0).result()

def test_delete_operation_location(lro_poller):
    result = lro_poller(HttpRequest("DELETE", "/polling/operation-location")).result()
    assert result['status'] == 'Succeeded'

def test_request_id(lro_poller):
    result = lro_poller(HttpRequest("POST", "/polling/request-id"), request_id="123456789").result()

def test_continuation_token(client, lro_poller, deserialization_callback):
    poller = lro_poller(HttpRequest("POST", "/polling/post/location-and-operation-location"))
    token = poller.continuation_token()
    new_poller = LROPoller.from_continuation_token(
        continuation_token=token,
        polling_method=LROBasePolling(0),
        client=client._client,
        deserialization_callback=deserialization_callback,
    )
    result = new_poller.result()
    assert result == {'location_result': True}
