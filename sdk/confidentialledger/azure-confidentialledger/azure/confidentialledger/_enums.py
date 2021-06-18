# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum


class LedgerUserRole(Enum):
    """User roles assignable in a Confidential Ledger."""

    ADMINISTRATOR = "Administrator"
    CONTRIBUTOR = "Contributor"
    READER = "Reader"


class TransactionState(Enum):
    """Indicates the status of a transaction."""

    COMMITTED = "Committed"
    PENDING = "Pending"
