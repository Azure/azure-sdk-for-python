from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from azure.mgmt.netapp.models import Backup
from test_account import delete_account
from test_volume import delete_volume, delete_pool, create_virtual_network
from test_backup import create_backup, disable_backup
from setup import *
import azure.mgmt.netapp.models


class TestNetAppAccountBackup(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        self.network_client = self.create_mgmt_client(NetworkManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_list_account_backups(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        backup1 = self.get_resource_name(TEST_BACKUP_1+"-")
        backup2 = self.get_resource_name(TEST_BACKUP_2+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')         

        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, vnet=VNETNAME, backup_name=backup1, live=self.is_live)
        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, backup_name=backup2, backup_only=True, live=self.is_live)

        account_backup_list = self.client.account_backups.list(TEST_RG, account_name=ACCOUNT1)
        backup_count = 0
        for backup in account_backup_list:
            if backup1 in backup.name or backup2 in backup.name:
                backup_count += 1

        assert backup_count == 2

        disable_backup(self.client,account_name=ACCOUNT1, volume_name=volumeName1, live=self.is_live)
        disable_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, backup_name=backup2, live=self.is_live)

        account_backup_list = self.client.account_backups.list(TEST_RG, ACCOUNT1)
        backup_count = 0
        for backup in account_backup_list:
            if backup1 in backup.name or backup2 in backup.name:
                backup_count += 1

        assert backup_count == 0
        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, live=self.is_live)                
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, ACCOUNT1, live=self.is_live)

    @recorded_by_proxy
    def test_get_account_backups(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        backup1 = self.get_resource_name(TEST_BACKUP_1+"-")   
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')    
        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, vnet=VNETNAME, backup_name=backup1, live=self.is_live)

        account_backup = self.client.account_backups.get(TEST_RG, ACCOUNT1, backup1)
        assert account_backup.name == ACCOUNT1 + "/" + backup1

        disable_backup(self.client, backup1, live=self.is_live)
        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, live=self.is_live)
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, ACCOUNT1, live=self.is_live)

    @recorded_by_proxy
    def test_delete_account_backups(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        backup1 = self.get_resource_name(TEST_BACKUP_1+"-")   
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')    
        create_backup(self.client, account_name=ACCOUNT1, volume_name=volumeName1, vnet=VNETNAME, backup_name=backup1, live=self.is_live)

        account_backup_list = self.client.account_backups.list(TEST_RG, ACCOUNT1)
        assert len(list(account_backup_list)) >= 1

        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, live=self.is_live)
        self.client.account_backups.begin_delete(TEST_RG, ACCOUNT1, backup1).wait()

        account_backup_list = self.client.account_backups.list(TEST_RG, ACCOUNT1)
        for backup in account_backup_list:
            assert backup.name != ACCOUNT1 + "/" + backup1

        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, ACCOUNT1, live=self.is_live)
