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
# Examples Total  : 10
# Examples Tested : 9
# Coverage %      : 90
# ----------------------

import unittest

import azure.mgmt.storageimportexport
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtXxxMgmtClientNameTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtXxxMgmtClientNameTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.storageimportexport.StorageImportExportMgmtClientName
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_storageimportexport(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"

        # /Jobs/put/Create job[put]
        BODY = {
          "location": "West US",
          "properties": {
            "storage_account_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ClassicStorage/storageAccounts/" + STORAGE_ACCOUNT_NAME + "",
            "job_type": "Import",
            "return_address": {
              "recipient_name": "Tets",
              "street_address1": "Street1",
              "street_address2": "street2",
              "city": "Redmond",
              "state_or_province": "wa",
              "postal_code": "98007",
              "country_or_region": "USA",
              "phone": "4250000000",
              "email": "Test@contoso.com"
            },
            "diagnostics_path": "waimportexport",
            "log_level": "Verbose",
            "backup_drive_manifest": True,
            "drive_list": [
              {
                "drive_id": "9CA995BB",
                "bit_locker_key": "238810-662376-448998-450120-652806-203390-606320-483076",
                "manifest_file": "\\DriveManifest.xml",
                "manifest_hash": "109B21108597EF36D5785F08303F3638",
                "drive_header_hash": ""
              }
            ]
          }
        }
        result = self.mgmt_client.jobs.create(resource_group.name, JOB_NAME, BODY)

        # /Jobs/get/Get job[get]
        result = self.mgmt_client.jobs.get(resource_group.name, JOB_NAME)

        # /Locations/get/Get locations[get]
        result = self.mgmt_client.locations.get(LOCATION_NAME)

        # /BitLockerKeys/post/List BitLocker Keys for drives in a job[post]
        BODY = {}
        result = self.mgmt_client.bit_locker_keys.list(resource_group.name, JOB_NAME, BODY)

        # /Jobs/get/List jobs in a resource group[get]
        result = self.mgmt_client.jobs.list_by_resource_group(resource_group.name)

        # /Jobs/get/List jobs in a subscription[get]
        result = self.mgmt_client.jobs.list_by_subscription()

        # /Locations/get/List locations[get]
        result = self.mgmt_client.locations.list()

        # /Jobs/patch/Update job[patch]
        BODY = {
          "properties": {
            "state": "",
            "log_level": "Verbose",
            "backup_drive_manifest": True
          }
        }
        result = self.mgmt_client.jobs.update(resource_group.name, JOB_NAME, BODY)

        # /Jobs/delete/Delete job[delete]
        result = self.mgmt_client.jobs.delete(resource_group.name, JOB_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
