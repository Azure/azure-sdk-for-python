# coding=utf-8
import pytest
from azure.mgmt.subscription import SubscriptionClient

from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    RandomNameResourceGroupPreparer,
    recorded_by_proxy,
)

AZURE_LOCATION = "eastus"


@pytest.mark.live_test_only
class TestSubscriptionSubscriptionPolicyOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(SubscriptionClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_subscription_policy_list_policy_for_tenant(self, resource_group):
        response = self.client.subscription_policy.list_policy_for_tenant()
        result = [r for r in response]
        assert len(result)
