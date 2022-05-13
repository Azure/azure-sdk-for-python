# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from azure.keyvault.certificates import CertificateClient, CertificatePolicy, KeyVaultCertificateIdentifier
from devtools_testutils import PowerShellPreparer, recorded_by_proxy

from _shared.test_case import KeyVaultTestCase


class TestParseId(KeyVaultTestCase):
    def create_client(self, vault_uri, **kwargs):
        credential = self.get_credential(CertificateClient)
        return self.create_client_from_credential(
            CertificateClient, credential=credential, vault_url=vault_uri, **kwargs
        )

    @PowerShellPreparer("keyvault", azure_keyvault_url="https://vaultname.vault.azure.net")
    @recorded_by_proxy
    def test_parse_certificate_id_with_version(self, azure_keyvault_url):
        client = self.create_client(azure_keyvault_url)

        cert_name = self.get_resource_name("cert")
        # create certificate
        certificate = client.begin_create_certificate(cert_name, CertificatePolicy.get_default()).result()

        # [START parse_key_vault_certificate_id]
        cert = client.get_certificate(cert_name)
        parsed_certificate_id = KeyVaultCertificateIdentifier(cert.id)

        print(parsed_certificate_id.name)
        print(parsed_certificate_id.vault_url)
        print(parsed_certificate_id.version)
        print(parsed_certificate_id.source_id)
        # [END parse_key_vault_certificate_id]
        assert parsed_certificate_id.name == cert_name
        assert parsed_certificate_id.vault_url == client.vault_url
        assert parsed_certificate_id.version == cert.properties.version
        assert parsed_certificate_id.source_id == cert.id


def test_parse_certificate_id_with_pending_version():
    source_id = "https://keyvault-name.vault.azure.net/certificates/certificate-name/pending"
    parsed_certificate_id = KeyVaultCertificateIdentifier(source_id)

    assert parsed_certificate_id.name == "certificate-name"
    assert parsed_certificate_id.vault_url == "https://keyvault-name.vault.azure.net"
    assert parsed_certificate_id.version == "pending"
    assert (
        parsed_certificate_id.source_id == "https://keyvault-name.vault.azure.net/certificates/certificate-name/pending"
    )


def test_parse_deleted_certificate_id():
    source_id = "https://keyvault-name.vault.azure.net/deletedcertificates/deleted-certificate"
    parsed_certificate_id = KeyVaultCertificateIdentifier(source_id)

    assert parsed_certificate_id.name == "deleted-certificate"
    assert parsed_certificate_id.vault_url == "https://keyvault-name.vault.azure.net"
    assert parsed_certificate_id.version is None
    assert (
        parsed_certificate_id.source_id
        == "https://keyvault-name.vault.azure.net/deletedcertificates/deleted-certificate"
    )
