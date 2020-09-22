# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 12
# Methods Covered : 12
# Examples Total  : 12
# Examples Tested : 12
# Coverage %      : 100
# ----------------------

# Current Operation Coverage:
#   DigitalTwins: 7/7
#   DigitalTwinsEndpoint: 0/4
#   Operations: 1/1

import unittest

import azure.mgmt.digitaltwins
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer, ResourceGroupPreparer

AZURE_LOCATION = 'westus2'

class MgmtAzureDigitalTwinsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAzureDigitalTwinsTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.digitaltwins.AzureDigitalTwinsManagementClient,
            api_version="2020-03-01-preview"
        )

        if self.is_live:
            from azure.mgmt.servicebus import ServiceBusManagementClient
            self.servicebus_client = self.create_mgmt_client(
                ServiceBusManagementClient
            )

    # use track1 sdk
    def create_servicebus(self, group_name, namespace_name, rule_name):
    
        BODY = {
          "sku": {
            "name": "Premium",
            "tier": "Premium"
          },
          "location": AZURE_LOCATION,
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.servicebus_client.namespaces.create_or_update(resource_group_name=group_name, namespace_name=namespace_name, parameters=BODY)
        namespace = result.result()

        BODY = {
          "rights": [
            "Listen",
            "Send"
          ]
        }
        result = self.servicebus_client.namespaces.create_or_update_authorization_rule(resource_group_name=group_name, namespace_name=namespace_name, authorization_rule_name=rule_name, rights=BODY["rights"])

        result = self.servicebus_client.namespaces.list_keys(resource_group_name=group_name, namespace_name=namespace_name, authorization_rule_name=rule_name)
        return {"primary_connection_string": result.primary_connection_string, "secondary_connection_string": result.secondary_connection_string}

    # msrest.exceptions.ValidationError: Parameter 'resource_group_name' must have length less than 64.
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_digitaltwins(self, resource_group):

        # UNIQUE = resource_group.name[-4:]
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        RESOURCE_NAME = "myResourcexxx"
        ENDPOINT_NAME = "myEndpoint"
        NAMESPACE_NAME = "myNamespacexxyyzzyx"
        AUTHORIZATION_RULE_NAME = "myrulename"

        # if self.is_live:
        #     servicebus = self.create_servicebus(RESOURCE_GROUP, NAMESPACE_NAME, AUTHORIZATION_RULE_NAME)
        # else:
        #     servicebus = {"primary_connection_string": "abc", "secondary_connection_string": "abc"}

#--------------------------------------------------------------------------
        # /DigitalTwins/put/Put a DigitalTwinsInstance resource[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.digital_twins.begin_create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, digital_twins_create=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DigitalTwinsEndpoint/put/Put a DigitalTwinsInstance resource[put]
#--------------------------------------------------------------------------
        BODY = {
          "properties": {
            "endpoint_type": "ServiceBus",
            "primary_connection_string": "Endpoint=sb://mysb.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=xyzxyzoX4=",
            # "primary_connection_string": servicebus.get("primary_connection_string"),
            "secondary_connection_string": "Endpoint=sb://mysb.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=xyzxyzoX4="
            # "secondary_connection_string": servicebus.get("secondary_connection_string")
          }
        }
        # result = self.mgmt_client.digital_twins_endpoint.begin_create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, endpoint_name=ENDPOINT_NAME, endpoint_description=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /DigitalTwinsEndpoint/get/Get a DigitalTwinsInstance endpoint[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.digital_twins_endpoint.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, endpoint_name=ENDPOINT_NAME)

#--------------------------------------------------------------------------
        # /DigitalTwinsEndpoint/get/Get a DigitalTwinsInstance endpoints[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.digital_twins_endpoint.list(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

#--------------------------------------------------------------------------
        # /DigitalTwins/get/Get a DigitalTwinsInstance resource[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.digital_twins.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

#--------------------------------------------------------------------------
        # /DigitalTwins/get/Get DigitalTwinsInstance resources by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.digital_twins.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /DigitalTwins/get/Get DigitalTwinsInstance resources by subscription[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.digital_twins.list()

#--------------------------------------------------------------------------
        # /Operations/get/Get available operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.operations.list()

#--------------------------------------------------------------------------
        # /DigitalTwins/patch/Patch a DigitalTwinsInstance resource[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "purpose": "dev"
          }
        }
        result = self.mgmt_client.digital_twins.begin_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, digital_twins_patch_description=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DigitalTwins/post/Check name Availability[post]
#--------------------------------------------------------------------------
        BODY = {
          "name": "myadtinstance",
          "type": "Microsoft.DigitalTwins/digitalTwinsInstances"
        }
        result = self.mgmt_client.digital_twins.check_name_availability(location=AZURE_LOCATION, digital_twins_instance_check_name=BODY)

#--------------------------------------------------------------------------
        # /DigitalTwinsEndpoint/delete/Delete a DigitalTwinsInstance endpoint[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.digital_twins_endpoint.begin_delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, endpoint_name=ENDPOINT_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /DigitalTwins/delete/Delete a DigitalTwinsInstance resource[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.digital_twins.begin_delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
