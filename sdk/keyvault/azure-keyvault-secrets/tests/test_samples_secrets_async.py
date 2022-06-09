# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
import asyncio


import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.sanitizers import set_custom_default_matcher

from _async_test_case import AsyncSecretsClientPreparer
from _shared.test_case_async import KeyVaultTestCase
from _test_case import get_decorator

all_api_versions = get_decorator()


def print(*args):
    assert all(arg is not None for arg in args)


@pytest.mark.asyncio
async def test_create_secret_client():
    vault_url = "vault_url"
    # pylint:disable=unused-variable
    # [START create_secret_client]
    from azure.identity.aio import DefaultAzureCredential
    from azure.keyvault.secrets.aio import SecretClient

    # Create a SecretClient using default Azure credentials
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url, credential)

    # the client and credential should be closed when no longer needed
    # (both are also async context managers)
    await secret_client.close()
    await credential.close()
    # [END create_secret_client]


class TestExamplesKeyVault(KeyVaultTestCase):
    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_example_secret_crud_operations(self, **kwargs):
        client = kwargs.pop("client")
        secret_client = client
        secret_name = self.get_resource_name("secret-name")

        # [START set_secret]
        from dateutil import parser as date_parse

        expires_on = date_parse.parse("2050-02-02T08:00:00.000Z")
        async with secret_client:
            # create a secret, setting optional arguments
            secret = await secret_client.set_secret(secret_name, "secret-value", enabled=True, expires_on=expires_on)

            print(secret.id)
            print(secret.name)
            print(secret.properties.enabled)
            print(secret.properties.expires_on)
            # [END set_secret]

            secret_version = secret.properties.version
            # [START get_secret]
            # get the latest version of a secret
            secret = await secret_client.get_secret(secret_name)

            # alternatively, specify a version
            secret = await secret_client.get_secret(secret_name, secret_version)

            print(secret.id)
            print(secret.name)
            print(secret.properties.version)
            print(secret.properties.vault_url)
            # [END get_secret]

            # [START update_secret]
            # update attributes of an existing secret
            content_type = "text/plain"
            tags = {"foo": "updated tag"}
            updated_secret_properties = await secret_client.update_secret_properties(
                secret_name, content_type=content_type, tags=tags
            )

            print(updated_secret_properties.version)
            print(updated_secret_properties.updated_on)
            print(updated_secret_properties.content_type)
            print(updated_secret_properties.tags)
            # [END update_secret]

            # [START delete_secret]
            # delete a secret
            deleted_secret = await secret_client.delete_secret(secret_name)

            print(deleted_secret.name)

            # if the vault has soft-delete enabled, the secret's deleted_date,
            # scheduled purge date and recovery id are set
            print(deleted_secret.deleted_date)
            print(deleted_secret.scheduled_purge_date)
            print(deleted_secret.recovery_id)
            # [END delete_secret]

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_example_secret_list_operations(self, **kwargs):
        client = kwargs.pop("client")
        if not is_live():
            set_custom_default_matcher(excluded_headers="Authorization")
        secret_client = client
        async with secret_client:
            for i in range(7):
                secret_name = self.get_resource_name("secret{}".format(i))
                await secret_client.set_secret(secret_name, "value{}".format(i))

            # [START list_secrets]
            # gets a list of secrets in the vault
            secrets = secret_client.list_properties_of_secrets()

            async for secret in secrets:
                # the list doesn't include values or versions of the secrets
                print(secret.id)
                print(secret.name)
                print(secret.enabled)
            # [END list_secrets]

            # [START list_properties_of_secret_versions]
            # gets a list of all versions of a secret
            secret_versions = secret_client.list_properties_of_secret_versions("secret-name")

            async for secret in secret_versions:
                # the list doesn't include the versions' values
                print(secret.id)
                print(secret.enabled)
                print(secret.updated_on)
            # [END list_properties_of_secret_versions]

            # [START list_deleted_secrets]
            # gets a list of deleted secrets (requires soft-delete enabled for the vault)
            deleted_secrets = secret_client.list_deleted_secrets()

            async for secret in deleted_secrets:
                # the list doesn't include values or versions of the deleted secrets
                print(secret.id)
                print(secret.name)
                print(secret.scheduled_purge_date)
                print(secret.recovery_id)
                print(secret.deleted_date)
            # [END list_deleted_secrets]

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_example_secrets_backup_restore(self, **kwargs):
        client = kwargs.pop("client")
        secret_client = client
        secret_name = self.get_resource_name("secret-name")
        async with secret_client:
            await secret_client.set_secret(secret_name, "secret-value")
            # [START backup_secret]
            # backup secret
            secret_backup = await secret_client.backup_secret(secret_name)

            # returns the raw bytes of the backed up secret
            print(secret_backup)
            # [END backup_secret]

            await secret_client.delete_secret(secret_name)
            await secret_client.purge_deleted_secret(secret_name)

            if self.is_live:
                await asyncio.sleep(60)

            # [START restore_secret_backup]
            # restores a backed up secret
            restored_secret = await secret_client.restore_secret_backup(secret_backup)
            print(restored_secret.id)
            print(restored_secret.version)
            # [END restore_secret_backup]

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("api_version", all_api_versions, ids=all_api_versions)
    @AsyncSecretsClientPreparer()
    @recorded_by_proxy_async
    async def test_example_secrets_recover(self, **kwargs):
        client = kwargs.pop("client")
        secret_client = client
        secret_name = self.get_resource_name("secret-name")
        async with client:
            await secret_client.set_secret(secret_name, "secret-value")
            await secret_client.delete_secret(secret_name)

            # [START get_deleted_secret]
            # gets a deleted secret (requires soft-delete enabled for the vault)
            deleted_secret = await secret_client.get_deleted_secret(secret_name)
            print(deleted_secret.name)
            # [END get_deleted_secret]

            # [START recover_deleted_secret]
            # recover deleted secret to the latest version
            recovered_secret = await secret_client.recover_deleted_secret(secret_name)
            print(recovered_secret.id)
            print(recovered_secret.name)
            # [END recover_deleted_secret]
