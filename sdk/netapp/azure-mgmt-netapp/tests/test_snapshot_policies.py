import time
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from azure.mgmt.netapp.models import (
    SnapshotPolicy,
    SnapshotPolicyPatch,
    HourlySchedule,
    DailySchedule,
    VolumeSnapshotProperties,
    VolumePatchPropertiesDataProtection,
    VolumePatch,
)
from test_account import create_account, delete_account
from test_pool import delete_pool
from test_volume import create_volume, delete_volume, wait_for_volume
import setup
import azure.mgmt.netapp.models

setup.TEST_SNAPSHOT_POLICY_1 = "sdk-py-tests-snapshot-policy-1"
setup.TEST_SNAPSHOT_POLICY_2 = "sdk-py-tests-snapshot-policy-2"


def create_snapshot_policy(
    client,
    snapshot_policy_name,
    rg=setup.TEST_RG,
    account_name=setup.TEST_ACC_1,
    location=setup.LOCATION,
    snapshot_policy_only=False,
):
    if not snapshot_policy_only:
        create_account(client, rg, account_name, location)

    snapshot_policy_body = SnapshotPolicy(
        location=location,
        hourly_schedule=HourlySchedule(snapshots_to_keep=1, minute=50),
        daily_schedule={},
        weekly_schedule={},
        monthly_schedule={},
        enabled=False,
    )

    snapshot_policy = client.snapshot_policies.create(rg, account_name, snapshot_policy_name, snapshot_policy_body)
    wait_for_snapshot_policy(client, rg, account_name, snapshot_policy_name)
    return snapshot_policy


def wait_for_snapshot_policy(client, rg, account_name, snapshot_policy_name):
    # a work around for the async nature of certain ARM processes
    retry = 0
    while retry < 60:
        retry += 1
        snapshot_policy = client.snapshot_policies.get(rg, account_name, snapshot_policy_name)
        if snapshot_policy.provisioning_state == "Succeeded":
            break
        if snapshot_policy.provisioning_state == "Failed":
            print("\t Wait for snapshotPolicy. SnapshotPolicy is in a failed state.")
            break
        if setup.LIVE:
            time.sleep(3)
    if retry == 60:
        raise Exception("Timeout when waiting for snapshot policy")


def delete_snapshot_policy(client, snapshot_policy_name, rg=setup.TEST_RG, account_name=setup.TEST_ACC_1):
    client.snapshot_policies.begin_delete(rg, account_name, snapshot_policy_name).wait()
    wait_for_no_snapshot_policy(client, rg, account_name, snapshot_policy_name)


def wait_for_no_snapshot_policy(client, rg, account_name, snapshot_policy_name):
    # a workaround for the async nature of certain ARM processes
    retry = 0
    while retry < 60:
        retry += 1
        try:
            client.snapshot_policies.get(rg, account_name, snapshot_policy_name)
        except:
            # not found is an exception case (status code 200 expected)
            # and is actually what we are waiting for
            break
        if setup.LIVE:
            time.sleep(3)
    if retry == 60:
        raise Exception("Timeout when waiting for no snapshot policy")


