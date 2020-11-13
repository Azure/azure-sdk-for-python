from devtools_testutils import AzureMgmtTestCase
from test_volume import create_volume
from setup import *
import azure.mgmt.netapp.models


class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.AzureNetAppFilesManagementClient)

    def test_get_vault(self):
        create_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        vaults = self.client.vaults.list(TEST_RG, TEST_ACC_1)
        self.assertEqual(len(list(vaults)), 1)
