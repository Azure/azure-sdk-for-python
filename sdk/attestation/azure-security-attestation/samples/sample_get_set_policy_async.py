# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_set_policy_async.py
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

from logging import fatal
from typing import Any, ByteString, Dict
import base64
import json
import os
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_der_x509_certificate
from dotenv import find_dotenv, load_dotenv
import base64
import asyncio

from azure.security.attestation.aio import (
    AttestationAdministrationClient,
    AttestationClient)
from azure.security.attestation import (
    AttestationType,
    AttestationData,
    AttestationSigningKey,
    CertificateModification)

from sample_collateral import sample_open_enclave_report, sample_runtime_data
from sample_utils import write_banner, create_rsa_key, create_x509_certificate, create_client_credentials_async

class AttestationClientPolicySamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.aad_url = os.environ.get("ATTESTATION_AAD_URL")
        self.isolated_url = os.environ.get("ATTESTATION_ISOLATED_URL")
        if self.isolated_url:
            self.isolated_certificate = base64.b64decode(os.getenv("ATTESTATION_ISOLATED_SIGNING_CERTIFICATE"))
            self.isolated_key = base64.b64decode(os.getenv("ATTESTATION_ISOLATED_SIGNING_KEY"))
        self._credentials = create_client_credentials_async()

    async def close(self):
        await self._credentials.close()

    async def get_policy_aad(self):
        """
        Demonstrates retrieving the policy document for an SGX enclave.
        """
        write_banner("get_policy_aad")
        print("Retrieve an unsecured Policy on an AAD mode attestation instance.")
        async with self._create_admin_client(self.aad_url) as admin_client:
            get_result = await admin_client.get_policy(AttestationType.SGX_ENCLAVE)
            print("SGX Policy is: ", get_result.value)


    async def set_policy_aad_unsecured(self):
        """
        Demonstrates setting an attestation policy for OpenEnclave attestation
        operations. 
        """

        write_banner("set_policy_aad_unsecured")
        print("Set an unsecured Policy on an AAD mode attestation instance.")
        async with self._create_admin_client(self.aad_url) as admin_client:
            new_policy="""
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

            set_result = await admin_client.set_policy(AttestationType.OPEN_ENCLAVE, new_policy)
            print("Policy Set result: ", set_result.value.policy_resolution)

            get_result = await admin_client.get_policy(AttestationType.OPEN_ENCLAVE)
            if new_policy != get_result.value:
                print("Policy does not match set policy.")
            # Attest an OpenEnclave using the new policy.
            await self._attest_open_enclave(self.aad_url)
        
    async def reset_policy_aad_unsecured(self):
        """
        Demonstrates reset the attestation policy on an AAD mode instance to the
        default value.
        """
        print("Reset an unsecured Policy on an AAD mode attestation instance.")
        async with self._create_admin_client(self.aad_url) as admin_client:

            set_result = await admin_client.reset_policy(AttestationType.OPEN_ENCLAVE)
            print("Policy reset result: ", set_result.value.policy_resolution)

    async def set_policy_aad_secured(self):
        """
        Sets a minimal attestation policy for SGX enclaves with a customer
        specified signing key and certificate.
        """

        write_banner("set_policy_aad_secured")
        print("Set Secured Policy on an AAD mode attestation instance.")
        async with self._create_admin_client(self.aad_url) as admin_client:

            # [START set_secured_policy]
            # Create an RSA Key and wrap an X.509 certificate around
            # the public key for that certificate.
            rsa_key = create_rsa_key()
            cert = create_x509_certificate(rsa_key, u'TestCertificate')

            # Set a minimal policy.
            set_result=await admin_client.set_policy(AttestationType.SGX_ENCLAVE, 
                """version= 1.0;authorizationrules{=> permit();};issuancerules {};""",
                signing_key=AttestationSigningKey(rsa_key, cert))
            print("Policy Set Resolution: ", set_result.value.policy_resolution)
            print("Resulting policy signer should match the input certificate:")
            print("Policy Signer: ", base64.b64encode(set_result.value.policy_signer.certificates[0]).decode('ascii'))
            print("Certificate:   ", base64.b64encode(cert).decode('ascii'))
            # [END set_secured_policy]

            # Reset the policy now that we're done.
            await admin_client.reset_policy(AttestationType.SGX_ENCLAVE)

    async def reset_policy_aad_secured(self):
        """ Set a secured attestation policy on an AAD mode instance"""
        write_banner("reset_policy_aad_secured")
        print("Set Secured Policy on an AAD mode attestation instance.")
        async with self._create_admin_client(self.aad_url) as admin_client:

            rsa_key = create_rsa_key()
            cert = create_x509_certificate(rsa_key, u'TestCertificate')

            set_result=await admin_client.reset_policy(AttestationType.SGX_ENCLAVE, 
                signing_key=AttestationSigningKey(rsa_key, cert))
            print("Policy Set Resolution: ", set_result.value.policy_resolution)

    async def get_policy_isolated(self):
        """
        Retrieve the SGX policy for an the isolated attestation instance.
        """
        write_banner("get_policy_isolated")
        print("Retrieve an unsecured Policy on an Isolated mode attestation instance.")
        async with self._create_admin_client(self.isolated_url) as admin_client:
            get_result = await admin_client.get_policy(AttestationType.SGX_ENCLAVE)
            print("SGX Policy is: ", get_result.value)

    async def set_policy_isolated_secured(self):
        """
        Set a secured attestation policy on an Isolated mode instance.

        For an isolated attestation instance, the new attestation policy must
        be signed with one of the existing policy management certificates.

        """
        write_banner("set_policy_isolated_secured")
        print("Set Secured Policy on an AAD mode attestation instance.")
        async with self._create_admin_client(self.isolated_url) as admin_client:

            set_result=await admin_client.set_policy(AttestationType.SGX_ENCLAVE, 
                """version= 1.0;authorizationrules{=> permit();};issuancerules {};""",
                signing_key=AttestationSigningKey(self.isolated_key, self.isolated_certificate))
            print("Policy Set Resolution: ", set_result.value.policy_resolution)
            print("Resulting policy signer should match the input certificate:")
            print("Policy Signer: ", base64.b64encode(set_result.value.policy_signer.certificates[0]).decode('ascii'))
            print("Certificate:   ", base64.b64encode(self.isolated_certificate).decode('ascii'))

            print("Reset the attestation policy to the default now to avoid side effects.")
            # Reset the policy now that we're done.
            await admin_client.reset_policy(AttestationType.SGX_ENCLAVE, 
                signing_key=AttestationSigningKey(
                    self.isolated_key,
                    self.isolated_certificate))


    async def get_policy_management_certificates(self):
        """
        Retrieve the policy management certificates for an Isolated mode attestation
        instance.

        This sample shows the use of the get_certificates API to retrieve the
        current set of attestation signing certificates.
        """
        write_banner("get_policy_management_certificates_isolated")
        print("Get the policy management certificates for a isolated instance.")
        async with self._create_admin_client(self.isolated_url) as admin_client:
            get_result= await admin_client.get_policy_management_certificates()
            print("Isolated instance has", len(get_result.value), "certificates")

            # The signing certificate for the isolated instance should be
            # the configured isolated_signing_certificate.
            #
            # Note that the certificate list returned is an array of certificate chains.
            actual_cert = base64.b64encode(get_result.value[0][0]).decode('ascii')
            isolated_cert = base64.b64encode(self.isolated_certificate).decode('ascii')
            print("Actual Cert:   ", actual_cert)
            print("Isolated Cert: ", isolated_cert)
            assert actual_cert == isolated_cert

    async def add_remove_policy_management_certificate(self):
        """
        Add and then remove a  policy management certificates for an Isolated
        mode attestation instance.

        """
        write_banner("add_remove_policy_management_certificate")
        print("Get and set the policy management certificates for a isolated instance.")
        async with self._create_admin_client(self.isolated_url) as admin_client:
            # [BEGIN add_policy_management_certificate]
            new_key = create_rsa_key()
            new_certificate = create_x509_certificate(new_key, u'NewCertificateName')

            # Add the new certificate to the list.
            add_result = await admin_client.add_policy_management_certificate(
                new_certificate,
                AttestationSigningKey(self.isolated_key, self.isolated_certificate))
            if add_result.value.certificate_resolution != CertificateModification.IS_PRESENT:
                raise Exception("Certificate was not added!")

            # [END add_policy_management_certificate]

            get_result = await admin_client.get_policy_management_certificates()
            print("Isolated instance now has", len(get_result.value), "certificates - should be 2")

            for cert_der in get_result.value:
                cert = load_der_x509_certificate(cert_der[0], default_backend())
                print("certificate subject: ", cert.subject)

            # The signing certificate for the isolated instance should be
            # the configured isolated_signing_certificate.
            #
            # Note that the certificate list returned is an array of certificate chains.
            actual_cert0 = base64.b64encode(get_result.value[0][0]).decode('ascii')
            isolated_cert = base64.b64encode(self.isolated_certificate).decode('ascii')
            print("Actual Cert 0:   ", actual_cert0)
            print("Isolated Cert: ", isolated_cert)
            if actual_cert0 != isolated_cert:
                raise Exception("Unexpected certificate mismatch.")

            found_cert = False
            expected_cert = base64.b64encode(new_certificate).decode('ascii')
            for cert_der in get_result.value:
                actual_cert1 = base64.b64encode(cert_der[0]).decode('ascii')
                if actual_cert1 == expected_cert:
                    found_cert = True
            if not found_cert:
                raise Exception("Could not find new certificate!")

            # Now remove the certificate we just added.
            print("Remove the newly added certificate.")
            # [BEGIN remove_policy_management_certificate]
            remove_result = await admin_client.remove_policy_management_certificate(
                new_certificate,
                AttestationSigningKey(self.isolated_key, self.isolated_certificate))

            if remove_result.value.certificate_resolution != CertificateModification.IS_ABSENT:
                raise Exception("Certificate was not removed!")
            # [END remove_policy_management_certificate]

    async def _attest_open_enclave(self, client_uri):
        oe_report = base64.urlsafe_b64decode(sample_open_enclave_report)
        runtime_data = base64.urlsafe_b64decode(sample_runtime_data)
        print('Attest open enclave using ', client_uri)
        async with self._create_client(client_uri) as attest_client:
            await attest_client.attest_open_enclave(
                oe_report, runtime_data=AttestationData(runtime_data, is_json=False))
            print("Successfully attested enclave.")

    def _create_admin_client(self, base_url, **kwargs):
        #type:(str, Dict[str, Any]) -> AttestationAdministrationClient
        return AttestationAdministrationClient(self._credentials, instance_url=base_url, **kwargs)

    def _create_client(self, base_url, **kwargs):
        #type:(str, Dict[str, Any]) -> AttestationClient
        return AttestationClient(self._credentials, instance_url=base_url, **kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_type):
        await self.close()


async def main():
    async with AttestationClientPolicySamples() as sample:
        await sample.get_policy_aad()
        await sample.set_policy_aad_unsecured()
        await sample.reset_policy_aad_unsecured()
        await sample.set_policy_aad_secured()
        await sample.reset_policy_aad_secured()
        await sample.set_policy_isolated_secured()
        await sample.get_policy_management_certificates()
        await sample.add_remove_policy_management_certificate()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

