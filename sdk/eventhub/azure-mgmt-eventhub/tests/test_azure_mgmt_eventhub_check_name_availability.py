# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.eventhub.models
from azure.mgmt.eventhub.models import EHNamespace
from azure.common.credentials import ServicePrincipalCredentials

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtEventHubTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtEventHubTest, self).setUp()

        self.eventhub_client = self.create_mgmt_client(
            azure.mgmt.eventhub.EventHubManagementClient
        )

    def process(self, result):
        pass

    def test_eh_namespace_available(self):
        # Check the namespace availability
        availabilityresult = self.eventhub_client.namespaces.check_name_availability("Testingehnamespaceavailabilityforpython")
        self.assertEqual(availabilityresult.name_available, True)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()