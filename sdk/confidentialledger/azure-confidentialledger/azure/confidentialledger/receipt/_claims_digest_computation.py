# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Algorithm implementation for computing Azure Confidential Ledger application claims."""

from base64 import b64decode
from hashlib import sha256
import hmac
from typing import Dict, List, Any

from azure.confidentialledger.receipt._claims_models import (
    ApplicationClaim,
    LedgerEntryClaim,
    ClaimDigest,
)

LEDGER_ENTRY_CLAIM_TYPE = "LedgerEntry"
DIGEST_CLAIM_TYPE = "ClaimDigest"
LEDGER_ENTRY_V1_CLAIM_PROTOCOL = "LedgerEntryV1"


def compute_claims_digest(application_claims: List[Dict[str, Any]]) -> str:
    """
    Compute the claims digest from a list of Azure Confidential Ledger application claims.

    :param application_claims: List of application claims to be verified against the receipt.
    :type application_claims: List[Dict[str, Any]]

    :return: The claims digest of the application claims.
    :rtype: str
    :raises ValueError: If the claims digest computation has failed.
    """

    # The logic is structured in three distinct steps:
    # 1. Claim dictionary validation
    # 2. Claim conversion to object
    # 3. Claims digest computation
    # For every step, we iterate over the list of application claims to process them one by one.
    # While it could be slightly inefficient to have three sets of iterations instead of a single one,
    # the main idea is to have a clean separation of concerns between the different steps
    # (e.g., not mix syntax/formatting errors with logical errors).
    # From a performance perspective, it is not expected to have a large number of application
    # claims in a single receipt (at the time of writing, we only support a single claim per receipt),
    # so the overhead of having three iterations should be negligible.

    # Validate application claims provided by the user
    _validate_application_claims(application_claims)

    # Convert application claims JSON objects to ApplicationClaim model
    application_claims_obj = []
    for claim_dict in application_claims:
        claim = ApplicationClaim.from_dict(claim_dict)
        application_claims_obj.append(claim)

    # Compute claims digest from application claims
    return _compute_claims_hexdigest(application_claims_obj)


def _validate_application_claims(application_claims: List[Dict[str, Any]]):
    """Validate the application claims in a write transaction receipt."""

    assert isinstance(application_claims, list)
    assert len(application_claims) > 0, "Application claims list cannot be empty"

    # Assert on each application claim object in the list
    for application_claim_object in application_claims:
        assert isinstance(application_claim_object, dict)

        # Assert on the kind of the claim
        assert "kind" in application_claim_object
        claim_kind = application_claim_object["kind"]
        assert isinstance(claim_kind, str)

        # Assert on the ledger entry claim
        if claim_kind == "LedgerEntry":
            ledger_entry_claim = application_claim_object.get("ledgerEntry")
            assert isinstance(ledger_entry_claim, dict)

            # Assert on the collection id
            assert "collectionId" in ledger_entry_claim
            assert isinstance(ledger_entry_claim["collectionId"], str)

            # Assert on the contents id
            assert "contents" in ledger_entry_claim
            assert isinstance(ledger_entry_claim["contents"], str)

            # Assert on the protocol
            assert "protocol" in ledger_entry_claim
            assert isinstance(ledger_entry_claim["protocol"], str)

            # Assert on the secret key
            assert "secretKey" in ledger_entry_claim
            assert isinstance(ledger_entry_claim["secretKey"], str)

        # Assert on the digest claim
        elif claim_kind == "ClaimDigest":
            assert "digest" in application_claim_object
            digest_claim = application_claim_object["digest"]
            assert isinstance(digest_claim, dict)

            # Assert on the digest value
            assert "value" in digest_claim
            assert isinstance(digest_claim["value"], str)

            # Assert on the protocol
            assert "protocol" in digest_claim
            assert isinstance(digest_claim["protocol"], str)

        else:
            assert False, f"Unknown claim kind: {claim_kind}"


def _compute_ledger_entry_v1_claim_digest(
    ledger_entry_claim: LedgerEntryClaim,
) -> bytes:
    """Compute the digest of a LedgerEntryV1 claim. It returns the digest in bytes."""

    # Decode the secret key
    secret_key = b64decode(ledger_entry_claim.secretKey, validate=True)

    # HMAC the collection ID with the secret key
    collection_id_digest = hmac.new(
        secret_key,
        ledger_entry_claim.collectionId.encode(),
        sha256,
    ).digest()

    # HMAC the ledger contents with the secret key
    contents_digest = hmac.new(
        secret_key,
        ledger_entry_claim.contents.encode(),
        sha256,
    ).digest()

    # Compute the SHA-256 of the concatenation of the collection ID and contents digests
    return sha256(collection_id_digest + contents_digest).digest()


def _compute_ledger_entry_claim_digest(ledger_entry_claim: LedgerEntryClaim) -> bytes:
    """Compute the digest of a LedgerEntry claim. It returns the digest in bytes."""

    claim_protocol = ledger_entry_claim.protocol

    # Compute the digest based on the specified protocol
    if claim_protocol == LEDGER_ENTRY_V1_CLAIM_PROTOCOL:
        # Compute the digest of the LedgerEntryV1 claim
        ledger_entry_digest = _compute_ledger_entry_v1_claim_digest(ledger_entry_claim)

    else:
        raise ValueError(f"Unsupported claim protocol: {claim_protocol}")

    # Compute the SHA-256 of the concatenation of the protocol and the ledger entry digest
    return sha256(claim_protocol.encode() + ledger_entry_digest).digest()


def _compute_claim_digest_from_object(claim_digest_object: ClaimDigest) -> bytes:
    # Compute the SHA-256 of the concatenation of the protocol and the digest value
    return sha256(
        claim_digest_object.protocol.encode() + bytes.fromhex(claim_digest_object.value)
    ).digest()


def _compute_claims_hexdigest(application_claims_list: List[ApplicationClaim]) -> str:
    """Compute the CCF claims digest from the provided list of application claims objects.
    It returns the hexdigest of the claims digest."""

    # Initialize the claims digest
    claims_digests_concatenation = b""

    # Iterate through all the application claims objects to compute their single digest.
    # We assume that the order of the application objects is valid
    # and the digests will be concatenated in the same order.
    for application_claim_object in application_claims_list:
        # Get the kind of the claim
        claim_kind = application_claim_object.kind

        if claim_kind == LEDGER_ENTRY_CLAIM_TYPE:
            # Compute the digest of the LedgerEntry claim
            claim_digest = _compute_ledger_entry_claim_digest(
                application_claim_object.ledgerEntry
            )

        elif claim_kind == DIGEST_CLAIM_TYPE:
            # Compute the digest of the ClaimDigest claim
            claim_digest = _compute_claim_digest_from_object(
                application_claim_object.digest
            )

        else:
            raise ValueError(f"Unsupported claim kind: {claim_kind}")

        # Append the computed digest to the result
        claims_digests_concatenation += claim_digest

    # Prepend the size of application claims to the concatenation of the digests
    claims_digests_concatenation = (
        len(application_claims_list).to_bytes(length=4, byteorder="little")
        + claims_digests_concatenation
    )

    # Hash the concatenation of application claims and return the digest in hexadecimal form
    return sha256(claims_digests_concatenation).hexdigest()
