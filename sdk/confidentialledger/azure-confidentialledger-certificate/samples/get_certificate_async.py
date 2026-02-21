# pylint: disable=line-too-long,useless-suppression
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_certificate_async.py
DESCRIPTION:
    This sample demonstrates how to get the certificate from the Confidential Ledger identity service.
USAGE:
    python get_certificate_async.py
    Set the environment variables with your own values before running the sample:
    1) CONFIDENTIALLEDGER_ENDPOINT - the endpoint of the Confidential Ledger.
"""

import asyncio
import logging
import os
import sys
import tempfile

from azure.confidentialledger.certificate.aio import (
    ConfidentialLedgerCertificateClient,
)


logging.basicConfig(level=logging.ERROR)
LOG = logging.getLogger()


async def main():
    # Set the values of the following environment variables before running the sample:
    # CONFIDENTIALLEDGER_ENDPOINT
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
    async with identity_service_client:
        ledger_certificate = await identity_service_client.get_ledger_identity(ledger_id)

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

        print(
            "The certificate can be used to create a ConfidentialLedgerClient instance."
            "See samples for the azure-confidentialledger package for details:"
            "https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/confidentialledger/azure-confidentialledger/samples"
        )


if __name__ == "__main__":
    asyncio.run(main())
