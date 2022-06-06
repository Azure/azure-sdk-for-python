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
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

class TestMgmtResourceSubscriptions(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.subscriptions_client = self.create_mgmt_client(
            azure.mgmt.resource.SubscriptionClient
        )

    @recorded_by_proxy
    def test_subscriptions(self):
        subs = list(self.subscriptions_client.subscriptions.list())
        assert len(subs) >= 0
        
        # [ZIM] temporarily disabled
        # assert all(isinstance(v, azure.mgmt.resource.subscriptions.models.Subscription) for v in subs)

        subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
        locations = list(self.subscriptions_client.subscriptions.list_locations(subscription_id))
        assert len(locations) >= 0

        # [ZIM] temporarily disabled
        # assert all(isinstance(v, azure.mgmt.resource.subscriptions.models.Location) for v in locations)

        sub = self.subscriptions_client.subscriptions.get(subscription_id)
        assert sub.subscription_id == subscription_id

    @recorded_by_proxy
    def test_tenants(self):
        tenants = list(self.subscriptions_client.tenants.list())
        assert len(tenants) >= 0
        
        # [ZIM] temporarily disabled
        # assert all(isinstance(v, azure.mgmt.resource.subscriptions.models.TenantIdDescription) for v in tenants)

    @recorded_by_proxy
    def test_operations(self):
        self.subscriptions_client.operations.list()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
