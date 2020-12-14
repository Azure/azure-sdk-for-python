# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 34
# Methods Covered : 34
# Examples Total  : 34
# Examples Tested : 34
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.kusto
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'
CLUSTER_NAME = 'MyClusterNameXarqRnd'
DATABASE_NAME = 'MyDatabase'
NAMESPACE_NAME = 'MyNameSpaceRnd'
EVENTHUB_NAME = 'myeventhub'
DATA_CONNECTION_NAME = 'DataConnections8xab'
ATTACHED_DATABASE_CONFIGURATION_NAME = 'MyAttachedDatabaseConfiguration'

class MgmtKustoTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtKustoTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.kusto.KustoManagementClient
        )
    
    @unittest.skip("unavailable in track2")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_kusto_adjusted(self, resource_group):

        # KustoClustersCreateOrUpdate[put]
        BODY = {
          "location": "westus",
          "sku": {
            "name": "Standard_L8s",
            "capacity": "2",
            "tier": "Standard"
          },
          "identity": {
            "type": "SystemAssigned"
          },
          "enable_streaming_ingest": True #,
          #"key_vault_properties": {
          #  "key_vault_uri": "https://dummy.keyvault.com",
          #  "key_name": "keyName",
          #  "key_version": "keyVersion"
          #}
        }
        result = self.mgmt_client.clusters.create_or_update(resource_group.name, CLUSTER_NAME, BODY)
        result = result.result()

        # KustoDatabasesCreateOrUpdate[put]
        BODY = {
          "location": "westus",
          "soft_delete_period": "P1D",
          "kind": "ReadWrite"
        }
        result = self.mgmt_client.databases.create_or_update(resource_group.name, CLUSTER_NAME, DATABASE_NAME, BODY)
        result = result.result()

        # KustoDataConnectionsCreateOrUpdate[put]
        #BODY = {
        #  "location": "westus",
        #  "kind": "EventHub",
        #  "event_hub_resource_id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + "zimsrg" + "/providers/Microsoft.EventHub/namespaces/" + NAMESPACE_NAME + "/eventhubs/" + EVENTHUB_NAME + "",
        #  "consumer_group": "testConsumerGroup1"
        #}
        #result = self.mgmt_client.data_connections.create_or_update(resource_group.name, CLUSTER_NAME, DATABASE_NAME, DATA_CONNECTION_NAME, BODY)
        #result = result.result()

        # AttachedDatabaseConfigurationsCreateOrUpdate[put]
        # BODY = {
        #  "location": "westus",
        #  "cluster_resource_id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.Kusto/Clusters/" + CLUSTER_NAME + "",
        #  "database_name": "db1",
        #  "default_principals_modification_kind": "Union"
        #}
        #result = self.mgmt_client.attached_database_configurations.create_or_update(resource_group.name, CLUSTER_NAME, ATTACHED_DATABASE_CONFIGURATION_NAME, BODY)
        #result = result.result()

        # AttachedDatabaseConfigurationsGet[get]
        #result = self.mgmt_client.attached_database_configurations.get(resource_group.name, CLUSTER_NAME, ATTACHED_DATABASE_CONFIGURATION_NAME)

        # KustoDataConnectionsGet[get]
        #result = self.mgmt_client.data_connections.get(resource_group.name, CLUSTER_NAME, DATABASE_NAME, DATA_CONNECTION_NAME)

        # KustoDatabasesListByCluster[get]
        result = self.mgmt_client.databases.list_by_cluster(resource_group.name, CLUSTER_NAME)

        # KustoAttachedDatabaseConfigurationsListByCluster[get]
        result = self.mgmt_client.attached_database_configurations.list_by_cluster(resource_group.name, CLUSTER_NAME)

        # KustoDatabasesGet[get]
        result = self.mgmt_client.databases.get(resource_group.name, CLUSTER_NAME, DATABASE_NAME)

        # KustoDatabasesListByCluster[get]
        result = self.mgmt_client.databases.list_by_cluster(resource_group.name, CLUSTER_NAME)

        # KustoClustersListResourceSkus[get]
        result = self.mgmt_client.clusters.list_skus_by_resource(resource_group.name, CLUSTER_NAME)

        # KustoClustersGet[get]
        result = self.mgmt_client.clusters.get(resource_group.name, CLUSTER_NAME)

        # KustoClustersListByResourceGroup[get]
        result = self.mgmt_client.clusters.list_by_resource_group(resource_group.name)

        # KustoClustersList[get]
        result = self.mgmt_client.clusters.list()

        # KustoClustersListSkus[get]
        result = self.mgmt_client.clusters.list_skus()

        # KustoOperationsList[get]
        result = self.mgmt_client.operations.list()

        # KustoDataConnectionsUpdate[patch]
        #BODY = {
        #  "location": "westus",
        #  "kind": "EventHub",
        #  "event_hub_resource_id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.EventHub/namespaces/" + NAMESPACE_NAME + "/eventhubs/" + EVENTHUB_NAME + "",
        #  "consumer_group": "testConsumerGroup1"
        #}
        #result = self.mgmt_client.data_connections.update(resource_group.name, CLUSTER_NAME, DATABASE_NAME, DATA_CONNECTION_NAME, BODY)
        #result = result.result()

        # KustoDataConnectionValidation[post]
        #BODY = {
        #  "data_connection_name": "DataConnections8",
        #  "kind": "EventHub",
        #  "event_hub_resource_id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.EventHub/namespaces/" + NAMESPACE_NAME + "/eventhubs/" + EVENTHUB_NAME + "",
        #  "consumer_group": "testConsumerGroup1"
        #}
        #result = self.mgmt_client.data_connections.data_connection_validation_method(resource_group.name, CLUSTER_NAME, DATABASE_NAME, "abc", BODY)

        # KustoDataConnectionsCheckNameAvailability[post]
        # BODY = {
        #  "name": "DataConnections8",
        #  "type": "Microsoft.Kusto/clusters/databases/dataConnections"
        #}
        result = self.mgmt_client.data_connections.check_name_availability(resource_group.name, CLUSTER_NAME, DATABASE_NAME, "abc")

        # KustoDatabaseRemovePrincipals[post]
        #BODY = {
        #  "value": [
        #    {
        #      "name": "Some User",
        #      "role": "Admin",
        #      "type": "User",
        #      "fqn": "aaduser=some_guid",
        #      "email": "user@microsoft.com",
        #      "app_id": ""
        #    },
        #    {
        #      "name": "Kusto",
        #      "role": "Viewer",
        #      "type": "Group",
        #      "fqn": "aadgroup=some_guid",
        #      "email": "kusto@microsoft.com",
        #      "app_id": ""
        #    },
        #    {
        #      "name": "SomeApp",
        #      "role": "Admin",
        #      "type": "App",
        #      "fqn": "aadapp=some_guid_app_id",
        #      "email": "",
        #      "app_id": "some_guid_app_id"
        #    }
        #  ]
        #}
        #result = self.mgmt_client.databases.remove_principals(resource_group.name, CLUSTER_NAME, DATABASE_NAME, "abc", BODY)

        # KustoDatabaseListPrincipals[post]
        result = self.mgmt_client.databases.list_principals(resource_group.name, CLUSTER_NAME, DATABASE_NAME)

        # KustoDatabaseAddPrincipals[post]
        #BODY = {
        #  "value": [
        #    {
        #      "name": "Some User",
        #      "role": "Admin",
        #      "type": "User",
        #      "fqn": "aaduser=some_guid",
        #      "email": "user@microsoft.com",
        #      "app_id": ""
        #    },
        #    {
        #      "name": "Kusto",
        #      "role": "Viewer",
        #      "type": "Group",
        #      "fqn": "aadgroup=some_guid",
        #      "email": "kusto@microsoft.com",
        #      "app_id": ""
        #    },
        #    {
        #      "name": "SomeApp",
        #      "role": "Admin",
        #      "type": "App",
        #      "fqn": "aadapp=some_guid_app_id",
        #      "email": "",
        #      "app_id": "some_guid_app_id"
        #    }
        #  ]
        #}
        #result = self.mgmt_client.databases.add_principals(resource_group.name, CLUSTER_NAME, DATABASE_NAME, "abc", BODY)

        # KustoDatabasesUpdate[patch]
        #BODY = {
        #  "properties": {
        #    "soft_delete_period": "P1D"
        #  }
        #}
        #result = self.mgmt_client.databases.update(resource_group.name, CLUSTER_NAME, DATABASE_NAME, BODY)
        #result = result.result()

        # KustoClusterDetachFollowerDatabases[post]
        #BODY = {
        #  "cluster_resource_id": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.Kusto/clusters/" + CLUSTER_NAME + "",
        #  "attached_database_configuration_name": "myAttachedDatabaseConfiguration"
        #}
        #result = self.mgmt_client.clusters.detach_follower_databases(resource_group.name, CLUSTER_NAME, "abc", BODY)
        #result = result.result()

        # KustoDatabaseCheckNameAvailability[post]
        #BODY = {
        #  "name": "kuskus",
        #  "type": "Microsoft.Kusto/clusters/databases"
        #}
        #result = self.mgmt_client.databases.check_name_availability(resource_group.name, CLUSTER_NAME, BODY)

        # KustoClusterListFollowerDatabases[post]
        BODY = {}
        result = self.mgmt_client.clusters.list_follower_databases(resource_group.name, CLUSTER_NAME)

        # KustoClustersStart[post]
        result = self.mgmt_client.clusters.start(resource_group.name, CLUSTER_NAME)
        result = result.result()

        # KustoClustersStop[post]
        result = self.mgmt_client.clusters.stop(resource_group.name, CLUSTER_NAME)
        result = result.result()

        # KustoClustersUpdate[patch]
        #BODY = {
        #  "location": "westus",
        #  "key_vault_properties": {
        #    "key_vault_uri": "https://dummy.keyvault.com",
        #    "key_name": "keyName",
        #    "key_version": "keyVersion"
        #  }
        #}
        #result = self.mgmt_client.clusters.update(resource_group.name, CLUSTER_NAME, BODY)
        #result = result.result()

        # KustoClustersCheckNameAvailability[post]
        #BODY = {
        #  "name": "kuskusprod",
        #  "type": "Microsoft.Kusto/clusters"
        #}
        #result = self.mgmt_client.clusters.check_name_availability(LOCATION_NAME, "abc", BODY)

        # AttachedDatabaseConfigurationsDelete[delete]
        # result = self.mgmt_client.attached_database_configurations.delete(resource_group.name, CLUSTER_NAME, ATTACHED_DATABASE_CONFIGURATION_NAME)
        # result = result.result()

        # KustoDataConnectionsDelete[delete]
        # result = self.mgmt_client.data_connections.delete(resource_group.name, CLUSTER_NAME, DATABASE_NAME, DATA_CONNECTION_NAME)
        # result = result.result()

        # KustoDatabasesDelete[delete]
        #result = self.mgmt_client.databases.delete(resource_group.name, CLUSTER_NAME, DATABASE_NAME)
        #result = result.result()

        # KustoClustersDelete[delete]
        #result = self.mgmt_client.clusters.delete(resource_group.name, CLUSTER_NAME)
        #result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()