# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   operations: 1/1
#   resource_links: 5/5

import unittest

import azure.mgmt.resource
import azure.mgmt.resource.resources.v2019_07_01
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtResourceLinksTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceLinksTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.resource.ManagementLinkClient
        )
        self.resource_client = self.create_mgmt_client(
            azure.mgmt.resource.resources.v2019_07_01.ResourceManagementClient
        )

    @ResourceGroupPreparer()
    def test_links(self, resource_group, location):
        if not self.is_playback():
            resource_name = self.get_resource_name("pytestavset")
            create_result = self.resource_client.resources.begin_create_or_update(
                resource_group_name=resource_group.name,
                resource_provider_namespace="Microsoft.Compute",
                parent_resource_path="",
                resource_type="availabilitySets",
                resource_name=resource_name,
                parameters={'location': location}
            )
            result = create_result.result()
            self.result_id = result.id
        else:
            self.result_id = resource_group.id + "/providers/Microsoft.Compute/availabilitySets/pytestavset7650e8a"

        link = self.client.resource_links.create_or_update(
            resource_group.id+'/providers/Microsoft.Resources/links/myLink',
            {
                'target_id' : self.result_id,
                'notes': 'Testing links'
            }
        )
        self.assertEqual(link.name, 'myLink')
    
        if not self.is_playback():
            import time
            time.sleep(10)

        link = self.client.resource_links.get(link.id)
        self.assertEqual(link.name, 'myLink')

        links = list(self.client.resource_links.list_at_subscription())
        self.assertTrue(any(link.name=='myLink' for link in links))

        links = list(self.client.resource_links.list_at_source_scope(resource_group.id))
        self.assertTrue(any(link.name=='myLink' for link in links))

        links = list(self.client.resource_links.list_at_source_scope(resource_group.id, 'atScope()'))
        self.assertTrue(any(link.name=='myLink' for link in links))

        self.client.resource_links.delete(link.id)

    def test_operations(self):
        self.client.operations.list()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
