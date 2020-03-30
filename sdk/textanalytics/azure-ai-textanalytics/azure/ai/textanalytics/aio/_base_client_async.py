# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any
from .._policies import CognitiveServicesCredentialPolicy
from ._policies_async import AsyncTextAnalyticsResponseHookPolicy
from .._generated.aio import TextAnalyticsClient
from .._user_agent import USER_AGENT


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


class AsyncTextAnalyticsClientBase(object):
    def __init__(self, endpoint, credential, **kwargs):
        self._client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=credential,
            sdk_moniker=USER_AGENT,
            authentication_policy=_authentication_policy(credential),
            custom_hook_policy=AsyncTextAnalyticsResponseHookPolicy(**kwargs),
            **kwargs
        )


    async def __aenter__(self) -> "AsyncTextAnalyticsClientBase":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        await self._client.__aexit__()
