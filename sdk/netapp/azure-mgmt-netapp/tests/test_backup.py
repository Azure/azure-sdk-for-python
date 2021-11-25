import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.netapp.models import Backup, BackupPatch, VolumePatch
from test_account import delete_account
from test_volume import create_volume, wait_for_volume, delete_volume, delete_pool
from setup import *
import azure.mgmt.netapp.models
import unittest

backups = [TEST_BACKUP_1, TEST_BACKUP_2]


def create_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1,
                  volume_name=TEST_VOL_1, location=LOCATION, backup_only=False, live=False):
    if not backup_only:
        create_volume(client, rg, account_name, pool_name, volume_name, location, vnet=VNET, live=live)
        wait_for_volume(client, rg, account_name, pool_name, volume_name, live)

    vaults = client.vaults.list(rg, account_name)
    volume_patch = VolumePatch(data_protection={
        "backup": {
            "vaultId": vaults.next().id,
            "backupEnabled": True
        }
    })
    client.volumes.begin_update(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, volume_patch).result()
    backup_body = Backup(location=location)
    backup = client.backups.begin_create(rg, account_name, pool_name, volume_name, backup_name, backup_body).result()
    wait_for_backup_created(client, rg, account_name, pool_name, volume_name, backup_name, live)
    return backup


def disable_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1,
                   volume_name=TEST_VOL_1, live=False):
    vaults = client.vaults.list(rg, account_name)
    volume_patch = VolumePatch(data_protection={
        "backup": {
            "vaultId": vaults.next().id,
            "backupEnabled": False
        }
    })
    client.volumes.begin_update(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, volume_patch).wait()
    wait_for_no_backup(client, rg, account_name, pool_name, volume_name, backup_name, live)


def delete_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1,
                  volume_name=TEST_VOL_1, live=False):
    client.backups.begin_delete(rg, account_name, pool_name, volume_name, backup_name).wait()
    wait_for_no_backup(client, rg, account_name, pool_name, volume_name, backup_name, live)


def get_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1):
    return client.backups.get(rg, account_name, pool_name, volume_name, backup_name)


def get_backup_list(client, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1):
    return client.backups.list(rg, account_name, pool_name, volume_name)


def wait_for_no_backup(client, rg, account_name, pool_name, volume_name, backup_name, live=False):
    # a workaround for the async nature of certain ARM processes
    co = 0
    while co < 10:
        co += 1
        if live:
            time.sleep(2)
        try:
            client.backups.get(rg, account_name, pool_name, volume_name, backup_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break


def wait_for_backup_created(client, rg, account_name, pool_name, volume_name, backup_name, live=False):
    co = 0
    while co < 40:
        co += 1
        if live:
            time.sleep(10)
        backup = client.backups.get(rg, account_name, pool_name, volume_name, backup_name)
        if backup.provisioning_state == "Succeeded":
            break


def clean_up(client, disable_bp=True, live=False):
    if disable_bp:
        disable_backup(client, live=live)

    delete_volume(client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=live)
    delete_pool(client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=live)
    delete_account(client, TEST_RG, TEST_ACC_1, live=live)


class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    def test_create_delete_backup(self):
        # Create 2 backups since delete backups can only be used when volume has multiple backups
        create_backup(self.client, live=self.is_live)
        create_backup(self.client, backup_name=TEST_BACKUP_2, backup_only=True, live=self.is_live)
        backup_list = get_backup_list(self.client)
        self.assertEqual(len(list(backup_list)), 2)

        # delete the older backup since we are not able to delete the newest one with delete backup service
        delete_backup(self.client, live=self.is_live)
        backup_list = get_backup_list(self.client)
        self.assertEqual(len(list(backup_list)), 1)

        # automatically delete the second backup by disable backups on volume
        disable_backup(self.client, live=self.is_live)
        backup_list = get_backup_list(self.client)
        self.assertEqual(len(list(backup_list)), 0)

        clean_up(self.client, disable_bp=False, live=self.is_live)

    def test_list_backup(self):
        create_backup(self.client, live=self.is_live)
        create_backup(self.client, backup_name=TEST_BACKUP_2, backup_only=True, live=self.is_live)
        backup_list = get_backup_list(self.client)
        self.assertEqual(len(list(backup_list)), 2)
        idx = 0
        for backup in backup_list:
            self.assertEqual(backup.name, backups[idx])
            idx += 1

        disable_backup(self.client, live=self.is_live)
        disable_backup(self.client, backup_name=TEST_BACKUP_2, live=self.is_live)

        backup_list = get_backup_list(self.client)
        self.assertEqual(len(list(backup_list)), 0)

        clean_up(self.client, disable_bp=False, live=self.is_live)

    def test_get_backup_by_name(self):
        create_backup(self.client, live=self.is_live)

        backup = get_backup(self.client, TEST_BACKUP_1)
        self.assertEqual(backup.name, TEST_ACC_1 + "/" + TEST_POOL_1 + "/" + TEST_VOL_1 + "/" + TEST_BACKUP_1)

        clean_up(self.client, live=self.is_live)

    def test_update_backup(self):
        create_backup(self.client, live=self.is_live)
        backup_body = BackupPatch(location=LOCATION, label="label1")
        self.client.backups.begin_update(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, TEST_BACKUP_1, backup_body).wait()

        backup = get_backup(self.client)
        self.assertEqual(backup.label, "label1")

        clean_up(self.client, live=self.is_live)

    def test_get_backup_status(self):
        create_backup(self.client, live=self.is_live)

        if self.is_live:
            time.sleep(120)

        backup_status = self.client.backups.get_status(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        self.assertTrue(backup_status.healthy)
        self.assertEqual(backup_status.mirror_state, "Mirrored")

        clean_up(self.client, live=self.is_live)

