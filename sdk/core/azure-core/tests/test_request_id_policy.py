# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the request id policy."""
from azure.core.pipeline.policies import RequestIdPolicy
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline import PipelineRequest, PipelineContext
import pytest

def test_request_id_policy_fix_id():
    """Test policy with no other policy and happy path"""
    test_request_id = 'test_request_id'
    request_id_policy = RequestIdPolicy(request_id=test_request_id)
    request = HttpRequest('GET', 'http://127.0.0.1/')
    pipeline_request = PipelineRequest(request, PipelineContext(None))
    request_id_policy.on_request(pipeline_request)
    assert request.headers["x-ms-client-request-id"] == test_request_id

def test_request_id_policy_fix_on_demand_id():
    """Test policy with no other policy and happy path"""
    test_request_id = 'test_request_id'
    request_id_policy = RequestIdPolicy()
    request = HttpRequest('GET', 'http://127.0.0.1/')
    pipeline_request = PipelineRequest(request, PipelineContext(None))
    pipeline_request.context.options['request_id'] = test_request_id
    request_id_policy.on_request(pipeline_request)
    assert request.headers["x-ms-client-request-id"] == test_request_id
