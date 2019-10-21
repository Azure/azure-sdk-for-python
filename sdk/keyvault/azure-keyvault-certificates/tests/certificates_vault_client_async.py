# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, TYPE_CHECKING
from azure.core.pipeline.transport import HttpTransport

from azure.keyvault.certificates.aio import CertificateClient
from azure.keyvault.certificates._shared import AsyncKeyVaultClientBase

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
        vault_endpoint: str,
        credential: "TokenCredential",
        transport: HttpTransport = None,
        api_version: str = None,
        **kwargs: Any
    ) -> None:
        super(VaultClient, self).__init__(
            vault_endpoint, credential, transport=transport, api_version=api_version, **kwargs
        )
        self._certificates = CertificateClient(self.vault_endpoint, credential, generated_client=self._client, **kwargs)

    @property
    def certificates(self):
        return self._certificates
