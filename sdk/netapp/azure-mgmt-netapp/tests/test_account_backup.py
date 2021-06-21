import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.netapp.models import Backup, VolumePatch
from test_account import delete_account
from test_volume import create_volume, wait_for_volume, delete_volume, delete_pool
from test_backup import create_backup, disable_backup
from setup import *
import azure.mgmt.netapp.models
import unittest


class NetAppAccountBackupTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountBackupTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    def test_list_account_backups(self):
        create_backup(self.client, backup_name=TEST_BACKUP_1, live=self.is_live)
        create_backup(self.client, backup_name=TEST_BACKUP_2, backup_only=True, live=self.is_live)

        account_backup_list = self.client.account_backups.list(TEST_RG, TEST_ACC_1)
        backup_count = 0
        for backup in account_backup_list:
            if TEST_BACKUP_1 in backup.name or TEST_BACKUP_2 in backup.name:
                backup_count += 1

        self.assertEqual(backup_count, 2)

        disable_backup(self.client, live=self.is_live)
        disable_backup(self.client, backup_name=TEST_BACKUP_2, live=self.is_live)

        account_backup_list = self.client.account_backups.list(TEST_RG, TEST_ACC_1)
        backup_count = 0
        for backup in account_backup_list:
            if TEST_BACKUP_1 in backup.name or TEST_BACKUP_2 in backup.name:
                backup_count += 1

        self.assertEqual(backup_count, 0)

        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)


    def test_get_account_backups(self):
        create_backup(self.client, backup_name=TEST_BACKUP_1, live=self.is_live)

        account_backup = self.client.account_backups.get(TEST_RG, TEST_ACC_1, TEST_BACKUP_1)
        self.assertEqual(account_backup.name, TEST_ACC_1 + "/" + TEST_BACKUP_1)

        disable_backup(self.client, TEST_BACKUP_1, live=self.is_live)
        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)


    def test_delete_account_backups(self):
        create_backup(self.client, backup_name=TEST_BACKUP_1, live=self.is_live)

        account_backup_list = self.client.account_backups.list(TEST_RG, TEST_ACC_1)
        self.assertGreaterEqual(len(list(account_backup_list)), 1)

        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        self.client.account_backups.begin_delete(TEST_RG, TEST_ACC_1, TEST_BACKUP_1).wait()

        account_backup_list = self.client.account_backups.list(TEST_RG, TEST_ACC_1)
        for backup in account_backup_list:
            self.assertNotEqual(backup.name, TEST_ACC_1 + "/" + TEST_BACKUP_1)

        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)
