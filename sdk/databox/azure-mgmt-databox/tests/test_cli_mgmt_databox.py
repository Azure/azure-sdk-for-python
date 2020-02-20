# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 16
# Methods Covered : 16
# Examples Total  : 21
# Examples Tested : 17
# Coverage %      : 80.95238095238095
# ----------------------

import os
import unittest

import azure.mgmt.databox
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtDataBoxTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtDataBoxTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.databox.DataBoxManagementClient
        )
        self.storage_client = self.create_mgmt_client(
            azure.mgmt.storage.StorageManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_databox(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        SUBSCRIPTION_ID = None
        if self.is_live:
            SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", None)
        if not SUBSCRIPTION_ID:
            SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        STORAGE_ACCOUNT_NAME = 'databoxaccountabc'
        JOB_NAME = 'testjob'

        # JobsCreate[put]
        BODY = {
          "details": {
            "job_details_type": "DataBox",
            "contact_details": {
              "contact_name": "Public SDK Test",
              "phone": "1234567890",
              "phone_extension": "1234",
              "email_list": [
                "testing@microsoft.com"
              ]
            },
            "shipping_address": {
              "street_address1": "16 TOWNSEND ST",
              "street_address2": "Unit 1",
              "city": "San Francisco",
              "state_or_province": "CA",
              "country": "US",
              "postal_code": "94107",
              "company_name": "Microsoft",
              "address_type": "Commercial"
            },
            "destination_account_details": [
              {
                "storage_account_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + "",
                "data_destination_type": "StorageAccount"
              }
            ]
          },
          "location": "westus",
          "sku": {
            "name": "DataBox"
          }
        }
        result = self.mgmt_client.jobs.create(resource_group.name, JOB_NAME, BODY)
        result = result.result()

        # JobsGet4[get]
        result = self.mgmt_client.jobs.get(resource_group.name, JOB_NAME)

        # JobsGet3[get]
        result = self.mgmt_client.jobs.get(resource_group.name, JOB_NAME)

        # JobsGet2[get]
        result = self.mgmt_client.jobs.get(resource_group.name, JOB_NAME)

        # JobsGet1[get]
        result = self.mgmt_client.jobs.get(resource_group.name, JOB_NAME)

        # JobsGet[get]
        result = self.mgmt_client.jobs.get(resource_group.name, JOB_NAME)

        # JobsGet5[get]
        result = self.mgmt_client.jobs.get(resource_group.name, JOB_NAME)

        # JobsListByResourceGroup[get]
        result = self.mgmt_client.jobs.list_by_resource_group(resource_group.name)

        # JobsList[get]
        result = self.mgmt_client.jobs.list()

        # OperationsGet[get]
        result = self.mgmt_client.operations.list()

        """
        # BookShipmentPickupPost[post]
        BODY = {
          "start_time": "2019-09-20T18:30:00Z",
          "end_time": "2019-09-22T18:30:00Z",
          "shipment_location": "Front desk"
        }
        result = self.mgmt_client.jobs.book_shipment_pick_up(resource_group.name, JOB_NAME, BODY, polling=False)

        # JobsListCredentials[post]
        result = self.mgmt_client.jobs.list_credentials(resource_group.name, JOB_NAME, polling=False)
        """

        # JobsPatch[patch]
        BODY = {
          "properties": {
            "details": {
              "contact_details": {
                "contact_name": "Update Job",
                "phone": "1234567890",
                "phone_extension": "1234",
                "email_list": [
                  "testing@microsoft.com"
                ]
              },
              # TODO: raise SsemUserErrorShippingAddressIsNotEditable
              # "shipping_address": {
              #   "street_address1": "16 TOWNSEND ST",
              #   "street_address2": "Unit 1",
              #   "city": "San Francisco",
              #   "state_or_province": "CA",
              #   "country": "US",
              #   "postal_code": "94107",
              #   "company_name": "Microsoft",
              #   "address_type": "Commercial"
              # }
            }
          }
        }
        result = self.mgmt_client.jobs.update(resource_group.name, JOB_NAME, BODY)
        result = result.result()

        # JobsCancelPost[post]
        BODY = {
          "reason": "CancelTest"
        }
        result = self.mgmt_client.jobs.cancel(resource_group.name, JOB_NAME, BODY)

        """
        # ValidateAddressPost[post]
        BODY = {
          "validation_type": "ValidateAddress",
          "shipping_address": {
            "street_address1": "16 TOWNSEND ST",
            "street_address2": "Unit 1",
            "city": "San Francisco",
            "state_or_province": "CA",
            "country": "US",
            "postal_code": "94107",
            "company_name": "Microsoft",
            "address_type": "Commercial"
          },
          "device_type": "DataBox"
        }
        result = self.mgmt_client.service.validate_address_method(LOCATION_NAME, BODY, polling=False)

        # AvailableSkusPost[post]
        BODY = {
          "country": "US",
          "location": "westus",
          "transfer_type": "ImportToAzure"
        }
        result = self.mgmt_client.service.list_available_skus(LOCATION_NAME, BODY, polling=False)
        """

        # JobsDelete[delete]
        result = self.mgmt_client.jobs.delete(resource_group.name, JOB_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
