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
        iothub = async_iot_hub.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
