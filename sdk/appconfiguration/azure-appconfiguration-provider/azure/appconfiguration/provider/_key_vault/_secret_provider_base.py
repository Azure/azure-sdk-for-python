# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import (
    Mapping,
    Any,
    TypeVar,
    Optional,
    Dict,
    Tuple,
)
from azure.appconfiguration import SecretReferenceConfigurationSetting  # type:ignore # pylint:disable=no-name-in-module
from azure.keyvault.secrets import KeyVaultSecretIdentifier
from .._azureappconfigurationproviderbase import _RefreshTimer

JSON = Mapping[str, Any]
_T = TypeVar("_T")


class _SecretProviderBase:

    def __init__(self, **kwargs: Any) -> None:
        # [source_id, (KeyVaultSecretIdentifier, key, value)]
        self._secret_cache: Dict[str, Tuple[KeyVaultSecretIdentifier, str, str]] = {}
        self.uses_key_vault = (
            "keyvault_credential" in kwargs
            or ("keyvault_client_configs" in kwargs and len(kwargs.get("keyvault_client_configs", {})) > 0)
            or "secret_resolver" in kwargs
        )

        if kwargs.get("secret_refresh_interval", 60) < 1:
            raise ValueError("Secret refresh interval must be greater than 1 second.")

        self.secret_refresh_timer: Optional[_RefreshTimer] = (
            _RefreshTimer(refresh_interval=kwargs.pop("secret_refresh_interval", 60))
            if self.uses_key_vault and "secret_refresh_interval" in kwargs
            else None
        )

    def _cache_value(self, key: str, keyvault_identifier: KeyVaultSecretIdentifier, secret_value: Any) -> str:
        if secret_value:
            self._secret_cache[keyvault_identifier.source_id] = (keyvault_identifier, key, secret_value)
            return secret_value

        raise ValueError("No Secret Client found for Key Vault reference %s" % (keyvault_identifier.vault_url))

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
