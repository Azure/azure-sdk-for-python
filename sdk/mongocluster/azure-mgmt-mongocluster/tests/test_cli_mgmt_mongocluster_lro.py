from azure.mgmt.mongocluster import MongoClusterMgmtClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'westus2'
Mongo_Cluster_Name = "pythontestmongocluster"

class TestMgmtMongoCluster(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(MongoClusterMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_mongo_clusters_mgmt(self, resource_group):
        response = self.client.mongo_clusters.begin_create_or_update(
            resource_group_name = resource_group.name,
            mongo_cluster_name = Mongo_Cluster_Name,
            resource = {
                "location": AZURE_LOCATION,
                "properties": {
                    "administratorLogin": "myMongoCluster",
                    "administratorLoginPassword": "myMongoCluster333",
                    "serverVersion": "5.0",
                    "nodeGroupSpecs": [
                        {
                            "diskSizeGB": 128,
                            "enableHa": True,
                            "kind": "Shard",
                            "nodeCount": 1,
                            "sku": "M30"
                        }
                    ],
                },
            }
        ).result()
        assert response

        response = self.client.mongo_clusters.begin_update(
            resource_group_name = resource_group.name,
            mongo_cluster_name = Mongo_Cluster_Name,
            properties = {
                "location": AZURE_LOCATION,
                "properties": {
                    "administratorLogin": "myMongoCluster",
                    "administratorLoginPassword": "myMongoCluster333",
                    "serverVersion": "5.0",
                    "nodeGroupSpecs": [
                        {
                            "kind": "Shard",
                            "sku": "M50",
                            "diskSizeGB": 256,
                            "enableHa": True,
                            "nodeCount": 1
                        }
                    ],
                    "publicNetworkAccess": "Enabled"
                },
            }
        ).result()
        assert response

        response = self.client.mongo_clusters.get(
            resource_group_name = resource_group.name,
            mongo_cluster_name = Mongo_Cluster_Name,
        )
        assert response

        response = self.client.mongo_clusters.list_by_resource_group(
            resource_group_name = resource_group.name,
        )
        assert len(list(response)) == 1

        response = self.client.mongo_clusters.begin_delete(
            resource_group_name = resource_group.name,
            mongo_cluster_name = Mongo_Cluster_Name,
        ).result()
