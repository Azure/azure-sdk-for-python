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
import cryptography
import cryptography.x509
import base64
import pytest
from azure.security.attestation import AttestationClient, AttestationAdministrationClient, AttestationType

AttestationPreparer = functools.partial(
            PowerShellPreparer, "attestation",
#            attestation_azure_authority_host='xxx',
#            attestation_resource_group='yyyy',
#            attestation_subscription_id='xxx',
#            attestation_location_short_name='xxx',
#            attestation_environment='AzureCloud',
            attestation_policy_signing_key0='keyvalue',
            attestation_policy_signing_key1='keyvalue',
            attestation_policy_signing_key2='keyvalue',
            attestation_policy_signing_certificate0='more junk',
            attestation_policy_signing_certificate1='more junk',
            attestation_policy_signing_certificate2='more junk',
            attestation_serialized_policy_signing_key0="junk",
            attestation_serialized_policy_signing_key1="junk",
            attestation_serialized_policy_signing_key2="junk",
            attestation_serialized_isolated_signing_key='yyyy',
            attestation_isolated_signing_key='xxxx',
            attestation_isolated_signing_certificate='xxxx',
            attestation_service_management_url='https://management.core.windows.net/',
            attestation_location_short_name='xxxx',
            attestation_client_id='xxxx',
            attestation_client_secret='secret',
            attestation_tenant_id='tenant',
            attestation_isolated_url='https://fakeresource.wus.attest.azure.net',
            attestation_aad_url='https://fakeresource.wus.attest.azure.net',
#            attestation_resource_manager_url='https://resourcemanager/zzz'
        )

class AzureAttestationTest(AzureTestCase):

    def setUp(self):
            super(AzureAttestationTest, self).setUp()

    @AttestationPreparer()
    def test_shared_getopenidmetadata(self, attestation_location_short_name):
        attest_client = self.shared_client(attestation_location_short_name)
        open_id_metadata = attest_client.get_openidmetadata()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == self.shared_base_uri(attestation_location_short_name)+"/certs"
        assert open_id_metadata["issuer"] == self.shared_base_uri(attestation_location_short_name)

    @AttestationPreparer()
    def test_aad_getopenidmetadata(self, attestation_aad_url):
        attest_client = self.create_client(attestation_aad_url)
        open_id_metadata = attest_client.get_openidmetadata()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == attestation_aad_url+"/certs"
        assert open_id_metadata["issuer"] == attestation_aad_url

    @AttestationPreparer()
    def test_isolated_getopenidmetadata(self, attestation_isolated_url):
        attest_client = self.create_client(attestation_isolated_url)
        open_id_metadata = attest_client.get_openidmetadata()
        print ('{}'.format(open_id_metadata))
        assert open_id_metadata["response_types_supported"] is not None
        assert open_id_metadata["jwks_uri"] == attestation_isolated_url+"/certs"
        assert open_id_metadata["issuer"] == attestation_isolated_url

    @AttestationPreparer()
    def test_shared_getsigningcertificates(self, attestation_location_short_name):
        attest_client = self.shared_client(attestation_location_short_name)
        signing_certificates = attest_client.get_signing_certificates()
        for cert in signing_certificates:
            x5c = cert.certificates[0] # type: cryptography.x509.Certificate
            print('Cert  iss:', x5c.issuer, '; subject:', x5c.subject)

    @AttestationPreparer()
    def test_aad_getsigningcertificates(self, attestation_aad_url):
        attest_client = self.create_client(attestation_aad_url)
        signing_certificates = attest_client.get_signing_certificates()
        for cert in signing_certificates:
            x5c = cert.certificates[0] # type: cryptography.x509.Certificate
            print('Cert  iss:', x5c.issuer, '; subject:', x5c.subject)

    @AttestationPreparer()
    def test_isolated_getsigningcertificates(self, attestation_isolated_url):
        attest_client = self.create_client(attestation_isolated_url)
        signing_certificates = attest_client.get_signing_certificates()
        for cert in signing_certificates:
            x5c = cert.certificates[0] # type: cryptography.x509.Certificate
            print('Cert  iss:', x5c.issuer, '; subject:', x5c.subject)

    @AttestationPreparer()
    def test_shared_get_policy_sgx(self, attestation_location_short_name):
        attest_client = self.shared_admin_client(attestation_location_short_name)
        policy_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        print('Shared policy: ', policy_response.value)
        assert(policy_response.value.startswith('version'))
        print('Token: ', policy_response.token)

#     @AttestationPreparer()
#     def test_isolated_get_policy_sgx(self, attestation_isolated_url):
#         attest_client = self.create_client(attestation_isolated_url)
#         default_policy_response = attest_client.policy.get(AttestationType.SGX_ENCLAVE)
#         default_policy = default_policy_response.token
#         policy_token = jwt.decode(
#             default_policy, 
#             options={"verify_signature":False, "verify_exp": False}, 
#             leeway=10, 
#             algorithms=["none", "RS256"])
        
