# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import hashlib
import os

from devtools_testutils import ResourceGroupPreparer, KeyVaultPreparer
from certificates_async_preparer import AsyncVaultClientPreparer
from certificates_async_test_case import AsyncKeyVaultTestCase
from azure.keyvault.certificates import CertificatePolicy, CertificateContentType, WellKnownIssuerNames


def print(*args):
    assert all(arg is not None for arg in args)


def test_create_certificate():
    vault_url = "vault_url"
    # pylint:disable=unused-variable
    # [START create_certificate_client]

    from azure.identity.aio import DefaultAzureCredential
    from azure.keyvault.certificates.aio import CertificateClient

    # Create a KeyVaultCertificate using default Azure credentials
    credential = DefaultAzureCredential()
    certificate_client = CertificateClient(vault_url=vault_url, credential=credential)

    # [END create_certificate_client]


class TestExamplesKeyVault(AsyncKeyVaultTestCase):
    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_example_certificate_crud_operations(self, vault_client, **kwargs):
        certificate_client = vault_client.certificates

        # [START create_certificate]
        from azure.keyvault.certificates import CertificatePolicy, CertificateContentType, WellKnownIssuerNames

        # specify the certificate policy
        cert_policy = CertificatePolicy(
            issuer_name=WellKnownIssuerNames.self,
            subject="CN=*.microsoft.com",
            san_dns_names=["sdk.azure-int.net"],
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type=CertificateContentType.pkcs12,
            validity_in_months=24,
        )
        cert_name = "cert-name"

        certificate = await certificate_client.create_certificate(certificate_name=cert_name, policy=cert_policy)

        print(certificate.id)
        print(certificate.name)
        print(certificate.policy.issuer_name)

        # [END create_certificate]

        # [START get_certificate]

        # get the latest version of a certificate
        certificate = await certificate_client.get_certificate(cert_name)

        print(certificate.id)
        print(certificate.name)
        print(certificate.policy.issuer_name)

        # [END get_certificate]
        # [START update_certificate]

        # update attributes of an existing certificate
        tags = {"foo": "updated tag"}
        updated_certificate = await certificate_client.update_certificate_properties(
            certificate_name=certificate.name, tags=tags
        )

        print(updated_certificate.properties.version)
        print(updated_certificate.properties.updated_on)
        print(updated_certificate.properties.tags)

        # [END update_certificate]
        # [START delete_certificate]

        # delete a certificate
        deleted_certificate = await certificate_client.delete_certificate(cert_name)

        print(deleted_certificate.name)

        # if the vault has soft-delete enabled, the certificate's
        # scheduled purge date, deleted_on, and recovery id are available
        print(deleted_certificate.deleted_on)
        print(deleted_certificate.scheduled_purge_date)
        print(deleted_certificate.recovery_id)

        # [END delete_certificate]

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_example_certificate_list_operations(self, vault_client, **kwargs):
        certificate_client = vault_client.certificates

        # specify the certificate policy
        cert_policy = CertificatePolicy(
            issuer_name=WellKnownIssuerNames.self,
            subject="CN=*.microsoft.com",
            san_dns_names=["sdk.azure-int.net"],
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type=CertificateContentType.pkcs12,
            validity_in_months=24,
        )

        create_certificate_pollers = []
        for i in range(4):
            create_certificate_pollers.append(
                certificate_client.create_certificate(certificate_name="certificate{}".format(i), policy=cert_policy)
            )

        for poller in create_certificate_pollers:
            await poller

        # [START list_properties_of_certificates]

        # list certificates
        certificates = certificate_client.list_properties_of_certificates()

        async for certificate in certificates:
            print(certificate.id)
            print(certificate.created_on)
            print(certificate.name)
            print(certificate.updated_on)
            print(certificate.enabled)

        # [END list_properties_of_certificates]
        # [START list_properties_of_certificate_versions]

        # get an iterator of all versions of a certificate
        certificate_versions = certificate_client.list_properties_of_certificate_versions("cert-name")

        async for certificate in certificate_versions:
            print(certificate.id)
            print(certificate.properties.updated_on)
            print(certificate.properties.version)

        # [END list_properties_of_certificate_versions]
        # [START list_deleted_certificates]

        # get an iterator of deleted certificates (requires soft-delete enabled for the vault)
        deleted_certificates = certificate_client.list_deleted_certificates()

        async for certificate in deleted_certificates:
            print(certificate.id)
            print(certificate.name)
            print(certificate.scheduled_purge_date)
            print(certificate.recovery_id)
            print(certificate.deleted_on)

        # [END list_deleted_certificates]

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer(enable_soft_delete=False)
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_example_certificate_backup_restore(self, vault_client, **kwargs):
        certificate_client = vault_client.certificates

        # specify the certificate policy
        cert_policy = CertificatePolicy(
            issuer_name=WellKnownIssuerNames.self,
            subject="CN=*.microsoft.com",
            san_dns_names=["sdk.azure-int.net"],
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type=CertificateContentType.pkcs12,
            validity_in_months=24,
        )

        cert_name = "cert-name"
        create_certificate_poller = certificate_client.create_certificate(
            certificate_name=cert_name, policy=cert_policy
        )

        await create_certificate_poller

        # [START backup_certificate]

        # backup certificate
        certificate_backup = await certificate_client.backup_certificate(cert_name)

        # returns the raw bytes of the backed up certificate
        print(certificate_backup)

        # [END backup_certificate]

        await certificate_client.delete_certificate(certificate_name=cert_name)

        # [START restore_certificate]

        # restores a certificate backup
        restored_certificate = await certificate_client.restore_certificate_backup(certificate_backup)
        print(restored_certificate.id)
        print(restored_certificate.name)
        print(restored_certificate.properties.version)

        # [END restore_certificate]

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_example_certificate_recover(self, vault_client, **kwargs):
        certificate_client = vault_client.certificates

        # specify the certificate policy
        cert_policy = CertificatePolicy(
            issuer_name=WellKnownIssuerNames.self,
            subject="CN=*.microsoft.com",
            san_dns_names=["sdk.azure-int.net"],
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type=CertificateContentType.pkcs12,
            validity_in_months=24,
        )

        cert_name = "cert-name"
        create_certificate_poller = certificate_client.create_certificate(
            certificate_name=cert_name, policy=cert_policy
        )
        await create_certificate_poller

        await certificate_client.delete_certificate(certificate_name=cert_name)

        # [START get_deleted_certificate]

        # get a deleted certificate (requires soft-delete enabled for the vault)
        deleted_certificate = await certificate_client.get_deleted_certificate("cert-name")
        print(deleted_certificate.name)

        # [END get_deleted_certificate]
        # [START recover_deleted_certificate]

        # recover deleted certificate to its latest version (requires soft-delete enabled for the vault)
        recovered_certificate = await certificate_client.recover_deleted_certificate("cert-name")
        print(recovered_certificate.id)
        print(recovered_certificate.name)

        # [END recover_deleted_certificate]

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_example_contacts(self, vault_client, **kwargs):
        certificate_client = vault_client.certificates

        # [START set_contacts]
        from azure.keyvault.certificates import CertificateContact

        # Create a list of the contacts that you want to set for this key vault.
        contact_list = [
            CertificateContact(email="admin@contoso.com", name="John Doe", phone="1111111111"),
            CertificateContact(email="admin2@contoso.com", name="John Doe2", phone="2222222222"),
        ]

        contacts = await certificate_client.set_contacts(contact_list)
        for contact in contacts:
            print(contact.name)
            print(contact.email)
            print(contact.phone)

        # [END set_contacts]

        # [START get_contacts]

        contacts = await certificate_client.get_contacts()

        # Loop through the certificate contacts for this key vault.
        for contact in contacts:
            print(contact.name)
            print(contact.email)
            print(contact.phone)

        # [END get_contacts]

        # [START delete_contacts]

        deleted_contacts = await certificate_client.delete_contacts()

        for deleted_contact in deleted_contacts:
            print(deleted_contact.name)
            print(deleted_contact.email)
            print(deleted_contact.phone)

        # [END delete_contacts]

    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @AsyncVaultClientPreparer()
    @AsyncKeyVaultTestCase.await_prepared_test
    async def test_example_issuers(self, vault_client, **kwargs):
        certificate_client = vault_client.certificates

        # [START create_issuer]
        from azure.keyvault.certificates import AdministratorContact

        # First we specify the AdministratorContact for a issuer.
        admin_contacts = [
            AdministratorContact(first_name="John", last_name="Doe", email="admin@microsoft.com", phone="4255555555")
        ]

        issuer = await certificate_client.create_issuer(
            issuer_name="issuer1",
            provider="Test",
            account_id="keyvaultuser",
            admin_contacts=admin_contacts,
            enabled=True,
        )

        print(issuer.name)
        print(issuer.provider)
        print(issuer.account_id)

        for contact in issuer.admin_contacts:
            print(contact.first_name)
            print(contact.last_name)
            print(contact.email)
            print(contact.phone)

        # [END create_issuer]

        # [START get_issuer]

        issuer = await certificate_client.get_issuer("issuer1")

        print(issuer.name)
        print(issuer.provider)
        print(issuer.account_id)

        for contact in issuer.admin_contacts:
            print(contact.first_name)
            print(contact.last_name)
            print(contact.email)
            print(contact.phone)

        # [END get_issuer]

        await certificate_client.create_issuer(
            issuer_name="issuer2", provider="Test", account_id="keyvaultuser", enabled=True
        )

        # [START list_properties_of_issuers]

        issuers = certificate_client.list_properties_of_issuers()

        async for issuer in issuers:
            print(issuer.name)
            print(issuer.provider)

        # [END list_properties_of_issuers]

        # [START delete_issuer]

        deleted_issuer = await certificate_client.delete_issuer("issuer1")

        print(deleted_issuer.name)
        print(deleted_issuer.provider)
        print(deleted_issuer.account_id)

        for contact in deleted_issuer.admin_contacts:
            print(contact.first_name)
            print(contact.last_name)
            print(contact.email)
            print(contact.phone)

        # [END delete_issuer]
