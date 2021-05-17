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
    3) AZURE_TENANT_ID - Tenant Instance for authentication.
    4) AZURE_CLIENT_ID - Client identity for authentication.
    5) AZURE_CLIENT_SECRET - Secret used to identify the client.
    6) ATTESTATION_ISOLATED_SIGNING_CERTIFICATE - Base64 encoded X.509 Certificate
        specified when the isolated mode instance is created. 
    7) ATTESTATION_ISOLATED_SIGNING_KEY - Base64 encoded DER encoded RSA Private key
        associated with the ATTESTATATION_ISOLATED_SIGNING_CERTIFICATE


"""

import datetime 
from logging import fatal
from typing import Any, ByteString, Dict
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from  cryptography.x509 import BasicConstraints, CertificateBuilder, NameOID, SubjectAlternativeName
import cryptography
from cryptography.hazmat.primitives import hashes, serialization
import base64
import json
import os
from dotenv import find_dotenv, load_dotenv
import base64

from azure.security.attestation import (
    AttestationAdministrationClient,
    AttestationType,
    AttestationClient,
    AttestationData,
    AttestationSigningKey,
    TokenValidationOptions)

from sample_collateral import sample_open_enclave_report, sample_runtime_data

class AttestationClientPolicySamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.aad_url = os.environ.get("ATTESTATION_AAD_URL")
        self.isolated_url = os.environ.get("ATTESTATION_ISOLATED_URL")
        if self.isolated_url:
            self.isolated_certificate = base64.b64decode(os.getenv("ATTESTATION_ISOLATED_SIGNING_CERTIFICATE"))
            self.isolated_key = base64.b64decode(os.getenv("ATTESTATION_ISOLATED_SIGNING_KEY"))

    def get_policy_aad(self):
        print("\nRetrieve an unsecured Policy on an AAD mode attestation instance.")
        admin_client = self._create_admin_client(self.aad_url)
        get_result = admin_client.get_policy(AttestationType.SGX_ENCLAVE)
        print("SGX Policy is: ", get_result.value)

    def set_policy_aad_unsecured(self):
        print("\nSet an unsecured Policy on an AAD mode attestation instance.")
        admin_client = self._create_admin_client(self.aad_url)
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

        set_result = admin_client.set_policy(AttestationType.OPEN_ENCLAVE, new_policy)
        print("Policy Set result: ", set_result.value.policy_resolution)

        get_result = admin_client.get_policy(AttestationType.OPEN_ENCLAVE)
        if new_policy != get_result.value:
            print("Policy does not match set policy.")
        # Attest an OpenEnclave using the new policy.
        self._attest_open_enclave(self.aad_url)

        
    def reset_policy_aad_unsecured(self):
        """ Reset the attestation policy on an AAD mode instance"""
        print("\nReset an unsecured Policy on an AAD mode attestation instance.")
        admin_client = self._create_admin_client(self.aad_url)

        set_result = admin_client.reset_policy(AttestationType.OPEN_ENCLAVE)
        print("Policy reset result: ", set_result.value.policy_resolution)

    def set_policy_aad_secured(self):
        """ Set a secured attestation policy on an AAD mode instance"""
        print("\nSet Secured Policy on an AAD mode attestation instance.")
        admin_client = self._create_admin_client(self.aad_url)

        rsa_key = self._create_rsa_key()
        cert = self._create_x509_certificate(rsa_key, u'TestCertificate')

        set_result=admin_client.set_policy(AttestationType.SGX_ENCLAVE, 
            """version= 1.0;authorizationrules{=> permit();};issuancerules {};""",
            signing_key=AttestationSigningKey(rsa_key, cert))
        print("Policy Set Resolution: ", set_result.value.policy_resolution)
        print("Resulting policy signer should match the input certificate:")
        print("Policy Signer: ", set_result.value.policy_signer.certificates[0])
        print("Certificate:   ", base64.b64encode(cert).decode('ascii'))

        # Reset the policy now that we're done.
        admin_client.reset_policy(AttestationType.SGX_ENCLAVE)

    def reset_policy_aad_secured(self):
        """ Set a secured attestation policy on an AAD mode instance"""
        print("\nSet Secured Policy on an AAD mode attestation instance.")
        admin_client = self._create_admin_client(self.aad_url)

        rsa_key = self._create_rsa_key()
        cert = self._create_x509_certificate(rsa_key, u'TestCertificate')

        set_result=admin_client.reset_policy(AttestationType.SGX_ENCLAVE, 
            signing_key=AttestationSigningKey(rsa_key, cert))
        print("Policy Set Resolution: ", set_result.value.policy_resolution)

    def get_policy_isolated(self):
        print("\nRetrieve an unsecured Policy on an Isolated mode attestation instance.")
        admin_client = self._create_admin_client(self.isolated_url)
        get_result = admin_client.get_policy(AttestationType.SGX_ENCLAVE)
        print("SGX Policy is: ", get_result.value)

    def set_policy_isolated_secured(self):
        """ Set a secured attestation policy on an Isolated mode instance"""
        print("\nSet Secured Policy on an AAD mode attestation instance.")
        admin_client = self._create_admin_client(self.isolated_url)


        set_result=admin_client.set_policy(AttestationType.SGX_ENCLAVE, 
            """version= 1.0;authorizationrules{=> permit();};issuancerules {};""",
            signing_key=AttestationSigningKey(self.isolated_key, self.isolated_certificate))
        print("Policy Set Resolution: ", set_result.value.policy_resolution)
        print("Resulting policy signer should match the input certificate:")
        print("Policy Signer: ", set_result.value.policy_signer.certificates[0])
        print("Certificate:   ", base64.b64encode(self.isolated_certificate).decode('ascii'))

        print("Reset the attestation policy to the default now to avoid side effects.")
        # Reset the policy now that we're done.
        admin_client.reset_policy(AttestationType.SGX_ENCLAVE, 
            signing_key=AttestationSigningKey(
                self.isolated_key,
                self.isolated_certificate))

    def _attest_open_enclave(self, client_uri):
        oe_report = base64.urlsafe_b64decode(sample_open_enclave_report)
        runtime_data = base64.urlsafe_b64decode(sample_runtime_data)
        print('Attest open enclave using ', client_uri)
        attest_client = self._create_client(client_uri)
        attest_client.attest_open_enclave(
            oe_report, runtime_data=AttestationData(runtime_data, is_json=False))
        print("Successfully attested enclave.")

    def _create_admin_client(self, base_url, **kwargs):
        #type:(str, Dict[str, Any]) -> AttestationAdministrationClient
        tenant_id = os.getenv("AZURE_TENANT_ID")
        client_id = os.getenv("AZURE_CLIENT_ID")
        secret = os.getenv("AZURE_CLIENT_SECRET")

        if tenant_id and client_id and secret:
            # Create azure-identity class
            from azure.identity import ClientSecretCredential

            credentials = ClientSecretCredential(
                tenant_id=tenant_id, client_id=client_id, client_secret=secret
            )

        return AttestationAdministrationClient(credentials, instance_url=base_url, **kwargs)

    def _create_client(self, base_url, **kwargs):
        #type:(str, Dict[str, Any]) -> AttestationClient
        tenant_id = os.getenv("AZURE_TENANT_ID")
        client_id = os.getenv("AZURE_CLIENT_ID")
        secret = os.getenv("AZURE_CLIENT_SECRET")

        if tenant_id and client_id and secret:
            # Create azure-identity class
            from azure.identity import ClientSecretCredential

            credentials = ClientSecretCredential(
                tenant_id=tenant_id, client_id=client_id, client_secret=secret
            )

        return AttestationClient(credentials, instance_url=base_url, **kwargs)

    @staticmethod
    def _create_rsa_key(): #type() -> RSAPrivateKey
        return rsa.generate_private_key(65537, 2048, backend=default_backend()).private_bytes(
            serialization.Encoding.DER,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())

    @staticmethod
    def _create_x509_certificate(key_der, subject_name): #type(Union[EllipticCurvePrivateKey,RSAPrivateKey], str) -> Certificate
        signing_key = serialization.load_der_private_key(key_der, password=None, backend=default_backend())
        builder = CertificateBuilder()
        builder = builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
        ]))
        builder = builder.issuer_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
        ]))

        one_day = datetime.timedelta(1, 0, 0)
        builder = builder.not_valid_before(datetime.datetime.today() - one_day)
        builder = builder.not_valid_after(datetime.datetime.today() + (one_day * 30))
        builder = builder.serial_number(x509.random_serial_number())        
        builder = builder.public_key(signing_key.public_key())
        builder = builder.add_extension(SubjectAlternativeName([x509.DNSName(subject_name)]), critical=False)
        builder = builder.add_extension(BasicConstraints(ca=False, path_length=None), critical=True)
        return builder.sign(private_key=signing_key, algorithm=hashes.SHA256(), backend=default_backend()).public_bytes(serialization.Encoding.DER)


if __name__ == "__main__":
    sample = AttestationClientPolicySamples()
    sample.get_policy_aad()
    sample.set_policy_aad_unsecured()
    sample.reset_policy_aad_unsecured()
    sample.set_policy_aad_secured()
    sample.reset_policy_aad_secured()
    sample.set_policy_isolated_secured()