# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 5
# Methods Covered : 5
# Examples Total  : 5
# Examples Tested : 5
# Coverage %      : 100
# ----------------------

#  web_application_firewall_policies: /5

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
    def test_network(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        POLICY_NAME = "myPolicy"

        # /WebApplicationFirewallPolicies/put/Creates or updates a WAF policy within a resource group[put]
        BODY = {
          "location": "WestUs",
          "managed_rules": {
            "managed_rule_sets": [
              {
                "rule_set_type": "OWASP",
                "rule_set_version": "3.0"
              }
            ]
          },
          "custom_rules": [
            # {
            #   "name": "Rule1",
            #   "priority": "1",
            #   "rule_type": "MatchRule",
            #   "action": "Block",
            #   "match_conditions": [
            #     {
            #       "match_variables": [
            #         {
            #           "variable_name": "RemoteAddr"
            #         }
            #       ],
            #       "operator": "IPMatch",
            #       "match_values": [
            #         "192.168.1.0/24",
            #         "10.0.0.0/24"
            #       ]
            #     }
            #   ]
            # },
            # {
            #   "name": "Rule2",
            #   "priority": "2",
            #   "rule_type": "MatchRule",
            #   "match_conditions": [
            #     {
            #       "match_variables": [
            #         {
            #           "variable_name": "RemoteAddr"
            #         }
            #       ],
            #       "operator": "IPMatch",
            #       "match_values": [
            #         "192.168.1.0/24"
            #       ]
            #     },
            #     {
            #       "match_variables": [
            #         {
            #           "variable_name": "RequestHeaders",
            #           "selector": "UserAgent"
            #         }
            #       ],
            #       "operator": "Contains",
            #       "match_values": [
            #         "Windows"
            #       ]
            #     }
            #   ],
            #   "action": "Block"
            # }
          ]
        }
        result = self.mgmt_client.web_application_firewall_policies.create_or_update(resource_group_name=RESOURCE_GROUP, policy_name=POLICY_NAME, parameters=BODY)

        # /WebApplicationFirewallPolicies/get/Gets a WAF policy within a resource group[get]
        result = self.mgmt_client.web_application_firewall_policies.get(resource_group_name=RESOURCE_GROUP, policy_name=POLICY_NAME)

        # /WebApplicationFirewallPolicies/get/Lists all WAF policies in a resource group[get]
        result = self.mgmt_client.web_application_firewall_policies.list(resource_group_name=RESOURCE_GROUP)

        # /WebApplicationFirewallPolicies/get/Lists all WAF policies in a subscription[get]
        result = self.mgmt_client.web_application_firewall_policies.list_all()

        # /WebApplicationFirewallPolicies/delete/Deletes a WAF policy within a resource group[delete]
        result = self.mgmt_client.web_application_firewall_policies.begin_delete(resource_group_name=RESOURCE_GROUP, policy_name=POLICY_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
