# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, Mapping, Optional
from datetime import datetime
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

from ._internal import _KeyVaultClientBase
from ._models import (
    Certificate,
    CertificateBase,
    DeletedCertificate,
    CertificatePolicy,
    Issuer,
    IssuerBase,
    Contact,
    CertificateOperation,
)


class CertificateClient(_KeyVaultClientBase):
    """CertificateClient defines a high level interface for
    managing certificates in the specified vault.
    Example:
        .. literalinclude:: ../tests/test_examples_certificates.py
            :start-after: [START create_certificate_client]
            :end-before: [END create_certificate_client]
            :language: python
            :dedent: 4
            :caption: Creates a new instance of the Certificate client
    """
    # pylint:disable=protected-access

    def create_certificate(self, name, policy=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs):
        # type: (str, Optional[CertificatePolicy], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Mapping[str, Any]]) -> CertificateOperation
        """Creates a new certificate.

        If this is the first version, the certificate resource is created. This
        operation requires the certificates/create permission.

        :param name: The name of the certificate.
        :type name: str
        :param policy: The management policy for the certificate.
        :type policy:
         ~azure.security.keyvault.v7_0.models.CertificatePolicy
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
        """

        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.CertificateAttributes(
                enabled=enabled, not_before=not_before, expires=expires
            )
        else:
            attributes = None

        bundle = self._client.create_certificate(
            self.vault_url,
            certificate_name=name,
            certificate_policy=policy,
            certificate_attributes=attributes,
            tags=tags,
            **kwargs
        )

        return CertificateOperation._from_certificate_operation_bundle(bundle)

    def get_certificate(self, name, version=None, **kwargs):
        # type: (str, Optional[str]) -> Certificate
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
        """
        if version is None:
            version = ""

        bundle = self._client.get_certificate(self.vault_url, name, certificate_version=version, **kwargs)
        return Certificate._from_certificate_bundle(bundle)

    def delete_certificate(self, name, **kwargs):
        # type: (str) -> DeletedCertificate
        """Deletes a certificate from a specified key vault.

        Deletes all versions of a certificate object along with its associated
        policy. Delete certificate cannot be used to remove individual versions
        of a certificate object. This operation requires the
        certificates/delete permission.

        :param name: The name of the certificate.
        :type name: str
        :returns: The deleted certificate
        :rtype: ~azure.security.keyvault.certificates._models.DeletedCertificate
        """
        bundle = self._client.delete_certificate(self.vault_url, certificate_name=name, **kwargs)
        return DeletedCertificate._from_deleted_certificate_bundle(bundle)

    def get_deleted_certificate(self, name, **kwargs):
        # type: (str) -> DeletedCertificate
        bundle = self._client.get_deleted_certificate(
            self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs
        )
        return DeletedCertificate._from_deleted_certificate_bundle(bundle)

    def purge_deleted_certificate(self, name, **kwargs):
        # type: (str) -> None
        self._client.purge_deleted_certificate(self.vault_url, name, **kwargs)

    def recover_deleted_certificate(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> Certificate
        bundle = self._client.recover_deleted_certificate(self.vault_url, name, **kwargs)
        return Certificate._from_certificate_bundle(bundle)

    def import_certificate(
        self,
        name,
        base64_encoded_certificate,
        password=None,
        policy=None,
        enabled=None,
        not_before=None,
        expires=None,
        tags=None,
        **kwargs
    ):
        # type: (str, str, Optional[str], Optional[CertificatePolicy], Optional[bool],Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Certificate
        """Imports a certificate into a specified key vault.

        Imports an existing valid certificate, containing a private key, into
        Azure Key Vault. The certificate to be imported can be in either PFX or
        PEM format. If the certificate is in PEM format the PEM file must
        contain the key as well as x509 certificates. This operation requires
        the certificates/import permission.

        :param name: The name of the certificate.
        :type name: str
        :param base64_encoded_certificate: Base64 encoded representation of
         the certificate object to import. This certificate needs to contain
         the private key.
        :type base64_encoded_certificate: str
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
        bundle = self._client.import_certificate(
            self.vault_url,
            name,
            base64_encoded_certificate=base64_encoded_certificate,
            password=password,
            polciy=policy,
            certificate_attributes=attributes,
            tags=tags,
            **kwargs
        )
        return Certificate._from_certificate_bundle(bundle)

    def get_policy(self, name, **kwargs):
        # type: (str) -> CertificatePolicy
        pass

    def update_policy(self, name, policy, enabled=None, not_before=None, expires=None, tags=None, **kwargs):
        # type: (str, CertificatePolicy) -> CertificatePolicy
        pass

    def update_certificate(self, name, version=None, not_before=None, expires=None, enabled=None, tags=None, **kwargs):
        # type: (str, str, Optional[bool], Optional[Dict[str, str]]) -> Certificate
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
        :rtype: ~azure.security.keyvault.v7_0.models.Certificate
        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.CertificateAttributes(
                enabled=enabled, not_before=not_before, expires=expires
            )
        else:
            attributes = None

        bundle = self._client.update_certificate(
            self.vault_url, name, certificate_version=version or "", certificate_attributes=attributes, tags=tags, **kwargs
        )
        return Certificate._from_certificate_bundle(bundle)

    def merge_certificate(
        self, name, x509_certificates, enabled=True, not_before=None, expires=None, tags=None, **kwargs
    ):
        # type: (str, list[str], Optional[bool], Optional[Dict[str, str]]) -> Certificate
        pass

    def backup_certificate(self, name, **kwargs):
        # type: (str) -> bytes
        backup_result = self._client.backup_certificate(
            self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs
        )
        return backup_result.value


    def restore_certificate(self, backup, **kwargs):
        # type: (bytes) -> Certificate
        bundle = self._client.restore_certificate(
            self.vault_url, backup, error_map={409: ResourceExistsError}, **kwargs
        )
        return Certificate._from_certificate_bundle(bundle)

    def list_deleted_certificates(self, include_pending=None, **kwargs):
        # type: (Optional[bool]) -> Generator[DeletedCertificate]
        max_page_size = kwargs.get("max_page_size", None)
        pages = self._client.get_deleted_certificates(
            self._vault_url, maxresults=max_page_size, include_pending=include_pending, **kwargs
        )
        return (DeletedCertificate._from_deleted_certificate_item(item) for item in pages)

    def list_certificates(self, include_pending=None, **kwargs):
        # type: (Optional[bool]) -> Generator[CertificateBase]
        """List certificates in a specified key vault.

        The GetCertificates operation returns the set of certificates resources
        in the specified key vault. This operation requires the
        certificates/list permission.

        :param include_pending: Specifies whether to include certificates
         which are not completely provisioned.
        :type include_pending: bool
        :returns: An iterator like instance of CertificateBase
        :rtype:
         typing.Generator[~azure.security.keyvault.certificates._models.CertificateBase]
        """
        max_page_size = kwargs.get("max_page_size", None)
        pages = self._client.get_certificates(
            self._vault_url, maxresults=max_page_size, include_pending=include_pending, **kwargs
        )
        return (CertificateBase._from_certificate_item(item) for item in pages)

    def list_versions(self, name, **kwargs):
        # type: (str) -> Generator[CertificateBase]
        """List the versions of a certificate.

        The GetCertificateVersions operation returns the versions of a
        certificate in the specified key vault. This operation requires the
        certificates/list permission.

        :param name: The name of the certificate.
        :type name: str
        :returns: An iterator like instance of CertificateBase
        :rtype:
         typing.Generator[~azure.security.keyvault.certificates._models.CertificateBase]
        """
        max_page_size = kwargs.get("max_page_size", None)
        pages = self._client.get_certificate_versions(self._vault_url, name, maxresults=max_page_size, **kwargs)
        return (CertificateBase._from_certificate_item(item) for item in pages)

    def create_contacts(self, contacts, **kwargs):
        # type: (Iterable[Contact]) -> Iterable[Contact]
        """Sets the certificate contacts for the specified key vault.

        Sets the certificate contacts for the specified key vault. This
        operation requires the certificates/managecontacts permission.

        :param contacts: The contact list for the vault certificates.
        :type contacts: list[~azure.keyvault.v7_0.models.Contact]
        :returns: The created list of contacts
        :rtype: ~azure.security.keyvault.certificates._models.Contacts
        """
        bundle = self._client.set_certificate_contacts(self.vault_url, contact_list=contacts, **kwargs)
        return Contact._from_certificate_contacts_item(bundle)

    def list_contacts(self, **kwargs):
        # type: () -> Iterable[Contact]
        pass

    def delete_contacts(self, **kwargs):
        # type: () -> Iterable[Contact]
        pass

    def get_certificate_operation(self, name, **kwargs):
        # type: (str) -> CertificateOperation
        """Gets the creation operation of a certificate.

        Gets the creation operation associated with a specified certificate.
        This operation requires the certificates/get permission.

        :param name: The name of the certificate.
        :type name: str
        :returns: The created CertificateOperation
        :rtype: ~azure.security.keyvault.v7_0.models.CertificateOperation
        """

        bundle = self._client.get_certificate_operation(self.vault_url, name, **kwargs)
        return CertificateOperation._from_certificate_operation_bundle(bundle)

    def delete_certificate_operation(self, name, **kwargs):
        # type: (str) -> CertificateOperation
        """Deletes the creation operation for a specific certificate.

        Deletes the creation operation for a specified certificate that is in
        the process of being created. The certificate is no longer created.
        This operation requires the certificates/update permission.

        :param name: The name of the certificate.
        :type name: str
        :return: The deleted CertificateOperation
        :rtype: ~azure.security.keyvault.certificates._models.CertificateOperation
        """
        bundle = self._client.delete_certificate_operation(self.vault_url, name, **kwargs)
        return CertificateOperation._from_certificate_operation_bundle(bundle)

    def cancel_certificate_operation(self, name, cancellation_requested, **kwargs):
        # type: (str) -> CertificateOperation
        """Updates a certificate operation.

        Updates a certificate creation operation that is already in progress.
        This operation requires the certificates/update permission.

        :param name: The name of the certificate.
        :type name: str
        :param cancellation_requested: Indicates if cancellation was requested
         on the certificate operation.
        :type cancellation_requested: bool
        :returns: The updated certificate operation
        :rtype: ~azure.security.keyvault.certificates._models.CertificateOperation
        """
        bundle = self._client.update_certificate_operation(self.vault_url, name, cancellation_requested, **kwargs)
        return CertificateOperation._from_certificate_operation_bundle(bundle)

    def get_pending_certificate_signing_request(self, name, **kwargs):
        # type: (str) -> str
        pass

    def get_issuer(self, name, **kwargs):
        # type: (str) -> Issuer
        pass

    def create_issuer(
        self,
        name,
        provider,
        account_id=None,
        password=None,
        organization_id=None,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        enabled=None,
        not_before=None,
        expires=None,
        tags=None,
        **kwargs
    ):
        # type: (str, str, Optional[str], Optional[str], Optional[organization_id], Optional[str], Optional[str], Optional[str], Optional[str], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Issuer
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
        :param first_name: First name.
        :type first_name: str
        :param last_name: Last name.
        :type last_name: str
        :param email: Email address.
        :type email: str
        :param phone: Phone number.
        :type phone: str
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param not_before: Not before date of the secret in UTC
        :type not_before: datetime.datetime
        :param expires: Expiry date of the secret  in UTC.
        :type expires: datetime.datetime
        :param tags: Application specific metadata in the form of key-value pairs.
        :type tags: dict(str, str)
        :returns: The created Issuer
        :rtype: ~azure.security.keyvault.certificates._models.Issuer
        """

    def update_issuer(
        self,
        name,
        provider=None,
        account_id=None,
        password=None,
        organization_id=None,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        enabled=True,
        not_before=None,
        expires=None,
        tags=None,
        **kwargs
    ):
        # type: (str, Optional[str], Optional[str], Optional[str], Optional[organization_id], Optional[str], Optional[str], Optional[str], Optional[str], Optional[bool], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Issuer
        pass

    def delete_issuer(self, name, **kwargs):
        # type: (str) -> Issuer
        pass

    def list_issuers(self, **kwargs):
        # type: () -> Iterable[IssuerBase]
        pass
