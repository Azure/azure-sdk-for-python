# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:ignore PHDR, tstr
"""Algorithm implementation for verifying CCF SCITT receipts."""

from base64 import urlsafe_b64decode
from dataclasses import dataclass
from hashlib import sha256, sha384, sha512
from typing import Dict, List, Any, Optional

from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm

from azure.codetransparency.cbor import CBOREncoder, CBORDecoder

# COSE header labels
COSE_HEADER_ALG = 1
COSE_HEADER_KID = 4
COSE_HEADER_CWT_MAP = 15  # CWT Claims map (RFC9597)
COSE_PHDR_VDS = 395  # Verifiable Data Structure
COSE_PHDR_VDP = 396  # Verifiable Data Proof

# CWT Claims
CWT_ISS_LABEL = 1  # Issuer claim

# CCF Tree Algorithm
CCF_TREE_ALG_LABEL = 2

# Inclusion proof labels
COSE_RECEIPT_INCLUSION_PROOF_LABEL = -1
CCF_PROOF_LEAF_LABEL = 1
CCF_PROOF_PATH_LABEL = 2


@dataclass
class _ProofElement:
    """Representation of a tree node (left or right) in the ledger and its digest."""

    left: bool
    digest: bytes


@dataclass
class _Leaf:
    """Representation of the leaf structure in the ledger."""

    internal_transaction_digest: bytes
    internal_evidence: str
    data_digest: bytes


def _combine_byte_arrays(*arrays: bytes) -> bytes:
    """Merge multiple byte arrays into a single byte array.

    :param arrays: Variable number of byte arrays to combine.
    :type arrays: bytes
    :return: The concatenated byte array.
    :rtype: bytes
    """
    return b"".join(arrays)


def _base64url_decode(data: str) -> bytes:
    """Decode base64url encoded string with padding.

    :param data: The base64url encoded string.
    :type data: str
    :return: The decoded bytes.
    :rtype: bytes
    """
    # Add padding if needed
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return urlsafe_b64decode(data)


def get_receipt_issuer_host(receipt_bytes: bytes) -> Optional[str]:
    """Extract the issuer host from a receipt.

    :param receipt_bytes: The COSE_Sign1 bytes of the receipt.
    :type receipt_bytes: bytes
    :return: The issuer host string if found, or None if not present.
    :rtype: Optional[str]
    """
    cose_sign1 = CBORDecoder(receipt_bytes).decode_cose_sign1()
    protected_headers = cose_sign1.get("protected_headers", {})

    cwt_map = protected_headers.get(COSE_HEADER_CWT_MAP)
    if cwt_map is None:
        return None

    # cwt_map may be bytes or already decoded
    if isinstance(cwt_map, bytes):
        decoder = CBORDecoder(cwt_map)
        try:
            cwt_map = decoder.decode()
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    if not isinstance(cwt_map, dict):
        return None

    issuer = cwt_map.get(CWT_ISS_LABEL)
    if issuer is None or not isinstance(issuer, str) or not issuer:
        return None

    return issuer


def get_receipt_kid(receipt_bytes: bytes) -> Optional[str]:
    """Extract the key ID (KID) from a receipt's protected headers.

    :param receipt_bytes: The COSE_Sign1 bytes of the receipt.
    :type receipt_bytes: bytes
    :return: The key ID as a string if found, or None if not present.
    :rtype: Optional[str]
    """
    receipt = CBORDecoder(receipt_bytes).decode_cose_sign1()
    protected_headers = receipt.get("protected_headers", {})
    kid = protected_headers.get(COSE_HEADER_KID)
    if kid is None:
        return None
    if isinstance(kid, bytes):
        return kid.decode("utf-8")
    return str(kid)


def _get_leaf(leaf_bytes: bytes) -> _Leaf:
    """Deserialize the leaf content from CBOR bytes.

    The CCF leaf structure is defined as::

        ccf-leaf = [
            internal-transaction-digest: bstr.size 32
            internal-evidence: tstr.size(1..1024)
            data-digest: bstr.size 32
        ]

    :param leaf_bytes: The CBOR-encoded leaf bytes.
    :type leaf_bytes: bytes
    :return: The deserialized leaf structure.
    :rtype: _Leaf
    :raises ValueError: If the leaf structure is invalid.
    """
    decoder = CBORDecoder(leaf_bytes)
    leaf_array = decoder.decode()

    if not isinstance(leaf_array, list) or len(leaf_array) != 3:
        raise ValueError("Invalid leaf structure: expected array of 3 elements.")

    return _Leaf(
        internal_transaction_digest=leaf_array[0],
        internal_evidence=leaf_array[1],
        data_digest=leaf_array[2],
    )


