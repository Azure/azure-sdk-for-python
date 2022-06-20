import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy
from azure.mgmt.netapp.models import BackupPolicy, BackupPolicyPatch
from test_account import create_account, delete_account
from setup import *
import azure.mgmt.netapp.models

TEST_BACKUP_POLICY_1='sdk-py-tests-backup-policy-1'
TEST_BACKUP_POLICY_2='sdk-py-tests-backup-policy-2'
BACKUP_POLICIES = [TEST_BACKUP_POLICY_1, TEST_BACKUP_POLICY_2]


def create_backup_policy(client, backup_policy_name, rg=TEST_RG, account_name=TEST_ACC_1, location=LOCATION, backup_policy_only=False):
    if not backup_policy_only:
        create_account(client, rg, account_name, location)

    backup_policy_body = BackupPolicy(
        location=location,
        daily_backups_to_keep=2,
        weekly_backups_to_keep=0,
        monthly_backups_to_keep=0,
        enabled=True
    )

    backup_policy = client.backup_policies.begin_create(rg, account_name, backup_policy_name, backup_policy_body).result()
    return backup_policy


def delete_backup_policy(client, backup_policy_name, rg=TEST_RG, account_name=TEST_ACC_1, live=False):
    client.backup_policies.begin_delete(rg, account_name, backup_policy_name).wait()
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


def wait_for_backup_policy_state(client, desired_state, rg=TEST_RG, account_name=TEST_ACC_1,
                                 backup_policy_name=TEST_BACKUP_POLICY_1, live=False):
    co = 0
    while co < 5:
        co += 1
        policy = client.backup_policies.get(rg, account_name, backup_policy_name)
        if policy.provisioning_state == desired_state:
            break
        if live:
            time.sleep(5)


class TestNetAppBackupPolicies(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_backup_policy(self):
        create_backup_policy(self.client, TEST_BACKUP_POLICY_1)

        backup_policies_list = self.client.backup_policies.list(TEST_RG, TEST_ACC_1)
        assert len(list(backup_policies_list)) == 1

        delete_backup_policy(self.client, TEST_BACKUP_POLICY_1, live=self.is_live)

        backup_policies_list = self.client.backup_policies.list(TEST_RG, TEST_ACC_1)
        assert len(list(backup_policies_list)) == 0

        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    @recorded_by_proxy
    def test_list_backup_policies(self):
        create_backup_policy(self.client, TEST_BACKUP_POLICY_1)
        create_backup_policy(self.client, TEST_BACKUP_POLICY_2, backup_policy_only=True)

        backup_policies_list = self.client.backup_policies.list(TEST_RG, TEST_ACC_1)
        assert len(list(backup_policies_list)) == 2
        idx = 0
        for backup_policy in backup_policies_list:
            assert backup_policy.name == BACKUP_POLICIES[idx]
            idx += 1

        delete_backup_policy(self.client, TEST_BACKUP_POLICY_1, live=self.is_live)
        delete_backup_policy(self.client, TEST_BACKUP_POLICY_2, live=self.is_live)

        backup_policies_list = self.client.backup_policies.list(TEST_RG, TEST_ACC_1)
        assert len(list(backup_policies_list)) == 0

        delete_account(self.client, TEST_RG, TEST_ACC_1)

    @recorded_by_proxy
    def test_get_backup_policy_by_name(self):
        create_backup_policy(self.client, TEST_BACKUP_POLICY_1)

        backup_policy = self.client.backup_policies.get(TEST_RG, TEST_ACC_1, TEST_BACKUP_POLICY_1)
        assert backup_policy.name == TEST_ACC_1 + "/" + TEST_BACKUP_POLICY_1

        delete_backup_policy(self.client, TEST_BACKUP_POLICY_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1)

    @recorded_by_proxy
    def test_update_backup_policies(self):
        create_backup_policy(self.client, TEST_BACKUP_POLICY_1)
        backup_policy_body = BackupPolicyPatch(
            location=LOCATION,
            daily_backups_to_keep=0,
            weekly_backups_to_keep=1,
            monthly_backups_to_keep=0,
            enabled=True
        )
        backup_policy = self.client.backup_policies.begin_update(TEST_RG, TEST_ACC_1, TEST_BACKUP_POLICY_1, backup_policy_body).result()
        assert backup_policy.daily_backups_to_keep == 0
        assert backup_policy.weekly_backups_to_keep == 1

        delete_backup_policy(self.client, TEST_BACKUP_POLICY_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1)
