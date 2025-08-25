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

JSON = Mapping[str, Any]
_T = TypeVar("_T")


class SecretProvider(Mapping[str, Union[str, JSON]]):

    def __init__(self, **kwargs: Any) -> None:
        self._secret_cache: Dict[str, Any] = {}
        self._secret_clients: Dict[str, SecretClient] = {}
        self._keyvault_credential = kwargs.pop("keyvault_credential", None)
        self._secret_resolver = kwargs.pop("secret_resolver", None)
        self._keyvault_client_configs = kwargs.pop("keyvault_client_configs", {})
        self.uses_key_vault = (
            self._keyvault_credential is not None
            or (self._keyvault_client_configs is not None and len(self._keyvault_client_configs) > 0)
            or self._secret_resolver is not None
        )
        self.secret_refresh_timer: Optional[_RefreshTimer] = (
            _RefreshTimer(refresh_interval=kwargs.pop("secret_refresh_interval", 60))
            if self.uses_key_vault and "secret_refresh_interval" in kwargs
            else None
        )

    def bust_cache(self) -> None:
        """
        Clears the secret cache.
        """
        self._secret_cache = {}

    async def resolve_keyvault_reference(self, config: SecretReferenceConfigurationSetting) -> str:
        # pylint:disable=protected-access
        if config.key in self._secret_cache:
            return self._secret_cache[config.key]
        if not (self._keyvault_credential or self._keyvault_client_configs or self._secret_resolver):
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

    def __getitem__(self, key: str) -> Any:
        # pylint:disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
        """
        Returns the value of the specified key.
        """
        return self._secret_cache[key]

    def __iter__(self) -> Iterator[str]:
        return self._secret_cache.__iter__()

    def __len__(self) -> int:
        return len(self._secret_cache)

    def __contains__(self, __x: object) -> bool:
        # pylint:disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
        """
        Returns True if the configuration settings contains the specified key.
        """
        return self._secret_cache.__contains__(__x)

    def keys(self) -> KeysView[str]:
        """
        Returns a list of keys loaded from Azure App Configuration.

        :return: A list of keys loaded from Azure App Configuration.
        :rtype: KeysView[str]
        """
        return self._secret_cache.keys()

    def items(self) -> ItemsView[str, Union[str, Mapping[str, Any]]]:
        """
        Returns a set-like object of key-value pairs loaded from Azure App Configuration. Any values that are Key Vault
         references will be resolved.

        :return: A set-like object of key-value pairs loaded from Azure App Configuration.
        :rtype: ItemsView[str, Union[str, Mapping[str, Any]]]
        """
        return self._secret_cache.items()

    def values(self) -> ValuesView[Union[str, Mapping[str, Any]]]:
        """
        Returns a list of values loaded from Azure App Configuration. Any values that are Key Vault references will be
        resolved.

        :return: A list of values loaded from Azure App Configuration. The values are either Strings or JSON objects,
         based on there content type.
        :rtype: ValuesView[Union[str, Mapping[str, Any]]]
        """
        return (self._secret_cache).values()

    @overload
    def get(self, key: str, default: None = None) -> Union[str, JSON, None]: ...

    @overload
    def get(self, key: str, default: Union[str, JSON, _T]) -> Union[str, JSON, _T]:  # pylint: disable=signature-differs
        ...

    def get(self, key: str, default: Optional[Union[str, JSON, _T]] = None) -> Union[str, JSON, _T, None]:
        """
        Returns the value of the specified key. If the key does not exist, returns the default value.

        :param str key: The key of the value to get.
        :param default: The default value to return.
        :type: str or None
        :return: The value of the specified key.
        :rtype: Union[str, JSON]
        """
        return self._secret_cache.get(key, default)

    def __ne__(self, other: Any) -> bool:
        return not self == other

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
