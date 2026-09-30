# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any

from azure.core.tracing.decorator_async import distributed_trace_async

from .._internal import AsyncKeyVaultClientBase
from .._models import KeyVaultEkmConnection, KeyVaultEkmProxyClientCertificateInfo, KeyVaultEkmProxyInfo


class KeyVaultEkmClient(AsyncKeyVaultClientBase):
    """Provides methods to manage Managed HSM External Key Manager (EKM) connections.

    :param str vault_url: URL of the vault on which the client will operate. This is also called the vault's "DNS Name".
        You should validate that this URL references a valid Key Vault or Managed HSM resource.
        See https://aka.ms/azsdk/blog/vault-uri for details.
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity.aio`
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential

    :keyword api_version: Version of the service API to use. EKM operations require service API version
        ``2026-01-01-preview`` or later.
    :paramtype api_version: ~azure.keyvault.administration.ApiVersion or str
    :keyword bool verify_challenge_resource: Whether to verify the authentication challenge resource matches the Key
        Vault or Managed HSM domain. Defaults to True.
    """

    # pylint:disable=protected-access

    @distributed_trace_async
    async def get_ekm_connection(self, **kwargs: Any) -> KeyVaultEkmConnection:
        """Gets the configured EKM connection.

        :returns: The configured EKM connection.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._client.get_ekm_connection(**kwargs)
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace_async
    async def create_ekm_connection(self, connection: KeyVaultEkmConnection, **kwargs: Any) -> KeyVaultEkmConnection:
        """Creates the EKM connection.

        If an EKM connection already exists, this operation fails.

        :param connection: The EKM connection to create.
        :type connection: ~azure.keyvault.administration.KeyVaultEkmConnection

        :returns: The created EKM connection.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._client.create_ekm_connection(ekm_connection=connection._to_generated(), **kwargs)
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace_async
    async def update_ekm_connection(self, connection: KeyVaultEkmConnection, **kwargs: Any) -> KeyVaultEkmConnection:
        """Updates the existing EKM connection.

        If no EKM connection exists, this operation fails.

        :param connection: The EKM connection to update.
        :type connection: ~azure.keyvault.administration.KeyVaultEkmConnection

        :returns: The updated EKM connection.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._client.update_ekm_connection(ekm_connection=connection._to_generated(), **kwargs)
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace_async
    async def delete_ekm_connection(  # pylint:disable=bad-option-value,delete-operation-wrong-return-type
        self, **kwargs: Any
    ) -> KeyVaultEkmConnection:
        """Deletes the existing EKM connection.

        If no EKM connection exists, this operation fails.

        :returns: The deleted EKM connection.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._client.delete_ekm_connection(**kwargs)
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace_async
    async def get_ekm_certificate(self, **kwargs: Any) -> KeyVaultEkmProxyClientCertificateInfo:
        """Gets the EKM proxy client certificate information used to authenticate to the EKM proxy.

        :returns: The EKM proxy client certificate information.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmProxyClientCertificateInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._client.get_ekm_certificate(**kwargs)
        return KeyVaultEkmProxyClientCertificateInfo._from_generated(result)

    @distributed_trace_async
    async def check_ekm_connection(self, **kwargs: Any) -> KeyVaultEkmProxyInfo:
        """Checks the EKM connection by pinging the EKM proxy.

        :returns: Information about the EKM proxy returned by the connectivity check.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmProxyInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._client.check_ekm_connection(**kwargs)
        return KeyVaultEkmProxyInfo._from_generated(result)

    async def __aenter__(self) -> "KeyVaultEkmClient":
        await self._client.__aenter__()
        return self