#         verifyToken=True
#         unverified_header = jwt.get_unverified_header(policy_token["x-ms-policy"])
#         if (unverified_header.get('alg')=='none'):
#           verifyToken = False
#         policyjwt = jwt.decode(
#             policy_token["x-ms-policy"],
#             leeway=10,
#             algorithms=["none", "RS256"],
#             options={"verify_signature":False, 'verify_exp': False})
#         base64urlpolicy = policyjwt.get("AttestationPolicy")
#         policy = Base64Url.decode(encoded=base64urlpolicy)
#         print("Default Policy: ", policy)

#     @AttestationPreparer()
#     def test_aad_get_policy_sgx(self, attestation_aad_url):
#         attest_client = self.create_client(attestation_aad_url)
#         default_policy_response = attest_client.policy.get(AttestationType.SGX_ENCLAVE)
#         default_policy = default_policy_response.token
#         policy_token = jwt.decode(
#             default_policy, 
#             options={"verify_signature":False, 'verify_exp': False},
#             leeway=10, 
#             algorithms=["none", "RS256"])

#         verifyToken=True
#         unverified_header = jwt.get_unverified_header(policy_token["x-ms-policy"])
#         if (unverified_header.get('alg')=='none'):
#           verifyToken = False
#         policyjwt = jwt.decode(
#             policy_token["x-ms-policy"],
#             leeway=10,
#             algorithms=["none", "RS256"],
#             options={"verify_signature":False, 'verify_exp': False})
#         base64urlpolicy = policyjwt.get("AttestationPolicy")
#         policy = Base64Url.decode(encoded=base64urlpolicy)
#         print("Default Policy: ", policy)

#     @AttestationPreparer()
#     def test_aad_get_policy_management_signers(self, attestation_aad_url):
#         attest_client = self.create_client(attestation_aad_url)
#         policy_signers = attest_client.policy_certificates.get()
#         default_signers = policy_signers.token
#         policy_token = jwt.decode(
#             default_signers, 
#             options={"verify_signature":False, 'verify_exp': False},
#             leeway=10, 
#             algorithms=["none", "RS256"])
#         print("{}".format(policy_token))
#         policy_certificates = policy_token["x-ms-policy-certificates"]
#         assert len(policy_certificates["keys"])==0

#     def test_shared_get_policy_management_signers(self):
#         attest_client = self.shared_client()
#         policy_signers = attest_client.policy_certificates.get()
#         default_signers = policy_signers.token
#         policy_token = jwt.decode(
#             default_signers, 
#             options={"verify_signature":False, 'verify_exp': False},
#             leeway=10,
#             algorithms=["none", "RS256"])
#         print("{}".format(policy_token))
#         policy_certificates = policy_token["x-ms-policy-certificates"]
#         assert len(policy_certificates["keys"])==0

#     @AttestationPreparer()
#     def test_isolated_get_policy_management_signers(self, attestation_isolated_url):
#         attest_client = self.create_client(attestation_isolated_url)
#         policy_signers = attest_client.policy_certificates.get()
#         default_signers = policy_signers.token
#         policy_token = jwt.decode(
#             default_signers, 
#             options={"verify_signature":False, 'verify_exp': False},
#             leeway=10,
#             algorithms=["none", "RS256"])
#         print("{}".format(policy_token))
#         policy_certificates = policy_token["x-ms-policy-certificates"]
#         assert len(policy_certificates["keys"])==1
#         policy_key = policy_certificates["keys"][0]
#         x5cs = policy_key["x5c"]
#         assert len(x5cs) != 0
#         for cert in x5cs:
#             der_cert = base64.b64decode(cert)
#             cert = cryptography.x509.load_der_x509_certificate(der_cert)
#             print('Policy Management Certificate iss:', cert.issuer, '}; subject: ', cert.subject)
            
    def create_client(self, base_uri) -> AttestationClient:
            """
            docstring
            """
            credential = self.get_credential(AttestationClient)
            attest_client = self.create_client_from_credential(AttestationClient,
                credential=credential,
                instance_url=base_uri)
            return attest_client

    def create_admin_client(self, base_uri) -> AttestationAdministrationClient:
            """
            docstring
            """
            credential = self.get_credential(AttestationAdministrationClient)
            attest_client = self.create_client_from_credential(AttestationAdministrationClient,
                credential=credential,
                instance_url=base_uri)
            return attest_client

    def shared_client(self, location_name: str) -> AttestationClient:
            """
            docstring
            """
            return self.create_client(self.shared_base_uri(location_name))

    def shared_admin_client(self, location_name: str) -> AttestationAdministrationClient:
            """
            docstring
            """
            return self.create_admin_client(self.shared_base_uri(location_name))


    @staticmethod
    def shared_base_uri(location_name: str):
        return 'https://shared'+location_name+'.'+location_name+'.attest.azure.net'
   
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