class TestNetAppSnapshotPolicy(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            setup.LIVE = True

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_snapshot_policy(self):
        print("Starting test_create_delete_snapshot_policy")
        ACCOUNT1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        create_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_1, account_name=ACCOUNT1)

        snapshot_policies_list = self.client.snapshot_policies.list(setup.TEST_RG, account_name=ACCOUNT1)
        assert len(list(snapshot_policies_list)) == 1

        delete_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_1, account_name=ACCOUNT1)

        snapshot_policies_list = self.client.snapshot_policies.list(setup.TEST_RG, ACCOUNT1)
        assert len(list(snapshot_policies_list)) == 0

        delete_account(self.client, setup.TEST_RG, ACCOUNT1)
        print("Finished with test_create_delete_snapshot_policy")

    @recorded_by_proxy
    def test_list_snapshot_policies(self):
        print("Starting test_list_snapshot_policies")
        ACCOUNT1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        create_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_1, account_name=ACCOUNT1)
        create_snapshot_policy(
            self.client, setup.TEST_SNAPSHOT_POLICY_2, account_name=ACCOUNT1, snapshot_policy_only=True
        )

        snapshot_policies_list = self.client.snapshot_policies.list(setup.TEST_RG, ACCOUNT1)
        assert len(list(snapshot_policies_list)) == 2
        snapshot_policies = [setup.TEST_SNAPSHOT_POLICY_1, setup.TEST_SNAPSHOT_POLICY_2]

        idx = 0
        for snapshot_policy in snapshot_policies_list:
            assert snapshot_policy.name == snapshot_policies[idx]
            idx += 1

        delete_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_1, account_name=ACCOUNT1)
        delete_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_2, account_name=ACCOUNT1)

        snapshot_policies_list = self.client.snapshot_policies.list(setup.TEST_RG, ACCOUNT1)
        assert len(list(snapshot_policies_list)) == 0

        delete_account(self.client, setup.TEST_RG, ACCOUNT1)
        print("Finished with test_list_snapshot_policies")

    @recorded_by_proxy
    def test_get_snapshot_policy_by_name(self):
        print("Starting test_get_snapshot_policy_by_name")
        ACCOUNT1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        create_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_1, account_name=ACCOUNT1)

        snapshot_policy = self.client.snapshot_policies.get(setup.TEST_RG, ACCOUNT1, setup.TEST_SNAPSHOT_POLICY_1)
        assert snapshot_policy.name == ACCOUNT1 + "/" + setup.TEST_SNAPSHOT_POLICY_1

        delete_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_1, account_name=ACCOUNT1)
        delete_account(self.client, setup.TEST_RG, ACCOUNT1)
        print("Finished with test_get_snapshot_policy_by_name")

    @recorded_by_proxy
    def test_update_snapshot_policies(self):
        print("Starting test_update_snapshot_policies")
        ACCOUNT1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        create_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_1, account_name=ACCOUNT1)

        snapshot_policy_body = SnapshotPolicyPatch(
            location=setup.LOCATION,
            hourly_schedule={},
            daily_schedule=DailySchedule(snapshots_to_keep=1, minute=50, hour=1),
            weekly_schedule={},
            monthly_schedule={},
            enabled=False,
        )
        snapshot_policy = self.client.snapshot_policies.begin_update(
            setup.TEST_RG, ACCOUNT1, setup.TEST_SNAPSHOT_POLICY_1, snapshot_policy_body
        ).result()
        wait_for_snapshot_policy(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_SNAPSHOT_POLICY_1)
        assert snapshot_policy.daily_schedule.snapshots_to_keep == 1
        assert snapshot_policy.daily_schedule.hour == 1
        assert snapshot_policy.daily_schedule.minute == 50

        delete_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_1, account_name=ACCOUNT1)
        delete_account(self.client, setup.TEST_RG, ACCOUNT1)
        print("Finished with test_update_snapshot_policies")

    @recorded_by_proxy
    def test_assign_snapshot_policy_to_volume(self):
        print("Starting test_assign_snapshot_policy_to_volume")
        set_bodiless_matcher()
        # create volume and snapshot policy
        ACCOUNT1 = self.get_resource_name(setup.TEST_ACC_1 + "-")
        volumeName1 = self.get_resource_name(setup.TEST_VOL_1 + "-")

        create_volume(
            self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName1, setup.LOCATION, vnet=setup.PERMA_VNET
        )

        snapshot_policy = create_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_1, account_name=ACCOUNT1)
        # assign the snapshot policy to the volume
        snapshot = VolumeSnapshotProperties(snapshot_policy_id=snapshot_policy.id)
        data_protection = VolumePatchPropertiesDataProtection(snapshot=snapshot)
        volume_patch = VolumePatch(data_protection=data_protection)
        volume = self.client.volumes.begin_update(
            setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName1, volume_patch
        ).result()
        wait_for_volume(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName1)

        assert volume.data_protection.snapshot.snapshot_policy_id == snapshot_policy.id

        # cleanup
        delete_volume(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1, volumeName1)
        delete_snapshot_policy(self.client, setup.TEST_SNAPSHOT_POLICY_1, account_name=ACCOUNT1)
        delete_pool(self.client, setup.TEST_RG, ACCOUNT1, setup.TEST_POOL_1)
        delete_account(self.client, setup.TEST_RG, ACCOUNT1)

        print("Finished with test_assign_snapshot_policy_to_volume")
