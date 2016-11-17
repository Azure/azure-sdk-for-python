# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.monitor
import azure.monitor
from msrest.version import msrest_version
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtMonitorTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMonitorTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.monitor.InsightsManagementClient
        )
        self.data_client = self.create_mgmt_client(
            azure.monitor.InsightsClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_metrics(self):
        resource_id = "subscriptions/f9d8179e-43f0-46cb-99cd-f72bfab0a63b/resourceGroups/DoNotDeleteGroup/providers/Microsoft.Compute/virtualMachines/UbuntuServerDoNotDelete"

        metrics = list(self.data_client.metric_definitions.list(
            resource_id,
        ))
        for item in metrics:
            print(item.name)
        
        metrics = list(self.data_client.metrics.list(
            resource_id,
            filter="(name.value eq 'Percentage CPU') and (aggregationType eq 'Total' or aggregationType eq 'Average') and startTime eq 2016-11-02 and endTime eq 2016-11-03 and timeGrain eq duration'PT1H'"
        ))
        for item in metrics:
            print(item)

        usage_metrics = list(self.data_client.usage_metrics.list(
            resource_id,
        ))


    @record
    def test_log_profile(self):
        profile_name = self.get_resource_name('pyprofile')

        profile = self.mgmt_client.log_profiles.create_or_update(
            profile_name,
            {
                "storage_account_id": "/subscriptions/f9d8179e-43f0-46cb-99cd-f72bfab0a63b/resourceGroups/test_mgmt_media_test_media8fdd0a81/providers/Microsoft.Storage/storageAccounts/msmediapttest",
            #    "service_bus_rule_id": "/subscriptions/6983c752-c9b8-48dd-b4d4-da739beb7e98/resourceGroups/Default-ServiceBus-WestUS/providers/Microsoft.ServiceBus/namespaces/myNamespace/RootManageSharedAccessKey",
                "locations": [
                  "eastus",
                  "westus"
                ],
                "categories": [
                  "Write",
                  "Delete",
                  "Action"
                ],
                "retention_policy": {
                  "enabled": True,
                  "days": 1
                }
            }
        )
        self.assertEqual(profile.name, profile_name)

        profile = self.mgmt_client.log_profiles.get(
            profile_name,
        )
        self.assertEqual(profile.name, profile_name)

        profiles = list(self.mgmt_client.log_profiles.list())
        self.assertEqual(len(profiles), 1)

        self.mgmt_client.log_profiles.delete(profile_name)

    @record
    def test_activity_log(self):

        # RBAC for this test (CLI command)
        # azure role assignment create 
        #     --objectId ed95d6cc-6ad3-42bb-834e-826d1c7db543
        #     --roleName "Monitoring Contributor Service Role"
        #     --scope /subscriptions/f9d8179e-43f0-46cb-99cd-f72bfab0a63

        filter = ("eventTimestamp ge '2016-11-01T00:00:00Z' and "
                    "eventChannels eq 'Admin, Operation'")
        select = "description"
        filter = filter.format(self.group_name)
        events = list(self.data_client.events.list(
            filter=filter,
            select=select
        ))
        print(len(events))

    @record
    def test_tenants_event(self):

        tenant_events = list(self.data_client.tenant_events.list())

    @record
    def test_event_categories(self):

        event_categories = list(self.data_client.event_categories.list())


    @record    
    def test_autoscale_settings(self):
        as_name = "setting1"
        resource_id = "/subscriptions/f9d8179e-43f0-46cb-99cd-f72bfab0a63b/resourcegroups/MonitorTestsDoNotDelete/providers/Microsoft.Compute/virtualMachines/MonitorTest/"

        as_obj = self.mgmt_client.autoscale_settings.create_or_update(
            self.group_name,
            as_name,
            {
                'location': self.region,
                'autoscale_setting_resource_name': as_name, # Name as to be written again
                'enabled': False,
                'target_resource_uri': resource_id,
                'profiles': [{
                    "name": "Day",
                    "capacity": {
                        "minimum": "1",
                        "maximum": "5",
                        "default": "4"
                    },
                    'rules': [{
                        "metric_trigger": {
                          "metric_name": "Percentage CPU",
                          "metric_resource_uri": resource_id,
                          "time_grain": "PT5M",
                          "statistic": "Average",
                          "time_window": "PT45M",
                          "time_aggregation": "Average",
                          "operator": "GreaterThanOrEqual",
                          "threshold": 60
                        },
                        "scale_action": {
                          "direction": "Increase",
                          "value": "2",
                          "cooldown": "PT20M"
                        }
                    }]
                }]
            }
        )
        self.assertEqual(as_obj.name, as_name)

        as_obj = self.mgmt_client.autoscale_settings.get(
            self.group_name,
            as_name
        )
        self.assertEqual(as_obj.name, as_name)

        ass = list(self.mgmt_client.autoscale_settings.list_by_resource_group(
            self.group_name
        ))
        self.assertEqual(len(ass), 1)
        self.assertEqual(ass[0].name, as_name)

        self.mgmt_client.autoscale_settings.delete(
            self.group_name,
            as_name
        )

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
