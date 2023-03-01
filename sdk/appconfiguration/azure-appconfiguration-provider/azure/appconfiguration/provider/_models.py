# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Optional, Callable, TYPE_CHECKING, Union, Awaitable, Mapping, Any
from ._constants import EMPTY_LABEL

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.credentials_async import AsyncTokenCredential


class AzureAppConfigurationKeyVaultOptions:
    def __init__(
            self,
            *,
            credential: Optional[Union["TokenCredential", "AsyncTokenCredential"]] = None,
            client_configs: Optional[Mapping[str, Mapping[str, Any]]] = None,
            secret_resolver: Optional[Union[Callable[[str], str], Callable[[str], Awaitable[str]]]] = None
        ):
        """
        Options for connecting to Key Vault.

        :keyword credential: A credential for authenticating with the key vault. This is optional if secret_clients is
         provided.
        :paramtype credential: ~azure.core.credentials.TokenCredential
        :keyword client_configs: A Mapping of SecretClient endpoints to client configurations from azure-keyvault-secrets. 
         This is optional if credential is provided. If a credential isn't provided a credential will need to be in each set for each.
        :paramtype client_configs: Mapping[Url, Mapping]
        :keyword secret_resolver: A function that takes a URI and returns a value.
        :paramtype secret_resolver: Callable[[str], str]
        """
        self.credential = credential
        self.client_configs = client_configs or {}
        self.secret_resolver = secret_resolver
        if self.credential is not None and self.secret_resolver is not None:
            raise ValueError("credential and secret_resolver can't both be configured.")


class SettingSelector:
    """
    Selects a set of configuration settings from Azure App Configuration.

    :keyword key_filter: A filter to select configuration settings based on their keys.
    :type key_filter: str
    :keyword label_filter: A filter to select configuration settings based on their labels. Default is value is EMPTY_LABEL 
     i.e. (No Label) as seen in the portal.
    :type label_filter: Optional[str]
    """

    def __init__(self, *, key_filter: str, label_filter: Optional[str] = EMPTY_LABEL, **kwargs):
        self.key_filter = key_filter
        self.label_filter = label_filter
