# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the request id policy."""
from azure.core.pipeline.policies import RequestIdPolicy
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline import PipelineRequest, PipelineContext
from mock import patch
from itertools import product
import pytest

auto_request_id_values = (True, False, None)
request_id_init_values = ("foo", None)
request_id_set_values = ("bar", None)
request_id_req_values = ("baz", None)
full_combination = list(product(auto_request_id_values, request_id_init_values, request_id_set_values, request_id_req_values))

@pytest.mark.parametrize("auto_request_id, request_id_init, request_id_set, request_id_req", full_combination)
def test_request_id_policy(auto_request_id, request_id_init, request_id_set, request_id_req):
    """Test policy with no other policy and happy path"""
    kwargs = {}
    if auto_request_id is not None:
        kwargs['auto_request_id'] = auto_request_id
    if request_id_init is not None:
        kwargs['request_id'] = request_id_init
    request_id_policy = RequestIdPolicy(**kwargs)
    if request_id_set is not None:
        request_id_policy.set_request_id(request_id_set)
    request = HttpRequest('GET', 'http://127.0.0.1/')
    pipeline_request = PipelineRequest(request, PipelineContext(None))
    if request_id_req is not None:
        pipeline_request.context.options['request_id'] = request_id_req
    with patch('uuid.uuid1', return_value="VALUE"):
        request_id_policy.on_request(pipeline_request)

    if request_id_req:
        assert request.headers["x-ms-client-request-id"] == request_id_req
    elif request_id_set:
        assert request.headers["x-ms-client-request-id"] == request_id_set
    elif request_id_init:
        assert request.headers["x-ms-client-request-id"] == request_id_init
    elif auto_request_id or auto_request_id is None:
        assert request.headers["x-ms-client-request-id"] == "VALUE"
    else:
        assert not "x-ms-client-request-id" in request.headers
