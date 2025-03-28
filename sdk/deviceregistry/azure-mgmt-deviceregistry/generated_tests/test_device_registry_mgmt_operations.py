# coding=utf-8
import pytest
from azure.mgmt.deviceregistry import DeviceRegistryMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDeviceRegistryMgmtOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(DeviceRegistryMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_operations_list(self, resource_group):
        response = self.client.operations.list()
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...
