# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   Certificates: 0/6
#   CertificateRegistrationProvider: 0/1

import unittest

import azure.mgmt.web
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtWebSiteTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtWebSiteTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.web.WebSiteManagementClient
        )

    @unittest.skip("Operation returned an invalid status 'Not Found' when create certificate")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_certificate(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        NAME = "myname"

#--------------------------------------------------------------------------
        # /Certificates/put/Create Or Update Certificate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "host_names": [
            "ServerCert"
          ],
          "password": "SWsSsd__233$Sdsds#%Sd!"
        }
        result = self.mgmt_client.certificates.create_or_update(resource_group_name=RESOURCE_GROUP, name=NAME, certificate_envelope=BODY)

#--------------------------------------------------------------------------
        # /Certificates/get/Get Certificate[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.certificates.get(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /Certificates/get/List Certificates by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.certificates.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /Certificates/get/List Certificates for subscription[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.certificates.list()

#--------------------------------------------------------------------------
        # /CertificateRegistrationProvider/get/List operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.certificate_registration_provider.list_operations()

#--------------------------------------------------------------------------
        # /Certificates/patch/Patch Certificate[patch]
#--------------------------------------------------------------------------
        BODY = {
          "password": "SWsSsd__233$Sdsds#%Sd!"
        }
        result = self.mgmt_client.certificates.update(resource_group_name=RESOURCE_GROUP, name=NAME, certificate_envelope=BODY)

#--------------------------------------------------------------------------
        # /Certificates/delete/Delete Certificate[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.certificates.delete(resource_group_name=RESOURCE_GROUP, name=NAME)
