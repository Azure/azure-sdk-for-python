# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.containerservice.models
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtContainerServiceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtContainerServiceTest, self).setUp()
        self.cs_client = self.create_mgmt_client(
            azure.mgmt.containerservice.ContainerServiceClient
        )

        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_container(self):
        container_name = self.get_resource_name('pycontainer')
        
        # https://msdn.microsoft.com/en-us/library/azure/mt711471.aspx
        async_create = self.cs_client.container_services.create_or_update(
            self.group_name,
            container_name,
            {
                'location': self.region,
                "orchestrator_profile": {
                    "orchestrator_type": "DCOS"
                },
                "master_profile": {
                    "count": 1,
                    "dns_prefix": "MasterPrefixTest"
                },
                "agent_pool_profiles": [{
                    "name": "AgentPool1",
                    "count": 3,
                    "vm_size": "Standard_A1",
                        "dns_prefix": "AgentPrefixTest"
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
            retries=0
        )
        container = async_create.result()

        container = self.cs_client.container_services.get(
            self.group_name,
            container.name
        )

        containers = list(self.cs_client.container_services.list_by_resource_group(
            self.group_name
        ))
        self.assertEqual(len(containers), 1)

        containers = list(self.cs_client.container_services.list())
        self.assertEqual(len(containers), 1)

        async_delete = self.cs_client.container_services.delete(
            self.group_name,
            container.name
        )
        async_delete.wait()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
