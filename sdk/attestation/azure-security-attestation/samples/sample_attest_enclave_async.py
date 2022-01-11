# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_attest_enclave.py
DESCRIPTION:
    These samples demonstrate attestating an SGX enclave from a customer supplied
    and the shared attestation service instance.

    Set the environment variables with your own values before running the sample:
    1) ATTESTATION_AAD_URL - the base URL for an attestation service instance in AAD mode.
    2) ATTESTATION_ISOLATED_URL - the base URL for an attestation service instance in Isolated mode.
    3) ATTESTATION_LOCATION_SHORT_NAME - the short name for the region in which the
        sample should be run - used to interact with the shared endpoint for that
        region.
    4) ATTESTATION_TENANT_ID - Tenant Instance for authentication.
    5) ATTESTATION_CLIENT_ID - Client identity for authentication.
    6) ATTESTATION_CLIENT_SECRET - Secret used to identify the client.

Usage:
    python sample_attest_enclave_async.py

This sample performs attestation of sample SGX collateral with both the
`attest_sgx_enclave` and `attest_open_enclave` APIs. It also demonstrates 
retrieving properties from the resulting attestation operation, providing draft
attestation policies (which can be used to test/verify the behavior of 
attestation policies) and shows how to use a validation callback to perform
additional token validations as a part of the `attest_sgx_enclave` API call. 

