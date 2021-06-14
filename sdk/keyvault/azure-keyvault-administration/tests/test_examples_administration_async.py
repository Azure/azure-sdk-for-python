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
        if not self.is_live:
            pytest.skip("Poller requests are incompatible with vcrpy in playback")

        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)

        # [START backup_vault]
        # begin a vault backup
        backup_poller = await backup_client.begin_backup(container_uri, sas_token)

        # to create a new poller for the operation, use a continuation token
        token = backup_poller.polling_method().get_continuation_token()
        new_poller = await backup_client.begin_backup(container_uri, sas_token, continuation_token=token)

        # get the final result
        backup_operation = await backup_poller.result()
        # [END backup_vault]

        await new_poller.wait()
        folder_url = backup_operation.folder_url

        # [START restore_vault]
        # begin a full vault restore; to restore a single key, use the key_name kwarg
        restore_poller = await backup_client.begin_restore(folder_url, sas_token)

        # to create a new poller for the operation, use a continuation token
        token = restore_poller.polling_method().get_continuation_token()
        new_poller = await backup_client.begin_restore(folder_url, sas_token, continuation_token=token)

        # wait for the restore to complete
        await restore_poller.wait()
        # [END restore_vault]

        await new_poller.wait()
