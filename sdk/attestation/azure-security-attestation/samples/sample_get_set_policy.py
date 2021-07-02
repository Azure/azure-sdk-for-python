# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_set_policy.py
DESCRIPTION:
    These samples demonstrate using the attestation administration APIs to manage
    attestation policy documents for the various modes of operation of the attestation
    service.

    Set the following environment variables with your own values before running
    the sample:
    1) ATTESTATION_AAD_URL - the base URL for an attestation service instance in AAD mode.
    2) ATTESTATION_ISOLATED_URL - the base URL for an attestation service instance in Isolated mode.
    3) ATTESTATION_TENANT_ID - Tenant Instance for authentication.
    4) ATTESTATION_CLIENT_ID - Client identity for authentication.
    5) ATTESTATION_CLIENT_SECRET - Secret used to identify the client.
    6) ATTESTATION_ISOLATED_SIGNING_CERTIFICATE - Base64 encoded X.509 Certificate
        specified when the isolated mode instance is created. 
    7) ATTESTATION_ISOLATED_SIGNING_KEY - Base64 encoded DER encoded RSA Private key
        associated with the ATTESTATION_ISOLATED_SIGNING_CERTIFICATE

Usage:
    python sample_get_set_policy.py

This sample demonstrates retrieving, setting policies, and resetting policies
on both AAD and Isolated mode attestation service instances.

It also demonstrates adding and removing attestation policy management certificates,
which are used to set attestation policy on isolated mode attestation service instances.

"""

import base64
import os
from azure.identity import DefaultAzureCredential
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from dotenv import find_dotenv, load_dotenv
import base64


from azure.security.attestation import (
    AttestationAdministrationClient,
    AttestationType,
    AttestationClient,
    CertificateModification,
    AttestationPolicyToken,
)

from sample_collateral import sample_open_enclave_report, sample_runtime_data
from sample_utils import (
    create_rsa_key,
    create_x509_certificate,
    write_banner,
    pem_from_base64,
)


class AttestationClientPolicySamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        if os.environ.get("ATTESTATION_ISOLATED_URL"):
            self.isolated_certificate = pem_from_base64(
                os.getenv("ATTESTATION_ISOLATED_SIGNING_CERTIFICATE"), "CERTIFICATE"
            )
            self.isolated_key = pem_from_base64(
                os.getenv("ATTESTATION_ISOLATED_SIGNING_KEY"), "PRIVATE KEY"
            )

    def close(self):
        pass

    def get_policy_aad(self):
        """
        Demonstrates retrieving the policy document for an SGX enclave.
        """
        write_banner("get_policy_aad")
        print("Retrieve an unsecured Policy on an AAD mode attestation instance.")

        # [BEGIN get_policy]
        with AttestationAdministrationClient(
            os.environ.get("ATTESTATION_AAD_URL"), DefaultAzureCredential()
        ) as admin_client:
            policy, _ = admin_client.get_policy(AttestationType.SGX_ENCLAVE)
            print("Current instance SGX Policy is: ", policy)
        # [END get_policy]

    def set_policy_aad_unsecured(self):
        """
        Demonstrates setting an attestation policy for OpenEnclave attestation
        operations.
        """

        write_banner("set_policy_aad_unsecured")
        print("Set an unsecured Policy on an AAD mode attestation instance.")
        # [BEGIN set_policy_unsecured]
        with AttestationAdministrationClient(
            os.environ.get("ATTESTATION_AAD_URL"), DefaultAzureCredential()
        ) as admin_client:
            new_policy = """
