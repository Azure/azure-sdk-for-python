# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Models for receipt verification."""

from typing import Any, Dict, List, Optional, Union


class ProofElement:
    """ProofElement represents the object contained in the `proof` list field
    of an Azure Confidential Ledger write transaction receipt. The `proof` list
    contains the hashes of the nodes in the Merkle Tree and their relative
    position with respect to the parent node (`left` or `right`); the given
    information allow the re-computation of the root node from a given leaf
    node.

    Each ProofElement should contain either the `left` or the `right` field,
    but not both or none of them.
    """

    def __init__(self, left: Optional[str] = None, right: Optional[str] = None):
        """
        :keyword left: Hash of a left node in the Merkle Tree, as an hexadecimal string.
        :paramtype left: Optional[str]

        :keyword right: Hash of a right node in the Merkle Tree, as an hexadecimal string.
        :paramtype right: Optional[str]
        """
        self.left = left
        self.right = right

    def __eq__(self, other):
        if not isinstance(other, ProofElement):
            return False

        return self.left == other.left and self.right == other.right

    @classmethod
    def from_dict(cls, proof_dict: Dict[str, Any]):
        """Create a new instance of this class from a dictionary."""

        return cls(
            proof_dict.get("left", None),
            proof_dict.get("right", None),
        )


class LeafComponents:
    """LeafComponents represents the object contained in the `leafComponents`
    field of an Azure Confidential Ledger write transaction receipt. The
    `leafComponents` field contains the elements that are hashed to compute
    the leaf node corresponding to the transaction associated to the given
    receipt.
    """

    def __init__(self, claimsDigest: str, commitEvidence: str, writeSetDigest: str):
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
        self.claimsDigest = claimsDigest
        self.commitEvidence = commitEvidence
        self.writeSetDigest = writeSetDigest

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, LeafComponents):
            return NotImplemented
        return (
            self.claimsDigest == other.claimsDigest
            and self.commitEvidence == other.commitEvidence
            and self.writeSetDigest == other.writeSetDigest
        )

    @classmethod
    def from_dict(cls, leaf_components_dict: Dict[str, Any]):
        """Create a new instance of this class from a dictionary."""

        return cls(
            leaf_components_dict["claimsDigest"],
            leaf_components_dict["commitEvidence"],
            leaf_components_dict["writeSetDigest"],
        )


class Receipt:
    """Receipt represents the object contained in the `receipt` field of an
    Azure Confidential Ledger `get_receipt` response. A
    receipt is a cryptographic proof that a transaction has been committed to
    the ledger: it can be used to verify that the ledger entry associated to a
    transaction has been appended to the ledger (thus, it can be used to
    validate properties such as non-repudiation, integrity, and tamper-
    proofing). A receipt contains all the information needed to verify
    transaction inclusion and the verification can be done by applying an ad-
    hoc algorithm.
    """

    def __init__(  # pylint: disable=dangerous-default-value
        self,
        cert: str,
        leafComponents: Union[Dict[str, Any], LeafComponents],
        proof: List[Union[Dict[str, Any], ProofElement]],
        signature: str,
        nodeId: Optional[str] = None,
        serviceEndorsements: Optional[List[str]] = [],
    ):
        """
        :keyword cert: PEM-encoded certificate string of the CCF node that signed the transaction.
        :paramtype cert: str

        :keyword leafComponents: Components of the leaf node in the Merkle Tree associated to
            the committed transaction.
        :paramtype leafComponents: Dict[str, Any]

        :keyword proof: List of nodes' hashes to be used to re-compute the root of the Merkle Tree,
            together with the leaf node hash, by iteratively concatenating and hashing the given values.
        :paramtype proof: List[Dict[str, Any]]

        :keyword signature: Base64 string representing the signature of the root of the Merkle Tree at
            the given transaction.
        :paramtype signature: str

        :keyword nodeId: Hexadecimal string representing the digest of the public key of the
            CCF node that signed the transaction.
        :paramtype nodeId: Optional[str]

        :keyword serviceEndorsements: List of PEM-encoded certificates strings representing
            previous service identities.
        :paramtype serviceEndorsements: Optional[List[str]]
        """
        self.cert = cert
        self.nodeId = nodeId
        self.serviceEndorsements = serviceEndorsements
        self.signature = signature

        if isinstance(leafComponents, LeafComponents):
            self.leafComponents = leafComponents
        else:
            self.leafComponents = LeafComponents.from_dict(leafComponents)

        self.proof = [
            elem if isinstance(elem, ProofElement) else ProofElement.from_dict(elem)
            for elem in proof
        ]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Receipt):
            return NotImplemented

        # print(self.cert == other.cert)
        # print( self.nodeId == other.nodeId)
        # print( self.serviceEndorsements == other.serviceEndorsements)
        # print( self.signature == other.signature)
        # print(self.leafComponents == other.leafComponents)

        # for elem_self, elem_other in zip(self.proof, other.proof):
        #     print(elem_self.left, elem_self.right)
        #     print(elem_other.left, elem_other.right)

        return (
            self.cert == other.cert
            and self.nodeId == other.nodeId
            and self.serviceEndorsements == other.serviceEndorsements
            and self.signature == other.signature
            and self.leafComponents == other.leafComponents
            and all(
                elem_self == elem_other
                for elem_self, elem_other in zip(self.proof, other.proof)
            )
        )

    @classmethod
    def from_dict(cls, receipt_dict: Dict[str, Any]):
        """Create a new instance of this class from a dictionary."""

        return cls(
            cert=receipt_dict["cert"],
            leafComponents=receipt_dict["leafComponents"],
            proof=receipt_dict["proof"],
            signature=receipt_dict["signature"],
            nodeId=receipt_dict.get("nodeId", None),
            serviceEndorsements=receipt_dict.get("serviceEndorsements", []),
        )
