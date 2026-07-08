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
class TestSubscriptionAliasOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(SubscriptionClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_alias_list(self, resource_group):
        response = self.client.alias.list()
        result = [r for r in response]
        assert len(result) == 0
