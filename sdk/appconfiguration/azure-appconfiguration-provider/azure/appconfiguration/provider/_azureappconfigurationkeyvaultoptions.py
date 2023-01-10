# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import overload, List, Optional, Callable
from azure.core.credentials import TokenCredential
from azure.keyvault.secrets import SecretClient

class AzureAppConfigurationKeyVaultOptions:

    @overload
    def __init__(self,  credential: TokenCredential, *, secret_clients: Optional[List[SecretClient]] = None):
        """
        Options for connecting to Key Vault.

        :param credential: A credential for authenticating with the key vault. This is optional if secret_clients is
        provided.
        :type credential: ~azure.core.credentials.TokenCredential
        :param secret_clients: A list of SecretClient from azure-keyvault-secrets. This is optional if credential is
        provided.
        :type secret_clients: list[~azure.keyvault.secrets.SecretClient]
        """
        ...

    @overload
    def __init__(self, secret_clients: List[SecretClient], * , secret_resolver: Optional[Callable[[str], str]] = None):
        """
        Options for connecting to Key Vault.

        :param secret_clients: A list of SecretClient from azure-keyvault-secrets. This is optional if credential is
        provided.
        :type secret_clients: list[~azure.keyvault.secrets.SecretClient]
        :param secret_resolver: A function that takes a URI and returns a value.
        :type secret_resolver: Callable[[str], str]
        """
        ...

    def __init__(self, *args, **kwargs):
        """
        Options for connecting to Key Vault.

        :param credential: A credential for authenticating with the key vault. This is optional if secret_clients is
        provided.
        :type credential: ~azure.core.credentials.TokenCredential
        :param secret_clients: A list of SecretClient from azure-keyvault-secrets. This is optional if credential is
        provided.
        :type secret_clients: list[~azure.keyvault.secrets.SecretClient]
        :param secret_resolver: A function that takes a URI and returns a value.
        :type secret_resolver: Callable[[str], str]
        """
        self.credential = kwargs.get("credential", None)
        self.secret_clients = kwargs.get("secret_clients", {})
        self.secret_resolver = kwargs.get("secret_resolver", None)
