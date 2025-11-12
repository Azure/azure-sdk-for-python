# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Optional, Callable, TYPE_CHECKING, Union, Awaitable, Mapping, Any, NamedTuple, List
from ._constants import NULL_CHAR

# Error message constants for SettingSelector validation
_SNAPSHOT_PARAMETER_CONFLICT_ERROR = (
    "Cannot specify both snapshot_name and {parameter}. "
    "When using snapshots, all other filtering parameters are ignored."
)
_SELECTOR_REQUIRED_ERROR = "Either key_filter or snapshot_name must be specified."

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.credentials_async import AsyncTokenCredential


class AzureAppConfigurationKeyVaultOptions:
    def __init__(
        self,
        *,
        credential: Optional[Union["TokenCredential", "AsyncTokenCredential"]] = None,
        client_configs: Optional[Mapping[str, Mapping[str, Any]]] = None,
        secret_resolver: Optional[Union[Callable[[str], str], Callable[[str], Awaitable[str]]]] = None,
    ):
        """
        Options for connecting to Key Vault.

        :keyword credential: A credential for authenticating with the key vault. This is optional if secret_clients is
         provided.
        :paramtype credential: ~azure.core.credentials.TokenCredential
        :keyword client_configs: A Mapping of SecretClient endpoints to client configurations from
         azure-keyvault-secrets. This is optional if credential is provided. If a credential isn't provided a
         credential will need to be in each set for each.
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

    :keyword key_filter: A filter to select configuration settings and feature flags based on their keys.
     Cannot be used with snapshot_name.
    :type key_filter: str
    :keyword label_filter: A filter to select configuration settings and feature flags based on their labels. Default
     value is \0 i.e. (No Label) as seen in the portal. Cannot be used with snapshot_name.
    :type label_filter: Optional[str]
    :keyword tag_filters: A filter to select configuration settings and feature flags based on their tags. This is a
     list of strings that will be used to match tags on the configuration settings. Reserved characters (\\*, \\, ,)
     must be escaped with backslash if they are part of the value. Tag filters must follow the format
     "tagName=tagValue", for empty values use "tagName=" and for null values use "tagName=\\0".
     Cannot be used with snapshot_name.
    :type tag_filters: Optional[List[str]]
    :keyword snapshot_name: The name of the snapshot to load configuration settings from. When specified,
     all configuration settings from the snapshot will be loaded. Cannot be used with key_filter, label_filter,
     or tag_filters.
    :type snapshot_name: Optional[str]
    """

    def __init__(
        self,
        *,
        key_filter: Optional[str] = None,
        label_filter: Optional[str] = NULL_CHAR,
        tag_filters: Optional[List[str]] = None,
        snapshot_name: Optional[str] = None,
    ):
        if snapshot_name is not None:
            # When using snapshots, no other filtering parameters should be specified
            if key_filter is not None:
                raise ValueError(_SNAPSHOT_PARAMETER_CONFLICT_ERROR.format(parameter="key_filter"))
            if label_filter != NULL_CHAR:
                raise ValueError(_SNAPSHOT_PARAMETER_CONFLICT_ERROR.format(parameter="label_filter"))
            if tag_filters is not None:
                raise ValueError(_SNAPSHOT_PARAMETER_CONFLICT_ERROR.format(parameter="tag_filters"))

        if snapshot_name is None and key_filter is None:
            raise ValueError(_SELECTOR_REQUIRED_ERROR)

        if tag_filters is not None:
            if not isinstance(tag_filters, list):
                raise TypeError("tag_filters must be a list of strings.")
            for tag in tag_filters:
                if not tag:
                    raise ValueError("Tag filter cannot be an empty string or None.")
                if not isinstance(tag, str) or "=" not in tag or tag.startswith("="):
                    raise ValueError("Tag filter " + tag + ' does not follow the format "tagName=tagValue".')

        self.key_filter = key_filter
        self.label_filter = label_filter
        self.tag_filters = tag_filters
        self.snapshot_name = snapshot_name


class WatchKey(NamedTuple):
    key: str
    label: str = NULL_CHAR
