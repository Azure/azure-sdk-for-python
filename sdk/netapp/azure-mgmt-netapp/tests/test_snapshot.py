import random
import string
import time
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from azure.mgmt.netapp.models import Volume, Snapshot
from test_volume import create_volume, wait_for_volume, delete_volume, create_virtual_network
from test_pool import delete_pool
from test_account import delete_account
import setup
import azure.mgmt.netapp.models

def create_snapshot(client, rg=setup.TEST_RG, account_name=setup.TEST_ACC_1, pool_name=setup.TEST_POOL_1, volume_name=setup.TEST_VOL_1,
                    snapshot_name=setup.TEST_SNAPSHOT_1, location=setup.LOCATION, vnet=setup.PERMA_VNET, snapshot_only=False):
    if not snapshot_only:
        volume = create_volume(client, rg, account_name, pool_name, volume_name, vnet=setup.PERMA_VNET, volume_only=True)
    else:
        # we need to get the volume id if we didn't just create it
        volume = client.volumes.get(rg, account_name, pool_name, volume_name)

    body = Snapshot(location=location, file_system_id=volume.file_system_id)
    client.snapshots.begin_create(rg, account_name, pool_name, volume_name, snapshot_name, body).result()
    snapshot = wait_for_snapshot(client, rg, account_name, pool_name, volume_name, snapshot_name)
    return snapshot


def delete_snapshot(client, rg, account_name, pool_name, volume_name, snapshot_name):
    client.snapshots.begin_delete(rg, account_name, pool_name, volume_name, snapshot_name).wait()
    wait_for_no_snapshot(client, rg, account_name, pool_name, volume_name, snapshot_name)

def wait_for_no_snapshot(client, rg, account_name, pool_name, volume_name, snapshot_name):
    retry = 0
    while retry < 60:
        retry += 1
        try:
            snapshot = client.snapshots.get(rg, account_name, pool_name, volume_name, snapshot_name)
            print("\tGot snapshot. Still waiting. state = " + snapshot.provisioning_state)
        except:
            # not found is an exception case (status code 200 expected)
            # but is what we are waiting for
            break
        if setup.LIVE:
            time.sleep(3)
    if retry == 60:
        raise Exception("Timeout when waiting for no snapshot")

def wait_for_snapshot(client, rg, account_name, pool_name, volume_name, snapshot_name):
    retry = 0
    while retry < 100:
        retry += 1
        snapshot = client.snapshots.get(rg, account_name, pool_name, volume_name, snapshot_name)
        if snapshot.provisioning_state == "Succeeded":
            break
        if snapshot.provisioning_state == "Failed":
            print("\t Wait for snapshot. Snapshot is in a failed state.")
            break
        if setup.LIVE:
            time.sleep(3)
    if retry == 100:
        raise Exception("Timeout when waiting for snapshot")
    return snapshot

class TestNetAppSnapshot(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            setup.LIVE = True

    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_snapshot(self):
        print("Starting test_create_delete_snapshot")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(setup.TEST_VOL_1+"-")
        snapshotname = self.get_resource_name(setup.TEST_SNAPSHOT_1+"-")
        try:
            create_snapshot(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, snapshotname, setup.LOCATION, vnet=setup.PERMA_VNET)

            snapshot_list = self.client.snapshots.list(setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)
            assert len(list(snapshot_list)) == 1

            delete_snapshot(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, snapshotname)
            snapshot_list = self.client.snapshots.list(setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)
            assert len(list(snapshot_list)) == 0
        finally:
            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)

        print("Finished with test_create_delete_snapshot")

    @recorded_by_proxy
    def test_list_snapshots(self):
        print("Starting test_list_snapshots")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(setup.TEST_VOL_1+"-")
        snapshotname = self.get_resource_name(setup.TEST_SNAPSHOT_1+"-")
        snapshotname2 = self.get_resource_name(setup.TEST_SNAPSHOT_2+"-")

        try:
            create_snapshot(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, snapshotname, setup.LOCATION, vnet=setup.PERMA_VNET)
            create_snapshot(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, snapshotname2, setup.LOCATION, snapshot_only=True)
            snapshots = [snapshotname, snapshotname2]

            snapshot_list = self.client.snapshots.list(setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)
            assert len(list(snapshot_list)) == 2
            idx = 0
            for snapshot in snapshot_list:
                assert snapshot.name == snapshots[idx]
                idx += 1
        finally:
            delete_snapshot(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, snapshotname)
            delete_snapshot(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, snapshotname2)
            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)

        print("Finished with test_list_snapshots")  

    @recorded_by_proxy
    def test_get_snapshot_by_name(self):
        print("Starting test_get_snapshot_by_name")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(setup.TEST_VOL_1+"-")
        snapshotname = self.get_resource_name(setup.TEST_SNAPSHOT_1+"-")

        try:      
            create_snapshot(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, snapshotname, setup.LOCATION, vnet=setup.PERMA_VNET)

            snapshot = self.client.snapshots.get(setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, snapshotname)
            assert snapshot.name == setup.PERMA_ACCOUNT + '/' + setup.PERMA_POOL + '/' + volumeName1+ '/' + snapshotname
        finally:
            delete_snapshot(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1, snapshotname)
            delete_volume(self.client, setup.TEST_RG, setup.PERMA_ACCOUNT, setup.PERMA_POOL, volumeName1)

        print("Finished with test_get_snapshot_by_name")