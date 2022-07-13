# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: use_collections.py
DESCRIPTION:
    This sample demonstrates how to use collections in Confidential Ledger. In this sample, we write
    ledger entries to different collections. Collections may be used to group semantically or
    logically related ledger entries.
USAGE:
    python use_collections.py
    Set the environment variables with your own values before running the sample:
    1) CONFIDENTIALLEDGER_ENDPOINT - the endpoint of the Confidential Ledger.
"""

import logging
import os
import sys
import tempfile

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
            "Missing environment variable 'CONFIDENTIALLEDGER_ENDPOINT' - "
            "please set if before running the example"
        )
        sys.exit(1)

    # Under the current URI format, the ledger id is the first part of the ledger endpoint.
    # i.e. https://<ledger id>.confidential-ledger.azure.com
    ledger_id = ledger_endpoint.replace("https://", "").split(".")[0]

    identity_service_client = ConfidentialLedgerCertificateClient()
    ledger_certificate = identity_service_client.get_ledger_identity(ledger_id)

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

        print("This Confidential Ledger will contain messages from different senders.")
        print(
            "We will group ledger entries by the sender of the message. For all client methods "
            "that take an optional 'collection_id' parameter, if none is provided, a "
            "service-assigned, default collection id will be assigned."
        )

        tids = {}
        senders = [None, "Alice", "Bob"]
        for msg_idx in range(3):
            for sender in senders:
                if sender is None:
                    msg = f"My message {msg_idx}"
                else:
                    msg = f"{sender}'s message {msg_idx}"

                post_poller = ledger_client.begin_create_ledger_entry(
                    entry={"contents": msg}, collection_id=sender,
                )
                post_result = post_poller.result()

                if sender is None:
                    print(
                        f"Wrote '{msg}' to the default collection at {post_result['transactionId']}"
                    )
                else:
                    print(f"Wrote '{msg}' to collection {sender} at {post_result['transactionId']}")

                if sender not in tids:
                    tids[sender] = {}
                    tids[sender]["first"] = post_result["transactionId"]

                tids[sender]["last"] = post_result["transactionId"]

        print("Let's retrieve the latest entry in each collection")
        for sender in senders:
            current_entry = ledger_client.get_current_ledger_entry()
            
            output = "Current entry in {0} is {1}"
            print(
                output.format(
                    "default collection" if sender is None else f"{sender}'s collection",
                    current_entry["contents"],
                )
            )

        print("Let's retrieve the first entry in each collection")
        for sender in senders:
            get_poller = ledger_client.begin_get_ledger_entry(
                tids[sender]["first"],
                collection_id=sender
            )
            first_entry = get_poller.result()
            
            output = "First entry in {0} is {1}"
            print(
                output.format(
                    "default collection" if sender is None else f"{sender}'s collection",
                    first_entry["entry"]["contents"],
                )
            )

        print("Let's retrieve get all the entries in each collection")
        for sender in senders:
            entries_list = ledger_client.list_ledger_entries(
                collection_id=sender,
                from_transaction_id=tids[sender]["first"],
                to_transaction_id=tids[sender]["last"],
            )
            
            for entry in entries_list:
                output = "Entry in {0}: {1}"
                print(
                    output.format(
                        "default collection" if sender is None else f"{sender}'s collection",
                        entry,
                    )
                )

        collection_ids = []
        collections = ledger_client.list_collections()
        for collection in collections:
            collection_ids.append(collection["collectionId"])

        print(
            "In conclusion, these are all the collections in the Confidential Ledger:\n" +
            "\n\t".join(collection_ids)
        )


if __name__ == "__main__":
    main()
