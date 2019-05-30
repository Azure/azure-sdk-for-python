# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time
import asyncio
import functools

from devtools_testutils import ResourceGroupPreparer
from preparer import VaultClientPreparer
from test_case import KeyVaultTestCase
from azure.security.keyvault._generated.v7_0.models import KeyVaultErrorException
from azure.security.keyvault.aio.vault_client import VaultClient


# TODO: Remove, later?
def await_prepared_test(test_fn):
    """Synchronous wrapper for async test methods. Used to avoid making changes
       upstream to AbstractPreparer (which doesn't await the functions it wraps)
    """
    @functools.wraps(test_fn)
    def run(test_class_instance, *args, **kwargs):
        # TODO: this is a workaround for VaultClientPreparer creating a sync client; let's obviate it
        vault_client = kwargs.get("vault_client")
        credentials = test_class_instance.settings.get_credentials(
            resource="https://vault.azure.net")
        aio_client = VaultClient(vault_client.vault_url, credentials)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_fn(test_class_instance, vault_client=aio_client))
    return run


class TestExamplesKeyVault(KeyVaultTestCase):

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_example_secret_crud_operations(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        try:
            # [START set_secret]
            from dateutil import parser as date_parse

            expires = date_parse.parse('2050-02-02T08:00:00.000Z')

            # create a secret with optional arguments
            secret = await secret_client.set_secret('secret-name', 'secret-value', enabled=True, expires=expires)

            print(secret.version)
            print(secret.created)
            print(secret.enabled)
            print(secret.expires)

            # [END set_secret]
        except KeyVaultErrorException:
            pass

        try:
            secret_version = secret.version
            # [START get_secret]

            # get secret with version
            secret = await secret_client.get_secret('secret-name', secret_version)

            # if the version argument is an empty string or None, the latest
            # version of the secret will be returned
            secret = await secret_client.get_secret('secret-name', '')

            print(secret.id)
            print(secret.name)
            print(secret.version)
            print(secret.vault_url)
            # [END get_secret]
        except KeyVaultErrorException:
            pass

        try:
            # [START update_secret_attributes]

            # update attributes of an existing secret

            content_type = 'text/plain'
            tags = {'foo': 'updated tag'}
            secret_version = secret.version
            updated_secret = await secret_client.update_secret_attributes(
                'secret-name', secret_version,
                content_type=content_type,
                tags=tags)

            print(updated_secret.version)
            print(updated_secret.updated)
            print(updated_secret.content_type)
            print(updated_secret.tags)

            # [END update_secret_attributes]
        except KeyVaultErrorException:
            pass

        try:
            # [START delete_secret]

            # delete a secret
            deleted_secret = await secret_client.delete_secret('secret-name')

            print(deleted_secret.name)
            print(deleted_secret.deleted_date)

            # [END delete_secret]
        except KeyVaultErrorException:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_example_secret_list_operations(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        try:
            # [START list_secrets]

            # gets a list of secrets in the vault
            secrets = secret_client.list_secrets()

            async for secret in secrets:
                # the list doesn't include values or versions of the secrets
                print(secret.id)
                print(secret.name)

            # [END list_secrets]
        except KeyVaultErrorException:
            pass

        try:
            # [START list_secret_versions]
            from azure.security.keyvault.vault_client import VaultClient

            # gets a list of all versions of a secret
            secret_versions = secret_client.list_secret_versions('secret-name')

            async for secret in secret_versions:
                # the list doesn't include secret values
                print(secret.id)
                print(secret.name)

            # [END list_secret_versions]
        except KeyVaultErrorException:
            pass

        try:
            # [START list_deleted_secrets]

            # gets a list of deleted secrets (requires soft-delete enabled for the vault)
            deleted_secrets = secret_client.list_deleted_secrets()

            async for secret in deleted_secrets:
                # the list doesn't include values or versions of the deleted secrets
                print(secret.id)
                print(secret.name)

            # [END list_deleted_secrets]
        except KeyVaultErrorException:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_example_secrets_backup_restore(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        created_secret = await secret_client.set_secret('secret-name', 'secret-value')
        secret_name = created_secret.name
        try:
            # [START backup_secret]
            # backup secret
            secret_backup = await secret_client.backup_secret(secret_name)

            # returns the raw bytes of the backed up secret
            print(secret_backup)

            # [END backup_secret]
        except KeyVaultErrorException:
            pass

        try:
            deleted_secret = await secret_client.delete_secret(secret_name)
            if self.is_live:
                # wait a second to ensure the secret has been deleted
                time.sleep(20)

            # [START get_deleted_secret]
            # gets a deleted secret (requires soft-delete enabled for the vault)
            deleted_secret = await secret_client.get_deleted_secret('secret-name')
            print(deleted_secret.name)

            # [END get_deleted_secret]
        except KeyVaultErrorException:
            pass

        try:
            await secret_client.purge_deleted_secret(created_secret.name)
            if self.is_live:
                # wait a second to ensure the secret has been deleted
                time.sleep(20)
            # [START restore_secret]

            # restores a backed up secret
            restored_secret = await secret_client.restore_secret(secret_backup)
            print(restored_secret.id)
            print(restored_secret.version)

            # [END restore_secret]
        except KeyVaultErrorException:
            pass

    @ResourceGroupPreparer()
    @VaultClientPreparer(enable_soft_delete=True)
    @await_prepared_test
    async def test_example_secrets_recover_purge(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        created_secret = await secret_client.set_secret('secret-name', 'secret-value')
        await secret_client.delete_secret(created_secret.name)
        if self.is_live:
            # wait a second to ensure the secret has been deleted
            time.sleep(50)

        try:
            # [START recover_deleted_secret]

            # recover deleted secret to the latest version
            recover_deleted_secret = await secret_client.recover_deleted_secret(
                'secret-name')
            print(recover_deleted_secret.id)
            print(recover_deleted_secret.name)

            # [END recover_deleted_secret]
        except KeyVaultErrorException:
            pass

        try:
            if self.is_live:
                # wait a second to ensure the secret has been recovered
                time.sleep(50)
            await secret_client.delete_secret(created_secret.name)
            if self.is_live:
                # wait a second to ensure the secret has been deleted
                time.sleep(50)
            # [START purge_deleted_secret]

            # if the vault has soft-delete enabled, purge permanently deletes the secret
            # (without soft-delete, an ordinary delete is permanent)
            await secret_client.purge_deleted_secret('secret-name')

            # [END purge_deleted_secret]
        except KeyVaultErrorException:
            pass
