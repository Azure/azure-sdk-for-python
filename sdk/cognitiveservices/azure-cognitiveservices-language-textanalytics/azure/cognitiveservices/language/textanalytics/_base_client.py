# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import six
from azure.core.configuration import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RequestIdPolicy,
    ProxyPolicy,
    NetworkTraceLoggingPolicy,
    RetryPolicy,
    RedirectPolicy,
    BearerTokenCredentialPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
)
from ._policies import CognitiveServicesCredentialPolicy, TextAnalyticsResponseHook
from ._version import VERSION


class TextAnalyticsClientBase(object):
    def __init__(self, credentials, **kwargs):
        self._pipeline = self._create_pipeline(credentials, **kwargs)

    def _create_pipeline(self, credentials, **kwargs):
        credential_policy = None
        if hasattr(credentials, "get_token"):
            credential_policy = BearerTokenCredentialPolicy(
                credentials, "https://cognitiveservices.azure.com/.default"
            )
        elif isinstance(credentials, six.string_types):
            credential_policy = CognitiveServicesCredentialPolicy(credentials, **kwargs)
        elif credentials is not None:
            raise TypeError("Unsupported credential: {}".format(credentials))

        config = self.create_configuration(**kwargs)
        config.transport = kwargs.get("transport")  # type: ignore
        if not config.transport:
            config.transport = RequestsTransport(**kwargs)
        config.user_agent_policy.add_user_agent(
            "azsdk-python-textanalyticsclient/{}".format(VERSION)
        )

        policies = [
            config.headers_policy,
            config.user_agent_policy,
            RequestIdPolicy(**kwargs),
            config.proxy_policy,
            credential_policy,
            config.redirect_policy,
            config.retry_policy,
            config.logging_policy,
            TextAnalyticsResponseHook(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]
        return Pipeline(config.transport, policies=policies)

    def create_configuration(self, **kwargs):
        config = Configuration(**kwargs)
        config.user_agent_policy = kwargs.get("user_agent_policy") or UserAgentPolicy(**kwargs)
        config.headers_policy = kwargs.get("headers_policy") or HeadersPolicy(**kwargs)
        config.proxy_policy = kwargs.get("proxy_policy") or ProxyPolicy(**kwargs)
        config.logging_policy = kwargs.get("logging_policy") or NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = kwargs.get("retry_policy") or RetryPolicy(**kwargs)
        config.redirect_policy = kwargs.get("redirect_policy") or RedirectPolicy(**kwargs)

        return config

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)
