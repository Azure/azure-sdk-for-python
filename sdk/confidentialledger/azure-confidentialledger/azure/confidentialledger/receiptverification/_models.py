# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Models for receipt verification."""

from typing import List, Optional
from azure.confidentialledger.receiptverification._serialization import (
    Model,
)


class ProofElement(Model):
    """ProofElement represents the object contained in the `proof` list field
    of an Azure Confidential Ledger write transaction receipt. The `proof` list
    contains the hashes of the nodes in the Merkle Tree and their relative
    position with respect to the parent node (`left` or `right`); the given
    information allow the re-computation of the root node from a given leaf
    node.

    Each ProofElement should contain either the `left` or the `right` field,
    but not both or none of them.

    :ivar left: Hash of a left node in the Merkle Tree, as an hexadecimal string.
    :vartype left: str
    :ivar right: Hash of a right node in the Merkle Tree, as an hexadecimal string.
    :vartype right: str
    """

    _attribute_map = {
        "left": {"key": "left", "type": "str"},
        "right": {"key": "right", "type": "str"},
    }

    def __init__(
        self, *, left: Optional[str] = None, right: Optional[str] = None, **kwargs
    ):
        """
        :keyword left: Hash of a left node in the Merkle Tree, as an hexadecimal string.
        :paramtype left: str
        :keyword right: Hash of a right node in the Merkle Tree, as an hexadecimal string.
        :paramtype right: str
        """
        super().__init__(**kwargs)
        self.left = left
        self.right = right


class LeafComponents(Model):
    """LeafComponents represents the object contained in the `leafComponents`
    field of an Azure Confidential Ledger write transaction receipt. The
    `leafComponents` field contains the elements that are hashed to compute
    the leaf node corresponding to the transaction associated to the given
    receipt.

    :ivar claimsDigest: Hexadecimal string representing the digest of
        the application claim attached by the Azure Confidential Ledger application.
    :vartype claimsDigest: str
    :ivar commitEvidence: A unique string that identifies a transaction / commit,
        derived from the transaction ID and the secrets used by the Azure Confidential Ledger.
    :vartype commitEvidence: str
    :ivar writeSetDigest: Hexadecimal string representing the digest of the keys
        and values written during a transaction, that captures the state of the
        ledger at the time the transaction was committed.
    :vartype writeSetDigest: str
    """

    _validation = {
        "claimsDigest": {"required": True},
        "commitEvidence": {"required": True},
        "writeSetDigest": {"required": True},
    }

    _attribute_map = {
        "claimsDigest": {"key": "claimsDigest", "type": "str"},
        "commitEvidence": {"key": "commitEvidence", "type": "str"},
        "writeSetDigest": {"key": "writeSetDigest", "type": "str"},
    }

    def __init__(
        self, *, claimsDigest: str, commitEvidence: str, writeSetDigest: str, **kwargs
    ):
        """
        :keyword claimsDigest: Hexadecimal string representing the digest of
            the application claim attached by the Azure Confidential Ledger application.
        :paramtype claimsDigest: str
        :keyword commitEvidence: A unique string that identifies a transaction / commit,
            derived from the transaction ID and the secrets used by the Azure Confidential Ledger.
        :paramtype commitEvidence: str
        :keyword writeSetDigest: Hexadecimal string representing the digest of the keys
            and values written during a transaction, that captures the state of the
            ledger at the time the transaction was committed.
        :paramtype writeSetDigest: str
        """
        super().__init__(**kwargs)
        self.claimsDigest = claimsDigest
        self.commitEvidence = commitEvidence
        self.writeSetDigest = writeSetDigest


class Receipt(Model):
    """Receipt represents the object contained in the `receipt` field of an
    Azure Confidential Ledger `get_receipt` response. A
    receipt is a cryptographic proof that a transaction has been committed to
    the ledger: it can be used to verify that the ledger entry associated to a
    transaction has been appended to the ledger (thus, it can be used to
    validate properties such as non-repudiation, integrity, and tamper-
    proofing). A receipt contains all the information needed to verify
    transaction inclusion and the verification can be done by applying an ad-
    hoc algorithm.

    :ivar cert: PEM-encoded certificate string of the CCF node that signed the transaction.
    :vartype cert: str
    :ivar leafComponents: Components of the leaf node in the Merkle Tree associated to
        the committed transaction.
    :vartype leafComponents: ~azure.confidentialledgertools.receiptverification.models.LeafComponents
    :ivar nodeId: Hexadecimal string representing the digest of the public key of the
        CCF node that signed the transaction.
    :vartype nodeId: str
    :ivar proof: List of nodes' hashes to be used to re-compute the root of the Merkle Tree,
        together with the leaf node hash, by iteratively concatenating and hashing the given values.
    :vartype proof: list[~azure.confidentialledgertools.receiptverification.models.ProofElement]
    :ivar serviceEndorsements: List of PEM-encoded certificates strings representing
        previous service identities.
    :vartype serviceEndorsements: list[str]
    :ivar signature: Base64 string representing the signature of the root of the Merkle Tree at
        the given transaction.
    :vartype signature: str
    """

    _validation = {
        "cert": {"required": True},
        "leafComponents": {"required": True},
        "nodeId": {"required": True},
        "proof": {"required": True},
        "serviceEndorsements": {"required": False},
        "signature": {"required": True},
    }

    _attribute_map = {
        "cert": {"key": "cert", "type": "str"},
        "leafComponents": {"key": "leafComponents", "type": "LeafComponents"},
        "nodeId": {"key": "nodeId", "type": "str"},
        "proof": {"key": "proof", "type": "[ProofElement]"},
        "serviceEndorsements": {
            "key": "serviceEndorsements",
            "type": "[str]",
        },
        "signature": {"key": "signature", "type": "str"},
    }

    def __init__(  # pylint: disable=dangerous-default-value
        self,
        *,
        cert: str,
        leafComponents: LeafComponents,
        nodeId: str,
        proof: List[ProofElement],
        serviceEndorsements: List[str] = [],
        signature: str,
        **kwargs
    ):
        """
        :keyword cert: PEM-encoded certificate string of the CCF node that signed the transaction.
        :paramtype cert: str
        :keyword leafComponents: Components of the leaf node in the Merkle Tree associated to
            the committed transaction.
        :paramtype leafComponents: ~azure.confidentialledgertools.receiptverification.models.LeafComponents
        :keyword nodeId: Hexadecimal string representing the digest of the public key of the
            CCF node that signed the transaction.
        :paramtype nodeId: str
        :keyword proof: List of nodes' hashes to be used to re-compute the root of the Merkle Tree,
            together with the leaf node hash, by iteratively concatenating and hashing the given values.
        :paramtype proof: list[~azure.confidentialledgertools.receiptverification.models.ProofElement]
        :keyword serviceEndorsements: List of PEM-encoded certificates strings representing
            previous service identities.
        :paramtype serviceEndorsements: list[str]
        :keyword signature: Base64 string representing the signature of the root of the Merkle Tree at
            the given transaction.
        :paramtype signature: str
        """
        super().__init__(**kwargs)
        self.cert = cert
        self.leafComponents = leafComponents
        self.nodeId = nodeId
        self.proof = proof
        self.serviceEndorsements = serviceEndorsements
        self.signature = signature
