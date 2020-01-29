# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

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
from ._credential import TextAnalyticsApiKeyCredential
from ._user_agent import USER_AGENT


class TextAnalyticsClientBase(object):
    def __init__(self, credential, **kwargs):
        self._pipeline = self._create_pipeline(credential, **kwargs)

    def _create_pipeline(self, credential, **kwargs):
        credential_policy = None
        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")
        if hasattr(credential, "get_token"):
            credential_policy = BearerTokenCredentialPolicy(
                credential, "https://cognitiveservices.azure.com/.default"
            )
        elif isinstance(credential, TextAnalyticsApiKeyCredential):
            credential_policy = CognitiveServicesCredentialPolicy(credential)
        elif credential is not None:
            raise TypeError("Unsupported credential: {}. Use an instance of TextAnalyticsApiKeyCredential "
                            "or a token credential from azure.identity".format(type(credential)))

        config = self._create_configuration(**kwargs)
        config.transport = kwargs.get("transport")  # type: ignore
        if not config.transport:
            config.transport = RequestsTransport(**kwargs)

        policies = [
            config.headers_policy,
            config.user_agent_policy,
            RequestIdPolicy(**kwargs),
            config.proxy_policy,
            config.redirect_policy,
            config.retry_policy,
            credential_policy,
            config.logging_policy,
            TextAnalyticsResponseHook(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]
        return Pipeline(config.transport, policies=policies)

    def _create_configuration(self, **kwargs):  # pylint: disable=no-self-use
        config = Configuration(**kwargs)
        config.user_agent_policy = kwargs.get("user_agent_policy") or \
            UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)
        config.headers_policy = kwargs.get("headers_policy") or HeadersPolicy(**kwargs)
        config.proxy_policy = kwargs.get("proxy_policy") or ProxyPolicy(**kwargs)
        config.logging_policy = kwargs.get("logging_policy") or NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = kwargs.get("retry_policy") or RetryPolicy(**kwargs)
        config.redirect_policy = kwargs.get("redirect_policy") or RedirectPolicy(**kwargs)

        return config

    def __enter__(self):
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)  # pylint:disable=no-member
