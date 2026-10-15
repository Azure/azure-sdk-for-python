# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional


class AuthorizedReceiptBehavior(Enum):
    """Specifies how receipts whose issuer domains ARE in the authorized list should be enforced."""

    VERIFY_ANY_MATCHING = 0
    """At least one receipt from any authorized domain must be present and valid."""

    VERIFY_ALL_MATCHING = 1
    """ALL receipts whose issuer is in the authorized list MUST pass verification."""

    REQUIRE_ALL = 2
    """There MUST be at least one valid receipt for EACH domain in the authorized list."""


class UnauthorizedReceiptBehavior(Enum):
    """Specifies behaviors for receipts whose issuer domains are not in the authorized list."""

    VERIFY_ALL = 0
    """Verify receipts even if their issuer domain is not in the authorized list."""

    IGNORE_ALL = 1
    """Ignore (skip verifying) receipts whose issuer domain is not in the authorized list."""

    FAIL_IF_PRESENT = 2
    """Fail verification immediately if any receipt exists whose issuer domain is not authorized."""


class OfflineKeysBehavior(Enum):
    """Specifies behaviors for the use of offline keys."""

    FALLBACK_TO_NETWORK = 0
    """Use offline keys when available, but fall back to network retrieval if no offline key is found."""

    NO_FALLBACK_TO_NETWORK = 1
    """Use only offline keys. If no offline key is found for a given ledger domain, verification fails."""


@dataclass
class CodeTransparencyOfflineKeys:
    """Stores offline keys by issuer domain for offline verification."""

    by_issuer: Dict[str, Any] = field(default_factory=dict)
    """Mapping of issuer domains to JWKS documents."""


@dataclass
class VerificationOptions:
    """Options controlling transparent statement verification."""

    authorized_domains: List[str] = field(default_factory=list)
    """An authorized list of issuer domains. If provided and not empty,
    at least one receipt must be issued by one of these domains.
    Domains are matched case-insensitively."""

    unauthorized_receipt_behavior: UnauthorizedReceiptBehavior = (
        UnauthorizedReceiptBehavior.FAIL_IF_PRESENT
    )
    """The behavior for receipts whose issuer domain is not in authorized_domains."""

    authorized_receipt_behavior: AuthorizedReceiptBehavior = (
        AuthorizedReceiptBehavior.VERIFY_ALL_MATCHING
    )
    """The enforcement behavior for receipts whose issuer domain IS in authorized_domains."""

    offline_keys: Optional[CodeTransparencyOfflineKeys] = None
    """A store mapping ledger domains to JWKS documents for offline verification."""

    offline_keys_behavior: OfflineKeysBehavior = OfflineKeysBehavior.FALLBACK_TO_NETWORK
    """The behavior for using offline keys."""
