from devtools_testutils import AzureMgmtTestCase
from test_volume import create_volume, delete_volume, delete_pool, delete_account
from setup import *
import azure.mgmt.netapp.models


class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    def test_get_vault(self):
        create_volume(self.client)
        vaults = self.client.vaults.list(TEST_RG, TEST_ACC_1)
        self.assertEqual(len(list(vaults)), 1)

        # clean up
        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, TEST_RG, TEST_ACC_1, live=self.is_live)
