# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from azure.core.credentials import TokenCredential
    except ImportError:
        # TokenCredential is a typing_extensions.Protocol; we don't depend on that package
        pass

from azure.core import Configuration
from azure.core.pipeline.transport import HttpTransport

from ._internal import _AsyncKeyVaultClientBase
from .keys._client import KeyClient
from .secrets._client import SecretClient


class VaultClient(_AsyncKeyVaultClientBase):
    """VaultClient is a high-level interface for managing a vault's resources.

    Example:
        .. literalinclude:: ../tests/test_examples_vault_client.py
            :start-after: [START create_async_vault_client]
            :end-before: [END create_async_vault_client]
            :language: python
            :dedent: 4
            :caption: Creates a new instance of VaultClient

    """

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
        self._secrets = SecretClient(self.vault_url, credential, generated_client=self._client, **kwargs)
        self._keys = KeyClient(self.vault_url, credential, generated_client=self._client, **kwargs)

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