version= 1.0;
authorizationrules
{
    [ type=="x-ms-sgx-is-debuggable", value==false ] &&
    [ type=="x-ms-sgx-product-id", value==1 ] &&
    [ type=="x-ms-sgx-svn", value>= 0 ] &&
    [ type=="x-ms-sgx-mrsigner", value=="2c1a44952ae8207135c6c29b75b8c029372ee94b677e15c20bd42340f10d41aa"]
        => permit();
};
issuancerules {
    c:[type=="x-ms-sgx-mrsigner"] => issue(type="My-MrSigner", value=c.value);
};
    """

            set_result, _ = admin_client.set_policy(
                AttestationType.OPEN_ENCLAVE, new_policy
            )
            print("Policy Set result: ", set_result.policy_resolution)
            # [END set_policy_unsecured]

            get_result, _ = admin_client.get_policy(AttestationType.OPEN_ENCLAVE)
            if new_policy != get_result:
                print("Policy does not match set policy.")

            # Attest an OpenEnclave using the new policy.
            self._attest_open_enclave(os.environ.get("ATTESTATION_AAD_URL"))

    def reset_policy_aad_unsecured(self):
        """
        Demonstrates reset the attestation policy on an AAD mode instance to the
        default value.
        """
        # [BEGIN reset_aad_policy]
        print("Reset an unsecured Policy on an AAD mode attestation instance.")
        with AttestationAdministrationClient(
            os.environ.get("ATTESTATION_AAD_URL"), DefaultAzureCredential()
        ) as admin_client:
            set_result, _ = admin_client.reset_policy(AttestationType.OPEN_ENCLAVE)
            print("Policy reset result: ", set_result.policy_resolution)
        # [END reset_aad_policy]

    def reset_policy_aad_secured(self):
        """Set a secured attestation policy on an AAD mode instance, specifying
        a default signing key and certificate to be used for all policy operations.
        """
        write_banner("reset_policy_aad_secured")
        # [BEGIN reset_aad_policy_secured]
        print("Set Secured Policy on an AAD mode attestation instance.")
        rsa_key = create_rsa_key()
        cert = create_x509_certificate(rsa_key, u"TestCertificate")

        # Create an administrative client, specifying a default key and certificate.
        # The key and certificate will be used for subsequent policy operations.
        with AttestationAdministrationClient(
            os.environ.get("ATTESTATION_AAD_URL"),
            DefaultAzureCredential(),
            signing_key=rsa_key,
            signing_certificate=cert,
        ) as admin_client:

            set_result, _ = admin_client.reset_policy(AttestationType.SGX_ENCLAVE)
            print("Policy Set Resolution: ", set_result.policy_resolution)
        # [END reset_aad_policy_secured]

    def set_policy_aad_secured(self):
        """
        Sets a minimal attestation policy for SGX enclaves with a customer
        specified signing key and certificate.
        """

        write_banner("set_policy_aad_secured")
        print("Set Secured Policy on an AAD mode attestation instance.")
        # [START set_secured_policy]
        with AttestationAdministrationClient(
            os.environ.get("ATTESTATION_AAD_URL"), DefaultAzureCredential()
        ) as admin_client:
            # Create an RSA Key and wrap an X.509 certificate around
            # the public key for that certificate.
            rsa_key = create_rsa_key()
            cert = create_x509_certificate(rsa_key, u"TestCertificate")

            # Set a minimal policy.
            set_result, _ = admin_client.set_policy(
                AttestationType.SGX_ENCLAVE,
                """version= 1.0;authorizationrules{=> permit();};issuancerules {};""",
                signing_key=rsa_key,
                signing_certificate=cert,
            )
            print("Policy Set Resolution: ", set_result.policy_resolution)
            print("Resulting policy signer should match the input certificate:")
            print("Policy Signer: ", set_result.policy_signer.certificates[0])
            print("Certificate:   ", cert)
            # [END set_secured_policy]

            # Reset the policy now that we're done.
            admin_client.reset_policy(AttestationType.SGX_ENCLAVE)

    def set_policy_validate_hash(self):
        """
        Sets a signed attestation policy and validates the signing certificate and
        policy hash after the `set_policy` API returns.
        """

        # [START validate_policy_hash]
        from cryptography.hazmat.primitives import hashes

        write_banner("set_policy_aad_secured")
        print("Set Secured Policy on an AAD mode attestation instance.")
        with AttestationAdministrationClient(
            os.environ.get("ATTESTATION_AAD_URL"), DefaultAzureCredential()
        ) as admin_client:
            # Create an RSA Key and wrap an X.509 certificate around
            # the public key for that certificate.
            rsa_key = create_rsa_key()
            cert = create_x509_certificate(rsa_key, u"TestCertificate")

            # Set a minimal policy.
            policy_to_set = """
