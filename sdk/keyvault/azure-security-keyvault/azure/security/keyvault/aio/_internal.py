# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Callable, Mapping, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from azure.core.credentials import TokenCredential
    except ImportError:
        # TokenCredential is a typing_extensions.Protocol; we don't depend on that package
        pass

from azure.core.async_paging import AsyncPagedMixin
from azure.core.configuration import Configuration
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.pipeline.transport import AsyncioRequestsTransport, HttpTransport
from msrest.serialization import Model

from .._generated import KeyVaultClient
from .._internal import KEY_VAULT_SCOPE


class AsyncPagingAdapter:
    """For each item in an AsyncPagedMixin, returns the result of applying fn to that item.
    Python 3.6 added syntax that could replace this (yield within async for)."""

    def __init__(self, pages: AsyncPagedMixin, fn: Callable[[Model], Any]) -> None:
        self._pages = pages
        self._fn = fn

    def __aiter__(self):
        return self

    async def __anext__(self) -> Any:
        item = await self._pages.__anext__()
        if not item:
            raise StopAsyncIteration
        return self._fn(item)


class _AsyncKeyVaultClientBase:
    """
    :param credential:  A credential or credential provider which can be used to authenticate to the vault,
        a ValueError will be raised if the entity is not provided
    :type credential: azure.authentication.Credential or azure.authentication.CredentialProvider
    :param str vault_url: The url of the vault to which the client will connect,
        a ValueError will be raised if the entity is not provided
    :param ~azure.core.configuration.Configuration config:  The configuration for the SecretClient
    """

    @staticmethod
    def create_config(
        credential: "TokenCredential", api_version: str = None, **kwargs: Mapping[str, Any]
    ) -> Configuration:
        if api_version is None:
            api_version = KeyVaultClient.DEFAULT_API_VERSION
        config = KeyVaultClient.get_configuration_class(api_version, aio=True)(credential, **kwargs)
        config.authentication_policy = AsyncBearerTokenCredentialPolicy(credential, KEY_VAULT_SCOPE)
        return config

    def __init__(
        self,
        vault_url: str,
        credential: "TokenCredential",
        config: Configuration = None,
        transport: HttpTransport = None,
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

        config = config or self.create_config(credential, api_version=api_version, **kwargs)
        pipeline = kwargs.pop("pipeline", None) or self._build_pipeline(config, transport=transport)
        self._client = KeyVaultClient(credential, api_version=api_version, pipeline=pipeline, aio=True)

    @staticmethod
    def _build_pipeline(config: Configuration, transport: HttpTransport) -> AsyncPipeline:
        policies = [
            config.headers_policy,
            config.user_agent_policy,
            config.proxy_policy,
            config.redirect_policy,
            config.retry_policy,
            config.authentication_policy,
            config.logging_policy,
        ]

        if transport is None:
            transport = AsyncioRequestsTransport(config)

        return AsyncPipeline(transport, policies=policies)

    @property
    def vault_url(self) -> str:
        return self._vault_url
