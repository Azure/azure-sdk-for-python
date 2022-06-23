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
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()


async def main():
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

    identity_service_client = ConfidentialLedgerIdentityServiceClient(ledger_endpoint)
    ledger_certificate = await identity_service_client.confidential_ledger_identity_service.get_ledger_identity(
        ledger_id
    )

    # The Confidential Ledger's TLS certificate must be written to a file to be used by the
    # ConfidentialLedgerClient. Here, we write it to a temporary file so that is is cleaned up
    # automatically when the program exits.
    with tempfile.NamedTemporaryFile("w", suffix=".pem") as ledger_certificate_file:
        ledger_certificate_file.write(ledger_certificate["ledgerTlsCertificate"])
        ledger_certificate_file.flush()

        # Build a client through AAD
        ledger_client = ConfidentialLedgerClient(
            ledger_endpoint,
            credential=DefaultAzureCredential(),
            ledger_certificate_path=ledger_certificate_file.name,
        )

        post_poller = await ledger_client.begin_post_ledger_entry(
            {"contents": "First message"}
        )
        first_transaction_id = await post_poller.result()["transactionId"]

        for i in range(10):
            await ledger_client.post_ledger_entry({"contents": f"Message {i}"})

        post_poller = await ledger_client.begin_post_ledger_entry(
            {"contents": "Last message"}
        )
        last_transaction_id = await post_poller.result()["transactionId"]

        ranged_result = ledger_client.list_ledger_entries(
            from_transaction_id=first_transaction_id,
            to_transaction_id=last_transaction_id,
        )
        async for entry in ranged_result:
            print(f'Contents at {entry["transactionId"]}: {entry["contents"]}')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
