import time
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from azure.mgmt.netapp.models import Backup, BackupPatch, VolumePatch
from test_account import delete_account
from test_volume import create_volume, wait_for_volume, delete_volume, delete_pool, create_virtual_network
from setup import *
import azure.mgmt.netapp.models

backups = [TEST_BACKUP_1, TEST_BACKUP_2]


def create_backup(client, backup_name=TEST_BACKUP_1, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1,
                  volume_name=TEST_VOL_1, location=LOCATION, backup_only=False, vnet=VNET, live=False):
    if not backup_only:
        create_volume(client, rg, account_name, pool_name, volume_name, location, vnet=vnet, live=live)
        wait_for_volume(client, rg, account_name, pool_name, volume_name, live)

    vaults = client.vaults.list(rg, account_name)
    volume_patch = VolumePatch(data_protection={
        "backup": {
            "vaultId": vaults.next().id,
            "backupEnabled": True
        }
    })
    client.volumes.begin_update(TEST_RG, account_name, TEST_POOL_1, volume_name, volume_patch).result()
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
    client.volumes.begin_update(TEST_RG, account_name, TEST_POOL_1, volume_name, volume_patch).wait()
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


def clean_up(client, network_client, disable_bp=True, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1, vnet=VNET, backup_name=TEST_BACKUP_1, live=False):
    if disable_bp:
        disable_backup(client, account_name=account_name, pool_name=pool_name, volume_name=volume_name, live=live)

    delete_volume(client, TEST_RG, account_name=account_name, pool_name=pool_name, volume_name=volume_name, live=live)
    delete_pool(client, TEST_RG, acc_name=account_name, pool_name=pool_name, live=live)
    #client.account_backups.begin_delete(TEST_RG, account_name, backup_name).wait()
    delete_account(client, TEST_RG, acc_name=account_name, live=live)
    network_client.virtual_networks.begin_delete(TEST_RG, vnet)


class TestNetAppBackup(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        self.network_client = self.create_mgmt_client(NetworkManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_backup(self):
        set_bodiless_matcher()        
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')                        

        # Create 2 backups since delete backups can only be used when volume has multiple backups
        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, vnet=VNETNAME, live=self.is_live)
        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, backup_name=TEST_BACKUP_2, backup_only=True, live=self.is_live)
        backup_list = get_backup_list(self.client, account_name=ACCOUNT1, volume_name=volumeName1)
        assert len(list(backup_list)) == 2

        # delete the older backup since we are not able to delete the newest one with delete backup service
        delete_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, live=self.is_live)
        backup_list = get_backup_list(self.client, account_name=ACCOUNT1, volume_name=volumeName1)
        assert len(list(backup_list)) == 1

        # automatically delete the second backup by disable backups on volume
        disable_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, live=self.is_live)
        backup_list = get_backup_list(self.client, account_name=ACCOUNT1, volume_name=volumeName1)
        assert len(list(backup_list)) == 0

        clean_up(self.client,self.network_client, disable_bp=False, account_name=ACCOUNT1, volume_name=volumeName1, vnet=VNETNAME, backup_name=TEST_BACKUP_1, live=self.is_live)

    @recorded_by_proxy
    def test_list_backup(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')
        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, vnet=VNETNAME,live=self.is_live)
        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, vnet=VNETNAME, backup_name=TEST_BACKUP_2, backup_only=True, live=self.is_live)
        backup_list = get_backup_list(self.client, account_name=ACCOUNT1, volume_name=volumeName1)
        assert len(list(backup_list)) == 2
        idx = 0
        for backup in backup_list:
            assert backup.name == backups[idx]
            idx += 1

        disable_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, live=self.is_live)
        disable_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, backup_name=TEST_BACKUP_2, live=self.is_live)

        backup_list = get_backup_list(self.client, account_name=ACCOUNT1, volume_name=volumeName1)
        assert len(list(backup_list)) == 0

        clean_up(self.client, self.network_client, account_name=ACCOUNT1, volume_name=volumeName1, vnet=VNETNAME, disable_bp=False, live=self.is_live)

    @recorded_by_proxy
    def test_get_backup_by_name(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')        
        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, vnet=VNETNAME, live=self.is_live)

        backup = get_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, backup_name=TEST_BACKUP_1)
        assert backup.name == ACCOUNT1 + "/" + TEST_POOL_1 + "/" + volumeName1 + "/" + TEST_BACKUP_1

        clean_up(self.client, self.network_client, account_name=ACCOUNT1, volume_name=volumeName1, vnet=VNETNAME, live=self.is_live)

    @recorded_by_proxy
    def test_update_backup(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        backup1 = self.get_resource_name(TEST_BACKUP_1+"-")
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')         
        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, backup_name=backup1, vnet=VNETNAME, live=self.is_live)
        backup_body = BackupPatch(account_name=ACCOUNT1, volume_name=volumeName1, backup_name=backup1, location=LOCATION, label="label1")
        self.client.backups.begin_update(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, backup1, backup_body).wait()

        backup = get_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, backup_name=backup1)
        assert backup.label == "label1"

        clean_up(self.client, self.network_client, account_name=ACCOUNT1, volume_name=volumeName1, backup_name=backup1, vnet=VNETNAME, live=self.is_live)

    @recorded_by_proxy
    def test_get_backup_status(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        backup1 = self.get_resource_name(TEST_BACKUP_1+"-")
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')         
        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, backup_name=backup1, vnet=VNETNAME, live=self.is_live)

        if self.is_live:
            time.sleep(120)

        backup_status = self.client.backups.get_status(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        assert backup_status.healthy
        assert backup_status.mirror_state == "Mirrored"

        clean_up(self.client, self.network_client, account_name=ACCOUNT1, volume_name=volumeName1, backup_name=backup1, vnet=VNETNAME, live=self.is_live)
