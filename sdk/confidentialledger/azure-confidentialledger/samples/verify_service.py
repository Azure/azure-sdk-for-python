# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: verify_service.py
DESCRIPTION:
    This sample demonstrates methods that may be used to check conditions about the Confidential
    Ledger service. This sample will print the results of verification methods.
USAGE:
    python verify_service.py
    Set the environment variables with your own values before running the sample:
    1) CONFIDENTIALLEDGER_ENDPOINT - the endpoint of the Confidential Ledger.
"""

import hashlib
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
        
        print("Retrieving information that can be used to validate a Confidential Ledger.")

        print(
            "Consortium members can manage and alter the "
            "Confidential Ledger. Microsoft participates in the consortium to maintain the "
            "Confidential Ledger instance."
        )
        consortium = ledger_client.list_consortium_members()
        for member in consortium:
            print(
                f'\tMember {member["id"]} has certificate (truncated) '
                f'{member["certificate"][:24]}...'
            )

        print(
            "The constitution is a collection of JavaScript code that defines actions available to "
            "members and vets proposals by members to execute those actions."
        )

        constitution = ledger_client.get_constitution()
        assert (
            constitution["digest"].lower() ==
            hashlib.sha256(constitution["script"].encode()).hexdigest().lower()
        )
        print(f'\tConstitution (truncated): {constitution["script"][:24]}...')
        print(f'\tConstitution digest: {constitution["digest"]}')

        print(
            "Enclave quotes contain material that can be used to cryptographically verify the "
            "validity and contents of an enclave."
        )
        ledger_enclaves = ledger_client.get_enclave_quotes()
        for node_id, quote in ledger_enclaves["enclaveQuotes"].items():
            print(
                f"\tMRENCLAVE for node {node_id}: {quote['mrenclave']}"
            )


if __name__ == "__main__":
    main()
