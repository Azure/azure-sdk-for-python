# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 9
# Methods Covered : 9
# Examples Total  : 12
# Examples Tested : 12
# Coverage %      : 100
# ----------------------

#  firewall_policies: 5/5
#  firewall_policy_rule_groups:  4/4

import unittest
import pytest

import azure.mgmt.network
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

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
        FIREWALL_POLICY_NAME = "myFirewallPolicy"
        RULE_GROUP_NAME = "myRuleGroup"

        # /FirewallPolicies/put/Create FirewallPolicy[put]
        BODY = {
          "tags": {
            "key1": "value1"
          },
          "location": "West US",
          "threat_intel_mode": "Alert"
        }
        result = self.mgmt_client.firewall_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, firewall_policy_name=FIREWALL_POLICY_NAME, parameters=BODY)
        result = result.result()

        # # /FirewallPolicyRuleGroups/put/Create FirewallPolicyRuleGroup With IpGroups[put]
        # BODY = {
        #   "priority": "110",
        #   "rules": [
        #     {
        #       "rule_type": "FirewallPolicyFilterRule",
        #       "name": "Example-Filter-Rule",
        #       "action": {
        #         "type": "Deny"
        #       },
        #       "rule_conditions": [
        #         {
        #           "rule_condition_type": "NetworkRuleCondition",
        #           "name": "network-condition1",
        #           "ip_protocols": [
        #             "TCP"
        #           ],
        #           "destination_ports": [
        #             "*"
        #           ],
        #           "source_ip_groups": [
        #             "/subscriptions/subid/providers/Microsoft.Network/resourceGroup/rg1/ipGroups/ipGroups1"
        #           ],
        #           "destination_ip_groups": [
        #             "/subscriptions/subid/providers/Microsoft.Network/resourceGroup/rg1/ipGroups/ipGroups2"
        #           ]
        #         }
        #       ]
        #     }
        #   ]
        # }
        # result = self.mgmt_client.firewall_policy_rule_groups.create_or_update(resource_group_name=RESOURCE_GROUP, firewall_policy_name=FIREWALL_POLICY_NAME, rule_group_name=RULE_GROUP_NAME, parameters=BODY)
        # result = result.result()

        # /FirewallPolicyRuleGroups/put/Create FirewallPolicyRuleGroup[put]
        BODY = {
          "priority": "110",
          "rules": [
            {
              "rule_type": "FirewallPolicyFilterRule",
              "name": "Example-Filter-Rule",
              "action": {
                "type": "Deny"
              },
              "rule_conditions": [
                {
                  "rule_condition_type": "NetworkRuleCondition",
                  "name": "network-condition1",
                  "source_addresses": [
                    "10.1.25.0/24"
                  ],
                  "destination_addresses": [
                    "*"
                  ],
                  "ip_protocols": [
                    "TCP"
                  ],
                  "destination_ports": [
                    "*"
                  ]
                }
              ]
            }
          ]
        }
        result = self.mgmt_client.firewall_policy_rule_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, firewall_policy_name=FIREWALL_POLICY_NAME, rule_group_name=RULE_GROUP_NAME, parameters=BODY)
        result = result.result()

        # /FirewallPolicyRuleGroups/get/Get FirewallPolicyRuleGroup With IpGroups[get]
        # result = self.mgmt_client.firewall_policy_rule_groups.get(resource_group_name=RESOURCE_GROUP, firewall_policy_name=FIREWALL_POLICY_NAME, rule_group_name=RULE_GROUP_NAME)

        # /FirewallPolicyRuleGroups/get/Get FirewallPolicyRuleGroup[get]
        result = self.mgmt_client.firewall_policy_rule_groups.get(resource_group_name=RESOURCE_GROUP, firewall_policy_name=FIREWALL_POLICY_NAME, rule_group_name=RULE_GROUP_NAME)

        # /FirewallPolicyRuleGroups/get/List all FirewallPolicyRuleGroups with IpGroups for a given FirewallPolicy[get]
        # result = self.mgmt_client.firewall_policy_rule_groups.list(resource_group_name=RESOURCE_GROUP, firewall_policy_name=FIREWALL_POLICY_NAME)

        # /FirewallPolicyRuleGroups/get/List all FirewallPolicyRuleGroups for a given FirewallPolicy[get]
        result = self.mgmt_client.firewall_policy_rule_groups.list(resource_group_name=RESOURCE_GROUP, firewall_policy_name=FIREWALL_POLICY_NAME)

        # /FirewallPolicies/get/Get FirewallPolicy[get]
        result = self.mgmt_client.firewall_policies.get(resource_group_name=RESOURCE_GROUP, firewall_policy_name=FIREWALL_POLICY_NAME)

        # /FirewallPolicies/get/List all Firewall Policies for a given resource group[get]
        result = self.mgmt_client.firewall_policies.list(resource_group_name=RESOURCE_GROUP)

        # /FirewallPolicies/get/List all Firewall Policies for a given subscription[get]
        result = self.mgmt_client.firewall_policies.list_all()

        # /FirewallPolicyRuleGroups/delete/Delete FirewallPolicyRuleGroup[delete]
        result = self.mgmt_client.firewall_policy_rule_groups.begin_delete(resource_group_name=RESOURCE_GROUP, firewall_policy_name=FIREWALL_POLICY_NAME, rule_group_name=RULE_GROUP_NAME)
        result = result.result()

        # /FirewallPolicies/delete/Delete Firewall Policy[delete]
        result = self.mgmt_client.firewall_policies.begin_delete(resource_group_name=RESOURCE_GROUP, firewall_policy_name=FIREWALL_POLICY_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
