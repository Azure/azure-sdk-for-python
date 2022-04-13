# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 23
# Methods Covered : 22
# Examples Total  : 22
# Examples Tested : 21
# Coverage %      : 91
# ----------------------

import unittest

import azure.mgmt.alertsmanagement
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtAlertsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAlertsTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.alertsmanagement.AlertsManagementClient
        )
    
    @unittest.skip("skip")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_alertsmanagement(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        ALERT_ID = "myAlertId"
        SMART_GROUP_ID = "mySmartGroupId"
        ACTION_RULE_NAME = "myActionRule"
        ALERT_RULE_NAME = "myAlertRule"

        # /ActionRules/put/PutActionRule[put]
        BODY = {
          "location": "Global",
          "properties": {
            "scope": {
              "scope_type": "ResourceGroup",
              "values": [
                "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP
              ]
            },
            "conditions": {
              "severity": {
                "operator": "Equals",
                "values": [
                  "Sev0",
                  "Sev2"
                ]
              },
              "monitor_service": {
                "operator": "Equals",
                "values": [
                  "Platform",
                  "Application Insights"
                ]
              },
              "monitor_condition": {
                "operator": "Equals",
                "values": [
                  "Fired"
                ]
              },
              "target_resource_type": {
                "operator": "NotEquals",
                "values": [
                  "Microsoft.Compute/VirtualMachines"
                ]
              }
            },
            "type": "Suppression",
            "suppression_config": {
              "recurrence_type": "Daily",
              "schedule": {
                "start_date": "12/09/2018",
                "end_date": "12/18/2018",
                "start_time": "06:00:00",
                "end_time": "14:00:00"
              }
            },
            "description": "Action rule on resource group for daily suppression",
            "status": "Enabled"
          }
        }
        result = self.mgmt_client.action_rules.create_update(resource_group_name=RESOURCE_GROUP, action_rule_name=ACTION_RULE_NAME, action_rule=BODY)

        # /SmartDetectorAlertRules/put/Create or update a Smart Detector alert rule[put]
        BODY = {
          "description": "Sample smart detector alert rule description",
          "state": "Enabled",
          "severity": "Sev3",
          "frequency": "PT5M",
          "detector": {
            "id": "VMMemoryLeak"
          },
          "scope": [
            "/subscriptions/b368ca2f-e298-46b7-b0ab-012281956afa/resourceGroups/MyVms/providers/Microsoft.Compute/virtualMachines/vm1"
          ],
          "action_groups": {
            "custom_email_subject": "My custom email subject",
            "custom_webhook_payload": "{\"AlertRuleName\":\"#alertrulename\"}",
            "group_ids": [
              "/subscriptions/b368ca2f-e298-46b7-b0ab-012281956afa/resourcegroups/actionGroups/providers/microsoft.insights/actiongroups/MyActionGroup"
            ]
          },
          "throttling": {
            "duration": "PT20M"
          }
        }
        # result = self.mgmt_client.smart_detector_alert_rules.create_or_update(resource_group_name=RESOURCE_GROUP, alert_rule_name=ALERT_RULE_NAME, parameters=BODY)

        # /SmartDetectorAlertRules/get/Get a Smart Detector alert rule[get]
        # result = self.mgmt_client.smart_detector_alert_rules.get(resource_group_name=RESOURCE_GROUP, alert_rule_name=ALERT_RULE_NAME)

        # /ActionRules/get/GetActionRuleById[get]
        result = self.mgmt_client.action_rules.get_by_name(resource_group_name=RESOURCE_GROUP, action_rule_name=ACTION_RULE_NAME)

        # /SmartDetectorAlertRules/get/List alert rules[get]
        result = self.mgmt_client.smart_detector_alert_rules.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /ActionRules/get/GetActionRulesResourceGroupWide[get]
        result = self.mgmt_client.action_rules.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /SmartGroups/get/Resolve[get]
        # result = self.mgmt_client.smart_groups.get_history(smart_group_id=SMART_GROUP_ID)

        # /SmartGroups/get/Get[get]
        # result = self.mgmt_client.smart_groups.get_by_id(smart_group_id=SMART_GROUP_ID)

        # /SmartDetectorAlertRules/get/List Smart Detector alert rules[get]
        result = self.mgmt_client.smart_detector_alert_rules.list()

        # /Alerts/get/GetById[get]
        # result = self.mgmt_client.alerts.get_by_id(alert_id=ALERT_ID)

        # /Alerts/get/Summary[get]
        result = self.mgmt_client.alerts.get_summary(groupby="severity,alertState")

        # /SmartGroups/get/List[get]
        result = self.mgmt_client.smart_groups.get_all()

        # /ActionRules/get/GetActionRulesSubscriptionWide[get]
        result = self.mgmt_client.action_rules.list_by_subscription()

        # /Alerts/get/ListAlerts[get]
        result = self.mgmt_client.alerts.get_all()

        # /Alerts/get/MonService[get]
        # result = self.mgmt_client.alerts.meta_data(identifier="MonitorServiceList")

        # /SmartDetectorAlertRules/patch/Patch alert rules[patch]
        BODY = {
          "tags": {
            "new_key": "newVal"
          },
          "description": "New description for patching",
          "frequency": "PT1M"
        }
        # result = self.mgmt_client.smart_detector_alert_rules.patch(resource_group_name=RESOURCE_GROUP, alert_rule_name=ALERT_RULE_NAME, parameters=BODY)

        # /ActionRules/patch/PatchActionRule[patch]
        BODY = {
          "tags": {
            "key1": "value1",
            "key2": "value2"
          },
          "status": "Disabled"
        }
        # result = self.mgmt_client.action_rules.update(resource_group_name=RESOURCE_GROUP, action_rule_name=ACTION_RULE_NAME, action_rule_patch=BODY)

        # /SmartGroups/post/changestate[post]
        BODY = {
          "comments": "Acknowledging smart group"
        }
        # result = self.mgmt_client.smart_groups.change_state(smart_group_id=SMART_GROUP_ID, body=BODY, new_state="Acknowledged")

        # /Alerts/post/Resolve[post]
        BODY = {
          "comments": "Acknowledging alert"
        }
        # result = self.mgmt_client.alerts.change_state(alert_id=ALERT_ID, body=BODY, new_state="Acknowledged")

        # /SmartDetectorAlertRules/delete/Delete a Smart Detector alert rule[delete]
        # result = self.mgmt_client.smart_detector_alert_rules.delete(resource_group_name=RESOURCE_GROUP, alert_rule_name=ALERT_RULE_NAME)

        # /ActionRules/delete/DeleteActionRule[delete]
        result = self.mgmt_client.action_rules.delete(resource_group_name=RESOURCE_GROUP, action_rule_name=ACTION_RULE_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
