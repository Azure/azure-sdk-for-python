# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any

from azure.core.tracing.decorator import distributed_trace

from ._models import KeyVaultEkmConnection
from ._generated.models import (
    EkmConnection,
    EkmProxyClientCertificateInfo,
    EkmProxyInfo,
)
from ._internal import KeyVaultClientBase


class KeyVaultEkmClient(KeyVaultClientBase):
    """Provides methods to manage External Key Manager (EKM) connections.

    :param str vault_url: URL of the vault on which the client will operate. This is also called the vault's "DNS Name".
        You should validate that this URL references a valid Key Vault or Managed HSM resource.
        See https://aka.ms/azsdk/blog/vault-uri for details.
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    :type credential: ~azure.core.credentials.TokenCredential

    :keyword api_version: Version of the service API to use. Defaults to the most recent.
    :paramtype api_version: ~azure.keyvault.administration.ApiVersion or str
    :keyword bool verify_challenge_resource: Whether to verify the authentication challenge resource matches the Key
        Vault or Managed HSM domain. Defaults to True.
    """

    @distributed_trace
    def get_ekm_connection(self, **kwargs: Any) -> KeyVaultEkmConnection:
        """Gets the EKM connection.

        The External Key Manager (EKM) Get operation returns EKM connection. This operation requires
        ekm/read permission.

        :return: KeyVaultEkmConnection. The KeyVaultEkmConnection is compatible with MutableMapping
        :rtype: ~azure.keyvault.administration._models.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.get_ekm_connection(**kwargs)
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace
    def get_ekm_certificate(self, **kwargs: Any) -> EkmProxyClientCertificateInfo:
        """Gets the EKM proxy client certificate.

        The External Key Manager (EKM) Certificate Get operation returns Proxy client certificate. This
        operation requires ekm/read permission.

        :return: EkmProxyClientCertificateInfo. The EkmProxyClientCertificateInfo is compatible with
         MutableMapping
        :rtype: ~azure.keyvault.administration._generated.models.EkmProxyClientCertificateInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._client.get_ekm_certificate(**kwargs)

    @distributed_trace
    def check_ekm_connection(self, **kwargs: Any) -> EkmProxyInfo:
        """Checks the connectivity and authentication with the EKM proxy.

        The External Key Manager (EKM) Check operation checks the connectivity and authentication with
        the EKM proxy. This operation requires ekm/read permission.

        :return: EkmProxyInfo. The EkmProxyInfo is compatible with MutableMapping
        :rtype: ~azure.keyvault.administration._generated.models.EkmProxyInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._client.check_ekm_connection(**kwargs)

    @distributed_trace
    def create_ekm_connection(
        self, ekm_connection: KeyVaultEkmConnection, **kwargs: Any
    ) -> KeyVaultEkmConnection:
        """Creates the EKM connection.

        The External Key Manager (EKM) sets up the EKM connection. If the EKM connection already
        exists, this operation fails. This operation requires ekm/write permission.

        :param ekm_connection: The KeyVaultEkmConnection to create.
        :type ekm_connection: ~azure.keyvault.administration._models.KeyVaultEkmConnection
        :return: KeyVaultEkmConnection. The KeyVaultEkmConnection is compatible with MutableMapping
        :rtype: ~azure.keyvault.administration._models.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        internal_ekm_connection = EkmConnection(
            host=ekm_connection.host,
            path_prefix=ekm_connection.path_prefix,
            server_ca_certificates=ekm_connection.server_ca_certificates,
            server_subject_common_name=ekm_connection.server_subject_common_name,
        )
        result = self._client.create_ekm_connection(
            ekm_connection=internal_ekm_connection, **kwargs
        )
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace
    def update_ekm_connection(
        self, ekm_connection: KeyVaultEkmConnection, **kwargs: Any
    ) -> KeyVaultEkmConnection:
        """Updates the EKM connection.

        The External Key Manager (EKM) updates the existing EKM connection. If the EKM connection does
        not exist, this operation fails. This operation requires ekm/write permission.

        :param ekm_connection: The ekmConnection to update.
        :type ekm_connection: ~azure.keyvault.administration._models.KeyVaultEkmConnection
        :return: KeyVaultEkmConnection. The KeyVaultEkmConnection is compatible with MutableMapping
        :rtype: ~azure.keyvault.administration._models.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        internal_ekm_connection = EkmConnection(
            host=ekm_connection.host,
            path_prefix=ekm_connection.path_prefix,
            server_ca_certificates=ekm_connection.server_ca_certificates,
            server_subject_common_name=ekm_connection.server_subject_common_name,
        )
        result = self._client.update_ekm_connection(
            ekm_connection=internal_ekm_connection, **kwargs
        )
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace
    def delete_ekm_connection(self, **kwargs: Any) -> KeyVaultEkmConnection:
        """Deletes the EKM connection.

        The External Key Manager (EKM) deletes the existing EKM connection. If the EKM connection does
        not already exists, this operation fails. This operation requires ekm/delete permission.

        :return: KeyVaultEkmConnection. The KeyVaultEkmConnection is compatible with MutableMapping
        :rtype: ~azure.keyvault.administration._models.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.delete_ekm_connection(**kwargs)
        return KeyVaultEkmConnection._from_generated(result)

    def __enter__(self) -> "KeyVaultEkmClient":
        self._client.__enter__()
        return self
