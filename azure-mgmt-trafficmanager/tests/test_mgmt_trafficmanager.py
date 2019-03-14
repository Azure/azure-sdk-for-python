# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.trafficmanager
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtTrafficManagerTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtTrafficManagerTest, self).setUp()
        self.commerce_client = self.create_mgmt_client(
            azure.mgmt.trafficmanager.TrafficManagerManagementClient
        )

    @ResourceGroupPreparer()
    def test_trafficmanager(self, resource_group, location):
        # FIXME, write tests
        pass


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
