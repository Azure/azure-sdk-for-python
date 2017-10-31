# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.servicebus.models
from azure.mgmt.servicebus.models import SBNamespace,SBSku,SkuName
from azure.common.credentials import ServicePrincipalCredentials

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtServiceBusTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtServiceBusTest, self).setUp()

        self.servicebus_client = self.create_mgmt_client(
            azure.mgmt.servicebus.ServiceBusManagementClient
        )

    def process(self, result):
        pass

    @ResourceGroupPreparer()
    def test_sb_curd1(self, resource_group, location):
        # List all topic types
        # resource_group_name = resource_group.name #"ardsouza-resourcemovetest-group2"
        #custom_headers={'next_link':'None'}
        # raw = False
        # print(resource_group.name)
        # namespace_name = "testingpythontestcase"
        # test=SBNamespace
        # test.location = location
        # test.tags={'tag1':'value1','tag2':'value2'}
        # test.sku=SBSku
        # test.sku.Name = SkuName
        # test.sku.Name = SkuName.standard
        #test.sku= {'name': <SkuName.standard: 'Standard'>}, 'tier': <SkuTier.standard: 'Standard'>, 'capacity': None}

        listnamespace = self.servicebus_client.namespaces.get("ardsouza-resourcemovetest-group2","ardsouza-5-11-movetest-SBNamespace")
        tesetList = listnamespace
        # print("sku: ", test.sku)
        # print("Location: ", test.location)
        # print("tags: ", test.tags)
        # creatednamespace = self.servicebus_client.namespaces.create_or_update(resource_group_name, namespace_name, test)
        # self.assertEqual(creatednamespace.name,name)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()