# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration._internal import HttpChallengeCache
from azure.keyvault.administration import KeyVaultBackupClient
from azure.keyvault.keys import KeyClient
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
import pytest
from six.moves.urllib_parse import urlparse

from _shared.helpers import mock
from _shared.test_case import KeyVaultTestCase
from blob_container_preparer import BlobContainerPreparer


@pytest.mark.usefixtures("managed_hsm")
class TestExamplesTests(KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super(TestExamplesTests, self).__init__(*args, match_body=False, **kwargs)

    def setUp(self, *args, **kwargs):
        if self.is_live:
            real = urlparse(self.managed_hsm["url"])
            playback = urlparse(self.managed_hsm["playback_url"])
            self.scrubber.register_name_pair(real.netloc, playback.netloc)
        super(TestExamplesTests, self).setUp(*args, **kwargs)

    def tearDown(self):
        HttpChallengeCache.clear()
        assert len(HttpChallengeCache._cache) == 0
        super(KeyVaultTestCase, self).tearDown()

    @property
    def credential(self):
        if self.is_live:
            return DefaultAzureCredential()
        return mock.Mock(get_token=lambda *_, **__: AccessToken("secret", time.time() + 3600))

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @StorageAccountPreparer(random_name_enabled=True)
    @BlobContainerPreparer()
    def test_example_backup_and_restore(self, container_uri, sas_token):
        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)

        # [START begin_backup]
        # begin a vault backup
        backup_poller = backup_client.begin_backup(container_uri, sas_token)

        # check if the backup completed
        done = backup_poller.done()

        # block until the backup completes
        # result() returns an object with a URL of the backup
        backup_operation = backup_poller.result()
        # [END begin_backup]

        folder_url = backup_operation.folder_url

        # [START begin_restore]
        # begin a full vault restore
        restore_poller = backup_client.begin_restore(folder_url, sas_token)

        # check if the restore completed
        done = backup_poller.done()

        # wait for the restore to complete
        restore_poller.wait()
        # [END begin_restore]

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @StorageAccountPreparer(random_name_enabled=True)
    @BlobContainerPreparer()
    def test_example_selective_key_restore(self, container_uri, sas_token):
        # create a key to selectively restore
        key_client = KeyClient(self.managed_hsm["url"], self.credential)
        key_name = self.get_resource_name("selective-restore-test-key")
        key_client.create_rsa_key(key_name)

        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)
        backup_poller = backup_client.begin_backup(container_uri, sas_token)
        backup_operation = backup_poller.result()
        folder_url = backup_operation.folder_url

        # [START begin_selective_restore]
        # begin a restore of a single key from a backed up vault
        restore_poller = backup_client.begin_restore(folder_url, sas_token, key_name=key_name)

        # check if the restore completed
        done = backup_poller.done()

        # wait for the restore to complete
        restore_poller.wait()
        # [END begin_selective_restore]
