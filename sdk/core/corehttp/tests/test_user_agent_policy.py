# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the user agent policy."""
from unittest import mock

from corehttp.rest import HttpRequest
from corehttp.runtime.policies import UserAgentPolicy
from corehttp.runtime.pipeline import PipelineRequest, PipelineContext
import pytest


def test_user_agent_policy():
    user_agent = UserAgentPolicy(base_user_agent="foo")
    assert user_agent._user_agent == "foo"

    user_agent = UserAgentPolicy(sdk_moniker="foosdk/1.0.0")
    assert user_agent._user_agent.startswith("python-foosdk/1.0.0 Python")

    user_agent = UserAgentPolicy(base_user_agent="foo", user_agent="bar", user_agent_use_env=False)
    assert user_agent._user_agent == "bar foo"

    request = HttpRequest("GET", "http://localhost/")
    pipeline_request = PipelineRequest(request, PipelineContext(None))

    pipeline_request.context.options["user_agent"] = "xyz"
    user_agent.on_request(pipeline_request)
    assert request.headers["User-Agent"] == "xyz bar foo"


def test_user_agent_environ():

    with mock.patch.dict("os.environ", {"CORE_HTTP_USER_AGENT": "mytools"}):
        policy = UserAgentPolicy(None)
        assert policy.user_agent.endswith("mytools")

        request = HttpRequest("GET", "http://localhost/")
        policy.on_request(PipelineRequest(request, PipelineContext(None)))
        assert request.headers["user-agent"].endswith("mytools")
