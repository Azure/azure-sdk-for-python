# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.appconfiguration import AzureAppConfigurationClient
from azure.keyvault.secrets import SecretClient
from ._settingselector import SettingSelector
from ._user_agent import USER_AGENT
from urllib.parse import urlparse
import json
import warnings


class AzureAppConfigurationProvider:

    @classmethod
    def load(cls, connection_string=None, endpoint=None, credential=None, **kwargs):
        """
        Requires either a connection-string, or an Endpoint with a Credential. Loads the selected configuration settings into itself for usage.
        Optional parameters:
        selectors (List of SettingSelector for selecting which applicationconfiguration settings to load),. If not specified, all key-values with the empty label will be loaded.
        trimmed_key_prefixes (remove prefixes in key name, list of what to trim),
        key_vault_options (Configurations for connecting to Key Vault(s))
        """
        provider = AzureAppConfigurationProvider()

        key_vault_options = kwargs.pop("key_vault_options", None)

        provider.client = cls.buildprovider(
            connection_string, endpoint, credential, key_vault_options)

        selects = kwargs.pop("selects", {SettingSelector("*", "\0")})
        provider.trim_prefixes = kwargs.pop("trimmed_key_prefixes", [])

        provider.dict = {}
        secret_clients = {}

        for select in selects:
            configurations = provider.client.list_configuration_settings(
                key_filter=select.key_filter, label_filter=select.label_filter)
            for config in configurations:
                if (config.content_type is None):
                    # Deals with possible null value via Rest API
                    provider.dict[provider.trim(config.key)] = config.value
                elif config.content_type == "application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8":
                    if (key_vault_options is None):
                        warnings.warn(
                            "Key Vault Reference found, but no Key Vault Options were provided")
                        continue
                    j_object = json.loads(config.value)
                    uri_value = j_object['uri']

                    uri = urlparse(uri_value)

                    key_vault_uri = "https://" + uri.hostname
                    key_vault_secret_prefix = "/secrets/"
                    key_vault_secret_name = uri.path[len(
                        key_vault_secret_prefix):]
                    if (key_vault_options.credential is not None):
                        secret_client = None

                        # Clients only should be made once, will reuse if client already made
                        for client_uri in secret_clients:
                            if client_uri == key_vault_uri:
                                secret_client = secret_clients[client_uri]
                                break
                        if (secret_client is None):
                            secret_client = SecretClient(
                                vault_url=key_vault_uri, credential=key_vault_options.credential)
                            secret_clients[key_vault_uri] = secret_client
                        secret = secret_client.get_secret(
                            key_vault_secret_name)
                        provider.dict[provider.trim(config.key)] = secret.value
                        continue
                    if (key_vault_options.secret_clients is not None):
                        for secret_client in key_vault_options.secret_clients:
                            if (secret_client._vault_url == key_vault_uri):
                                secret = secret_client.get_secret(
                                    key_vault_secret_name)
                                provider.dict[provider.trim(
                                    config.key)] = secret.value
                            break
                        continue
                    if (key_vault_options.secret_resolver is not None):
                        provider.dict[provider.trim(
                            config.key)] = key_vault_options.secret_resolver(uri)
                elif "application/json" in config.content_type:
                    j_object = json.loads(config.value)
                    provider.dict[provider.trim(config.key)] = j_object
                else:
                    provider.dict[provider.trim(config.key)] = config.value
        return provider

    def buildprovider(connection_string, endpoint, credential, key_vault_options):
        usesKeyVault = False

        if (key_vault_options is not None and (key_vault_options.credential is not None or key_vault_options.secret_clients is not None or key_vault_options.secret_resolver is not None)):
            usesKeyVault = True

        headers = {}
        correlation_context = "RequestType=Startup"

        if (usesKeyVault):
            correlation_context += ",UsesKeyVault"

        headers["Correlation-Context"] = correlation_context
        useragent = USER_AGENT

        if (connection_string is not None):
            return AzureAppConfigurationClient.from_connection_string(
                connection_string, user_agent=useragent, headers=headers)
        else:
            return AzureAppConfigurationClient(
                endpoint, credential, user_agent=useragent, headers=headers)

    def trim(self, key):
        for trim in self.trim_prefixes:
            if key.startswith(trim):
                return key[len(trim):]
        return key

    def __getitem__(self, key):
        return self.dict[key]

    def __repr__(self):
        return repr(self.dict)

    def __len__(self):
        return len(self.dict)

    def copy(self):
        return self.dict.copy()

    def has_key(self, k):
        return k in self.dict

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()
