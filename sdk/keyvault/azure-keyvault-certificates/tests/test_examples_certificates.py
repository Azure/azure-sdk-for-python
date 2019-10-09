# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import print_function
import functools

from devtools_testutils import ResourceGroupPreparer
from certificates_preparer import VaultClientPreparer
from certificates_test_case import KeyVaultTestCase


def print(*args):
    assert all(arg is not None for arg in args)


def test_create_certificate_client():
    vault_endpoint = "vault_endpoint"
    # pylint:disable=unused-variable
    # [START create_certificate_client]

    from azure.identity import DefaultAzureCredential
    from azure.keyvault.certificates import CertificateClient

    # Create a CertificateClient using default Azure credentials
    credential = DefaultAzureCredential()
    certificate_client = CertificateClient(vault_endpoint, credential)

    # [END create_certificate_client]


class TestExamplesKeyVault(KeyVaultTestCase):
    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_certificate_crud_operations(self, vault_client, **kwargs):

        certificate_client = vault_client.certificates
        # [START create_certificate]
        from azure.keyvault.certificates import CertificatePolicy, SecretContentType

        # specify the certificate policy
        cert_policy = CertificatePolicy(
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type=SecretContentType.PKCS12,
            issuer_name="Self",
            subject_name="CN=*.microsoft.com",
            validity_in_months=24,
            san_dns_names=["sdk.azure-int.net"],
        )

        cert_name = "cert-name"
        # create a certificate with optional arguments, returns a long running operation poller
        certificate_operation_poller = certificate_client.create_certificate(name=cert_name, policy=cert_policy)

        # Here we are waiting for the certificate creation operation to be completed
        certificate = certificate_operation_poller.result()

        # You can get the final status of the certificate operation poller using .result()
        print(certificate_operation_poller.result())

        print(certificate.id)
        print(certificate.name)
        print(certificate.policy.issuer_name)

        # [END create_certificate]

        # [START get_certificate]

        # get the certificate
        certificate = certificate_client.get_certificate_with_policy(name=cert_name)

        print(certificate.id)
        print(certificate.name)
        print(certificate.policy.issuer_name)

        # [END get_certificate]
        # [START update_certificate]

        # update attributes of an existing certificate
        tags = {"foo": "updated tag"}
        updated_certificate = certificate_client.update_certificate_properties(name=certificate.name, tags=tags)

        print(updated_certificate.properties.version)
        print(updated_certificate.properties.updated)
        print(updated_certificate.properties.tags)

        # [END update_certificate]
        # [START delete_certificate]

        # delete a certificate
        deleted_certificate = certificate_client.delete_certificate(name=certificate.name)

        print(deleted_certificate.name)

        # if the vault has soft-delete enabled, the certificate's deleted date,
        # scheduled purge date, and recovery id are available
        print(deleted_certificate.deleted_date)
        print(deleted_certificate.scheduled_purge_date)
        print(deleted_certificate.recovery_id)

        # [END delete_certificate]

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_certificate_list_operations(self, vault_client, **kwargs):
        from azure.keyvault.certificates import CertificatePolicy, SecretContentType

        certificate_client = vault_client.certificates

        # specify the certificate policy
        cert_policy = CertificatePolicy(
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type=SecretContentType.PKCS12,
            issuer_name="Self",
            subject_name="CN=*.microsoft.com",
            validity_in_months=24,
            san_dns_names=["sdk.azure-int.net"],
        )

        for i in range(4):
            certificate_client.create_certificate(name="certificate{}".format(i), policy=cert_policy).wait()

        # [START list_certificates]

        # get an iterator of certificates
        certificates = certificate_client.list_certificates()

        for certificate in certificates:
            print(certificate.id)
            print(certificate.created)
            print(certificate.name)
            print(certificate.updated)
            print(certificate.enabled)

        # [END list_certificates]
        # [START list_certificate_versions]

        # get an iterator of a certificate's versions
        certificate_versions = certificate_client.list_certificate_versions(name="certificate-name")

        for certificate in certificate_versions:
            print(certificate.id)
            print(certificate.updated)
            print(certificate.version)

        # [END list_certificate_versions]
        # [START list_deleted_certificates]

        # get an iterator of deleted certificates (requires soft-delete enabled for the vault)
        deleted_certificates = certificate_client.list_deleted_certificates()

        for certificate in deleted_certificates:
            print(certificate.id)
            print(certificate.name)
            print(certificate.deleted_date)
            print(certificate.scheduled_purge_date)
            print(certificate.deleted_date)

        # [END list_deleted_certificates]

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_example_certificate_backup_restore(self, vault_client, **kwargs):
        from azure.keyvault.certificates import CertificatePolicy, SecretContentType

        certificate_client = vault_client.certificates

        # specify the certificate policy
        cert_policy = CertificatePolicy(
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type=SecretContentType.PKCS12,
            issuer_name="Self",
            subject_name="CN=*.microsoft.com",
            validity_in_months=24,
            san_dns_names=["sdk.azure-int.net"],
        )

        cert_name = "cert-name"
        certificate_client.create_certificate(name=cert_name, policy=cert_policy).wait()

        # [START backup_certificate]

        # backup certificate
        certificate_backup = certificate_client.backup_certificate(name=cert_name)

        # returns the raw bytes of the backed up certificate
        print(certificate_backup)

        # [END backup_certificate]

        certificate_client.delete_certificate(name=cert_name)

        # [START restore_certificate]

        # restore a certificate backup
        restored_certificate = certificate_client.restore_certificate(backup=certificate_backup)

        print(restored_certificate.id)
        print(restored_certificate.name)
        print(restored_certificate.properties.version)

        # [END restore_certificate]

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_certificate_recover(self, vault_client, **kwargs):
        from azure.keyvault.certificates import CertificatePolicy, SecretContentType
        from azure.core.exceptions import HttpResponseError

        certificate_client = vault_client.certificates

        # specify the certificate policy
        cert_policy = CertificatePolicy(
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type=SecretContentType.PKCS12,
            issuer_name="Self",
            subject_name="CN=*.microsoft.com",
            validity_in_months=24,
            san_dns_names=["sdk.azure-int.net"],
        )

        cert_name = "cert-name"
        certificate_client.create_certificate(name=cert_name, policy=cert_policy).wait()
        certificate_client.delete_certificate(name=cert_name)
        self._poll_until_no_exception(
            functools.partial(certificate_client.get_deleted_certificate, cert_name), HttpResponseError
        )
        # [START get_deleted_certificate]

        # get a deleted certificate (requires soft-delete enabled for the vault)
        deleted_certificate = certificate_client.get_deleted_certificate(name=cert_name)
        print(deleted_certificate.name)

        # if the vault has soft-delete enabled, the certificate's deleted date,
        # scheduled purge date, and recovery id are available
        print(deleted_certificate.deleted_date)
        print(deleted_certificate.scheduled_purge_date)
        print(deleted_certificate.recovery_id)

        # [END get_deleted_certificate]
        # [START recover_deleted_certificate]

        # recover a deleted certificate to its latest version (requires soft-delete enabled for the vault)
        recovered_certificate = certificate_client.recover_deleted_certificate(name=cert_name)

        print(recovered_certificate.id)
        print(recovered_certificate.name)

        # [END recover_deleted_certificate]

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_example_contacts(self, vault_client, **kwargs):
        from azure.keyvault.certificates import CertificatePolicy, Contact

        certificate_client = vault_client.certificates

        # [START create_contacts]

        # Create a list of the contacts that you want to set for this key vault.
        contact_list = [
            Contact(email="admin@contoso.com", name="John Doe", phone="1111111111"),
            Contact(email="admin2@contoso.com", name="John Doe2", phone="2222222222"),
        ]

        contacts = certificate_client.create_contacts(contacts=contact_list)
        for contact in contacts:
            print(contact.name)
            print(contact.email)
            print(contact.phone)

        # [END create_contacts]

        # [START get_contacts]

        contacts = certificate_client.get_contacts()

        # Loop through the certificate contacts for this key vault.
        for contact in contacts:
            print(contact.name)
            print(contact.email)
            print(contact.phone)

        # [END get_contacts]

        # [START delete_contacts]

        deleted_contacts = certificate_client.delete_contacts()

        for deleted_contact in deleted_contacts:
            print(deleted_contact.name)
            print(deleted_contact.email)
            print(deleted_contact.phone)

        # [END delete_contacts]

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_example_issuers(self, vault_client, **kwargs):
        from azure.keyvault.certificates import AdministratorDetails, CertificatePolicy

        certificate_client = vault_client.certificates

        # [START create_issuer]

        # First we specify the AdministratorDetails for a issuer.
        admin_details = [
            AdministratorDetails(first_name="John", last_name="Doe", email="admin@microsoft.com", phone="4255555555")
        ]

        issuer = certificate_client.create_issuer(
            name="issuer1", provider="Test", account_id="keyvaultuser", admin_details=admin_details, enabled=True
        )

        print(issuer.name)
        print(issuer.properties.provider)
        print(issuer.account_id)

        for admin_detail in issuer.admin_details:
            print(admin_detail.first_name)
            print(admin_detail.last_name)
            print(admin_detail.email)
            print(admin_detail.phone)

        # [END create_issuer]

        # [START get_issuer]

        issuer = certificate_client.get_issuer(name="issuer1")

        print(issuer.name)
        print(issuer.properties.provider)
        print(issuer.account_id)

        for admin_detail in issuer.admin_details:
            print(admin_detail.first_name)
            print(admin_detail.last_name)
            print(admin_detail.email)
            print(admin_detail.phone)

        # [END get_issuer]

        certificate_client.create_issuer(name="issuer2", provider="Test", account_id="keyvaultuser", enabled=True)

        # [START list_issuers]

        issuers = certificate_client.list_issuers()

        for issuer in issuers:
            print(issuer.name)
            print(issuer.provider)

        # [END list_issuers]

        # [START delete_issuer]

        deleted_issuer = certificate_client.delete_issuer(name="issuer1")

        print(deleted_issuer.name)
        print(deleted_issuer.properties.provider)
        print(deleted_issuer.account_id)

        for admin_detail in deleted_issuer.admin_details:
            print(admin_detail.first_name)
            print(admin_detail.last_name)
            print(admin_detail.email)
            print(admin_detail.phone)

        # [END delete_issuer]
