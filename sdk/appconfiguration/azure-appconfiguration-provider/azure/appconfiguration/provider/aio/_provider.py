# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Dict, Iterable, List, Optional, overload
import json

from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.keyvault.secrets import SecretClient, KeyVaultSecretIdentifier
from azure.core.exceptions import ResourceNotFoundError
from azure.core.credentials_async import AsyncTokenCredential

from .._settingselector import SettingSelector
from .._azureappconfigurationkeyvaultoptions import AzureAppConfigurationKeyVaultOptions
from .._azure_appconfiguration_provider_error import KeyVaultReferenceError
from .._constants import KEY_VAULT_REFERENCE_CONTENT_TYPE

from .._user_agent import USER_AGENT


@overload
async def load_provider(
        endpoint: str,
        credential: AsyncTokenCredential,
        *,
        selects: Optional[SettingSelector] = None,
        trim_prefixes: Optional[List[str]] = None,
        key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
        **kwargs
    ) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :param str endpoint: Endpoint
    :param credential: Credential
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword selects: List of setting selectors to filter configuration settings
    :paramtype selects: list[~azure.appconfigurationprovider.SettingSelector]
    :keyword trim_prefixes: List of prefixes to trim from configuration keys
    :paramtype trim_prefixes: list[str]
    :keyword key_vault_options: Options for resolving Key Vault references
    :paramtype key_vault_options: ~azure.appconfigurationprovider.KeyVaultOptions
    """
    ...

@overload
async def load_provider(
        connection_string: str,
        *,
        selects: Optional[SettingSelector] = None,
        trim_prefixes: Optional[List[str]] = None,
        key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
        **kwargs
    ) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :param str connection_string: Connection string
    :keyword selects: List of setting selectors to filter configuration settings
    :paramtype selects: list[~azure.appconfigurationprovider.SettingSelector]
    :keyword trim_prefixes: List of prefixes to trim from configuration keys
    :paramtype trim_prefixes: list[str]
    :keyword key_vault_options: Options for resolving Key Vault references
    :paramtype key_vault_options: ~azure.appconfigurationprovider.KeyVaultOptions
    """
    ...

async def load_provider(*args, **kwargs):
    key_vault_options = kwargs.pop("key_vault_options", None)
    selects = kwargs.pop("selects", {SettingSelector("*", "\0")})
    trim_prefixes = sorted(kwargs.pop("trimmed_key_prefixes", []), key=len, reverse=True)

    if len(args) == 1:
        client = _buildprovider(connection_string=args[0], key_vault_options=key_vault_options)
    else:
        client = _buildprovider(endpoint=args[0], credential=args[1], key_vault_options=key_vault_options)
    provider = AzureAppConfigurationProvider(client, trim_prefixes=trim_prefixes)

    secret_clients = key_vault_options.secret_clients if key_vault_options else {}
    for select in selects:
        configurations = await client.list_configuration_settings(
            key_filter=select.key_filter, label_filter=select.label_filter
        )
        for config in configurations:
            trimmed_key = config.key
            # Trim the key if it starts with one of the prefixes provided
            for trim in trim_prefixes:
                if config.key.startswith(trim):
                    trimmed_key = config.key[len(trim) :]
                    break

            if config.content_type == KEY_VAULT_REFERENCE_CONTENT_TYPE:
                secret = await _resolve_keyvault_reference(config, key_vault_options, secret_clients)
                provider._dict[trimmed_key] = secret
            elif _is_json_content_type(config.content_type):
                try:
                    j_object = json.loads(config.value)
                    provider._dict[trimmed_key] = j_object
                except json.JSONDecodeError:
                    # If the value is not a valid JSON, treat it like regular string value
                    provider._dict[trimmed_key] = config.value
            else:
                provider._dict[trimmed_key] = config.value
    return provider

