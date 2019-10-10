# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
from __future__ import print_function
import functools

from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import ResourceGroupPreparer
from secrets_preparer import VaultClientPreparer
from secrets_test_case import KeyVaultTestCase


def print(*args):
    assert all(arg is not None for arg in args)


def test_create_secret_client():
    vault_endpoint = "vault_endpoint"
    # pylint:disable=unused-variable
    # [START create_secret_client]

    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient

    # Create a SecretClient using default Azure credentials
    credentials = DefaultAzureCredential()
    secret_client = SecretClient(vault_endpoint, credentials)

    # [END create_secret_client]


class TestExamplesKeyVault(KeyVaultTestCase):
    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_secret_crud_operations(self, vault_client, **kwargs):
        secret_client = vault_client.secrets

        # [START set_secret]
        from dateutil import parser as date_parse

        expires = date_parse.parse("2050-02-02T08:00:00.000Z")

        # create a secret, setting optional arguments
        secret = secret_client.set_secret("secret-name", "secret-value", expires=expires)

        print(secret.name)
        print(secret.properties.version)
        print(secret.properties.expires)

        # [END set_secret]
        # [START get_secret]

        # get the latest version of a secret
        secret = secret_client.get_secret("secret-name")

        # alternatively, specify a version
        secret = secret_client.get_secret("secret-name", secret.properties.version)

        print(secret.id)
        print(secret.name)
        print(secret.properties.version)
        print(secret.properties.vault_endpoint)

        # [END get_secret]
        # [START update_secret]

        # update attributes of an existing secret

        content_type = "text/plain"
        tags = {"foo": "updated tag"}
        updated_secret_properties = secret_client.update_secret_properties(
            "secret-name", content_type=content_type, tags=tags
        )

        print(updated_secret_properties.version)
        print(updated_secret_properties.updated)
        print(updated_secret_properties.content_type)
        print(updated_secret_properties.tags)

        # [END update_secret]
        # [START delete_secret]

        # delete a secret
        deleted_secret = secret_client.delete_secret("secret-name")

        print(deleted_secret.name)

        # if the vault has soft-delete enabled, the secret's, deleted_date
        # scheduled purge date and recovery id are set
        print(deleted_secret.deleted_date)
        print(deleted_secret.scheduled_purge_date)
        print(deleted_secret.recovery_id)

        # [END delete_secret]

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_secret_list_operations(self, vault_client, **kwargs):
        secret_client = vault_client.secrets

        for i in range(7):
            secret_client.set_secret("key{}".format(i), "value{}".format(i))

        # [START list_secrets]

        # list secrets
        secrets = secret_client.list_secrets()

        for secret in secrets:
            # the list doesn't include values or versions of the secrets
            print(secret.id)
            print(secret.name)
            print(secret.enabled)

        # [END list_secrets]

        # pylint: disable=unused-variable

        # [START list_secret_versions]
        secret_versions = secret_client.list_secret_versions("secret-name")

        for secret in secrets:
            # the list doesn't include the values at each version
            print(secret.id)
            print(secret.enabled)
            print(secret.updated)

        # [END list_secret_versions]
        # [START list_deleted_secrets]

        # gets an iterator of deleted secrets (requires soft-delete enabled for the vault)
        deleted_secrets = secret_client.list_deleted_secrets()

        for secret in deleted_secrets:
            # the list doesn't include values or versions of the deleted secrets
            print(secret.id)
            print(secret.name)
            print(secret.scheduled_purge_date)
            print(secret.recovery_id)
            print(secret.deleted_date)

        # [END list_deleted_secrets]

    @ResourceGroupPreparer()
    @VaultClientPreparer()
    def test_example_secrets_backup_restore(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        created_secret = secret_client.set_secret("secret-name", "secret-value")
        secret_name = created_secret.name
        # [START backup_secret]
        # backup secret
        # returns the raw bytes of the backed up secret
        secret_backup = secret_client.backup_secret("secret-name")

        print(secret_backup)

        # [END backup_secret]
        deleted_secret = secret_client.delete_secret("secret-name")
        # [START restore_secret]

        # restores a backed up secret
        restored_secret = secret_client.restore_secret(secret_backup)
        print(restored_secret.id)
        print(restored_secret.version)

        # [END restore_secret]

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_secrets_recover(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        created_secret = secret_client.set_secret("secret-name", "secret-value")
        secret_client.delete_secret(created_secret.name)

        self._poll_until_no_exception(
            functools.partial(secret_client.get_deleted_secret, created_secret.name), ResourceNotFoundError
        )

        # [START get_deleted_secret]
        # gets a deleted secret (requires soft-delete enabled for the vault)
        deleted_secret = secret_client.get_deleted_secret("secret-name")
        print(deleted_secret.name)

        # [END get_deleted_secret]
        # [START recover_deleted_secret]

        # recover deleted secret to the latest version
        recovered_secret = secret_client.recover_deleted_secret("secret-name")
        print(recovered_secret.id)
        print(recovered_secret.name)

        # [END recover_deleted_secret]
