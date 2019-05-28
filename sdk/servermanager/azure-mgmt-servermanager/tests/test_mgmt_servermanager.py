# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.servermanager
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtServerManagerTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtServerManagerTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.servermanager.ServerManagement
        )

    @ResourceGroupPreparer()
    def test_servermanager_gateways(self, resource_group, location):
        gateway_name = self.get_resource_name('pygateway')
        region = 'centralus'

        gateway_async = self.client.gateway.create(
            resource_group.name,
            gateway_name,
            region
        )
        gateway = gateway_async.result()
        self.assertEqual(gateway.name, gateway_name)

        gateway = self.client.gateway.get(
            resource_group.name,
            gateway_name
        )
        self.assertEqual(gateway.name, gateway_name)

        gateways = list(self.client.gateway.list())
        self.assertEqual(len(gateways), 1)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
