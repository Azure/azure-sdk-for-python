# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Optional

from azure.core import Configuration
from azure.core.credentials import SupportsGetToken

from .keys._client import KeyClient
from .secrets._client import SecretClient


class VaultClient(object):
    def __init__(
        self, vault_url: str, credential: SupportsGetToken, config: Configuration = None, **kwargs: Any
    ) -> None:
        self.vault_url = vault_url
        self._secrets = SecretClient(vault_url, credential, config=config, **kwargs)
        self._keys = KeyClient(vault_url, credential, config=config, **kwargs)

    @property
    def secrets(self):
        """
        :rtype: ~azure.security.keyvault.aio.secrets.SecretClient
        """
        return self._secrets

    @property
    def keys(self):
        """
        :rtype:`azure.security.keyvault.aio.keys.KeyClient`
        """
        return self._keys

    # @property
    # def certificates(self):
    #     """
    #     :rtype: ~azure.keyvault.aio.certificates.CertificateClient`
    #     """
    #     pass
