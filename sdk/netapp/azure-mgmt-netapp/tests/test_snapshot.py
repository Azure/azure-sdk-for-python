import time
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from azure.mgmt.netapp.models import Volume, Snapshot
from test_volume import create_volume, wait_for_volume, delete_volume, create_virtual_network
from test_pool import delete_pool
from test_account import delete_account
from setup import *
import azure.mgmt.netapp.models

TEST_SNAPSHOT_1 = 'sdk-py-tests-snapshot-1'
TEST_SNAPSHOT_2 = 'sdk-py-tests-snapshot-2'


def create_snapshot(client, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1,
                    snapshot_name=TEST_SNAPSHOT_1, location=LOCATION, vnet=VNET, snapshot_only=False):
    if not snapshot_only:
        volume = create_volume(client, rg, account_name, pool_name, volume_name, vnet=vnet)
        # be sure the volume is really available
        wait_for_volume(client, rg, account_name, pool_name, volume_name)
    else:
        # we need to get the volume id if we didn't just create it
        volume = client.volumes.get(rg, account_name, pool_name, volume_name)

    body = Snapshot(location=location, file_system_id=volume.file_system_id)
    return client.snapshots.begin_create(rg, account_name, pool_name, volume_name, snapshot_name, body).result()


def delete_snapshot(client, rg, account_name, pool_name, volume_name, snapshot_name, live=False):
    client.snapshots.begin_delete(rg, account_name, pool_name, volume_name, snapshot_name).wait()

    # wait to be sure it has gone - a workaround for the async nature of certain ARM processes
    co = 0
    while co < 10:
        co += 1
        if live:
            time.sleep(20)
        try:
            client.snapshots.get(rg, account_name, pool_name, volume_name, snapshot_name)
        except:
            # not found is an exception case (status code 200 expected)
            # but is what we are waiting for
            break


class TestNetAppSnapshot(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        self.network_client = self.create_mgmt_client(NetworkManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_create_delete_snapshot(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')                
        create_snapshot(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SNAPSHOT_1, LOCATION, vnet=VNETNAME)

        snapshot_list = self.client.snapshots.list(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        assert len(list(snapshot_list)) == 1

        delete_snapshot(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SNAPSHOT_1, self.is_live)
        snapshot_list = self.client.snapshots.list(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        assert len(list(snapshot_list)) == 0

        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, self.is_live)
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, self.is_live)
        delete_account(self.client, TEST_RG, ACCOUNT1, self.is_live)
        self.network_client.virtual_networks.begin_delete(TEST_RG, VNETNAME)

    @recorded_by_proxy
    def test_list_snapshots(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')           
        create_snapshot(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SNAPSHOT_1, LOCATION, vnet=VNETNAME)
        create_snapshot(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SNAPSHOT_2, LOCATION, snapshot_only=True)
        snapshots = [TEST_SNAPSHOT_1, TEST_SNAPSHOT_2]

        snapshot_list = self.client.snapshots.list(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        assert len(list(snapshot_list)) == 2
        idx = 0
        for snapshot in snapshot_list:
            assert snapshot.name == snapshots[idx]
            idx += 1

        delete_snapshot(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SNAPSHOT_1, self.is_live)
        delete_snapshot(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SNAPSHOT_2, self.is_live)
        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, self.is_live)
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, self.is_live)
        delete_account(self.client, TEST_RG, ACCOUNT1, self.is_live)

    @recorded_by_proxy
    def test_get_snapshot_by_name(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')           
        create_snapshot(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SNAPSHOT_1, LOCATION, vnet=VNETNAME)

        snapshot = self.client.snapshots.get(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SNAPSHOT_1)
        assert snapshot.name == ACCOUNT1 + '/' + TEST_POOL_1 + '/' + volumeName1+ '/' + TEST_SNAPSHOT_1

        delete_snapshot(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SNAPSHOT_1, self.is_live)
        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, self.is_live)
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, self.is_live)
        delete_account(self.client, TEST_RG, ACCOUNT1, self.is_live)
