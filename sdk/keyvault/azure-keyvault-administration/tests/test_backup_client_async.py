# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest import mock
from urllib.parse import urlparse

from azure.core.credentials import AccessToken
from azure.core.exceptions import ResourceExistsError
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient
from azure.keyvault.administration._internal import HttpChallengeCache
from azure.keyvault.administration.aio import KeyVaultBackupClient
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
import pytest

from _shared.test_case_async import KeyVaultTestCase
from blob_container_preparer import BlobContainerPreparer


@pytest.mark.usefixtures("managed_hsm")
class BackupClientTests(KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, match_body=False, **kwargs)

    def setUp(self, *args, **kwargs):
        if self.is_live:
            real = urlparse(self.managed_hsm["url"])
            playback = urlparse(self.managed_hsm["playback_url"])
            self.scrubber.register_name_pair(real.netloc, playback.netloc)
        super().setUp(*args, **kwargs)

    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(KeyVaultTestCase, self).tearDown()

    @property
    def credential(self):
        if self.is_live:
            return DefaultAzureCredential()

        async def get_token(*_, **__):
            return AccessToken("secret", time.time() + 3600)

        return mock.Mock(get_token=get_token)

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @StorageAccountPreparer(random_name_enabled=True)
    @BlobContainerPreparer()
    async def test_full_backup_and_restore(self, container_uri, sas_token):
        # backup the vault
        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)
        backup_poller = await backup_client.begin_backup(container_uri, sas_token)
        backup_operation = await backup_poller.result()
        assert backup_operation.folder_url

        # restore the backup
        restore_poller = await backup_client.begin_restore(backup_operation.folder_url, sas_token)
        await restore_poller.wait()

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @StorageAccountPreparer(random_name_enabled=True)
    @BlobContainerPreparer()
    async def test_full_backup_and_restore_rehydration(self, container_uri, sas_token):
        if not self.is_live:
            pytest.skip("Poller requests are incompatible with vcrpy in playback")

        # backup the vault
        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)
        backup_poller = await backup_client.begin_backup(container_uri, sas_token)

        # create a new poller from a continuation token
        token = backup_poller.continuation_token()
        rehydrated = await backup_client.begin_backup(container_uri, sas_token, continuation_token=token)

        rehydrated_operation = await rehydrated.result()
        assert rehydrated_operation.folder_url
        backup_operation = await backup_poller.result()
        assert backup_operation.folder_url == rehydrated_operation.folder_url

        # restore the backup
        restore_poller = await backup_client.begin_restore(backup_operation.folder_url, sas_token)

        # create a new poller from a continuation token
        token = restore_poller.continuation_token()
        rehydrated = await backup_client.begin_restore(backup_operation.folder_url, sas_token, continuation_token=token)

        await rehydrated.wait()
        await restore_poller.wait()

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @StorageAccountPreparer(random_name_enabled=True)
    @BlobContainerPreparer()
    async def test_selective_key_restore(self, container_uri, sas_token):
        # create a key to selectively restore
        key_client = KeyClient(self.managed_hsm["url"], self.credential)
        key_name = self.get_resource_name("selective-restore-test-key")
        await key_client.create_rsa_key(key_name)

        # backup the vault
        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)
        backup_poller = await backup_client.begin_backup(container_uri, sas_token)
        backup_operation = await backup_poller.result()

        # restore the key
        restore_poller = await backup_client.begin_restore(backup_operation.folder_url, sas_token, key_name=key_name)
        await restore_poller.wait()

        # delete the key
        await self._poll_until_no_exception(key_client.delete_key, key_name, expected_exception=ResourceExistsError)
        await key_client.purge_deleted_key(key_name)

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @StorageAccountPreparer(random_name_enabled=True)
    @BlobContainerPreparer()
    async def test_backup_client_polling(self, container_uri, sas_token):
        if not self.is_live:
            pytest.skip("Poller requests are incompatible with vcrpy in playback")

        # backup the vault
        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)
        backup_poller = await backup_client.begin_backup(container_uri, sas_token)
        
        # create a new poller from a continuation token
        token = backup_poller.continuation_token()
        rehydrated = await backup_client.begin_backup(container_uri, sas_token, continuation_token=token)

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
        late_rehydrated = await backup_client.begin_backup(container_uri, sas_token, continuation_token=token)
        assert late_rehydrated.status() == "Succeeded"

        # restore the backup
        restore_poller = await backup_client.begin_restore(backup_operation.folder_url, sas_token)

        # create a new poller from a continuation token
        token = restore_poller.continuation_token()
        rehydrated = await backup_client.begin_restore(backup_operation.folder_url, sas_token, continuation_token=token)

        # check that pollers and polling methods behave as expected
        assert restore_poller.status() == "InProgress"
        assert not restore_poller.done() or restore_poller.polling_method().finished()
        assert rehydrated.status() == "InProgress"
        assert not rehydrated.done() or rehydrated.polling_method().finished()

        await rehydrated.wait()
        assert rehydrated.status() == "Succeeded" and rehydrated.polling_method().status() == "Succeeded"
        await restore_poller.wait()
        assert restore_poller.status() == "Succeeded" and restore_poller.polling_method().status() == "Succeeded"
