# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the user agent policy."""
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.pipeline import PipelineRequest, PipelineContext
try:
    from unittest import mock
except ImportError:
    import mock
import pytest
from utils import HTTP_REQUESTS

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_user_agent_policy(http_request):
    user_agent = UserAgentPolicy(base_user_agent='foo')
    assert user_agent._user_agent == 'foo'

    user_agent = UserAgentPolicy(sdk_moniker='foosdk/1.0.0')
    assert user_agent._user_agent.startswith('azsdk-python-foosdk/1.0.0 Python')

    user_agent = UserAgentPolicy(base_user_agent='foo', user_agent='bar', user_agent_use_env=False)
    assert user_agent._user_agent == 'bar foo'

    request = http_request('GET', 'http://localhost/')
    pipeline_request = PipelineRequest(request, PipelineContext(None))

    pipeline_request.context.options['user_agent'] = 'xyz'
    user_agent.on_request(pipeline_request)
    assert request.headers['User-Agent'] == 'xyz bar foo'


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_user_agent_environ(http_request):

    with mock.patch.dict('os.environ', {'AZURE_HTTP_USER_AGENT': "mytools"}):
        policy = UserAgentPolicy(None)
        assert policy.user_agent.endswith("mytools")

        request = http_request('GET', 'http://localhost/')
        policy.on_request(PipelineRequest(request, PipelineContext(None)))
        assert request.headers["user-agent"].endswith("mytools")
