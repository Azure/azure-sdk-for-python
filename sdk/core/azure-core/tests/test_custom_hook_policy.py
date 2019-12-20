# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the custom hook policy."""
from azure.core.pipeline.policies import CustomHookPolicy
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline import PipelineRequest, PipelineContext
import pytest

def test_custom_hook_policy_set_hook():
    def test_callback(response):
        raise ValueError()
    custom_hook_policy = CustomHookPolicy()
    request = HttpRequest('GET', 'http://127.0.0.1/')
    pipeline_request = PipelineRequest(request, PipelineContext(None, raw_response_hook=test_callback))
    custom_hook_policy.on_request(pipeline_request)
    assert custom_hook_policy._callback is test_callback

def test_custom_hook_policy_invoke_hook():
    def test_callback(response):
        raise ValueError()

    custom_hook_policy = CustomHookPolicy()
    request = HttpRequest('GET', 'http://127.0.0.1/')
    pipeline_request = PipelineRequest(request, PipelineContext(None, raw_response_hook=test_callback))
    custom_hook_policy.on_request(pipeline_request)
    with pytest.raises(ValueError):
        custom_hook_policy.on_response(pipeline_request, None)
