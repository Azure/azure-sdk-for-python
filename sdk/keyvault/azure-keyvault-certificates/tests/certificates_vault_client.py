# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

from azure.keyvault.certificates._shared import KeyVaultClientBase
from azure.keyvault.certificates import CertificateClient

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpTransport
    from typing import Any, Optional


class VaultClient(KeyVaultClientBase):
    def __init__(self, vault_url, credential, transport=None, api_version=None, **kwargs):
        # type: (str, TokenCredential, Optional[HttpTransport], Optional[str], **Any) -> None
        super(VaultClient, self).__init__(
            vault_url, credential, transport=transport, api_version=api_version, **kwargs
        )
        self._certificates = CertificateClient(self.vault_url, credential, generated_client=self._client, **kwargs)

    @property
    def certificates(self):
        """
        :rtype: ~azure.keyvault.certificates.CertificateClient
        """
        return self._certificates
