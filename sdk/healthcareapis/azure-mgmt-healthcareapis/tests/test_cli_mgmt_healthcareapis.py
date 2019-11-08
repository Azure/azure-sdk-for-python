# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest

import azure.mgmt.healthcareapis
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtHealthcareApisTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtHealthcareApisTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.healthcareapis.HealthcareApisManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_healthcareapis(self, resource_group):

        SERVICE_NAME = "myhcasrvanxy"

        # Check name availability[post]
        result = self.mgmt_client.services.check_name_availability(type="Microsoft.HealthcareApis/services", name=SERVICE_NAME)

        # Create or Update a service with all parameters[put]
        BODY = {
          "location": "westus2",
          "kind": "fhir-R4",
          "properties": {
            "access_policies": [
              {
                "object_id": "c487e7d1-3210-41a3-8ccc-e9372b78da47"
              },
              {
                "object_id": "5b307da8-43d4-492b-8b66-b0294ade872f"
              }
            ],
            "cosmos_db_configuration": {
              "offer_throughput": "1000"
            },
            "authentication_configuration": {
              "authority": "https://login.microsoftonline.com/abfde7b2-df0f-47e6-aabf-2462b07508dc",
              "audience": "https://azurehealthcareapis.com",
              "smart_proxy_enabled": True
            },
            "cors_configuration": {
              "origins": [
                "*"
              ],
              "headers": [
                "*"
              ],
              "methods": [
                "DELETE",
                "GET",
                "OPTIONS",
                "PATCH",
                "POST",
                "PUT"
              ],
              "max_age": "1440",
              "allow_credentials": False
            }
          }
        }
        result = self.mgmt_client.services.create_or_update(resource_group.name, SERVICE_NAME, BODY)
        result = result.result()

        # Delete service[delete]
        result = self.mgmt_client.services.delete(resource_group.name, SERVICE_NAME)
        result = result.result()

        # Create or Update a service with minimum parameters[put]
        BODY = {
          "location": "westus2",
          "kind": "fhir-R4",
          "properties": {
            "access_policies": [
              {
                "object_id": "c487e7d1-3210-41a3-8ccc-e9372b78da47"
              }
            ]
          }
        }
        result = self.mgmt_client.services.create_or_update(resource_group.name, SERVICE_NAME, BODY)
        result = result.result()

        # List all services in subscription[get]
        result = self.mgmt_client.services.list()

        # List all services in resource group[get]
        result = self.mgmt_client.services.list_by_resource_group(resource_group.name, )

        # Delete service[delete]
        result = self.mgmt_client.services.delete(resource_group.name, SERVICE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()