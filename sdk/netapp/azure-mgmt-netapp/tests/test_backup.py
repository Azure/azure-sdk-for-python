import random
import string
import time
import pytest
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from azure.mgmt.netapp.models import Backup, BackupPatch, VolumePatch
from test_volume import create_volume, wait_for_volume, delete_volume
from setup import *
import azure.mgmt.netapp.models

backups = [TEST_BACKUP_1, TEST_BACKUP_2]
LIVE = False

def create_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1,
                  volume_name=TEST_VOL_1, location=LOCATION, backup_only=False, vnet=PERMA_VNET):
    if not backup_only:
        create_volume(client, rg, account_name, pool_name, volume_name, location, vnet=vnet, volume_only=True)

    update_volume_enable_backup(client, rg, account_name, pool_name, volume_name)
    backup = create_backup_entity(client, rg, account_name, pool_name, volume_name, backup_name)
    print("\tdone")
    return backup

def create_backup_entity(client, rg, account_name, pool_name, volume_name, backup_name):
    print("Create backup entity {0}".format(backup_name))
    retry = 0
    backup_body = Backup(location=LOCATION)
    
    while retry < 3:
        try:
            client.backups.begin_create(rg, account_name, pool_name, volume_name, backup_name, backup_body).result()
            break
        except Exception as e: 
            print("failed to create backup entity. Retry number: {0}".format(retry))
            print(e)
            retry += 1
            if LIVE:
                time.sleep(10)
    wait_for_backup_created(client, rg, account_name, pool_name, volume_name, backup_name)
    print("\tdone")

def update_volume_enable_backup(client, rg, account_name, pool_name, volume_name):
    print("Update volume {0}".format(volume_name))
    retry = 0
    volume_patch = VolumePatch(data_protection={
        "backup": {
            "backupEnabled": True
        }
    })
    
    while retry < 3:
        try:
            client.volumes.begin_update(rg, account_name, pool_name, volume_name, volume_patch).result()
            break
        except Exception as e: 
            print("failed to update volume. Retry number: {0}".format(retry))
            print(e)
            retry += 1
            if LIVE:
                time.sleep(10)
    wait_for_volume(client, rg, account_name, pool_name, volume_name)
    print("\tdone")


def disable_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1,
                   volume_name=TEST_VOL_1):
    print("Disabling backup {0} of volume '{1}'".format(backup_name, volume_name))
    volume_patch = VolumePatch(data_protection={
        "backup": {
            "backupEnabled": False
        }
    })
    retry = 0
    while retry < 3:
        try:
            client.volumes.begin_update(rg, account_name, pool_name, volume_name, volume_patch).wait()
            break
        except Exception as e: 
            print("failed to disable backup. Retry number: {0}".format(retry))
            print(e)
            retry += 1
            if LIVE:
                time.sleep(20)
    wait_for_volume(client, rg, account_name, pool_name, volume_name)
    print("\tdone")

def delete_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1,
                  volume_name=TEST_VOL_1):
    print("Deleting backup {0}".format(backup_name))
    retry = 0
    while retry < 3:
        try:
            client.backups.begin_delete(rg, account_name, pool_name, volume_name, backup_name).wait()
            break
        except Exception as e: 
            print("failed to delete backup. Retry number: {0}".format(retry))
            print(e)
            retry += 1
            if LIVE:
                time.sleep(20)
    print("\tdone")

def get_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1):
    print("Geting backup {0}".format(backup_name))
    backup = client.backups.get(rg, account_name, pool_name, volume_name, backup_name)
    print("\tdone")
    return backup

def get_backup_list(client, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1):
    print("Geting backup list for volume {0}".format(volume_name))
    backuplist = client.backups.list(rg, account_name, pool_name, volume_name)
    print("\tdone")
    return backuplist

