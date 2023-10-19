# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from corehttp.exceptions import (
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
    error_map = {404: ResourceNotFoundError}
    with pytest.raises(ResourceNotFoundError):
        map_error(404, response, error_map)


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_error_map_no_default(http_request, http_response):
    request = http_request("GET", "")
    response = create_http_response(http_response, request, None)
    error_map = ErrorMap({404: ResourceNotFoundError})
    with pytest.raises(ResourceNotFoundError):
        map_error(404, response, error_map)


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_error_map_with_default(http_request, http_response):
    request = http_request("GET", "")
    response = create_http_response(http_response, request, None)
    error_map = ErrorMap({404: ResourceNotFoundError}, default_error=ResourceExistsError)
    with pytest.raises(ResourceExistsError):
        map_error(401, response, error_map)


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_RESPONSES))
def test_only_default(http_request, http_response):
    request = http_request("GET", "")
    response = create_http_response(http_response, request, None)
    error_map = ErrorMap(default_error=ResourceExistsError)
    with pytest.raises(ResourceExistsError):
        map_error(401, response, error_map)
