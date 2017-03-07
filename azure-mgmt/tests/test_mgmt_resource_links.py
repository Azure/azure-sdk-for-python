# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.resource
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtResourceLinksTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceLinksTest, self).setUp()
        self.client = self.create_basic_client(
            azure.mgmt.resource.Client,
            subscription_id=self.settings.SUBSCRIPTION_ID,
        )

    @record
    def test_links(self):
        resource_groups_operations = self.client.resource_groups()
        resources_operations = self.client.resources()
        links_operations = self.client.resource_links()

        self.create_resource_group() # self.group_name
        group1 = resource_groups_operations.create_or_update(
            "FakeGroup1ForLinksTest",
            {
                'location': self.region
            }
        )

        resource_name = self.get_resource_name("pytestavset")
        create_result = resources_operations.create_or_update(
            resource_group_name=self.group_name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2015-05-01-preview",
            parameters={'location': self.region}
        )
        result = create_result.result()


        link = links_operations.create_or_update(
            self.group.id+'/providers/Microsoft.Resources/links/myLink',
            {
                'target_id' : result.id,
                'notes': 'Testing links'
            }
        )
        self.assertEqual(link.name, 'myLink')
        
        if not self.is_playback():
            import time
            time.sleep(10)

        link = links_operations.get(link.id)
        self.assertEqual(link.name, 'myLink')

        links = list(links_operations.list_at_subscription())
        self.assertTrue(any(link.name=='myLink' for link in links))

        links = list(links_operations.list_at_source_scope(self.group.id))
        self.assertTrue(any(link.name=='myLink' for link in links))

        links = list(links_operations.list_at_source_scope(self.group.id, 'atScope()'))
        self.assertTrue(any(link.name=='myLink' for link in links))

        links_operations.delete(link.id)
        resource_groups_operations.delete(group1.name)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
