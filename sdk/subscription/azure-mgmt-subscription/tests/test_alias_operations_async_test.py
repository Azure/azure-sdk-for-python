# coding=utf-8
import pytest
from azure.mgmt.subscription.aio import SubscriptionClient

from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    RandomNameResourceGroupPreparer,
)
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.live_test_only
class TestSubscriptionAliasOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(SubscriptionClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_alias_list(self, resource_group):
        response = self.client.alias.list()
        result = [r async for r in response]
        assert len(result) == 0
