# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.subscription
from azure.mgmt.subscription.models import *
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy


class TestMgmtSubscription(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.subscription.SubscriptionClient
        )
    @recorded_by_proxy
    def test_subscriptions_list(self):
        result = self.mgmt_client.subscriptions.list()
        assert list(result) is not None


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
