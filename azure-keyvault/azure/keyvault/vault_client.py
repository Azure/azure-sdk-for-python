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
        :rtype:`azure.security.keyvault.SecretClient`
        """
        return self._secrets

    @property
    def keys(self):
        """
        :rtype:`azure.security.keyvault.KeyClient`
        """
        return self._keys

    @property
    def certificates(self):
        """
        :rtype:`azure.security.keyvault.CertificateClient`
        """
        pass

    @property
    def vault_url(self):
        return self._vault_url
