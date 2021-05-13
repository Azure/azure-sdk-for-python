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

from logging import fatal
from typing import ByteString
import unittest
from cryptography.hazmat.primitives import hashes
from devtools_testutils import AzureTestCase, PowerShellPreparer
import functools
import cryptography.x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import base64
import pytest
from preparers import AttestationPreparer

from azure.security.attestation import (
    AttestationAdministrationClient,
    AttestationType,
    TokenValidationOptions,
    StoredAttestationPolicy,
    AttestationToken,
    AttestationSigningKey,
    PolicyModification,
    CertificateModification)

class PolicyGetSetTests(AzureTestCase):

    @AttestationPreparer()
    def test_shared_get_policy_sgx(self, attestation_location_short_name):
        attest_client = self.shared_admin_client(attestation_location_short_name)
        policy_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        print('Shared policy: ', policy_response.value)
        assert(policy_response.value.startswith('version'))
        print('Token: ', policy_response.token)

    @AttestationPreparer()
    def test_shared_get_policy_openenclave(self, attestation_location_short_name):
        attest_client = self.shared_admin_client(attestation_location_short_name)
        policy_response = attest_client.get_policy(AttestationType.OPEN_ENCLAVE)
        print('Shared policy: ', policy_response.value)
        assert(policy_response.value.startswith('version'))
        print('Token: ', policy_response.token)


    @AttestationPreparer()
    def test_isolated_get_policy_sgx(self, attestation_isolated_url):
        attest_client = self.create_admin_client(attestation_isolated_url)
        policy_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        print('Shared policy: ', policy_response.value)
        assert(policy_response.value.startswith('version'))
        print('Token: ', policy_response.token)

    @AttestationPreparer()
    def test_aad_get_policy_sgx(self, attestation_aad_url):
        attest_client = self.create_admin_client(attestation_aad_url)
        policy_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        print('Shared policy: ', policy_response.value)
        assert(policy_response.value.startswith('version'))
        print('Token: ', policy_response.token)

    @AttestationPreparer()
    def test_aad_set_policy_sgx_unsecured(self, attestation_aad_url):
        attestation_policy = u"version=1.0; authorizationrules{=> permit();}; issuancerules{};"

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response = attest_client.set_policy(AttestationType.SGX_ENCLAVE, attestation_policy)
        policy_get_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        assert policy_get_response.value == attestation_policy

        expected_policy = AttestationToken(body=StoredAttestationPolicy(attestation_policy))
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(expected_policy.serialize().encode('utf-8'))
        expected_hash = hasher.finalize()

        assert expected_hash == policy_set_response.value.policy_token_hash

    @AttestationPreparer()
    def test_aad_reset_policy_sgx_unsecured(self, attestation_aad_url):

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response = attest_client.reset_policy(AttestationType.SGX_ENCLAVE)

        assert None == policy_set_response.value.policy_token_hash
        assert policy_set_response.value.policy_resolution == PolicyModification.REMOVED

    @AttestationPreparer()
    @pytest.mark.live_test_only
    def test_aad_reset_policy_sgx_secured(self, attestation_aad_url, attestation_policy_signing_key0, attestation_policy_signing_certificate0):
        signing_certificate = base64.b64decode(attestation_policy_signing_certificate0)
        key = base64.b64decode(attestation_policy_signing_key0)

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response = attest_client.reset_policy(AttestationType.SGX_ENCLAVE, signing_key=AttestationSigningKey(key, signing_certificate))

        assert None == policy_set_response.value.policy_token_hash
        assert policy_set_response.value.policy_resolution == PolicyModification.REMOVED



    @AttestationPreparer()
    @pytest.mark.live_test_only
    def test_aad_set_policy_sgx_secured(self, attestation_aad_url, attestation_policy_signing_key0, attestation_policy_signing_certificate0):
        attestation_policy = u"version=1.0; authorizationrules{=> permit();}; issuancerules{};"

        signing_certificate = base64.b64decode(attestation_policy_signing_certificate0)
        key = base64.b64decode(attestation_policy_signing_key0)

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response = attest_client.set_policy(AttestationType.SGX_ENCLAVE,
            attestation_policy,
            signing_key=AttestationSigningKey(key, signing_certificate))
        policy_get_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        assert policy_get_response.value == attestation_policy

        expected_policy = AttestationToken(body=StoredAttestationPolicy(attestation_policy), signer=AttestationSigningKey(key, signing_certificate))
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(expected_policy.serialize().encode('utf-8'))
        expected_hash = hasher.finalize()

        assert expected_hash == policy_set_response.value.policy_token_hash


    @AttestationPreparer()
    @pytest.mark.live_test_only
    def test_isolated_set_policy_sgx_secured(self, attestation_isolated_url, attestation_isolated_signing_key, attestation_isolated_signing_certificate):
        attestation_policy = u"version=1.0; authorizationrules{=> permit();}; issuancerules{};"

        decoded_cert = base64.b64decode(attestation_isolated_signing_certificate)
        key = base64.b64decode(attestation_isolated_signing_key)

        attest_client = self.create_admin_client(attestation_isolated_url)
        policy_set_response = attest_client.set_policy(AttestationType.SGX_ENCLAVE,
            attestation_policy,
            signing_key=AttestationSigningKey(key, decoded_cert))
        policy_get_response = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        assert policy_get_response.value == attestation_policy

        expected_policy = AttestationToken(body=StoredAttestationPolicy(attestation_policy), signer=AttestationSigningKey(key, decoded_cert))
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(expected_policy.serialize().encode('utf-8'))
        expected_hash = hasher.finalize()

        assert expected_hash == policy_set_response.value.policy_token_hash

    @AttestationPreparer()
    @pytest.mark.live_test_only
    def test_isolated_reset_policy_sgx_secured(self, attestation_aad_url, attestation_isolated_signing_key, attestation_isolated_signing_certificate):
        signing_certificate = base64.b64decode(attestation_isolated_signing_certificate)
        key = base64.b64decode(attestation_isolated_signing_key)

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response = attest_client.reset_policy(AttestationType.SGX_ENCLAVE, signing_key=AttestationSigningKey(key, signing_certificate))

        assert None == policy_set_response.value.policy_token_hash
        assert policy_set_response.value.policy_resolution == PolicyModification.REMOVED


    def _test_get_policy_management_certificates(self, base_uri, expected_certificate):
        #type:(str, bytes) -> None
        admin_client = self.create_admin_client(base_uri)
        policy_signers = admin_client.get_policy_management_certificates()
        if expected_certificate is not None:
            found_cert=False
            decoded_cert = base64.b64decode(expected_certificate)
            for signer in policy_signers.value:
                # the signer is an X.509 certificate chain, look at the first certificate
                # to see if it's our signing certificate.
                if (signer[0] == decoded_cert):
                    found_cert = True
                    break
            assert found_cert
        else:
            assert len(policy_signers.value)==0

    @AttestationPreparer()
    @pytest.mark.live_test_only
    def test_isolated_get_policy_management_certificates(self, attestation_isolated_url, attestation_isolated_signing_certificate):
        self._test_get_policy_management_certificates(attestation_isolated_url, attestation_isolated_signing_certificate)

    @AttestationPreparer()
    def test_aad_get_policy_management_certificates(self, attestation_aad_url):
        self._test_get_policy_management_certificates(attestation_aad_url, None)

    @AttestationPreparer()
    def test_shared_get_policy_management_certificates(self, attestation_location_short_name):
        self._test_get_policy_management_certificates(self.shared_base_uri(attestation_location_short_name), None)

    @AttestationPreparer()
    @pytest.mark.live_test_only
    def test_add_remove_policy_certificate(
        self, 
        attestation_isolated_url,
        attestation_isolated_signing_certificate,
        attestation_isolated_signing_key,
        attestation_policy_signing_key0,
        attestation_policy_signing_certificate0):
        #type:(str, str, str, str, str, str) -> None

        der_signing_cert = base64.b64decode(attestation_isolated_signing_certificate)
        der_signing_key = base64.b64decode(attestation_isolated_signing_key)
        signing_key = AttestationSigningKey(der_signing_key, der_signing_cert)

        admin_client = self.create_admin_client(attestation_isolated_url)

        # Add a new certificate.
        result = admin_client.add_policy_management_certificate(base64.b64decode(attestation_policy_signing_certificate0), signing_key)
        assert result.value.certificate_resolution == CertificateModification.IS_PRESENT

        # Add it again - this should be ok.
        result = admin_client.add_policy_management_certificate(base64.b64decode(attestation_policy_signing_certificate0), signing_key)
        assert result.value.certificate_resolution == CertificateModification.IS_PRESENT

        # Ensure that the new certificate is present. 
        # We'll leverage the get certificates test to validate this.
        self._test_get_policy_management_certificates(attestation_isolated_url, attestation_policy_signing_certificate0)

        # Now remove the certificate we just added.
        result = admin_client.remove_policy_management_certificate(base64.b64decode(attestation_policy_signing_certificate0), signing_key)
        assert result.value.certificate_resolution == CertificateModification.IS_ABSENT

        # Remove it again, this should be ok.
        result = admin_client.remove_policy_management_certificate(base64.b64decode(attestation_policy_signing_certificate0), signing_key)
        assert result.value.certificate_resolution == CertificateModification.IS_ABSENT

        # The set of certificates should now just contain the original isolated certificate.
        self._test_get_policy_management_certificates(attestation_isolated_url, attestation_isolated_signing_certificate)


    def create_admin_client(self, base_uri): #type() -> AttestationAdministrationClient:
            """
            docstring
            """
            credential = self.get_credential(AttestationAdministrationClient)
            attest_client = self.create_client_from_credential(AttestationAdministrationClient,
                credential=credential,
                instance_url=base_uri,
                token_validation_options = TokenValidationOptions(
                    validate_token=True,
                    validate_signature=True,
                    validate_issuer=self.is_live,
                    issuer=base_uri,
                    validate_expiration=self.is_live))
            return attest_client

    def shared_admin_client(self, location_name): #type(str) -> AttestationAdministrationClient:
            """
            docstring
            """
            return self.create_admin_client(self.shared_base_uri(location_name))

    @staticmethod
    def shared_base_uri(location_name): #type(str) -> str
        # When run with recorded tests, the location_name may be 'None', deal with it.
#        return 'https://shareduks.uks.test.attest.azure.net'
        if location_name is not None:
            return 'https://shared'+location_name+'.'+location_name+'.attest.azure.net'
        return 'https://sharedcus.cus.attest.azure.net'
   
class Base64Url:
    """Equivalent to base64.urlsafe_b64encode, but strips padding from the encoded and decoded strings.
    """
    @staticmethod
    def encode(unencoded):
        # type(bytes)->str
        base64val = base64.urlsafe_b64encode(unencoded)
        strip_trailing=base64val.split(b'=')[0] # pick the string before the trailing =
        return strip_trailing.decode('utf-8')

    @staticmethod
    def decode(encoded):
        # type(str)->bytes
        padding_added = encoded + "=" * ((len(encoded)* -1) % 4)
        return base64.urlsafe_b64decode(padding_added.encode('utf-8'))


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
