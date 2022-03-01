from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy
from setup import *
import azure.mgmt.netapp.models


class TestNetAppResourceQuota(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_list_resource_quota_limit(self):
        limits = self.client.net_app_resource_quota_limits.list(LOCATION)

        assert limits is not None
