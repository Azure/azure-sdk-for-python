# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio

import pytest
from azure.core.exceptions import ResourceExistsError
from devtools_testutils import set_bodiless_matcher
from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import KeyVaultBackupClientPreparer, get_decorator
from _shared.test_case_async import KeyVaultTestCase

all_api_versions = get_decorator(is_async=True)


class TestBackupClientTests(KeyVaultTestCase):
    def create_key_client(self, vault_uri, **kwargs):
         from azure.keyvault.keys.aio import KeyClient
         credential = self.get_credential(KeyClient, is_async=True)
         return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @KeyVaultBackupClientPreparer()
    @recorded_by_proxy_async
    async def test_full_backup_and_restore(self, **kwargs):
        client = kwargs.pop("client")
        set_bodiless_matcher()
        # backup the vault
        container_uri = kwargs.pop("container_uri")
        sas_token = kwargs.pop("sas_token")
        backup_poller = await client.begin_backup(container_uri, sas_token)
        backup_operation = await backup_poller.result()
        assert backup_operation.folder_url

        # restore the backup
        restore_poller = await client.begin_restore(backup_operation.folder_url, sas_token)
        await restore_poller.wait()
        if self.is_live:
            await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @KeyVaultBackupClientPreparer()
    @recorded_by_proxy_async
    async def test_full_backup_and_restore_rehydration(self, **kwargs):
        client = kwargs.pop("client")
        set_bodiless_matcher()

        # backup the vault
        container_uri = kwargs.pop("container_uri")
        sas_token = kwargs.pop("sas_token")
        backup_poller = await client.begin_backup(container_uri, sas_token)

        # create a new poller from a continuation token
        token = backup_poller.continuation_token()
        rehydrated = await client.begin_backup(container_uri, sas_token, continuation_token=token)

        rehydrated_operation = await rehydrated.result()
        assert rehydrated_operation.folder_url
        backup_operation = await backup_poller.result()
        assert backup_operation.folder_url == rehydrated_operation.folder_url

        # restore the backup
        restore_poller = await client.begin_restore(backup_operation.folder_url, sas_token)

        # create a new poller from a continuation token
        token = restore_poller.continuation_token()
        rehydrated = await client.begin_restore(backup_operation.folder_url, sas_token, continuation_token=token)

        await rehydrated.wait()
        await restore_poller.wait()
        if self.is_live:
            await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @KeyVaultBackupClientPreparer()
    @recorded_by_proxy_async
    async def test_selective_key_restore(self, **kwargs):
        client = kwargs.pop("client")
        set_bodiless_matcher()
        # create a key to selectively restore
        managed_hsm_url = kwargs.pop("managed_hsm_url")
        key_client = self.create_key_client(managed_hsm_url, is_async=True)
        key_name = self.get_resource_name("selective-restore-test-key")
        await key_client.create_rsa_key(key_name)

        # backup the vault
        container_uri = kwargs.pop("container_uri")
        sas_token = kwargs.pop("sas_token")
        backup_poller = await client.begin_backup(container_uri, sas_token)
        backup_operation = await backup_poller.result()

        # restore the key
        restore_poller = await client.begin_restore(backup_operation.folder_url, sas_token, key_name=key_name)
        await restore_poller.wait()

        # delete the key
        await self._poll_until_no_exception(key_client.delete_key, key_name, expected_exception=ResourceExistsError)
        await key_client.purge_deleted_key(key_name)
        if self.is_live:
            await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @KeyVaultBackupClientPreparer()
    @recorded_by_proxy_async
    async def test_backup_client_polling(self, **kwargs):
        client = kwargs.pop("client")
        set_bodiless_matcher()

        # backup the vault
        container_uri = kwargs.pop("container_uri")
        sas_token = kwargs.pop("sas_token")
        backup_poller = await client.begin_backup(container_uri, sas_token)
        
        # create a new poller from a continuation token
        token = backup_poller.continuation_token()
        rehydrated = await client.begin_backup(container_uri, sas_token, continuation_token=token)

        # check that pollers and polling methods behave as expected
        if self.is_live:
            assert backup_poller.status() == "InProgress"
        assert not backup_poller.done() or backup_poller.polling_method().finished()
        #assert rehydrated.status() == "InProgress"
        assert not rehydrated.done() or rehydrated.polling_method().finished()

        backup_operation = await backup_poller.result()
        assert backup_poller.status() == "Succeeded" and backup_poller.polling_method().status() == "Succeeded"
        rehydrated_operation = await rehydrated.result()
        assert rehydrated.status() == "Succeeded" and rehydrated.polling_method().status() == "Succeeded"
        assert backup_operation.folder_url == rehydrated_operation.folder_url

        # rehydrate a poller with a continuation token of a completed operation
        late_rehydrated = await client.begin_backup(container_uri, sas_token, continuation_token=token)
        assert late_rehydrated.status() == "Succeeded"
        await late_rehydrated.wait()

        # restore the backup
        restore_poller = await client.begin_restore(backup_operation.folder_url, sas_token)

        # create a new poller from a continuation token
        token = restore_poller.continuation_token()
        rehydrated = await client.begin_restore(backup_operation.folder_url, sas_token, continuation_token=token)

        # check that pollers and polling methods behave as expected
        if self.is_live:
            assert restore_poller.status() == "InProgress"
        assert not restore_poller.done() or restore_poller.polling_method().finished()
        #assert rehydrated.status() == "InProgress"
        assert not rehydrated.done() or rehydrated.polling_method().finished()

        await rehydrated.wait()
        assert rehydrated.status() == "Succeeded" and rehydrated.polling_method().status() == "Succeeded"
        await restore_poller.wait()
        assert restore_poller.status() == "Succeeded" and restore_poller.polling_method().status() == "Succeeded"

        if self.is_live:
            await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests
