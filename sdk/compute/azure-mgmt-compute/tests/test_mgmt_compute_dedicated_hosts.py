# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   dedicated_hosts: 5/5
#   dedicated_host_groups: 6/6

import unittest

import azure.mgmt.compute
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtComputeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtComputeTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_dedicated_hosts(self, resource_group):
        HOST_GROUP_NAME = self.get_resource_name("hostgroup")
        HOST_NAME = self.get_resource_name("hostname")

        # Create or update a dedicated host group.[put]
        BODY = {
          "location": "eastus",
          "tags": {
            "department": "finance"
          },
          "zones": [
            "1"
          ],
          "platform_fault_domain_count": "3"
        }
        result = self.mgmt_client.dedicated_host_groups.create_or_update(resource_group.name, HOST_GROUP_NAME, BODY)
        
        # Create or update a dedicated host .[put]
        BODY = {
          "location": "eastus",
          "tags": {
            "department": "HR"
          },
          "platform_fault_domain": "1",
          "sku": {
            "name": "DSv3-Type1"
          }
        }
        result = self.mgmt_client.dedicated_hosts.begin_create_or_update(resource_group.name, HOST_GROUP_NAME, HOST_NAME, BODY)
        result = result.result()

        # Get a dedicated host group.[get]
        result = self.mgmt_client.dedicated_host_groups.get(resource_group.name, HOST_GROUP_NAME)

        # Get a dedicated host.[get]
        result = self.mgmt_client.dedicated_hosts.get(resource_group.name, HOST_GROUP_NAME, HOST_NAME)

        # List dedicated host groups in a resource group (TODO: need swagger file)
        result = self.mgmt_client.dedicated_host_groups.list_by_resource_group(resource_group.name)

        # List dedicated hosts in host group (TODO: need swagger file)
        result = self.mgmt_client.dedicated_hosts.list_by_host_group(resource_group.name, HOST_GROUP_NAME)

        # List dedicated host groups in a subscription (TODO: need swagger file)
        result = self.mgmt_client.dedicated_host_groups.list_by_subscription()

        # Update a dedicated host group.[put]
        BODY = {
          "tags": {
            "department": "finance"
          },
          "platform_fault_domain_count": "3"
        }
        result = self.mgmt_client.dedicated_host_groups.update(resource_group.name, HOST_GROUP_NAME, BODY)

        # Update a dedicated host (TODO: need swagger file )
        BODY = {
          "tags": {
            "department": "HR"
          },
        }
        result = self.mgmt_client.dedicated_hosts.begin_update(resource_group.name, HOST_GROUP_NAME, HOST_NAME, BODY)
        result = result.result()

        # Delete a dedicated host (TODO: need swagger file)
        result = self.mgmt_client.dedicated_hosts.begin_delete(resource_group.name, HOST_GROUP_NAME, HOST_NAME)
        result = result.result()

        # Delete a dedicated host group (TODO: need swagger file)
        result = self.mgmt_client.dedicated_host_groups.delete(resource_group.name, HOST_GROUP_NAME)
