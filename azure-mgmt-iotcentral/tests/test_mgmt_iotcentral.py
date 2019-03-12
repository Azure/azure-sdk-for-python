# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.iotcentral
from azure.mgmt.iotcentral.models import App, AppSkuInfo
from datetime import date, timedelta
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtIoTCentralTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtIoTCentralTest, self).setUp()
        self.iotcentral_client = self.create_mgmt_client(
            azure.mgmt.iotcentral.IotCentralClient
        )

    @ResourceGroupPreparer()
    def test_iotcentral(self, resource_group, location):
        account_name = self.get_resource_name('iot')
        
        is_available = self.iotcentral_client.apps.check_name_availability(
            account_name
        )
        self.assertTrue(is_available.name_available)

        async_iotcentral_app = self.iotcentral_client.apps.create_or_update(
            resource_group.name,
            account_name,
            {
                'location': location,
                'subscriptionid': self.settings.SUBSCRIPTION_ID,
                'subdomain': account_name,
                'display_name': account_name,
                'sku': {
                  'name': 'S1'
                }
            }
        )
        iotcentral_account = async_iotcentral_app.result()
        self.assertEqual(iotcentral_account.name, account_name)

        iotcentral_account = self.iotcentral_client.apps.get(
            resource_group.name,
            account_name
        )
        self.assertEqual(iotcentral_account.display_name, account_name)

        iotcentral_accounts = list(self.iotcentral_client.apps.list_by_resource_group(resource_group.name))
        self.assertTrue(all(i.display_name == account_name for i in iotcentral_accounts))

        iotcentral_accounts =  list(self.iotcentral_client.apps.list_by_subscription())
        self.assertTrue(any(i.display_name == account_name for i in iotcentral_accounts))

        async_delete = self.iotcentral_client.apps.delete(
            resource_group.name,
            account_name
        )
        async_delete.wait()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
