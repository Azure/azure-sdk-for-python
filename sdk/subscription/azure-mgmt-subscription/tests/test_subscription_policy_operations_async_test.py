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
class TestSubscriptionSubscriptionPolicyOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(SubscriptionClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_subscription_policy_list_policy_for_tenant(self, resource_group):
        response = self.client.subscription_policy.list_policy_for_tenant()
        result = [r async for r in response]
        assert len(result)
