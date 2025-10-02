# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Mapping, Any, Dict
from azure.appconfiguration import SecretReferenceConfigurationSetting  # type:ignore # pylint:disable=no-name-in-module
from azure.keyvault.secrets import SecretClient, KeyVaultSecretIdentifier
from azure.core.exceptions import ServiceRequestError
from ._secret_provider_base import _SecretProviderBase

JSON = Mapping[str, Any]


class SecretProvider(_SecretProviderBase):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._secret_clients: Dict[str, SecretClient] = {}
        self._keyvault_credential = kwargs.pop("keyvault_credential", None)
        self._secret_resolver = kwargs.pop("secret_resolver", None)
        self._keyvault_client_configs = kwargs.pop("keyvault_client_configs", {})

    def resolve_keyvault_reference(self, config: SecretReferenceConfigurationSetting) -> str:
        keyvault_identifier, vault_url = self.resolve_keyvault_reference_base(config)
        if keyvault_identifier.source_id in self._secret_cache:
            value, _ = self._secret_cache[keyvault_identifier.source_id]
            return value
        if keyvault_identifier.source_id in self._secret_version_cache:
            value, _ = self._secret_version_cache[keyvault_identifier.source_id]
            return value

        return self.__get_secret_value(keyvault_identifier.source_id, keyvault_identifier)

    def refresh_secrets(self) -> None:
        original_cache = self._secret_cache.copy()
        self._secret_cache.clear()
        for secret_id, (_, secret_identifier) in original_cache.items():
            self._secret_cache[secret_id] = self.__get_secret_value(secret_id, secret_identifier), secret_identifier

    def __get_secret_value(self, secret_id: str, secret_identifier: KeyVaultSecretIdentifier) -> str:
        referenced_client = self._secret_clients.get(secret_identifier.vault_url, None)

        vault_config = self._keyvault_client_configs.get(secret_identifier.vault_url, {})
        credential = vault_config.pop("credential", self._keyvault_credential)

        if referenced_client is None and credential is not None:
            referenced_client = SecretClient(vault_url=secret_identifier.vault_url, credential=credential, **vault_config)
            self._secret_clients[secret_identifier.vault_url] = referenced_client

        secret_value = None

        if referenced_client:
            try:
                secret_value = referenced_client.get_secret(
                    secret_identifier.name, version=secret_identifier.version
                ).value
            except ServiceRequestError as e:
                raise ValueError("Failed to retrieve secret from Key Vault") from e

        if self._secret_resolver and secret_value is None:
            secret_value = self._secret_resolver(secret_id)

        return self._cache_value(secret_id, secret_identifier, secret_value)

    def close(self) -> None:
        """
        Closes the connection to Azure App Configuration.
        """
        for client in self._secret_clients.values():
            client.close()

    def __enter__(self) -> "SecretProvider":
        for client in self._secret_clients.values():
            client.__enter__()
        return self

    def __exit__(self, *args) -> None:
        for client in self._secret_clients.values():
            client.__exit__()
