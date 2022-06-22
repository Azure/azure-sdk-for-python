import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from azure.mgmt.netapp.models import SnapshotPolicy, SnapshotPolicyPatch, HourlySchedule, DailySchedule, VolumeSnapshotProperties, VolumePatchPropertiesDataProtection, VolumePatch
from test_account import create_account, delete_account
from test_pool import delete_pool
from test_volume import create_volume, delete_volume
from setup import *
import azure.mgmt.netapp.models

TEST_SNAPSHOT_POLICY_1 = 'sdk-py-tests-snapshot-policy-1'
TEST_SNAPSHOT_POLICY_2 = 'sdk-py-tests-snapshot-policy-2'


def create_snapshot_policy(client, snapshot_policy_name, rg=TEST_RG, account_name=TEST_ACC_1, location=LOCATION, snapshot_policy_only=False):
    if not snapshot_policy_only:
        create_account(client, rg, account_name, location)

    snapshot_policy_body = SnapshotPolicy(
        location=location,
        hourly_schedule=HourlySchedule(snapshots_to_keep=1, minute=50),
        daily_schedule={},
        weekly_schedule={},
        monthly_schedule={},
        enabled=False
    )

    snapshot_policy = client.snapshot_policies.create(rg, account_name, snapshot_policy_name, snapshot_policy_body)
    return snapshot_policy


def delete_snapshot_policy(client, snapshot_policy_name, rg=TEST_RG, account_name=TEST_ACC_1, live=False):
    client.snapshot_policies.begin_delete(rg, account_name, snapshot_policy_name).wait()
    wait_for_no_snapshot_policy(client, rg, account_name, snapshot_policy_name, live)


def wait_for_no_snapshot_policy(client, rg, account_name, snapshot_policy_name, live=False):
    # a workaround for the async nature of certain ARM processes
    co = 0
    while co < 10:
        co += 1
        if live:
            time.sleep(5)
        try:
            client.snapshot_policies.get(rg, account_name, snapshot_policy_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break


class TestNetAppSnapshotPolicy(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_snapshot_policy(self):
        create_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_1)

        snapshot_policies_list = self.client.snapshot_policies.list(TEST_RG, TEST_ACC_1)
        assert len(list(snapshot_policies_list)) == 1

        delete_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_1, live=self.is_live)

        snapshot_policies_list = self.client.snapshot_policies.list(TEST_RG, TEST_ACC_1)
        assert len(list(snapshot_policies_list)) == 0

        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)

    @recorded_by_proxy
    def test_list_snapshot_policies(self):
        create_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_1)
        create_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_2, snapshot_policy_only=True)

        snapshot_policies_list = self.client.snapshot_policies.list(TEST_RG, TEST_ACC_1)
        assert len(list(snapshot_policies_list)) == 2
        snapshot_policies = [TEST_SNAPSHOT_POLICY_1, TEST_SNAPSHOT_POLICY_2]

        idx = 0
        for snapshot_policy  in snapshot_policies_list:
            assert snapshot_policy.name == snapshot_policies[idx]
            idx += 1

        delete_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_1, live=self.is_live)
        delete_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_2, live=self.is_live)

        snapshot_policies_list = self.client.snapshot_policies.list(TEST_RG, TEST_ACC_1)
        assert len(list(snapshot_policies_list)) == 0

        delete_account(self.client, TEST_RG, TEST_ACC_1)

    @recorded_by_proxy
    def test_get_snapshot_policy_by_name(self):
        create_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_1)

        snapshot_policy = self.client.snapshot_policies.get(TEST_RG, TEST_ACC_1, TEST_SNAPSHOT_POLICY_1)
        assert snapshot_policy.name == TEST_ACC_1 + "/" + TEST_SNAPSHOT_POLICY_1

        delete_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1)

    @recorded_by_proxy
    def test_update_snapshot_policies(self):
        create_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_1)

        snapshot_policy_body = SnapshotPolicyPatch(
            location=LOCATION,
            hourly_schedule={},
            daily_schedule=DailySchedule(snapshots_to_keep=1, minute=50, hour=1),
            weekly_schedule={},
            monthly_schedule={},
            enabled=False
        )
        snapshot_policy = self.client.snapshot_policies.begin_update(TEST_RG, TEST_ACC_1, TEST_SNAPSHOT_POLICY_1, snapshot_policy_body).result()
        assert snapshot_policy.daily_schedule.snapshots_to_keep == 1
        assert snapshot_policy.daily_schedule.hour == 1
        assert snapshot_policy.daily_schedule.minute == 50

        delete_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1)

    @recorded_by_proxy
    def test_assign_snapshot_policy_to_volume(self):
        set_bodiless_matcher()
        # create volume and snapshot policy
        create_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        snapshot_policy = create_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_1)
        # assign the snapshot policy to the volume
        snapshot = VolumeSnapshotProperties(snapshot_policy_id=snapshot_policy.id)
        data_protection = VolumePatchPropertiesDataProtection(snapshot=snapshot)
        volume_patch = VolumePatch(data_protection=data_protection)
        volume = self.client.volumes.begin_update(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, volume_patch).result()

        assert volume.data_protection.snapshot.snapshot_policy_id == snapshot_policy.id

        # cleanup
        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        delete_snapshot_policy(self.client, TEST_SNAPSHOT_POLICY_1, live=self.is_live)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)
