# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# from .keys._client import KeyClient
from .secrets._client import SecretClient


class VaultClient(object):

    def __init__(self, vault_url, credentials, config=None, **kwargs):
        self.vault_url = vault_url
        self._secrets = SecretClient(vault_url, credentials, config=config, **kwargs)
        # self._keys = KeyClient(vault_url, credentials, config=config, **kwargs)

    @property
    def secrets(self):
        """
        :rtype: ~azure.keyvault.aio.secrets.SecretClient
        """
        return self._secrets

    # @property
    # def keys(self):
    #     """
    #     :rtype:`azure.security.keyvault.KeyClient`
    #     """
    #     return self._keys

    @property
    def certificates(self):
        """
        :rtype: ~azure.keyvault.aio.certificates.CertificateClient`
        """
        pass
