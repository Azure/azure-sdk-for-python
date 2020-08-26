# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
import pytest
from azure.keyvault.certificates import parse_certificate_id
from _shared.test_case import KeyVaultTestCase


class TestParseId(KeyVaultTestCase):
    def test_parse_certificate_id_with_version(self):
        # [START parse_certificate_id]
        original_id = "https://keyvault-name.vault.azure.net/certificates/certificate-name/version"
        parsed_certificate_id = parse_certificate_id(original_id)

        print(parsed_certificate_id.name)
        print(parsed_certificate_id.collection)
        print(parsed_certificate_id.vault_url)
        print(parsed_certificate_id.version)
        print(parsed_certificate_id.original_id)
        # [END parse_certificate_id]
        assert parsed_certificate_id.name == "certificate-name"
        assert parsed_certificate_id.collection == "certificates"
        assert parsed_certificate_id.vault_url == "https://keyvault-name.vault.azure.net"
        assert parsed_certificate_id.version == "version"
        assert parsed_certificate_id.original_id == "https://keyvault-name.vault.azure.net/certificates/certificate-name/version"

    def test_parse_certificate_id_with_pending_version(self):
        original_id = "https://keyvault-name.vault.azure.net/certificates/certificate-name/pending"
        parsed_certificate_id = parse_certificate_id(original_id)

        assert parsed_certificate_id.name == "certificate-name"
        assert parsed_certificate_id.collection == "certificates"
        assert parsed_certificate_id.vault_url == "https://keyvault-name.vault.azure.net"
        assert parsed_certificate_id.version == "pending"
        assert parsed_certificate_id.original_id == "https://keyvault-name.vault.azure.net/certificates/certificate-name/pending"

    def test_parse_deleted_certificate_id(self):
        original_id = "https://keyvault-name.vault.azure.net/deletedcertificates/deleted-certificate"
        parsed_certificate_id = parse_certificate_id(original_id)

        assert parsed_certificate_id.name == "deleted-certificate"
        assert parsed_certificate_id.collection == "deletedcertificates"
        assert parsed_certificate_id.vault_url == "https://keyvault-name.vault.azure.net"
        assert parsed_certificate_id.version == None
        assert parsed_certificate_id.original_id == "https://keyvault-name.vault.azure.net/deletedcertificates/deleted-certificate"

    def test_parse_certificate_id_with_invalid_collection(self):
        original_id = "https://keyvault-name.vault.azure.net/invalidcollection/certificate"

        with pytest.raises(ValueError) as excinfo:
            parse_certificate_id(original_id)
        assert "Collection 'invalidcollection' is not a valid certificate collection" in str(excinfo.value)
