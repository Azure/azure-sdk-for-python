# coding=utf-8
import pytest
from azure.mgmt.healthdataaiservices.aio import HealthDataAIServicesMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestHealthDataAIServicesMgmtPrivateLinksOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(HealthDataAIServicesMgmtClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_private_links_list_by_deid_service(self, resource_group):
        response = self.client.private_links.list_by_deid_service(
            resource_group_name=resource_group.name,
            deid_service_name="str",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...
