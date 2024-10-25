from azure.mgmt.mongocluster import MongoClusterMgmtClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy
import pytest

AZURE_LOCATION = "westus2"
Mongo_Cluster_Name = "pythonmongoclustertest"

@pytest.mark.live_test_only
class TestMgmtMongoCluster(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(MongoClusterMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_mongo_clusters_mgmt(self, resource_group):
        response = self.client.mongo_clusters.begin_create_or_update(
            resource_group_name=resource_group.name,
            mongo_cluster_name=Mongo_Cluster_Name,
            resource={
                "location": AZURE_LOCATION,
                "properties": {
                    "administrator": {"password": "mongoAdmin3", "userName": "mongoAdmin"},
                    "compute": {"tier": "M30"},
                    "highAvailability": {"targetMode": "Disabled"},
                    "serverVersion": "5.0",
                    "sharding": {"shardCount": 1},
                    "storage": {"sizeGb": 128},
                },
            },
        ).result()
        assert response

        response = self.client.mongo_clusters.begin_update(
            resource_group_name=resource_group.name,
            mongo_cluster_name=Mongo_Cluster_Name,
            properties={
                "location": AZURE_LOCATION,
                "properties": {
                    "administrator": {"userName": "mongoAdmin"},
                    "compute": {"tier": "M50"},
                    "highAvailability": {"targetMode": "Disabled"},
                    "previewFeatures": [],
                    "publicNetworkAccess": "Enabled",
                    "serverVersion": "5.0",
                    "storage": {"sizeGb": 256},
                },
            },
        ).result()
        assert response

        response = self.client.mongo_clusters.get(
            resource_group_name=resource_group.name,
            mongo_cluster_name=Mongo_Cluster_Name,
        )
        assert response

        response = self.client.mongo_clusters.list_by_resource_group(
            resource_group_name=resource_group.name,
        )
        assert len(list(response)) == 1

        response = self.client.mongo_clusters.begin_delete(
            resource_group_name=resource_group.name,
            mongo_cluster_name=Mongo_Cluster_Name,
        ).result()