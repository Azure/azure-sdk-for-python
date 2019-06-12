# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import print_function
import functools

from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import ResourceGroupPreparer
from preparer import VaultClientPreparer
from test_case import KeyVaultTestCase


def print(*args):
    assert all(arg is not None for arg in args)


def test_create_secret_client():
    vault_url = "vault_url"
    # pylint:disable=unused-variable
    # [START create_secret_client]

    from azure.identity import DefaultAzureCredential
    from azure.security.keyvault.secrets import SecretClient

    # Create a SecretClient using default Azure credentials
    credentials = DefaultAzureCredential()
    secret_client = SecretClient(vault_url, credentials)

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
        secret = secret_client.set_secret("secret-name", "secret-value", enabled=True, expires=expires)

        print(secret.version)
        print(secret.created)
        print(secret.enabled)
        print(secret.expires)

        # [END set_secret]
        # [START get_secret]

        # get the latest version of a secret
        secret = secret_client.get_secret("secret-name")

        # alternatively, specify a version
        secret = secret_client.get_secret("secret-name", secret.version)

        print(secret.id)
        print(secret.name)
        print(secret.version)
        print(secret.vault_url)

        # [END get_secret]
        # [START update_secret]

        # update attributes of an existing secret

        content_type = "text/plain"
        tags = {"foo": "updated tag"}
        updated_secret = secret_client.update_secret("secret-name", content_type=content_type, tags=tags)

        print(updated_secret.version)
        print(updated_secret.updated)
        print(updated_secret.content_type)
        print(updated_secret.tags)

        # [END update_secret]
        # [START delete_secret]

        # delete a secret
        deleted_secret = secret_client.delete_secret("secret-name")

        print(deleted_secret.name)
        print(deleted_secret.deleted_date)

        # if the vault has soft-delete enabled, the secret's
        # scheduled purge date and recovery id are set
        print(deleted_secret.scheduled_purge_date)
        print(deleted_secret.recovery_id)

        # [END delete_secret]

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_secret_list_operations(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        # [START list_secrets]

        # list secrets
        secrets = secret_client.list_secrets()

        for secret in secrets:
            # the list doesn't include values or versions of the secrets
            print(secret.id)
            print(secret.name)

        # [END list_secrets]

        # pylint: disable=unused-variable

        # [START list_secret_versions]
        # list a secret's versions
        secret_versions = secret_client.list_secret_versions("secret-name")

        for secret in secrets:
            # the list doesn't include the values at each version
            print(secret.version)

        # [END list_secret_versions]
        # [START list_deleted_secrets]

        # get a list of deleted secrets (requires soft-delete enabled for the vault)
        deleted_secrets = secret_client.list_deleted_secrets()

        for secret in deleted_secrets:
            # the list doesn't include values or versions of the deleted secrets
            print(secret.id)
            print(secret.name)

        # [END list_deleted_secrets]

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
