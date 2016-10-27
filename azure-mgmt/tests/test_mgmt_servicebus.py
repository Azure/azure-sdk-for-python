# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.servicebus
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtServiceBusTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtServiceBusTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.servicebus.ServiceBusManagementClient
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
    def test_topics(self):
        ns_name = self.get_resource_name('pyarmns')
        topic_name = self.get_resource_name('pyarmtopic')

        async_create_ns = self.client.namespaces.create_or_update(
            self.group_name,
            ns_name,
            {
                'location': self.region
            }
        )
        ns = async_create_ns.result()
        
        topic = self.client.topics.create_or_update(
            self.group_name,
            ns_name,
            topic_name,
            {
                'location': self.region
            }
        )
        self.assertEqual(topic.name, topic_name)
    
        topic = self.client.topics.get(
            self.group_name,
            ns_name,
            topic_name
        )
        self.assertEqual(topic.name, topic_name)        
    
        topic = self.client.topics.delete(
            self.group_name,
            ns_name,
            topic_name
        )



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
