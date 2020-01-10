# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import six
from azure.core.pipeline import AsyncPipeline
from azure.core.configuration import Configuration
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    ProxyPolicy,
    RequestIdPolicy,
    NetworkTraceLoggingPolicy,
    AsyncRetryPolicy,
    AsyncRedirectPolicy,
    AsyncBearerTokenCredentialPolicy,
    HttpLoggingPolicy,
    DistributedTracingPolicy
)
from .._policies import CognitiveServicesCredentialPolicy
from ._policies_async import AsyncTextAnalyticsResponseHook
from .._version import VERSION


class AsyncTextAnalyticsClientBase(object):

    def __init__(self, credential, **kwargs):
        self._pipeline = self._create_pipeline(credential, **kwargs)

    def _create_pipeline(self, credential, **kwargs):
        self.credential_policy = None
        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")
        if hasattr(credential, "get_token"):
            self.credential_policy = AsyncBearerTokenCredentialPolicy(
                credential, "https://cognitiveservices.azure.com/.default"
            )
        elif isinstance(credential, six.string_types):
            self.credential_policy = CognitiveServicesCredentialPolicy(credential)
        elif credential is not None:
            raise TypeError("Unsupported credential: {}".format(credential))

        config = self._create_configuration(**kwargs)
        config.transport = kwargs.get("transport")  # type: ignore
        if not config.transport:
            try:
                from azure.core.pipeline.transport import AioHttpTransport
            except ImportError:
                raise ImportError("Unable to create async transport. Please check aiohttp is installed.")
            config.transport = AioHttpTransport(**kwargs)
        config.user_agent_policy.add_user_agent(
            'azsdk-python-azure-ai-textanalytics/{}'.format(VERSION)
        )

        policies = [
            config.headers_policy,
            config.user_agent_policy,
            RequestIdPolicy(**kwargs),
            config.proxy_policy,
            AsyncRedirectPolicy(**kwargs),
            AsyncRetryPolicy(**kwargs),
            self.credential_policy,
            config.logging_policy,
            AsyncTextAnalyticsResponseHook(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs)
        ]
        return AsyncPipeline(config.transport, policies=policies)

    def _create_configuration(self, **kwargs):  # pylint: disable=no-self-use
        config = Configuration(**kwargs)
        config.user_agent_policy = kwargs.get('user_agent_policy') or UserAgentPolicy(**kwargs)
        config.headers_policy = kwargs.get('headers_policy') or HeadersPolicy(**kwargs)
        config.proxy_policy = kwargs.get('proxy_policy') or ProxyPolicy(**kwargs)
        config.logging_policy = kwargs.get('logging_policy') or NetworkTraceLoggingPolicy(**kwargs)
        return config

    async def __aenter__(self):
        await self._client.__aenter__()  # pylint: disable=no-member
        return self

    async def __aexit__(self, *args):
        await self._client.__aexit__(*args)  # pylint: disable=no-member
