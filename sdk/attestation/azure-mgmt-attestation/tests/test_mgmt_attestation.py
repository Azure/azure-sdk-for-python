# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

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
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_attestation(self, resource_group):

        ATTESTATION_PROVIDER_NAME = "MyAttestationProvider"
        # result = self.mgmt_client.operations.list()

        certs = { 'keys': [ { 'kty': 'RSA'}]}


        azure_operation_poller = self.mgmt_client.attestation_providers.create(resource_group.name, ATTESTATION_PROVIDER_NAME, attestation_policy="MyPolicy", policy_signing_certificates=certs)
        result = azure_operation_poller.result()
        
        result = self.mgmt_client.attestation_providers.get(resource_group.name, ATTESTATION_PROVIDER_NAME)
        
        result = self.mgmt_client.attestation_providers.list()

        result = self.mgmt_client.attestation_providers.list_by_resource_group(resource_group.name)

        result = self.mgmt_client.attestation_providers.delete(resource_group.name, ATTESTATION_PROVIDER_NAME)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()