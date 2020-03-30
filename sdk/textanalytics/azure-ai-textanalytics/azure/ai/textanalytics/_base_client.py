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
from ._policies import CognitiveServicesCredentialPolicy, TextAnalyticsResponseHookPolicy
from ._user_agent import USER_AGENT


def _authentication_policy(credential):
    credential_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "api_key"):
        credential_policy = CognitiveServicesCredentialPolicy(credential)
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError("Unsupported credential: {}. Use an instance of TextAnalyticsApiKeyCredential "
                        "or a token credential from azure.identity".format(type(credential)))
    return credential_policy


class TextAnalyticsClientBase(object):
    def __init__(self, endpoint, credential, aio, **kwargs):
        if aio:
            from ._generated.aio import TextAnalyticsClient as Client
            from .aio._policies_async import AsyncTextAnalyticsResponseHookPolicy as ResponseHookPolicy
        else:
            from ._generated import TextAnalyticsClient as Client
            from ._policies import TextAnalyticsResponseHookPolicy as ResponseHookPolicy
        self._client = Client(
            endpoint=endpoint,
            credential=credential,
            sdk_moniker=USER_AGENT,
            authentication_policy=_authentication_policy(credential),
            custom_hook_policy=ResponseHookPolicy(**kwargs)
        )


    def __enter__(self):
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)  # pylint:disable=no-member
