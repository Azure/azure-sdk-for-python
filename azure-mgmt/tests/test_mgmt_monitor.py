# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import datetime

import azure.mgmt.monitor
import azure.monitor
from msrest.version import msrest_version
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtMonitorTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMonitorTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.monitor.MonitorManagementClient
        )
        self.data_client = self.create_mgmt_client(
            azure.monitor.MonitorClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_activity_log(self):

        # RBAC for this test (CLI command)
        # > azure role assignment create 
        #     --objectId 00000000-0000-0000-0000-000000000
        #     --roleName "Monitoring Contributor Service Role"
        #     --scope /subscriptions/00000000-0000-0000-0000-000000000

        # filter/select syntax: https://msdn.microsoft.com/en-us/library/azure/dn931934.aspx

        # Need to freeze the date for the recorded tests
        today = datetime.date(2016,11,17)
        filter = " and ".join([
            "eventTimestamp ge {}".format(today),
            "eventChannels eq 'Admin, Operation'"
        ])
        select = "eventName,operationName"
        filter = filter.format(self.group_name)
        activity_logs = list(self.data_client.activity_logs.list(
            filter=filter,
            select=select
        ))
        for log in activity_logs:
            # azure.monitor.models.EventData
            #print(" ".join([
            #    log.event_name.localized_value,
            #    log.operation_name.localized_value
            #]))
            self.assertIsNotNone(log.event_name.localized_value)
            self.assertIsNotNone(log.operation_name.localized_value)


    @record
    def test_metrics(self):
        # Get the VM or your resource and use "id" attribute, or build the id yourself from RG and name
        resource_id = (
            "subscriptions/{}/"
            "resourceGroups/DoNotDeleteGroup/"
            "providers/Microsoft.Compute/virtualMachines/UbuntuServerDoNotDelete"
        ).format(self.settings.SUBSCRIPTION_ID)

        metrics = list(self.data_client.metric_definitions.list(
            resource_id,
        ))
        self.assertGreaterEqual(len(metrics), 1)
        for item in metrics:
            self.assertIsNotNone(item.name)
            print("{}: id={}, unit={}".format(
                item.name.localized_value,
                item.name.value,
                item.unit)
            )

        # Need to freeze the date for the recorded tests
        today = datetime.date(2016,11,17)
        yesterday = today - datetime.timedelta(days=1)

        filter = " and ".join([
            "(name.value eq 'Percentage CPU')",
            "(aggregationType eq 'Total')",
            "startTime eq {}".format(yesterday),
            "endTime eq {}".format(today),
            "timeGrain eq duration'PT1H'"
        ])
        
        metrics = list(self.data_client.metrics.list(
            resource_id,
            filter=filter
        ))
        self.assertGreaterEqual(len(metrics), 1)
        for item in metrics:
            self.assertIsNotNone(item.name)
            self.assertIsNotNone(item.unit)
            for data in item.data:
                self.assertIsNotNone(data.time_stamp)
                self.assertIsNotNone(data.total)

        for item in metrics:
            print("{} ({})".format(item.name.localized_value, item.unit.name))
            for data in item.data:
                print("{}: {}".format(data.time_stamp, data.total))


    @unittest.skip("Known bug")
    @record
    def test_tenants_event(self):

        tenant_events = list(self.data_client.tenant_events.list())

    @record
    def test_event_categories(self):
        event_categories = list(self.data_client.event_categories.list())

        for cat in event_categories:
            # azure.monitor.models.LocalizableString
            # print("Category: {} (localized: {})".format(cat.value, cat.localized_value))
            self.assertIsNotNone(cat.value)
            self.assertIsNotNone(cat.localized_value)

    @unittest.skip("Deprecated. Monitor team stopped support")
    @record
    def test_usage_metrics(self):
        # Get the DocDB or your resource and use "id" attribute, or build the id yourself from RG and name
        # Usage metric is rare, DocDb and WebPlan are good example.
        resource_id = (
            "subscriptions/{}/"
            "resourceGroups/MonitorTestsDoNotDelete/"
            "providers/Microsoft.DocumentDb/databaseAccounts/pymonitortest"
        ).format(self.settings.SUBSCRIPTION_ID)

        usage_metrics = list(self.data_client.usage_metrics.list(
            resource_id,
        ))
        for item in usage_metrics:
            # azure.monitor.models.UsageMetric
            print("{} ({}): {} / {}".format(
                item.name.localized_value,
                item.unit,
                item.current_value,
                item.limit 
            ))
            self.assertIsNotNone(item.name)

    @unittest.skip("Known bug")
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

    @unittest.skip("Known bug")
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
