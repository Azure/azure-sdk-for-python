# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: use_tags.py
DESCRIPTION:
    This sample demonstrates how to use tags inside a Confidential Ledger. In this sample, we write
    ledger entries to a collection using different tags. Tags may be used to group semantically or
    logically related ledger entries within a collection.
USAGE:
    python use_tags.py
    Set the environment variables with your own values before running the sample:
    1) CONFIDENTIALLEDGER_ENDPOINT - the endpoint of the Confidential Ledger.
"""

import logging
import os
import sys
import tempfile
from typing import Any, Dict

from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import (
    ConfidentialLedgerCertificateClient,
)
from azure.identity import DefaultAzureCredential


logging.basicConfig(level=logging.ERROR)
LOG = logging.getLogger()


def main():
    # Set the values of the client ID, tenant ID, and client secret of the AAD application as
    # environment variables:
    #   AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, CONFIDENTIALLEDGER_ENDPOINT
    try:
        ledger_endpoint = os.environ["CONFIDENTIALLEDGER_ENDPOINT"]
    except KeyError:
        LOG.error(
            "Missing environment variable 'CONFIDENTIALLEDGER_ENDPOINT' - " "please set it before running the example"
        )
        sys.exit(1)

    # Under the current URI format, the ledger id is the first part of the ledger endpoint.
    # i.e. https://<ledger id>.confidential-ledger.azure.com
    ledger_id = ledger_endpoint.replace("https://", "").split(".")[0]

    identity_service_client = ConfidentialLedgerCertificateClient()  # type: ignore[call-arg]
    ledger_certificate = identity_service_client.get_ledger_identity(ledger_id)

    # The Confidential Ledger's TLS certificate must be written to a file to be used by the
    # ConfidentialLedgerClient. Here, we write it to a temporary file so that is is cleaned up
    # automatically when the program exits.
    with tempfile.TemporaryDirectory() as tempdir:
        ledger_cert_file = os.path.join(tempdir, f"{ledger_id}.pem")
        with open(ledger_cert_file, "w") as outfile:
            outfile.write(ledger_certificate["ledgerTlsCertificate"])

        print(
            f"Ledger certificate has been written to {ledger_cert_file}. "
            "It will be deleted when the script completes."
        )

        # Build a client through AAD
        ledger_client = ConfidentialLedgerClient(
            ledger_endpoint,
            credential=DefaultAzureCredential(),
            ledger_certificate_path=ledger_cert_file,
        )

        print("This Confidential Ledger will contain messages from different senders.")
        print(
            "We will group ledger entries by the sender of the message. For all client methods "
            "that take an optional 'collection_id' parameter, if none is provided, a "
            "service-assigned, default collection id will be assigned."
        )

        # Lets write some entries with tags and collections.
        # We will write entries into "messages" collection and add tags to each entry.

        transactions = [
            {"contents": "Hello from Alice!"},
            {"contents": "Hi from Bob!"},
            {"contents": "Bye from Alice!"},
            {"contents": "Bye from Bob!"},
        ]

        print("Here are the entries being written to the 'messages' collection:")
        write_result = ledger_client.create_ledger_entry(
            collection_id="messages", entry=transactions[0], tags="alice,greeting"
        )
        print(f"Transaction ID for Alice's greeting: {write_result['transactionId']}")
        write_result = ledger_client.create_ledger_entry(
            collection_id="messages", entry=transactions[1], tags="bob,greeting"
        )
        print(f"Transaction ID for Bob's greeting: {write_result['transactionId']}")
        write_result = ledger_client.create_ledger_entry(
            collection_id="messages", entry=transactions[2], tags="alice,goodbye"
        )
        print(f"Transaction ID for Alice's goodbye: {write_result['transactionId']}")
        write_result = ledger_client.create_ledger_entry(
            collection_id="messages", entry=transactions[3], tags="bob,goodbye"
        )
        print(f"Transaction ID for Bob's goodbye: {write_result['transactionId']}")

        # Lets retrieve all the entries in the collection
        list_result = ledger_client.list_ledger_entries(collection_id="messages")
        print("Here are the entries in the 'messages' collection:")
        for entry in list_result:
            print(f"Transaction ID: {entry['transactionId']}")
            print(f"Contents: {entry['contents']}")
            if "tags" in entry:
                print(f"Tags: {entry['tags']}")
            print("-" * 30)

        # Now lets retrieve all the entries in the collection that are a "greeting"
        list_result = ledger_client.list_ledger_entries(collection_id="messages", tag="greeting")
        print("Here are the entries in the 'messages' collection with tag 'greeting':")
        for entry in list_result:
            print(f"Transaction ID: {entry['transactionId']}")
            print(f"Contents: {entry['contents']}")
            if "tags" in entry:
                print(f"Tags: {entry['tags']}")
            print("-" * 30)

        # Let's retrieve all the goodbyes
        list_result = ledger_client.list_ledger_entries(collection_id="messages", tag="goodbye")
        print("Here are the entries in the 'messages' collection with tag 'goodbye':")
        for entry in list_result:
            print(f"Transaction ID: {entry['transactionId']}")
            print(f"Contents: {entry['contents']}")
            if "tags" in entry:
                print(f"Tags: {entry['tags']}")
            print("-" * 30)

        # Lets retrieve all the entries in the collection that are from Alice
        list_result = ledger_client.list_ledger_entries(collection_id="messages", tag="alice")
        print("Here are the entries in the 'messages' collection with tag 'alice':")
        for entry in list_result:
            print(f"Transaction ID: {entry['transactionId']}")
            print(f"Contents: {entry['contents']}")
            if "tags" in entry:
                print(f"Tags: {entry['tags']}")
            print("-" * 30)

        # Lets retrieve all the entries in the collection that are from Bob
        list_result = ledger_client.list_ledger_entries(collection_id="messages", tag="bob")
        print("Here are the entries in the 'messages' collection with tag 'bob':")
        for entry in list_result:
            print(f"Transaction ID: {entry['transactionId']}")
            print(f"Contents: {entry['contents']}")
            if "tags" in entry:
                print(f"Tags: {entry['tags']}")
            print("-" * 30)


if __name__ == "__main__":
    main()
