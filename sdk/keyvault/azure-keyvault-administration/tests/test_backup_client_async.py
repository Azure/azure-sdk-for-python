# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio

from azure.core.exceptions import ResourceExistsError
import pytest

from _shared.test_case_async import KeyVaultTestCase
from _test_case import AdministrationTestCase, backup_client_setup, get_decorator


all_api_versions = get_decorator(is_async=True)


class BackupClientTests(AdministrationTestCase, KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, match_body=False, **kwargs)

    @all_api_versions()
    @backup_client_setup
    async def test_full_backup_and_restore(self, client):
        # backup the vault
        backup_poller = await client.begin_backup(self.container_uri, self.sas_token)
        backup_operation = await backup_poller.result()
        assert backup_operation.folder_url

        # restore the backup
        restore_poller = await client.begin_restore(backup_operation.folder_url, self.sas_token)
        await restore_poller.wait()
        if self.is_live:
            await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @all_api_versions()
    @backup_client_setup
    async def test_full_backup_and_restore_rehydration(self, client):
        if not self.is_live:
            pytest.skip("Poller requests are incompatible with vcrpy in playback")

        # backup the vault
        backup_poller = await client.begin_backup(self.container_uri, self.sas_token)

        # create a new poller from a continuation token
        token = backup_poller.continuation_token()
        rehydrated = await client.begin_backup(self.container_uri, self.sas_token, continuation_token=token)

        rehydrated_operation = await rehydrated.result()
        assert rehydrated_operation.folder_url
        backup_operation = await backup_poller.result()
        assert backup_operation.folder_url == rehydrated_operation.folder_url

        # restore the backup
        restore_poller = await client.begin_restore(backup_operation.folder_url, self.sas_token)

        # create a new poller from a continuation token
        token = restore_poller.continuation_token()
        rehydrated = await client.begin_restore(backup_operation.folder_url, self.sas_token, continuation_token=token)

        await rehydrated.wait()
        await restore_poller.wait()
        if self.is_live:
            await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @all_api_versions()
    @backup_client_setup
    async def test_selective_key_restore(self, client):
        # create a key to selectively restore
        key_client = self.create_key_client(self.managed_hsm_url, is_async=True)
        key_name = self.get_resource_name("selective-restore-test-key")
        await key_client.create_rsa_key(key_name)

        # backup the vault
        backup_poller = await client.begin_backup(self.container_uri, self.sas_token)
        backup_operation = await backup_poller.result()

        # restore the key
        restore_poller = await client.begin_restore(backup_operation.folder_url, self.sas_token, key_name=key_name)
        await restore_poller.wait()

        # delete the key
        await self._poll_until_no_exception(key_client.delete_key, key_name, expected_exception=ResourceExistsError)
        await key_client.purge_deleted_key(key_name)
        if self.is_live:
            await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @all_api_versions()
    @backup_client_setup
    async def test_backup_client_polling(self, client):
        if not self.is_live:
            pytest.skip("Poller requests are incompatible with vcrpy in playback")

        # backup the vault
        backup_poller = await client.begin_backup(self.container_uri, self.sas_token)
        
        # create a new poller from a continuation token
        token = backup_poller.continuation_token()
        rehydrated = await client.begin_backup(self.container_uri, self.sas_token, continuation_token=token)

        # check that pollers and polling methods behave as expected
        assert backup_poller.status() == "InProgress"
        assert not backup_poller.done() or backup_poller.polling_method().finished()
        assert rehydrated.status() == "InProgress"
        assert not rehydrated.done() or rehydrated.polling_method().finished()

        backup_operation = await backup_poller.result()
        assert backup_poller.status() == "Succeeded" and backup_poller.polling_method().status() == "Succeeded"
        rehydrated_operation = await rehydrated.result()
        assert rehydrated.status() == "Succeeded" and rehydrated.polling_method().status() == "Succeeded"
        assert backup_operation.folder_url == rehydrated_operation.folder_url

        # rehydrate a poller with a continuation token of a completed operation
        late_rehydrated = await client.begin_backup(self.container_uri, self.sas_token, continuation_token=token)
        assert late_rehydrated.status() == "Succeeded"
        await late_rehydrated.wait()

        # restore the backup
        restore_poller = await client.begin_restore(backup_operation.folder_url, self.sas_token)

        # create a new poller from a continuation token
        token = restore_poller.continuation_token()
        rehydrated = await client.begin_restore(backup_operation.folder_url, self.sas_token, continuation_token=token)

        # check that pollers and polling methods behave as expected
        assert restore_poller.status() == "InProgress"
        assert not restore_poller.done() or restore_poller.polling_method().finished()
        assert rehydrated.status() == "InProgress"
        assert not rehydrated.done() or rehydrated.polling_method().finished()

        await rehydrated.wait()
        assert rehydrated.status() == "Succeeded" and rehydrated.polling_method().status() == "Succeeded"
        await restore_poller.wait()
        assert restore_poller.status() == "Succeeded" and restore_poller.polling_method().status() == "Succeeded"

        if self.is_live:
            await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests
