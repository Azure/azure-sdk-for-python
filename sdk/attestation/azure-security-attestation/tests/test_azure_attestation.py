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
from azure.security.attestation.v2020_10_01.models import AttestationType
import azure.security.attestation.v2020_10_01.models

AttestationPreparer = functools.partial(
            PowerShellPreparer, "attestation",
            ATTESTATION_AZURE_AUTHORITY_HOST='xxx',
            ATTESTATION_RESOURCE_GROUP='yyyy',
            ATTESTATION_SUBSCRIPTION_ID='xxx',
            ATTESTATION_LOCATION_SHORT_NAME='xxx',
            ATTESTATION_ENVIRONMENT='AzureCloud',
            ATTESTATION_POLICY_SIGNING_KEY0='keyvalue',
            ATTESTATION_POLICY_SIGNING_KEY1='keyvalue',
            ATTESTATION_POLICY_SIGNING_KEY2='keyvalue',
            ATTESTATION_POLICY_SIGNING_CERTIFICATE0='more junk',
            ATTESTATION_POLICY_SIGNING_CERTIFICATE1='more junk',
            ATTESTATION_POLICY_SIGNING_CERTIFICATE2='more junk',
            ATTESTATION_SERIALIZED_POLICY_SIGNING_KEY0="junk",
            ATTESTATION_SERIALIZED_POLICY_SIGNING_KEY1="junk",
            ATTESTATION_SERIALIZED_POLICY_SIGNING_KEY2="junk",
            ATTESTATION_SERIALIZED_ISOLATED_SIGNING_KEY='yyyy',
            ATTESTATION_ISOLATED_SIGNING_KEY='xxxx',
            ATTESTATION_ISOLATED_SIGNING_CERTIFICATE='xxxx',
            ATTESTATION_SERVICE_MANAGEMENT_URL='xxx',
            ATTESTATION_LOCATION='xxxx',
            ATTESTATION_CLIENT_ID='xxxx',
            ATTESTATION_CLIENT_SECRET='secret',
            ATTESTATION_TENANT_ID='tenant',
            ATTESTATION_ISOLATED_URL='xxx',
            ATTESTATION_AAD_URL='yyy',
            ATTESTATION_RESOURCE_MANAGER_URL='resourcemanager'
        )

