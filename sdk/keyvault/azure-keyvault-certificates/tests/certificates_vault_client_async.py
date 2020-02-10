# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
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
        vault_url: str,
        credential: "TokenCredential",
        transport: HttpTransport = None,
        api_version: str = None,
        is_live: bool = True,
        **kwargs: Any
    ) -> None:
        super(VaultClient, self).__init__(vault_url, credential, transport=transport, api_version=api_version, **kwargs)
        self._certificates = CertificateClient(self.vault_url, credential, generated_client=self._client, **kwargs)

        if not is_live:
            # ensure pollers don't sleep during playback
            self._certificates.create_certificate = functools.partial(
                self._certificates.create_certificate, _polling_interval=0
            )
            self._certificates.delete_certificate = functools.partial(
                self._certificates.delete_certificate, _polling_interval=0
            )
            self._certificates.recover_deleted_certificate = functools.partial(
                self._certificates.recover_deleted_certificate, _polling_interval=0
            )

    @property
    def certificates(self):
        return self._certificates
