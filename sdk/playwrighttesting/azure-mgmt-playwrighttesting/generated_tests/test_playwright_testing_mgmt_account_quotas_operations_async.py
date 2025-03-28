# coding=utf-8
import pytest
from azure.mgmt.playwrighttesting.aio import PlaywrightTestingMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestPlaywrightTestingMgmtAccountQuotasOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(PlaywrightTestingMgmtClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_account_quotas_get(self, resource_group):
        response = await self.client.account_quotas.get(
            resource_group_name=resource_group.name,
            account_name="str",
            quota_name="str",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_account_quotas_list_by_account(self, resource_group):
        response = self.client.account_quotas.list_by_account(
            resource_group_name=resource_group.name,
            account_name="str",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...
