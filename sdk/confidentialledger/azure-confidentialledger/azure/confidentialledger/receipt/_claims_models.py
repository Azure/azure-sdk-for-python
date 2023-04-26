# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Models for application claims."""

from typing import Any, Dict, Optional, Union


class LedgerEntryClaim:
    """
    LedgerEntryClaim represents an Application Claim derived from ledger entry data.
    """

    def __init__(
        self,
        protocol: str,
        collectionId: str,
        contents: str,
        secretKey: str,
    ):
        """
        :keyword protocol: The protocol used to compute the claim.
        :paramtype protocol: str

        :keyword collectionId: The collection ID of the ledger entry.
        :paramtype collectionId: str

        :keyword contents: The contents of the ledger entry.
        :paramtype contents: str

        :keyword secretKey: The secret key used to compute the claim digest.
        :paramtype secretKey: str
        """
        self.protocol = protocol
        self.collectionId = collectionId
        self.contents = contents
        self.secretKey = secretKey

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, LedgerEntryClaim):
            return NotImplemented

        return (
            self.protocol == other.protocol
            and self.collectionId == other.collectionId
            and self.contents == other.contents
            and self.secretKey == other.secretKey
        )

    @classmethod
    def from_dict(cls, ledger_entry_claim_dict: Dict[str, Any]):
        """Create a new instance of this class from a dictionary."""

        return cls(
            protocol=ledger_entry_claim_dict["protocol"],
            collectionId=ledger_entry_claim_dict["collectionId"],
            contents=ledger_entry_claim_dict["contents"],
            secretKey=ledger_entry_claim_dict["secretKey"],
        )


class ClaimDigest:
    """
    ClaimDigest represents an Application Claim in digested form.
    """

    def __init__(
        self,
        protocol: str,
        value: str,
    ):
        """
        :keyword protocol: The protocol used to compute the claim.
        :paramtype protocol: str

        :keyword value: The digest of the claim.
        :paramtype value: str
        """
        self.protocol = protocol
        self.value = value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ClaimDigest):
            return NotImplemented

        return self.protocol == other.protocol and self.value == other.value

    @classmethod
    def from_dict(cls, ledger_entry_claim_dict: Dict[str, Any]):
        """Create a new instance of this class from a dictionary."""

        return cls(
            protocol=ledger_entry_claim_dict["protocol"],
            value=ledger_entry_claim_dict["value"],
        )


class ApplicationClaim:
    """
    ApplicationClaim represents a claim of a ledger application.
    """

    def __init__(
        self,
        kind: str,
        ledgerEntry: Optional[Union[Dict[str, Any], LedgerEntryClaim]] = None,
        digest: Optional[Union[Dict[str, Any], ClaimDigest]] = None,
    ):
        """
        :keyword kind: The kind of the claim.
        :paramtype kind: str

        :keyword ledgerEntry: The ledger entry claim.
        :paramtype ledgerEntry: Optional[Union[Dict[str, Any], LedgerEntryClaim]]

        :keyword digest: The claim digest object.
        :paramtype digest: Optional[Union[Dict[str, Any], ClaimDigest]]
        """
        self.kind = kind

        if ledgerEntry:
            if isinstance(ledgerEntry, LedgerEntryClaim):
                self.ledgerEntry = ledgerEntry
            else:
                self.ledgerEntry = LedgerEntryClaim.from_dict(ledgerEntry)
        else:
            self.ledgerEntry = None

        if digest:
            if isinstance(digest, ClaimDigest):
                self.digest = digest
            else:
                self.digest = ClaimDigest.from_dict(digest)
        else:
            self.digest = None

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ApplicationClaim):
            return NotImplemented

        return (
            self.kind == other.kind
            and self.ledgerEntry == other.ledgerEntry
            and self.digest == other.digest
        )

    @classmethod
    def from_dict(cls, claim_dict: Dict[str, Any]):
        """Create a new instance of this class from a dictionary."""

        return cls(
            kind=claim_dict["kind"],
            ledgerEntry=claim_dict.get("ledgerEntry", None),
            digest=claim_dict.get("digest", None),
        )
