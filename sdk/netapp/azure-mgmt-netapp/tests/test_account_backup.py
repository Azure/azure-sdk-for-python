from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from azure.mgmt.netapp.models import Backup
from test_volume import delete_volume
from test_backup import create_backup, disable_backup
import setup
import azure.mgmt.netapp.models

class TestNetAppAccountBackup(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        print("Live status: {0}".format(self.is_live))
        if self.is_live:
            print("Live global status: {0}".format(setup.LIVE))
            setup.LIVE = True
            print("Live global status after set: {0}".format(setup.LIVE))

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_list_account_backups(self):
        print("Starting test_list_account_backups")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(setup.TEST_VOL_1+"-")
        backup1 = self.get_resource_name(setup.TEST_BACKUP_1+"-")
        backup2 = self.get_resource_name(setup.TEST_BACKUP_2+"-")

        try:
            create_backup(self.client, account_name=setup.PERMA_ACCOUNT, pool_name=setup.PERMA_POOL, volume_name=volumeName1, backup_name=backup1, backup_only=False)
            create_backup(self.client, account_name=setup.PERMA_ACCOUNT, pool_name=setup.PERMA_POOL, volume_name=volumeName1, backup_name=backup2, backup_only=True)

            account_backup_list = self.client.account_backups.list(setup.TEST_RG, account_name=setup.PERMA_ACCOUNT)
            backup_count = 0
            for backup in account_backup_list:
                if backup1 in backup.name or backup2 in backup.name:
                    backup_count += 1

            assert backup_count == 2
        finally:
            disable_backup(self.client, account_name=setup.PERMA_ACCOUNT, pool_name=setup.PERMA_POOL, volume_name=volumeName1, backup_name=backup1)
            disable_backup(self.client, account_name=setup.PERMA_ACCOUNT, pool_name=setup.PERMA_POOL, volume_name=volumeName1, backup_name=backup2)

            account_backup_list = self.client.account_backups.list(setup.TEST_RG, setup.PERMA_ACCOUNT)
            backup_count = 0
            for backup in account_backup_list:
                if backup1 in backup.name or backup2 in backup.name:
                    backup_count += 1

            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, pool_name=setup.PERMA_POOL, volume_name=volumeName1)
            assert backup_count == 0
        
        print("Finished with test_list_account_backups")

    @recorded_by_proxy
    def test_get_account_backups(self):
        print("Starting test_get_account_backups")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(setup.TEST_VOL_1+"-")
        backup1 = self.get_resource_name(setup.TEST_BACKUP_1+"-")
        try:
            create_backup(self.client, account_name=setup.PERMA_ACCOUNT, pool_name=setup.PERMA_POOL, volume_name=volumeName1, vnet=setup.PERMA_VNET, backup_name=backup1)

            account_backup = self.client.account_backups.get(setup.TEST_RG, setup.PERMA_ACCOUNT, backup1)
            assert account_backup.name == setup.PERMA_ACCOUNT + "/" + backup1
        finally:
            disable_backup(self.client, account_name=setup.PERMA_ACCOUNT, pool_name=setup.PERMA_POOL, volume_name=volumeName1, backup_name=backup1)
            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, pool_name=setup.PERMA_POOL, volume_name=volumeName1)
        
        print("Finished with test_get_account_backups")

    @recorded_by_proxy
    def test_delete_account_backups(self):
        print("Starting test_delete_account_backups")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(setup.TEST_VOL_1+"-")
        backup1 = self.get_resource_name(setup.TEST_BACKUP_1+"-")
        
        try:
            create_backup(self.client, account_name=setup.PERMA_ACCOUNT, pool_name=setup.PERMA_POOL, volume_name=volumeName1, vnet=setup.PERMA_VNET, backup_name=backup1)

            account_backup_list = self.client.account_backups.list(setup.TEST_RG, setup.PERMA_ACCOUNT)
            assert len(list(account_backup_list)) >= 1
        finally:
            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)
            self.client.account_backups.begin_delete(setup.TEST_RG, setup.PERMA_ACCOUNT, backup1).wait()

        account_backup_list = self.client.account_backups.list(setup.TEST_RG, setup.PERMA_ACCOUNT)
        for backup in account_backup_list:
            assert backup.name != setup.PERMA_ACCOUNT + "/" + backup1

        print("Finished with test_delete_account_backups")