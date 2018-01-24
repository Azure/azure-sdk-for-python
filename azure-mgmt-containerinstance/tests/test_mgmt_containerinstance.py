# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest

import azure.mgmt.containerinstance
from azure.mgmt.containerinstance.models import Volume, VolumeMount

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
        restart_policy = 'OnFailure'

        empty_volume = Volume(name='empty-volume', empty_dir={})
        volume_mount = VolumeMount(name='empty-volume', mount_path='/mnt/mydir')

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
                    },
                    'volume_mounts': [volume_mount]
                }],
                'os_type': os_type,
                'restart_policy': restart_policy,
                'volumes': [empty_volume]
            }
        )

        self.assertEqual(container_group.name, container_group_name)
        self.assertEqual(container_group.location, location)
        self.assertEqual(container_group.os_type, os_type)
        self.assertEqual(container_group.restart_policy, restart_policy)
        self.assertEqual(container_group.containers[0].name, container_group_name)
        self.assertEqual(container_group.containers[0].image, image)
        self.assertEqual(container_group.containers[0].resources.requests.memory_in_gb, memory)
        self.assertEqual(container_group.containers[0].resources.requests.cpu, cpu)
        self.assertEqual(container_group.volumes[0].name, empty_volume.name)

        container_group = self.client.container_groups.get(resource_group.name, container_group_name)

        self.assertEqual(container_group.name, container_group_name)
        self.assertEqual(container_group.location, location)
        self.assertEqual(container_group.os_type, os_type)
        self.assertEqual(container_group.restart_policy, restart_policy)
        self.assertEqual(container_group.containers[0].name, container_group_name)
        self.assertEqual(container_group.containers[0].image, image)
        self.assertEqual(container_group.containers[0].resources.requests.memory_in_gb, memory)
        self.assertEqual(container_group.containers[0].resources.requests.cpu, cpu)
        self.assertEqual(container_group.volumes[0].name, empty_volume.name)

        container_groups = list(self.client.container_groups.list_by_resource_group(resource_group.name))
        self.assertEqual(len(container_groups), 1)
        self.assertEqual(container_groups[0].name, container_group_name)
        self.assertEqual(container_groups[0].location, location)
        self.assertEqual(container_groups[0].os_type, os_type)
        self.assertEqual(container_groups[0].restart_policy, restart_policy)
        self.assertEqual(container_groups[0].containers[0].name, container_group_name)
        self.assertEqual(container_groups[0].containers[0].image, image)
        self.assertEqual(container_groups[0].containers[0].resources.requests.memory_in_gb, memory)
        self.assertEqual(container_groups[0].containers[0].resources.requests.cpu, cpu)
        self.assertEqual(container_groups[0].volumes[0].name, empty_volume.name)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