version= 1.0;
authorizationrules{=> permit();};
issuancerules {};
"""
            set_result, _ = admin_client.set_policy(
                AttestationType.SGX_ENCLAVE,
                policy_to_set,
                signing_key=rsa_key,
                signing_certificate=cert,
            )
            print("Policy Set Resolution: ", set_result.policy_resolution)
            print("Resulting policy signer should match the input certificate:")
            print("Policy Signer: ", set_result.policy_signer.certificates[0])
            print("Certificate:   ", cert)

            # Create an Attestation Token object representing the
            # attestation policy.
            expected_policy = AttestationPolicyToken(
                policy_to_set, signing_key=rsa_key, signing_certificate=cert
            )

            # Generate the Sha256 hash of the attestation token.
            hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
            hasher.update(expected_policy.to_jwt_string().encode("utf-8"))
            expected_hash = hasher.finalize()

            print("Expected hash should match returned hash.")
            print("Expected hash: ", expected_hash)
            print("Returned hash: ", set_result.policy_token_hash)

            # [END validate_policy_hash]

            # Reset the policy now that we're done.
            admin_client.reset_policy(AttestationType.SGX_ENCLAVE)

    def reset_policy_isolated(self):
        """Set a secured attestation policy on an AAD mode instance"""
        write_banner("reset_policy_isolated")
        isolated_certificate = pem_from_base64(
            os.getenv("ATTESTATION_ISOLATED_SIGNING_CERTIFICATE"), "CERTIFICATE"
        )
        isolated_key = pem_from_base64(
            os.getenv("ATTESTATION_ISOLATED_SIGNING_KEY"), "PRIVATE KEY"
        )

        # [BEGIN reset_isolated_policy]
        print("Set Secured Policy on an Isolated mode attestation instance.")
        # < Load the PEM encoded isolated signing certificate and  key >
        with AttestationAdministrationClient(
            os.environ.get("ATTESTATION_ISOLATED_URL"), DefaultAzureCredential()
        ) as admin_client:
            set_result, _ = admin_client.reset_policy(
                AttestationType.SGX_ENCLAVE,
                signing_key=isolated_key,
                signing_certificate=isolated_certificate,
            )
            print("Policy Set Resolution: ", set_result.policy_resolution)
        # [END reset_isolated_policy]

    def get_policy_isolated(self):
        """
        Retrieve the SGX policy for an the isolated attestation instance.
        """
        write_banner("get_policy_isolated")
        print(
            "Retrieve the SGX Policy on an Isolated mode attestation instance, explicitly setting the issuer for validation.."
        )
        endpoint = os.environ.get("ATTESTATION_ISOLATED_URL")
        with AttestationAdministrationClient(
            endpoint, DefaultAzureCredential()
        ) as admin_client:
            get_result, _ = admin_client.get_policy(
                AttestationType.SGX_ENCLAVE, validate_issuer=True, issuer=endpoint
            )
            print("SGX Policy is: ", get_result)

    def set_policy_isolated_secured(self):
        """
        Set a secured attestation policy on an Isolated mode instance.

        This sample sets the signing key on the admin client object directly, rather
        than providing the signing key to individual APIs.

        For an isolated attestation instance, the new attestation policy must
        be signed with one of the existing policy management certificates.

        """
        write_banner("set_policy_isolated_secured")
        print("Set Secured Policy on an AAD mode attestation instance.")
        endpoint = os.environ.get("ATTESTATION_ISOLATED_URL")
        with AttestationAdministrationClient(
            endpoint,
            DefaultAzureCredential(),
            signing_key=self.isolated_key,
            signing_certificate=self.isolated_certificate,
        ) as admin_client:
            set_result, _ = admin_client.set_policy(
                AttestationType.SGX_ENCLAVE,
                """version= 1.0;authorizationrules{=> permit();};issuancerules {};""",
                validation_slack=1.0,
            )
            print("Policy Set Resolution: ", set_result.policy_resolution)
            print("Resulting policy signer should match the input certificate:")
            print("Policy Signer: ", set_result.policy_signer.certificates[0])
            print("Certificate:   ", self.isolated_certificate)

            print(
                "Reset the attestation policy to the default now to avoid side effects."
            )
            # Reset the policy now that we're done.
            admin_client.reset_policy(AttestationType.SGX_ENCLAVE)

    def get_policy_management_certificates(self):
        """
        Retrieve the policy management certificates for an Isolated mode attestation
        instance.

        This sample shows the use of the get_certificates API to retrieve the
        current set of attestation signing certificates.
        """
        write_banner("get_policy_management_certificates_isolated")

        # [BEGIN get_policy_management_certificate]
        print("Get the policy management certificates for a isolated instance.")

        endpoint = os.environ.get("ATTESTATION_ISOLATED_URL")
        with AttestationAdministrationClient(
            endpoint, DefaultAzureCredential()
        ) as admin_client:
            certificates, _ = admin_client.get_policy_management_certificates(
                validation_slack=1.0
            )
            print("Isolated instance has", len(certificates), "certificates")

            # An Isolated attestation instance should have at least one signing
            # certificate which is configured when the instance is created.
            #
            # Note that the certificate list returned is an array of certificate chains.
            for cert_chain in certificates:
                print("Certificate chain has ", len(cert_chain), " elements.")
                i = 1
                for cert in cert_chain:
                    # load_pem_x509_certifcate takes a bytes, not str, so convert.
                    certificate = load_pem_x509_certificate(cert.encode("ascii"))
                    print("    Certificate", i, "subject:", certificate.subject)
                    i += 1

            # [END get_policy_management_certificate]

    def add_remove_policy_management_certificate(self):
        """
        Add and then remove a  policy management certificates for an Isolated
        mode attestation instance.

        """
        write_banner("add_remove_policy_management_certificate")
        print("Get and set the policy management certificates for a isolated instance.")
        endpoint = os.environ.get("ATTESTATION_ISOLATED_URL")
        with AttestationAdministrationClient(
            endpoint, DefaultAzureCredential()
        ) as admin_client:
            # [BEGIN add_policy_management_certificate]
            new_key = create_rsa_key()
            new_certificate = create_x509_certificate(new_key, u"NewCertificateName")

            # Add the new certificate to the list. Specify a validation slack of
            # 1.0 to test passing in validation parameters to this method.
            add_result, _ = admin_client.add_policy_management_certificate(
                new_certificate,
                signing_key=self.isolated_key,
                signing_certificate=self.isolated_certificate,
                validation_slack=1.0,
            )
            if add_result.certificate_resolution != CertificateModification.IS_PRESENT:
                raise Exception("Certificate was not added!")

            # [END add_policy_management_certificate]

            certificates, _ = admin_client.get_policy_management_certificates()
            print("Isolated instance now has", len(certificates), "certificates")

            for cert_pem in certificates:
                cert = load_pem_x509_certificate(
                    cert_pem[0].encode("ascii"), default_backend()
                )
                print("certificate subject: ", cert.subject)

            # The signing certificate for the isolated instance should be
            # the configured isolated_signing_certificate.
            #
            # Note that the certificate list returned is an array of certificate chains.
            actual_cert0 = certificates[0][0]
            isolated_cert = self.isolated_certificate
            print("Actual Cert 0:   ", actual_cert0)
            print("Isolated Cert: ", isolated_cert)
            if actual_cert0 != isolated_cert:
                raise Exception("Unexpected certificate mismatch.")

            found_cert = False
            expected_cert = new_certificate
            for cert_pem in certificates:
                actual_cert1 = cert_pem[0]
                if actual_cert1 == expected_cert:
                    found_cert = True
            if not found_cert:
                raise Exception("Could not find new certificate!")

        # [BEGIN remove_policy_management_certificate]
        with AttestationAdministrationClient(
            endpoint, DefaultAzureCredential()
        ) as admin_client:
            # Now remove the certificate we just added.
            print("Remove the newly added certificate.")
            remove_result, _ = admin_client.remove_policy_management_certificate(
                new_certificate,
                signing_key=self.isolated_key,
                signing_certificate=self.isolated_certificate,
            )

            if (
                remove_result.certificate_resolution
                != CertificateModification.IS_ABSENT
            ):
                raise Exception("Certificate was not removed!")
        # [END remove_policy_management_certificate]

    def _attest_open_enclave(self, client_uri):
        oe_report = base64.urlsafe_b64decode(sample_open_enclave_report)
        runtime_data = base64.urlsafe_b64decode(sample_runtime_data)
        print("Attest open enclave using ", client_uri)
        with AttestationClient(client_uri, DefaultAzureCredential()) as attest_client:
            attest_client.attest_open_enclave(oe_report, runtime_data=runtime_data)
            print("Successfully attested enclave.")

    def __enter__(self):
        return self

    def __exit__(self, *exc_type):
        self.close()


if __name__ == "__main__":
    with AttestationClientPolicySamples() as sample:
        sample.get_policy_aad()
        sample.set_policy_aad_unsecured()
        sample.reset_policy_aad_unsecured()
        sample.set_policy_aad_secured()
        sample.set_policy_validate_hash()
        sample.reset_policy_aad_secured()
        sample.reset_policy_isolated()
        sample.set_policy_isolated_secured()
        sample.get_policy_management_certificates()
        sample.add_remove_policy_management_certificate()
