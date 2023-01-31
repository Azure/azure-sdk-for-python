# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import overload, List, Optional, Callable
from azure.keyvault.secrets import SecretClient

class AzureAppConfigurationKeyVaultOptions:

    @overload
    def __init__(self,  credential, *, secret_clients: Optional[List[SecretClient]] = None):
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

    def __init__(self, **kwargs):
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
        if self.credential is not None and self.secret_resolver is not None:
            raise ValueError("credential and secret_resolver can't both be configured.")

class SettingSelector:
    """
    Selects a set of configuration settings from Azure App Configuration.

    :param key_filter: A filter to select configuration settings based on their keys.
    :type key_filter: str
    :param label_filter: A filter to select configuration settings based on their labels. Default is value is '\0'
    :type label_filter: str
    """

    def __init__(self, key_filter: str, label_filter:str="\0"):
        self.key_filter = key_filter
        self.label_filter = label_filter
