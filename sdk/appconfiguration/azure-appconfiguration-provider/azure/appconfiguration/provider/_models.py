# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import List, Optional, Callable, TYPE_CHECKING, Union, Awaitable

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.keyvault.secrets import SecretClient
    from azure.keyvault.secrets.aio import SecretClient as AsyncSecretClient


class AzureAppConfigurationKeyVaultOptions:
    def __init__(
            self,
            *,
            credential: Optional[Union["TokenCredential", "AsyncTokenCredential"]] = None,
            secret_clients: Optional[Union[List["SecretClient"], List["AsyncSecretClient"]]] = None,
            secret_resolver: Optional[Union[Callable[[str], str], Callable[[str], Awaitable[str]]]] = None
        ):
        """
        Options for connecting to Key Vault.

        :keyword credential: A credential for authenticating with the key vault. This is optional if secret_clients is
         provided.
        :paramtype credential: ~azure.core.credentials.TokenCredential
        :keyword secret_clients: A list of SecretClient from azure-keyvault-secrets. This is optional if credential is
         provided.
        :paramtype secret_clients: list[~azure.keyvault.secrets.SecretClient]
        :keyword secret_resolver: A function that takes a URI and returns a value.
        :paramtype secret_resolver: Callable[[str], str]
        """
        self.credential = credential
        self.secret_clients = secret_clients or []
        self.secret_resolver = secret_resolver
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

    def __init__(self, key_filter: str, label_filter: str = "\0"):
        self.key_filter = key_filter
        self.label_filter = label_filter
