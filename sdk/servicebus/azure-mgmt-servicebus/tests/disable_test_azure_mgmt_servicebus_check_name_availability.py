# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.servicebus.models
from azure.mgmt.servicebus.models import SBNamespace
from azure.common.credentials import ServicePrincipalCredentials

from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer


class MgmtServiceBusTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtServiceBusTest, self).setUp()

        self.servicebus_client = self.create_mgmt_client(
            azure.mgmt.servicebus.ServiceBusManagementClient
        )

    def process(self, result):
        pass

    @RandomNameResourceGroupPreparer()
    def test_sb_namespace_available(self, resource_group, location):
        # Check the namespace availability
        availabilityresult = self.servicebus_client.namespaces.check_name_availability_method("Testingthenamespacenameforpython")
        self.assertEqual(availabilityresult.name_available, True)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()