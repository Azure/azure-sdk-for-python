# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from unittest import mock
from urllib.parse import urlparse

from azure.core.credentials import AccessToken
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.administration._internal import HttpChallengeCache
from azure.keyvault.administration.aio import KeyVaultBackupClient
from azure.keyvault.keys.aio import KeyClient
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
import pytest

from _shared.test_case_async import KeyVaultTestCase
from blob_container_preparer import BlobContainerPreparer


@pytest.mark.usefixtures("managed_hsm")
class TestExamplesTests(KeyVaultTestCase):
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
    async def test_example_backup_and_restore(self, container_uri, sas_token):
        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)

        # [START begin_backup]
        # begin a vault backup
        backup_poller = await backup_client.begin_backup(container_uri, sas_token)

        # check if the backup completed
        done = backup_poller.done()

        # yield until the backup completes
        # result() returns an object with a URL of the backup
        backup_operation = await backup_poller.result()
        # [END begin_backup]

        folder_url = backup_operation.folder_url

        # [START begin_restore]
        # begin a full vault restore
        restore_poller = await backup_client.begin_restore(folder_url, sas_token)

        # check if the restore completed
        done = backup_poller.done()

        # wait for the restore to complete
        await restore_poller.wait()
        # [END begin_restore]

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @StorageAccountPreparer(random_name_enabled=True)
    @BlobContainerPreparer()
    async def test_example_selective_key_restore(self, container_uri, sas_token):
        # create a key to selectively restore
        key_client = KeyClient(self.managed_hsm["url"], self.credential)
        key_name = self.get_resource_name("selective-restore-test-key")
        await key_client.create_rsa_key(key_name)

        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)
        backup_poller = await backup_client.begin_backup(container_uri, sas_token)
        backup_operation = await backup_poller.result()
        folder_url = backup_operation.folder_url

        # [START begin_selective_restore]
        # begin a restore of a single key from a backed up vault
        restore_poller = await backup_client.begin_restore(folder_url, sas_token, key_name=key_name)

        # check if the restore completed
        done = backup_poller.done()

        # wait for the restore to complete
        await restore_poller.wait()
        # [END begin_selective_restore]
