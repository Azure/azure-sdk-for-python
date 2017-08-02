# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest

import azure.mgmt.containerinstance

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtContainerInstanceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtContainerInstanceTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.containerinstance.ContainerInstanceManagementClient
        )

    @ResourceGroupPreparer()
    def test_container_instance(self, resource_group, location):
        container_group_name = self.get_resource_name('pycontainer')
        image = 'alpine:latest'
        os_type = 'Linux'
        cpu = 1
        memory = 1

        container_group = self.client.container_groups.create_or_update(
            resource_group.name,
            container_group_name,
            {
                'location': location,
                'containers': [{
                    'name': container_group_name,
                    'image': image,
                    'resources': {
                        'requests': {
                            'memory_in_gb': memory,
                            'cpu': cpu
                        }
                    }
                }],
                'os_type': os_type
            }
        )

        self.assertEqual(container_group.name, container_group_name)
        self.assertEqual(container_group.location, location)
        self.assertEqual(container_group.os_type, os_type)
        self.assertEqual(container_group.containers[0].name, container_group_name)
        self.assertEqual(container_group.containers[0].image, image)
        self.assertEqual(container_group.containers[0].resources.requests.memory_in_gb, memory)
        self.assertEqual(container_group.containers[0].resources.requests.cpu, cpu)

        container_group = self.client.container_groups.get(resource_group.name, container_group_name)

        self.assertEqual(container_group.name, container_group_name)
        self.assertEqual(container_group.location, location)
        self.assertEqual(container_group.os_type, os_type)
        self.assertEqual(container_group.containers[0].name, container_group_name)
        self.assertEqual(container_group.containers[0].image, image)
        self.assertEqual(container_group.containers[0].resources.requests.memory_in_gb, memory)
        self.assertEqual(container_group.containers[0].resources.requests.cpu, cpu)

        container_groups = list(self.client.container_groups.list_by_resource_group(resource_group.name))
        self.assertEqual(len(container_groups), 1)
        self.assertEqual(container_groups[0].name, container_group_name)
        self.assertEqual(container_groups[0].location, location)
        self.assertEqual(container_groups[0].os_type, os_type)
        self.assertEqual(container_groups[0].containers[0].name, container_group_name)
        self.assertEqual(container_groups[0].containers[0].image, image)
        self.assertEqual(container_groups[0].containers[0].resources.requests.memory_in_gb, memory)
        self.assertEqual(container_groups[0].containers[0].resources.requests.cpu, cpu)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
