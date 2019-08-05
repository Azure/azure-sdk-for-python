# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.pipeline.transport import RequestsTransport
from azure.core.pipeline.policies.distributed_tracing import DistributedTracingPolicy
from ._generated import KeyVaultClient

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Mapping, Optional
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpTransport

from .challenge_auth_policy import ChallengeAuthPolicy
from .._user_agent import USER_AGENT


KEY_VAULT_SCOPE = "https://vault.azure.net/.default"


class KeyVaultClientBase(object):
    """Base class for Key Vault clients"""

    @staticmethod
    def _create_config(credential, api_version=None, **kwargs):
        # type: (TokenCredential, Optional[str], Mapping[str, Any]) -> Configuration
        if api_version is None:
            api_version = KeyVaultClient.DEFAULT_API_VERSION
        config = KeyVaultClient.get_configuration_class(api_version, aio=False)(credential, **kwargs)
        config.authentication_policy = ChallengeAuthPolicy(credential)

        # replace the autorest-generated UserAgentPolicy and its hard-coded user agent
        # https://github.com/Azure/azure-sdk-for-python/issues/6637
        config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)

        # Override config policies if found in kwargs
        if "user_agent_policy" in kwargs:
            config.user_agent_policy = kwargs["user_agent_policy"]
        if "headers_policy" in kwargs:
            config.headers_policy = kwargs["headers_policy"]
        if "proxy_policy" in kwargs:
            config.proxy_policy = kwargs["proxy_policy"]
        if "logging_policy" in kwargs:
            config.logging_policy = kwargs["logging_policy"]
        if "retry_policy" in kwargs:
            config.retry_policy = kwargs["retry_policy"]
        if "custom_hook_policy" in kwargs:
            config.custom_hook_policy = kwargs["custom_hook_policy"]
        if "redirect_policy" in kwargs:
            config.redirect_policy = kwargs["redirect_policy"]

        return config

    def __init__(self, vault_url, credential, transport=None, api_version=None, **kwargs):
        # type: (str, TokenCredential, Optional[HttpTransport], Optional[str], **Any) -> None
        if not credential:
            raise ValueError(
                "credential should be an object supporting the TokenCredential protocol, such as a credential from azure-identity"
            )
        if not vault_url:
            raise ValueError("vault_url must be the URL of an Azure Key Vault")

        self._vault_url = vault_url.strip(" /")

        client = kwargs.pop("generated_client", None)
        if client:
            # caller provided a configured client -> nothing left to initialize
            self._client = client
            return

        if api_version is None:
            api_version = KeyVaultClient.DEFAULT_API_VERSION

        config = self._create_config(credential, api_version=api_version, **kwargs)
        pipeline = kwargs.pop("pipeline", None) or self._build_pipeline(config, transport, **kwargs)
        self._client = KeyVaultClient(credential, api_version=api_version, pipeline=pipeline, aio=False, **kwargs)

    def _build_pipeline(self, config, transport, **kwargs):
        # type: (Configuration, HttpTransport) -> Pipeline
        policies = [
            config.headers_policy,
            config.user_agent_policy,
            config.proxy_policy,
            config.redirect_policy,
            config.retry_policy,
            config.authentication_policy,
            config.logging_policy,
            DistributedTracingPolicy(),
        ]

        if transport is None:
            transport = RequestsTransport(**kwargs)

        return Pipeline(transport, policies=policies)

    @property
    def vault_url(self):
        # type: () -> str
        return self._vault_url
