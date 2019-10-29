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

        ATTESTATION_PROVIDER_NAME = "myattestationprovider"
        # result = self.mgmt_client.operations.list()

        certs = { 'keys': 
       [
         {"kty":"EC",
          "crv":"P-256",
          "x":"MKBCTNIcKUSDii11ySs3526iDZ8AiTo7Tu6KPAqv7D4",
          "y":"4Etl6SRW2YiLUrN5vfvVHuhp7x8PxltmWWlbbM4IFyM",
          "use":"enc",
          "kid":"1"},

         {"kty":"RSA",
          "n": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw",
          "e":"AQAB",
          "alg":"RS256",
          "kid":"2011-04-29"}
       ]
     }


        azure_operation_poller = self.mgmt_client.attestation_providers.create(resource_group.name, ATTESTATION_PROVIDER_NAME, policy_signing_certificates=certs)
        result = azure_operation_poller.result()
        
        result = self.mgmt_client.attestation_providers.get(resource_group.name, ATTESTATION_PROVIDER_NAME)
        
        result = self.mgmt_client.attestation_providers.list()

        result = self.mgmt_client.attestation_providers.list_by_resource_group(resource_group.name)

        result = self.mgmt_client.attestation_providers.delete(resource_group.name, ATTESTATION_PROVIDER_NAME)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()