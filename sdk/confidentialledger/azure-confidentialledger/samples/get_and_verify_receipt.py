# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_and_verify_receipt.py
DESCRIPTION:
    This sample demonstrates how to retrieve Confidential Ledger receipts
    and verify their content. In this sample, we write a ledger entry, retrieve
    a receipt certifying that it was written correctly, and then verify its
    content by applying the receipt verification algorithm.
USAGE:
    python get_and_verify_receipt.py
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
from azure.confidentialledger.receipt import (
    verify_receipt,
)
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential


logging.basicConfig(level=logging.ERROR)
LOG = logging.getLogger()


def main():
    """Main method."""

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

        # Write a ledger entry and wait for the transaction to be committed.
        try:
            entry_contents = "Hello world!"
            post_poller = ledger_client.begin_create_ledger_entry(
                {"contents": entry_contents}
            )
            post_entry_result = post_poller.result()
            transaction_id = post_entry_result["transactionId"]
            print(
                f"Wrote '{entry_contents}' to the ledger at transaction {transaction_id}."
            )
        except HttpResponseError as e:
            if e.response != None:
                print("Request failed: {}".format(e.response.json()))
            else:
                print("No response found")
            raise

        # Get a receipt for a ledger entry.
        # A receipt can be retrieved for any transaction id to provide cryptographic proof of the
        # contents of the transaction.
        try:
            print(
                f"Retrieving a receipt for {transaction_id}. The receipt may be used to "
                "cryptographically verify the contents of the transaction."
            )
            print(
                "For more information about receipts, please see "
                "https://microsoft.github.io/CCF/main/audit/receipts.html#receipts"
            )
            get_receipt_poller = ledger_client.begin_get_receipt(transaction_id)
            get_receipt_result = get_receipt_poller.result()
            print(f"Receipt for transaction id {transaction_id}: {get_receipt_result}")
        except HttpResponseError as e:
            if e.response != None:
                print("Request failed: {}".format(e.response.json()))
            else:
                print("No response found")
            raise

        # Read content of service certificate file saved in previous step.
        with open(ledger_cert_file, "r") as service_cert_file:
            service_cert_content = service_cert_file.read()

        # Optionally read application claims, if any
        application_claims = get_receipt_result.get("applicationClaims", None)

        try:
            # Verify the contents of the receipt.
            verify_receipt(
                get_receipt_result["receipt"],
                service_cert_content,
                application_claims=application_claims,
            )
            print(f"Receipt for transaction id {transaction_id} successfully verified")
        except ValueError:
            print(f"Receipt verification for transaction id {transaction_id} failed")
            raise


if __name__ == "__main__":
    main()
