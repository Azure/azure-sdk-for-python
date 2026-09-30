# coding=utf-8
import pytest
from azure.mgmt.resourcegraph.aio import ResourceGraphClient

from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    RandomNameResourceGroupPreparer,
)
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.live_test_only
class TestResourceGraphGraphQueryOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ResourceGraphClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_graph_query_list(self, resource_group):
        response = self.client.graph_query.list(
            resource_group_name=resource_group.name,
        )
        result = [r async for r in response]
        assert len(result) == 0

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_graph_query_list_by_subscription(self, resource_group):
        response = self.client.graph_query.list_by_subscription()
        result = [r async for r in response]
        assert len(result) >= 0
