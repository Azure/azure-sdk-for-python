# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.confidentialledger.receipt._claims_models import (
    ApplicationClaim,
    LedgerEntryClaim,
    ClaimDigest,
)


def get_test_application_claims_with_ledger_entry_dict():
    return [
        {
            "kind": "LedgerEntry",
            "ledgerEntry": {
                "collectionId": "subledger:0",
                "contents": "Hello world",
                "protocol": "LedgerEntryV1",
                "secretKey": "Jde/VvaIfyrjQ/B19P+UJCBwmcrgN7sERStoyHnYO0M=",
            },
        }
    ]


def get_test_application_claims_with_ledger_entry():
    return [
        ApplicationClaim(
            kind="LedgerEntry",
            ledgerEntry=LedgerEntryClaim(
                collectionId="subledger:0",
                contents="Hello world",
                protocol="LedgerEntryV1",
                secretKey="Jde/VvaIfyrjQ/B19P+UJCBwmcrgN7sERStoyHnYO0M=",
            ),
        )
    ]


def get_test_application_claims_with_claim_digest_dict():
    return [
        {
            "kind": "ClaimDigest",
            "digest": {
                "protocol": "LedgerEntryV1",
                "value": "feb516ef1f903c64f1e388d9ee9fde11f64d1e2bc170248828c9eab9894f9ab9",
            },
        }
    ]


def get_test_application_claims_with_claim_digest():
    return [
        ApplicationClaim(
            kind="ClaimDigest",
            digest=ClaimDigest(
                protocol="LedgerEntryV1",
                value="feb516ef1f903c64f1e388d9ee9fde11f64d1e2bc170248828c9eab9894f9ab9",
            ),
        )
    ]
