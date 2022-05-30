# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.iothub
from datetime import date, timedelta
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy

class TestMgmtIoTHub(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.iothub_client = self.create_mgmt_client(
            azure.mgmt.iothub.IotHubClient
        )

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_iothub(self, resource_group, location):
        account_name = self.get_resource_name('iot')
        
        is_available = self.iothub_client.iot_hub_resource.check_name_availability(
            {
                "name": account_name
            }
        )
        assert is_available.name_available

        async_iot_hub = self.iothub_client.iot_hub_resource.begin_create_or_update(
            resource_group.name,
            account_name,
            {
                'location': location,
                'subscriptionid': self.get_settings_value("SUBSCRIPTION_ID"),
                'resourcegroup': resource_group.name,
                'sku': {
                  'name': 'S1',
                  'capacity': 2
                },
                'properties': {
                  'enable_file_upload_notifications': False,
                  'operations_monitoring_properties': {
                    'events': {
                      "C2DCommands": "Error",
                      "DeviceTelemetry": "Error",
                      "DeviceIdentityOperations": "Error",
                      "Connections": "Information"
                    }
                  },
                  "features": "None",
                }
            }
        )
        iothub_account = async_iot_hub.result()
        assert iothub_account.name == account_name

        iothub_account = self.iothub_client.iot_hub_resource.get(
            resource_group.name,
            account_name
        )
        assert iothub_account.name == account_name

        iothub_accounts =  list(self.iothub_client.iot_hub_resource.list_by_resource_group(resource_group.name))
        assert all(i.name == account_name for i in iothub_accounts)

        iothub_accounts =  list(self.iothub_client.iot_hub_resource.list_by_subscription())
        assert any(i.name == account_name for i in iothub_accounts)

        stats = self.iothub_client.iot_hub_resource.get_stats(
            resource_group.name,
            account_name
        )

        skus = list(self.iothub_client.iot_hub_resource.get_valid_skus(
            resource_group.name,
            account_name
        ))

        jobs = list(self.iothub_client.iot_hub_resource.list_jobs(
            resource_group.name,
            account_name
        ))

        quota_metrics = list(self.iothub_client.iot_hub_resource.get_quota_metrics(
            resource_group.name,
            account_name
        ))

        async_delete = self.iothub_client.iot_hub_resource.begin_delete(
            resource_group.name,
            account_name
        )
        async_delete.wait()

    @unittest.skip('hard to test')
    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_iothub_consumer_group(self, resource_group, location):
        account_name = self.get_resource_name('iot')

        async_iot_hub = self.iothub_client.iot_hub_resource.begin_create_or_update(
            resource_group.name,
            account_name,
            {
                'location': location,
                'subscriptionid': self.get_settings_value("SUBSCRIPTION_ID"),
                'resourcegroup': resource_group.name,
                'sku': {
                  'name': 'S1',
                  'capacity': 2
                },
                'properties': {
                  'enable_file_upload_notifications': False,
                  'operations_monitoring_properties': {
                    'events': {
                      "C2DCommands": "Error",
                      "DeviceTelemetry": "Error",
                      "DeviceIdentityOperations": "Error",
                      "Connections": "Information"
                    }
                  },
                  "features": "None",
                }
            }
        )
        async_iot_hub.wait()

        cg_account_name = self.get_resource_name('consumergrp')
        consumer_group = self.iothub_client.iot_hub_resource.create_event_hub_consumer_group(
            resource_group.name,
            account_name,
            'events',
            cg_account_name
        )

        consumer_group = self.iothub_client.iot_hub_resource.get_event_hub_consumer_group(
            resource_group.name,
            account_name,
            'events',
            consumer_group.name
        )

        consumer_groups = list(self.iothub_client.iot_hub_resource.list_event_hub_consumer_groups(
            resource_group.name,
            account_name,
            'events'
        ))
        assert any(group.name == consumer_group.name for group in consumer_groups)

        self.iothub_client.iot_hub_resource.delete_event_hub_consumer_group(
            resource_group.name,
            account_name,
            'events',
            consumer_group.name
        )

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
