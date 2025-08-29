# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import inspect
from typing import Mapping, Any, TypeVar, Dict
from azure.appconfiguration import SecretReferenceConfigurationSetting  # type:ignore # pylint:disable=no-name-in-module
from azure.keyvault.secrets.aio import SecretClient
from azure.core.exceptions import ServiceRequestError
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
        keyvault_identifier, vault_url = self.resolve_keyvault_reference_base(config)
        if keyvault_identifier.source_id in self._secret_cache:
            return self._secret_cache[keyvault_identifier.source_id]
        if keyvault_identifier.source_id in self._secret_version_cache:
            return self._secret_version_cache[keyvault_identifier.source_id]

        # pylint:disable=protected-access
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
                    await referenced_client.get_secret(keyvault_identifier.name, version=keyvault_identifier.version)
                ).value
            except ServiceRequestError as e:
                raise ValueError("Failed to retrieve secret from Key Vault") from e

        if self._secret_resolver and secret_value is None:
            secret_value = self._secret_resolver(config.secret_id)
            if inspect.isawaitable(secret_value):
                # Secret resolver was async
                secret_value = await secret_value

        if secret_value:
            if keyvault_identifier.version:
                self._secret_version_cache[keyvault_identifier.source_id] = secret_value
            else:
                self._secret_cache[keyvault_identifier.source_id] = secret_value
            return secret_value

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
