# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.resource
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtResourceSubscriptionsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceSubscriptionsTest, self).setUp()
        self.client = self.create_basic_client(
            azure.mgmt.resource.Client
        )

    @record
    def test_subscriptions(self):
        models = azure.mgmt.resource.models('2016-06-01')
        subscriptions_operations = self.client.subscriptions('2016-06-01')

        subs = list(subscriptions_operations.list())
        self.assertGreater(len(subs), 0)
        self.assertTrue(all(isinstance(v, models.Subscription) for v in subs))

        locations = list(subscriptions_operations.list_locations(self.settings.SUBSCRIPTION_ID))
        self.assertGreater(len(locations), 0)
        self.assertTrue(all(isinstance(v, models.Location) for v in locations))

        sub = subscriptions_operations.get(self.settings.SUBSCRIPTION_ID)
        self.assertEqual(sub.subscription_id, self.settings.SUBSCRIPTION_ID)

    @record
    def test_tenants(self):
        models = azure.mgmt.resource.models('2016-06-01')
        tenants_operations = self.client.tenants('2016-06-01')

        tenants = list(tenants_operations.list())
        self.assertGreater(len(tenants), 0)
        self.assertTrue(all(isinstance(v, models.TenantIdDescription) for v in tenants))


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