class AzureAttestationTest(AzureTestCase):

    def setUp(self):
            super(AzureAttestationTest, self).setUp()

    def test_shared_getopenidmetadata(self):
        attest_client = self.shared_client()
        open_id_metadata = attest_client.metadata_configuration.get()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == self.shared_base_uri()+"/certs"
        assert open_id_metadata["issuer"] == self.shared_base_uri()

    def test_aad_getopenidmetadata(self):
        attest_client = self.aad_client()
        open_id_metadata = attest_client.metadata_configuration.get()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == self.aad_base_uri()+"/certs"
        assert open_id_metadata["issuer"] == self.aad_base_uri()

    def test_isolated_getopenidmetadata(self):
        attest_client = self.isolated_client()
        open_id_metadata = attest_client.metadata_configuration.get()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == self.IsolatedBaseUri()+"/certs"
        assert open_id_metadata["issuer"] == self.IsolatedBaseUri()

    def test_shared_getsigningcertificates(self):
        attest_client = self.shared_client()
        signing_certificates = attest_client.signing_certificates.get()
        print ('{}'.format(signing_certificates))
        assert signing_certificates.keys is not None
        assert len(signing_certificates.keys) != 0
        for key in signing_certificates.keys:
            assert key.x5_c is not None
            x5cs = key.x5_c
            assert len(x5cs) >= 1
            print('Found key with x5c, length = ', len(x5cs))
            for x5c in x5cs:
                der_cert = base64.b64decode(x5c)
                cert = cryptography.x509.load_der_x509_certificate(der_cert)
                print(f'Cert  iss: {cert.issuer}; subject: {cert.subject}')

    def test_aad_getsigningcertificates(self):
        attest_client = self.aad_client()
        signing_certificates = attest_client.signing_certificates.get()
        print ('{}'.format(signing_certificates))
        assert signing_certificates.keys is not None
        assert len(signing_certificates.keys) != 0
        for key in signing_certificates.keys:
            assert key.x5_c is not None
            x5cs = key.x5_c
            assert len(x5cs) >= 1
            print('Found key with x5c, length = ', len(x5cs))
            for x5c in x5cs:
                der_cert = base64.b64decode(x5c)
                cert = cryptography.x509.load_der_x509_certificate(der_cert)
                print(f'Cert  iss: {cert.issuer}; subject: {cert.subject}')

    def test_isolated_getsigningcertificates(self):
        attest_client = self.isolated_client()
        signing_certificates = attest_client.signing_certificates.get()
        print ('{}'.format(signing_certificates))
        assert signing_certificates.keys is not None
        assert len(signing_certificates.keys) != 0
        for key in signing_certificates.keys:
            assert key.x5_c is not None
            x5cs = key.x5_c
            assert len(x5cs) >= 1
            print('Found key with x5c, length = ', len(x5cs))
            for x5c in x5cs:
                der_cert = base64.b64decode(x5c)
                cert = cryptography.x509.load_der_x509_certificate(der_cert)
                print(f'Cert  iss: {cert.issuer}; subject: {cert.subject}')


    def test_shared_get_policy_sgx(self):
        attest_client = self.shared_client()
        default_policy_response = attest_client.policy.get("SgxEnclave")
        default_policy = default_policy_response.token
        policy_token = jwt.decode(default_policy, options={"verify_signature":False}, algorithms=["none", "RS256"])
        
        verifyToken=True
        unverified_header = jwt.get_unverified_header(policy_token["x-ms-policy"])
        if (unverified_header.get('alg')=='none'):
          verifyToken = False
        policyjwt = jwt.decode(
            policy_token["x-ms-policy"],
            algorithms=["none", "RS256"],
            options={"verify_signature": verifyToken})
        base64urlpolicy = policyjwt.get("AttestationPolicy")
        policy = Base64Url.decode(encoded=base64urlpolicy)
        print("Default Policy: ", policy)

    def test_isolated_get_policy_sgx(self):
        attest_client = self.isolated_client()
        default_policy_response = attest_client.policy.get("SgxEnclave")
        default_policy = default_policy_response.token
        policy_token = jwt.decode(default_policy, options={"verify_signature":False}, algorithms=["none", "RS256"])
        
        verifyToken=True
        unverified_header = jwt.get_unverified_header(policy_token["x-ms-policy"])
        if (unverified_header.get('alg')=='none'):
          verifyToken = False
        policyjwt = jwt.decode(
            policy_token["x-ms-policy"],
            algorithms=["none", "RS256"],
            options={"verify_signature": verifyToken})
        base64urlpolicy = policyjwt.get("AttestationPolicy")
        policy = Base64Url.decode(encoded=base64urlpolicy)
        print("Default Policy: ", policy)

    def test_aad_get_policy_sgx(self):
        attest_client = self.aad_client()
        default_policy_response = attest_client.policy.get("SgxEnclave")
        default_policy = default_policy_response.token
        policy_token = jwt.decode(default_policy, options={"verify_signature":False}, algorithms=["none", "RS256"])
        
        verifyToken=True
        unverified_header = jwt.get_unverified_header(policy_token["x-ms-policy"])
        if (unverified_header.get('alg')=='none'):
          verifyToken = False
        policyjwt = jwt.decode(
            policy_token["x-ms-policy"],
            algorithms=["none", "RS256"],
            options={"verify_signature": verifyToken})
        base64urlpolicy = policyjwt.get("AttestationPolicy")
        policy = Base64Url.decode(encoded=base64urlpolicy)
        print("Default Policy: ", policy)

    def test_aad_get_policy_management_signers(self):
        attest_client = self.aad_client()
        policy_signers = attest_client.policy_certificates.get()
        default_signers = policy_signers.token
        policy_token = jwt.decode(default_signers, options={"verify_signature":False}, algorithms=["none", "RS256"])
        print("{}".format(policy_token))
        policy_certificates = policy_token["x-ms-policy-certificates"]
        assert len(policy_certificates["keys"])==0

    def test_shared_get_policy_management_signers(self):
        attest_client = self.shared_client()
        policy_signers = attest_client.policy_certificates.get()
        default_signers = policy_signers.token
        policy_token = jwt.decode(default_signers, options={"verify_signature":False}, algorithms=["none", "RS256"])
        print("{}".format(policy_token))
        policy_certificates = policy_token["x-ms-policy-certificates"]
        assert len(policy_certificates["keys"])==0

    def test_isolated_get_policy_management_signers(self):
        attest_client = self.isolated_client()
        policy_signers = attest_client.policy_certificates.get()
        default_signers = policy_signers.token
        policy_token = jwt.decode(default_signers, options={"verify_signature":False}, algorithms=["none", "RS256"])
        print("{}".format(policy_token))
        policy_certificates = policy_token["x-ms-policy-certificates"]
        assert len(policy_certificates["keys"])==1
        policy_key = policy_certificates["keys"][0]
        x5cs = policy_key["x5c"]
        assert len(x5cs) != 0
        for cert in x5cs:
            der_cert = base64.b64decode(cert)
            cert = cryptography.x509.load_der_x509_certificate(der_cert)
            print(f'Policy Management Certificate iss: {cert.issuer}; subject: {cert.subject}')
            



    def shared_client(self):
            """
            docstring
            """
            credential = self.get_credential(AttestationClient)
            attest_client = self.create_client_from_credential(AttestationClient,
                credential=credential,
                instance_url=self.shared_base_uri())
            return attest_client

#    @AttestationPreparer()
    def aad_client(self):
            """
            docstring
            """
            credential = self.get_credential(AttestationClient)
            baseUri = self.original_env["ATTESTATION_AAD_URL"]
#            baseUri = ATTESTATION_AAD_ATTESTATION_URL
            attest_client = self.create_client_from_credential(AttestationClient,
                credential=credential,
                instance_url=baseUri)
            return attest_client

    def isolated_client(self):
            """
            docstring
            """
            credential = self.get_credential(AttestationClient)
            baseUri = self.original_env["ATTESTATION_ISOLATED_URL"]
            attest_client = self.create_client_from_credential(AttestationClient,
                credential=credential,
                instance_url=baseUri)
            return attest_client


    @staticmethod
    def shared_base_uri():
        return "https://shareduks.uks.test.attest.azure.net"

    def IsolatedBaseUri(self):
        return self.original_env["ATTESTATION_ISOLATED_URL"]

    def aad_base_uri(self):
        return self.original_env["ATTESTATION_AAD_URL"]
    
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
