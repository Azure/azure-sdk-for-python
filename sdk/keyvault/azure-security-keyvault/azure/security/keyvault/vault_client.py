# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from .keys._client import KeyClient
from .secrets._client import SecretClient


class VaultClient(object):
    def __init__(self, vault_url, credentials, config=None, **kwargs):
        self._vault_url = vault_url.strip(" /")
        self._secrets = SecretClient(self._vault_url, credentials, config=config, **kwargs)
        self._keys = KeyClient(self._vault_url, credentials, config=config, **kwargs)

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

    @property
    def certificates(self):
        """
        :rtype: ~azure.keyvault.certificates.CertificateClient
        """
        pass

    @property
    def vault_url(self):
        return self._vault_url
