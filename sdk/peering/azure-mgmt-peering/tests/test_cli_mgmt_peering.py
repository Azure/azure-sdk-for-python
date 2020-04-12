# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 35
# Methods Covered : 35
# Examples Total  : 38
# Examples Tested : 0
# Coverage %      : 0
# ----------------------

import unittest

import azure.mgmt.peering
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtPeeringTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtPeeringTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.peering.PeeringManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_peering(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        RESOURCE_GROUP_NAME = resource_group.name


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
