# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.eventhub
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtEventHubTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtEventHubTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.eventhub.EventHubManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_namespace(self):
        ns_name = self.get_resource_name('pyarmns')

        async_create_ns = self.client.namespaces.create_or_update(
            self.group_name,
            ns_name,
            {
                'location': self.region
            }
        )

        ns = async_create_ns.result()
        self.assertEqual(ns.name, ns_name)

        result = self.client.namespaces.get(
            self.group_name, 
            ns_name,
        )
        self.assertEqual(result.name, ns_name)

        nss = list(self.client.namespaces.list_by_resource_group(self.group_name))
        self.assertEqual(len(nss), 1)

        async_delete = self.client.namespaces.delete(self.group_name, ns_name)
        async_delete.wait()

    @record
    def test_hubs(self):
        ns_name = self.get_resource_name('pyarmns')
        eventhub_name = self.get_resource_name('pyarmeh')

        async_create_ns = self.client.namespaces.create_or_update(
            self.group_name,
            ns_name,
            {
                'location': self.region
            }
        )
        ns = async_create_ns.result()
        
        event_hub = self.client.event_hubs.create_or_update(
            self.group_name,
            ns_name,
            eventhub_name,
            {
                'location': self.region
            }
        )
        self.assertEqual(event_hub.name, eventhub_name)
    
        event_hub = self.client.event_hubs.get(
            self.group_name,
            ns_name,
            eventhub_name
        )
        self.assertEqual(event_hub.name, eventhub_name)        
    
        event_hub = self.client.event_hubs.delete(
            self.group_name,
            ns_name,
            eventhub_name
        )



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()