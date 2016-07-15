# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.resource
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtResourceSubscriptionsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceSubscriptionsTest, self).setUp()
        self.subscriptions_client = self.create_basic_client(
            azure.mgmt.resource.SubscriptionClient
        )

    @record
    def test_subscriptions(self):
        subs = list(self.subscriptions_client.subscriptions.list())
        self.assertGreater(len(subs), 0)
        self.assertTrue(all(isinstance(v, azure.mgmt.resource.subscriptions.models.Subscription) for v in subs))

        locations = list(self.subscriptions_client.subscriptions.list_locations(self.settings.SUBSCRIPTION_ID))
        self.assertGreater(len(locations), 0)
        self.assertTrue(all(isinstance(v, azure.mgmt.resource.subscriptions.models.Location) for v in locations))

        sub = self.subscriptions_client.subscriptions.get(self.settings.SUBSCRIPTION_ID)
        self.assertEqual(sub.subscription_id, self.settings.SUBSCRIPTION_ID)

    @record
    def test_tenants(self):
        tenants = list(self.subscriptions_client.tenants.list())
        self.assertGreater(len(tenants), 0)
        self.assertTrue(all(isinstance(v, azure.mgmt.resource.subscriptions.models.TenantIdDescription) for v in tenants))


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
