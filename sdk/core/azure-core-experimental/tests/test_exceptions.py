# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from itertools import product

from azure.core.exceptions import HttpResponseError

from rest_client import MockRestClient
from utils import SYNC_TRANSPORTS, HTTP_REQUESTS, create_http_request


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_httpresponse_error_with_response(port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/basic/string")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request, stream=False)
    error = HttpResponseError(response=response)
    assert error.message == "Operation returned an invalid status 'OK'"
    assert error.response is not None
    assert error.reason == "OK"
    assert isinstance(error.status_code, int)


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_malformed_json(port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/errors/malformed-json")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request)
    with pytest.raises(HttpResponseError) as ex:
        response.raise_for_status()
    assert (
        str(ex.value)
        == 'Operation returned an invalid status \'BAD REQUEST\'\nContent: {"code": 400, "error": {"global": ["MY-ERROR-MESSAGE-THAT-IS-COMING-FROM-THE-API"]'
    )


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_text(port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/errors/text")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request)
    with pytest.raises(HttpResponseError) as ex:
        response.raise_for_status()
    assert str(ex.value) == "Operation returned an invalid status 'BAD REQUEST'\nContent: I am throwing an error"
