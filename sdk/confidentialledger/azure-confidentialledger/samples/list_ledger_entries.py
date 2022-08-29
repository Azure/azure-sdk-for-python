# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: list_ledger_entries.py
DESCRIPTION:
    This sample demonstrates how to iteratively retrieve a batch of ledger entries. In this sample,
    we write many ledger entries before retrieving them at once.
USAGE:
    python list_ledger_entries.py
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
            "please set it before running the example"
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

        post_poller = ledger_client.begin_create_ledger_entry({"contents": "First message"})
        first_transaction_id = post_poller.result()["transactionId"]

        print(
            "Wrote 'First message' to the ledger. It is recorded at transaction id "
            f"{first_transaction_id}."
        )

        for i in range(10):
            entry_contents = f"Message {i}"
            print(
                f"Writing '{entry_contents}' to the ledger."
            )

            ledger_client.create_ledger_entry({"contents": entry_contents})

        post_poller = ledger_client.begin_create_ledger_entry({"contents": "Last message"})
        last_transaction_id = post_poller.result()["transactionId"]

        print(
            "Wrote 'Last message' to the ledger. It is recorded at transaction id "
            f"{last_transaction_id}."
        )

        ranged_result = ledger_client.list_ledger_entries(
            from_transaction_id=first_transaction_id,
            to_transaction_id=last_transaction_id,
        )
        for entry in ranged_result:
            print(f'Contents at {entry["transactionId"]}: {entry["contents"]}')


if __name__ == "__main__":
    main()
