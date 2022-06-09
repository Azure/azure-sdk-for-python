# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 10
# Methods Covered : 10
# Examples Total  : 11
# Examples Tested : 11
# Coverage %      : 100
# ----------------------

#  service_endpoint_policies: /6
#  service_endpoint_policy_definitions:  /4

import unittest
import pytest

import azure.mgmt.network
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'


@pytest.mark.live_test_only
class TestMgmtNetwork(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.network.NetworkManagementClient
        )
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_network(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        SERVICE_ENDPOINT_POLICY_NAME = "myServiceEndpointPolicy"
        SERVICE_ENDPOINT_POLICY_DEFINITION_NAME = "myServiceEndpointPolicyDefinition"

        # /ServiceEndpointPolicies/put/Create service endpoint policy[put]
        BODY = {
          "location": "eastus"
        }
        result = self.mgmt_client.service_endpoint_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, service_endpoint_policy_name=SERVICE_ENDPOINT_POLICY_NAME, parameters=BODY)
        result = result.result()

        # # /ServiceEndpointPolicies/put/Create service endpoint policy with definition[put]
        # BODY = {
        #   "location": "westus",
        #   "properties": {
        #     "service_endpoint_policy_definitions": [
        #       {
        #         "name": "StorageServiceEndpointPolicyDefinition",
        #         "properties": {
        #           "description": "Storage Service EndpointPolicy Definition",
        #           "service": "Microsoft.Storage",
        #           "service_resources": [
        #             "/subscriptions/subid1",
        #             "/subscriptions/subid1/resourceGroups/storageRg",
        #             "/subscriptions/subid1/resourceGroups/storageRg/providers/Microsoft.Storage/storageAccounts/stAccount"
        #           ]
        #         }
        #       }
        #     ]
        #   }
        # }
        # result = self.mgmt_client.service_endpoint_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, service_endpoint_policy_name=SERVICE_ENDPOINT_POLICY_NAME, parameters=BODY)
        # result = result.result()

        # /ServiceEndpointPolicyDefinitions/put/Create service endpoint policy definition[put]
        BODY = {
          "description": "Storage Service EndpointPolicy Definition",
          "service": "Microsoft.Storage",
          "service_resources": [
            # "/subscriptions/subid1",
            # "/subscriptions/subid1/resourceGroups/storageRg",
            # "/subscriptions/subid1/resourceGroups/storageRg/providers/Microsoft.Storage/storageAccounts/stAccount"
            "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP
          ]
        }
        result = self.mgmt_client.service_endpoint_policy_definitions.begin_create_or_update(resource_group_name=RESOURCE_GROUP, service_endpoint_policy_name=SERVICE_ENDPOINT_POLICY_NAME, service_endpoint_policy_definition_name=SERVICE_ENDPOINT_POLICY_DEFINITION_NAME, service_endpoint_policy_definitions=BODY)
        result = result.result()

        # /ServiceEndpointPolicyDefinitions/get/Get service endpoint definition in service endpoint policy[get]
        result = self.mgmt_client.service_endpoint_policy_definitions.get(resource_group_name=RESOURCE_GROUP, service_endpoint_policy_name=SERVICE_ENDPOINT_POLICY_NAME, service_endpoint_policy_definition_name=SERVICE_ENDPOINT_POLICY_DEFINITION_NAME)

        # /ServiceEndpointPolicyDefinitions/get/List service endpoint definitions in service end point policy[get]
        result = self.mgmt_client.service_endpoint_policy_definitions.list_by_resource_group(resource_group_name=RESOURCE_GROUP, service_endpoint_policy_name=SERVICE_ENDPOINT_POLICY_NAME)

        # /ServiceEndpointPolicies/get/Get service endPoint Policy[get]
        result = self.mgmt_client.service_endpoint_policies.get(resource_group_name=RESOURCE_GROUP, service_endpoint_policy_name=SERVICE_ENDPOINT_POLICY_NAME)

        # /ServiceEndpointPolicies/get/List resource group service endpoint policies[get]
        result = self.mgmt_client.service_endpoint_policies.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /ServiceEndpointPolicies/get/List all service endpoint policy[get]
        result = self.mgmt_client.service_endpoint_policies.list()

        # /ServiceEndpointPolicies/patch/Update service endpoint policy tags[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.service_endpoint_policies.update_tags(resource_group_name=RESOURCE_GROUP, service_endpoint_policy_name=SERVICE_ENDPOINT_POLICY_NAME, parameters=BODY)

        # /ServiceEndpointPolicyDefinitions/delete/Delete service endpoint policy definitions from service endpoint policy[delete]
        result = self.mgmt_client.service_endpoint_policy_definitions.begin_delete(resource_group_name=RESOURCE_GROUP, service_endpoint_policy_name=SERVICE_ENDPOINT_POLICY_NAME, service_endpoint_policy_definition_name=SERVICE_ENDPOINT_POLICY_DEFINITION_NAME)
        result = result.result()

        # /ServiceEndpointPolicies/delete/Delete service endpoint policy[delete]
        result = self.mgmt_client.service_endpoint_policies.begin_delete(resource_group_name=RESOURCE_GROUP, service_endpoint_policy_name=SERVICE_ENDPOINT_POLICY_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
