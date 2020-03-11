# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.pipeline import AsyncPipeline

from . import AsyncChallengeAuthPolicy
from .client_base import _get_policies
from .multi_api import load_generated_api

if TYPE_CHECKING:
    try:
        # pylint:disable=unused-import
        from typing import Any
        from azure.core.configuration import Configuration
        from azure.core.pipeline.transport import AsyncHttpTransport
        from azure.core.credentials_async import AsyncTokenCredential
    except ImportError:
        # AsyncTokenCredential is a typing_extensions.Protocol; we don't depend on that package
        pass


def _build_pipeline(config: "Configuration", transport: "AsyncHttpTransport" = None, **kwargs: "Any") -> AsyncPipeline:
    policies = _get_policies(config, **kwargs)
    if transport is None:
        from azure.core.pipeline.transport import AioHttpTransport

        transport = AioHttpTransport(**kwargs)

    return AsyncPipeline(transport, policies=policies)


class AsyncKeyVaultClientBase(object):
    def __init__(self, vault_url: str, credential: "AsyncTokenCredential", **kwargs: "Any") -> None:
        if not credential:
            raise ValueError(
                "credential should be an object supporting the AsyncTokenCredential protocol, "
                "such as a credential from azure-identity"
            )
        if not vault_url:
            raise ValueError("vault_url must be the URL of an Azure Key Vault")

        self._vault_url = vault_url.strip(" /")
        client = kwargs.get("generated_client")
        if client:
            # caller provided a configured client -> nothing left to initialize
            self._client = client
            return

        api_version = kwargs.pop("api_version", None)
        generated = load_generated_api(api_version, aio=True)

        pipeline = kwargs.pop("pipeline", None)
        if not pipeline:
            config = generated.config_cls(credential, **kwargs)
            config.authentication_policy = AsyncChallengeAuthPolicy(credential)
            pipeline = _build_pipeline(config, **kwargs)

        # generated clients don't use their credentials parameter
        self._client = generated.client_cls(credentials="", pipeline=pipeline)
        self._models = generated.models

    @property
    def vault_url(self) -> str:
        return self._vault_url

    async def __aenter__(self) -> "AsyncKeyVaultClientBase":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close sockets opened by the client.

        Calling this method is unnecessary when using the client as a context manager.
        """
        await self._client.__aexit__()
