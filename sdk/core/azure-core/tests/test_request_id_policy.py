# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the request id policy."""
from azure.core.pipeline.policies import RequestIdPolicy
from azure.core.pipeline import PipelineRequest, PipelineContext
try:
    from unittest import mock
except ImportError:
    import mock
from itertools import product
import pytest
from utils import HTTP_REQUESTS

auto_request_id_values = (True, False, None)
request_id_init_values = ("foo", None, "_unset")
request_id_set_values = ("bar", None, "_unset")
request_id_req_values = ("baz", None, "_unset")
full_combination = list(product(auto_request_id_values, request_id_init_values, request_id_set_values, request_id_req_values, HTTP_REQUESTS))

@pytest.mark.parametrize("auto_request_id, request_id_init, request_id_set, request_id_req, http_request", full_combination)
def test_request_id_policy(auto_request_id, request_id_init, request_id_set, request_id_req, http_request):
    """Test policy with no other policy and happy path"""
    kwargs = {}
    if auto_request_id is not None:
        kwargs['auto_request_id'] = auto_request_id
    if request_id_init != "_unset":
        kwargs['request_id'] = request_id_init
    request_id_policy = RequestIdPolicy(**kwargs)
    if request_id_set != "_unset":
        request_id_policy.set_request_id(request_id_set)
    request = http_request('GET', 'http://localhost/')
    pipeline_request = PipelineRequest(request, PipelineContext(None))
    if request_id_req != "_unset":
        pipeline_request.context.options['request_id'] = request_id_req
    with mock.patch('uuid.uuid1', return_value="VALUE"):
        request_id_policy.on_request(pipeline_request)

    assert all(v is not None for v in request.headers.values())
    if request_id_req != "_unset" and request_id_req:
        assert request.headers["x-ms-client-request-id"] == request_id_req
    elif not request_id_req:
        assert not "x-ms-client-request-id" in request.headers
    elif request_id_set != "_unset" and request_id_set:
        assert request.headers["x-ms-client-request-id"] == request_id_set
    elif not request_id_set:
        assert not "x-ms-client-request-id" in request.headers
    elif request_id_init != "_unset" and request_id_init:
        assert request.headers["x-ms-client-request-id"] == request_id_init
    elif not request_id_init:
        assert not "x-ms-client-request-id" in request.headers
    elif auto_request_id or auto_request_id is None:
        assert request.headers["x-ms-client-request-id"] == "VALUE"
    else:
        assert not "x-ms-client-request-id" in request.headers

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_request_id_already_exists(http_request):
    """Test policy with no other policy and happy path"""
    request_id_policy = RequestIdPolicy()
    request = http_request('GET', 'http://localhost/')
    request.headers["x-ms-client-request-id"] = "VALUE"
    pipeline_request = PipelineRequest(request, PipelineContext(None))
    request_id_policy.on_request(pipeline_request)
    assert request.headers["x-ms-client-request-id"] == "VALUE"
