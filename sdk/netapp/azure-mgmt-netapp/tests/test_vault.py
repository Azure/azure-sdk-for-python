from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from test_volume import create_volume, delete_volume, delete_pool, delete_account, create_virtual_network
from setup import *
import azure.mgmt.netapp.models


class TestNetAppVault(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)
        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(NetworkManagementClient) 

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_get_vault(self):
        set_bodiless_matcher()
        print("Starting test_get_vault...")
        ACCOUNT1 = self.get_resource_name(TEST_ACC_1+"-")
        volumeName1 = self.get_resource_name(TEST_VOL_1+"-")
        VNETNAME = self.get_resource_name(VNET+"-")
        if self.is_live:
            SUBNET = create_virtual_network(self.network_client, TEST_RG, LOCATION, VNETNAME, 'default')         
        volume = create_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, LOCATION, vnet=VNETNAME, live=self.is_live)
        vaults = self.client.vaults.list(TEST_RG, ACCOUNT1)
        assert len(list(vaults)) == 1

        # clean up
        delete_volume(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, volumeName1, live=self.is_live)
        delete_pool(self.client, TEST_RG, ACCOUNT1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, ACCOUNT1, live=self.is_live)
        if self.is_live:
            self.network_client.virtual_networks.begin_delete(TEST_RG, VNETNAME)

