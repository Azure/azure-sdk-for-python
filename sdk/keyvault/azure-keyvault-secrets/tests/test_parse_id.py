# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
import functools
from azure.keyvault.secrets import SecretClient, parse_key_vault_secret_id
from devtools_testutils import ResourceGroupPreparer, KeyVaultPreparer

from _shared.preparer import KeyVaultClientPreparer as _KeyVaultClientPreparer
from _shared.test_case import KeyVaultTestCase

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
KeyVaultClientPreparer = functools.partial(_KeyVaultClientPreparer, SecretClient)


class TestParseId(KeyVaultTestCase):
    @ResourceGroupPreparer(random_name_enabled=True)
    @KeyVaultPreparer()
    @KeyVaultClientPreparer()
    def test_parse_secret_id_with_version(self, client):
        secret_name = self.get_resource_name("secret")
        secret_value = "secret_value"
        # create secret
        created_secret = client.set_secret(secret_name, secret_value)

        # [START parse_key_vault_secret_id]
        secret = client.get_secret(secret_name)
        parsed_secret_id = parse_key_vault_secret_id(secret.id)

        print(parsed_secret_id.name)
        print(parsed_secret_id.vault_url)
        print(parsed_secret_id.version)
        print(parsed_secret_id.source_id)
        # [END parse_key_vault_secret_id]
        self.assertEqual(parsed_secret_id.name, secret_name)
        self.assertEqual(parsed_secret_id.vault_url, client.vault_url)
        self.assertEqual(parsed_secret_id.version, secret.properties.version)
        self.assertEqual(parsed_secret_id.source_id, secret.id)

    def test_parse_secret_id_with_pending_version(self):
        source_id = "https://keyvault-name.vault.azure.net/secrets/secret-name/pending"
        parsed_secret_id = parse_key_vault_secret_id(source_id)

        self.assertEqual(parsed_secret_id.name, "secret-name")
        self.assertEqual(parsed_secret_id.vault_url, "https://keyvault-name.vault.azure.net")
        self.assertEqual(parsed_secret_id.version, "pending")
        self.assertEqual(
            parsed_secret_id.source_id,
            "https://keyvault-name.vault.azure.net/secrets/secret-name/pending",
        )

    def test_parse_deleted_secret_id(self):
        source_id = "https://keyvault-name.vault.azure.net/deletedsecrets/deleted-secret"
        parsed_secret_id = parse_key_vault_secret_id(source_id)

        self.assertEqual(parsed_secret_id.name, "deleted-secret")
        self.assertEqual(parsed_secret_id.vault_url, "https://keyvault-name.vault.azure.net")
        self.assertIsNone(parsed_secret_id.version)
        self.assertEqual(
            parsed_secret_id.source_id,
            "https://keyvault-name.vault.azure.net/deletedsecrets/deleted-secret",
        )