def _get_proof_elements(proof_paths_bytes: bytes) -> List[_ProofElement]:
    """Deserialize a list of ProofElements from the inclusion proof path CBOR bytes.

    The CCF proof element structure is defined as::

        ccf-proof-element = [
            left: bool
            digest: bstr.size 32
        ]

    :param proof_paths_bytes: The CBOR-encoded proof paths bytes.
    :type proof_paths_bytes: bytes
    :return: A list of proof elements.
    :rtype: List[_ProofElement]
    :raises ValueError: If the proof paths structure is invalid.
    """
    decoder = CBORDecoder(proof_paths_bytes)
    proof_paths = decoder.decode()

    if not isinstance(proof_paths, list):
        raise ValueError("Invalid proof paths: expected array.")

    proof_elements: List[_ProofElement] = []
    for element in proof_paths:
        if not isinstance(element, list) or len(element) != 2:
            raise ValueError("Invalid proof element: expected array of 2 elements.")
        proof_elements.append(_ProofElement(left=element[0], digest=element[1]))

    return proof_elements


def _get_expected_algorithm(crv: str) -> int:
    """Get the expected COSE algorithm value for a given curve.

    :param crv: The curve name (P-256, P-384, or P-521).
    :type crv: str
    :return: The COSE algorithm value (-7 for ES256, -35 for ES384, -36 for ES512).
    :rtype: int
    :raises ValueError: If the curve is not supported.
    """
    # COSE algorithm values from https://www.iana.org/assignments/cose/cose.xhtml#algorithms
    curve_to_algorithm = {
        "P-256": -7,  # ES256
        "P-384": -35,  # ES384
        "P-521": -36,  # ES512
    }

    try:
        return curve_to_algorithm[crv]
    except KeyError as exc:
        raise ValueError(f"Unsupported curve: {crv}") from exc


def _encode_cose_sign1_to_be_signed(
    protected_headers_bytes: bytes,
    payload: bytes,
) -> bytes:
    """Create the Sig_structure for COSE_Sign1 verification.

    The Sig_structure is defined as::

        Sig_structure = [
            context : "Signature1",
            body_protected : protected_headers_bytes,
            external_aad : bstr (empty),
            payload : bstr
        ]

    :param protected_headers_bytes: The protected headers as encoded bytes.
    :type protected_headers_bytes: bytes
    :param payload: The payload bytes.
    :type payload: bytes
    :return: The CBOR-encoded Sig_structure.
    :rtype: bytes
    """
    # Sig_structure is a 4-element array:
    # ["Signature1", protected_headers_bytes, b"", payload]
    sig_structure = [
        "Signature1",
        protected_headers_bytes,
        b"",  # external_aad (empty)
        payload,
    ]
    return CBOREncoder.encode_value(sig_structure)


def _get_protected_headers_bytes_from_cose(data: bytes) -> bytes:
    """Extract the raw protected headers bytes from a COSE_Sign1 message.

    :param data: The COSE_Sign1 bytes.
    :type data: bytes
    :return: The raw protected headers bytes.
    :rtype: bytes
    :raises ValueError: If the COSE_Sign1 structure is invalid.
    """
    decoder = CBORDecoder(data)
    cose_structure = decoder.decode()

    # Handle COSE_Sign1 structure (tag 18)
    if isinstance(cose_structure, dict) and cose_structure.get("tag") == 18:
        cose_structure = cose_structure["value"]

    if not isinstance(cose_structure, list) or len(cose_structure) != 4:
        raise ValueError("Invalid COSE_Sign1 structure")

    return cose_structure[0]  # protected headers bytes


