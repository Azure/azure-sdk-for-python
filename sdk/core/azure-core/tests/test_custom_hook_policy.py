# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the custom hook policy."""
from azure.core import PipelineClient
from azure.core.pipeline.policies import CustomHookPolicy, UserAgentPolicy
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.rest import HttpRequest as RestHttpRequest
from azure.core.pipeline import PipelineRequest, PipelineContext
import pytest

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_response_hook_policy_in_init(request_type):
    def test_callback(response):
        raise ValueError()

    url = "https://bing.com"
    custom_hook_policy = CustomHookPolicy(raw_response_hook=test_callback)
    policies = [
        UserAgentPolicy("myuseragent"),
        custom_hook_policy
    ]
    client = PipelineClient(base_url=url, policies=policies)
    if hasattr(request_type, "content"):
        request = request_type("GET", url)
    else:
        request = client.get(url)
    with pytest.raises(ValueError):
        client._pipeline.run(request)

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_response_hook_policy_in_request(request_type):
    def test_callback(response):
        raise ValueError()

    url = "https://bing.com"
    custom_hook_policy = CustomHookPolicy()
    policies = [
        UserAgentPolicy("myuseragent"),
        custom_hook_policy
    ]
    client = PipelineClient(base_url=url, policies=policies)
    if hasattr(request_type, "content"):
        request = request_type("GET", url)
    else:
        request = client.get(url)
    with pytest.raises(ValueError):
        client._pipeline.run(request, raw_response_hook=test_callback)

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_response_hook_policy_in_both(request_type):
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
    if hasattr(request_type, "content"):
        request = request_type("GET", url)
    else:
        request = client.get(url)
    with pytest.raises(TypeError):
        client._pipeline.run(request, raw_response_hook=test_callback_request)

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_request_hook_policy_in_init(request_type):
    def test_callback(response):
        raise ValueError()

    url = "https://bing.com"
    custom_hook_policy = CustomHookPolicy(raw_request_hook=test_callback)
    policies = [
        UserAgentPolicy("myuseragent"),
        custom_hook_policy
    ]
    client = PipelineClient(base_url=url, policies=policies)
    if hasattr(request_type, "content"):
        request = request_type("GET", url)
    else:
        request = client.get(url)
    with pytest.raises(ValueError):
        client._pipeline.run(request)

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_request_hook_policy_in_request(request_type):
    def test_callback(response):
        raise ValueError()

    url = "https://bing.com"
    custom_hook_policy = CustomHookPolicy()
    policies = [
        UserAgentPolicy("myuseragent"),
        custom_hook_policy
    ]
    client = PipelineClient(base_url=url, policies=policies)
    if hasattr(request_type, "content"):
        request = request_type("GET", url)
    else:
        request = client.get(url)
    with pytest.raises(ValueError):
        client._pipeline.run(request, raw_request_hook=test_callback)

@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
def test_request_hook_policy_in_both(request_type):
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
    if hasattr(request_type, "content"):
        request = request_type("GET", url)
    else:
        request = client.get(url)
    with pytest.raises(TypeError):
        client._pipeline.run(request, raw_request_hook=test_callback_request)
