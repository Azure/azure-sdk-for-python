# coding=utf-8
import pytest
from azure.mgmt.deviceregistry import DeviceRegistryMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDeviceRegistryMgmtBillingContainersOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(DeviceRegistryMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_billing_containers_get(self, resource_group):
        response = self.client.billing_containers.get(
            billing_container_name="str",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_billing_containers_list_by_subscription(self, resource_group):
        response = self.client.billing_containers.list_by_subscription()
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...
