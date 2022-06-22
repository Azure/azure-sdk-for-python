from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy, set_bodiless_matcher
from test_volume import create_volume, delete_volume, delete_pool, delete_account
from setup import *
import azure.mgmt.netapp.models


class TestNetAppVault(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_get_vault(self):
        set_bodiless_matcher()
        create_volume(self.client)
        vaults = self.client.vaults.list(TEST_RG, TEST_ACC_1)
        assert len(list(vaults)) == 1

        # clean up
        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)
