from devtools_testutils import AzureMgmtTestCase
from setup import *
import azure.mgmt.netapp.models

class NetAppAccountTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(NetAppAccountTestCase, self).setUp()
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    def test_list_resource_quota_limit(self):
        limits = self.client.net_app_resource_quota_limits.list(LOCATION)

        self.assertIsNotNone(limits)
