import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.netapp.models import BackupPolicy
from test_account import create_account, delete_account
from setup import *
import azure.mgmt.netapp.models

TEST_BACKUP_POLICY_1='sdk-py-tests-backup-policy-1'
TEST_BACKUP_POLICY_2='sdk-py-tests-backup-policy-2'
BACKUP_POLICIES = [TEST_BACKUP_POLICY_1, TEST_BACKUP_POLICY_2]
BP_LOCATION = 'eastus2euap'
BP_RESOURCE_GROUP = 'bp_rg_python_sdk_test'
BP_ACCOUNT = 'sdk-py-tests-bp-acc'


def create_backup_policy(client, backup_policy_name, rg=BP_RESOURCE_GROUP, account_name=BP_ACCOUNT, location=BP_LOCATION, backup_policy_only=False):
    if not backup_policy_only:
        create_account(client, rg, account_name, location)

    backup_policy_body = BackupPolicy(
        location=location,
        daily_backups_to_keep=1,
        weekly_backups_to_keep=0,
        monthly_backups_to_keep=0,
        enabled=False
    )

    backup_policy = client.backup_policies.create(rg, account_name, backup_policy_name, backup_policy_body).result()
    return backup_policy


def delete_backup_policy(client, backup_policy_name, rg=BP_RESOURCE_GROUP, account_name=BP_ACCOUNT, live=False):
    client.backup_policies.delete(rg, account_name, backup_policy_name).wait()
    wait_for_no_backup_policy(client, rg, account_name, backup_policy_name, live)


def wait_for_no_backup_policy(client, rg, account_name, backup_policy_name, live=False):
    # a workaround for the async nature of certain ARM processes
    co = 0
    while co < 5:
        co += 1
        if live:
            time.sleep(2)
        try:
            client.backup_policies.get(rg, account_name, backup_policy_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break


class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.AzureNetAppFilesManagementClient)

    def test_create_delete_backup_policy(self):
        create_backup_policy(self.client, TEST_BACKUP_POLICY_1)

        backup_policies_list = self.client.backup_policies.list(BP_RESOURCE_GROUP, BP_ACCOUNT)
        self.assertEqual(len(list(backup_policies_list)), 1)

        delete_backup_policy(self.client, TEST_BACKUP_POLICY_1, live=self.is_live)

        backup_policies_list = self.client.backup_policies.list(BP_RESOURCE_GROUP, BP_ACCOUNT)
        self.assertEqual(len(list(backup_policies_list)), 0)

        delete_account(self.client, BP_RESOURCE_GROUP, BP_ACCOUNT, live=self.is_live)

    def test_list_backup_policies(self):
        create_backup_policy(self.client, TEST_BACKUP_POLICY_1)
        create_backup_policy(self.client, TEST_BACKUP_POLICY_2, backup_policy_only=True)

        backup_policies_list = self.client.backup_policies.list(BP_RESOURCE_GROUP, BP_ACCOUNT)
        self.assertEqual(len(list(backup_policies_list)), 2)
        idx = 0
        for backup_policy in backup_policies_list:
            self.assertEqual(backup_policy.name, BACKUP_POLICIES[idx])
            idx += 1

        delete_backup_policy(self.client, TEST_BACKUP_POLICY_1, live=self.is_live)
        delete_backup_policy(self.client, TEST_BACKUP_POLICY_2, live=self.is_live)

        backup_policies_list = self.client.backup_policies.list(BP_RESOURCE_GROUP, BP_ACCOUNT)
        self.assertEqual(len(list(backup_policies_list)), 0)

        delete_account(self.client, BP_RESOURCE_GROUP, BP_ACCOUNT)

    def test_get_backup_policy_by_name(self):
        create_backup_policy(self.client, TEST_BACKUP_POLICY_1)

        backup_policy = self.client.backup_policies.get(BP_RESOURCE_GROUP, BP_ACCOUNT, TEST_BACKUP_POLICY_1)
        self.assertEqual(backup_policy.name, BP_ACCOUNT + "/" + TEST_BACKUP_POLICY_1)

        delete_backup_policy(self.client, TEST_BACKUP_POLICY_1, live=self.is_live)
        delete_account(self.client, BP_RESOURCE_GROUP, BP_ACCOUNT)

    def test_update_backup_policies(self):
        create_backup_policy(self.client, TEST_BACKUP_POLICY_1)
        backup_policy_body = BackupPolicy(
            location=BP_LOCATION,
            daily_backups_to_keep=0,
            weekly_backups_to_keep=1,
            monthly_backups_to_keep=0,
            enabled=False
        )
        self.client.backup_policies.update(BP_RESOURCE_GROUP, BP_ACCOUNT, TEST_BACKUP_POLICY_1, backup_policy_body)

        backup_policy = self.client.backup_policies.get(BP_RESOURCE_GROUP, BP_ACCOUNT, TEST_BACKUP_POLICY_1)
        self.assertEqual(backup_policy.daily_backups_to_keep, 0)
        self.assertEqual(backup_policy.weekly_backups_to_keep, 1)

        delete_backup_policy(self.client, TEST_BACKUP_POLICY_1, live=self.is_live)
        delete_account(self.client, BP_RESOURCE_GROUP, BP_ACCOUNT)
