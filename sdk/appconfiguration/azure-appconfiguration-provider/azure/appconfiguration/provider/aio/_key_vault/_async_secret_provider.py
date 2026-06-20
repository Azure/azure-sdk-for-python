# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import inspect
from typing import Mapping, Any, Dict
from azure.appconfiguration import SecretReferenceConfigurationSetting  # type:ignore # pylint:disable=no-name-in-module
from azure.keyvault.secrets import KeyVaultSecretIdentifier
from azure.keyvault.secrets.aio import SecretClient
from azure.core.exceptions import ServiceRequestError
from ..._key_vault._secret_provider_base import _SecretProviderBase

JSON = Mapping[str, Any]


class SecretProvider(_SecretProviderBase):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._secret_clients: Dict[str, SecretClient] = {}
        self._keyvault_credential = kwargs.pop("keyvault_credential", None)
        self._secret_resolver = kwargs.pop("secret_resolver", None)
        self._keyvault_client_configs = kwargs.pop("keyvault_client_configs", {})

    async def resolve_keyvault_reference(self, config: SecretReferenceConfigurationSetting) -> str:
        keyvault_identifier, vault_url = self.resolve_keyvault_reference_base(config)
        if keyvault_identifier.source_id in self._secret_cache:
            _, _, value = self._secret_cache[keyvault_identifier.source_id]
            return value

        return await self.__get_secret_value(config.key, keyvault_identifier, vault_url)

    async def refresh_secrets(self) -> Dict[str, Any]:
        secrets = {}
        if self.secret_refresh_timer:
            original_cache = self._secret_cache.copy()
            self._secret_cache.clear()
            for source_id, (secret_identifier, key, _) in original_cache.items():
                value = await self.__get_secret_value(key, secret_identifier, secret_identifier.vault_url + "/")
                self._secret_cache[source_id] = (
                    secret_identifier,
                    key,
                    value,
                )
                secrets[key] = value
            self.secret_refresh_timer.reset()
        return secrets

    async def __get_secret_value(self, key: str, secret_identifier: KeyVaultSecretIdentifier, vault_url: str) -> str:
        referenced_client = self._secret_clients.get(vault_url, None)

        vault_config = self._keyvault_client_configs.get(vault_url, {})
        credential = vault_config.pop("credential", self._keyvault_credential)

        if referenced_client is None and credential is not None:
            referenced_client = SecretClient(vault_url=vault_url, credential=credential, **vault_config)
            self._secret_clients[vault_url] = referenced_client

        secret_value = None

        if referenced_client:
            try:
                secret_value = (
                    await referenced_client.get_secret(secret_identifier.name, version=secret_identifier.version)
                ).value
            except ServiceRequestError as e:
                raise ValueError("Failed to retrieve secret from Key Vault") from e

        if self._secret_resolver and secret_value is None:
            secret_value = self._secret_resolver(secret_identifier.source_id)
            if inspect.isawaitable(secret_value):
                # Secret resolver was async
                # Need to ignore type, mypy doesn't like the callback could return `Never`
                secret_value = await secret_value  # type: ignore

        return self._cache_value(key, secret_identifier, secret_value)

    async def close(self) -> None:
        """
        Closes the connection to Azure App Configuration.
        """
        for client in self._secret_clients.values():
            await client.close()

    async def __aenter__(self) -> "SecretProvider":
        for client in self._secret_clients.values():
            await client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        for client in self._secret_clients.values():
            await client.__aexit__()
