# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_receipt_async.py
DESCRIPTION:
    This sample demonstrates how to retrieve Confidential Ledger receipts. In this sample, we write
    a ledger entry and retrieve a receipt certifying that it was written correctly. 
USAGE:
    python get_receipt_async.py
    Set the environment variables with your own values before running the sample:
    1) CONFIDENTIALLEDGER_ENDPOINT - the endpoint of the Confidential Ledger.
"""

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
from azure.identity.aio import DefaultAzureCredential


logging.basicConfig(level=logging.ERROR)
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
                # Write a ledger entry.
                try:
                    entry_contents = "Hello world!"
                    post_poller = await ledger_client.begin_post_ledger_entry(
                        {"contents": entry_contents}
                    )
                    post_entry_result = await post_poller.result()
                    transaction_id = post_entry_result["transactionId"]
                    print(f"Wrote '{entry_contents}' to the ledger at transaction {transaction_id}.")
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise

                # Get a receipt for a ledger entry.
                # A receipt can be retrieved for any transaction id to provide cryptographic proof
                # of the contents of the transaction.
                try:
                    print(
                        f"Retrieving a receipt for {transaction_id}. The receipt may be used to "
                        "cryptographically verify the contents of the transaction."
                    )
                    print(
                        "For more information about receipts, please see "
                        "https://microsoft.github.io/CCF/main/audit/receipts.html#receipts"
                    )
                    get_receipt_poller = await ledger_client.begin_get_receipt(transaction_id)
                    get_receipt_result = await get_receipt_poller.result()
                    print(
                        f'Receipt for transaction id {transaction_id}: {get_receipt_result}'
                    )
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
