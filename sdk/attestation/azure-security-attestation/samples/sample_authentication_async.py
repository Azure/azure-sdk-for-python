# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py

DESCRIPTION:
    These samples demonstrate authenticating an attestation client instance and
    an attestation administration client instance.

USAGE:
    python sample_authentication.py

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
    python sample_authentication_async.py

This sample demonstrates establishing a connection to the attestation service
using client secrets stored in environment variables. 

To verify that the connection completed successfully, it also calls the 
`get_openidmetadata` API on the client to retrieve the OpenID metadata discovery 
document for the attestation service instance.

"""


import os
from dotenv import find_dotenv, load_dotenv
import base64
import asyncio
from sample_utils import write_banner


class AttestationClientCreateSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.aad_url = os.environ.get("ATTESTATION_AAD_URL")
        self.isolated_url = os.environ.get("ATTESTATION_ISOLATED_URL")
        if self.isolated_url:
            self.isolated_certificate = base64.b64decode(
                os.getenv("ATTESTATION_ISOLATED_SIGNING_CERTIFICATE")
            )
            self.isolated_key = base64.b64decode(
                os.getenv("ATTESTATION_ISOLATED_SIGNING_KEY")
            )
        shared_short_name = os.getenv("ATTESTATION_LOCATION_SHORT_NAME")
        self.shared_url = "https://shared{}.{}.attest.azure.net".format(
            shared_short_name, shared_short_name
        )  # type: str

    async def close(self):
        pass

    async def create_attestation_client_aad(self):
        """
        Instantiate an attestation client using client secrets.
        """

        write_banner("create_attestation_client_aad")
        # [START client_create]
        # Create azure-identity class
        from azure.identity.aio import DefaultAzureCredential

        from azure.security.attestation.aio import AttestationClient

        async with DefaultAzureCredential() as credentials, AttestationClient(
            self.aad_url, credentials
        ) as client:
            print("Retrieve OpenID metadata from: ", self.aad_url)
            openid_metadata = await client.get_open_id_metadata()
            print(" Certificate URI: ", openid_metadata["jwks_uri"])
            print(" Issuer: ", openid_metadata["issuer"])
            await client.close()
        # [END client_create]

    async def create_attestation_client_shared(self):
        """
        Instantiate an attestation client using client secrets to access the shared attestation provider.
        """

        write_banner("create_attestation_client_shared")
        # [START sharedclient_create]
        # Import default credential and Attestation client
        from azure.identity.aio import DefaultAzureCredential
        from azure.security.attestation.aio import AttestationClient

        shared_short_name = os.getenv("ATTESTATION_LOCATION_SHORT_NAME")
        shared_url = (
            "https://shared"
            + shared_short_name
            + "."
            + shared_short_name
            + ".attest.azure.net"
        )

        async with DefaultAzureCredential() as credentials, AttestationClient(
            self.aad_url, credentials
        ) as client:
            print("Retrieve OpenID metadata from: ", shared_url)
            openid_metadata = await client.get_open_id_metadata()
            print(" Certificate URI: ", openid_metadata["jwks_uri"])
            print(" Issuer: ", openid_metadata["issuer"])
        # [END shared_client_create]

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_type):
        await self.close()


async def main():
    async with AttestationClientCreateSamples() as sample:
        await sample.create_attestation_client_aad()
        await sample.create_attestation_client_shared()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
