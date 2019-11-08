# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import six
from .._policies import CognitiveServicesCredentialPolicy
from ._policies_async import AsyncTextAnalyticsResponseHook
from azure.core.pipeline import AsyncPipeline
from azure.core.configuration import Configuration
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    ProxyPolicy,
    NetworkTraceLoggingPolicy,
    AsyncRetryPolicy,
    AsyncRedirectPolicy,
    AsyncBearerTokenCredentialPolicy,
    HttpLoggingPolicy,
    DistributedTracingPolicy
)
from .._version import VERSION


class AsyncTextAnalyticsClientBase(object):

    def __init__(self, credentials, **kwargs):
        self._pipeline = self._create_pipeline(credentials, **kwargs)

    def _create_pipeline(self, credentials, **kwargs):
        credential_policy = None
        if hasattr(credentials, "get_token"):
            credential_policy = AsyncBearerTokenCredentialPolicy(
                credentials, "https://cognitiveservices.azure.com/.default"
            )
        elif isinstance(credentials, six.text_type):
            credential_policy = CognitiveServicesCredentialPolicy(credentials, **kwargs)
        elif credentials is not None:
            raise TypeError("Unsupported credential: {}".format(credentials))

        config = self.create_configuration(**kwargs)
        config.transport = kwargs.get("transport")  # type: ignore
        if not config.transport:
            try:
                from azure.core.pipeline.transport import AioHttpTransport
            except ImportError:
                raise ImportError("Unable to create async transport. Please check aiohttp is installed.")
            config.transport = AioHttpTransport(**kwargs)
        config.user_agent_policy.add_user_agent('azsdk-python-textanalyticsclient/{}'.format(VERSION))

        policies = [
            config.headers_policy,
            config.user_agent_policy,
            config.proxy_policy,
            credential_policy,
            AsyncRedirectPolicy(**kwargs),
            AsyncRetryPolicy(**kwargs),
            config.logging_policy,
            AsyncTextAnalyticsResponseHook(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs)
        ]
        return AsyncPipeline(config.transport, policies=policies)

    def create_configuration(self, **kwargs):
        config = Configuration(**kwargs)
        config.user_agent_policy = kwargs.get('user_agent_policy') or UserAgentPolicy(**kwargs)
        config.headers_policy = kwargs.get('headers_policy') or HeadersPolicy(**kwargs)
        config.proxy_policy = kwargs.get('proxy_policy') or ProxyPolicy(**kwargs)
        config.logging_policy = kwargs.get('logging_policy') or NetworkTraceLoggingPolicy(**kwargs)
        return config

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._client.__aexit__(*args)
