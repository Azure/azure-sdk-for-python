# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------
import pytest
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    map_error,
    ErrorMap,
)
from utils import request_and_responses_product, create_http_response, HTTP_RESPONSES

@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_error_map(http_request, http_response):
    request = http_request("GET", "")
    response = create_http_response(http_response, request, None)
    error_map = {
        404: ResourceNotFoundError
    }
    with pytest.raises(ResourceNotFoundError):
        map_error(404, response, error_map)

@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_error_map_no_default(http_request, http_response):
    request = http_request("GET", "")
    response = create_http_response(http_response, request, None)
    error_map = ErrorMap({
        404: ResourceNotFoundError
    })
    with pytest.raises(ResourceNotFoundError):
        map_error(404, response, error_map)

@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_error_map_with_default(http_request, http_response):
    request = http_request("GET", "")
    response = create_http_response(http_response, request, None)
    error_map = ErrorMap({
        404: ResourceNotFoundError
    }, default_error=ResourceExistsError)
    with pytest.raises(ResourceExistsError):
        map_error(401, response, error_map)

@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_only_default(http_request, http_response):
    request = http_request("GET", "")
    response = create_http_response(http_response, request, None)
    error_map = ErrorMap(default_error=ResourceExistsError)
    with pytest.raises(ResourceExistsError):
        map_error(401, response, error_map)
