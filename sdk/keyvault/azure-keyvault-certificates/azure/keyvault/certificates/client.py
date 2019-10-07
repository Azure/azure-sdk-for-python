# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint:disable=too-many-lines,too-many-public-methods
import base64
import uuid
from functools import partial

from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from ._shared import KeyVaultClientBase
from ._shared.exceptions import error_map as _error_map
from .models import (
    Certificate,
    CertificateProperties,
    CertificatePolicy,
    DeletedCertificate,
    Issuer,
    IssuerProperties,
    Contact,
    CertificateOperation,
)
from ._polling import CreateCertificatePoller

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, List, Optional, Iterable


class CertificateClient(KeyVaultClientBase):
    """CertificateClient defines a high level interface for
    managing certificates in the specified vault.
    Example:
        .. literalinclude:: ../tests/test_examples_certificates.py
            :start-after: [START create_certificate_client]
            :end-before: [END create_certificate_client]
            :language: python
            :caption: Create a new ``CertificateClient``
            :dedent: 4
    """

    # pylint:disable=protected-access

    @distributed_trace
    def create_certificate(
        self,
        name,  # type: str
        policy=None,  # type: Optional[CertificatePolicy]
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller
        """Creates a new certificate.

        If this is the first version, the certificate resource is created. This
        operation requires the certificates/create permission.

        :param str name: The name of the certificate.
        :param policy: The management policy for the certificate.
        :type policy:
         ~azure.keyvault.certificates.models.CertificatePolicy
        :returns: An LROPoller for the create certificate operation. Waiting on the poller
         gives you the certificate if creation is successful, the CertificateOperation if not.
        :rtype: ~azure.core.polling.LROPoller[~azure.keyvault.certificates.models.Certificate or
         ~azure.keyvault.certificates.models.CertificateOperation]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Determines whether the object is enabled.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START create_certificate]
                :end-before: [END create_certificate]
                :language: python
                :caption: Create a certificate
                :dedent: 8
        """

        enabled = kwargs.pop("enabled", None)
        tags = kwargs.pop("enabled", None)

        if enabled is not None:
            attributes = self._client.models.CertificateAttributes(enabled=enabled)
        else:
            attributes = None

        if not policy:
            # pylint: disable=protected-access
            policy = CertificatePolicy._get_default_certificate_policy()

        cert_bundle = self._client.create_certificate(
            vault_base_url=self.vault_endpoint,
            certificate_name=name,
            certificate_policy=policy._to_certificate_policy_bundle(),
            certificate_attributes=attributes,
            tags=tags,
            **kwargs
        )

        create_certificate_operation = CertificateOperation._from_certificate_operation_bundle(cert_bundle)

        command = partial(self.get_certificate_operation, name=name, **kwargs)

        get_certificate_command = partial(self.get_certificate_with_policy, name=name, **kwargs)

        create_certificate_polling = CreateCertificatePoller(get_certificate_command=get_certificate_command)
        return LROPoller(command, create_certificate_operation, None, create_certificate_polling)

    @distributed_trace
    def get_certificate_with_policy(self, name, **kwargs):
        # type: (str, **Any) -> Certificate
        """Gets a certificate and returns it's management policy as well.


        This operation requires the certificates/get permission. Does not accept the
        version of the certificate as a parameter. If you wish to specify version, use
        the get_certificate function and specify version.

        :param str name: The name of the certificate in the given vault.
        :returns: An instance of Certificate
        :rtype: ~azure.keyvault.certificates.models.Certificate
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START get_certificate]
                :end-before: [END get_certificate]
                :language: python
                :caption: Get a certificate
                :dedent: 8
        """
        bundle = self._client.get_certificate(
            vault_base_url=self.vault_endpoint,
            certificate_name=name,
            certificate_version="",
            error_map=_error_map,
            **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace
    def get_certificate(self, name, version, **kwargs):
        # type: (str, str, **Any) -> Certificate
        """Gets a certificate by version without returning it's management policy.

        If you wish to not specify a version or to get the certificate's policy as well,
        use the get_certificate_with_policy function.

        :param str name: The name of the certificate in the given vault.
        :param str version: The version of the certificate.
        :returns: An instance of Certificate
        :rtype: ~azure.keyvault.certificates.models.Certificate
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START get_certificate]
                :end-before: [END get_certificate]
                :language: python
                :caption: Get a certificate
                :dedent: 8
        """
        bundle = self._client.get_certificate(
            vault_base_url=self.vault_endpoint,
            certificate_name=name,
            certificate_version=version,
            error_map=_error_map,
            **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace
    def delete_certificate(self, name, **kwargs):
        # type: (str, **Any) -> DeletedCertificate
        """Deletes a certificate from the key vault.

        Deletes all versions of a certificate object along with its associated
        policy. Delete certificate cannot be used to remove individual versions
        of a certificate object. This operation requires the
        certificates/delete permission.

        :param str name: The name of the certificate.
        :returns: The deleted certificate
        :rtype: ~azure.keyvault.certificates.models.DeletedCertificate
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START delete_certificate]
                :end-before: [END delete_certificate]
                :language: python
                :caption: Delete a certificate
                :dedent: 8
        """
        bundle = self._client.delete_certificate(
            vault_base_url=self.vault_endpoint, certificate_name=name, error_map=_error_map, **kwargs
        )
        return DeletedCertificate._from_deleted_certificate_bundle(deleted_certificate_bundle=bundle)

    @distributed_trace
    def get_deleted_certificate(self, name, **kwargs):
        # type: (str, **Any) -> DeletedCertificate
        """Retrieves information about the specified deleted certificate.

        Retrieves the deleted certificate information plus its attributes,
        such as retention interval, scheduled permanent deletion, and the
        current deletion recovery level. This operation requires the certificates/
        get permission.

        :param str name: The name of the certificate.
        :return: The deleted certificate
        :rtype: ~azure.keyvault.certificates.models.DeletedCertificate
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START get_deleted_certificate]
                :end-before: [END get_deleted_certificate]
                :language: python
                :caption: Get a deleted certificate
                :dedent: 8
        """
        bundle = self._client.get_deleted_certificate(
            vault_base_url=self.vault_endpoint, certificate_name=name, error_map=_error_map, **kwargs
        )
        return DeletedCertificate._from_deleted_certificate_bundle(deleted_certificate_bundle=bundle)

    @distributed_trace
    def purge_deleted_certificate(self, name, **kwargs):
        # type: (str, **Any) -> None
        """Permanently deletes the specified deleted certificate.

        Performs an irreversible deletion of the specified certificate, without
        possibility for recovery. The operation is not available if the recovery
        level does not specified 'Purgeable'. This operation requires the
        certificate/purge permission.

        :param str name: The name of the certificate
        :return: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        self._client.purge_deleted_certificate(vault_base_url=self.vault_endpoint, certificate_name=name, **kwargs)

    @distributed_trace
    def recover_deleted_certificate(self, name, **kwargs):
        # type: (str, **Any) -> Certificate
        """Recovers the deleted certificate back to its current version under
        /certificates.

        Performs the reversal of the Delete operation. THe operation is applicable
        in vaults enabled for soft-delete, and must be issued during the retention
        interval (available in the deleted certificate's attributes). This operation
        requires the certificates/recover permission.

        :param str name: The name of the deleted certificate
        :return: The recovered certificate
        :rtype: ~azure.keyvault.certificates.models.Certificate
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START recover_deleted_certificate]
                :end-before: [END recover_deleted_certificate]
                :language: python
                :caption: Recover a deleted certificate
                :dedent: 8
        """
        bundle = self._client.recover_deleted_certificate(
            vault_base_url=self.vault_endpoint, certificate_name=name, **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace
    def import_certificate(
        self,
        name,  # type: str
        certificate_bytes,  # type: bytes
        password=None,  # type: Optional[str]
        policy=None,  # type: Optional[CertificatePolicy]
        **kwargs  # type: **Any
    ):
        # type: (...) -> Certificate
        """Imports a certificate into a specified key vault.

        Imports an existing valid certificate, containing a private key, into
        Azure Key Vault. The certificate to be imported can be in either PFX or
        PEM format. If the certificate is in PEM format the PEM file must
        contain the key as well as x509 certificates. This operation requires
        the certificates/import permission.

        :param str name: The name of the certificate.
        :param bytes certificate_bytes: Bytes of the certificate object to import. This certificate
            needs to contain the private key.
        :param str password: If the private key in the passed in certificate is encrypted, it is the
            password used for encryption.
        :param policy: The management policy for the certificate.
        :type policy:
         ~azure.keyvault.certificates.models.CertificatePolicy
        :returns: The imported Certificate
        :rtype: ~azure.keyvault.certificates.models.Certificate
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Determines whether the object is enabled.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.
        """

        enabled = kwargs.pop("enabled", None)
        tags = kwargs.pop("tags", None)

        if enabled is not None:
            attributes = self._client.models.CertificateAttributes(enabled=enabled)
        else:
            attributes = None
        base64_encoded_certificate = base64.b64encode(certificate_bytes).decode("utf-8")
        bundle = self._client.import_certificate(
            vault_base_url=self.vault_endpoint,
            certificate_name=name,
            base64_encoded_certificate=base64_encoded_certificate,
            password=password,
            certificate_policy=policy._to_certificate_policy_bundle(),
            certificate_attributes=attributes,
            tags=tags,
            **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace
    def get_policy(self, certificate_name, **kwargs):
        # type: (str, **Any) -> CertificatePolicy
        """Gets the policy for a certificate.

        Returns the specified certificate policy resources in the key
        vault. This operation requires the certificates/get permission.

        :param str certificate_name: The name of the certificate in a given key vault.
        :return: The certificate policy
        :rtype: ~azure.keyvault.certificates.models.CertificatePolicy
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        bundle = self._client.get_certificate_policy(
            vault_base_url=self.vault_endpoint, certificate_name=certificate_name, **kwargs
        )
        return CertificatePolicy._from_certificate_policy_bundle(certificate_policy_bundle=bundle)

    @distributed_trace
    def update_policy(self, certificate_name, policy, **kwargs):
        # type: (str, CertificatePolicy, **Any) -> CertificatePolicy
        """Updates the policy for a certificate.

        Set specified members in the certificate policy. Leaves others as null.
        This operation requires the certificates/update permission.

        :param str certificate_name: The name of the certificate in the given vault.
        :param policy: The policy for the certificate.
        :type policy: ~azure.keyvault.certificates.models.CertificatePolicy
        :return: The certificate policy
        :rtype: ~azure.keyvault.certificates.models.CertificatePolicy
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        bundle = self._client.update_certificate_policy(
            vault_base_url=self.vault_endpoint,
            certificate_name=certificate_name,
            certificate_policy=policy._to_certificate_policy_bundle(),
            **kwargs
        )
        return CertificatePolicy._from_certificate_policy_bundle(certificate_policy_bundle=bundle)

    @distributed_trace
    def update_certificate_properties(
        self,
        name,  # type: str
        version=None,  # type: Optional[str]
        **kwargs  # type: **Any
    ):
        # type: (...) -> Certificate
        """Updates the specified attributes associated with the given certificate.

        The UpdateCertificate operation applies the specified update on the
        given certificate; the only elements updated are the certificate's
        attributes. This operation requires the certificates/update permission.

        :param str name: The name of the certificate in the given key
            vault.
        :param str version: The version of the certificate.
        :returns: The updated Certificate
        :rtype: ~azure.keyvault.certificates.models.Certificate
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Determines whether the object is enabled.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START update_certificate]
                :end-before: [END update_certificate]
                :language: python
                :caption: Update a certificate's attributes
                :dedent: 8
        """

        enabled = kwargs.pop("enabled", None)
        tags = kwargs.pop("tags", None)

        if enabled is not None:
            attributes = self._client.models.CertificateAttributes(enabled=enabled)
        else:
            attributes = None

        bundle = self._client.update_certificate(
            vault_base_url=self.vault_endpoint,
            certificate_name=name,
            certificate_version=version or "",
            certificate_attributes=attributes,
            tags=tags,
            **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace
    def backup_certificate(self, name, **kwargs):
        # type: (str, **Any) -> bytes
        """Backs up the specified certificate.

        Requests that a backup of the specified certificate be downloaded
        to the client. All versions of the certificate will be downloaded.
        This operation requires the certificates/backup permission.

        :param str name: The name of the certificate.
        :return: the backup blob containing the backed up certificate.
        :rtype: bytes
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START backup_certificate]
                :end-before: [END backup_certificate]
                :language: python
                :caption: Get a certificate backup
                :dedent: 8
        """
        backup_result = self._client.backup_certificate(
            vault_base_url=self.vault_endpoint, certificate_name=name, error_map=_error_map, **kwargs
        )
        return backup_result.value

    @distributed_trace
    def restore_certificate(self, backup, **kwargs):
        # type: (bytes, **Any) -> Certificate
        """Restores a backed up certificate to a vault.

        Restores a backed up certificate, and all its versions, to a vault.
        this operation requires the certificates/restore permission.

        :param bytes backup: The backup blob associated with a certificate bundle.
        :return: The restored Certificate
        :rtype: ~azure.keyvault.certificates.models.Certificate
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START restore_certificate]
                :end-before: [END restore_certificate]
                :language: python
                :caption: Restore a certificate backup
                :dedent: 8
        """
        bundle = self._client.restore_certificate(
            vault_base_url=self.vault_endpoint, certificate_bundle_backup=backup, **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace
    def list_deleted_certificates(self, include_pending=None, **kwargs):
        # type: (Optional[bool], **Any) -> Iterable[DeletedCertificate]
        """Lists the deleted certificates in the specified vault currently
        available for recovery.

        Retrieves the certificates in the current vault which are in a deleted
        state and ready for recovery or purging. This operation includes
        deletion-specific information. This operation requires the certificates/get/list
        permission. This operation can only be enabled on soft-delete enabled vaults.

        :param bool include_pending: Specifies whether to include certificates which are not
            completely provisioned.
        :return: An iterator like instance of DeletedCertificate
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.keyvault.certificates.models.DeletedCertificate]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START list_deleted_certificates]
                :end-before: [END list_deleted_certificates]
                :language: python
                :caption: List all the deleted certificates
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)
        return self._client.get_deleted_certificates(
            vault_base_url=self._vault_endpoint,
            maxresults=max_page_size,
            include_pending=include_pending,
            cls=lambda objs: [
                DeletedCertificate._from_deleted_certificate_item(deleted_certificate_item=x) for x in objs
            ],
            **kwargs
        )

    @distributed_trace
    def list_certificates(self, include_pending=None, **kwargs):
        # type: (Optional[bool], **Any) -> Iterable[CertificateProperties]
        """List certificates in the key vault.

        The GetCertificates operation returns the set of certificates resources
        in the key vault. This operation requires the
        certificates/list permission.

        :param bool include_pending: Specifies whether to include certificates
            which are not completely provisioned.
        :returns: An iterator like instance of CertificateProperties
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.keyvault.certificates.models.CertificateProperties]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START list_certificates]
                :end-before: [END list_certificates]
                :language: python
                :caption: List all certificates
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)
        return self._client.get_certificates(
            vault_base_url=self._vault_endpoint,
            maxresults=max_page_size,
            include_pending=include_pending,
            cls=lambda objs: [CertificateProperties._from_certificate_item(certificate_item=x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_certificate_versions(self, name, **kwargs):
        # type: (str, **Any) -> Iterable[CertificateProperties]
        """List the versions of a certificate.

        The GetCertificateVersions operation returns the versions of a
        certificate in the key vault. This operation requires the
        certificates/list permission.

        :param str name: The name of the certificate.
        :returns: An iterator like instance of CertificateProperties
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.keyvault.certificates.models.CertificateProperties]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START list_certificate_versions]
                :end-before: [END list_certificate_versions]
                :language: python
                :caption: List all versions of a certificate
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)
        return self._client.get_certificate_versions(
            vault_base_url=self._vault_endpoint,
            certificate_name=name,
            maxresults=max_page_size,
            cls=lambda objs: [CertificateProperties._from_certificate_item(certificate_item=x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def create_contacts(self, contacts, **kwargs):
        # type: (Iterable[Contact], **Any) -> List[Contact]
        """Sets the certificate contacts for the key vault.

        Sets the certificate contacts for the key vault. This
        operation requires the certificates/managecontacts permission.

        :param contacts: The contact list for the vault certificates.
        :type contacts: list[~azure.keyvault.certificates.models.Contact]
        :returns: The created list of contacts
        :rtype: list[~azure.keyvault.certificates.models.Contact]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START create_contacts]
                :end-before: [END create_contacts]
                :language: python
                :caption: Create contacts
                :dedent: 8
        """
        contacts = self._client.set_certificate_contacts(
            vault_base_url=self.vault_endpoint,
            contact_list=[c._to_certificate_contacts_item() for c in contacts],
            **kwargs
        )
        return [Contact._from_certificate_contacts_item(contact_item=item) for item in contacts.contact_list]

    @distributed_trace
    def get_contacts(self, **kwargs):
        # type: (**Any) -> List[Contact]
        """Gets the certificate contacts for the key vault.

        Returns the set of certificate contact resources in the specified
        key vault. This operation requires the certificates/managecontacts
        permission.

        :return: The certificate contacts for the key vault.
        :rtype: list[~azure.keyvault.certificates.models.Contact]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START get_contacts]
                :end-before: [END get_contacts]
                :language: python
                :caption: Get contacts
                :dedent: 8
        """
        contacts = self._client.get_certificate_contacts(vault_base_url=self._vault_endpoint, **kwargs)
        return [Contact._from_certificate_contacts_item(contact_item=item) for item in contacts.contact_list]

    @distributed_trace
    def delete_contacts(self, **kwargs):
        # type: (**Any) -> List[Contact]
        """Deletes the certificate contacts for the key vault.

        Deletes the certificate contacts for the key vault certificate.
        This operation requires the certificates/managecontacts permission.

        :return: Contacts
        :rtype: list[~azure.keyvault.certificates.models.Contact]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START delete_contacts]
                :end-before: [END delete_contacts]
                :language: python
                :caption: Delete contacts
                :dedent: 8
        """
        contacts = self._client.delete_certificate_contacts(vault_base_url=self.vault_endpoint, **kwargs)
        return [Contact._from_certificate_contacts_item(contact_item=item) for item in contacts.contact_list]

    @distributed_trace
    def get_certificate_operation(self, name, **kwargs):
        # type: (str, **Any) -> CertificateOperation
        """Gets the creation operation of a certificate.

        Gets the creation operation associated with a specified certificate.
        This operation requires the certificates/get permission.

        :param str name: The name of the certificate.
        :returns: The created CertificateOperation
        :rtype: ~azure.keyvault.certificates.models.CertificateOperation
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors
        """

        bundle = self._client.get_certificate_operation(
            vault_base_url=self.vault_endpoint, certificate_name=name, error_map=_error_map, **kwargs
        )
        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace
    def delete_certificate_operation(self, name, **kwargs):
        # type: (str, **Any) -> CertificateOperation
        """Deletes the creation operation for a specific certificate.

        Deletes the creation operation for a specified certificate that is in
        the process of being created. The certificate is no longer created.
        This operation requires the certificates/update permission.

        :param str name: The name of the certificate.
        :return: The deleted CertificateOperation
        :rtype: ~azure.keyvault.certificates.models.CertificateOperation
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        bundle = self._client.delete_certificate_operation(
            vault_base_url=self.vault_endpoint, certificate_name=name, **kwargs
        )
        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace
    def cancel_certificate_operation(self, name, **kwargs):
        # type: (str, **Any) -> CertificateOperation
        """Cancels a certificate operation.

        Cancels a certificate creation operation that is already in progress.
        This operation requires the certificates/update permission.

        :param str name: The name of the certificate.
        :returns: The cancelled certificate operation
        :rtype: ~azure.keyvault.certificates.models.CertificateOperation
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        bundle = self._client.update_certificate_operation(
            vault_base_url=self.vault_endpoint, certificate_name=name, cancellation_requested=True, **kwargs
        )
        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace
    def merge_certificate(
        self,
        name,  # type: str
        x509_certificates,  # type: List[bytearray]
        **kwargs  # type: **Any
    ):
        # type: (...) -> Certificate
        """Merges a certificate or a certificate chain with a key pair existing on the server.

        Performs the merging of a certificate or certificate chain with a key pair currently
        available in the service. This operation requires the certificates/create permission.
        Make sure when creating the certificate to merge using create_certificate that you set
        it's issuer to 'Unknown'. This way Key Vault knows that the certificate will not be signed
        by an issuer known to it.

        :param str name: The name of the certificate
        :param x509_certificates: The certificate or the certificate chain to merge.
        :type x509_certificates: list[bytearray]
        :return: The merged certificate
        :rtype: ~azure.keyvault.certificates.models.Certificate
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Determines whether the object is enabled.
            - *tags (dict[str, str])* - Application specific metadata in the form of key-value pairs.
        """

        enabled = kwargs.pop("enabled", None)
        tags = kwargs.pop("tags", None)

        if enabled is not None:
            attributes = self._client.models.CertificateAttributes(enabled=enabled)
        else:
            attributes = None
        bundle = self._client.merge_certificate(
            vault_base_url=self.vault_endpoint,
            certificate_name=name,
            x509_certificates=x509_certificates,
            certificate_attributes=attributes,
            tags=tags,
            **kwargs
        )
        return Certificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace
    def get_pending_certificate_signing_request(
        self,
        name,  # type: str
        **kwargs  # type: **Any
    ):
        # type: (...) -> str
        """Gets the Base64 pending certificate signing request (PKCS-10).

        :param str name: The name of the certificate
        :param custom_headers: headers that will be added to the request
        :type custom_headers: dict[str, str]
        :return: Base64 encoded pending certificate signing request (PKCS-10).
        :rtype: str
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        vault_base_url = self.vault_endpoint
        # Construct URL
        url = "/certificates/{certificate-name}/pending"
        path_format_arguments = {
            "vaultBaseUrl": self._client._serialize.url("vault_base_url", vault_base_url, "str", skip_quote=True),
            "certificate-name": self._client._serialize.url("certificate_name", name, "str"),
        }
        url = self._client._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters["api-version"] = self._client._serialize.query(
            name="self.api_version", data=self._client.api_version, data_type="str"
        )

        # Construct headers
        header_parameters = {}
        header_parameters["Accept"] = "application/pkcs10"
        if self._client._config.generate_client_request_id:
            header_parameters["x-ms-client-request-id"] = str(uuid.uuid1())

        # Construct and send request
        request = self._client._client.get(url=url, params=query_parameters, headers=header_parameters)
        pipeline_response = self._client._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            self._client.map_error(status_code=response.status_code, response=response, error_map=_error_map)
            raise self._client.models.KeyVaultErrorException(response, self._client._deserialize)

        deserialized = None

        if response.status_code == 200:
            deserialized = response.body() if hasattr(response, "body") else response.content

        return deserialized

    @distributed_trace
    def get_issuer(self, name, **kwargs):
        # type: (str, **Any) -> Issuer
        """Gets the specified certificate issuer.

        Returns the specified certificate issuer resources in the key vault.
        This operation requires the certificates/manageissuers/getissuers permission.

        :param str name: The name of the issuer.
        :return: The specified certificate issuer.
        :rtype: ~azure.keyvault.certificates.models.Issuer
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the issuer doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START get_issuer]
                :end-before: [END get_issuer]
                :language: python
                :caption: Get an issuer
                :dedent: 8
        """
        issuer_bundle = self._client.get_certificate_issuer(
            vault_base_url=self.vault_endpoint, issuer_name=name, error_map=_error_map, **kwargs
        )
        return Issuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace
    def create_issuer(
        self,
        name,  # type: str,
        provider,  # type: str,
        account_id=None,  # type: Optional[str]
        password=None,  # type: Optional[str]
        organization_id=None,  # type: Optional[str]
        admin_details=None,  # type: Optional[List[AdministratorDetails]]
        **kwargs  # type: **Any
    ):
        # type: (...) -> Issuer
        """Sets the specified certificate issuer.

        The SetCertificateIssuer operation adds or updates the specified
        certificate issuer. This operation requires the certificates/setissuers
        permission.

        :param str name: The name of the issuer.
        :param str provider: The issuer provider.
        :param str account_id: The user name/account name/account id.
        :param str password: The password/secret/account key.
        :param str organization_id: Id of the organization.
        :param admin_details: Details of the organization administrators of the certificate issuer.
        :type admin_details: list[~azure.keyvault.certificates.models.AdministratorDetails]
        :returns: The created Issuer
        :rtype: ~azure.keyvault.certificates.models.Issuer
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Determines whether the object is enabled.

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START create_issuer]
                :end-before: [END create_issuer]
                :language: python
                :caption: Create an issuer
                :dedent: 8
        """

        enabled = kwargs.pop("enabled", None)

        if account_id or password:
            issuer_credentials = self._client.models.IssuerCredentials(account_id=account_id, password=password)
        else:
            issuer_credentials = None
        if admin_details and admin_details[0]:
            admin_details_to_pass = [
                self._client.models.AdministratorDetails(
                    first_name=admin_detail.first_name,
                    last_name=admin_detail.last_name,
                    email_address=admin_detail.email,
                    phone=admin_detail.phone,
                )
                for admin_detail in admin_details
            ]
        else:
            admin_details_to_pass = admin_details
        if organization_id or admin_details:
            organization_details = self._client.models.OrganizationDetails(
                id=organization_id, admin_details=admin_details_to_pass
            )
        else:
            organization_details = None
        if enabled is not None:
            issuer_attributes = self._client.models.IssuerAttributes(enabled=enabled)
        else:
            issuer_attributes = None
        issuer_bundle = self._client.set_certificate_issuer(
            vault_base_url=self.vault_endpoint,
            issuer_name=name,
            provider=provider,
            credentials=issuer_credentials,
            organization_details=organization_details,
            attributes=issuer_attributes,
            **kwargs
        )
        return Issuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace
    def update_issuer(
        self,
        name,  # type: str,
        provider=None,  # type: Optional[str],
        account_id=None,  # type: Optional[str]
        password=None,  # type: Optional[str]
        organization_id=None,  # type: Optional[str]
        admin_details=None,  # type: Optional[List[AdministratorDetails]]
        **kwargs  # type: **Any
    ):
        # type: (...) -> Issuer
        """Updates the specified certificate issuer.

        Performs an update on the specified certificate issuer entity.
        This operation requires the certificates/setissuers permission.

        :param str name: The name of the issuer.
        :param str provider: The issuer provider.
        :param str account_id: The username / account name / account key.
        :param str password: The password / secret / account key.
        :param str organization_id: Id of the organization
        :param admin_details: Details of the organization administrators of the certificate issuer.
        :type admin_details: list[~azure.keyvault.certificates.models.AdministratorDetails]
        :param bool enabled: Determines whether the issuer is enabled.
        :return: The updated issuer
        :rtype: ~azure.keyvault.certificates.models.Issuer
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Keyword arguments
            - *enabled (bool)* - Determines whether the object is enabled.
        """

        enabled = kwargs.pop("enabled", None)

        if account_id or password:
            issuer_credentials = self._client.models.IssuerCredentials(account_id=account_id, password=password)
        else:
            issuer_credentials = None
        if admin_details and admin_details[0]:
            admin_details_to_pass = [
                self._client.models.AdministratorDetails(
                    first_name=admin_detail.first_name,
                    last_name=admin_detail.last_name,
                    email_address=admin_detail.email,
                    phone=admin_detail.phone,
                )
                for admin_detail in admin_details
            ]
        else:
            admin_details_to_pass = admin_details
        if organization_id or admin_details:
            organization_details = self._client.models.OrganizationDetails(
                id=organization_id, admin_details=admin_details_to_pass
            )
        else:
            organization_details = None
        if enabled is not None:
            issuer_attributes = self._client.models.IssuerAttributes(enabled=enabled)
        else:
            issuer_attributes = None
        issuer_bundle = self._client.update_certificate_issuer(
            vault_base_url=self.vault_endpoint,
            issuer_name=name,
            provider=provider,
            credentials=issuer_credentials,
            organization_details=organization_details,
            attributes=issuer_attributes,
            **kwargs
        )
        return Issuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace
    def delete_issuer(self, name, **kwargs):
        # type: (str, **Any) -> Issuer
        """Deletes the specified certificate issuer.

        Permanently removes the specified certificate issuer from the vault.
        This operation requires the certificates/manageissuers/deleteissuers permission.

        :param str name: The name of the issuer.
        :return: Issuer
        :rtype: ~azure.keyvault.certificates.models.Issuer
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START delete_issuer]
                :end-before: [END delete_issuer]
                :language: python
                :caption: Delete an issuer
                :dedent: 8
        """
        issuer_bundle = self._client.delete_certificate_issuer(
            vault_base_url=self.vault_endpoint, issuer_name=name, **kwargs
        )
        return Issuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace
    def list_issuers(self, **kwargs):
        # type: (**Any) -> Iterable[IssuerProperties]
        """List certificate issuers for the key vault.

        Returns the set of certificate issuer resources in the key
        vault. This operation requires the certificates/manageissuers/getissuers
        permission.

        :return: An iterator like instance of Issuers
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.certificates.models.Issuer]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates.py
                :start-after: [START list_issuers]
                :end-before: [END list_issuers]
                :language: python
                :caption: List issuers of a vault
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)
        return self._client.get_certificate_issuers(
            vault_base_url=self.vault_endpoint,
            maxresults=max_page_size,
            cls=lambda objs: [IssuerProperties._from_issuer_item(issuer_item=x) for x in objs],
            **kwargs
        )
