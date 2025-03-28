# coding=utf-8
import pytest
from azure.mgmt.mongocluster.aio import MongoClusterMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestMongoClusterMgmtReplicasOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(MongoClusterMgmtClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_replicas_list_by_parent(self, resource_group):
        response = self.client.replicas.list_by_parent(
            resource_group_name=resource_group.name,
            mongo_cluster_name="str",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...
