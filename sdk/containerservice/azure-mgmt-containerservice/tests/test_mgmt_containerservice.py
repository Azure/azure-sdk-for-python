# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.containerservice
from azure.mgmt.containerservice.models import ContainerServiceVMSizeTypes

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtContainerServiceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtContainerServiceTest, self).setUp()
        self.cs_client = self.create_mgmt_client(
            azure.mgmt.containerservice.ContainerServiceClient
        )
        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )
    
    def create_subet(self, group_name, location):
        # Create virtual network
        self.network_client.virtual_networks.create_or_update(
            group_name,
            "vnet",
            {
                "address_space": {
                    "address_prefixes": [
                    "10.0.0.0/8"
                    ]
                },
                "location": location 
            }
        ).result()

        # Create subnet
        subnet = self.network_client.subnets.create_or_update(
            group_name,
            "vnet",
            "v-subnet",
            {
                "address_prefix": "10.0.0.0/8"
            }
        ).result()

        return subnet.id

    @ResourceGroupPreparer(location='eastus')
    def test_container(self, resource_group, location):
        container_name = self.get_resource_name('pycontainer')

        if self.is_live:
            subnet_id = self.create_subet(resource_group.name, location)
        else:
            subnet_id = "<fake_id>"
        
        async_create = self.cs_client.container_services.create_or_update(
            resource_group.name,
            container_name,
            {
                'location': location,
                "orchestrator_profile": {
                    "orchestrator_type": "Swarm"
                },
                "master_profile": {
                    "count": 1,
                    "dns_prefix": "masterPrefixTest",
                    "vm_size": ContainerServiceVMSizeTypes.standard_d2_v2,
                    "vnet_subnet_id": subnet_id
                },
                "agent_pool_profiles": [{
                    "name": "agentpool0",
                    "count": 3,
                    "vm_size": "Standard_A2_v2",
                    # "dns_prefix": "AgentPrefixTest" - Optional in latest version
                    "vnet_subnet_id": subnet_id
                }],
                "linux_profile": {
                    "admin_username": "acslinuxadmin",
                    "ssh": {
                       "public_keys": [{
                            "key_data": "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAlj9UC6+57XWVu0fd6zqXa256EU9EZdoLGE3TqdZqu9fvUvLQOX2G0d5DmFhDCyTmWLQUx3/ONQ9RotYmHGymBIPQcpx43nnxsuihAILcpGZ5NjCj4IOYnmhdULxN4ti7k00S+udqokrRYpmwt0N4NA4VT9cN+7uJDL8Opqa1FYu0CT/RqSW+3aoQ0nfGj11axoxM37FuOMZ/c7mBSxvuI9NsDmcDQOUmPXjlgNlxrLzf6VcjxnJh4AO83zbyLok37mW/C7CuNK4WowjPO1Ix2kqRHRxBrzxYZ9xqZPc8GpFTw/dxJEYdJ3xlitbOoBoDgrL5gSITv6ESlNqjPk6kHQ== azureuser@linuxvm"
                       }]
                    }
                },
            },
        )
        container = async_create.result()

        container = self.cs_client.container_services.get(
            resource_group.name,
            container.name
        )

        containers = list(self.cs_client.container_services.list_by_resource_group(
            resource_group.name
        ))
        self.assertEqual(len(containers), 1)

        containers = list(self.cs_client.container_services.list())
        self.assertGreaterEqual(len(containers), 1)

        async_delete = self.cs_client.container_services.delete(
            resource_group.name,
            container.name
        )
        async_delete.wait()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
