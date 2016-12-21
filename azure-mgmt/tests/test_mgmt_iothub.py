# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.iothub
from datetime import date, timedelta
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtIoTHubTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtIoTHubTest, self).setUp()
        self.iothub_client = self.create_mgmt_client(
            azure.mgmt.iothub.IotHubClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_iothub(self):
        account_name = self.get_resource_name('iot')
        
        is_available = self.iothub_client.iot_hub_resource.check_name_availability(
            account_name
        )
        self.assertTrue(is_available.name_available)

        async_iot_hub = self.iothub_client.iot_hub_resource.create_or_update(
            self.group_name,
            account_name,
            {
                'location': self.region,
                'subscriptionid': self.settings.SUBSCRIPTION_ID,
                'resourcegroup': self.group_name,
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
        self.assertEqual(iothub_account.name, account_name)

        iothub_account = self.iothub_client.iot_hub_resource.get(
            self.group_name,
            account_name
        )
        self.assertEqual(iothub_account.name, account_name)

        iothub_accounts =  list(self.iothub_client.iot_hub_resource.list_by_resource_group(self.group_name))
        self.assertTrue(all(i.name == account_name for i in iothub_accounts))

        iothub_accounts =  list(self.iothub_client.iot_hub_resource.list_by_subscription())
        self.assertTrue(any(i.name == account_name for i in iothub_accounts))

        stats = self.iothub_client.iot_hub_resource.get_stats(
            self.group_name,
            account_name
        )

        skus = list(self.iothub_client.iot_hub_resource.get_valid_skus(
            self.group_name,
            account_name
        ))

        jobs = list(self.iothub_client.iot_hub_resource.list_jobs(
            self.group_name,
            account_name
        ))

        quota_metrics = list(self.iothub_client.iot_hub_resource.get_quota_metrics(
            self.group_name,
            account_name
        ))

        async_delete = self.iothub_client.iot_hub_resource.delete(
            self.group_name,
            account_name
        )
        async_delete.wait()

    @record
    def test_iothub_consumer_group(self):
        account_name = self.get_resource_name('iot')

        async_iot_hub = self.iothub_client.iot_hub_resource.create_or_update(
            self.group_name,
            account_name,
            {
                'location': self.region,
                'subscriptionid': self.settings.SUBSCRIPTION_ID,
                'resourcegroup': self.group_name,
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

        cg_account_name = self.get_resource_name('consumergrp')
        consumer_group = self.iothub_client.iot_hub_resource.create_event_hub_consumer_group(
            self.group_name,
            account_name,
            'events',
            cg_account_name
        )

        consumer_group = self.iothub_client.iot_hub_resource.get_event_hub_consumer_group(
            self.group_name,
            account_name,
            'events',
            consumer_group.name
        )

        consumer_groups = list(self.iothub_client.iot_hub_resource.list_event_hub_consumer_groups(
            self.group_name,
            account_name,
            'events'
        ))
        self.assertTrue(any(name == consumer_group.name for name in consumer_groups))

        self.iothub_client.iot_hub_resource.delete_event_hub_consumer_group(
            self.group_name,
            account_name,
            'events',
            consumer_group.name
        )

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
