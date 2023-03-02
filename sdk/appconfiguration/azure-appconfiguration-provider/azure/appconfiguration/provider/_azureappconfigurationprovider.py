# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import json
from typing import Any, Dict, Iterable, Mapping, Optional, overload, List, Tuple, TYPE_CHECKING, Union
from azure.appconfiguration import (
    AzureAppConfigurationClient,
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting
)
from azure.keyvault.secrets import SecretClient, KeyVaultSecretIdentifier
from ._models import AzureAppConfigurationKeyVaultOptions, SettingSelector
from ._constants import (
    FEATURE_MANAGEMENT_KEY,
    FEATURE_FLAG_PREFIX,
    ServiceFabricEnvironmentVariable,
    AzureFunctionEnvironmentVariable,
    AzureWebAppEnvironmentVariable,
    ContainerAppEnvironmentVariable,
    KubernetesEnvironmentVariable,
    EMPTY_LABEL
)

from ._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

JSON = Union[str, Mapping[str, Any]]  # pylint: disable=unsubscriptable-object

@overload
def load_provider(
        endpoint: str,
        credential: "TokenCredential",
        *,
        selects: Optional[List[SettingSelector]] = None,
        trimmed_key_prefixes: Optional[List[str]] = None,
        key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
        **kwargs
    ) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :param str endpoint: Endpoint for App Configuration resource.
    :param credential: Credential for App Configuration resource.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword selects: List of setting selectors to filter configuration settings
    :paramtype selects: Optional[List[~azure.appconfiguration.provider.SettingSelector]]
    :keyword trimmed_key_prefixes: List of prefixes to trim from configuration keys
    :paramtype trimmed_key_prefixes: Optional[List[str]]
    :keyword key_vault_options: Options for resolving Key Vault references
    :paramtype key_vault_options: ~azure.appconfiguration.provider.AzureAppConfigurationKeyVaultOptions
    """
    ...

@overload
def load_provider(
        *,
        connection_string: str,
        selects: Optional[List[SettingSelector]] = None,
        trimmed_key_prefixes: Optional[List[str]] = None,
        key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = None,
        **kwargs
    ) -> "AzureAppConfigurationProvider":
    """
    Loads configuration settings from Azure App Configuration into a Python application.

    :keyword str connection_string: Connection string for App Configuration resource.
    :keyword selects: List of setting selectors to filter configuration settings
    :paramtype selects: Optional[List[~azure.appconfiguration.provider.SettingSelector]]
    :keyword trimmed_key_prefixes: List of prefixes to trim from configuration keys
    :paramtype trimmed_key_prefixes: Optional[List[str]]
    :keyword key_vault_options: Options for resolving Key Vault references
    :paramtype key_vault_options: ~azure.appconfiguration.provider.AzureAppConfigurationKeyVaultOptions
    """
    ...

def load_provider(*args, **kwargs) -> "AzureAppConfigurationProvider":
    #pylint:disable=protected-access

    # Start by parsing kwargs
    endpoint: Optional[str] = kwargs.pop("endpoint", None)
    credential: Optional["TokenCredential"] = kwargs.pop("credential", None)
    connection_string: Optional[str] = kwargs.pop("connection_string", None)
    key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = kwargs.pop("key_vault_options", None)
    selects: List[SettingSelector] = kwargs.pop("selects", [SettingSelector(key_filter="*", label_filter=EMPTY_LABEL)])
    trim_prefixes : List[str] = kwargs.pop("trim_prefixes", [])

    # Update endpoint and credential if specified positionally.
    if len(args) > 2:
        raise TypeError(
            "Unexpected positional parameters. Please pass either endpoint and credential, or a connection string."
        )
    if len(args) == 1:
        if endpoint is not None:
            raise TypeError("Received multiple values for parameter 'endpoint'.")
        endpoint = args[0]
    elif len(args) == 2:
        if credential is not None:
            raise TypeError("Received multiple values for parameter 'credential'.")
        endpoint, credential = args

    if (endpoint or credential) and connection_string:
        raise ValueError("Please pass either endpoint and credential, or a connection string.")


    provider = _buildprovider(connection_string, endpoint, credential, key_vault_options, **kwargs)
    provider._trim_prefixes = sorted(trim_prefixes, key=len, reverse=True)

    for select in selects:
        configurations = provider._client.list_configuration_settings(
            key_filter=select.key_filter, label_filter=select.label_filter
        )
        for config in configurations:

            trimmed_key = config.key
            # Trim the key if it starts with one of the prefixes provided
            for trim in provider._trim_prefixes:
                if config.key.startswith(trim):
                    trimmed_key = config.key[len(trim) :]
                    break

            if isinstance(config, SecretReferenceConfigurationSetting):
                secret = _resolve_keyvault_reference(config, key_vault_options, provider)
                provider._dict[trimmed_key] = secret
            elif isinstance(config, FeatureFlagConfigurationSetting):
                feature_management = provider._dict.get(FEATURE_MANAGEMENT_KEY, {})
                if trimmed_key.startswith(FEATURE_FLAG_PREFIX):
                    feature_management[trimmed_key[len(FEATURE_FLAG_PREFIX) :]] = config.value
                else:
                    feature_management[trimmed_key] = config.value
                if FEATURE_MANAGEMENT_KEY not in provider.keys():
                    provider._dict[FEATURE_MANAGEMENT_KEY] = feature_management
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


def _get_correlation_context(key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions]) -> str:
    correlation_context = "RequestType=Startup"
    if key_vault_options and (
        key_vault_options.credential or key_vault_options.client_configs or key_vault_options.secret_resolver
    ):
        correlation_context += ",UsesKeyVault"
    host_type = ""
    if os.environ.get(AzureFunctionEnvironmentVariable) is not None:
        host_type = "AzureFunctions"
    elif os.environ.get(AzureWebAppEnvironmentVariable) is not None:
        host_type = "AzureWebApps"
    elif os.environ.get(ContainerAppEnvironmentVariable) is not None:
        host_type = "ContainerApps"
    elif os.environ.get(KubernetesEnvironmentVariable) is not None:
        host_type = "Kubernetes"
    elif os.environ.get(ServiceFabricEnvironmentVariable) is not None:
        host_type = "ServiceFabric"
    if host_type:
        correlation_context += ",Host=" + host_type
    return correlation_context


def _buildprovider(
        connection_string: Optional[str],
        endpoint: Optional[str],
        credential: Optional["TokenCredential"],
        key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions],
        **kwargs
    ) -> "AzureAppConfigurationProvider":
    #pylint:disable=protected-access
    provider = AzureAppConfigurationProvider()
    headers = kwargs.pop("headers", {})
    headers["Correlation-Context"] = _get_correlation_context(key_vault_options)
    useragent = USER_AGENT

    if connection_string:
        provider._client = AzureAppConfigurationClient.from_connection_string(
            connection_string, user_agent=useragent, headers=headers, **kwargs
        )
        return provider
    provider._client = AzureAppConfigurationClient(
        endpoint, credential, user_agent=useragent, headers=headers, **kwargs
    )
    return provider


def _resolve_keyvault_reference(
        config,
        key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions],
        provider: "AzureAppConfigurationProvider"
    ) -> str:
    if key_vault_options is None:
        raise ValueError("Key Vault options must be set to resolve Key Vault references.")

    if config.secret_id is None:
        raise ValueError("Key Vault reference must have a uri value.")

    key_vault_identifier = KeyVaultSecretIdentifier(config.secret_id)

    vault_url = key_vault_identifier.vault_url + "/"

    #pylint:disable=protected-access
    referenced_client = provider._secret_clients.get(vault_url, None)

    vault_config = key_vault_options.client_configs.get(vault_url, {})
    credential = vault_config.pop("credential", key_vault_options.credential)

    if referenced_client is None and credential is not None:
        referenced_client = SecretClient(
            vault_url=vault_url, credential=credential, **vault_config
        )
        provider._secret_clients[vault_url] = referenced_client

    if referenced_client:
        return referenced_client.get_secret(key_vault_identifier.name, version=key_vault_identifier.version).value

    if key_vault_options.secret_resolver is not None:
        return key_vault_options.secret_resolver(config.secret_id)

    raise ValueError(
        "No Secret Client found for Key Vault reference %s" % (vault_url)
    )


def _is_json_content_type(content_type: str) -> bool:
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


class AzureAppConfigurationProvider(Mapping[str, Union[str, JSON]]):
    """
    Provides a dictionary-like interface to Azure App Configuration settings. Enables loading of sets of configuration
    settings from Azure App Configuration into a Python application. Enables trimming of prefixes from configuration
    keys. Enables resolution of Key Vault references in configuration settings.
    """

    def __init__(self) -> None:
        self._dict: Dict[str, str] = {}
        self._trim_prefixes: List[str] = []
        self._client: Optional[AzureAppConfigurationClient] = None
        self._secret_clients: Dict[str, SecretClient] = {}

    def __getitem__(self, key: str) -> str:
        """
        Returns the value of the specified key.
        """
        return self._dict[key]

    def __iter__(self) -> Iterable[str]:
        return self._dict.__iter__()

    def __len__(self) -> int:
        return len(self._dict)

    def __contains__(self, __x: object) -> bool:
        """
        Returns True if the configuration settings contains the specified key.
        """
        return self._dict.__contains__(__x)

    def keys(self) -> Iterable[str]:
        """
        Returns a list of keys loaded from Azure App Configuration.
        """
        return self._dict.keys()

    def items(self) -> Iterable[Tuple[str, str]]:
        """
        Returns a list of key-value pairs loaded from Azure App Configuration. Any values that are Key Vault references
        will be resolved.
        """
        return self._dict.items()

    def values(self) -> Iterable[str]:
        """
        Returns a list of values loaded from Azure App Configuration. Any values that are Key Vault references will be
        resolved.
        """
        return self._dict.values()

    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        Returns the value of the specified key. If the key does not exist, returns the default value.
        """
        return self._dict.get(key, default)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AzureAppConfigurationProvider):
            return False
        if self._dict != other._dict:
            return False
        if self._trim_prefixes != other._trim_prefixes:
            return False
        if self._client != other._client:
            return False
        return True

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def close(self) -> None:
        """
        Closes the connection to Azure App Configuration.
        """
        for client in self._secret_clients.values():
            client.close()
        self._client.close()

    def __enter__(self) -> "AzureAppConfigurationProvider":
        self._client.__enter__()
        for client in self._secret_clients.values():
            client.__enter__()
        return self

    def __exit__(self, *args) -> None:
        self._client.__exit__(*args)
        for client in self._secret_clients.values():
            client.__exit__()
