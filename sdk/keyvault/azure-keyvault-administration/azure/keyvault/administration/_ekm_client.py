# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Optional

from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._generated.models import EkmPrivateEndpointCreateParameters
from ._internal import KeyVaultClientBase
from ._models import (
    KeyVaultEkmConnection,
    KeyVaultEkmPrivateEndpoint,
    KeyVaultEkmPrivateEndpointOperation,
    KeyVaultEkmProxyClientCertificateInfo,
    KeyVaultEkmProxyInfo,
)


class KeyVaultEkmClient(KeyVaultClientBase):
    """Provides methods to manage Managed HSM External Key Manager (EKM) connections and private endpoints.

    :param str vault_url: URL of the vault on which the client will operate. This is also called the vault's "DNS Name".
        You should validate that this URL references a valid Key Vault or Managed HSM resource.
        See https://aka.ms/azsdk/blog/vault-uri for details.
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    :type credential: ~azure.core.credentials.TokenCredential

    :keyword api_version: Version of the service API to use. EKM operations require service API version
        ``2026-01-01-preview`` or later. EKM private endpoint operations require service API version
        ``2026-07-01-preview`` or later.
    :paramtype api_version: ~azure.keyvault.administration.ApiVersion or str
    :keyword bool verify_challenge_resource: Whether to verify the authentication challenge resource matches the Key
        Vault or Managed HSM domain. Defaults to True.
    """

    # pylint:disable=protected-access

    @distributed_trace
    def get_ekm_connection(self, **kwargs: Any) -> KeyVaultEkmConnection:
        """Gets the configured EKM connection.

        :returns: The configured EKM connection.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.get_ekm_connection(**kwargs)
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace
    def create_ekm_connection(self, connection: KeyVaultEkmConnection, **kwargs: Any) -> KeyVaultEkmConnection:
        """Creates the EKM connection.

        If an EKM connection already exists, this operation fails.

        :param connection: The EKM connection to create.
        :type connection: ~azure.keyvault.administration.KeyVaultEkmConnection

        :returns: The created EKM connection.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.create_ekm_connection(ekm_connection=connection._to_generated(), **kwargs)
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace
    def update_ekm_connection(self, connection: KeyVaultEkmConnection, **kwargs: Any) -> KeyVaultEkmConnection:
        """Updates the existing EKM connection.

        If no EKM connection exists, this operation fails.

        :param connection: The EKM connection to update.
        :type connection: ~azure.keyvault.administration.KeyVaultEkmConnection

        :returns: The updated EKM connection.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.update_ekm_connection(ekm_connection=connection._to_generated(), **kwargs)
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace
    def delete_ekm_connection(  # pylint:disable=bad-option-value,delete-operation-wrong-return-type
        self, **kwargs: Any
    ) -> KeyVaultEkmConnection:
        """Deletes the existing EKM connection.

        If no EKM connection exists, this operation fails.

        :returns: The deleted EKM connection.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmConnection
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.delete_ekm_connection(**kwargs)
        return KeyVaultEkmConnection._from_generated(result)

    @distributed_trace
    def get_ekm_certificate(self, **kwargs: Any) -> KeyVaultEkmProxyClientCertificateInfo:
        """Gets the EKM proxy client certificate information used to authenticate to the EKM proxy.

        :returns: The EKM proxy client certificate information.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmProxyClientCertificateInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.get_ekm_certificate(**kwargs)
        return KeyVaultEkmProxyClientCertificateInfo._from_generated(result)

    @distributed_trace
    def check_ekm_connection(self, **kwargs: Any) -> KeyVaultEkmProxyInfo:
        """Checks the EKM connection by pinging the EKM proxy.

        :returns: Information about the EKM proxy returned by the connectivity check.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmProxyInfo
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.check_ekm_connection(**kwargs)
        return KeyVaultEkmProxyInfo._from_generated(result)

    @distributed_trace
    def begin_create_ekm_private_endpoint(
        self, name: str, private_link_service_id: str, *, request_message: Optional[str] = None, **kwargs: Any
    ) -> LROPoller[KeyVaultEkmPrivateEndpointOperation]:
        """Begins creating an EKM proxy private endpoint.

        A Managed HSM pool may have up to two EKM proxy private endpoints.

        :param str name: The name of the private endpoint to create. Must be 1-24 characters, start and end with an
            alphanumeric character, and contain only alphanumeric characters and hyphens.
        :param str private_link_service_id: Alias of the Private Link Service that the private endpoint connects to.

        :keyword request_message: An optional message shown to the Private Link Service owner when approving the
            private endpoint connection.
        :paramtype request_message: str or None

        :returns: An :class:`~azure.core.polling.LROPoller` instance. Call `result()` on this object to wait for the
            operation to complete and get a :class:`KeyVaultEkmPrivateEndpointOperation`.
        :rtype:
            ~azure.core.polling.LROPoller[~azure.keyvault.administration.KeyVaultEkmPrivateEndpointOperation]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        parameters = EkmPrivateEndpointCreateParameters(
            private_link_service_id=private_link_service_id, request_message=request_message
        )
        return self._client.begin_create_ekm_private_endpoint(
            pe_name=name,
            parameters=parameters,
            cls=KeyVaultEkmPrivateEndpointOperation._from_polling_result,
            **kwargs,
        )

    @distributed_trace
    def begin_delete_ekm_private_endpoint(  # pylint:disable=bad-option-value,delete-operation-wrong-return-type
        self, name: str, **kwargs: Any
    ) -> LROPoller[KeyVaultEkmPrivateEndpointOperation]:
        """Begins deleting an EKM proxy private endpoint.

        The operation is rejected while an EKM connection still references the private endpoint.

        :param str name: The name of the private endpoint to delete.

        :returns: An :class:`~azure.core.polling.LROPoller` instance. Call `result()` on this object to wait for the
            operation to complete and get a :class:`KeyVaultEkmPrivateEndpointOperation`.
        :rtype:
            ~azure.core.polling.LROPoller[~azure.keyvault.administration.KeyVaultEkmPrivateEndpointOperation]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return self._client.begin_delete_ekm_private_endpoint(
            pe_name=name, cls=KeyVaultEkmPrivateEndpointOperation._from_polling_result, **kwargs
        )

    @distributed_trace
    def get_ekm_private_endpoint(self, name: str, **kwargs: Any) -> KeyVaultEkmPrivateEndpoint:
        """Gets an EKM proxy private endpoint.

        :param str name: The name of the private endpoint to get.

        :returns: The requested EKM proxy private endpoint.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmPrivateEndpoint
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.get_ekm_private_endpoint(pe_name=name, **kwargs)
        return KeyVaultEkmPrivateEndpoint._from_generated(result)

    @distributed_trace
    def list_ekm_private_endpoints(self, **kwargs: Any) -> ItemPaged[KeyVaultEkmPrivateEndpoint]:
        """Lists the EKM proxy private endpoints on the Managed HSM.

        :returns: A paged object containing the EKM proxy private endpoints.
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.administration.KeyVaultEkmPrivateEndpoint]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.list_ekm_private_endpoints(**kwargs)
        converted_result = [KeyVaultEkmPrivateEndpoint._from_generated(endpoint) for endpoint in result.value or []]

        # We don't actually get a paged response from the generated method, so we mock the typical iteration methods
        def get_next(_=None):
            return converted_result

        def extract_data(_):
            return None, converted_result

        return ItemPaged(get_next, extract_data)

    @distributed_trace
    def get_ekm_private_endpoint_operation_status(  # pylint:disable=name-too-long
        self, job_id: str, **kwargs: Any
    ) -> KeyVaultEkmPrivateEndpointOperation:
        """Gets the status of an EKM proxy private endpoint create or delete operation.

        :param str job_id: The identifier of the private endpoint operation.

        :returns: The status of the private endpoint operation.
        :rtype: ~azure.keyvault.administration.KeyVaultEkmPrivateEndpointOperation
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = self._client.get_ekm_private_endpoint_operation_status(operation_id=job_id, **kwargs)
        return KeyVaultEkmPrivateEndpointOperation._from_generated(result)

    def __enter__(self) -> "KeyVaultEkmClient":
        self._client.__enter__()
        return self
