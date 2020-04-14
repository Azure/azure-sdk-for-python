# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 17
# Methods Covered : 17
# Examples Total  : 19
# Examples Tested : 0
# Coverage %      : 0
# ----------------------

import unittest

import azure.mgmt.appconfiguration
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtAppConfigurationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAppConfigurationTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.appconfiguration.AppConfigurationManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_appconfiguration(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        CONFIGURATION_STORE_NAME = "myConfigurationStore"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "myPrivateEndpointConnection"
        PRIVATE_LINK_RESOURCE_NAME = "myPrivateLinkResource"


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
