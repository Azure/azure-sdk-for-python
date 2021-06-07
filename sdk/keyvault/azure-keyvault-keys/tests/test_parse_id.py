# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from azure.keyvault.keys import KeyVaultKeyIdentifier

from _shared.test_case import KeyVaultTestCase
from _test_case import KeysTestCase


class TestParseId(KeysTestCase, KeyVaultTestCase):
    def test_parse_key_id_with_version(self):
        client = self.create_key_client(self.vault_url)
        key_name = self.get_resource_name("key")
        # create key
        created_key = client.create_rsa_key(key_name)

        # [START parse_key_vault_key_id]
        key = client.get_key(key_name)
        parsed_key_id = KeyVaultKeyIdentifier(key.id)

        print(parsed_key_id.name)
        print(parsed_key_id.vault_url)
        print(parsed_key_id.version)
        print(parsed_key_id.source_id)
        # [END parse_key_vault_key_id]
        assert parsed_key_id.name == key_name
        assert parsed_key_id.vault_url == client.vault_url
        assert parsed_key_id.version == key.properties.version
        assert parsed_key_id.source_id == key.id


def test_parse_key_id_with_pending_version():
    source_id = "https://keyvault-name.vault.azure.net/keys/key-name/pending"
    parsed_key_id = KeyVaultKeyIdentifier(source_id)

    assert parsed_key_id.name == "key-name"
    assert parsed_key_id.vault_url == "https://keyvault-name.vault.azure.net"
    assert parsed_key_id.version == "pending"
    assert parsed_key_id.source_id == "https://keyvault-name.vault.azure.net/keys/key-name/pending"


def test_parse_deleted_key_id():
    source_id = "https://keyvault-name.vault.azure.net/deletedkeys/deleted-key"
    parsed_key_id = KeyVaultKeyIdentifier(source_id)

    assert parsed_key_id.name == "deleted-key"
    assert parsed_key_id.vault_url == "https://keyvault-name.vault.azure.net"
    assert parsed_key_id.version is None
    assert parsed_key_id.source_id == "https://keyvault-name.vault.azure.net/deletedkeys/deleted-key"
