# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Callable, Mapping, TYPE_CHECKING
from azure.core.configuration import Configuration
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.pipeline.transport import AsyncioRequestsTransport, HttpTransport
from msrest.serialization import Model

from azure.keyvault.secrets._shared import AsyncKeyVaultClientBase
from azure.keyvault.secrets.aio import SecretClient

if TYPE_CHECKING:
    try:
        from azure.core.credentials_async import AsyncTokenCredential
    except ImportError:
        # AsyncTokenCredential is a typing_extensions.Protocol; we don't depend on that package
        pass

KEY_VAULT_SCOPE = "https://vault.azure.net/.default"


class VaultClient(AsyncKeyVaultClientBase):
    def __init__(
        self,
        vault_url: str,
        credential: "AsyncTokenCredential",
        transport: HttpTransport = None,
        api_version: str = None,
        **kwargs: Any
    ) -> None:
        super(VaultClient, self).__init__(
            vault_url, credential, transport=transport, api_version=api_version, **kwargs
        )
        self._credential = credential
        self._secrets = SecretClient(self.vault_url, self._credential, generated_client=self._client, **kwargs)

    @property
    def secrets(self):
        return self._secrets

    @property
    def client(self):
        return self._client

    async def close(self):
        await self._client.close()
        await self._credential.close()
