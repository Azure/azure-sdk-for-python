# coding=utf-8
import pytest
from azure.mgmt.mongocluster import MongoClusterMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestMongoClusterMgmtReplicasOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(MongoClusterMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_replicas_list_by_parent(self, resource_group):
        response = self.client.replicas.list_by_parent(
            resource_group_name=resource_group.name,
            mongo_cluster_name="str",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...
