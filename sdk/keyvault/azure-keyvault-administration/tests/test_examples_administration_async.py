# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio

import pytest
from devtools_testutils import set_bodiless_matcher
from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import KeyVaultBackupClientPreparer, get_decorator
from _shared.test_case_async import KeyVaultTestCase

all_api_versions = get_decorator(is_async=True)


class TestExamplesTests(KeyVaultTestCase):
    def create_key_client(self, vault_uri, **kwargs):
        from azure.keyvault.keys.aio import KeyClient
        credential = self.get_credential(KeyClient, is_async=True)
        return self.create_client_from_credential(KeyClient, credential=credential, vault_url=vault_uri, **kwargs )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @KeyVaultBackupClientPreparer()
    @recorded_by_proxy_async
    async def test_example_backup_and_restore(self, client, **kwargs):
        set_bodiless_matcher()
        backup_client = client
        container_uri = kwargs.pop("container_uri")
        sas_token = kwargs.pop("sas_token")

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
        done = restore_poller.done()

        # wait for the restore to complete
        await restore_poller.wait()
        # [END begin_restore]

        if self.is_live:
            await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", all_api_versions)
    @KeyVaultBackupClientPreparer()
    @recorded_by_proxy_async
    async def test_example_selective_key_restore(self, client, **kwargs):
        # create a key to selectively restore
        set_bodiless_matcher()
        managed_hsm_url = kwargs.pop("managed_hsm_url")
        key_client = self.create_key_client(managed_hsm_url, is_async=True)
        key_name = self.get_resource_name("selective-restore-test-key")
        await key_client.create_rsa_key(key_name)

        backup_client = client
        sas_token = kwargs.pop("sas_token")
        container_uri = kwargs.pop("container_uri")
        backup_poller = await backup_client.begin_backup(container_uri, sas_token)
        backup_operation = await backup_poller.result()
        folder_url = backup_operation.folder_url

        # [START begin_selective_restore]
        # begin a restore of a single key from a backed up vault
        restore_poller = await backup_client.begin_restore(folder_url, sas_token, key_name=key_name)

        # check if the restore completed
        done = restore_poller.done()

        # wait for the restore to complete
        await restore_poller.wait()
        # [END begin_selective_restore]

        if self.is_live:
            await asyncio.sleep(60)  # additional waiting to avoid conflicts with resources in other tests
