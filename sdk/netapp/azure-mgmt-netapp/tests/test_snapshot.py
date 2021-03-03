import time
import json
import unittest
from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.netapp.models import Volume
from test_volume import create_volume, wait_for_volume, delete_volume
from test_pool import delete_pool
from test_account import delete_account
from azure.mgmt.netapp.models import Snapshot
from setup import *
import azure.mgmt.netapp.models
import unittest

snapshots = [TEST_SNAPSHOT_1, TEST_SNAPSHOT_2]


def create_snapshot(client, rg=TEST_RG, account_name=TEST_ACC_1, pool_name=TEST_POOL_1, volume_name=TEST_VOL_1, snapshot_name=TEST_SNAPSHOT_1, location=LOCATION, snapshot_only=False):
    if not snapshot_only:
        volume = create_volume(client, rg, account_name, pool_name, volume_name)
        # be sure the volume is really available
        wait_for_volume(client, rg, account_name, pool_name, volume_name)
    else:
        # we need to get the volume id if we didn't just create it
        volume = client.volumes.get(rg, account_name, pool_name, volume_name)

    snapshot = client.snapshots.create(rg, account_name, pool_name, volume_name, snapshot_name,location=location, file_system_id=volume.file_system_id).result()
    
    return snapshot

def delete_snapshot(client, rg, account_name, pool_name, volume_name, snapshot_name, live=False):
    client.snapshots.delete(rg, account_name, pool_name, volume_name, snapshot_name).wait()

    # wait to be sure it has gone - a workaround for the async nature of certain ARM processes
    co=0
    while co<10:
        co += 1
        if live:
            time.sleep(20)
        try:
            snapshot = client.snapshots.get(rg, account_name, pool_name, volume_name, snapshot_namne)
        except:
            # not found is an exception case (status code 200 expected)
            # but is what we are waiting for
            break


@unittest.skip("skip test")
class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.AzureNetAppFilesManagementClient)

    def test_create_delete_snapshot(self):
        print("@@@@@@@@@", TEST_RG)
        snapshot = create_snapshot(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, TEST_SNAPSHOT_1, LOCATION)

        snapshot_list = self.client.snapshots.list(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        self.assertEqual(len(list(snapshot_list)), 1)

        self.client.snapshots.delete(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, TEST_SNAPSHOT_1).wait()
        snapshot_list = self.client.snapshots.list(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        self.assertEqual(len(list(snapshot_list)), 0)

        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, TEST_ACC_1)

    def test_list_snapshots(self):
        snapshot = create_snapshot(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, TEST_SNAPSHOT_1, LOCATION)
        snapshot = create_snapshot(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, TEST_SNAPSHOT_2, LOCATION, snapshot_only=True)

        snapshot_list = self.client.snapshots.list(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        self.assertEqual(len(list(snapshot_list)), 2)
        idx = 0
        for snapshot in snapshot_list:
            self.assertEqual(snapshot.name, snapshots[idx])
            idx += 1

        delete_snapshot(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, TEST_SNAPSHOT_1)
        delete_snapshot(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, TEST_SNAPSHOT_2)
        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, TEST_ACC_1)

    def test_get_snapshot_by_name(self):
        snapshot = create_snapshot(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, TEST_SNAPSHOT_1, LOCATION)

        snapshot = self.client.snapshots.get(TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, TEST_SNAPSHOT_1)
        self.assertEqual(snapshot.name, TEST_ACC_1 + '/' + TEST_POOL_1 + '/' + TEST_VOL_1+ '/' + TEST_SNAPSHOT_1)

        delete_snapshot(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, TEST_SNAPSHOT_1)
        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, TEST_ACC_1)






