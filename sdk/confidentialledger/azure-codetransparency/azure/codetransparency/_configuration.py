# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import TYPE_CHECKING

from azure.core.configuration import Configuration
from azure.core.pipeline import policies

from ._version import VERSION

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials import TokenCredential


class CodeTransparencyClientConfiguration(Configuration):
    """Configuration for CodeTransparencyClient.

    :param endpoint: The Code Transparency Service endpoint.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential
    """

    def __init__(
        self,
        endpoint: str,
        credential: "TokenCredential",
        **kwargs: "Any"
    ) -> None:
        super(CodeTransparencyClientConfiguration, self).__init__(**kwargs)
        if endpoint is None:
            raise ValueError("Parameter 'endpoint' must not be None.")
        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")

        self.endpoint = endpoint
        self.credential = credential
        self.api_version = kwargs.pop("api_version", "2024-01-11-preview")
        self.credential_scopes = kwargs.pop("credential_scopes", ["https://cognitiveservices.azure.com/.default"])
        kwargs.setdefault("sdk_moniker", "azure-codetransparency/{}".format(VERSION))
        self._configure(**kwargs)

    def _configure(
        self,
        **kwargs: "Any"
    ) -> None:
        self.user_agent_policy = kwargs.get("user_agent_policy") or policies.UserAgentPolicy(**kwargs)
        self.headers_policy = kwargs.get("headers_policy") or policies.HeadersPolicy(**kwargs)
        self.proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)
        self.logging_policy = kwargs.get("logging_policy") or policies.NetworkTraceLoggingPolicy(**kwargs)
        self.http_logging_policy = kwargs.get("http_logging_policy") or policies.HttpLoggingPolicy(**kwargs)
        self.retry_policy = kwargs.get("retry_policy") or policies.RetryPolicy(**kwargs)
        self.custom_hook_policy = kwargs.get("custom_hook_policy") or policies.CustomHookPolicy(**kwargs)
        self.redirect_policy = kwargs.get("redirect_policy") or policies.RedirectPolicy(**kwargs)
        self.authentication_policy = kwargs.get("authentication_policy")
        if self.credential and not self.authentication_policy:
            self.authentication_policy = policies.BearerTokenCredentialPolicy(
                self.credential, *self.credential_scopes, **kwargs
            )