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
# Examples Total  : 10
# Examples Tested : 10
# Coverage %      : 100
# ----------------------

#  route_filters: 6/6
#  route_filter_rules:  4/4
#  service_tags: 1/1
#  bgp_service_communities: 1/1

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
        ROUTE_FILTER_NAME = "myRouteFilter"
        RULE_NAME = "myRule"
        LOCATION = AZURE_LOCATION

        # /RouteFilters/put/RouteFilterCreate[put]
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "key1": "value1"
          },
          "rules": [
            # {
            #   "name": "ruleName",
            #   "properties": {
            #     "access": "Allow",
            #     "route_filter_rule_type": "Community",
            #     "communities": [
            #       "12076:5030",
            #       "12076:5040"
            #     ]
            #   }
            # }
          ]
        }
        result = self.mgmt_client.route_filters.begin_create_or_update(resource_group_name=RESOURCE_GROUP, route_filter_name=ROUTE_FILTER_NAME, route_filter_parameters=BODY)
        result = result.result()

        # /ServiceTags/get/Get list of service tags[get]
        result = self.mgmt_client.service_tags.list(location=LOCATION)

        # /BgpServiceCommunities/get/ServiceCommunityList[get]
        result = self.mgmt_client.bgp_service_communities.list()

        # /RouteFilterRules/put/RouteFilterRuleCreate[put]
        BODY = {
          "access": "Allow",
          "route_filter_rule_type": "Community",
          "communities": [
            # "12076:5030",
            "12076:51004"
            # "12076:5040"
          ]
        }
        result = self.mgmt_client.route_filter_rules.begin_create_or_update(resource_group_name=RESOURCE_GROUP, route_filter_name=ROUTE_FILTER_NAME, rule_name=RULE_NAME, route_filter_rule_parameters=BODY)
        result = result.result()

        # /RouteFilterRules/get/RouteFilterRuleGet[get]
        result = self.mgmt_client.route_filter_rules.get(resource_group_name=RESOURCE_GROUP, route_filter_name=ROUTE_FILTER_NAME, rule_name=RULE_NAME)

        # /RouteFilterRules/get/RouteFilterRuleListByRouteFilter[get]
        result = self.mgmt_client.route_filter_rules.list_by_route_filter(resource_group_name=RESOURCE_GROUP, route_filter_name=ROUTE_FILTER_NAME)

        # /RouteFilters/get/RouteFilterGet[get]
        result = self.mgmt_client.route_filters.get(resource_group_name=RESOURCE_GROUP, route_filter_name=ROUTE_FILTER_NAME)

        # /RouteFilters/get/RouteFilterListByResourceGroup[get]
        result = self.mgmt_client.route_filters.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /RouteFilters/get/RouteFilterList[get]
        result = self.mgmt_client.route_filters.list()

        # /RouteFilters/patch/Update route filter tags[patch]
        BODY = {
          "tags": {
            "key1": "value1"
          }
        }
        result = self.mgmt_client.route_filters.update_tags(resource_group_name=RESOURCE_GROUP, route_filter_name=ROUTE_FILTER_NAME, parameters=BODY)

        # /RouteFilterRules/delete/RouteFilterRuleDelete[delete]
        result = self.mgmt_client.route_filter_rules.begin_delete(resource_group_name=RESOURCE_GROUP, route_filter_name=ROUTE_FILTER_NAME, rule_name=RULE_NAME)
        result = result.result()

        # /RouteFilters/delete/RouteFilterDelete[delete]
        result = self.mgmt_client.route_filters.begin_delete(resource_group_name=RESOURCE_GROUP, route_filter_name=ROUTE_FILTER_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
