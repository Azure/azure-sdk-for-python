# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time

import pytest

from _shared.test_case import KeyVaultTestCase
from _test_case import AdministrationTestCase, backup_client_setup, get_decorator


all_api_versions = get_decorator()


class TestExamplesTests(AdministrationTestCase, KeyVaultTestCase):
    def __init__(self, *args, **kwargs):
        super(TestExamplesTests, self).__init__(*args, match_body=False, **kwargs)

    @all_api_versions()
    @backup_client_setup
    def test_example_backup_and_restore(self, client):
        backup_client = client
        container_uri = self.container_uri
        sas_token = self.sas_token

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
        done = restore_poller.done()

        # wait for the restore to complete
        restore_poller.wait()
        # [END begin_restore]

        if self.is_live:
            time.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @all_api_versions()
    @backup_client_setup
    def test_example_selective_key_restore(self, client):
        # create a key to selectively restore
        key_client = self.create_key_client(self.managed_hsm_url)
        key_name = self.get_resource_name("selective-restore-test-key")
        key_client.create_rsa_key(key_name)

        backup_client = client
        sas_token = self.sas_token
        backup_poller = backup_client.begin_backup(self.container_uri, sas_token)
        backup_operation = backup_poller.result()
        folder_url = backup_operation.folder_url

        # [START begin_selective_restore]
        # begin a restore of a single key from a backed up vault
        restore_poller = backup_client.begin_restore(folder_url, sas_token, key_name=key_name)

        # check if the restore completed
        done = restore_poller.done()

        # wait for the restore to complete
        restore_poller.wait()
        # [END begin_selective_restore]

        if self.is_live:
            time.sleep(60)  # additional waiting to avoid conflicts with resources in other tests
