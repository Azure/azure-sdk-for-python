import random
import string
from azure.mgmt.netapp.models import SubvolumeInfo, SubvolumePatchRequest
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from test_volume import create_volume, delete_volume, delete_pool, delete_account, create_virtual_network, wait_for_volume
from setup import *
import azure.mgmt.netapp.models
import time

LIVE = False

def create_subvolume(client, rg, account_name, pool_name, volume_name, subvolume_name, path, size):
    print("Creating subvolume {0} under volume {1}".format(subvolume_name, volume_name))
       
    subvolume_body = SubvolumeInfo(
        path=path,
        size=size
    )

    client.subvolumes.begin_create(
        rg, account_name, pool_name, volume_name, subvolume_name, subvolume_body).result()
    subvolume = wait_for_subvolume(client, rg, account_name, pool_name, volume_name, subvolume_name)
    print("\tdone")
    return subvolume

def wait_for_subvolume(client, rg, account_name, pool_name, volume_name, subvolume_name):
    co = 0
    while co < 60:
        co += 1
        subvolume = client.subvolumes.get(rg, account_name, pool_name, volume_name, subvolume_name)
        if subvolume.provisioning_state == "Succeeded":
            break
        if subvolume.provisioning_state == "Failed":
            print("\t Wait for subvolume. Subvolume is in a failed state.")
            break
        if LIVE:
            time.sleep(3)
    return subvolume    

def delete_subvolume(client, rg, account_name, pool_name, volume_name, subvolume_name):
    print("Delete subvolume {0}".format(volume_name))
    client.subvolumes.begin_delete(rg, account_name, pool_name, volume_name, subvolume_name).wait()
    wait_for_no_subvolume(client, rg, account_name, pool_name, volume_name, subvolume_name)
    print("\tDone")

def wait_for_no_subvolume(client, rg, account_name, pool_name, volume_name, subvolume_name):
    co = 0
    while co < 60:
        co += 1
        try:
            vol = client.subvolumes.get(rg, account_name, pool_name, volume_name, subvolume_name)
            print("\tGot subvolume. Still waiting. State = " + vol.provisioning_state)
        except:
            # not found is an exception case (status code 200 expected)
            # but is what we are waiting for
            break
        if LIVE:
            time.sleep(3)

class TestNetAppSubvolume(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            global LIVE
            LIVE = True
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(NetworkManagementClient) 

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_crud_subvolumes(self):
        print("Starting test_crud_subvolumes")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        subvolumeName = self.get_resource_name(TEST_SUBVOLUME_1+"-")
        
        try:
            create_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, LOCATION, vnet=PERMA_VNET, volume_only=True, enable_subvolumes="Enabled")

            # create
            subvolume = create_subvolume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName, "/sub_vol_1.txt", 1000000)
            
            assert subvolume.name == PERMA_ACCOUNT + "/" + PERMA_POOL + "/" + volumeName1 + "/" + subvolumeName
            assert subvolume.path == "/sub_vol_1.txt"

            # update
            subvolume_patch = SubvolumePatchRequest(path="/sub_vol_update.txt", size=2000000)
            print("Updating subvolume")
            subvolume = self.client.subvolumes.begin_update(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName, subvolume_patch).result()
            print("\tDone")
            wait_for_subvolume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName)
            wait_for_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
            assert subvolume.name == PERMA_ACCOUNT + "/" + PERMA_POOL + "/" + volumeName1 + "/" + subvolumeName
            assert subvolume.path == "/sub_vol_update.txt"

            # get
            subvolume_info = self.client.subvolumes.get(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName)
            assert subvolume_info.name == PERMA_ACCOUNT + "/" + PERMA_POOL + "/" + volumeName1 + "/" + subvolumeName
            assert subvolume_info.path == "/sub_vol_update.txt"
        finally:
            # delete
            delete_subvolume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName)
            subvolume_list = self.client.subvolumes.list_by_volume(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
            assert len(list(subvolume_list)) == 0
            delete_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
        
        print("Finished with test_crud_subvolumes")

    @recorded_by_proxy
    def test_list_by_volume(self):
        print("Starting test_list_by_volume")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        subvolumeName = self.get_resource_name(TEST_SUBVOLUME_1+"-")
        subvolumeName2 = self.get_resource_name(TEST_SUBVOLUME_2+"-")
        
        try:
            create_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, LOCATION, vnet=PERMA_VNET, enable_subvolumes="Enabled")

            # create
            subvolume = create_subvolume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName, "/sub_vol_2.txt", 1000000)
            subvolume2 = create_subvolume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName2, "/sub_vol_3.txt", 2000000)

            # list_by_volume
            subvolume_list = self.client.subvolumes.list_by_volume(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
            assert len(list(subvolume_list)) == 2

            delete_subvolume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName)
            subvolume_list = self.client.subvolumes.list_by_volume(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
            assert len(list(subvolume_list)) == 1

            delete_subvolume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName2)
            subvolume_list = self.client.subvolumes.list_by_volume(TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
            assert len(list(subvolume_list)) == 0
        finally:
            # clean up
            delete_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
        
        print("Finished with test_list_by_volume")

    @recorded_by_proxy
    def test_get_metadata(self):
        print("Starting test_get_metadata")
        set_bodiless_matcher()
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        subvolumeName = self.get_resource_name(TEST_SUBVOLUME_1+"-")

        try:
            create_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, LOCATION, vnet=PERMA_VNET, enable_subvolumes="Enabled")

            # create
            subvolume = create_subvolume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName, "/sub_vol_4.txt", 123)
            assert subvolume.name == PERMA_ACCOUNT + "/" + PERMA_POOL + "/" + volumeName1 + "/" + subvolumeName
            assert subvolume.path == "/sub_vol_4.txt"

            # get metadata
            metadata = self.client.subvolumes.begin_get_metadata(
                TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName).result()
            assert metadata is not None

        finally:
            # clean up
            delete_subvolume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1, subvolumeName)
            delete_volume(self.client, TEST_RG, PERMA_ACCOUNT, PERMA_POOL, volumeName1)
        
        print("Finished with test_get_metadata")
