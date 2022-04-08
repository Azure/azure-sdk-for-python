# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 4
# Methods Covered : 4
# Examples Total  : 4
# Examples Tested : 4
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.serialconsole
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

@unittest.skip("skip test")
class MgmtMicrosoftSerialConsoleClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMicrosoftSerialConsoleClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.serialconsole.MicrosoftSerialConsoleClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_serialconsole(self, resource_group):

        # Get the Serial Console disabled status for a subscription[get]
        result = self.mgmt_client.list_console.disabled()

        # List all Serial Console management operations supported by Serial Console RP[get]
        result = self.mgmt_client.list.operations()

        # Enable Serial Console for a subscription[post]
        result = self.mgmt_client.console.enable_console()

        # Disable Serial Console for a subscription[post]
        result = self.mgmt_client.console.disable_console()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
