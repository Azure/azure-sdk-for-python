# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

import asyncio
import logging
import os
import sys
import tempfile

from azure.confidentialledger_identity_service.aio import (
    ConfidentialLedgerIdentityServiceClient,
)
from azure.confidentialledger.aio import ConfidentialLedgerClient
from azure.identity.aio import DefaultAzureCredential


logging.basicConfig(level=logging.DEBUG)
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
