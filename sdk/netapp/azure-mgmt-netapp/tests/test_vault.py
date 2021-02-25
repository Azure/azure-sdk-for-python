from devtools_testutils import AzureMgmtTestCase
from test_volume import create_volume, delete_volume, delete_pool, delete_account
from setup import *
import azure.mgmt.netapp.models

CBS_LOCATION = 'eastus2euap'
CBS_RESOURCE_GROUP = 'vault_python_sdk_test_2'
CBS_VNET = 'bprgpythonsdktest1vnet464'
CBS_ACCOUNT = 'sdk-py-tests-cbs-acc'

class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.AzureNetAppFilesManagementClient)

    def test_get_vault(self):
        create_volume(self.client, CBS_RESOURCE_GROUP, CBS_ACCOUNT, TEST_POOL_1, TEST_VOL_1, location=CBS_LOCATION,
                      vnet=CBS_VNET)
        vaults = self.client.vaults.list(CBS_RESOURCE_GROUP, CBS_ACCOUNT)
        self.assertEqual(len(list(vaults)), 1)

        # clean up
        delete_volume(self.client, CBS_RESOURCE_GROUP, CBS_ACCOUNT, TEST_POOL_1, TEST_VOL_1, live=self.is_live)
        delete_pool(self.client, CBS_RESOURCE_GROUP, CBS_ACCOUNT, TEST_POOL_1, live=self.is_live)
        delete_account(self.client, CBS_RESOURCE_GROUP, CBS_ACCOUNT, live=self.is_live)
