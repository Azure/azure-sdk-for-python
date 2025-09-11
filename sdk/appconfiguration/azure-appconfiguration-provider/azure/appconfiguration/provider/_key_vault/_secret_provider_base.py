# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import (
    Mapping,
    Union,
    Any,
    Iterator,
    KeysView,
    ItemsView,
    ValuesView,
    TypeVar,
    overload,
    Optional,
    Dict,
    Tuple,
)
from azure.appconfiguration import SecretReferenceConfigurationSetting  # type:ignore # pylint:disable=no-name-in-module
from azure.keyvault.secrets import KeyVaultSecretIdentifier
from .._azureappconfigurationproviderbase import _RefreshTimer

JSON = Mapping[str, Any]
_T = TypeVar("_T")


class _SecretProviderBase(Mapping[str, Union[str, JSON]]):

    def __init__(self, **kwargs: Any) -> None:
        self._secret_cache: Dict[str, Any] = {}
        self._secret_version_cache: Dict[str, str] = {}
        self.uses_key_vault = (
            "keyvault_credential" in kwargs
            or ("keyvault_client_configs" in kwargs and len(kwargs.get("keyvault_client_configs", {})) > 0)
            or "secret_resolver" in kwargs
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

    def resolve_keyvault_reference_base(
        self, config: SecretReferenceConfigurationSetting
    ) -> Tuple[KeyVaultSecretIdentifier, str]:
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

        return keyvault_identifier, vault_url

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
