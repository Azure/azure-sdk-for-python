# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the user agent policy."""
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline import PipelineRequest, PipelineContext

def test_user_agent_policy():
    user_agent = UserAgentPolicy(base_user_agent='foo')
    assert user_agent._user_agent == 'foo'

    user_agent = UserAgentPolicy(base_user_agent='foo', user_agent='bar')
    assert user_agent._user_agent == 'bar foo'

    request = HttpRequest('GET', 'http://127.0.0.1/')
    pipeline_request = PipelineRequest(request, PipelineContext(None))

    pipeline_request.context.options['user_agent'] = 'xyz'
    user_agent.on_request(pipeline_request)
    assert request.headers['User-Agent'] == 'xyz bar foo'
