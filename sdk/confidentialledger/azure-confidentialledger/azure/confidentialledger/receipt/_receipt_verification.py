# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Algorithm implementation for verifying Azure Confidential Ledger write
transaction receipts."""

from base64 import b64decode
from hashlib import sha256
from typing import Dict, List, Any, cast, Optional

from cryptography.x509 import load_pem_x509_certificate, Certificate
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from azure.confidentialledger.receipt._receipt_models import (
    LeafComponents,
    ProofElement,
    Receipt,
)

from azure.confidentialledger.receipt._utils import (
    _convert_dict_to_camel_case,
)

from azure.confidentialledger.receipt._claims_digest_computation import (
    compute_claims_digest,
)


def verify_receipt(
    receipt: Dict[str, Any],
    service_cert: str,
    *,
    application_claims: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """Verify that a given Azure Confidential Ledger write transaction receipt
    is valid from its content and the Confidential Ledger service identity
    certificate.

    :param receipt: Receipt dictionary containing the content of an Azure
     Confidential Ledger write transaction receipt.
    :type receipt: Dict[str, Any]

    :param service_cert: String containing the PEM-encoded
     certificate of the Confidential Ledger service identity.
    :type service_cert: str

    :keyword application_claims: List of application claims to be verified against the receipt.
    :paramtype application_claims: Optional[List[Dict[str, Any]]]

    :raises ValueError: If the receipt verification has failed.
    """

    # Validate receipt content and convert it into a Receipt model
    receipt_obj = _preprocess_input_receipt(receipt)

    # Validate application claims provided by the user, if any
    if application_claims:
        computed_claims_digest = compute_claims_digest(application_claims)
        if computed_claims_digest != receipt_obj.leafComponents.claimsDigest:
            raise ValueError(
                "The computed claims digest from application claims does not match the receipt claims digest."
            )

    # Load node PEM certificate
    node_cert = _load_and_verify_pem_certificate(receipt_obj.cert)

    # Verify node certificate is endorsed by the service certificate
    # through endorsements certificates
    _verify_node_cert_endorsed_by_service_cert(
        node_cert, service_cert, receipt_obj.serviceEndorsements
    )

    # Compute hash of the leaf node in the Merkle Tree corresponding
    # to the transaction associated to the given receipt
    leaf_node_hash = _compute_leaf_node_hash(receipt_obj.leafComponents)

    # Compute root of the Merkle Tree at the time the transaction was committed
    root_node_hash = _compute_root_node_hash(leaf_node_hash, receipt_obj.proof)

    # Verify signature of the signing node over the root of the tree with
    # node certificate public key
    _verify_signature_over_root_node_hash(
        receipt_obj.signature, node_cert, receipt_obj.nodeId, root_node_hash
    )


def _preprocess_input_receipt(receipt_dict: Dict[str, Any]) -> Receipt:
    """Preprocess input receipt dictionary, validate its content, and returns a
    valid Receipt object based on the vetted input data."""

    # Convert any key in the receipt dictionary to camel case
    # to match the model fields (we do this because customers may
    # provide receipts with snake case keys since they were returned
    # by older ACL instances)
    receipt_dict = _convert_dict_to_camel_case(receipt_dict)

    _validate_receipt_content(receipt_dict)

    # Convert receipt JSON object to Receipt model
    return Receipt.from_dict(receipt_dict)


def _validate_receipt_content(receipt: Dict[str, Any]):
    """Validate the content of a write transaction receipt."""

    try:
        assert "cert" in receipt
        assert isinstance(receipt["cert"], str)

        assert "leafComponents" in receipt
        assert isinstance(receipt["leafComponents"], dict)

        assert "claimsDigest" in receipt["leafComponents"]
        assert isinstance(receipt["leafComponents"]["claimsDigest"], str)

        assert "commitEvidence" in receipt["leafComponents"]
        assert isinstance(receipt["leafComponents"]["commitEvidence"], str)

        assert "writeSetDigest" in receipt["leafComponents"]
        assert isinstance(receipt["leafComponents"]["writeSetDigest"], str)

        assert "proof" in receipt
        assert isinstance(receipt["proof"], list)

        # Validate elements in proof
        for elem in receipt["proof"]:
            assert "left" in elem or "right" in elem
            if "left" in elem:
                assert isinstance(elem["left"], str)
            if "right" in elem:
                assert isinstance(elem["right"], str)

        assert "signature" in receipt
        assert isinstance(receipt["signature"], str)

        # Validate nodeId, if present
        if "nodeId" in receipt:
            assert isinstance(receipt["nodeId"], str)

        # Validate serviceEndorsements, if present
        if "serviceEndorsements" in receipt:
            assert isinstance(receipt["serviceEndorsements"], list)

            # Validate elements in serviceEndorsements
            for elem in receipt["serviceEndorsements"]:
                assert isinstance(elem, str)

    except Exception as exception:
        raise ValueError("The receipt content is invalid.") from exception


def _verify_signature_over_root_node_hash(
    signature: str, node_cert: Certificate, node_id: str, root_node_hash: bytes
) -> None:
    """Verify signature over root node hash of the Merkle Tree using node
    certificate public key."""

    try:
        # Verify public key contained in the node certificate is equal to the node_id
        public_key_bytes = node_cert.public_key().public_bytes(
            Encoding.DER, PublicFormat.SubjectPublicKeyInfo
        )

        if node_id is not None:
            assert sha256(public_key_bytes).digest() == bytes.fromhex(node_id)

        # Verify signature over root node hash using node certificate public key
        _verify_ec_signature(
            node_cert,
            b64decode(signature, validate=True),
            root_node_hash,
            hashes.SHA256(),
        )

    except Exception as exception:
        raise ValueError(
            f"Encountered exception when verifying signature {signature} over root node hash."
        ) from exception


def _compute_leaf_node_hash(leaf_components: LeafComponents) -> bytes:
    """Compute the hash of the leaf node associated to a transaction given the
    leaf components from a write transaction receipt."""

    try:
        # Digest commit evidence string
        commit_evidence_digest = sha256(
            leaf_components.commitEvidence.encode()
        ).digest()

        # Convert write set digest to bytes
        write_set_digest = bytes.fromhex(leaf_components.writeSetDigest)

        # Convert claims digest to bytes
        claims_digest = bytes.fromhex(leaf_components.claimsDigest)

        # Create leaf node hash by hashing the concatenation of its three components
        # as bytes objects in the following order:
        # 1. write_set_digest
        # 2. commit_evidence_digest
        # 3. claims_digest
        return sha256(
            write_set_digest + commit_evidence_digest + claims_digest
        ).digest()

    except Exception as exception:
        raise ValueError(
            f"Encountered exception when computing leaf node hash from leaf components {leaf_components}."
        ) from exception


def _compute_root_node_hash(leaf_hash: bytes, proof: List[ProofElement]) -> bytes:
    """Re-compute the hash of the root of the Merkle tree from a leaf node hash
    and a receipt proof list containing the required nodes hashes for the
    computation."""

    try:
        # Initialize current hash to leaf hash
        current_node_hash = leaf_hash

        # Iterate through all the elements in proof list
        for element in proof:
            # Check that the current element only contains either one left or right node hash
            if (
                element is None
                or (element.left is None and element.right is None)
                or (element.left is not None and element.right is not None)
            ):
                raise ValueError(
                    "Invalid proof element in receipt: element must contain either one left or right node hash."
                )

            parent_node_hash = bytes()

            # If the current element contains a left hash, concatenate the left hash and the current node hash
            if element.left is not None:
                parent_node_hash = bytes.fromhex(element.left) + current_node_hash

            # If the current element contains a right hash, concatenate the current node hash and the right hash
            if element.right is not None:
                parent_node_hash = current_node_hash + bytes.fromhex(element.right)

            # Hash the parent node hash
            current_node_hash = sha256(parent_node_hash).digest()

        return current_node_hash

    except Exception as exception:
        raise ValueError(
            f"Encountered exception when computing root node hash from proof list {proof}."
        ) from exception


def _verify_certificate_endorsement(
    endorsee: Certificate, endorser: Certificate
) -> None:
    """Verify that the endorser certificate has endorsed endorsee
    certificate using ECDSA."""

    try:
        # Extract TBS certificate hash from endorsee certificate
        hash_algorithm = cast(hashes.HashAlgorithm, endorsee.signature_hash_algorithm)
        digester = hashes.Hash(hash_algorithm)
        digester.update(endorsee.tbs_certificate_bytes)
        cert_digest = digester.finalize()

        # Verify endorser signature over endorsee certificate digest
        _verify_ec_signature(endorser, endorsee.signature, cert_digest, hash_algorithm)

    except Exception as exception:
        raise ValueError(
            f"Encountered exception when verifying endorsement of certificate {endorsee} by certificate {endorser}."
        ) from exception


def _verify_ec_signature(
    certificate: Certificate,
    signature: bytes,
    data: bytes,
    hash_algorithm: hashes.HashAlgorithm,
) -> None:
    """Verify a signature over data using the certificate public key."""

    public_key = cast(ec.EllipticCurvePublicKey, certificate.public_key())

    public_key.verify(
        signature,
        data,
        ec.ECDSA(utils.Prehashed(hash_algorithm)),
    )


def _verify_node_cert_endorsed_by_service_cert(
    node_cert: Certificate, service_cert_str: str, endorsements_certs: List[str]
) -> None:
    """Check a node certificate is endorsed by a service certificate.

    If a list of endorsements certificates is not empty, check that the
    node certificate is transitively endorsed by the service certificate
    through the endorsement certificates in the list.
    """

    current_cert = node_cert

    # Validate endorsement certificates list is present
    if endorsements_certs is None:
        endorsements_certs = []

    # Add service certificate to the list of endorsements certificates
    endorsements_certs.append(service_cert_str)

    # Iterate through all the endorsements certificates
    for endorsement in endorsements_certs:
        # Load endorsement PEM certificate
        endorsement_cert = _load_and_verify_pem_certificate(endorsement)

        # Verify endorsement certificate has endorsed current certificate
        _verify_certificate_endorsement(current_cert, endorsement_cert)

        # Set current certificate to endorsement certificate to continue the chain verification
        current_cert = endorsement_cert


def _load_and_verify_pem_certificate(cert_str: str) -> Certificate:
    """Load PEM certificate from a string representation and verify it is a
    valid certificate with expected Elliptic Curve public key."""

    try:
        # Load certificate from string
        cert = load_pem_x509_certificate(cert_str.encode())

        # Verify public key is of the correct type
        assert isinstance(cert.public_key(), ec.EllipticCurvePublicKey)

        return cert

    except Exception as exception:
        raise ValueError(f"PEM certificate {cert_str} is not valid.") from exception
