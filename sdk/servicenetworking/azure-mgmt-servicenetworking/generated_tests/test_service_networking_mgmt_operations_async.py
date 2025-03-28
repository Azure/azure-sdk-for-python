# coding=utf-8
import pytest
from azure.mgmt.servicenetworking.aio import ServiceNetworkingMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestServiceNetworkingMgmtOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ServiceNetworkingMgmtClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_operations_list(self, resource_group):
        response = self.client.operations.list()
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...
