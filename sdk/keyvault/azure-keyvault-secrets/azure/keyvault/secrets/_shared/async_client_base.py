# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Callable, Mapping, AsyncIterator, TYPE_CHECKING

from azure.core.configuration import Configuration
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import UserAgentPolicy
from azure.core.pipeline.policies.distributed_tracing import DistributedTracingPolicy
from azure.core.pipeline.transport import AsyncHttpTransport
from msrest.serialization import Model

from ._generated import KeyVaultClient
from . import AsyncChallengeAuthPolicy
from .._user_agent import USER_AGENT


if TYPE_CHECKING:
    try:
        from azure.core.credentials import TokenCredential
    except ImportError:
        # TokenCredential is a typing_extensions.Protocol; we don't depend on that package
        pass


class AsyncKeyVaultClientBase:
    """Base class for async Key Vault clients"""

    @staticmethod
    def _create_config(
        credential: "TokenCredential", api_version: str = None, **kwargs: Mapping[str, Any]
    ) -> Configuration:
        if api_version is None:
            api_version = KeyVaultClient.DEFAULT_API_VERSION
        config = KeyVaultClient.get_configuration_class(api_version, aio=True)(credential, **kwargs)
        config.authentication_policy = AsyncChallengeAuthPolicy(credential)

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

    def __init__(
        self,
        vault_url: str,
        credential: "TokenCredential",
        transport: AsyncHttpTransport = None,
        api_version: str = None,
        **kwargs: Any
    ) -> None:
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
        pipeline = kwargs.pop("pipeline", None) or self._build_pipeline(config, transport=transport, **kwargs)
        self._client = KeyVaultClient(credential, api_version=api_version, pipeline=pipeline, aio=True)

    @staticmethod
    def _build_pipeline(config: Configuration, transport: AsyncHttpTransport, **kwargs: Any) -> AsyncPipeline:
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
            from azure.core.pipeline.transport import AioHttpTransport

            transport = AioHttpTransport(**kwargs)

        return AsyncPipeline(transport, policies=policies)

    @property
    def vault_url(self) -> str:
        return self._vault_url
