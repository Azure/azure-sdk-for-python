# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import TYPE_CHECKING, Any, List, Optional

from azure.ai.ml._user_agent import USER_AGENT
from azure.core.configuration import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    CustomHookPolicy,
    DistributedTracingPolicy,
    HeadersPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    RetryPolicy,
    UserAgentPolicy,
)

# pylint: disable-next=no-name-in-module,non-abstract-transport-import
from azure.core.pipeline.transport import HttpTransport, RequestsTransport

if TYPE_CHECKING:
    from azure.core.pipeline import AsyncPipeline


def _get_config(**kwargs: Any) -> Configuration:
    """Configuration common to a/sync pipelines.

    :return: The configuration object
    :rtype: Configuration
    """
    config = Configuration(**kwargs)
    config.custom_hook_policy = CustomHookPolicy(**kwargs)
    config.headers_policy = HeadersPolicy(**kwargs)
    config.http_logging_policy = HttpLoggingPolicy(**kwargs)
    config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
    config.proxy_policy = ProxyPolicy(**kwargs)
    config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)
    return config


def _get_policies(config: Any, _per_retry_policies: Any = None, **kwargs: Any) -> List:
    policies = [
        config.headers_policy,
        config.user_agent_policy,
        config.proxy_policy,
        ContentDecodePolicy(**kwargs),
        config.retry_policy,
    ]

    if _per_retry_policies:
        policies.extend(_per_retry_policies)

    policies.extend(
        [
            config.custom_hook_policy,
            config.logging_policy,
            DistributedTracingPolicy(**kwargs),
            config.http_logging_policy,
        ]
    )

    return policies


def build_pipeline(transport: HttpTransport = None, policies: Optional[List] = None, **kwargs: Any) -> Pipeline:
    if not policies:
        config = _get_config(**kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        policies = _get_policies(config, **kwargs)
    if not transport:
        transport = RequestsTransport(**kwargs)

    return Pipeline(transport, policies=policies)


def build_async_pipeline(
    transport: HttpTransport = None, policies: Optional[List] = None, **kwargs: Any
) -> "AsyncPipeline":
    from azure.core.pipeline import AsyncPipeline

    if not policies:
        from azure.core.pipeline.policies import AsyncRetryPolicy

        config = _get_config(**kwargs)
        config.retry_policy = AsyncRetryPolicy(**kwargs)
        policies = _get_policies(config, **kwargs)
    if not transport:
        # pylint: disable-next=no-name-in-module,non-abstract-transport-import
        from azure.core.pipeline.transport import AioHttpTransport

        transport = AioHttpTransport(**kwargs)

    return AsyncPipeline(transport, policies=policies)
