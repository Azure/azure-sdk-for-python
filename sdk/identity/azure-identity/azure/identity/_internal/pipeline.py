# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections.abc import Iterable

from azure.core.configuration import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    CustomHookPolicy,
    DistributedTracingPolicy,
    HeadersPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    RequestIdPolicy,
    RetryPolicy,
    UserAgentPolicy,
    HttpLoggingPolicy,
)


from .user_agent import USER_AGENT


def _get_config(**kwargs) -> Configuration:
    """Configuration common to a/sync pipelines.

    :return: A configuration object.
    :rtype: ~azure.core.configuration.Configuration
    """
    config: Configuration = Configuration(**kwargs)
    config.custom_hook_policy = kwargs.get("custom_hook_policy") or CustomHookPolicy(**kwargs)
    config.headers_policy = kwargs.get("headers_policy") or HeadersPolicy(**kwargs)
    config.http_logging_policy = kwargs.get("http_logging_policy") or HttpLoggingPolicy(**kwargs)
    config.logging_policy = kwargs.get("logging_policy") or NetworkTraceLoggingPolicy(**kwargs)
    config.proxy_policy = kwargs.get("proxy_policy") or ProxyPolicy(**kwargs)
    config.user_agent_policy = kwargs.get("user_agent_policy") or UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)
    return config


def _get_policies(config, **kwargs):
    per_call_policies = kwargs.get("per_call_policies", None) or []
    per_retry_policies = kwargs.get("per_retry_policies", None) or []

    policies = [
        RequestIdPolicy(**kwargs),
        config.headers_policy,
        config.user_agent_policy,
        config.proxy_policy,
        ContentDecodePolicy(**kwargs),
    ]

    if isinstance(per_call_policies, Iterable):
        policies.extend(per_call_policies)
    elif per_call_policies is not None:
        policies.append(per_call_policies)

    policies.append(config.retry_policy)

    if isinstance(per_retry_policies, Iterable):
        policies.extend(per_retry_policies)
    elif per_retry_policies is not None:
        policies.append(per_retry_policies)

    policies.extend(
        [
            config.custom_hook_policy,
            config.logging_policy,
            DistributedTracingPolicy(**kwargs),
            config.http_logging_policy,
        ]
    )

    return policies


def build_pipeline(transport=None, policies=None, **kwargs):
    if not policies:
        config = _get_config(**kwargs)
        config.retry_policy = kwargs.pop("retry_policy", None) or RetryPolicy(**kwargs)
        policies = _get_policies(config, **kwargs)
    if not transport:
        from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import, no-name-in-module
            RequestsTransport,
        )

        transport = RequestsTransport(**kwargs)

    return Pipeline(transport, policies=policies)


def build_async_pipeline(transport=None, policies=None, **kwargs):
    from azure.core.pipeline import AsyncPipeline

    if not policies:
        from azure.core.pipeline.policies import AsyncRetryPolicy

        config = _get_config(**kwargs)
        config.retry_policy = kwargs.pop("retry_policy", None) or AsyncRetryPolicy(**kwargs)
        policies = _get_policies(config, **kwargs)
    if not transport:
        from azure.core.pipeline.transport import (  # pylint: disable=non-abstract-transport-import, no-name-in-module
            AioHttpTransport,
        )

        transport = AioHttpTransport(**kwargs)

    return AsyncPipeline(transport, policies=policies)
