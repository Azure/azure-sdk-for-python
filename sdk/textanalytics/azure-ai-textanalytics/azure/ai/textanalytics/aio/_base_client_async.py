# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Union
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, HttpLoggingPolicy
from .._generated.aio import TextAnalyticsClient as _TextAnalyticsClient
from .._policies import TextAnalyticsResponseHookPolicy, QuotaExceededPolicy
from .._user_agent import USER_AGENT
from .._version import DEFAULT_API_VERSION


def _authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(
            name="Ocp-Apim-Subscription-Key", credential=credential
        )
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError(
            "Unsupported credential: {}. Use an instance of AzureKeyCredential "
            "or a token credential from azure.identity".format(type(credential))
        )
    return authentication_policy


class AsyncTextAnalyticsClientBase:
    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        **kwargs: Any
    ) -> None:
        http_logging_policy = HttpLoggingPolicy(**kwargs)
        http_logging_policy.allowed_header_names.update(
            {
                "Operation-Location",
                "apim-request-id",
                "x-envoy-upstream-service-time",
                "Strict-Transport-Security",
                "x-content-type-options",
            }
        )
        http_logging_policy.allowed_query_params.update(
            {
                "model-version",
                "showStats",
                "loggingOptOut",
                "domain",
                "stringIndexType",
                "piiCategories",
                "$top",
                "$skip",
                "opinionMining",
                "api-version"
            }
        )
        try:
            endpoint = endpoint.rstrip("/")
        except AttributeError:
            raise ValueError("Parameter 'endpoint' must be a string.")
        self._client = _TextAnalyticsClient(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            api_version=kwargs.pop("api_version", DEFAULT_API_VERSION),
            sdk_moniker=USER_AGENT,
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            custom_hook_policy=kwargs.pop("custom_hook_policy", TextAnalyticsResponseHookPolicy(**kwargs)),
            http_logging_policy=kwargs.pop("http_logging_policy", http_logging_policy),
            per_retry_policies=kwargs.get("per_retry_policies", QuotaExceededPolicy()),
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
