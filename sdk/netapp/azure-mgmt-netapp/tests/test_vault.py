from devtools_testutils import AzureMgmtTestCase
from test_volume import create_volume
from setup import *
import azure.mgmt.netapp.models

CBS_LOCATION = 'eastus2euap'
CBS_RESOURCE_GROUP = 'vault_python_sdk_test'
CBS_VNET = 'bprgpythonsdktestvnet464'

class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.AzureNetAppFilesManagementClient)

    def test_get_vault(self):
        create_volume(self.client, CBS_RESOURCE_GROUP, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1, location=CBS_LOCATION,
                      vnet=CBS_VNET)
        vaults = self.client.vaults.list(CBS_RESOURCE_GROUP, TEST_ACC_1)
        self.assertEqual(len(list(vaults)), 1)
