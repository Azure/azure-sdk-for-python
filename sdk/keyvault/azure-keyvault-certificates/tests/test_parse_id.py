# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
import pytest
import functools
from azure.keyvault.certificates import CertificateClient, CertificatePolicy, parse_key_vault_certificate_id
from devtools_testutils import ResourceGroupPreparer, KeyVaultPreparer

from _shared.preparer import KeyVaultClientPreparer as _KeyVaultClientPreparer
from _shared.test_case import KeyVaultTestCase

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
KeyVaultClientPreparer = functools.partial(_KeyVaultClientPreparer, CertificateClient)


class TestParseId(KeyVaultTestCase):
    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @KeyVaultClientPreparer()
    def test_parse_certificate_id_with_version(self, client):
        cert_name = self.get_resource_name("cert")
        # create certificate
        certificate = client.begin_create_certificate(cert_name, CertificatePolicy.get_default()).result()

        # [START parse_key_vault_certificate_id]
        cert = client.get_certificate(cert_name)
        parsed_certificate_id = parse_key_vault_certificate_id(cert.id)

        print(parsed_certificate_id.name)
        print(parsed_certificate_id.vault_url)
        print(parsed_certificate_id.version)
        print(parsed_certificate_id.source_id)
        # [END parse_key_vault_certificate_id]
        self.assertEqual(parsed_certificate_id.name, cert_name)
        self.assertEqual(parsed_certificate_id.vault_url, client.vault_url)
        self.assertEqual(parsed_certificate_id.version, cert.properties.version)
        self.assertEqual(parsed_certificate_id.source_id, cert.id)

    def test_parse_certificate_id_with_pending_version(self):
        source_id = "https://keyvault-name.vault.azure.net/certificates/certificate-name/pending"
        parsed_certificate_id = parse_key_vault_certificate_id(source_id)

        self.assertEqual(parsed_certificate_id.name, "certificate-name")
        self.assertEqual(parsed_certificate_id.vault_url, "https://keyvault-name.vault.azure.net")
        self.assertEqual(parsed_certificate_id.version, "pending")
        self.assertEqual(
            parsed_certificate_id.source_id,
            "https://keyvault-name.vault.azure.net/certificates/certificate-name/pending",
        )

    def test_parse_deleted_certificate_id(self):
        source_id = "https://keyvault-name.vault.azure.net/deletedcertificates/deleted-certificate"
        parsed_certificate_id = parse_key_vault_certificate_id(source_id)

        self.assertEqual(parsed_certificate_id.name, "deleted-certificate")
        self.assertEqual(parsed_certificate_id.vault_url, "https://keyvault-name.vault.azure.net")
        self.assertIsNone(parsed_certificate_id.version)
        self.assertEqual(
            parsed_certificate_id.source_id,
            "https://keyvault-name.vault.azure.net/deletedcertificates/deleted-certificate",
        )
