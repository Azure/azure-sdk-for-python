# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint:disable=too-many-lines,too-many-public-methods
import base64
import uuid
from datetime import datetime
from typing import Any, AsyncIterable, Mapping, Optional, Iterable, List, Dict

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from azure.keyvault.certificates import(
    AdministratorDetails,
    CertificatePolicy,
    CertificateOperation,
    Certificate,
    DeletedCertificate,
    CertificateBase,
    Contact,
    Issuer,
    IssuerBase
)
from .._shared import AsyncKeyVaultClientBase


class CertificateClient(AsyncKeyVaultClientBase):
    """"CertificateClient defines a high level interface for
    managing certificates in the specified vault.
    Example:
        .. literalinclude:: ../tests/test_examples_certificates_async.py
            :start-after: [START create_certificate_client]
            :end-before: [END create_certificate_client]
            :language: python
            :dedent: 4
            :caption: Creates a new instance of the Certificate client
    """

    # pylint:disable=protected-access
    @distributed_trace_async
    async def create_certificate(
        self,
        name: str,
        policy: CertificatePolicy,
        enabled: Optional[bool] = None,
        not_before: Optional[datetime] = None,
        expires: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Mapping[str, Any]
    ) -> CertificateOperation:
        """Creates a new certificate.

        If this is the first version, the certificate resource is created. This
        operation requires the certificates/create permission.

        :param name: The name of the certificate.
        :type name: str
        :param policy: The management policy for the certificate.
        :type policy:
         ~azure.security.keyvault.certificates._models.CertificatePolicy
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param not_before: Not before date of the secret in UTC
        :type not_before: datetime.datetime
        :param expires: Expiry date of the secret  in UTC.
        :type expires: datetime.datetime
        :param tags: Application specific metadata in the form of key-value pairs.
        :type tags: dict(str, str)
        :returns: The created CertificateOperation
        :rtype: ~azure.security.keyvault.certificates._models.CertificateOperation
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START create_certificate]
                :end-before: [END create_certificate]
                :language: python
                :caption: Create a certificate
                :dedent: 8
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.CertificateAttributes(
                enabled=enabled,
                not_before=not_before,
                expires=expires
            )
        else:
            attributes = None

        bundle = await self._client.create_certificate(
            vault_base_url=self.vault_url,
            certificate_name=name,
            certificate_policy=policy._to_certificate_policy_bundle(),
            certificate_attributes=attributes,
            tags=tags,
            **kwargs
        )

        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace_async
    async def get_certificate(
        self,
        name: str,
        version: Optional[str] = None,
        **kwargs: Mapping[str, Any]
    ) -> Certificate:
        """Gets information about a certificate.

        Gets information about a specific certificate. This operation requires
        the certificates/get permission.

        :param name: The name of the certificate in the given
         vault.
        :type name: str
        :param version: The version of the certificate.
        :type version: str
        :returns: An instance of Certificate
        :rtype: ~azure.security.keyvault.certificates._models.Certificate
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START get_certificate]
                :end-before: [END get_certificate]
                :language: python
                :caption: Get a certificate
                :dedent: 8
        """
        if version is None:
            version = ""

        bundle = await self._client.get_certificate(
            vault_base_url=self.vault_url,
            certificate_name=name,
            certificate_version=version,
            **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace_async
    async def delete_certificate(self, name: str, **kwargs: Mapping[str, Any]) -> DeletedCertificate:
        """Deletes a certificate from the key vault.

        Deletes all versions of a certificate object along with its associated
        policy. Delete certificate cannot be used to remove individual versions
        of a certificate object. This operation requires the
        certificates/delete permission.

        :param name: The name of the certificate.
        :type name: str
        :returns: The deleted certificate
        :rtype: ~azure.security.keyvault.certificates._models.DeletedCertificate
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START delete_certificate]
                :end-before: [END delete_certificate]
                :language: python
                :caption: Delete a certificate
                :dedent: 8
        """
        bundle = await self._client.delete_certificate(vault_base_url=self.vault_url, certificate_name=name, **kwargs)
        return DeletedCertificate._from_deleted_certificate_bundle(deleted_certificate_bundle=bundle)

    @distributed_trace_async
    async def get_deleted_certificate(self, name: str, **kwargs: Mapping[str, Any]) -> DeletedCertificate:
        """Retrieves information about the specified deleted certificate.

        Retrieves the deleted certificate information plus its attributes,
        such as retention interval, scheduled permanent deletion, and the
        current deletion recovery level. This operaiton requires the certificates/
        get permission.

        :param name: The name of the certificate.
        :type name: str
        :return: The deleted certificate
        :rtype: ~azure.security.keyvault.certificates._models.DeletedCertificate
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START get_deleted_certificate]
                :end-before: [END get_deleted_certificate]
                :language: python
                :caption: Get a deleted certificate
                :dedent: 8
        """
        bundle = await self._client.get_deleted_certificate(
            vault_base_url=self.vault_url,
            certificate_name=name,
            error_map={404: ResourceNotFoundError},
            **kwargs
        )
        return DeletedCertificate._from_deleted_certificate_bundle(deleted_certificate_bundle=bundle)

    @distributed_trace_async
    async def purge_deleted_certificate(self, name: str, **kwargs: Mapping[str, Any]) -> None:
        """Permanently deletes the specified deleted certificate.

        Performs an irreversible deletion of the specified certificate, without
        possibility for recovery. The operation is not available if the recovery
        level does not specified 'Purgeable'. This operation requires the
        certificate/purge permission.

        :param name: The name of the certificate
        :type name: str
        :return: None
        :rtype: None
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        await self._client.purge_deleted_certificate(vault_base_url=self.vault_url, certificate_name=name, **kwargs)

    @distributed_trace_async
    async def recover_deleted_certificate(self, name: str, **kwargs: Mapping[str, Any]) -> Certificate:
        """Recovers the deleted certificate back to its current version under
        /certificates.

        Performs the reversal of the Delete operation. THe operation is applicable
        in vaults enabled for soft-delete, and must be issued during the retention
        interval (available in the deleted certificate's attributes). This operation
        requires the certificates/recover permission.

        :param name: The name of the deleted certificate
        :type name: str
        :return: The recovered certificate
        :rtype ~azure.security.keyvault.certificates._models.Certificate
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START recover_deleted_certificate]
                :end-before: [END recover_deleted_certificate]
                :language: python
                :caption: Recover a deleted certificate
                :dedent: 8
        """
        bundle = await self._client.recover_deleted_certificate(
            vault_base_url=self.vault_url,
            certificate_name=name,
            **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace_async
    async def import_certificate(
        self,
        name: str,
        certificate_bytes: bytes,
        password: Optional[str] = None,
        policy: Optional[CertificatePolicy] = None,
        enabled: Optional[bool] = None,
        not_before: Optional[datetime] = None,
        expires: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Mapping[str, Any]
        ) -> Certificate:
        """Imports a certificate into a specified key vault.

        Imports an existing valid certificate, containing a private key, into
        Azure Key Vault. The certificate to be imported can be in either PFX or
        PEM format. If the certificate is in PEM format the PEM file must
        contain the key as well as x509 certificates. This operation requires
        the certificates/import permission.

        :param name: The name of the certificate.
        :type name: str
        :param certificate_bytes: Bytes of the ertificate object to import.
        This certificate needs to contain the private key.
        :type certificate_bytes: str
        :param password: If the private key in base64EncodedCertificate is
         encrypted, the password used for encryption.
        :type password: str
        :param policy: The management policy for the certificate.
        :type policy:
         ~azure.security.keyvault.v7_0.models.CertificatePolicy
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param not_before: Not before date of the secret in UTC
        :type not_before: datetime.datetime
        :param expires: Expiry date of the secret  in UTC.
        :type expires: datetime.datetime
        :param tags: Application specific metadata in the form of key-value
         pairs.
        :type tags: dict[str, str]
        :returns: The imported Certificate
        :rtype: ~azure.security.keyvault.certificates._models.Certificate
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.CertificateAttributes(
                enabled=enabled, not_before=not_before, expires=expires
            )
        else:
            attributes = None
        base64_encoded_certificate = base64.b64encode(certificate_bytes).decode("utf-8")
        bundle = await self._client.import_certificate(
            vault_base_url=self.vault_url,
            certificate_name=name,
            base64_encoded_certificate=base64_encoded_certificate,
            password=password,
            certificate_policy=CertificatePolicy._to_certificate_policy_bundle(policy),
            certificate_attributes=attributes,
            tags=tags,
            **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace_async
    async def get_policy(self, name: str, **kwargs: Mapping[str, Any]) -> CertificatePolicy:
        """Gets the policy for a certificate.

        Returns the specified certificate policy resources in the key
        vault. This operation requires the certificates/get permission.

        :param name: The name of the certificate in a given key vault.
        :type name: str
        :return: The certificate policy
        :rtype ~azure.security.keyvault.certificates._models.CertificatePolicy
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        bundle = await self._client.get_certificate_policy(
            vault_base_url=self.vault_url,
            certificate_name=name,
            **kwargs
        )
        return CertificatePolicy._from_certificate_policy_bundle(certificate_policy_bundle=bundle)

    @distributed_trace_async
    async def update_policy(
        self,
        name: str,
        policy: CertificatePolicy,
        **kwargs: Mapping[str, Any]
    ) -> CertificatePolicy:
        """Updates the policy for a certificate.

        Set specified members in the certificate policy. Leaves others as null.
        This operation requries the certificates/update permission.

        :param name: The name of the certificate in the given vault.
        :type name: str
        :param policy: The policy for the certificate.
        :type policy: ~azure.security.keyvault.certificates._models.CertificatePolicy
        :return: The certificate policy
        :rtype: ~azure.security.keyvault.certificates._models.CertificatePolicy
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        bundle = await self._client.update_certificate_policy(
            vault_base_url=self.vault_url,
            certificate_name=name,
            certificate_policy=policy._to_certificate_policy_bundle(),
            **kwargs
        )
        return CertificatePolicy._from_certificate_policy_bundle(certificate_policy_bundle=bundle)

    @distributed_trace_async
    async def update_certificate(
        self,
        name: str,
        version: Optional[str] = None,
        not_before: Optional[datetime] = None,
        expires: Optional[datetime] = None,
        enabled: Optional[bool] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Mapping[str, Any]
    ) -> Certificate:
        """Updates the specified attributes associated with the given certificate.

        The UpdateCertificate operation applies the specified update on the
        given certificate; the only elements updated are the certificate's
        attributes. This operation requires the certificates/update permission.

        :param name: The name of the certificate in the given key
         vault.
        :type name: str
        :param version: The version of the certificate.
        :type version: str
        :param not_before: Not before date of the secret in UTC
        :type not_before: datetime.datetime
        :param expires: Expiry date of the secret  in UTC.
        :type expires: datetime.datetime
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param tags: Application specific metadata in the form of key-value pairs.
        :type tags: dict(str, str)
        :returns: The updated Certificate
        :rtype: ~azure.security.keyvault.certificates._models.Certificate
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START update_certificate]
                :end-before: [END update_certificate]
                :language: python
                :caption: Update a certificate's attributes
                :dedent: 8
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.CertificateAttributes(
                enabled=enabled, not_before=not_before, expires=expires
            )
        else:
            attributes = None

        bundle = await self._client.update_certificate(
            vault_base_url=self.vault_url,
            certificate_name=name,
            certificate_version=version or "",
            certificate_attributes=attributes,
            tags=tags,
            **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace_async
    async def backup_certificate(self, name: str, **kwargs: Mapping[str, Any]) -> bytes:
        """Backs up the specified certificate.

        Requests that a backup of the specified certificate be downloaded
        to the client. All versions of the certificate will be downloaded.
        This operation requires the certificates/backup permission.

        :param name: The name of the certificate.
        :type name: str
        :return: the backup blob containing the backed up certificate.
        :rtype: bytes
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START backup_certificate]
                :end-before: [END backup_certificate]
                :language: python
                :caption: Get a certificate backup
                :dedent: 8
        """
        backup_result = await self._client.backup_certificate(
            vault_base_url=self.vault_url,
            certificate_name=name,
            error_map={404: ResourceNotFoundError},
            **kwargs
        )
        return backup_result.value

    @distributed_trace_async
    async def restore_certificate(self, backup: bytes, **kwargs: Mapping[str, Any]) -> Certificate:
        """Restores a backed up certificate to a vault.

        Restores a backed up certificate, and all its versions, to a vault.
        this operation requires the certificates/restore permission.

        :param backup: The backup blob associated with a certificate bundle.
        :type backup bytes
        :return: The restored Certificate
        :rtype: ~azure.security.keyvault.certificates._models.Certificate
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START restore_certificate]
                :end-before: [END restore_certificate]
                :language: python
                :caption: Restore a certificate backup
                :dedent: 8
        """
        bundle = await self._client.restore_certificate(
            vault_base_url=self.vault_url,
            certificate_bundle_backup=backup,
            error_map={409: ResourceExistsError},
            **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace
    def list_deleted_certificates(
        self,
        include_pending: Optional[bool] = None,
        **kwargs: Mapping[str, Any]
    ) -> AsyncIterable[DeletedCertificate]:
        """Lists the deleted certificates in the specified vault currently
        available for recovery.

        Retrieves the certificates in the current vault which are in a deleted
        state and ready for recovery or purging. This operation includes
        deletion-specific information. This operation requires the certificates/get/list
        permission. This operation can only be enabled on soft-delete enabled vaults.

        :param include_pending: Specifies whether to include certificates which are not
        completely provisioned.
        :type include_pending: bool
        :return: An iterator like instance of DeletedCertificate
        :rtype:
         typing.Generator[~azure.security.keyvault.certificates._models.DeletedCertificate]
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START list_deleted_certificates]
                :end-before: [END list_deleted_certificates]
                :language: python
                :caption: List all the deleted certificates
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)
        return self._client.get_deleted_certificates(
            vault_base_url=self._vault_url,
            maxresults=max_page_size,
            include_pending=include_pending,
            cls=lambda objs: [DeletedCertificate._from_deleted_certificate_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_certificates(
        self,
        include_pending: Optional[bool] = None,
        **kwargs: Mapping[str, Any]
    ) -> AsyncIterable[CertificateBase]:
        """List certificates in the key vault.

        The GetCertificates operation returns the set of certificates resources
        in the key vault. This operation requires the
        certificates/list permission.

        :param include_pending: Specifies whether to include certificates
         which are not completely provisioned.
        :type include_pending: bool
        :returns: An iterator like instance of CertificateBase
        :rtype:
         typing.Generator[~azure.security.keyvault.certificates._models.CertificateBase]
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START list_certificates]
                :end-before: [END list_certificates]
                :language: python
                :caption: List all certificates
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)
        return self._client.get_certificates(
            vault_base_url=self._vault_url,
            maxresults=max_page_size,
            include_pending=include_pending,
            cls=lambda objs: [CertificateBase._from_certificate_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_certificate_versions(self, name: str, **kwargs: Mapping[str, Any]) -> AsyncIterable[CertificateBase]:
        """List the versions of a certificate.

        The GetCertificateVersions operation returns the versions of a
        certificate in the key vault. This operation requires the
        certificates/list permission.

        :param name: The name of the certificate.
        :type name: str
        :returns: An iterator like instance of CertificateBase
        :rtype:
         typing.Generator[~azure.security.keyvault.certificates._models.CertificateBase]
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START list_certificate_versions]
                :end-before: [END list_certificate_versions]
                :language: python
                :caption: List all versions of a certificate
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)
        return self._client.get_certificate_versions(
            vault_base_url=self._vault_url,
            certificate_name=name,
            maxresults=max_page_size,
            cls=lambda objs: [CertificateBase._from_certificate_item(x) for x in objs],
            **kwargs)

    @distributed_trace_async
    async def create_contacts(self, contacts: Iterable[Contact], **kwargs: Mapping[str, Any]) -> Iterable[Contact]:
        """Sets the certificate contacts for the key vault.

        Sets the certificate contacts for the key vault. This
        operation requires the certificates/managecontacts permission.

        :param contacts: The contact list for the vault certificates.
        :type contacts: list[~azure.keyvault.v7_0.models.Contact]
        :returns: The created list of contacts
        :rtype: Iterator[~azure.security.keyvault.certificates._models.Contact]
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        contacts = await self._client.set_certificate_contacts(
            vault_base_url=self.vault_url,
            contact_list=contacts,
            **kwargs
        )
        return (Contact._from_certificate_contacts_item(contact_item=item) for item in contacts.contact_list)

    @distributed_trace_async
    async def get_contacts(self, **kwargs: Mapping[str, Any]) -> AsyncIterable[Contact]:
        """Gets the certificate contacts for the key vault.

        Returns the set of certificate contact resources in the specified
        key vault. This operation requires the certificates/managecontacts
        permission.

        :return: The certificate contacts for the key vault.
        :rtype: Iterator[azure.security.keyvault.certificates._models.Contact]
        """
        contacts = await self._client.get_certificate_contacts(vault_base_url=self._vault_url, **kwargs)
        return (Contact._from_certificate_contacts_item(contact_item=item) for item in contacts.contact_list)

    @distributed_trace_async
    async def delete_contacts(self, **kwargs: Mapping[str, Any]) -> AsyncIterable[Contact]:
        """Deletes the certificate contacts for the key vault.

        Deletes the certificate contacts for the key vault certificate.
        This operation requires the certificates/managecontacts permission.

        :return: Contacts
        :rtype: Iterator[~azure.security.certificates._models.Contact]
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        contacts = await self._client.delete_certificate_contacts(vault_base_url=self.vault_url, **kwargs)
        return (Contact._from_certificate_contacts_item(contact_item=item) for item in contacts.contact_list)

    @distributed_trace_async
    async def get_certificate_operation(self, name: str, **kwargs: Mapping[str, Any]) -> CertificateOperation:
        """Gets the creation operation of a certificate.

        Gets the creation operation associated with a specified certificate.
        This operation requires the certificates/get permission.

        :param name: The name of the certificate.
        :type name: str
        :returns: The created CertificateOperation
        :rtype: ~azure.security.keyvault.v7_0.models.CertificateOperation
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """

        bundle = await self._client.get_certificate_operation(
            vault_base_url=self.vault_url,
            certificate_name=name,
            **kwargs
        )
        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace_async
    async def delete_certificate_operation(self, name: str, **kwargs: Mapping[str, Any]) -> CertificateOperation:
        """Deletes the creation operation for a specific certificate.

        Deletes the creation operation for a specified certificate that is in
        the process of being created. The certificate is no longer created.
        This operation requires the certificates/update permission.

        :param name: The name of the certificate.
        :type name: str
        :return: The deleted CertificateOperation
        :rtype: ~azure.security.keyvault.certificates._models.CertificateOperation
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        bundle = await self._client.delete_certificate_operation(
            vault_base_url=self.vault_url,
            certificate_name=name,
            **kwargs
        )
        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace_async
    async def cancel_certificate_operation(self, name: str, **kwargs: Mapping[str, Any]) -> CertificateOperation:
        """Updates a certificate operation.

        Updates a certificate creation operation that is already in progress.
        This operation requires the certificates/update permission.

        :param name: The name of the certificate.
        :type name: str
        :returns: The updated certificate operation
        :rtype: ~azure.security.keyvault.certificates._models.CertificateOperation
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        bundle = await self._client.update_certificate_operation(
            vault_base_url=self.vault_url,
            certificate_name=name,
            cancellation_requested=True,
            **kwargs
        )
        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace_async
    async def get_pending_certificate_signing_request(
            self,
            name: str,
            custom_headers: Optional[Dict[str, str]] = None,
            **kwargs: Mapping[str, Any]) -> str:
        """Gets the Base64 pending certificate signing request (PKCS-10).
        :param name: The name of the certificate
        :type name: str
        :param custom_headers: headers that will be added to the request
        :type custom_headers: dict
        :return: Base64 encoded pending certificate signing request (PKCS-10).
        :rtype: str
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        error_map = kwargs.pop('error_map', None)

        vault_base_url = self.vault_url
        # Construct URL
        url = '/certificates/{certificate-name}/pending'
        path_format_arguments = {
            'vaultBaseUrl': self._client._serialize.url("vault_base_url", vault_base_url, 'str', skip_quote=True),
            'certificate-name': self._client._serialize.url("certificate_name", name, 'str')
        }
        url = self._client._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._client._serialize.query(
            name="self.api_version",
            data=self._client.api_version,
            data_type='str'
        )

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/pkcs10'
        if self._client._config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client._client.get(
            url=url,
            params=query_parameters,
            headers=header_parameters
        )
        pipeline_response = await self._client._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            self._client.map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise self._client.models.KeyVaultErrorException(response, self._client._deserialize)

        deserialized = None

        if response.status_code == 200:
            deserialized = response.body() if hasattr(response, 'body') else response.content

        return deserialized

    @distributed_trace_async
    async def merge_certificate(
        self,
        name: str,
        x509_certificates: List[bytearray],
        enabled: Optional[bool] = None,
        not_before: Optional[datetime] = None,
        expires: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Mapping[str, Any]
    ) -> Certificate:
        """Merges a certificate or a certificate chain with a key pair existing on the server.

        Performs the merging of a certificate or certificate chain with a key pair currently
        available in the service. This operation requires the certificates/create permission.

        :param name: The name of the certificate
        :type name: str
        :param x509_certificates: The certificate or the certificate chain to merge.
        :type x509_certificates: list[bytearray]
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param not_before: Not before date of the secret in UTC
        :type not_before: datetime.datetime
        :param expires: Expiry date of the secret  in UTC.
        :type expires: datetime.datetime
        :param tags: Application specific metadata in the form of key-value pairs.
        :type tags: dict[str, str]
        :return: The merged certificate operation
        :rtype: ~azure.security.keyvault.certificates._models.CertificateOperation
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.CertificateAttributes(
                enabled=enabled, not_before=not_before, expires=expires
            )
        else:
            attributes = None
        bundle = await self._client.merge_certificate(
            vault_base_url=self.vault_url,
            certificate_name=name,
            x509_certificates=x509_certificates,
            certificate_attributes=attributes,
            tags=tags,
            **kwargs
        )
        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace_async
    async def get_issuer(self, name: str, **kwargs: Mapping[str, Any]) -> Issuer:
        """Gets the specified certificate issuer.

        Returns the specified certificate issuer resources in the key vault.
        This operation requires the certificates/manageissuers/getissuers permission.

        :param name: The name of the issuer.
        :type name: str
        :return: The specified certificate issuer.
        :rtype: ~azure.security.keyvault.certificates._models.Issuer
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        issuer_bundle = await self._client.get_certificate_issuer(
            vault_base_url=self.vault_url,
            issuer_name=name,
            **kwargs
        )
        return Issuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace_async
    async def create_issuer(
        self,
        name: str,
        provider: str,
        account_id: Optional[str] = None,
        password: Optional[str] = None,
        organization_id: Optional[str] = None,
        admin_details: Optional[List[AdministratorDetails]] = None,
        enabled: Optional[bool] = None,
        **kwargs: Mapping[str, Any]
    ) -> Issuer:
        """Sets the specified certificate issuer.

        The SetCertificateIssuer operation adds or updates the specified
        certificate issuer. This operation requires the certificates/setissuers
        permission.

        :param name: The name of the issuer.
        :type name: str
        :param provider: The issuer provider.
        :type provider: str
        :param account_id: The user name/account name/account id.
        :type account_id: str
        :param password: The password/secret/account key.
        :type password: str
        :param organization_id: Id of the organization.
        :type organization_id: str
        :param admin_details: Details of the organization administrators of the certificate issuer.
        :type admin_details: ~azure.security.keyvault.certificates._models.AdministratorDetails
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :returns: The created Issuer
        :rtype: ~azure.security.keyvault.certificates._models.Issuer
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        if account_id or password:
            issuer_credentials = self._client.models.IssuerCredentials(account_id=account_id, password=password)
        else:
            issuer_credentials = None
        if admin_details and admin_details[0]:
            admin_details_to_pass = list(self._client.models.AdministratorDetails(
                                            first_name=admin_detail.first_name,
                                            last_name=admin_detail.last_name,
                                            email_address=admin_detail.email,
                                            phone=admin_detail.phone
                                        ) for admin_detail in admin_details)
        else:
            admin_details_to_pass = admin_details
        if organization_id or admin_details:
            organization_details = self._client.models.OrganizationDetails(
                id=organization_id,
                admin_details=admin_details_to_pass
            )
        else:
            organization_details = None
        if enabled is not None:
            issuer_attributes = self._client.models.IssuerAttributes(enabled=enabled)
        else:
            issuer_attributes = None
        issuer_bundle = await self._client.set_certificate_issuer(
            vault_base_url=self.vault_url,
            issuer_name=name,
            provider=provider,
            credentials=issuer_credentials,
            organization_details=organization_details,
            attributes=issuer_attributes,
            **kwargs
        )
        return Issuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace_async
    async def update_issuer(
        self,
        name: str,
        provider: Optional[str] = None,
        account_id: Optional[str] = None,
        password: Optional[str] = None,
        organization_id: Optional[str] = None,
        admin_details: Optional[List[AdministratorDetails]] = None,
        enabled: Optional[bool] = None,
        **kwargs: Mapping[str, Any]
    ) -> Issuer:
        """Updates the specified certificate issuer.

        Performs an update on the specified certificate issuer entity.
        THis operation requires the certificates/setissuers permission.

        :param name: The name of the issuer.
        :type name: str
        :param provider: The issuer provider.
        :type provider: str
        :param account_id: The username / account name / account key.
        :type account_id: str
        :param password: The password / secret / account key.
        :type password: str
        :param organization_id: Id of the organization
        :type organization_id: str
        :param admin_details: Details of the organization administrators of the certificate issuer.
        :type admin_details: ~azure.security.keyvault.certificates._models.AdministratorDetails
        :param enabled: Determines whether the issuer is enabled.
        :type enabled: bool
        :return: The updated issuer
        :rtype: ~azure.security.keyvault.certificates._models.Issuer
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        if account_id or password:
            issuer_credentials = self._client.models.IssuerCredentials(account_id=account_id, password=password)
        else:
            issuer_credentials = None
        if admin_details and admin_details[0]:
            admin_details_to_pass = list(self._client.models.AdministratorDetails(
                                            first_name=admin_detail.first_name,
                                            last_name=admin_detail.last_name,
                                            email_address=admin_detail.email,
                                            phone=admin_detail.phone
                                        ) for admin_detail in admin_details)
        else:
            admin_details_to_pass = admin_details
        if organization_id or admin_details:
            organization_details = self._client.models.OrganizationDetails(
                id=organization_id,
                admin_details=admin_details_to_pass
            )
        else:
            organization_details = None
        if enabled is not None:
            issuer_attributes = self._client.models.IssuerAttributes(enabled=enabled)
        else:
            issuer_attributes = None
        issuer_bundle = await self._client.update_certificate_issuer(
            vault_base_url=self.vault_url,
            issuer_name=name,
            provider=provider,
            credentials=issuer_credentials,
            organization_details=organization_details,
            attributes=issuer_attributes,
            **kwargs
        )
        return Issuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace_async
    async def delete_issuer(self, name: str, **kwargs: Mapping[str, Any]) -> Issuer:
        """Deletes the specified certificate issuer.

        Permanently removes the specified certificate issuer from the vault.
        This operation requires the certificates/manageissuers/deleteissuers permission.

        :param name: The name of the issuer.
        :type name: str
        :return: Issuer
        :rtype: ~azure.security.keyvault.certificates._models.Issuer
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        issuer_bundle = await self._client.delete_certificate_issuer(
            vault_base_url=self.vault_url,
            issuer_name=name,
            **kwargs
        )
        return Issuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace
    def list_issuers(self, **kwargs: Mapping[str, Any]) -> AsyncIterable[IssuerBase]:
        """List certificate issuers for the key vault.

        Returns the set of certificate issuer resources in the key
        vault. This operation requires the certificates/manageissuers/getissuers
        permission.

        :return: An iterator like instance of Issuers
        :rtype: Iterable[~azure.security.keyvault.certificates._models.Issuer]
        :raises:
         :class:`KeyVaultErrorException<azure.keyvault.v7_0.models.KeyVaultErrorException>`
        """
        max_page_size = kwargs.pop("max_page_size", None)
        return self._client.get_certificate_issuers(
            vault_base_url=self.vault_url,
            maxresults=max_page_size,
            cls=lambda objs: [IssuerBase._from_issuer_item(x) for x in objs],
            **kwargs
        )
