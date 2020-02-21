# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the custom hook policy."""
from azure.core import PipelineClient
from azure.core.pipeline.policies import CustomHookPolicy, UserAgentPolicy
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline import PipelineRequest, PipelineContext
import pytest

def test_response_hook_policy():
    def test_callback(response):
        raise ValueError()

    url = "https://bing.com"
    custom_hook_policy = CustomHookPolicy()
    policies = [
        UserAgentPolicy("myuseragent"),
        custom_hook_policy
    ]
    client = PipelineClient(base_url=url, policies=policies)
    request = client.get(url)
    with pytest.raises(ValueError):
        client._pipeline.run(request, raw_response_hook=test_callback)

def test_request_hook_policy():
    def test_callback(response):
        raise ValueError()

    url = "https://bing.com"
    custom_hook_policy = CustomHookPolicy()
    policies = [
        UserAgentPolicy("myuseragent"),
        custom_hook_policy
    ]
    client = PipelineClient(base_url=url, policies=policies)
    request = client.get(url)
    with pytest.raises(ValueError):
        client._pipeline.run(request, raw_request_hook=test_callback)
