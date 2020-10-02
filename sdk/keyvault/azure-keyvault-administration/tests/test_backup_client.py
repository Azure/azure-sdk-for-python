# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
from functools import partial
import time

from azure.core.credentials import AccessToken
from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.administration import KeyVaultBackupClient, BackupOperation
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
import pytest

from _shared.helpers import mock
from _shared.test_case import KeyVaultTestCase
from blob_container_preparer import BlobContainerPreparer


@pytest.mark.usefixtures("managed_hsm")
class BackupClientTests(KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super(BackupClientTests, self).__init__(*args, match_body=False, **kwargs)

    def setUp(self, *args, **kwargs):
        if self.is_live:
            self.scrubber.register_name_pair(self.managed_hsm["url"].lower(), self.managed_hsm["playback_url"])
        super(BackupClientTests, self).setUp(*args, **kwargs)

    @property
    def credential(self):
        if self.is_live:
            return DefaultAzureCredential()
        return mock.Mock(get_token=lambda *_, **__: AccessToken("secret", time.time() + 3600))

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @StorageAccountPreparer(random_name_enabled=True)
    @BlobContainerPreparer()
    def test_full_backup_and_restore(self, container_uri, sas_token):
        # backup the vault
        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)
        backup_poller = backup_client.begin_full_backup(container_uri, sas_token)

        # check backup status and result
        job_id = backup_poller.polling_method().resource().id
        backup_status = backup_client.get_backup_status(job_id)
        assert_in_progress_operation(backup_status)
        backup_operation = backup_poller.result()
        assert_successful_operation(backup_operation)
        backup_status = backup_client.get_backup_status(job_id)
        assert_successful_operation(backup_status)

        # restore the backup
        folder_name = backup_operation.azure_storage_blob_container_uri.split("/")[-1]
        restore_poller = backup_client.begin_full_restore(container_uri, sas_token, folder_name)

        # check restore status and result
        job_id = restore_poller.polling_method().resource().id
        restore_status = backup_client.get_restore_status(job_id)
        assert_in_progress_operation(restore_status)
        restore_operation = restore_poller.result()
        assert_successful_operation(restore_operation)
        restore_status = backup_client.get_restore_status(job_id)
        assert_successful_operation(restore_status)

    @ResourceGroupPreparer(random_name_enabled=True, use_cache=True)
    @StorageAccountPreparer(random_name_enabled=True)
    @BlobContainerPreparer()
    def test_selective_key_restore(self, container_uri, sas_token):
        # create a key to selectively restore
        key_client = KeyClient(self.managed_hsm["url"], self.credential)
        key_name = self.get_resource_name("selective-restore-test-key")
        key_client.create_rsa_key(key_name)

        # backup the vault
        backup_client = KeyVaultBackupClient(self.managed_hsm["url"], self.credential)
        backup_poller = backup_client.begin_full_backup(container_uri, sas_token)

        # check backup status and result
        job_id = backup_poller.polling_method().resource().id
        backup_status = backup_client.get_backup_status(job_id)
        assert_in_progress_operation(backup_status)
        backup_operation = backup_poller.result()
        assert_successful_operation(backup_operation)
        backup_status = backup_client.get_backup_status(job_id)
        assert_successful_operation(backup_status)

        # restore the key
        folder_name = backup_operation.azure_storage_blob_container_uri.split("/")[-1]
        restore_poller = backup_client.begin_selective_restore(container_uri, sas_token, folder_name, key_name)

        # check restore status and result
        job_id = restore_poller.polling_method().resource().id
        restore_status = backup_client.get_restore_status(job_id)
        assert_in_progress_operation(restore_status)
        restore_operation = restore_poller.result()
        assert_successful_operation(restore_operation)
        restore_status = backup_client.get_restore_status(job_id)
        assert_successful_operation(restore_status)

        # delete the key
        delete_function = partial(key_client.begin_delete_key, key_name)
        delete_poller = self._poll_until_no_exception(delete_function, ResourceExistsError)
        delete_poller.wait()
        key_client.purge_deleted_key(key_name)


def test_continuation_token():
    """Methods returning pollers should accept continuation tokens"""

    expected_token = "token"
    mock_generated_client = mock.Mock()

    backup_client = KeyVaultBackupClient("vault-url", object())
    backup_client._client = mock_generated_client
    backup_client.begin_full_restore("storage uri", "sas", "folder", continuation_token=expected_token)
    backup_client.begin_full_backup("storage uri", "sas", continuation_token=expected_token)
    backup_client.begin_selective_restore("storage uri", "sas", "folder", "key", continuation_token=expected_token)

    for method in ("begin_full_backup", "begin_full_restore_operation", "begin_selective_key_restore_operation"):
        mock_method = getattr(mock_generated_client, method)
        assert mock_method.call_count == 1
        _, kwargs = mock_method.call_args
        assert kwargs["continuation_token"] == expected_token


def assert_in_progress_operation(operation):
    if isinstance(operation, BackupOperation):
        assert operation.azure_storage_blob_container_uri is None
    assert operation.status == "InProgress"
    assert operation.end_time is None
    assert isinstance(operation.start_time, datetime)


def assert_successful_operation(operation):
    if isinstance(operation, BackupOperation):
        assert operation.azure_storage_blob_container_uri
    assert operation.status == "Succeeded"
    assert isinstance(operation.end_time, datetime)
    assert operation.start_time < operation.end_time