def _trim_unprotected_headers(
    signed_statement_bytes: bytes,
) -> bytes:
    """Prepare the signed statement for verification by clearing unprotected headers.

    :param signed_statement_bytes: The signed statement COSE_Sign1 bytes.
    :type signed_statement_bytes: bytes
    :return: The encoded signed statement with cleared unprotected headers.
    :rtype: bytes
    """
    cose_sign1 = CBORDecoder(signed_statement_bytes).decode_cose_sign1()
    return CBOREncoder().encode_cose_sign1(
        protected_headers=cose_sign1.get("protected_headers", {}),
        unprotected_headers={},
        payload=cose_sign1.get("payload", b""),
        signature=cose_sign1.get("signature", b""),
        include_tag=cose_sign1.get("was_tagged", True),
    )


def verify_receipt(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    jwk: Dict[str, Any],
    receipt_bytes: bytes,
    signed_statement_bytes: bytes,
    trim_unprotected_headers: bool = True,
) -> None:
    """Verify a CCF SCITT receipt.

    :param jwk: The service certificate key (JWK).
    :type jwk: Dict[str, Any]
    :param receipt_bytes: Receipt in COSE_Sign1 CBOR bytes.
    :type receipt_bytes: bytes
    :param signed_statement_bytes: The input signed statement in COSE_Sign1 CBOR bytes.
    :type signed_statement_bytes: bytes
    :param trim_unprotected_headers: Whether to clear unprotected headers before
        computing the digest. Defaults to True.
    :type trim_unprotected_headers: bool
    :raises ValueError: If the verification fails.
    """
    # Compute the digest of the signed statement
    if trim_unprotected_headers:
        cleaned_claim = _trim_unprotected_headers(signed_statement_bytes)
        claims_digest = sha256(cleaned_claim).digest()
    else:
        claims_digest = sha256(signed_statement_bytes).digest()

    # Extract expected KID from the JWK
    expected_kid = jwk.get("kid", "").encode("utf-8")

    # Decode the receipt
    receipt = CBORDecoder(receipt_bytes).decode_cose_sign1()
    protected_headers = receipt.get("protected_headers", {})
    unprotected_headers = receipt.get("unprotected_headers", {})
    signature = receipt.get("signature", b"")

    # Verify algorithm
    alg = protected_headers.get(COSE_HEADER_ALG)
    if alg is None:
        raise ValueError("Algorithm not found in receipt protected headers.")

    crv = jwk.get("crv")
    if crv is None:
        raise ValueError("Curve not found in JWK.")
    expected_alg = _get_expected_algorithm(crv)
    if alg != expected_alg:
        raise ValueError(f"Algorithm mismatch. Expected {expected_alg}, found {alg}.")

    # Verify KID
    kid = protected_headers.get(COSE_HEADER_KID)
    if kid is None:
        raise ValueError("KID not found in receipt protected headers.")
    if isinstance(kid, bytes):
        kid_bytes = kid
    else:
        kid_bytes = kid.encode("utf-8") if isinstance(kid, str) else bytes(kid)

    if kid_bytes != expected_kid:
        raise ValueError("KID mismatch.")

    # Verify VDS (Verifiable Data Structure)
    vds = protected_headers.get(COSE_PHDR_VDS)
    if vds is None:
        raise ValueError("Verifiable Data Structure is required.")
    if vds != CCF_TREE_ALG_LABEL:
        raise ValueError("Verifiable Data Structure is not CCF.")

    # Get VDP (Verifiable Data Proof)
    vdp = unprotected_headers.get(COSE_PHDR_VDP)
    if vdp is None:
        raise ValueError(f"Verifiable data proof {COSE_PHDR_VDP} is required.")

    # Decode VDP if it's bytes
    if isinstance(vdp, bytes):
        decoder = CBORDecoder(vdp)
        vdp = decoder.decode()

    if not isinstance(vdp, dict):
        raise ValueError("Invalid verifiable data proof format.")

    # Get inclusion proofs
    inclusion_proofs_data = vdp.get(COSE_RECEIPT_INCLUSION_PROOF_LABEL)
    if inclusion_proofs_data is None:
        raise ValueError("Inclusion proof is required.")

    # Decode inclusion proofs if bytes
    if isinstance(inclusion_proofs_data, bytes):
        decoder = CBORDecoder(inclusion_proofs_data)
        inclusion_proofs_data = decoder.decode()

    if not isinstance(inclusion_proofs_data, list) or len(inclusion_proofs_data) == 0:
        raise ValueError("At least one inclusion proof is required.")

    alg = protected_headers.get(COSE_HEADER_ALG)
    if alg == -7:  # ES256
        sig_alg = SignatureAlgorithm.es256
        hash_alg = sha256
    elif alg == -35:  # ES384
        sig_alg = SignatureAlgorithm.es384
        hash_alg = sha384
    elif alg == -36:  # ES512
        sig_alg = SignatureAlgorithm.es512
        hash_alg = sha512
    else:
        raise ValueError(f"Unsupported algorithm for signature verification: {alg}")

    # update JWK to match azure keyvault expectations
    # Decode x and y from base64url if they are strings
    if "x" in jwk and isinstance(jwk["x"], str):
        jwk["x"] = _base64url_decode(jwk["x"])
    if "y" in jwk and isinstance(jwk["y"], str):
        jwk["y"] = _base64url_decode(jwk["y"])
    jwk["key_ops"] = ["verify"]
    crypto_client = CryptographyClient.from_jwk(jwk)

    # Get the protected headers bytes for signature verification
    protected_headers_bytes = _get_protected_headers_bytes_from_cose(receipt_bytes)

    # Verify each inclusion proof
    for inclusion_proof_bytes in inclusion_proofs_data:
        # Decode inclusion proof if bytes
        if isinstance(inclusion_proof_bytes, bytes):
            decoder = CBORDecoder(inclusion_proof_bytes)
            inclusion_proof = decoder.decode()
        else:
            inclusion_proof = inclusion_proof_bytes

        if not isinstance(inclusion_proof, dict):
            raise ValueError("Invalid inclusion proof format.")

        # Get leaf
        leaf_data = inclusion_proof.get(CCF_PROOF_LEAF_LABEL)
        if leaf_data is None:
            raise ValueError("Leaf must be present in inclusion proof.")

        # Decode leaf if bytes
        if isinstance(leaf_data, bytes):
            leaf = _get_leaf(leaf_data)
        elif isinstance(leaf_data, list):
            leaf = _Leaf(
                internal_transaction_digest=leaf_data[0],
                internal_evidence=leaf_data[1],
                data_digest=leaf_data[2],
            )
        else:
            raise ValueError("Invalid leaf format.")

        # Get proof path
        proof_paths_data = inclusion_proof.get(CCF_PROOF_PATH_LABEL)
        if proof_paths_data is None:
            raise ValueError("Path must be present in inclusion proof.")

        # Decode proof paths if bytes
        if isinstance(proof_paths_data, bytes):
            proof_elements = _get_proof_elements(proof_paths_data)
        elif isinstance(proof_paths_data, list):
            proof_elements = [
                _ProofElement(left=elem[0], digest=elem[1]) for elem in proof_paths_data
            ]
        else:
            raise ValueError("Invalid proof paths format.")

        # Compute accumulator (root digest)
        accumulator = sha256(
            _combine_byte_arrays(
                leaf.internal_transaction_digest,
                sha256(leaf.internal_evidence.encode("utf-8")).digest(),
                leaf.data_digest,
            )
        ).digest()

        for proof_element in proof_elements:
            if proof_element.left:
                accumulator = sha256(
                    _combine_byte_arrays(proof_element.digest, accumulator)
                ).digest()
            else:
                accumulator = sha256(
                    _combine_byte_arrays(accumulator, proof_element.digest)
                ).digest()

        to_be_signed = _encode_cose_sign1_to_be_signed(
            protected_headers_bytes,
            accumulator,
        )

        # Verify signature
        try:
            verification_result = crypto_client.verify(
                sig_alg, hash_alg(to_be_signed).digest(), signature
            )
            if not verification_result.is_valid:
                raise ValueError("Invalid signature.")
        except Exception as exc:
            raise ValueError("Signature verification failed.") from exc

        # Verify claims digest matches leaf data digest
        if claims_digest != leaf.data_digest:
            raise ValueError(
                f"Statement digest does not match the leaf digest in the receipt: {claims_digest.hex()} != {leaf.data_digest.hex()}"
            )
