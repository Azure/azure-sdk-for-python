# coding=utf-8
import pytest
from azure.mgmt.resourcegraph import ResourceGraphClient

from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    RandomNameResourceGroupPreparer,
    recorded_by_proxy,
)

AZURE_LOCATION = "eastus"


@pytest.mark.live_test_only
class TestResourceGraphGraphQueryOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ResourceGraphClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_graph_query_list(self, resource_group):
        response = self.client.graph_query.list(
            resource_group_name=resource_group.name,
        )
        result = [r for r in response]
        assert len(result) == 0

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_graph_query_list_by_subscription(self, resource_group):
        response = self.client.graph_query.list_by_subscription()
        result = [r for r in response]
        assert len(result) >= 0
