# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.servermanager
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy

class TestMgmtServerManager(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            azure.mgmt.servermanager.ServerManagement
        )

    @ResourceGroupPreparer()
    @recorded_by_proxy
    def test_servermanager_gateways(self, resource_group, location):
        gateway_name = self.get_resource_name('pygateway')
        region = 'centralus'

        gateway_async = self.client.gateway.create(
            resource_group.name,
            gateway_name,
            region
        )
        gateway = gateway_async.result()
        assert gateway.name == gateway_name

        gateway = self.client.gateway.get(
            resource_group.name,
            gateway_name
        )
        assert gateway.name == gateway_name

        gateways = list(self.client.gateway.list())
        assert len(gateways) == 1

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
