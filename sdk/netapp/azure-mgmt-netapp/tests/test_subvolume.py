from azure.mgmt.netapp.models import SubvolumeInfo, SubvolumePatchRequest
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from test_volume import create_volume, delete_volume, delete_pool, delete_account, create_virtual_network
from setup import *
import azure.mgmt.netapp.models
import time

def wait_for_subvolume_created(client, rg, account_name, pool_name, volume_name, subvolume_name, live=False):
    co = 0
    while co < 40:
        co += 1
        if live:
            time.sleep(5)
        subvolume = client.subvolumes.get(rg, account_name, pool_name, volume_name, subvolume_name)
        if subvolume.provisioning_state == "Succeeded":
            break


class TestNetAppSubvolume(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(NetworkManagementClient) 

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_crud_subvolumes(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        if self.is_live:
            SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')
        create_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, LOCATION, vnet=VNETNAME, enable_subvolumes="Enabled")
        path = "/sub_vol_1.txt"
        size = 1000000
        parent_path = "/parent_sub_vol_1.txt"        
        subvolume_body = SubvolumeInfo(
            path=path,
            size=size
        )

        # create
        subvolume_info = self.client.subvolumes.begin_create(
            TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_1, subvolume_body).result()
        assert subvolume_info.name == ACCOUNT1 + "/" + TEST_POOL_1 + "/" + volumeName1 + "/" + TEST_SUBVOLUME_1
        assert subvolume_info.path == path

        # update
        path = "/sub_vol_update.txt"
        size = 2000000
        subvolume_patch = SubvolumePatchRequest(
            path=path,
            size=size,
        )
        subvolume_info = self.client.subvolumes.begin_update(
            TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_1, subvolume_patch).result()
        assert subvolume_info.name == ACCOUNT1 + "/" + TEST_POOL_1 + "/" + volumeName1 + "/" + TEST_SUBVOLUME_1
        assert subvolume_info.path, path

        # get
        subvolume_info = self.client.subvolumes.get(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_1)
        assert subvolume_info.name == ACCOUNT1 + "/" + TEST_POOL_1 + "/" + volumeName1 + "/" + TEST_SUBVOLUME_1
        assert subvolume_info.path == path

        # delete
        self.client.subvolumes.begin_delete(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_1).wait()
        subvolume_list = self.client.subvolumes.list_by_volume(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        assert len(list(subvolume_list)) == 0

        # clean up
        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, live=self.is_live)
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, ACCOUNT1, live=self.is_live)
        if self.is_live:
            self.network_client.virtual_networks.begin_delete(TEST_RG, VNETNAME)


    @recorded_by_proxy
    def test_list_by_volume(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        if self.is_live:
            SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')
        create_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, LOCATION, vnet=VNETNAME, enable_subvolumes="Enabled")

        path1 = "/sub_vol_1.txt"
        size1 = 1000000
        subvolume_body1 = SubvolumeInfo(
            path=path1,
            size=size1
        )

        path2 = "/sub_vol_2.txt"
        size2 = 2000000
        subvolume_body2 = SubvolumeInfo(
            path=path2,
            size=size2
        )

        # create
        self.client.subvolumes.begin_create(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_1, subvolume_body1)
        wait_for_subvolume_created(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_1)
        self.client.subvolumes.begin_create(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_2, subvolume_body2)

        # list_by_volume
        subvolume_list = self.client.subvolumes.list_by_volume(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        assert len(list(subvolume_list)) == 2

        self.client.subvolumes.begin_delete(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_1).wait()
        subvolume_list = self.client.subvolumes.list_by_volume(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        assert len(list(subvolume_list)) == 1

        self.client.subvolumes.begin_delete(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_2).wait()
        subvolume_list = self.client.subvolumes.list_by_volume(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1)
        assert len(list(subvolume_list)) == 0

        # clean up
        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, live=self.is_live)
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, ACCOUNT1, live=self.is_live)
        if self.is_live:
            self.network_client.virtual_networks.begin_delete(TEST_RG, VNETNAME)

    @recorded_by_proxy
    def test_get_metadata(self):
        set_bodiless_matcher()
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        if self.is_live:
            SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')
        create_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, LOCATION, vnet=VNETNAME, enable_subvolumes="Enabled")

        path = "/sub_vol_1.txt"
        size = 123
        subvolume_body = SubvolumeInfo(
            path=path,
            size=size
        )

        # create
        subvolume_info = self.client.subvolumes.begin_create(
            TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_1, subvolume_body).result()
        assert subvolume_info.name == ACCOUNT1 + "/" + TEST_POOL_1 + "/" + volumeName1 + "/" + TEST_SUBVOLUME_1
        assert subvolume_info.path == path

        # get metadata
        metadata = self.client.subvolumes.begin_get_metadata(
            TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_1).result()
        assert metadata is not None

        # clean up
        self.client.subvolumes.begin_delete(TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, TEST_SUBVOLUME_1).wait()
        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, live=self.is_live)
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, ACCOUNT1, live=self.is_live)
        if self.is_live:
            self.network_client.virtual_networks.begin_delete(TEST_RG, VNETNAME)
