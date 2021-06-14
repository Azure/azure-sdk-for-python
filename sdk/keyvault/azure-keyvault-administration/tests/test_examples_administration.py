# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration._internal import HttpChallengeCache
from azure.keyvault.administration import KeyVaultBackupClient
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
        if not self.is_live:
            pytest.skip("Poller requests are incompatible with vcrpy in playback")

        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)

        # [START backup_vault]
        # begin a vault backup
        backup_poller = backup_client.begin_backup(container_uri, sas_token)

        # to create a new poller for the operation, use a continuation token
        token = backup_poller.polling_method().get_continuation_token()
        new_poller = backup_client.begin_backup(container_uri, sas_token, continuation_token=token)

        # get the final result
        backup_operation = backup_poller.result()
        # [END backup_vault]

        new_poller.wait()
        folder_url = backup_operation.folder_url

        # [START restore_vault]
        # begin a full vault restore; to restore a single key, use the key_name kwarg
        restore_poller = backup_client.begin_restore(folder_url, sas_token)

        # to create a new poller for the operation, use a continuation token
        token = restore_poller.polling_method().get_continuation_token()
        new_poller = backup_client.begin_restore(folder_url, sas_token, continuation_token=token)

        # wait for the restore to complete
        restore_poller.wait()
        # [END restore_vault]

        new_poller.wait()
