# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time

import pytest
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher

from _shared.test_case import KeyVaultTestCase
from _test_case import KeyVaultBackupClientPreparer, get_decorator

all_api_versions = get_decorator()


class TestExamplesTests(KeyVaultTestCase):
    def create_key_client(self, vault_uri, **kwargs):
        from azure.keyvault.keys import KeyClient
        credential = self.get_credential(KeyClient)
        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs )

    @pytest.mark.parametrize("api_version", all_api_versions)
    @KeyVaultBackupClientPreparer()
    @recorded_by_proxy
    def test_example_backup_and_restore(self, client, **kwargs):
        set_bodiless_matcher()
        backup_client = client
        container_uri = kwargs.pop("container_uri")
        sas_token = kwargs.pop("sas_token")

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

    @pytest.mark.parametrize("api_version", all_api_versions)
    @KeyVaultBackupClientPreparer()
    @recorded_by_proxy
    def test_example_selective_key_restore(self, client, **kwargs):
        set_bodiless_matcher()
        # create a key to selectively restore
        managed_hsm_url = kwargs.pop("managed_hsm_url")
        key_client = self.create_key_client(managed_hsm_url)
        key_name = self.get_resource_name("selective-restore-test-key")
        key_client.create_rsa_key(key_name)

        backup_client = client
        sas_token = kwargs.pop("sas_token")
        container_uri = kwargs.pop("container_uri")
        backup_poller = backup_client.begin_backup(container_uri, sas_token)
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
