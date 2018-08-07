# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.billing
import azure.mgmt.subscription
from testutils.common_recordingtestcase import record
from devtools_testutils import AzureMgmtTestCase

class MgmtSubscriptionTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSubscriptionTest, self).setUp()
        self.subscription_client = self.create_basic_client(azure.mgmt.subscription.SubscriptionClient)
        self.billing_client = self.create_mgmt_client(azure.mgmt.billing.BillingManagementClient)

    def test_create_subscription(self):
        enrollment_accounts = list(self.billing_client.enrollment_accounts.list())
        self.assertTrue(len(enrollment_accounts) > 0)
        creation_parameters = azure.mgmt.subscription.models.SubscriptionCreationParameters(
            offer_type='MS-AZR-0148P')
        creation_result = self.subscription_client.subscription_factory \
            .create_subscription_in_enrollment_account(
                enrollment_accounts[0].name,
                creation_parameters)
        self.assertTrue(len(creation_result.result().subscription_link) > 0)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
