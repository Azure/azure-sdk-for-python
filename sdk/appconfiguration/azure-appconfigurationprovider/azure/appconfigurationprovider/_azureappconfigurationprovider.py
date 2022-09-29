# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import json
from azure.appconfiguration import AzureAppConfigurationClient
from azure.keyvault.secrets import SecretClient, KeyVaultSecretIdentifier
from azure.core.exceptions import ResourceNotFoundError
from ._settingselector import SettingSelector
from ._azure_appconfiguration_provider_error import KeyVaultReferenceError
from ._constants import KEY_VAULT_REFERENCE_CONTENT_TYPE

from ._user_agent import USER_AGENT


class AzureAppConfigurationProvider:
    """
    Provides a dictionary-like interface to Azure App Configuration settings. Enables loading of sets of configuration
    settings from Azure App Configuration into a Python application. Enables trimming of prefixes from configuration
    keys. Enables resolution of Key Vault references in configuration settings.
    """

    def __init__(self):
        # type: () -> None
        self._dict = {}
        self._trim_prefixes = []
        self._client = None

    @classmethod
    def load(cls, connection_string=None, endpoint=None, credential=None, **kwargs):
        """
        Loads configuration settings from Azure App Configuration into a Python application.

        :param connection_string: Connection string (one of connection_string or endpoint and credential must be set)
        :type connection_string: str
        :param endpoint: Endpoint (one of connection_string or endpoint and credential must be set)
        :type endpoint: str
        :param credential: Credential (one of connection_string or endpoint and credential must be set)
        :type credential: Union[AppConfigConnectionStringCredential, TokenCredential]
        :keyword selectors: List of setting selectors to filter configuration settings
        :type selectors: list[~azure.appconfigurationprovider.SettingSelector]
        :keyword trim_prefixes: List of prefixes to trim from configuration keys
        :type trim_prefixes: list[str]
        :keyword key_vault_options: Options for resolving Key Vault references
        :type key_vault_options: ~azure.appconfigurationprovider.KeyVaultOptions
        """
        provider = AzureAppConfigurationProvider()

        key_vault_options = kwargs.pop("key_vault_options", None)

        provider.__buildprovider(connection_string, endpoint, credential, key_vault_options)

        selects = kwargs.pop("selects", {SettingSelector("*", "\0")})

        provider._trim_prefixes = sorted(kwargs.pop("trimmed_key_prefixes", []), key=len, reverse=True)

        provider._dict = {}

        secret_clients = key_vault_options.secret_clients if key_vault_options else {}

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

                if config.content_type == KEY_VAULT_REFERENCE_CONTENT_TYPE:
                    secret = provider.__resolve_keyvault_reference(config, key_vault_options, secret_clients)
                    provider._dict[trimmed_key] = secret
                elif provider.__is_json_content_type(config.content_type):
                    try:
                        j_object = json.loads(config.value)
                        provider._dict[trimmed_key] = j_object
                    except json.JSONDecodeError:
                        # If the value is not a valid JSON, treat it like regular string value
                        provider._dict[trimmed_key] = config.value
                else:
                    provider._dict[trimmed_key] = config.value
        return provider

    def __buildprovider(self, connection_string, endpoint, credential, key_vault_options):
        headers = {}
        correlation_context = "RequestType=Startup"

        if key_vault_options and (
            key_vault_options.credential or key_vault_options.secret_clients or key_vault_options.secret_resolver
        ):
            correlation_context += ",UsesKeyVault"

        headers["Correlation-Context"] = correlation_context
        useragent = USER_AGENT

        if connection_string and endpoint:
            raise AttributeError("Both connection_string and endpoint are set. Only one of these should be set.")

        if connection_string:
            self._client = AzureAppConfigurationClient.from_connection_string(
                connection_string, user_agent=useragent, headers=headers
            )
            return
        self._client = AzureAppConfigurationClient(endpoint, credential, user_agent=useragent, headers=headers)

    @staticmethod
    def __resolve_keyvault_reference(config, key_vault_options, secret_clients):
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
                return referenced_client.get_secret(
                    key_vault_identifier.name, version=key_vault_identifier.version
                ).value
            except ResourceNotFoundError:
                raise KeyVaultReferenceError(
                    "Key Vault %s does not contain secret %s"
                    % (key_vault_identifier.vault_url, key_vault_identifier.name)
                )

        if key_vault_options.secret_resolver is not None:
            return key_vault_options.secret_resolver(config.secret_id)
        raise KeyVaultReferenceError(
            "No Secret Client found for Key Vault reference %s" % (key_vault_identifier.vault_url)
        )

    @staticmethod
    def __is_json_content_type(content_type):
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

    def __getitem__(self, key):
        return self._dict[key]

    def __repr__(self):
        return repr(self._dict)

    def __len__(self):
        return len(self._dict)

    def copy(self):
        """
        Returns a copy of the configuration settings

        type: () -> dict
        """
        return self._dict.copy()

    def __contains__(self, __x: object):
        """
        Returns True if the configuration settings contains the specified key

        type: (object) -> bool
        """
        return self._dict.__contains__(__x)

    def keys(self):
        """
        Returns a list of keys loaded from Azure App Configuration.

        type: () -> list
        """
        return self._dict.keys()

    def values(self):
        """
        Returns a list of values loaded from Azure App Configuration. Any values that are Key Vault references will be
        resolved.

        type: () -> list
        """
        return self._dict.values()
