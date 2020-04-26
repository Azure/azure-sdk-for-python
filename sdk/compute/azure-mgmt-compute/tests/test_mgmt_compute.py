# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   usage: 1/1
#   availability_sets: 7/7
#   log_analytics: 0/2
#   operations: 1/1
#   proximity_placement_groups: 6/6
#   resource_skus: 1/1

import unittest

import azure.mgmt.compute
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtComputeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtComputeTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )

        if self.is_live:
            self.network_client = self.create_mgmt_client(
                azure.mgmt.network.NetworkManagementClient
            )

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute(self, resource_group):

        # List operations (TODO: need swagger file)
        result = self.mgmt_client.operations.list()

        # List usage (TODO: need swagger file)
        result = self.mgmt_client.usage.list(AZURE_LOCATION)

        # Lists all available Resource SKUs[get]
        result = self.mgmt_client.resource_skus.list()

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_availability_sets(self, resource_group):
        AVAILABILITY_SET_NAME = self.get_resource_name("availabilitysets")

        # Create an availability set.[put]
        BODY = {
          "location": "eastus",
          "platform_fault_domain_count": "2",
          "platform_update_domain_count": "20"
        }
        result = self.mgmt_client.availability_sets.create_or_update(resource_group.name, AVAILABILITY_SET_NAME, BODY)

        # Get availability set (TODO: need swagger file)
        result = self.mgmt_client.availability_sets.get(resource_group.name, AVAILABILITY_SET_NAME)

        # List availability sets in a subscription.[get]
        result = self.mgmt_client.availability_sets.list_by_subscription()

        # List availability sets (TODO: need swagger file)
        result = self.mgmt_client.availability_sets.list(resource_group.name)

        # List availability sets available sizes (TODO: need swagger file)
        result = self.mgmt_client.availability_sets.list_available_sizes(resource_group.name, AVAILABILITY_SET_NAME)

        # Update availability sets (TODO: need swagger file)
        BODY = {
          "platform_fault_domain_count": "2",
          "platform_update_domain_count": "20"
        }
        result = self.mgmt_client.availability_sets.update(resource_group.name, AVAILABILITY_SET_NAME, BODY)

        # Delete availability sets (TODO: need a swagger file)
        resout = self.mgmt_client.availability_sets.delete(resource_group.name, AVAILABILITY_SET_NAME)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_proximity_placement_groups(self, resource_group):
        PROXIMITY_PLACEMENT_GROUP_NAME = self.get_resource_name("proximiityplacementgroups")
        
        # Create or Update a proximity placement group.[put]
        BODY = {
          "location": "eastus",
          "proximity_placement_group_type": "Standard"
        }
        result = self.mgmt_client.proximity_placement_groups.create_or_update(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME, BODY)

        # Get a proximity placement group.[get]
        result = self.mgmt_client.proximity_placement_groups.get(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME)

        # List proximity placement groups in a resource group.[get]
        result = self.mgmt_client.proximity_placement_groups.list_by_resource_group(resource_group.name)

        # List proximity placement groups in a subscription. [get]
        result = self.mgmt_client.proximity_placement_groups.list_by_subscription()

        # Update a proximity placement group.[get]
        BODY = {
          "location": "eastus",
          "proximity_placement_group_type": "Standard"
        }
        result = self.mgmt_client.proximity_placement_groups.update(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME, BODY)

        # Delete a proximity placement group.[delete]
        result = self.mgmt_client.proximity_placement_groups.delete(resource_group.name, PROXIMITY_PLACEMENT_GROUP_NAME)

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_compute_log_analytics(self, resource_group):
        pass
        # Export logs which contain all Api requests made to Compute Resource Provider within the given time period broken down by intervals.[post]
        # BODY = {
        #   "interval_length": "FiveMins",
        #   # "blob_container_sas_uri": "https://somesasuri",
        #   "blob_container_sas_uri": SAS_URI,
        #   "from_time": "2018-01-21T01:54:06.862601Z",
        #   "to_time": "2018-01-23T01:54:06.862601Z",
        #   "group_by_resource_name": True
        # }
        # result = self.mgmt_client.log_analytics.export_request_rate_by_interval(AZURE_LOCATION, LOG_ANALYTIC_NAME, BODY)
        # result = result.result()

        # Export logs which contain all throttled Api requests made to Compute Resource Provider within the given time period.[post]
        # BODY = {
        #   # "blob_container_sas_uri": "https://somesasuri",
        #   "blob_container_sas_uri": SAS_URI,
        #   "from_time": "2018-01-21T01:54:06.862601Z",
        #   "to_time": "2018-01-23T01:54:06.862601Z",
        #   "group_by_operation_name": True,
        #   "group_by_resource_name": False
        # }
        # result = self.mgmt_client.log_analytics.export_throttled_requests(LOCATION_NAME, LOG_ANALYTIC_NAME, BODY)
        # result = result.result()
 
