# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for policy override support in azure-identity pipelines."""

from unittest.mock import Mock

import pytest

from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    CustomHookPolicy,
    DistributedTracingPolicy,
    HeadersPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    RequestIdPolicy,
    RetryPolicy,
    SansIOHTTPPolicy,
    UserAgentPolicy,
)

from azure.identity._internal.pipeline import (
    _get_config,
    _get_policies,
    build_pipeline,
    build_async_pipeline,
)

CONFIG_POLICIES = [
    ("custom_hook_policy", CustomHookPolicy),
    ("headers_policy", HeadersPolicy),
    ("http_logging_policy", HttpLoggingPolicy),
    ("logging_policy", NetworkTraceLoggingPolicy),
    ("proxy_policy", ProxyPolicy),
    ("user_agent_policy", UserAgentPolicy),
]


class TestGetConfigPolicyOverrides:
    """Tests that _get_config respects policy override kwargs."""

    def test_default_policies_created_when_no_overrides(self):
        config = _get_config()
        for attr, cls in CONFIG_POLICIES:
            assert isinstance(getattr(config, attr), cls)

    @pytest.mark.parametrize("kwarg,cls", CONFIG_POLICIES)
    def test_single_policy_override(self, kwarg, cls):
        custom = Mock(spec=cls)
        config = _get_config(**{kwarg: custom})
        assert getattr(config, kwarg) is custom

    @pytest.mark.parametrize("kwarg,cls", CONFIG_POLICIES)
    def test_non_overridden_policies_unaffected(self, kwarg, cls):
        """Overriding one policy should not affect others."""
        custom = Mock(spec=cls)
        config = _get_config(**{kwarg: custom})
        for other_attr, other_cls in CONFIG_POLICIES:
            if other_attr == kwarg:
                assert getattr(config, other_attr) is custom
            else:
                assert isinstance(getattr(config, other_attr), other_cls)


class TestGetPoliciesOverrides:
    """Tests for per_call_policies and per_retry_policies in _get_policies."""

    @staticmethod
    def _make_config():
        config = _get_config()
        config.retry_policy = RetryPolicy()
        return config

    def test_default_policy_order(self):
        policies = _get_policies(self._make_config())

        assert [type(p) for p in policies] == [
            RequestIdPolicy,
            HeadersPolicy,
            UserAgentPolicy,
            ProxyPolicy,
            ContentDecodePolicy,
            RetryPolicy,
            CustomHookPolicy,
            NetworkTraceLoggingPolicy,
            DistributedTracingPolicy,
            HttpLoggingPolicy,
        ]

    @pytest.mark.parametrize("as_list", [False, True], ids=["single", "list"])
    def test_per_call_policies_inserted_before_retry(self, as_list):
        custom_policies = [Mock(spec=SansIOHTTPPolicy) for _ in range(2 if as_list else 1)]
        arg = custom_policies if as_list else custom_policies[0]

        policies = _get_policies(self._make_config(), per_call_policies=arg)
        retry_idx = next(i for i, p in enumerate(policies) if isinstance(p, RetryPolicy))
        for custom in custom_policies:
            assert policies.index(custom) < retry_idx

    @pytest.mark.parametrize("as_list", [False, True], ids=["single", "list"])
    def test_per_retry_policies_inserted_after_retry(self, as_list):
        custom_policies = [Mock(spec=SansIOHTTPPolicy) for _ in range(2 if as_list else 1)]
        arg = custom_policies if as_list else custom_policies[0]

        policies = _get_policies(self._make_config(), per_retry_policies=arg)
        retry_idx = next(i for i, p in enumerate(policies) if isinstance(p, RetryPolicy))
        for custom in custom_policies:
            assert policies.index(custom) > retry_idx

    def test_both_per_call_and_per_retry(self):
        per_call = Mock(spec=SansIOHTTPPolicy)
        per_retry = Mock(spec=SansIOHTTPPolicy)

        policies = _get_policies(self._make_config(), per_call_policies=per_call, per_retry_policies=per_retry)
        retry_idx = next(i for i, p in enumerate(policies) if isinstance(p, RetryPolicy))
        assert policies.index(per_call) < retry_idx
        assert policies.index(per_retry) > retry_idx


class TestBuildPipelineOverrides:
    """Tests for policy overrides in build_pipeline and build_async_pipeline."""

    @pytest.mark.parametrize("builder", [build_pipeline, build_async_pipeline])
    def test_retry_policy_override(self, builder):
        custom_retry = Mock(spec=RetryPolicy)
        pipeline = builder(retry_policy=custom_retry, transport=Mock())
        effective_policies = [getattr(policy, "_policy", policy) for policy in pipeline._impl_policies]
        assert custom_retry in effective_policies

    def test_default_retry_policy_when_no_override(self):
        pipeline = build_pipeline(transport=Mock())
        retry_policies = [p for p in pipeline._impl_policies if isinstance(p, RetryPolicy)]
        assert len(retry_policies) == 1

    @pytest.mark.parametrize("builder", [build_pipeline, build_async_pipeline])
    def test_policy_override_flows_through(self, builder):
        """Verify that config policy overrides reach the pipeline."""
        custom_headers = Mock(spec=HeadersPolicy)
        pipeline = builder(headers_policy=custom_headers, transport=Mock())
        effective_policies = [getattr(policy, "_policy", policy) for policy in pipeline._impl_policies]
        assert custom_headers in effective_policies
