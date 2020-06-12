# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   operations: 1/1
#   subscriptions: 3/3
#   tenants: 1/1

import unittest

import azure.mgmt.resource
from devtools_testutils import AzureMgmtTestCase

class MgmtResourceSubscriptionsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceSubscriptionsTest, self).setUp()
        self.subscriptions_client = self.create_basic_client(
            azure.mgmt.resource.SubscriptionClient
        )

    def test_subscriptions(self):
        subs = list(self.subscriptions_client.subscriptions.list())
        self.assertGreater(len(subs), 0)
        
        # [ZIM] temporarily disabled
        # self.assertTrue(all(isinstance(v, azure.mgmt.resource.subscriptions.models.Subscription) for v in subs))

        locations = list(self.subscriptions_client.subscriptions.list_locations(self.settings.SUBSCRIPTION_ID))
        self.assertGreater(len(locations), 0)

        # [ZIM] temporarily disabled
        # self.assertTrue(all(isinstance(v, azure.mgmt.resource.subscriptions.models.Location) for v in locations))

        sub = self.subscriptions_client.subscriptions.get(self.settings.SUBSCRIPTION_ID)
        self.assertEqual(sub.subscription_id, self.settings.SUBSCRIPTION_ID)

    def test_tenants(self):
        tenants = list(self.subscriptions_client.tenants.list())
        self.assertGreater(len(tenants), 0)
        
        # [ZIM] temporarily disabled
        # self.assertTrue(all(isinstance(v, azure.mgmt.resource.subscriptions.models.TenantIdDescription) for v in tenants))

    def test_operations(self):
        self.subscriptions_client.operations.list()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
