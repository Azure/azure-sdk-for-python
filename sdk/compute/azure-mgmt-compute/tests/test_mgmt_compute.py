# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   usage: 1/1
#   availability_sets: 7/7
#   log_analytics: 2/2
#   operations: 1/1
#   proximity_placement_groups: 6/6
#   resource_skus: 1/1

import os
import datetime as dt
import unittest

import pytest
import azure.mgmt.compute
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtCompute(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        # self.re_replacer.register_pattern_pair('"value":".{88}"', '"value":"FakeValue"')
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.compute.ComputeManagementClient
        )

        from azure.mgmt.storage import StorageManagementClient
        self.storage_client = self.create_mgmt_client(
            StorageManagementClient
        )

    def create_sas_uri(self, group_name, location, storage_account_name):
        from azure.mgmt.storage.models import BlobContainer
        from azure.storage.blob import generate_account_sas, AccountSasPermissions, ContainerClient, ResourceTypes
        BODY = {
          "sku": {
            "name": "Standard_GRS"
          },
          "kind": "StorageV2",  # Storage v2 support policy
          "location": location,
          "encryption": {
            "services": {
              "file": {
                "key_type": "Account",
                "enabled": True
              },
              "blob": {
                "key_type": "Account",
                "enabled": True
              }
            },
            "key_source": "Microsoft.Storage"
          },

          "tags": {
            "key1": "value1",
            "key2": "value2"
          }
        }
        result = self.storage_client.storage_accounts.begin_create(
            group_name,
            storage_account_name,
            BODY
        )
        storage_account = result.result()

        # result = self.storage_client.blob_containers.create(
        #     group_name,
        #     storage_account_name,
        #     "foo",
        #     {}
        # )
        # result = result.result()

        keys = self.storage_client.storage_accounts.list_keys(
            group_name,
            storage_account_name
        ).keys

        sas_token = generate_account_sas(
            account_name=storage_account_name,
            account_key=keys[0].value,
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True, list=True),
            start=dt.datetime.now() - dt.timedelta(hours=24),
            expiry=dt.datetime.now() - dt.timedelta(days=8)
        )
        
        container_client = ContainerClient(
            storage_account.primary_endpoints.blob.rstrip("/"),
            credential="?" + sas_token,
            container_name="foo",
            blob_name="default"
        )
        # self.scrubber.register_name_pair(container_client.url, "fakeuri")
        return container_client.url
        # container_client.create_container()
        # return container_client.url + "?" + sas_token

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_compute(self, resource_group):

        # List operations (TODO: need swagger file)
        result = self.mgmt_client.operations.list()

        # List usage (TODO: need swagger file)
        result = self.mgmt_client.usage.list(AZURE_LOCATION)

        # Lists all available Resource SKUs[get]
        result = self.mgmt_client.resource_skus.list()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
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

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
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
