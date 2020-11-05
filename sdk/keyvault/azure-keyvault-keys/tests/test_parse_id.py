# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
import functools
from azure.keyvault.keys import KeyClient, parse_key_vault_key_id
from devtools_testutils import ResourceGroupPreparer, KeyVaultPreparer

from _shared.preparer import KeyVaultClientPreparer as _KeyVaultClientPreparer
from _shared.test_case import KeyVaultTestCase

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
KeyVaultClientPreparer = functools.partial(_KeyVaultClientPreparer, KeyClient)


class TestParseId(KeyVaultTestCase):
    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @KeyVaultClientPreparer()
    def test_parse_key_id_with_version(self, client):
        key_name = self.get_resource_name("key")
        # create key
        created_key = client.create_rsa_key(key_name)

        # [START parse_key_vault_key_id]
        key = client.get_key(key_name)
        parsed_key_id = parse_key_vault_key_id(key.id)

        print(parsed_key_id.name)
        print(parsed_key_id.vault_url)
        print(parsed_key_id.version)
        print(parsed_key_id.source_id)
        # [END parse_key_vault_key_id]
        self.assertEqual(parsed_key_id.name, key_name)
        self.assertEqual(parsed_key_id.vault_url, client.vault_url)
        self.assertEqual(parsed_key_id.version, key.properties.version)
        self.assertEqual(parsed_key_id.source_id, key.id)

    def test_parse_key_id_with_pending_version(self):
        source_id = "https://keyvault-name.vault.azure.net/keys/key-name/pending"
        parsed_key_id = parse_key_vault_key_id(source_id)

        self.assertEqual(parsed_key_id.name, "key-name")
        self.assertEqual(parsed_key_id.vault_url, "https://keyvault-name.vault.azure.net")
        self.assertEqual(parsed_key_id.version, "pending")
        self.assertEqual(
            parsed_key_id.source_id,
            "https://keyvault-name.vault.azure.net/keys/key-name/pending",
        )

    def test_parse_deleted_certificate_id(self):
        source_id = "https://keyvault-name.vault.azure.net/deletedkeys/deleted-key"
        parsed_key_id = parse_key_vault_key_id(source_id)

        self.assertEqual(parsed_key_id.name, "deleted-key")
        self.assertEqual(parsed_key_id.vault_url, "https://keyvault-name.vault.azure.net")
        self.assertIsNone(parsed_key_id.version)
        self.assertEqual(
            parsed_key_id.source_id,
            "https://keyvault-name.vault.azure.net/deletedkeys/deleted-key",
        )
