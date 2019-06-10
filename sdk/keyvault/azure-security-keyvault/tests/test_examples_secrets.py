# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import print_function
import functools
import time

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from devtools_testutils import ResourceGroupPreparer
from preparer import VaultClientPreparer
from test_case import KeyVaultTestCase


def print(*args):
    assert all(arg is not None for arg in args)


def create_vault_client():
    client_id = ""
    client_secret = ""
    tenant_id = ""
    vault_url = ""

    # [START create_vault_client
    from azure.security.keyvault.vault_client import VaultClient
    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credential=credentials)
    # [END create_vault_client]
    return vault_client


def create_secret_client():
    client_id = ""
    client_secret = ""
    tenant_id = ""
    vault_url = ""

    # [START create_secret_client
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.security.keyvault.secrets._client import SecretClient

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Secret client using Azure credentials
    secret_client = SecretClient(vault_url=vault_url, credential=credentials)
    # [END create_secret_client]
    return secret_client


class TestExamplesKeyVault(KeyVaultTestCase):
    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_secret_crud_operations(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        try:
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
        except HttpResponseError:
            pass

        try:
            # [START get_secret]
            secret_version = secret.version

            # get the latest version of a secret
            secret = secret_client.get_secret("secret-name")

            # alternatively, specify a version
            secret = secret_client.get_secret("secret-name", secret_version)

            print(secret.id)
            print(secret.name)
            print(secret.version)
            print(secret.vault_url)

            # [END get_secret]
        except HttpResponseError:
            pass

        try:
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
        except HttpResponseError:
            pass

        try:
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
        except HttpResponseError:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_secret_list_operations(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        try:
            # [START list_secrets]

            # list secrets
            secrets = secret_client.list_secrets()

            for secret in secrets:
                # the list doesn't include values or versions of the secrets
                print(secret.id)
                print(secret.name)

            # [END list_secrets]
        except HttpResponseError:
            pass

        # pylint: disable=unused-variable
        try:
            # [START list_secret_versions]
            # list a secret's versions
            secret_versions = secret_client.list_secret_versions("secret-name")

            for secret in secrets:
                # the list doesn't include the values at each version
                print(secret.version)

            # [END list_secret_versions]
        except HttpResponseError:
            pass

        try:
            # [START list_deleted_secrets]

            # get a list of deleted secrets (requires soft-delete enabled for the vault)
            deleted_secrets = secret_client.list_deleted_secrets()

            for secret in deleted_secrets:
                # the list doesn't include values or versions of the deleted secrets
                print(secret.id)
                print(secret.name)

            # [END list_deleted_secrets]
        except HttpResponseError:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_secrets_backup_restore(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        created_secret = secret_client.set_secret("secret-name", "secret-value")
        secret_name = created_secret.name
        try:
            # [START backup_secret]
            # backup a secret
            secret_backup = secret_client.backup_secret(secret_name)

            # returns the raw bytes of the backed up secret
            print(secret_backup)

            # [END backup_secret]
        except HttpResponseError:
            pass

        try:
            deleted_secret = secret_client.delete_secret(secret_name)
            self._poll_until_no_exception(
                functools.partial(secret_client.get_deleted_secret, secret_name), ResourceNotFoundError
            )

            # [START get_deleted_secret]
            # gets a deleted secret (requires soft-delete enabled for the vault)
            deleted_secret = secret_client.get_deleted_secret("secret-name")
            print(deleted_secret.name)

            # [END get_deleted_secret]
        except HttpResponseError:
            pass

        try:
            # [START restore_secret]

            # restores a backed up secret
            restored_secret = secret_client.restore_secret(secret_backup)
            print(restored_secret.id)
            print(restored_secret.value)
            print(restored_secret.version)

            # [END restore_secret]
        except HttpResponseError:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    def test_example_secrets_recover_purge(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        created_secret = secret_client.set_secret("secret-name", "secret-value")
        secret_client.delete_secret(created_secret.name)
        self._poll_until_no_exception(
            functools.partial(secret_client.get_deleted_secret, created_secret.name), ResourceNotFoundError
        )

        try:
            # [START recover_deleted_secret]

            # recover deleted secret to its latest version
            recover_deleted_secret = secret_client.recover_deleted_secret("secret-name")
            print(recover_deleted_secret.id)
            print(recover_deleted_secret.name)

            # [END recover_deleted_secret]
        except HttpResponseError:
            pass

        try:
            self._poll_until_no_exception(
                functools.partial(secret_client.get_secret, created_secret.name), ResourceNotFoundError
            )

            secret_client.delete_secret(created_secret.name)

            self._poll_until_no_exception(
                functools.partial(secret_client.get_deleted_secret, created_secret.name), ResourceNotFoundError
            )

            # [START purge_deleted_secret]

            # if the vault has soft-delete enabled, purge permanently deletes the secret
            # (without soft-delete, an ordinary delete is permanent)
            secret_client.purge_deleted_secret("secret-name")

            # [END purge_deleted_secret]
        except HttpResponseError:
            pass