"""

from azure.identity.aio import DefaultAzureCredential
from cryptography.hazmat.backends import default_backend
import cryptography
from azure.core.exceptions import HttpResponseError
import base64
import os
from dotenv import find_dotenv, load_dotenv
import base64
import asyncio
import json

from azure.security.attestation.aio import AttestationClient
from azure.security.attestation import AttestationToken, AttestationSigner

from sample_collateral import sample_open_enclave_report, sample_runtime_data
from sample_utils import write_banner


class AttestationClientAttestationSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        shared_short_name = os.getenv("ATTESTATION_LOCATION_SHORT_NAME")
        self.shared_url = "https://shared{}.{}.attest.azure.net".format(
            shared_short_name, shared_short_name
        )  # type: str

    async def close(self):
        pass

    async def attest_sgx_enclave_shared(self):
        """
        Demonstrates attesting an SGX Enclave quote, reporting back the issuer of the token.
        """
        write_banner("attest_sgx_enclave_shared")
        oe_report = base64.urlsafe_b64decode(sample_open_enclave_report)
        # Convert the OE report into an SGX quote by stripping off the first 16 bytes.
        quote = oe_report[16:]
        runtime_data = base64.urlsafe_b64decode(sample_runtime_data)

        # [START attest_sgx_enclave_shared]
        print("\nAttest SGX enclave using {}".format(self.shared_url))
        async with DefaultAzureCredential() as credential, AttestationClient(
            self.shared_url, credential
        ) as attest_client:
            response, _ = await attest_client.attest_sgx_enclave(
                quote, runtime_data=runtime_data
            )

        print("Issuer of token is: ", response.issuer)
        # [END attest_sgx_enclave_shared]

    async def attest_open_enclave_shared(self):
        """
        Demonstrates attesting an OpenEnclave report, reporting back the issuer of the token.
        """
        write_banner("attest_open_enclave_shared")
        oe_report = base64.urlsafe_b64decode(sample_open_enclave_report)
        runtime_data = base64.urlsafe_b64decode(sample_runtime_data)

        # [START attest_open_enclave_shared]
        print("Attest Open enclave using ", self.shared_url)
        async with DefaultAzureCredential() as credential, AttestationClient(
            self.shared_url, credential
        ) as attest_client:
            response, _ = await attest_client.attest_open_enclave(
                oe_report, runtime_json=runtime_data
            )

        print("Issuer of token is: ", response.issuer)
        # [END attest_open_enclave_shared]

    async def attest_open_enclave_json_data(self):
        """
        Demonstrates attesting an OpenEnclave report, reporting back the issuer of the token.
        """
        write_banner("attest_open_enclave_shared")
        oe_report = base64.urlsafe_b64decode(sample_open_enclave_report)
        runtime_data = base64.urlsafe_b64decode(sample_runtime_data)

        # [START attest_open_enclave_shared_json]
        print("Attest Open enclave using ", self.shared_url)
        async with DefaultAzureCredential() as credential, AttestationClient(
            self.shared_url,
            credential,
        ) as attest_client:
            response, _ = await attest_client.attest_open_enclave(
                oe_report, runtime_json=runtime_data
            )

        print("Issuer of token is: ", response.issuer)
        print("Response JSON value is:", json.dumps(response.runtime_claims))
        # [END attest_open_enclave_shared_json]

    async def attest_open_enclave_with_draft_policy(self):
        """
        Calls attest_open_enclave specifying a draft attestation policy.

        This functionality can be used to test attestation policies against real attestation
        collateral. This can be extremely helpful in debugging attestation policies.
        """
        write_banner("attest_open_enclave_with_draft_policy")
        oe_report = base64.urlsafe_b64decode(sample_open_enclave_report)
        runtime_data = base64.urlsafe_b64decode(sample_runtime_data)

        # [START attest_open_enclave_shared_draft]
        draft_policy = """
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
        print("Attest Open enclave using ", self.shared_url)
        print("Using draft policy:", draft_policy)
        async with DefaultAzureCredential() as credential, AttestationClient(
            self.shared_url, credential
        ) as attest_client:
            response, token = await attest_client.attest_open_enclave(
                oe_report, runtime_data=runtime_data, draft_policy=draft_policy
            )

            print("Token algorithm", token.algorithm)
            print("Issuer of token is: ", response.issuer)
        # [END attest_open_enclave_shared_draft]

    async def attest_open_enclave_with_draft_failing_policy(self):
        """
        Sets a draft policy which is guaranteed to fail attestation with the
        sample test collateral to show how to manage attestation failures.
        """
        write_banner("attest_open_enclave_with_draft_failing_policy")
        oe_report = base64.urlsafe_b64decode(sample_open_enclave_report)
        runtime_data = base64.urlsafe_b64decode(sample_runtime_data)

        draft_policy = """
version= 1.0;
authorizationrules
{
    [ type=="x-ms-sgx-is-debuggable", value == false] => deny();
    [ type=="x-ms-sgx-product-id", value==1 ] &&
    [ type=="x-ms-sgx-svn", value>= 0 ] &&
    [ type=="x-ms-sgx-mrsigner", value=="2c1a44952ae8207135c6c29b75b8c029372ee94b677e15c20bd42340f10d41aa"]
        => permit();
};
issuancerules {
    c:[type=="x-ms-sgx-mrsigner"] => issue(type="My-MrSigner", value=c.value);
};
"""

        print("Attest Open enclave using ", self.shared_url)
        print("Using draft policy which will fail.:", draft_policy)
        try:
            async with DefaultAzureCredential() as credential, AttestationClient(
                self.shared_url, credential
            ) as attest_client:
                await attest_client.attest_open_enclave(
                    oe_report, runtime_data=runtime_data, draft_policy=draft_policy
                )
                print("Unexpectedly passed attestation.")
        except HttpResponseError as err:
            print("Caught expected exception: ", err.message)
            print("Error is:", err.error.code)
            pass

    async def attest_open_enclave_shared_with_options(self):
        """
        Demonstrates calling into the attest_open_enclave API using an attestation
        token validation callback to perform validation of the attestation collateral
        received from the server.
        """

        write_banner("attest_open_enclave_shared_with_options")
        oe_report = base64.urlsafe_b64decode(sample_open_enclave_report)
        runtime_data = base64.urlsafe_b64decode(sample_runtime_data)
        print()
        print("Attest Open enclave using ", self.shared_url)

        # [START attest_open_enclave_shared_with_options]
        def validate_token(token, signer):
            # type: (AttestationToken, AttestationSigner) -> bool
            """
            Perform minimal validation of the issued SGX token.
            The token validation logic will have checked the issuance_time
            and expiration_time, but this shows accessing those fields.

            The validation logic also checks the subject of the certificate to verify
            that the issuer of the certificate is the expected instance of the service.
            """
            print("In validation callback, checking token...")
            print("     Token issuer: ", token.issuer)
            print("     Token was issued at: ", token.issued)
            print("     Token expires at: ", token.expires)
            if token.issuer != self.shared_url:
                print(
                    "Token issuer {} does not match expected issuer {}".format(
                        token.issuer, self.shared_url
                    )
                )
                return False

            # Check the subject of the signing certificate used to validate the token.
            certificate = cryptography.x509.load_pem_x509_certificate(
                signer.certificates[0].encode("ascii"), backend=default_backend()
            )
            if certificate.subject.rfc4514_string() != "CN=" + self.shared_url:
                print(
                    "Certificate subject {} does not match expected subject {}".format(
                        certificate.subject, self.shared_url
                    )
                )
                return False

            print("Token passes validation checks.")
            return True

        async with DefaultAzureCredential() as credential, AttestationClient(
            self.shared_url, credential, validation_callback=validate_token
        ) as attest_client:
            response, token = await attest_client.attest_open_enclave(
                oe_report, runtime_data=runtime_data
            )

            print("Issuer of token is: ", response.issuer)
            print("Expiration time: ", token.expires)

        # Repeat the same operation, this time specifying the callback options
        # on the attest_open_enclave call.
        async with DefaultAzureCredential() as credential, AttestationClient(
            self.shared_url, credential
        ) as attest_client:
            response, token = await attest_client.attest_open_enclave(
                oe_report, runtime_data=runtime_data, validation_callback=validate_token
            )

            print("Issuer of token is: ", response.issuer)
            print("Expiration time: ", token.expires)
        # [END attest_open_enclave_shared_with_options]

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_type):
        await self.close()


async def main():
    async with AttestationClientAttestationSamples() as sample:
        await sample.attest_sgx_enclave_shared()
        await sample.attest_open_enclave_shared()
        await sample.attest_open_enclave_json_data()
        await sample.attest_open_enclave_shared_with_options()
        await sample.attest_open_enclave_with_draft_policy()
        await sample.attest_open_enclave_with_draft_failing_policy()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
