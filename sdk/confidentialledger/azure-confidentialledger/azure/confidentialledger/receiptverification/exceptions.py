# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Custom exceptions for receipt verification."""


class ReceiptVerificationException(Exception):
    """Exception raised when the receipt verification fails."""


class RootSignatureVerificationException(Exception):
    """Error indicating that the signature verification over the root of the Merkle Tree failed."""


class RootNodeComputationException(Exception):
    """Error indicating that the computation of the root node hash of the Merkle Tree failed."""


class LeafNodeComputationException(Exception):
    """Error indicating that the computation of the leaf node hash failed."""


class EndorsementVerificationException(Exception):
    """Error indicating that the certificate endorsement verification failed."""
