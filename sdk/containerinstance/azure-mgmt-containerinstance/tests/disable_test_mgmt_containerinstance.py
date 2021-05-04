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
        livenessprob_period_seconds = 5
        log_analytics_workspace_id = 'workspaceId'
        log_analytics_workspace_key = 'workspaceKey'
        identity_system_assigned = 'SystemAssigned'

        empty_volume = Volume(name='empty-volume', empty_dir={})
        volume_mount = VolumeMount(name='empty-volume', mount_path='/mnt/mydir')

        poller = self.client.container_groups.create_or_update(
            resource_group.name,
            container_group_name,
            {
                'identity': {
                    'type': identity_system_assigned
                },
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
                    'volume_mounts': [volume_mount],
                    'liveness_probe': {
                        'exec': {
                            'command': [
                                'cat'
                                '/tmp/healthy'
                            ]
                        },
                        'periodSeconds': livenessprob_period_seconds
                    }
                }],
                'os_type': os_type,
                'restart_policy': restart_policy,
                'diagnostics': {
                    'log_analytics': {
                        'workspace_id': log_analytics_workspace_id,
                        'workspace_key': log_analytics_workspace_key
                    }
                },
                'volumes': [empty_volume],
            }
        )
        container_group = poller.result()

        self.assertEqual(container_group.name, container_group_name)
        self.assertEqual(container_group.location, location)
        self.assertEqual(container_group.identity.type, identity_system_assigned)
        self.assertEqual(container_group.os_type, os_type)
        self.assertEqual(container_group.restart_policy, restart_policy)
        self.assertEqual(container_group.diagnostics.log_analytics.workspace_id, log_analytics_workspace_id)
        self.assertEqual(container_group.containers[0].name, container_group_name)
        self.assertEqual(container_group.containers[0].image, image)
        self.assertEqual(container_group.containers[0].resources.requests.memory_in_gb, memory)
        self.assertEqual(container_group.containers[0].resources.requests.cpu, cpu)
        self.assertEqual(container_group.volumes[0].name, empty_volume.name)
        self.assertEqual(container_group.containers[0].liveness_probe.period_seconds, livenessprob_period_seconds)

        container_group = self.client.container_groups.get(resource_group.name, container_group_name)

        self.assertEqual(container_group.name, container_group_name)
        self.assertEqual(container_group.location, location)
        self.assertEqual(container_group.os_type, os_type)
        self.assertEqual(container_group.restart_policy, restart_policy)
        self.assertEqual(container_group.diagnostics.log_analytics.workspace_id, log_analytics_workspace_id)
        self.assertEqual(container_group.containers[0].name, container_group_name)
        self.assertEqual(container_group.containers[0].image, image)
        self.assertEqual(container_group.containers[0].resources.requests.memory_in_gb, memory)
        self.assertEqual(container_group.containers[0].resources.requests.cpu, cpu)
        self.assertEqual(container_group.volumes[0].name, empty_volume.name)
        self.assertEqual(container_group.containers[0].liveness_probe.period_seconds, livenessprob_period_seconds)

        container_groups = list(self.client.container_groups.list_by_resource_group(resource_group.name))
        self.assertEqual(len(container_groups), 1)
        self.assertEqual(container_groups[0].name, container_group_name)
        self.assertEqual(container_groups[0].location, location)
        self.assertEqual(container_groups[0].os_type, os_type)
        self.assertEqual(container_groups[0].restart_policy, restart_policy)
        self.assertEqual(container_groups[0].diagnostics.log_analytics.workspace_id, log_analytics_workspace_id)
        self.assertEqual(container_groups[0].containers[0].name, container_group_name)
        self.assertEqual(container_groups[0].containers[0].image, image)
        self.assertEqual(container_groups[0].containers[0].resources.requests.memory_in_gb, memory)
        self.assertEqual(container_groups[0].containers[0].resources.requests.cpu, cpu)
        self.assertEqual(container_groups[0].volumes[0].name, empty_volume.name)
        self.assertEqual(container_groups[0].containers[0].liveness_probe.period_seconds, livenessprob_period_seconds)

        # Testing Container_Execute_Command
        terminal_size = {
            "rows": 24,
            "cols": 80
        }
        command = "/bin/bash"
        containerExecResponse = self.client.container.execute_command(resource_group.name, container_group.name, container_group.containers[0].name, command, terminal_size)
        self.assertNotEqual(containerExecResponse.web_socket_uri, None)
        self.assertNotEqual(containerExecResponse.password, None)

        # Testing Container_List_Logs
        containerLogResponse = self.client.container.list_logs(resource_group.name, container_group.name, container_group.containers[0].name)

        # Testing Restart Container Group
        poller = self.client.container_groups.restart(resource_group.name, container_group_name)
        poller.result()



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
