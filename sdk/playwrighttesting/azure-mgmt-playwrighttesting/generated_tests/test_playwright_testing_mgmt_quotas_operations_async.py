# coding=utf-8
import pytest
from azure.mgmt.playwrighttesting.aio import PlaywrightTestingMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestPlaywrightTestingMgmtQuotasOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(PlaywrightTestingMgmtClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_quotas_get(self, resource_group):
        response = await self.client.quotas.get(
            location="str",
            quota_name="str",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_quotas_list_by_subscription(self, resource_group):
        response = self.client.quotas.list_by_subscription(
            location="str",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...
