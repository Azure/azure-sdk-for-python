# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 7
# Methods Covered : 7
# Examples Total  : 7
# Examples Tested : 7
# Coverage %      : 100
# ----------------------

from cryptography.hazmat.primitives import hashes
from devtools_testutils import AzureTestCase
from cryptography.hazmat.backends import default_backend
import pytest
from preparers import AllAttestationTypes, AllInstanceTypes
from attestation_preparer import AttestationPreparer
from helpers import pem_from_base64

from azure.security.attestation import (
    AttestationAdministrationClient,
    AttestationType,
    AttestationToken,
    PolicyModification,
    CertificateModification,
    AttestationPolicyToken,
)


class PolicyGetSetTests(AzureTestCase):
    @AttestationPreparer()
    @AllAttestationTypes
    @AllInstanceTypes
    def test_get_policy(self, **kwargs):
        attest_client = self.create_admin_client(kwargs.pop("instance_url"))
        policy, token = attest_client.get_policy(kwargs.pop("attestation_type"))
        print("Shared policy: ", policy)
        assert policy.startswith("version") or len(policy) == 0
        print("Token: ", token)

    @AttestationPreparer()
    @AllAttestationTypes
    def test_aad_set_policy_unsecured(self, attestation_aad_url, **kwargs):
        attestation_policy = (
            u"version=1.0; authorizationrules{=> permit();}; issuancerules{};"
        )

        attestation_type = kwargs.pop("attestation_type")
        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response, _ = attest_client.set_policy(
            attestation_type, attestation_policy
        )
        new_policy = attest_client.get_policy(attestation_type)[0]
        assert new_policy == attestation_policy

        expected_policy = AttestationPolicyToken(attestation_policy)

        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(expected_policy.to_jwt_string().encode("utf-8"))
        expected_hash = hasher.finalize()

        assert expected_hash == policy_set_response.policy_token_hash

    @AttestationPreparer()
    @AllAttestationTypes
    def test_aad_reset_policy_unsecured(self, attestation_aad_url, **kwargs):

        attestation_type = kwargs.pop("attestation_type")
        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response, _ = attest_client.reset_policy(attestation_type)

        assert policy_set_response.policy_token_hash is None
        assert policy_set_response.policy_resolution == PolicyModification.REMOVED

    @pytest.mark.live_test_only
    @AttestationPreparer()
    @AllAttestationTypes
    def test_aad_reset_policy_secured(
        self,
        attestation_aad_url,
        attestation_policy_signing_key0,
        attestation_policy_signing_certificate0,
        **kwargs
    ):
        signing_certificate = pem_from_base64(
            attestation_policy_signing_certificate0, "CERTIFICATE"
        )
        key = pem_from_base64(attestation_policy_signing_key0, "PRIVATE KEY")

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response, _ = attest_client.reset_policy(
            kwargs.pop("attestation_type"),
            signing_key=key,
            signing_certificate=signing_certificate,
        )

        assert policy_set_response.policy_token_hash is None
        assert policy_set_response.policy_resolution == PolicyModification.REMOVED

    @pytest.mark.live_test_only
    @AllAttestationTypes
    @AttestationPreparer()
    def test_aad_set_policy_secured(
        self,
        attestation_aad_url,
        attestation_policy_signing_key0,
        attestation_policy_signing_certificate0,
        **kwargs
    ):
        attestation_policy = (
            u"version=1.0; authorizationrules{=> permit();}; issuancerules{};"
        )

        signing_certificate = pem_from_base64(
            attestation_policy_signing_certificate0, "CERTIFICATE"
        )
        key = pem_from_base64(attestation_policy_signing_key0, "PRIVATE KEY")

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response, _ = attest_client.set_policy(
            kwargs.pop("attestation_type"),
            attestation_policy,
            signing_key=key,
            signing_certificate=signing_certificate,
        )
        policy, _ = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        assert policy == attestation_policy

        expected_policy = AttestationPolicyToken(
            attestation_policy,
            signing_key=key,
            signing_certificate=signing_certificate,
        )
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(expected_policy.to_jwt_string().encode("utf-8"))
        expected_hash = hasher.finalize()

        assert expected_hash == policy_set_response.policy_token_hash

    @pytest.mark.live_test_only
    @AttestationPreparer()
    @AllAttestationTypes
    def test_isolated_set_policy_secured(
        self,
        attestation_isolated_url,
        attestation_isolated_signing_key,
        attestation_isolated_signing_certificate,
        **kwargs
    ):
        attestation_policy = (
            u"version=1.0; authorizationrules{=> permit();}; issuancerules{};"
        )

        signing_certificate = pem_from_base64(
            attestation_isolated_signing_certificate, "CERTIFICATE"
        )
        key = pem_from_base64(attestation_isolated_signing_key, "PRIVATE KEY")

        attest_client = self.create_admin_client(attestation_isolated_url)
        policy_set_response, _ = attest_client.set_policy(
            kwargs.pop("attestation_type"),
            attestation_policy,
            signing_key=key,
            signing_certificate=signing_certificate,
        )
        new_policy, _ = attest_client.get_policy(AttestationType.SGX_ENCLAVE)
        assert new_policy == attestation_policy

        expected_policy = AttestationPolicyToken(
            attestation_policy,
            signing_key=key,
            signing_certificate=signing_certificate,
        )
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(expected_policy.to_jwt_string().encode("utf-8"))
        expected_hash = hasher.finalize()

        assert expected_hash == policy_set_response.policy_token_hash

    @pytest.mark.live_test_only
    @AttestationPreparer()
    @AllAttestationTypes
    def test_isolated_reset_policy_secured(
        self,
        attestation_aad_url,
        attestation_isolated_signing_key,
        attestation_isolated_signing_certificate,
        **kwargs
    ):
        signing_certificate = pem_from_base64(
            attestation_isolated_signing_certificate, "CERTIFICATE"
        )
        key = pem_from_base64(attestation_isolated_signing_key, "PRIVATE KEY")

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response, _ = attest_client.reset_policy(
            kwargs.pop("attestation_type"),
            signing_key=key,
            signing_certificate=signing_certificate,
        )

        assert policy_set_response.policy_token_hash is None
        assert policy_set_response.policy_resolution == PolicyModification.REMOVED

    def _test_get_policy_management_certificates(self, base_uri, expected_certificate):
        # type: (str, str) -> None
        admin_client = self.create_admin_client(base_uri)
        policy_signers, _ = admin_client.get_policy_management_certificates()
        if expected_certificate is not None:
            found_cert = False
            for signer in policy_signers:
                # the signer is an X.509 certificate chain, look at the first certificate
                # to see if it's our signing certificate.
                if signer[0] == expected_certificate:
                    found_cert = True
                    break
            assert found_cert
        else:
            assert len(policy_signers) == 0

    @staticmethod
    def is_isolated_url(instance_url, **kwargs):
        # type: (str, Any) -> bool
        return instance_url == kwargs.get("attestation_isolated_url")

    @pytest.mark.live_test_only
    @AttestationPreparer()
    @AllInstanceTypes
    def test_get_policy_management_certificates(self, **kwargs):
        instance_url = kwargs.pop("instance_url")
        expected_certificate = None
        if self.is_isolated_url(instance_url, **kwargs):
            expected_certificate = pem_from_base64(
                kwargs.get("attestation_isolated_signing_certificate"), "CERTIFICATE"
            )
        self._test_get_policy_management_certificates(
            instance_url, expected_certificate
        )

    @pytest.mark.live_test_only
    @AttestationPreparer()
    def test_add_remove_policy_certificate(
        self,
        attestation_isolated_url,
        attestation_isolated_signing_certificate,
        attestation_isolated_signing_key,
        attestation_policy_signing_key0,
        attestation_policy_signing_certificate0,
    ):
        # type: (str, str, str, str, str, str) -> None

        pem_signing_cert = pem_from_base64(
            attestation_isolated_signing_certificate, "CERTIFICATE"
        )
        pem_signing_key = pem_from_base64(
            attestation_isolated_signing_key, "PRIVATE KEY"
        )

        pem_certificate_to_add = pem_from_base64(
            attestation_policy_signing_certificate0, "CERTIFICATE"
        )

        admin_client = self.create_admin_client(
            attestation_isolated_url,
            signing_key=pem_signing_key,
            signing_certificate=pem_signing_cert,
        )

        # Test 0 positional parameters, should throw.
        with pytest.raises(TypeError):
            admin_client.add_policy_management_certificate()

        # And test more than one positional parameter. Should also throw.
        with pytest.raises(TypeError):
            admin_client.add_policy_management_certificate(
                pem_certificate_to_add, pem_certificate_to_add
            )

        # Now let's do something meaningful :). Add a new certificate, using
        # the key and cert specified when the admin client was created.
        result, _ = admin_client.add_policy_management_certificate(
            pem_certificate_to_add
        )
        assert result.certificate_resolution == CertificateModification.IS_PRESENT

        # Add it again - this should be ok.
        result, _ = admin_client.add_policy_management_certificate(
            pem_certificate_to_add,
            signing_key=pem_signing_key,
            signing_certificate=pem_signing_cert,
        )
        assert result.certificate_resolution == CertificateModification.IS_PRESENT

        # Ensure that the new certificate is present.
        # We'll leverage the get certificates test to validate this.
        self._test_get_policy_management_certificates(
            attestation_isolated_url, pem_certificate_to_add
        )

        # Now remove the certificate we just added.
        result, _ = admin_client.remove_policy_management_certificate(
            pem_certificate_to_add
        )
        assert result.certificate_resolution == CertificateModification.IS_ABSENT

        # Remove it again, this should be ok.
        result, _ = admin_client.remove_policy_management_certificate(
            pem_certificate_to_add
        )
        assert result.certificate_resolution == CertificateModification.IS_ABSENT

        # The set of certificates should now just contain the original isolated certificate.
        self._test_get_policy_management_certificates(
            attestation_isolated_url, pem_signing_cert
        )

    def create_admin_client(
        self, base_uri, **kwargs
    ):  # type: (str, Any) -> AttestationAdministrationClient
        """
        docstring
        """
        credential = self.get_credential(AttestationAdministrationClient)
        attest_client = self.create_client_from_credential(
            AttestationAdministrationClient,
            credential=credential,
            endpoint=base_uri,
            validate_token=True,
            validate_signature=True,
            validate_issuer=self.is_live,
            issuer=base_uri,
            validate_expiration=self.is_live,
            **kwargs
        )
        return attest_client
