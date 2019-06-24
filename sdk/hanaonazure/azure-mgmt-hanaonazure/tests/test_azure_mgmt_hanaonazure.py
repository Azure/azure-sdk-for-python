# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest

import azure.mgmt.hanaonazure.models

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtHanaOnAzureTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtHanaOnAzureTest, self).setUp()

        self.hanaonazure_client = self.create_mgmt_client(
            azure.mgmt.hanaonazure.HanaManagementClient
        )

    def process(self, result):
        pass

    def test_hanainstance_list(self):
        hanainstances = list(self.hanaonazure_client.hana_instances.list())
        self.assertEqual(len(hanainstances), 3)

    @ResourceGroupPreparer()
    def test_hanainstance_list_by_resource_group(self, resource_group):

        resource_group_name = resource_group.name

        hanainstances = list(self.hanaonazure_client.hana_instances.list_by_resource_group(resource_group_name))
        self.assertEqual(len(hanainstances), 3)

    @ResourceGroupPreparer()
    def test_hanainstance_get(self, resource_group):

        resource_group_name = resource_group.name
        resource_name = "testhanainstanceresourcename"

        hanainstance = self.hanaonazure_client.hana_instances.get(resource_group_name, resource_name)
        self.assertEqual(hanainstance.name, resource_name)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()