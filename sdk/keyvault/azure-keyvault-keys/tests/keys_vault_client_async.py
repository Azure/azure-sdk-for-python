# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Callable, Mapping, TYPE_CHECKING
from azure.core.async_paging import AsyncPagedMixin
from azure.core.configuration import Configuration
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.pipeline.transport import AsyncioRequestsTransport, HttpTransport
from msrest.serialization import Model

from azure.keyvault.keys.aio import KeyClient
from azure.keyvault.keys._shared import AsyncKeyVaultClientBase

if TYPE_CHECKING:
    try:
        from azure.core.credentials import TokenCredential
    except ImportError:
        # TokenCredential is a typing_extensions.Protocol; we don't depend on that package
        pass

KEY_VAULT_SCOPE = "https://vault.azure.net/.default"


class VaultClient(AsyncKeyVaultClientBase):
    def __init__(
        self,
        vault_url: str,
        credential: "TokenCredential",
        config: Configuration = None,
        transport: HttpTransport = None,
        api_version: str = None,
        **kwargs: Any
    ) -> None:
        super(VaultClient, self).__init__(
            vault_url, credential, config=config, transport=transport, api_version=api_version, **kwargs
        )
        self._keys = KeyClient(self.vault_url, credential, generated_client=self._client, **kwargs)

    @property
    def keys(self):
        return self._keys