def _buildprovider(connection_string=None, endpoint=None, credential=None, key_vault_options=None):
    headers = {}
    correlation_context = "RequestType=Startup"

    if key_vault_options and (
        key_vault_options.credential or key_vault_options.secret_clients or key_vault_options.secret_resolver
    ):
        correlation_context += ",UsesKeyVault"

    headers["Correlation-Context"] = correlation_context
    useragent = USER_AGENT

    if connection_string and endpoint:
        raise ValueError("Both connection_string and endpoint are set. Only one of these should be set.")
    if connection_string:
        return AzureAppConfigurationClient.from_connection_string(
            connection_string, user_agent=useragent, headers=headers
        )
        return
    return AzureAppConfigurationClient(endpoint, credential, user_agent=useragent, headers=headers)

async def _resolve_keyvault_reference(config, key_vault_options, secret_clients):
    if key_vault_options is None:
        raise AttributeError("Key Vault options must be set to resolve Key Vault references.")

    if config.secret_id is None:
        raise AttributeError("Key Vault reference must have a uri value.")

    key_vault_identifier = KeyVaultSecretIdentifier(config.secret_id)

    referenced_client = next(
        (client for client in secret_clients if client.vault_url == key_vault_identifier.vault_url), None
    )

    if referenced_client is None and key_vault_options.credential is not None:
        referenced_client = SecretClient(
            vault_url=key_vault_identifier.vault_url, credential=key_vault_options.credential
        )
        secret_clients[key_vault_identifier.vault_url] = referenced_client

    if referenced_client:
        try:
            return await referenced_client.get_secret(
                key_vault_identifier.name, version=key_vault_identifier.version
            ).value
        except ResourceNotFoundError:
            raise KeyVaultReferenceError(
                "Key Vault %s does not contain secret %s"
                % (key_vault_identifier.vault_url, key_vault_identifier.name)
            )

    if key_vault_options.secret_resolver is not None:
        return await key_vault_options.secret_resolver(config.secret_id)
    raise KeyVaultReferenceError(
        "No Secret Client found for Key Vault reference %s" % (key_vault_identifier.vault_url)
    )

def _is_json_content_type(content_type):
    if not content_type:
        return False

    content_type = content_type.strip().lower()
    mime_type = content_type.split(";")[0].strip()

    type_parts = mime_type.split("/")
    if len(type_parts) != 2:
        return False

    (main_type, sub_type) = type_parts
    if main_type != "application":
        return False

    sub_types = sub_type.split("+")
    if "json" in sub_types:
        return True

    return False


class AzureAppConfigurationProvider:
    """
    Provides a dictionary-like interface to Azure App Configuration settings. Enables loading of sets of configuration
    settings from Azure App Configuration into a Python application. Enables trimming of prefixes from configuration
    keys. Enables resolution of Key Vault references in configuration settings.
    """

    def __init__(self, client, *, trim_prefixes: Optional[List[str]] = None) -> None:
        self._dict: Dict[str, str] = {}
        self._trim_prefixes: List[str] = trim_prefixes or []
        self._client: AzureAppConfigurationClient = client
    
    async def __aenter__(self) -> "AzureAppConfigurationProvider":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)

    def __getitem__(self, key) -> str:
        return self._dict[key]

    def __repr__(self) -> str:
        return repr(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def copy(self) -> Dict[str, str]:
        """
        Returns a copy of the configuration settings
        """
        return self._dict.copy()

    def __contains__(self, __x: object) -> bool:
        """
        Returns True if the configuration settings contains the specified key
        """
        return self._dict.__contains__(__x)

    def keys(self) -> List[str]:
        """
        Returns a list of keys loaded from Azure App Configuration.

        type: () -> list
        """
        return list(self._dict.keys())

    def values(self) -> List[str]:
        """
        Returns a list of values loaded from Azure App Configuration. Any values that are Key Vault references will be
        resolved.
        """
        return list(self._dict.values())

    async def close(self) -> None:
        """Closes the underlying connection pool."""
        await self._client.close()
