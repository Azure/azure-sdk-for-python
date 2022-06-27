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
from azure.identity.aio import DefaultAzureCredential


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
                # Write a ledger entry.
                try:
                    post_entry_result = await ledger_client.post_ledger_entry(
                        {"contents": "Hello world!"}
                    )
                    transaction_id = post_entry_result["transactionId"]
                    print(
                        f"Successfully sent a ledger entry with transaction id {transaction_id}"
                    )
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise

                # For some scenarios, users may want to eventually ensure the written entry is durably
                # committed.
                try:
                    wait_poller = await ledger_client.begin_wait_for_commit(
                        transaction_id
                    )
                    await wait_poller.wait()
                    print(
                        f"Ledger entry at transaction id {transaction_id} has been committed successfully"
                    )
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise

                # Get the latest ledger entry.
                try:
                    current_ledger_entry = (
                        await ledger_client.get_current_ledger_entry()
                    )
                    print(
                        f'The current ledger entry is {current_ledger_entry["contents"]}'
                    )
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise

                # Users may wait for a durable commit when writing a ledger entry though this will reduce
                # client throughput.
                try:
                    post_poller = await ledger_client.begin_post_ledger_entry(
                        {"contents": "Hello world again!"}
                    )
                    new_post_result = await post_poller.result()
                    print(
                        "The new ledger entry has been committed successfully at transaction id "
                        f'{new_post_result["transactionId"]}'
                    )
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise

                # Get the latest ledger entry.
                try:
                    current_ledger_entry = (
                        await ledger_client.get_current_ledger_entry()
                    )
                    print(
                        f'The current ledger entry is {current_ledger_entry["contents"]}'
                    )
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise

                # Make a query for a prior ledger entry. The service may take some time to load the result, so a
                # poller is provided.
                try:
                    get_entry_poller = await ledger_client.begin_get_ledger_entry(
                        transaction_id
                    )
                    get_entry_result = await get_entry_poller.result()
                    print(
                        f'At transaction id {get_entry_result["transactionId"]}, the ledger entry contains '
                        f'\'{get_entry_result["contents"]}\''
                    )
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise

                # Get a receipt for a  ledger entry.
                try:
                    get_receipt_poller = await ledger_client.begin_get_receipt(
                        transaction_id
                    )
                    get_receipt_result = await get_receipt_poller.result()
                    print(
                        f'Receipt for transaction id {get_entry_result["transactionId"]}: {get_receipt_result}'
                    )
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise

                # Users may specify a collectionId to group different sets of writes.
                collection_id = "myCollection"
                try:
                    post_poller = await ledger_client.begin_post_ledger_entry(
                        {"contents": "Hello world again!"},
                        collection_id=collection_id,
                    )
                    new_post_result = await post_poller.result()
                    print(
                        f"The ledger entry for {collection_id} has been committed successfully at "
                        f'transaction id {new_post_result["transactionId"]}'
                    )
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise

                # Get the latest ledger entry in the collection.
                try:
                    current_ledger_entry = await ledger_client.get_current_ledger_entry(
                        collection_id=collection_id
                    )
                    print(
                        f'The current ledger entry in {collection_id} is {current_ledger_entry["contents"]}'
                    )
                except HttpResponseError as e:
                    print("Request failed: {}".format(e.response.json()))
                    raise


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
