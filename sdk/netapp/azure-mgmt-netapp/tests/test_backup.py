import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.netapp.models import Backup, VolumePatch
from test_account import delete_account
from test_volume import create_volume, wait_for_volume, delete_volume, delete_pool
from setup import *
import azure.mgmt.netapp.models
import unittest

TEST_BACKUP_1 = 'sdk-py-tests-backup-1'
TEST_BACKUP_2 = 'sdk-py-tests-backup-2'
backups = [TEST_BACKUP_1, TEST_BACKUP_2]


def create_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1,
                  volume_name=TEST_VOL_1, location=LOCATION, backup_only=False):
    if not backup_only:
        create_volume(client, rg, account_name, pool_name, volume_name, location)
        wait_for_volume(client, rg, account_name, pool_name, volume_name)

    vaults = client.vaults.list(rg, account_name, None, True)
    volume_patch = VolumePatch(data_protection={
        "backup": {
            "vaultId": vaults.next().id,
            "backupEnabled": True
        }
    })
    client.volumes.update(volume_patch, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1).result()
    backup = client.backups.create(rg, account_name, pool_name, volume_name, backup_name, location).result()
    return backup


def delete_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1,
                  volume_name=TEST_VOL_1, live=False):
    vaults = client.vaults.list(rg, account_name, None, True)
    volume_patch = VolumePatch(data_protection={
        "backup": {
            "vaultId": vaults.next().id,
            "backupEnabled": False
        }
    })
    client.volumes.update(volume_patch, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1).wait()
    client.backups.delete(rg, account_name, pool_name, volume_name, backup_name).wait()
    wait_for_no_backup(client, rg, account_name, pool_name, volume_name, backup_name, live)


def get_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1):
    backup = client.backups.get(rg, account_name, pool_name, volume_name, backup_name)
    return backup


def get_backup_list(client, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1):
    backup_list = client.backups.list(rg, account_name, pool_name, volume_name)
    return backup_list


def wait_for_no_backup(client, rg, account_name, pool_name, volume_name, backup_name, live=False):
    # a workaround for the async nature of certain ARM processes
    co = 0
    while co < 5:
        co += 1
        if live:
            time.sleep(2)
        try:
            client.backups.get(rg, account_name, pool_name, volume_name, backup_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break


class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.AzureNetAppFilesManagementClient)

    @unittest.skip("Backup deletion not ready and therefore skipping this test for now")
    def test_create_delete_backup(self):
        raise unittest.SkipTest("Skipping Backup tests because deletion is not ready yet")

        create_backup(self.client)

        backup_list = get_backup_list(self.client)
        self.assertEqual(len(list(backup_list)), 1)

        delete_backup(self.client, live=self.is_live)

        backup_list = get_backup_list(self.client)
        self.assertEqual(len(list(backup_list)), 0)

        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    @unittest.skip("Backup deletion not ready and therefore skipping this test for now")
    def test_list_backup(self):
        raise unittest.SkipTest("Skipping Backup tests because deletion is not ready yet")

        create_backup(self.client)
        create_backup(self.client, backup_name=TEST_BACKUP_2, backup_only=True)

        backup_list = get_backup_list(self.client)
        self.assertEqual(len(list(backup_list)), 2)
        idx = 0
        for backup in backup_list:
            self.assertEqual(backup.name, backups[idx])
            idx += 1

        delete_backup(self.client, live=self.is_live)
        delete_backup(self.client, backup_name=TEST_BACKUP_2, live=self.is_live)

        backup_list = get_backup_list(self.client)
        self.assertEqual(len(list(backup_list)), 0)

        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, TEST_ACC_1)

    @unittest.skip("Backup deletion not ready and therefore skipping this test for now")
    def test_get_backup_by_name(self):
        raise unittest.SkipTest("Skipping Backup tests because deletion is not ready yet")

        create_backup(self.client)

        backup = get_backup(self.client, TEST_BACKUP_1)
        self.assertEqual(backup.name, TEST_BACKUP_1)

        delete_backup(self.client, TEST_BACKUP_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1)

    @unittest.skip("Backup deletion not ready and therefore skipping this test for now")
    def test_update_backup(self):
        raise unittest.SkipTest("Skipping Backup tests because deletion is not ready yet")

        create_backup(self.client)

        self.client.backup.update(TEST_RG, TEST_ACC_1, TEST_BACKUP_1)

        backup = get_backup(self.client)
        self.assertEqual(backup.daily_backups_to_keep, 0)
        self.assertEqual(backup.weekly_backups_to_keep, 1)

        delete_backup(self.client, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1)
