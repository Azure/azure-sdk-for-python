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
import base64
import pytest
from helpers import pem_from_base64
from preparers_async import AllAttestationTypes, AllInstanceTypes
from attestation_preparer import AttestationPreparer

from azure.security.attestation.aio import AttestationAdministrationClient
from azure.security.attestation import (
    AttestationType,
    AttestationPolicyToken,
    PolicyModification,
    CertificateModification,
)

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class AsyncPolicyGetSetTests(AzureTestCase):
    @AttestationPreparer()
    @AllAttestationTypes
    @AllInstanceTypes
    async def test_get_policy_async(self, **kwargs):
        attest_client = self.create_admin_client(
            kwargs.pop("instance_url", kwargs.pop("attestation_aad_url"))
        )
        policy, token = await attest_client.get_policy(
            kwargs.pop("attestation_type", AttestationType.SGX_ENCLAVE)
        )
        assert policy.startswith("version") or len(policy) == 0
        print("Token: ", token)
        await attest_client.close()

    @AttestationPreparer()
    @AllAttestationTypes
    async def test_aad_set_policy_unsecured(self, attestation_aad_url, **kwargs):
        attestation_policy = (
            u"version=1.0; authorizationrules{=> permit();}; issuancerules{};"
        )

        attestation_type = kwargs.pop("attestation_type")
        attest_client = self.create_admin_client(attestation_aad_url, **kwargs)
        policy_set_response, _ = await attest_client.set_policy(
            attestation_type, attestation_policy
        )
        new_policy, _ = await attest_client.get_policy(attestation_type)
        assert new_policy == attestation_policy

        expected_policy = AttestationPolicyToken(attestation_policy)

        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(expected_policy.to_jwt_string().encode("utf-8"))
        expected_hash = hasher.finalize()

        assert expected_hash == policy_set_response.policy_token_hash

    @AttestationPreparer()
    @AllAttestationTypes
    async def test_aad_reset_policy_unsecured(self, attestation_aad_url, **kwargs):

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response, _ = await attest_client.reset_policy(
            kwargs.pop("attestation_type")
        )

        assert None == policy_set_response.policy_token_hash
        assert policy_set_response.policy_resolution == PolicyModification.REMOVED

    @pytest.mark.live_test_only
    @AttestationPreparer()
    @AllAttestationTypes
    async def test_aad_reset_policy_secured(
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
        attestation_type = kwargs.pop("attestation_type", AttestationType.SGX_ENCLAVE)

        attest_client = self.create_admin_client(attestation_aad_url)
        policy_set_response, _ = await attest_client.reset_policy(
            attestation_type,
            signing_key=key,
            signing_certificate=signing_certificate,
        )

        assert None == policy_set_response.policy_token_hash
        assert policy_set_response.policy_resolution == PolicyModification.REMOVED

    @pytest.mark.live_test_only
    @AttestationPreparer()
    @AllAttestationTypes
    async def test_aad_set_policy_secured(
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
        attestation_type = kwargs.pop("attestation_type")
        policy_set_response, _ = await attest_client.set_policy(
            attestation_type,
            attestation_policy,
            signing_key=key,
            signing_certificate=signing_certificate,
        )
        policy, _ = await attest_client.get_policy(attestation_type)
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
    async def test_isolated_set_policy_secured(
        self,
        attestation_isolated_url,
        attestation_isolated_signing_key,
        attestation_isolated_signing_certificate,
        **kwargs
    ):
        attestation_policy = (
            u"version=1.0; authorizationrules{=> permit();}; issuancerules{};"
        )

        decoded_cert = pem_from_base64(
            attestation_isolated_signing_certificate, "CERTIFICATE"
        )
        key = pem_from_base64(attestation_isolated_signing_key, "PRIVATE KEY")

        attestation_type = kwargs.pop("attestation_type")
        attest_client = self.create_admin_client(attestation_isolated_url)
        policy_set_response, _ = await attest_client.set_policy(
            attestation_type,
            attestation_policy,
            signing_key=key,
            signing_certificate=decoded_cert,
        )
        policy, _ = await attest_client.get_policy(attestation_type)
        assert policy == attestation_policy

        expected_policy = AttestationPolicyToken(
            attestation_policy,
            signing_key=key,
            signing_certificate=decoded_cert,
        )
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(expected_policy.to_jwt_string().encode("utf-8"))
        expected_hash = hasher.finalize()

        assert expected_hash == policy_set_response.policy_token_hash

    @pytest.mark.live_test_only
    @AttestationPreparer()
    @AllAttestationTypes
    async def test_isolated_reset_policy_secured(
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
        policy_set_response, _ = await attest_client.reset_policy(
            kwargs.pop("attestation_type"),
            signing_key=key,
            signing_certificate=signing_certificate,
        )

        assert None == policy_set_response.policy_token_hash
        assert policy_set_response.policy_resolution == PolicyModification.REMOVED

    async def _test_get_policy_management_certificates(
        self, base_uri, pem_expected_certificate
    ):
        # type: (str, str) -> None
        admin_client = self.create_admin_client(base_uri)
        policy_signers, _ = await admin_client.get_policy_management_certificates()
        if pem_expected_certificate is not None:
            found_cert = False
            for signer in policy_signers:
                # the signer is an X.509 certificate chain, look at the first certificate
                # to see if it's our signing certificate.
                if signer[0] == pem_expected_certificate:
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
    async def test_get_policy_management_certificates(self, **kwargs):
        instance_url = kwargs.pop("instance_url")
        expected_certificate = None
        if self.is_isolated_url(instance_url, **kwargs):
            expected_certificate = pem_from_base64(
                kwargs.get("attestation_isolated_signing_certificate"), "CERTIFICATE"
            )
        await self._test_get_policy_management_certificates(
            instance_url, expected_certificate
        )

    @pytest.mark.live_test_only
    @AttestationPreparer()
    async def test_add_remove_policy_certificate(
        self,
        attestation_isolated_url,
        attestation_isolated_signing_certificate,
        attestation_isolated_signing_key,
        attestation_policy_signing_key0,
        attestation_policy_signing_certificate0,
    ):
        # type: (str, str, str, str, str, str) -> None

        signing_certificate = pem_from_base64(
            attestation_isolated_signing_certificate, "CERTIFICATE"
        )
        key = pem_from_base64(attestation_isolated_signing_key, "PRIVATE KEY")

        pem_certificate_to_add = pem_from_base64(
            attestation_policy_signing_certificate0, "CERTIFICATE"
        )

        admin_client = self.create_admin_client(
            attestation_isolated_url,
            signing_key=key,
            signing_certificate=signing_certificate,
        )

        # Test 0 positional parameters, should throw.
        with pytest.raises(TypeError):
            await admin_client.add_policy_management_certificate()

        # And test more than one positional parameter. Should also throw.
        with pytest.raises(TypeError):
            await admin_client.add_policy_management_certificate(
                pem_certificate_to_add, pem_certificate_to_add
            )

        # Add a new certificate.
        result, _ = await admin_client.add_policy_management_certificate(
            pem_certificate_to_add
        )

        assert result.certificate_resolution == CertificateModification.IS_PRESENT

        # Add it again - this should be ok.
        result, _ = await admin_client.add_policy_management_certificate(
            pem_certificate_to_add
        )
        assert result.certificate_resolution == CertificateModification.IS_PRESENT

        # Ensure that the new certificate is present.
        # We'll leverage the get certificates test to validate this.
        await self._test_get_policy_management_certificates(
            attestation_isolated_url, pem_certificate_to_add
        )

        # Now remove the certificate we just added.
        result, _ = await admin_client.remove_policy_management_certificate(
            pem_certificate_to_add,
            signing_key=key,
            signing_certificate=signing_certificate,
        )
        assert result.certificate_resolution == CertificateModification.IS_ABSENT

        # Remove it again, this should be ok.
        result, _ = await admin_client.remove_policy_management_certificate(
            pem_certificate_to_add,
            signing_key=key,
            signing_certificate=signing_certificate,
        )
        assert result.certificate_resolution == CertificateModification.IS_ABSENT

        # The set of certificates should now just contain the original isolated certificate (PEM encoded :))
        await self._test_get_policy_management_certificates(
            attestation_isolated_url, signing_certificate
        )

    def create_admin_client(
        self, base_uri, **kwargs
    ) -> AttestationAdministrationClient:
        """
        docstring
        """
        credential = self.get_credential(AttestationAdministrationClient, is_async=True)
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

    def shared_admin_client(
        self, location_name: str
    ) -> AttestationAdministrationClient:
        """
        docstring
        """
        return self.create_admin_client(self.shared_base_uri(location_name))

    @staticmethod
    def shared_base_uri(location_name):  # type: (str) -> str
        # When run with recorded tests, the location_name may be 'None', deal with it.
        #        return 'https://shareduks.uks.test.attest.azure.net'
        if location_name is not None:
            return (
                "https://shared"
                + location_name
                + "."
                + location_name
                + ".attest.azure.net"
            )
        return "https://sharedcus.cus.attest.azure.net"


class Base64Url:
    """Equivalent to base64.urlsafe_b64encode, but strips padding from the encoded and decoded strings."""

    @staticmethod
    def encode(unencoded):
        # type: (bytes)->str
        base64val = base64.urlsafe_b64encode(unencoded)
        strip_trailing = base64val.split(b"=")[
            0
        ]  # pick the string before the trailing =
        return strip_trailing.decode("utf-8")

    @staticmethod
    def decode(encoded):
        # type: (str)->bytes
        padding_added = encoded + "=" * ((len(encoded) * -1) % 4)
        return base64.urlsafe_b64decode(padding_added.encode("utf-8"))
