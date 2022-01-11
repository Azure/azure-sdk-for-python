# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 10
# Methods Covered : 10
# Examples Total  : 11
# Examples Tested : 11
# Coverage %      : 100
# ----------------------

#  route_tables: 6/6
#  route: 4/4

import unittest

import azure.mgmt.network
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy
import pytest

AZURE_LOCATION = 'eastus'


@pytest.mark.live_test_only
class TestMgmtNetwork(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, resource_group):

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        ROUTE_TABLE_NAME = "myRouteTable"
        ROUTE_NAME = "myRoute"

        # /RouteTables/put/Create route table[put]
        BODY = {
          "location": "westus"
        }
        result = self.mgmt_client.route_tables.begin_create_or_update(resource_group_name=RESOURCE_GROUP, route_table_name=ROUTE_TABLE_NAME, parameters=BODY)
        result = result.result()

        # # /RouteTables/put/Create route table with route[put]
        # BODY = {
        #   "properties": {
        #     "disable_bgp_route_propagation": True,
        #     "routes": [
        #       {
        #         "name": "route1",
        #         "properties": {
        #           "address_prefix": "10.0.3.0/24",
        #           "next_hop_type": "VirtualNetworkGateway"
        #         }
        #       }
        #     ]
        #   },
        #   "location": "westus"
        # }
        # result = self.mgmt_client.route_tables.begin_create_or_update(resource_group_name=RESOURCE_GROUP, route_table_name=ROUTE_TABLE_NAME, parameters=BODY)
        # result = result.result()

        # /Routes/put/Create route[put]
        BODY = {
          "address_prefix": "10.0.3.0/24",
          "next_hop_type": "VirtualNetworkGateway"
        }
        result = self.mgmt_client.routes.begin_create_or_update(resource_group_name=RESOURCE_GROUP, route_table_name=ROUTE_TABLE_NAME, route_name=ROUTE_NAME, route_parameters=BODY)
        result = result.result()

        # /Routes/get/Get route[get]
        result = self.mgmt_client.routes.get(resource_group_name=RESOURCE_GROUP, route_table_name=ROUTE_TABLE_NAME, route_name=ROUTE_NAME)

        # /Routes/get/List routes[get]
        result = self.mgmt_client.routes.list(resource_group_name=RESOURCE_GROUP, route_table_name=ROUTE_TABLE_NAME)

        # /RouteTables/get/Get route table[get]
        result = self.mgmt_client.route_tables.get(resource_group_name=RESOURCE_GROUP, route_table_name=ROUTE_TABLE_NAME)

        # /RouteTables/get/List route tables in resource group[get]
        result = self.mgmt_client.route_tables.list(resource_group_name=RESOURCE_GROUP)

        # /RouteTables/get/List all route tables[get]
        result = self.mgmt_client.route_tables.list_all()

        # /RouteTables/patch/Update route table tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.route_tables.update_tags(resource_group_name=RESOURCE_GROUP, route_table_name=ROUTE_TABLE_NAME, parameters=BODY)

        # /Routes/delete/Delete route[delete]
        result = self.mgmt_client.routes.begin_delete(resource_group_name=RESOURCE_GROUP, route_table_name=ROUTE_TABLE_NAME, route_name=ROUTE_NAME)
        result = result.result()

        # /RouteTables/delete/Delete route table[delete]
        result = self.mgmt_client.route_tables.begin_delete(resource_group_name=RESOURCE_GROUP, route_table_name=ROUTE_TABLE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
