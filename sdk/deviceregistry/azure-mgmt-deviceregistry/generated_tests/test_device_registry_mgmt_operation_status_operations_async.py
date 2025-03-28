# coding=utf-8
import pytest
from azure.mgmt.deviceregistry.aio import DeviceRegistryMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestDeviceRegistryMgmtOperationStatusOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(DeviceRegistryMgmtClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_operation_status_get(self, resource_group):
        response = await self.client.operation_status.get(
            location="str",
            operation_id="str",
        )

        # please add some check logic here by yourself
        # ...
