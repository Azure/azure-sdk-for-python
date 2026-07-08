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
class TestResourceGraphOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ResourceGraphClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_operations_list(self, resource_group):
        response = self.client.operations.list()
        result = [r for r in response]
        assert len(result)
