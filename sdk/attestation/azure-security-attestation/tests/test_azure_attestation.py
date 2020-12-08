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
from devtools_testutils import AzureTestCase, ResourceGroupPreparer, PowerShellPreparer
import functools
import json
import cryptography
import base64
import jwt

from azure.security.attestation.v2020_10_01 import AttestationClient
import azure.security.attestation.v2020_10_01.models

AttestationPreparer = functools.partial(
            PowerShellPreparer, "attestation",
            serializedPolicySigningKey1="junk",
            policySigningCertificate0='more junk',
            ATTESTATION_AZURE_AUTHORITY_HOST='xxx',
            ATTESTATION_RESOURCE_GROUP='yyyy',
            policySigningKey0='keyvalue',
            policySigningCertificate1='xxx',
            ATTESTATION_SUBSCRIPTION_ID='xxx',
            isolatedSigningKey='xxxx',
            serializedIsolatedSigningKey='yyyy',
            serializedPolicySigningKey0='xxxx',
            locationShortName='xxx',
            ATTESTATION_ENVIRONMENT='AzureCloud',
            policySigningKey2='xxxx',
            isolatedSIgningCertificate='xxxx',
            serializedPolicySigningKey2='xxx',
            ATTESTATION_SERVICE_MANAGEMENT_URL='xxx',
            ATTESTATION_LOCATION='xxxx',
            policySigningKey1='xxxx',
            ATTESTATION_CLIENT_ID='xxxx',
            ATTESTATION_CLIENT_SECRET='secret',
            ATTESTATION_TENANT_ID='tenant',
            policySigningCertificate2='cert2',
            ISOLATED_ATTESTATION_URL='xxx',
            AAD_ATTESTATION_URL='yyy',
            ATTESTATION_RESOURCE_MANAGER_URL='resourcemanager'
        )

class AzureAttestationTest(AzureTestCase):

    def setUp(self):
            super(AzureAttestationTest, self).setUp()
            print('starting up')

    def test_shared_getopenidmetadata(self):
        attest_client = self.SharedClient()
        open_id_metadata = attest_client.metadata_configuration.get()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == self.SharedBaseUri()+"/certs"
        assert open_id_metadata["issuer"] == self.SharedBaseUri()

    def test_aad_getopenidmetadata(self):
        attest_client = self.AadClient()
        open_id_metadata = attest_client.metadata_configuration.get()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == self.AadBaseUri()+"/certs"
        assert open_id_metadata["issuer"] == self.AadBaseUri()

    def test_isolated_getopenidmetadata(self):
        attest_client = self.IsolatedClient()
        open_id_metadata = attest_client.metadata_configuration.get()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == self.IsolatedBaseUri()+"/certs"
        assert open_id_metadata["issuer"] == self.IsolatedBaseUri()

    def test_shared_getsigningcertificates(self):
        attest_client = self.SharedClient()
        signing_certificates = attest_client.signing_certificates.get()
        print ('{}'.format(signing_certificates))
        assert signing_certificates["keys"] is not None
        keys = signing_certificates["keys"]
        assert len(keys) != 0
        for key in keys:
            assert key["x5c"] is not None
            x5cs = key["x5c"]
            assert len(x5cs) >= 1
            print('Found key with x5c, length = ', len(x5cs))
            for x5c in x5cs:
                der_cert = base64.b64decode(x5c)
                cert = cryptography.x509.load_der_x509_certificate(der_cert)
                print(f'Cert  iss: {cert.issuer}; subject: {cert.subject}')

    def test_aad_getsigningcertificates(self):
        attest_client = self.AadClient()
        signing_certificates = attest_client.signing_certificates.get()
        print ('{}'.format(signing_certificates))
        assert signing_certificates["keys"] is not None
        keys = signing_certificates["keys"]
        assert len(keys) != 0
        for key in keys:
            assert key["x5c"] is not None
            x5cs = key["x5c"]
            assert len(x5cs) >= 1
            print('Found key with x5c, length = ', len(x5cs))
            for x5c in x5cs:
                der_cert = base64.b64decode(x5c)
                cert = cryptography.x509.load_der_x509_certificate(der_cert)
                print(f'Cert  iss: {cert.issuer}; subject: {cert.subject}')

    def test_isolated_getsigningcertificates(self):
        attest_client = self.IsolatedClient()
        signing_certificates = attest_client.signing_certificates.get()
        print ('{}'.format(signing_certificates))
        assert signing_certificates["keys"] is not None
        keys = signing_certificates["keys"]
        assert len(keys) != 0
        for key in keys:
            assert key["x5c"] is not None
            x5cs = key["x5c"]
            assert len(x5cs) >= 1
            print('Found key with x5c, length =', len(x5cs))
            for x5c in x5cs:
                der_cert = base64.b64decode(x5c)
                cert = cryptography.x509.load_der_x509_certificate(der_cert)
                print(f'Cert  iss: {cert.issuer}; subject: {cert.subject}')


    def test_shared_get_policy_sgx(self):
        attest_client = self.SharedClient()
        default_policy_response = attest_client.policy.get("SgxEnclave")
        default_policy = default_policy_response.additional_properties["Policy"]
        verify=True
        unverified_header = jwt.get_unverified_header(default_policy)
        if (unverified_header.get('alg')=='none'):
          verify = False
        policyjwt = jwt.decode(default_policy, verify=verify, algorithms=["none", "RS256"],)
        base64urlpolicy = policyjwt.get("AttestationPolicy")
        policy = Base64Url.decode(encoded=base64urlpolicy)
        print("Default Policy: ", policy)

    def SharedClient(self):
            """
            docstring
            """
            credential = self.get_credential(AttestationClient)
            attest_client = self.create_client_from_credential(AttestationClient,
                credential=credential,
                tenant_base_url=self.SharedBaseUri())
            return attest_client

#   @AttestationPreparer()
    def AadClient(self, AAD_ATTESTATION_URL):
            """
            docstring
            """
            credential = self.get_credential(AttestationClient)
#            baseUri = self.original_env["ATTESTATION_AAD_ATTESTATION_URL"]
            baseUri = ATTESTATION_AAD_ATTESTATION_URL
            attest_client = self.create_client_from_credential(AttestationClient,
                credential=credential,
                tenant_base_url=baseUri)
            return attest_client

    def IsolatedClient(self):
            """
            docstring
            """
            credential = self.get_credential(AttestationClient)
            baseUri = self.original_env["ATTESTATION_ISOLATED_ATTESTATION_URL"]
            attest_client = self.create_client_from_credential(AttestationClient,
                credential=credential,
                tenant_base_url=baseUri)
            return attest_client


    @staticmethod
    def SharedBaseUri():
        return "https://shareduks.uks.test.attest.azure.net"

    def IsolatedBaseUri(self):
        return self.original_env["ISOLATED_ATTESTATION_URL"]

    def AadBaseUri(self):
        return self.original_env["AAD_ATTESTATION_URL"]
    
class Base64Url:
        @staticmethod
        def encode(unencoded):
            base64val= base64.b64encode(unencoded)
            strip_trailing=base64val.split("=")[0] # pick the string before the trailing =
            converted = strip_trailing.replace("+", "-").replace("/", "_")
            return converted

        @staticmethod
        def decode(encoded):
            converted = encoded.replace("-", "+").replace("_", "/")
            padding_added = converted + "=" * ((len(converted)* -1) % 4)
            return base64.b64decode(padding_added)



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
