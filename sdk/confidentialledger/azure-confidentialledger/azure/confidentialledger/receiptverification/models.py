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
    """LeafComponents represents the object contained in the `leaf_components`
    field of an Azure Confidential Ledger write transaction receipt. The
    `leaf_components` field contains the elements that are hashed to compute
    the leaf node corresponding to the transaction associated to the given
    receipt.

    :ivar claims_digest: Hexadecimal string representing the digest of
        the application claim attached by the Azure Confidential Ledger application.
    :vartype claims_digest: str
    :ivar commit_evidence: A unique string that identifies a transaction / commit,
        derived from the transaction ID and the secrets used by the Azure Confidential Ledger.
    :vartype commit_evidence: str
    :ivar write_set_digest: Hexadecimal string representing the digest of the keys
        and values written during a transaction, that captures the state of the
        ledger at the time the transaction was committed.
    :vartype write_set_digest: str
    """

    _validation = {
        "claims_digest": {"required": True},
        "commit_evidence": {"required": True},
        "write_set_digest": {"required": True},
    }

    _attribute_map = {
        "claims_digest": {"key": "claims_digest", "type": "str"},
        "commit_evidence": {"key": "commit_evidence", "type": "str"},
        "write_set_digest": {"key": "write_set_digest", "type": "str"},
    }

    def __init__(
        self,
        *,
        claims_digest: str,
        commit_evidence: str,
        write_set_digest: str,
        **kwargs
    ):
        """
        :keyword claims_digest: Hexadecimal string representing the digest of
            the application claim attached by the Azure Confidential Ledger application.
        :paramtype claims_digest: str
        :keyword commit_evidence: A unique string that identifies a transaction / commit,
            derived from the transaction ID and the secrets used by the Azure Confidential Ledger.
        :paramtype commit_evidence: str
        :keyword write_set_digest: Hexadecimal string representing the digest of the keys
            and values written during a transaction, that captures the state of the
            ledger at the time the transaction was committed.
        :paramtype write_set_digest: str
        """
        super().__init__(**kwargs)
        self.claims_digest = claims_digest
        self.commit_evidence = commit_evidence
        self.write_set_digest = write_set_digest


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
    :ivar is_signature_transaction: Boolean value representing whether the receipt is
        related to a signature transaction or not.
    :vartype is_signature_transaction: bool
    :ivar leaf_components: Components of the leaf node in the Merkle Tree associated to
        the committed transaction.
    :vartype leaf_components: ~azure.confidentialledgertools.receiptverification.models.LeafComponents
    :ivar node_id: Hexadecimal string representing the digest of the public key of the
        CCF node that signed the transaction.
    :vartype node_id: str
    :ivar proof: List of nodes' hashes to be used to re-compute the root of the Merkle Tree,
        together with the leaf node hash, by iteratively concatenating and hashing the given values.
    :vartype proof: list[~azure.confidentialledgertools.receiptverification.models.ProofElement]
    :ivar service_endorsements: List of PEM-encoded certificates strings representing
        previous service identities.
    :vartype service_endorsements: list[str]
    :ivar signature: Base64 string representing the signature of the root of the Merkle Tree at
        the given transaction.
    :vartype signature: str
    """

    _validation = {
        "cert": {"required": True},
        "is_signature_transaction": {"required": True},
        "leaf_components": {"required": True},
        "node_id": {"required": True},
        "proof": {"required": True},
        "service_endorsements": {"required": True},
        "signature": {"required": True},
    }

    _attribute_map = {
        "cert": {"key": "cert", "type": "str"},
        "is_signature_transaction": {
            "key": "is_signature_transaction",
            "type": "bool",
        },
        "leaf_components": {"key": "leaf_components", "type": "LeafComponents"},
        "node_id": {"key": "node_id", "type": "str"},
        "proof": {"key": "proof", "type": "[ProofElement]"},
        "service_endorsements": {
            "key": "service_endorsements",
            "type": "[str]",
        },
        "signature": {"key": "signature", "type": "str"},
    }

    def __init__(
        self,
        *,
        cert: str,
        is_signature_transaction: bool,
        leaf_components: LeafComponents,
        node_id: str,
        proof: List[ProofElement],
        service_endorsements: List[str],
        signature: str,
        **kwargs
    ):
        """
        :keyword cert: PEM-encoded certificate string of the CCF node that signed the transaction.
        :paramtype cert: str
        :keyword is_signature_transaction: Boolean value representing whether the receipt is
            related to a signature transaction or not.
        :paramtype is_signature_transaction: bool
        :keyword leaf_components: Components of the leaf node in the Merkle Tree associated to
            the committed transaction.
        :paramtype leaf_components: ~azure.confidentialledgertools.receiptverification.models.LeafComponents
        :keyword node_id: Hexadecimal string representing the digest of the public key of the
            CCF node that signed the transaction.
        :paramtype node_id: str
        :keyword proof: List of nodes' hashes to be used to re-compute the root of the Merkle Tree,
            together with the leaf node hash, by iteratively concatenating and hashing the given values.
        :paramtype proof: list[~azure.confidentialledgertools.receiptverification.models.ProofElement]
        :keyword service_endorsements: List of PEM-encoded certificates strings representing
            previous service identities.
        :paramtype service_endorsements: list[str]
        :keyword signature: Base64 string representing the signature of the root of the Merkle Tree at
            the given transaction.
        :paramtype signature: str
        """
        super().__init__(**kwargs)
        self.cert = cert
        self.is_signature_transaction = is_signature_transaction
        self.leaf_components = leaf_components
        self.node_id = node_id
        self.proof = proof
        self.service_endorsements = service_endorsements
        self.signature = signature
