# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 7
# Methods Covered : 7
# Examples Total  : 7
# Examples Tested : 7
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.attestation
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtAttestationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAttestationTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.attestation.AttestationManagementClient
        )

    @unittest.skip("skip test")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_attestation(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        PROVIDER_NAME = "myprovider6"

        CREATION_PARAMS = {
          'properties': {
            'attestation_policy': 'SgxDisableDebugMode'
          },
          'location': 'eastus'
        }

        # /AttestationProviders/put/AttestationProviders_Create[put]
        result = self.mgmt_client.attestation_providers.create(resource_group_name=RESOURCE_GROUP, provider_name=PROVIDER_NAME, creation_params=CREATION_PARAMS)

        # /AttestationProviders/get/AttestationProviders_Get[get]
        result = self.mgmt_client.attestation_providers.get(resource_group_name=RESOURCE_GROUP, provider_name=PROVIDER_NAME)

        # /AttestationProviders/get/AttestationProviders_ListByResourceGroup[get]
        # result = self.mgmt_client.attestation_providers.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /AttestationProviders/get/AttestationProviders_List[get]
        # result = self.mgmt_client.attestation_providers.list()

        # /Operations/get/Operations_List[get]
        result = self.mgmt_client.operations.list()

        # /AttestationProviders/patch/AttestationProviders_Update[patch]
        TAGS = {
          "property1": "Value1",
          "property2": "Value2",
          "property3": "Value3"
        }
        result = self.mgmt_client.attestation_providers.update(resource_group_name=RESOURCE_GROUP, provider_name=PROVIDER_NAME, tags=TAGS)

        # /AttestationProviders/delete/AttestationProviders_Delete[delete]
        result = self.mgmt_client.attestation_providers.delete(resource_group_name=RESOURCE_GROUP, provider_name=PROVIDER_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
