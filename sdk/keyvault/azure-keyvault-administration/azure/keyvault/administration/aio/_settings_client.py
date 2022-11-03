# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .._generated_models import UpdateSettingsRequest
from .._internal import AsyncKeyVaultClientBase
from .._models import GetSettingsResult, KeyVaultSetting

class KeyVaultSettingsClient(AsyncKeyVaultClientBase):
    """Provides methods to create, update, get, and list settings for an Azure Key Vault.

    :param str vault_url: URL of the vault on which the client will operate. This is also called the vault's "DNS Name".
        You should validate that this URL references a valid Key Vault or Managed HSM resource.
        See https://aka.ms/azsdk/blog/vault-uri for details.
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity.aio`
    :type credential: :class:`~azure.core.credentials_async.AsyncTokenCredential`

    :keyword api_version: Version of the service API to use. Defaults to the most recent.
    :paramtype api_version: ~azure.keyvault.administration.ApiVersion
    :keyword bool verify_challenge_resource: Whether to verify the authentication challenge resource matches the Key
        Vault or Managed HSM domain. Defaults to True.
    """

    async def set_setting(self, name: str, value: str, **kwargs) -> KeyVaultSetting:
        """Creates or updates a given account setting with the provided value.

        :param str name: The name of the account setting to create or update.
        :param str value: The value to set.

        :returns: The created or updated account setting, as a :class:`~azure.keyvault.administration.KeyVaultSetting`.
        :rtype: ~azure.keyvault.administration.KeyVaultSetting
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        parameters = UpdateSettingsRequest(value=value)
        result = await self._client.update_settings(
            vault_base_url=self._vault_url,
            setting_name=name,
            parameters=parameters,
            **kwargs
        )
        return KeyVaultSetting._from_generated(result)

    async def get_setting(self, name: str, **kwargs) -> KeyVaultSetting:
        """Gets the setting with the specified name.

        :param str name: The name of the account setting.

        :returns: The account setting, as a :class:`~azure.keyvault.administration.KeyVaultSetting`.
        :rtype: ~azure.keyvault.administration.KeyVaultSetting
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        result = await self._client.get_setting_value(vault_base_url=self._vault_url, setting_name=name, **kwargs)
        return KeyVaultSetting._from_generated(result)

    async def get_settings(self, **kwargs) -> GetSettingsResult:
        """Gets all account settings.

        :returns: A :class:`~azure.keyvault.administration.GetSettingsResult` object containing the account's settings.
        :rtype: ~azure.keyvault.administration.GetSettingsResult
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        result = await self._client.get_settings(vault_base_url=self._vault_url, *kwargs)
        return GetSettingsResult._from_generated(result)
