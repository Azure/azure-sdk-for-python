# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from urllib.parse import urlparse
import json
import warnings
from azure.appconfiguration import AzureAppConfigurationClient
from azure.keyvault.secrets import SecretClient
from ._settingselector import SettingSelector
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

        provider.__buildprovider(connection_string, endpoint,
                                 credential, key_vault_options)

        selects = kwargs.pop("selects", {SettingSelector("*", "\0")})
        provider._trim_prefixes = kwargs.pop("trimmed_key_prefixes", [])

        provider._dict = {}
        secret_clients = {}

        for select in selects:
            configurations = provider._client.list_configuration_settings(
                key_filter=select.key_filter, label_filter=select.label_filter)
            for config in configurations:
                if config.content_type is None:
                    # Deals with possible null value via Rest API
                    provider._dict[provider.__trim(config.key)] = config.value
                elif config.content_type == "application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8":
                    provider.__resolve_keyvault_references(
                        config, key_vault_options, secret_clients)
                elif "application/json" in config.content_type:
                    j_object = json.loads(config.value)
                    provider._dict[provider.__trim(config.key)] = j_object
                else:
                    provider._dict[provider.__trim(config.key)] = config.value
        return provider

    def __buildprovider(self, connection_string, endpoint, credential, key_vault_options):
        headers = {}
        correlation_context = "RequestType=Startup"

        if (key_vault_options is not None and
                (key_vault_options.credential is not None or key_vault_options.secret_clients is not None or
                 key_vault_options.secret_resolver is not None)):
            correlation_context += ",UsesKeyVault"

        headers["Correlation-Context"] = correlation_context
        useragent = USER_AGENT

        if connection_string is not None:
            self._client = AzureAppConfigurationClient.from_connection_string(
                connection_string, user_agent=useragent, headers=headers)
            return
        self._client = AzureAppConfigurationClient(
            endpoint, credential, user_agent=useragent, headers=headers)

    def __resolve_keyvault_references(self, config, key_vault_options, secret_clients):
        if key_vault_options is None:
            raise AttributeError(
                "Key Vault options must be set to resolve Key Vault references.")
        j_object = json.loads(config.value)
        uri_value = j_object['uri']

        uri = urlparse(uri_value)

        key_vault_uri = "https://" + uri.hostname
        key_vault_secret_prefix = "/secrets/"
        key_vault_secret_name = uri.path[len(
            key_vault_secret_prefix):]
        if key_vault_options.credential is not None:
            secret_client = None

            # Clients only should be made once, will reuse if client already made
            for client_uri in secret_clients:
                if client_uri == key_vault_uri:
                    secret_client = secret_clients[client_uri]
                    break
            if secret_client is None:
                secret_client = SecretClient(
                    vault_url=key_vault_uri, credential=key_vault_options.credential)
                secret_clients[key_vault_uri] = secret_client
                secret = secret_client.get_secret(
                    key_vault_secret_name)
                self._dict[self.__trim(config.key)] = secret.value
                return
            raise AttributeError(
                "No Secret Client found for Key Vault reference %s%s" % (key_vault_uri, uri.path))
        if key_vault_options.secret_clients is not None:
            for secret_client in key_vault_options.secret_clients:
                if secret_client._vault_url == key_vault_uri:
                    secret = secret_client.get_secret(
                        key_vault_secret_name)
                    self._dict[self.__trim(
                        config.key)] = secret.value
                    return
        if key_vault_options.secret_resolver is not None:
            self._dict[self.__trim(
                config.key)] = key_vault_options.secret_resolver(uri)
            return
        raise AttributeError(
            "No Secret Client found for Key Vault reference %s%s" % (key_vault_uri, uri.path))

    def __trim(self, key):
        for trim in self._trim_prefixes:
            if key.startswith(trim):
                return key[len(trim):]
        return key

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

    def has_key(self, k):
        """
        Returns True if the configuration settings has been loaded from Azure App Configuration.
        type: (str) -> bool
        """
        return k in self._dict

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
