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

def test_response_hook_policy_in_init():
    def test_callback(response):
        raise ValueError()

    url = "https://bing.com"
    custom_hook_policy = CustomHookPolicy(raw_response_hook=test_callback)
    policies = [
        UserAgentPolicy("myuseragent"),
        custom_hook_policy
    ]
    client = PipelineClient(base_url=url, policies=policies)
    request = client.get(url)
    with pytest.raises(ValueError):
        client._pipeline.run(request)

def test_response_hook_policy_in_request():
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

def test_response_hook_policy_in_both():
    def test_callback(response):
        raise ValueError()

    def test_callback_request(response):
        raise TypeError()

    url = "https://bing.com"
    custom_hook_policy = CustomHookPolicy(raw_response_hook=test_callback)
    policies = [
        UserAgentPolicy("myuseragent"),
        custom_hook_policy
    ]
    client = PipelineClient(base_url=url, policies=policies)
    request = client.get(url)
    with pytest.raises(TypeError):
        client._pipeline.run(request, raw_response_hook=test_callback_request)

def test_request_hook_policy_in_init():
    def test_callback(response):
        raise ValueError()

    url = "https://bing.com"
    custom_hook_policy = CustomHookPolicy(raw_request_hook=test_callback)
    policies = [
        UserAgentPolicy("myuseragent"),
        custom_hook_policy
    ]
    client = PipelineClient(base_url=url, policies=policies)
    request = client.get(url)
    with pytest.raises(ValueError):
        client._pipeline.run(request)

def test_request_hook_policy_in_request():
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

def test_request_hook_policy_in_both():
    def test_callback(response):
        raise ValueError()

    def test_callback_request(response):
        raise TypeError()

    url = "https://bing.com"
    custom_hook_policy = CustomHookPolicy(raw_request_hook=test_callback)
    policies = [
        UserAgentPolicy("myuseragent"),
        custom_hook_policy
    ]
    client = PipelineClient(base_url=url, policies=policies)
    request = client.get(url)
    with pytest.raises(TypeError):
        client._pipeline.run(request, raw_request_hook=test_callback_request)
