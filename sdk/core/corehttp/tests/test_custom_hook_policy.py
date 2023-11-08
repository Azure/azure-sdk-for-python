# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the custom hook policy."""
from unittest import mock

from corehttp.rest import HttpRequest
from corehttp.runtime import PipelineClient
from corehttp.runtime.policies import CustomHookPolicy, UserAgentPolicy
from corehttp.transport import HttpTransport
import pytest


def test_response_hook_policy_in_init():
    def test_callback(response):
        raise ValueError()

    transport = mock.MagicMock(spec=HttpTransport)
    url = "http://localhost"
    custom_hook_policy = CustomHookPolicy(raw_response_hook=test_callback)
    policies = [UserAgentPolicy("myuseragent"), custom_hook_policy]
    client = PipelineClient(endpoint=url, policies=policies, transport=transport)
    request = HttpRequest("GET", url)
    with pytest.raises(ValueError):
        client.send_request(request)


def test_response_hook_policy_in_request():
    def test_callback(response):
        raise ValueError()

    transport = mock.MagicMock(spec=HttpTransport)
    url = "http://localhost"
    custom_hook_policy = CustomHookPolicy()
    policies = [UserAgentPolicy("myuseragent"), custom_hook_policy]
    client = PipelineClient(endpoint=url, policies=policies, transport=transport)
    request = HttpRequest("GET", url)
    with pytest.raises(ValueError):
        client.send_request(request, raw_response_hook=test_callback)


def test_response_hook_policy_in_both():
    def test_callback(response):
        raise ValueError()

    def test_callback_request(response):
        raise TypeError()

    transport = mock.MagicMock(spec=HttpTransport)
    url = "http://localhost"
    custom_hook_policy = CustomHookPolicy(raw_response_hook=test_callback)
    policies = [UserAgentPolicy("myuseragent"), custom_hook_policy]
    client = PipelineClient(endpoint=url, policies=policies, transport=transport)
    request = HttpRequest("GET", url)
    with pytest.raises(TypeError):
        client.send_request(request, raw_response_hook=test_callback_request)


def test_request_hook_policy_in_init():
    def test_callback(response):
        raise ValueError()

    transport = mock.MagicMock(spec=HttpTransport)
    url = "http://localhost"
    custom_hook_policy = CustomHookPolicy(raw_request_hook=test_callback)
    policies = [UserAgentPolicy("myuseragent"), custom_hook_policy]
    client = PipelineClient(endpoint=url, policies=policies, transport=transport)
    request = HttpRequest("GET", url)
    with pytest.raises(ValueError):
        client.send_request(request)


def test_request_hook_policy_in_request():
    def test_callback(response):
        raise ValueError()

    transport = mock.MagicMock(spec=HttpTransport)
    url = "http://localhost"
    custom_hook_policy = CustomHookPolicy()
    policies = [UserAgentPolicy("myuseragent"), custom_hook_policy]
    client = PipelineClient(endpoint=url, policies=policies, transport=transport)
    request = HttpRequest("GET", url)
    with pytest.raises(ValueError):
        client.send_request(request, raw_request_hook=test_callback)


def test_request_hook_policy_in_both():
    def test_callback(response):
        raise ValueError()

    def test_callback_request(response):
        raise TypeError()

    transport = mock.MagicMock(spec=HttpTransport)
    url = "http://localhost"
    custom_hook_policy = CustomHookPolicy(raw_request_hook=test_callback)
    policies = [UserAgentPolicy("myuseragent"), custom_hook_policy]
    client = PipelineClient(endpoint=url, policies=policies, transport=transport)
    request = HttpRequest("GET", url)
    with pytest.raises(TypeError):
        client.send_request(request, raw_request_hook=test_callback_request)
