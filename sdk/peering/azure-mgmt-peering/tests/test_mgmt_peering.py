# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest

import azure.mgmt.peering
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'westus'

class MgmtPeeringTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtPeeringTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.peering.PeeringManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_peering(self, resource_group):

        PEERING_SERVICE_NAME = "MyPeerServiceName"
        PREFIX_NAME = "MyPeerPrefix"
        PREFIX_VALUE = "192.168.1.0/24"

        BODY = {
          "properties": {
            "peeringServiceLocation": "California",
            "peeringServiceProvider": "Kordia Limited"
          },
          "location": "westus"
        }
        azure_operation_poller = self.mgmt_client.peering_services.create_or_update(resource_group.name, PEERING_SERVICE_NAME, BODY)
        self.assertEqual(azure_operation_poller.name, PEERING_SERVICE_NAME)
        self.assertEqual(azure_operation_poller.provisioning_state, "Succeeded")
        
        azure_operation_poller = self.mgmt_client.prefixes.create_or_update(resource_group.name, PEERING_SERVICE_NAME, PREFIX_NAME, prefix=PREFIX_VALUE)
        self.assertEqual(azure_operation_poller.prefix, PREFIX_VALUE)
        self.assertEqual(azure_operation_poller.provisioning_state, "Succeeded")

        azure_operation_poller = self.mgmt_client.prefixes.delete(resource_group.name, PEERING_SERVICE_NAME, PREFIX_NAME, prefix=PREFIX_VALUE)

        BODY = {}
        azure_operation_poller = self.mgmt_client.peering_services.delete(resource_group.name, PEERING_SERVICE_NAME, BODY)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
