# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Models for application claims."""

from typing import Any, Dict, Optional, Union
from dataclasses import dataclass


@dataclass
class LedgerEntryClaim:
    """
    LedgerEntryClaim represents an Application Claim derived from ledger entry data.

    :keyword protocol: The protocol used to compute the claim.
    :paramtype protocol: str

    :keyword collectionId: The collection ID of the ledger entry.
    :paramtype collectionId: str

    :keyword contents: The contents of the ledger entry.
    :paramtype contents: str

    :keyword secretKey: The secret key used to compute the claim digest.
    :paramtype secretKey: str
    """

    protocol: str
    collectionId: str
    contents: str
    secretKey: str

    @classmethod
    def from_dict(cls, ledger_entry_claim_dict: Dict[str, Any]):
        """Create a new instance of this class from a dictionary."""

        return cls(**ledger_entry_claim_dict)


@dataclass
class ClaimDigest:
    """
    ClaimDigest represents an Application Claim in digested form.

    :keyword protocol: The protocol used to compute the claim.
    :paramtype protocol: str

    :keyword value: The digest of the claim.
    :paramtype value: str
    """

    protocol: str
    value: str

    @classmethod
    def from_dict(cls, ledger_entry_claim_dict: Dict[str, Any]):
        """Create a new instance of this class from a dictionary."""

        return cls(**ledger_entry_claim_dict)


@dataclass
class ApplicationClaim:
    """
    ApplicationClaim represents a claim of a ledger application.

    :keyword kind: The kind of the claim.
    :paramtype kind: str

    :keyword ledgerEntry: The ledger entry claim.
    :paramtype ledgerEntry: Optional[Union[Dict[str, Any], LedgerEntryClaim]]

    :keyword digest: The claim digest object.
    :paramtype digest: Optional[Union[Dict[str, Any], ClaimDigest]]
    """

    kind: str
    ledgerEntry: Optional[LedgerEntryClaim] = None
    digest: Optional[ClaimDigest] = None

    def __init__(
        self,
        kind: str,
        ledgerEntry: Optional[Union[Dict[str, Any], LedgerEntryClaim]] = None,
        digest: Optional[Union[Dict[str, Any], ClaimDigest]] = None,
        **kwargs: Any
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

        self.kwargs = kwargs

    @classmethod
    def from_dict(cls, claim_dict: Dict[str, Any]):
        """Create a new instance of this class from a dictionary."""

        return cls(**claim_dict)
