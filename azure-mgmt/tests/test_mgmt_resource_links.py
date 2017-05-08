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
        self.client = self.create_mgmt_client(
            azure.mgmt.resource.ManagementLinkClient
        )            

    def test_links(self):
        if not self.is_playback():
            self.create_resource_group()
            self.group_id = self.group.id
            group1 = self.resource_client.resource_groups.create_or_update(
                "FakeGroup1ForLinksTest",
                {
                    'location': self.region
                }
            )

            resource_name = self.get_resource_name("pytestavset")
            create_result = self.resource_client.resources.create_or_update(
                resource_group_name=self.group_name,
                resource_provider_namespace="Microsoft.Compute",
                parent_resource_path="",
                resource_type="availabilitySets",
                resource_name=resource_name,
                api_version="2015-05-01-preview",
                parameters={'location': self.region}
            )
            result = create_result.result()
            self.result_id = result.id
        else:
            self.group_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test_mgmt_resource_links_test_links7650e8a"
            self.result_id = self.group_id + "/providers/Microsoft.Compute/availabilitySets/pytestavset7650e8a"

        with self.recording():
            link = self.client.resource_links.create_or_update(
                self.group_id+'/providers/Microsoft.Resources/links/myLink',
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

            links = list(self.client.resource_links.list_at_source_scope(self.group_id))
            self.assertTrue(any(link.name=='myLink' for link in links))

            links = list(self.client.resource_links.list_at_source_scope(self.group_id, 'atScope()'))
            self.assertTrue(any(link.name=='myLink' for link in links))

            self.client.resource_links.delete(link.id)

        if not self.is_playback():
            self.resource_client.resource_groups.delete(group1.name)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