def wait_for_no_backup(client, rg, account_name, pool_name, volume_name, backup_name):
    # a workaround for the async nature of certain ARM processes
    co = 0
    while co < 60:
        try:
            client.backups.get(rg, account_name, pool_name, volume_name, backup_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break
        if LIVE:
            time.sleep(5)
        co += 1
    print("Retried {0} times".format(co))

def wait_for_backup_created(client, rg, account_name, pool_name, volume_name, backup_name):
    co = 0
    while co < 60:
        backup = client.backups.get(rg, account_name, pool_name, volume_name, backup_name)
        if backup.provisioning_state == "Succeeded":
            break
        if backup.provisioning_state == "Failed":
            print("Wait for backup. Backup is in a failed state.")
            break
        if LIVE:
            time.sleep(10)
        co += 1
    print("Retried {0} times".format(co))
    return backup

def clean_up(self, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, disable_bp=True, volume_name=TEST_VOL_1, backup_name=TEST_BACKUP_1):
    if disable_bp:
        disable_backup(self.client, account_name=account_name, pool_name=pool_name, volume_name=volume_name, backup_name=backup_name)

    delete_volume(self.client, TEST_RG, account_name=account_name, pool_name=pool_name, volume_name=volume_name)

class TestNetAppBackup(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            global LIVE
            LIVE = True
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(NetworkManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_backup(self):
        print("Starting test_create_delete_backup")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        backup1 = self.get_resource_name(TEST_BACKUP_1+"-")
        backup2 = self.get_resource_name(TEST_BACKUP_2+"-")                 

        try:
            # Create 2 backups since delete backups can only be used when volume has multiple backups
            create_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup1, backup_only=False, vnet=PERMA_VNET)
            create_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup2, backup_only=True)
            backup_list = get_backup_list(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1)
            assert len(list(backup_list)) == 2
        finally:
            # delete the older backup since we are not able to delete the newest one with delete backup service
            delete_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup1)
            backup_list2 = get_backup_list(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1)
            assert len(list(backup_list2)) == 1

            # automatically delete the second backup by disable backups on volume
            disable_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup2)
            backup_list3 = get_backup_list(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1)
            assert len(list(backup_list3)) == 0

            clean_up(self, PERMA_ACCOUNT, PERMA_POOL, disable_bp=False, volume_name=volumeName1)
        print("Finished with test_create_delete_backup")

    @recorded_by_proxy
    def test_list_backup(self):
        print("Starting test_list_backup")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        backup1 = self.get_resource_name(TEST_BACKUP_1+"-")
        backup2 = self.get_resource_name(TEST_BACKUP_2+"-")  
        try:
            create_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup1, vnet=PERMA_VNET)
            create_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, vnet=PERMA_VNET, backup_name=backup2, backup_only=True)
            backup_list = get_backup_list(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1)
            assert len(list(backup_list)) == 2
            idx = 0
            for backup in backup_list:
                assert backup.name == backups[idx]
                idx += 1
        finally:
            disable_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup1)
            disable_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup2)

            backup_list = get_backup_list(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1)
            assert len(list(backup_list)) == 0
            clean_up(self, PERMA_ACCOUNT, PERMA_POOL, volume_name=volumeName1, disable_bp=False)
        print("Finished with test_list_backup")

    @recorded_by_proxy
    def test_get_backup_by_name(self):
        print("Starting test_get_backup_by_name")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        backup1 = self.get_resource_name(TEST_BACKUP_1+"-")
        try:
            create_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup1, vnet=PERMA_VNET)

            backup = get_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup1)
            assert backup.name == PERMA_ACCOUNT + "/" + PERMA_POOL + "/" + volumeName1 + "/" + backup1
        finally:
            clean_up(self, PERMA_ACCOUNT, PERMA_POOL, volume_name=volumeName1, backup_name=backup1)
        print("Finished with test_get_backup_by_name")

    #@pytest.mark.skip(reason="CBS is not working properly on any region")
    @recorded_by_proxy
    def test_update_backup(self):
        print("Starting test_update_backup")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        backup1 = self.get_resource_name(TEST_BACKUP_1+"-")
        try:      
            create_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup1, vnet=PERMA_VNET)
            backup_body = BackupPatch(account_name=PERMA_ACCOUNT, volume_name=volumeName1, backup_name=backup1, location=LOCATION, label="label1")
            self.client.backups.begin_update(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, backup1, backup_body).wait()

            backup = get_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup1)
            assert backup.label == "label1"
        finally:
            clean_up(self, PERMA_ACCOUNT, PERMA_POOL, volume_name=volumeName1, backup_name=backup1)
        print("Finished with test_update_backup")

    #@pytest.mark.skip(reason="CBS is not working properly on any region")
    @recorded_by_proxy
    def test_get_backup_status(self):
        print("Starting test_get_backup_status")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        backup1 = self.get_resource_name(TEST_BACKUP_1+"-")
        try:
            create_backup(self.client, account_name=PERMA_ACCOUNT, pool_name=PERMA_POOL, volume_name=volumeName1, backup_name=backup1, vnet=PERMA_VNET)

            backup_status = self.client.backups.get_status(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
            assert backup_status.healthy
            assert backup_status.mirror_state == "Mirrored"
        finally:
            clean_up(self, PERMA_ACCOUNT, PERMA_POOL, volume_name=volumeName1, backup_name=backup1)
        print("Finished with test_get_backup_status")
