from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase
from test_volume import create_volume, delete_volume
from test_pool import delete_pool
from test_account import delete_account
from setup import *
import azure.mgmt.netapp.models
import json

class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.AzureNetAppFilesManagementClient)

    def test_list_mount_target(self):
        volume = create_volume(self. client,TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        self.assertEqual(volume.name, TEST_ACC_1 + '/' + TEST_POOL_1 + '/' + TEST_VOL_1)

        mount_target_list = self.client.mount_targets.list(
            TEST_RG,
            TEST_ACC_1,
            TEST_POOL_1,
            TEST_VOL_1
        )
        self.assertEqual(len(list(mount_target_list)), 1)

        delete_volume(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1, TEST_VOL_1)
        delete_pool(self.client, TEST_RG, TEST_ACC_1, TEST_POOL_1)
        delete_account(self.client, TEST_RG, TEST_ACC_1)

