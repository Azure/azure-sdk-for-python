from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy
import setup
import azure.mgmt.netapp.models


class TestNetAppResourceOperations(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(azure.mgmt.netapp.NetAppManagementClient)

    # Before tests are run live a resource group needs to be created along with vnet and subnet
    # Note that when tests are run in live mode it is best to run one test at a time.
    @recorded_by_proxy
    def test_query_network_sibling_set(self):

        print("Starting test_query_network_sibling_set")
        try:
            self.client.net_app_resource.query_network_sibling_set(
                setup.LOCATION,
                "9760acf5-4638-11e7-9bdb-020073ca3333",
                "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sdk-python-tests-rg-tmp/providers/Microsoft.Network/virtualNetworks/testVnet/subnets/sdk-python-tests-subnet",
            )
        except Exception as e:
            assert str(e).startswith("(NoNicsFoundForSubnet)")
        print("Finished with test_query_network_sibling_set")

    @recorded_by_proxy
    def test_begin_update_network_sibling_set(self):

        print("Starting test_begin_update_network_sibling_set")
        try:
            self.client.net_app_resource.begin_update_network_sibling_set(
                setup.LOCATION,
                "9760acf5-4638-11e7-9bdb-020073ca3333",
                "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sdk-python-tests-rg-tmp/providers/Microsoft.Network/virtualNetworks/testVnet/subnets/sdk-python-tests-subnet",
                "herpiderp",
                "Standard",
            )
        except Exception as e:
            assert str(e).startswith("(NetworkSiblingSetChanged)")
        print("Finished with test_begin_update_network_sibling_set")
