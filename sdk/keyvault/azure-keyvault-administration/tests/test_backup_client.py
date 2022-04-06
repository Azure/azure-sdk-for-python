# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from functools import partial
import time

from azure.core.exceptions import ResourceExistsError
from azure.keyvault.administration._internal import parse_folder_url
import pytest

from _shared.test_case import KeyVaultTestCase
from _test_case import AdministrationTestCase, backup_client_setup, get_decorator


all_api_versions = get_decorator()


class BackupClientTests(AdministrationTestCase, KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super(BackupClientTests, self).__init__(*args, match_body=False, **kwargs)

    @all_api_versions()
    @backup_client_setup
    def test_full_backup_and_restore(self, client):
        # backup the vault
        backup_poller = client.begin_backup(self.container_uri, self.sas_token)
        backup_operation = backup_poller.result()
        assert backup_operation.folder_url

        # restore the backup
        restore_poller = client.begin_restore(backup_operation.folder_url, self.sas_token)
        restore_poller.wait()
        if self.is_live:
            time.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @all_api_versions()
    @backup_client_setup
    def test_full_backup_and_restore_rehydration(self, client):
        if not self.is_live:
            pytest.skip("Poller requests are incompatible with vcrpy in playback")

        # backup the vault
        backup_poller = client.begin_backup(self.container_uri, self.sas_token)

        # create a new poller from a continuation token
        token = backup_poller.continuation_token()
        rehydrated = client.begin_backup(self.container_uri, self.sas_token, continuation_token=token)

        rehydrated_operation = rehydrated.result()
        assert rehydrated_operation.folder_url
        backup_operation = backup_poller.result()
        assert backup_operation.folder_url == rehydrated_operation.folder_url

        # restore the backup
        restore_poller = client.begin_restore(backup_operation.folder_url, self.sas_token)

        # create a new poller from a continuation token
        token = restore_poller.continuation_token()
        rehydrated = client.begin_restore(backup_operation.folder_url, self.sas_token, continuation_token=token)

        rehydrated.wait()
        restore_poller.wait()
        if self.is_live:
            time.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @all_api_versions()
    @backup_client_setup
    def test_selective_key_restore(self, client):
        # create a key to selectively restore
        key_client = self.create_key_client(self.managed_hsm_url)
        key_name = self.get_resource_name("selective-restore-test-key")
        key_client.create_rsa_key(key_name)

        # backup the vault
        backup_poller = client.begin_backup(self.container_uri, self.sas_token)
        backup_operation = backup_poller.result()

        # restore the key
        restore_poller = client.begin_restore(backup_operation.folder_url, self.sas_token, key_name=key_name)
        restore_poller.wait()

        # delete the key
        delete_function = partial(key_client.begin_delete_key, key_name)
        delete_poller = self._poll_until_no_exception(delete_function, ResourceExistsError)
        delete_poller.wait()
        key_client.purge_deleted_key(key_name)
        if self.is_live:
            time.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @all_api_versions()
    @backup_client_setup
    def test_backup_client_polling(self, client):
        if not self.is_live:
            pytest.skip("Poller requests are incompatible with vcrpy in playback")

        # backup the vault
        backup_poller = client.begin_backup(self.container_uri, self.sas_token)

        # create a new poller from a continuation token
        token = backup_poller.continuation_token()
        rehydrated = client.begin_backup(self.container_uri, self.sas_token, continuation_token=token)

        # check that pollers and polling methods behave as expected
        assert backup_poller.status() == "InProgress"
        assert not backup_poller.done() or backup_poller.polling_method().finished()
        assert rehydrated.status() == "InProgress"
        assert not rehydrated.done() or rehydrated.polling_method().finished()

        backup_operation = backup_poller.result()
        assert backup_poller.status() == "Succeeded" and backup_poller.polling_method().status() == "Succeeded"
        rehydrated_operation = rehydrated.result()
        assert rehydrated.status() == "Succeeded" and rehydrated.polling_method().status() == "Succeeded"
        assert backup_operation.folder_url == rehydrated_operation.folder_url

        # rehydrate a poller with a continuation token of a completed operation
        late_rehydrated = client.begin_backup(self.container_uri, self.sas_token, continuation_token=token)
        assert late_rehydrated.status() == "Succeeded"
        late_rehydrated.wait()

        # restore the backup
        restore_poller = client.begin_restore(backup_operation.folder_url, self.sas_token)

        # create a new poller from a continuation token
        token = restore_poller.continuation_token()
        rehydrated = client.begin_restore(backup_operation.folder_url, self.sas_token, continuation_token=token)

        # check that pollers and polling methods behave as expected
        assert restore_poller.status() == "InProgress"
        assert not restore_poller.done() or restore_poller.polling_method().finished()
        assert rehydrated.status() == "InProgress"
        assert not rehydrated.done() or rehydrated.polling_method().finished()

        rehydrated.wait()
        assert rehydrated.status() == "Succeeded" and rehydrated.polling_method().status() == "Succeeded"
        restore_poller.wait()
        assert restore_poller.status() == "Succeeded" and restore_poller.polling_method().status() == "Succeeded"

        if self.is_live:
            time.sleep(60)  # additional waiting to avoid conflicts with resources in other tests


@pytest.mark.parametrize(
    "url,expected_container_url,expected_folder_name",
    [
        (
            "https://account.blob.core.windows.net/backup/mhsm-account-2020090117323313",
            "https://account.blob.core.windows.net/backup",
            "mhsm-account-2020090117323313",
        ),
        ("https://account.storage/account/storage", "https://account.storage/account", "storage"),
        ("https://account.storage/a/b/c", "https://account.storage/a", "b/c"),
        ("https://account.storage/a/b-c", "https://account.storage/a", "b-c"),
    ],
)
def test_parse_folder_url(url, expected_container_url, expected_folder_name):
    container_url, folder_name = parse_folder_url(url)
    assert container_url == expected_container_url
    assert folder_name == expected_folder_name
