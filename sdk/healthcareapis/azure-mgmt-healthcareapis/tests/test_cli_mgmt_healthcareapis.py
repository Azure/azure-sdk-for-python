# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 9
# Methods Covered : 9
# Examples Total  : 9
# Examples Tested : 9
# Coverage %      : 100
# ----------------------

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
    
    @unittest.skip("skip test")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_healthcareapis(self, resource_group):

        SERVICE_NAME = "myapimrndxyzabc"
        OPERATIONRESULT_NAME = "read"
        LOCATION_NAME = AZURE_LOCATION

        # ServicePut[put]
        BODY = {
          "location": "eastus",
          "kind": "fhir",
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

        # OperationResultsGet[get]
        result = self.mgmt_client.operation_results.get(LOCATION_NAME, OPERATIONRESULT_NAME)

        # ServiceGet[get]
        result = self.mgmt_client.services.get(resource_group.name, SERVICE_NAME)

        # ServiceListByResourceGroup[get]
        result = self.mgmt_client.services.list_by_resource_group(resource_group.name)

        # ServiceList[get]
        result = self.mgmt_client.services.list()

        # OperationsList[get]
        result = self.mgmt_client.operations.list()

        # ServicePatch[patch]
        BODY = {
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.mgmt_client.services.update(resource_group.name, SERVICE_NAME, BODY)
        result = result.result()

        # CheckNameAvailabilityPost[post]
        BODY = {
          "type": "Microsoft.HealthcareApis/services",
          "name": "serviceName"
        }
        NAME = SERVICE_NAME + 'ABC'
        TYPE = "Microsoft.HealthcareApis/services"
        result = self.mgmt_client.services.check_name_availability(NAME, TYPE)

        # ServiceDelete[delete]
        result = self.mgmt_client.services.delete(resource_group.name, SERVICE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
