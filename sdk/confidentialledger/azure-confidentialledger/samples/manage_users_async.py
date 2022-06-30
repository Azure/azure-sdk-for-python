# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: manage_users_async.py
DESCRIPTION:
    This sample demonstrates how to manage users using Confidential Ledger's native role-based
    access control. In this sample, we add two test users - one using a random AAD-object-id-like
    identifier, and one using the thumbprint of a test certificate.
USAGE:
    python manage_users_async.py
    Set the environment variables with your own values before running the sample:
    1) CONFIDENTIALLEDGER_ENDPOINT - the endpoint of the Confidential Ledger.
"""

import asyncio
import logging
import os
import sys
import tempfile

from azure.confidentialledger.aio import ConfidentialLedgerClient
from azure.confidentialledger.identity_service.aio import (
    ConfidentialLedgerIdentityServiceClient,
)
from azure.identity.aio import DefaultAzureCredential


logging.basicConfig(level=logging.ERROR)
LOG = logging.getLogger()


async def main():
    # Example values identifying users.
    # This is an example thumbprint for certificate identifying a certificate-based user.
    cert_thumbprint = "4F:E1:61:D8:6E:5A:7B:E6:00:25:A6:D8:5D:EC:2C:71:E5:86:C3:E4:70:BE:D0:3C:73:7E:69:00:87:98:B0:25"
    # This is an example AAD object id identifying an AAD-based user.
    aad_object_id = "0" * 36  # AAD Object Ids have length 36

    # Set the values of the client ID, tenant ID, and client secret of the AAD application as
    # environment variables:
    #   AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, CONFIDENTIALLEDGER_ENDPOINT
    try:
        ledger_endpoint = os.environ["CONFIDENTIALLEDGER_ENDPOINT"]
    except KeyError:
        LOG.error(
            "Missing environment variable 'CONFIDENTIALLEDGER_ENDPOINT' - "
            "please set if before running the example"
        )
        sys.exit(1)

    # Under the current URI format, the ledger id is the first part of the ledger endpoint.
    # i.e. https://<ledger id>.confidential-ledger.azure.com
    ledger_id = ledger_endpoint.replace("https://", "").split(".")[0]

    identity_service_client = ConfidentialLedgerIdentityServiceClient()
    async with identity_service_client:
        ledger_certificate = await identity_service_client.get_ledger_identity(
            ledger_id
        )

    # The Confidential Ledger's TLS certificate must be written to a file to be used by the
    # ConfidentialLedgerClient. Here, we write it to a temporary file so that is is cleaned up
    # automatically when the program exits.
    with tempfile.NamedTemporaryFile("w", suffix=".pem") as ledger_certificate_file:
        ledger_certificate_file.write(ledger_certificate["ledgerTlsCertificate"])
        ledger_certificate_file.flush()

        # Build a client through AAD
        credential = DefaultAzureCredential()
        ledger_client = ConfidentialLedgerClient(
            ledger_endpoint,
            credential=credential,
            ledger_certificate_path=ledger_certificate_file.name,
        )

        # Using the async objects as a context manager ensures they are properly closed after use.
        async with credential:
            async with ledger_client:
                try:
                    role = "Reader"
                    await ledger_client.create_or_update_user(
                        aad_object_id, {"assignedRole": role}
                    )
                    print(f"User {aad_object_id} has been added as a {role}")

                    role = "Contributor"
                    await ledger_client.create_or_update_user(
                        cert_thumbprint, {"assignedRole": role}
                    )
                    print(f"User {cert_thumbprint} has been added as a {role}")

                    print(
                        "Sleeping 3 seconds before getting user details. Due to replication lag, "
                        "it may not immediately be available."
                    )
                    await asyncio.sleep(3)

                    aad_user_details = await ledger_client.get_user(aad_object_id)
                    print(f"Details about user {aad_object_id}: {aad_user_details}")

                    cert_user_details = await ledger_client.get_user(cert_thumbprint)
                    print(f"Details about user {cert_thumbprint}: {cert_user_details}")

                # Always delete the user in case an exception is raised.
                finally:
                    try:
                        await ledger_client.delete_user(aad_object_id)
                        print(f"User {aad_object_id} deleted")
                    finally:
                        await ledger_client.delete_user(cert_thumbprint)
                        print(f"User {cert_thumbprint} deleted")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
