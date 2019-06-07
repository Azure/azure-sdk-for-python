# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from azure.core import Configuration
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpTransport
    from typing import Any, Mapping, Optional

from ._internal import _KeyVaultClientBase
from .keys._client import KeyClient
from .secrets._client import SecretClient


class VaultClient(_KeyVaultClientBase):
    def __init__(self, vault_url, credential, config=None, transport=None, api_version=None, **kwargs):
        # type: (str, TokenCredential, Configuration, Optional[HttpTransport], Optional[str], **Any) -> None
        super(VaultClient, self).__init__(
            vault_url, credential, config=config, transport=transport, api_version=api_version, **kwargs
        )
        self._secrets = SecretClient(self.vault_url, credential, generated_client=self._client, **kwargs)
        self._keys = KeyClient(self.vault_url, credential, generated_client=self._client, **kwargs)

    @property
    def secrets(self):
        """
        :rtype: ~azure.keyvault.secrets.SecretClient
        """
        return self._secrets

    @property
    def keys(self):
        """
        :rtype: ~azure.keyvault.keys.KeyClient
        """
        return self._keys

    # @property
    # def certificates(self):
    #     """
    #     :rtype: ~azure.keyvault.certificates.CertificateClient
    #     """
    #     pass
