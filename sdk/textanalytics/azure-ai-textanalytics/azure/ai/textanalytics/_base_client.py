# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Union, Any, Optional
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, HttpLoggingPolicy
from azure.core.credentials import AzureKeyCredential, TokenCredential
from ._generated import TextAnalyticsClient as _TextAnalyticsClient
from ._policies import TextAnalyticsResponseHookPolicy, QuotaExceededPolicy
from ._user_agent import USER_AGENT
from ._version import DEFAULT_API_VERSION


class TextAnalyticsApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Cognitive Service for Language or Text Analytics API versions supported by this package"""

    #: This is the default version and corresponds to the Cognitive Service for Language API.
    V2023_04_01 = "2023-04-01"
    #: This version corresponds to the Cognitive Service for Language API.
    V2022_05_01 = "2022-05-01"
    #: This version corresponds to Text Analytics API.
    V3_1 = "v3.1"
    #: This version corresponds to Text Analytics API.
    V3_0 = "v3.0"


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


class TextAnalyticsClientBase:
    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, TokenCredential],
        *,
        api_version: Optional[Union[str, TextAnalyticsApiVersion]] = None,
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
                "warn-code",
                "warn-agent",
                "warn-text",
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
        except AttributeError as exc:
            raise ValueError("Parameter 'endpoint' must be a string.") from exc

        self._api_version = api_version if api_version is not None else DEFAULT_API_VERSION
        if hasattr(self._api_version, "value"):
            self._api_version = self._api_version.value  # type: ignore
        self._client = _TextAnalyticsClient(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            api_version=self._api_version,
            sdk_moniker=USER_AGENT,
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            custom_hook_policy=kwargs.pop("custom_hook_policy", TextAnalyticsResponseHookPolicy(**kwargs)),
            http_logging_policy=kwargs.pop("http_logging_policy", http_logging_policy),
            per_retry_policies=kwargs.get("per_retry_policies", QuotaExceededPolicy()),
            **kwargs
        )

    def __enter__(self):
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self) -> None:
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        self._client.close()
