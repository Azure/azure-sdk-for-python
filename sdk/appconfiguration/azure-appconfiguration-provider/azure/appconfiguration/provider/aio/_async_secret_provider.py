# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Mapping, Union, Any, Iterator, KeysView, ItemsView, ValuesView, TypeVar, overload, Optional, Dict
from azure.appconfiguration import SecretReferenceConfigurationSetting  # type:ignore # pylint:disable=no-name-in-module
from azure.keyvault.secrets.aio import SecretClient
from azure.keyvault.secrets import KeyVaultSecretIdentifier
from .._azureappconfigurationproviderbase import _RefreshTimer
from .._secret_provider_base import _SecretProviderBase

JSON = Mapping[str, Any]
_T = TypeVar("_T")


class SecretProvider(_SecretProviderBase):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._secret_clients: Dict[str, SecretClient] = {}
        self._keyvault_credential = kwargs.pop("keyvault_credential", None)
        self._secret_resolver = kwargs.pop("secret_resolver", None)
        self._keyvault_client_configs = kwargs.pop("keyvault_client_configs", {})

    async def resolve_keyvault_reference(self, config: SecretReferenceConfigurationSetting) -> str:
        # pylint:disable=protected-access
        if config.key in self._secret_cache:
            return self._secret_cache[config.key]
        if not self.uses_key_vault:
            raise ValueError(
                """
                Either a credential to Key Vault, custom Key Vault client, or a secret resolver must be set to resolve
                Key Vault references.
                """
            )

        if config.secret_id is None:
            raise ValueError("Key Vault reference must have a uri value.")

        keyvault_identifier = KeyVaultSecretIdentifier(config.secret_id)

        vault_url = keyvault_identifier.vault_url + "/"

        # pylint:disable=protected-access
        referenced_client = self._secret_clients.get(vault_url, None)

        vault_config = self._keyvault_client_configs.get(vault_url, {})
        credential = vault_config.pop("credential", self._keyvault_credential)

        if referenced_client is None and credential is not None:
            referenced_client = SecretClient(vault_url=vault_url, credential=credential, **vault_config)
            self._secret_clients[vault_url] = referenced_client

        if referenced_client:
            secret_value = (
                await referenced_client.get_secret(keyvault_identifier.name, version=keyvault_identifier.version)
            ).value
            if secret_value is not None:
                self._secret_cache[config.key] = secret_value
                return secret_value

        if self._secret_resolver:
            resolved = self._secret_resolver(config.secret_id)
            try:
                # Secret resolver was async
                value = await resolved
                self._secret_cache[config.key] = value
                return value
            except TypeError:
                # Secret resolver was sync
                self._secret_cache[config.key] = resolved
                return resolved

        raise ValueError("No Secret Client found for Key Vault reference %s" % (vault_url))

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
