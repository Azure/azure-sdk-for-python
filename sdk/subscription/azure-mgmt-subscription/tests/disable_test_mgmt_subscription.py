# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.subscription.models import *
from devtools_testutils import AzureMgmtTestCase
import six


class MgmtSubscriptionTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSubscriptionTest, self).setUp()
        self.subscription_client = self.create_basic_client(
            SubscriptionClient
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
