# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------

import pytest
from azure.keyvault.secrets import KeyVaultSecretIdentifier
from azure.keyvault.secrets._shared.client_base import DEFAULT_VERSION
from devtools_testutils import recorded_by_proxy

from _shared.test_case import KeyVaultTestCase
from _test_case import SecretsClientPreparer


class TestParseId(KeyVaultTestCase):
    @pytest.mark.parametrize("api_version", [(DEFAULT_VERSION)])
    @SecretsClientPreparer()
    @recorded_by_proxy
    def test_parse_secret_id_with_version(self, client, **kwargs):
        secret_name = self.get_resource_name("secret")
        secret_value = "secret_value"
        # create secret
        created_secret = client.set_secret(secret_name, secret_value)

        # [START parse_key_vault_secret_id]
        secret = client.get_secret(secret_name)
        parsed_secret_id = KeyVaultSecretIdentifier(secret.id)

        print(parsed_secret_id.name)
        print(parsed_secret_id.vault_url)
        print(parsed_secret_id.version)
        print(parsed_secret_id.source_id)
        # [END parse_key_vault_secret_id]
        assert parsed_secret_id.name == secret_name
        assert parsed_secret_id.vault_url == client.vault_url
        assert parsed_secret_id.version == secret.properties.version
        assert parsed_secret_id.source_id == secret.id


def test_parse_secret_id_with_pending_version():
    source_id = "https://keyvault-name.vault.azure.net/secrets/secret-name/pending"
    parsed_secret_id = KeyVaultSecretIdentifier(source_id)

    assert parsed_secret_id.name == "secret-name"
    assert parsed_secret_id.vault_url == "https://keyvault-name.vault.azure.net"
    assert parsed_secret_id.version == "pending"
    assert parsed_secret_id.source_id == "https://keyvault-name.vault.azure.net/secrets/secret-name/pending"


def test_parse_deleted_secret_id():
    source_id = "https://keyvault-name.vault.azure.net/deletedsecrets/deleted-secret"
    parsed_secret_id = KeyVaultSecretIdentifier(source_id)

    assert parsed_secret_id.name == "deleted-secret"
    assert parsed_secret_id.vault_url == "https://keyvault-name.vault.azure.net"
    assert parsed_secret_id.version is None
    assert parsed_secret_id.source_id == "https://keyvault-name.vault.azure.net/deletedsecrets/deleted-secret"
