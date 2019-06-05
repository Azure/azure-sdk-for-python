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
    from azure.core.credentials import SupportsGetToken
    from typing import Any, Mapping, Optional

from .keys._client import KeyClient
from .secrets._client import SecretClient


class VaultClient(object):
    def __init__(self, vault_url, credential, config=None, **kwargs):
        # type: (str, SupportsGetToken, Optional[Configuration], **Any) -> None
        self._vault_url = vault_url.strip(" /")
        self._secrets = SecretClient(self._vault_url, credential, config=config, **kwargs)
        self._keys = KeyClient(self._vault_url, credential, config=config, **kwargs)

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

    @property
    def vault_url(self):
        return self._vault_url
