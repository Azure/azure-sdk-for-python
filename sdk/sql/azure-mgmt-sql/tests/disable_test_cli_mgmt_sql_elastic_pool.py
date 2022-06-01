# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   ElasticPools: 6/7
#   ElasticPoolActivities: 0/1
#   ElasticPoolDatabaseActivities: 1/1
#   ElasticPoolOperations: 1/2
#   RecommendedElasticPools: 0/3

import unittest

import azure.mgmt.sql
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtSqlTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSqlTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.sql.SqlManagementClient
        )

    @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_recommended_elastic_pool(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        ELASTIC_POOL_NAME = "myelasticpool"
        RECOMMENDED_ELASTIC_POOL_NAME = ELASTIC_POOL_NAME

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /RecommendedElasticPools/get/List recommended elastic pools[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recommended_elastic_pools.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ElasticPools/put/Create or update elastic pool with minimum parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.elastic_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /RecommendedElasticPools/get/Get recommended elastic pool metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recommended_elastic_pools.list_metrics(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, recommended_elastic_pool_name=RECOMMENDED_ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /RecommendedElasticPools/get/Get a recommended elastic pool[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recommended_elastic_pools.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, recommended_elastic_pool_name=RECOMMENDED_ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /ElasticPools/delete/Delete an elastic pool[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()
        
    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_elastic_pool(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        ELASTIC_POOL_NAME = "myelasticpool"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ElasticPools/put/Create or update elastic pool with minimum parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.elastic_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ElasticPools/get/List database usage metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.list_metrics(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, filter="name/value eq 'cpu_percent' and timeGrain eq '00:10:00' and startTime eq '2017-06-02T18:35:00Z' and endTime eq '2017-06-02T18:55:00Z'")

#--------------------------------------------------------------------------
        # /ElasticPools/get/Get an elastic pool[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /ElasticPools/get/Get all elastic pools in a server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ElasticPoolActivities/get/List Elastic pool activity[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.elastic_pool_activities.list_by_elastic_pool(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /ElasticPoolOperations/get/List the elastic pool management operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pool_operations.list_by_elastic_pool(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /ElasticPoolOperations/post/Cancel the elastic pool management operation[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.elastic_pool_operations.cancel(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /ElasticPoolDatabaseActivities/get/List elastic pool database activity[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pool_database_activities.list_by_elastic_pool(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /ElasticPools/post/Failover an elastic pool[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.elastic_pools.begin_failover(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /ElasticPools/patch/Update an elastic pool with minimum parameters[patch]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.elastic_pools.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ElasticPools/delete/Delete an elastic pool[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()
