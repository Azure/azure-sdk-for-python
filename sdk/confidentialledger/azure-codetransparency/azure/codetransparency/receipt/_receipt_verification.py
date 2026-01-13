# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Algorithm implementation for verifying CCF SCITT receipts."""

from base64 import urlsafe_b64decode
from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256, sha384, sha512
from typing import Dict, List, Any, Optional, Tuple

from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm

from azure.codetransparency.cbor._decoder import CBORDecoder


# COSE header labels
COSE_HEADER_ALG = 1
COSE_HEADER_KID = 4
COSE_HEADER_CWT_MAP = 15  # CWT Claims map (RFC9597)
COSE_HEADER_EMBEDDED_RECEIPTS = 394
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

# Prefix for unknown issuers
UNKNOWN_ISSUER_PREFIX = "__unknown-issuer::"


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
    """Merge multiple byte arrays."""
    return b"".join(arrays)


def _decode_cose_sign1(data: bytes) -> Dict[str, Any]:
    """Decode a COSE_Sign1 structure using CBORDecoder."""
    decoder = CBORDecoder(data)
    return decoder.decode_cose_sign1()


def _get_receipts_from_transparent_statement(
    transparent_statement_bytes: bytes,
) -> List[Tuple[str, bytes]]:
    """Extract receipts from a transparent statement COSE_Sign1 envelope.

    :param transparent_statement_bytes: The COSE_Sign1 bytes containing the transparent statement.
    :return: A list of tuples containing (issuer_host, receipt_bytes).
    :raises ValueError: If embedded receipts are not found.
    """
    cose_sign1 = _decode_cose_sign1(transparent_statement_bytes)
    unprotected_headers = cose_sign1.get("unprotected_headers", {})

    embedded_receipts = unprotected_headers.get(COSE_HEADER_EMBEDDED_RECEIPTS)
    if embedded_receipts is None:
        raise ValueError("Embedded receipts not found in transparent statement.")

    # If the embedded receipts value is bytes, decode it as CBOR
    if isinstance(embedded_receipts, bytes):
        decoder = CBORDecoder(embedded_receipts)
        embedded_receipts = decoder.decode()

    if not isinstance(embedded_receipts, list):
        raise ValueError("Embedded receipts must be a CBOR array.")

    receipt_list: List[Tuple[str, bytes]] = []
    for idx, receipt in enumerate(embedded_receipts):
        if not isinstance(receipt, bytes):
            raise ValueError(f"Receipt at index {idx} must be a byte string.")

        try:
            issuer = _get_receipt_issuer_host(receipt)
        except ValueError:
            # Receipt could be from any other system, identify with unknown issuer prefix
            issuer = f"{UNKNOWN_ISSUER_PREFIX}{idx}"

        receipt_list.append((issuer, receipt))

    return receipt_list


def _get_receipt_issuer_host(receipt_bytes: bytes) -> str:
    """Extract the issuer host from a receipt.

    :param receipt_bytes: The COSE_Sign1 bytes of the receipt.
    :return: The issuer host string.
    :raises ValueError: If the issuer cannot be found.
    """
    cose_sign1 = _decode_cose_sign1(receipt_bytes)
    protected_headers = cose_sign1.get("protected_headers", {})

    cwt_map = protected_headers.get(COSE_HEADER_CWT_MAP)
    if cwt_map is None:
        raise ValueError("CWT Claims map not found in receipt.")

    # cwt_map may be bytes or already decoded
    if isinstance(cwt_map, bytes):
        decoder = CBORDecoder(cwt_map)
        cwt_map = decoder.decode()

    if not isinstance(cwt_map, dict):
        raise ValueError("CWT Claims map is not a valid map.")

    issuer = cwt_map.get(CWT_ISS_LABEL)
    if issuer is None or not isinstance(issuer, str) or not issuer:
        raise ValueError("Issuer not found in receipt.")

    return issuer


def _get_leaf(leaf_bytes: bytes) -> _Leaf:
    """Deserialize the leaf content from CBOR bytes.

    ccf-leaf = [
      internal-transaction-digest: bstr.size 32
      internal-evidence: tstr.size(1..1024)
      data-digest: bstr.size 32
    ]
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

    ccf-proof-element = [
        left: bool
        digest: bstr.size 32
    ]
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

    :param crv: The curve name (P-256, P-384, P-521).
    :return: The COSE algorithm value.
    :raises ValueError: If the curve is not supported.
    """
    # COSE algorithm values from https://www.iana.org/assignments/cose/cose.xhtml#algorithms
    if crv == "P-256":
        return -7  # ES256
    elif crv == "P-384":
        return -35  # ES384
    elif crv == "P-521":
        return -36  # ES512
    else:
        raise ValueError(f"Unsupported curve: {crv}")


def _encode_cose_sign1_to_be_signed(
    protected_headers_bytes: bytes,
    payload: bytes,
) -> bytes:
    """Create the Sig_structure for COSE_Sign1 verification.

    Sig_structure = [
        context : "Signature1",
        body_protected : protected_headers_bytes,
        external_aad : bstr (empty),
        payload : bstr
    ]

    :param protected_headers_bytes: The protected headers as encoded bytes.
    :param payload: The payload bytes.
    :return: The CBOR-encoded Sig_structure.
    """
    # Manual CBOR encoding for Sig_structure array
    # This is a 4-element array
    result = bytearray()

    # CBOR array header for 4 elements
    result.append(0x84)  # array(4)

    # context: "Signature1"
    context = b"Signature1"
    result.append(0x6A)  # text(10)
    result.extend(context)

    # body_protected: bstr
    if len(protected_headers_bytes) < 24:
        result.append(0x40 | len(protected_headers_bytes))
    elif len(protected_headers_bytes) < 256:
        result.append(0x58)
        result.append(len(protected_headers_bytes))
    else:
        result.append(0x59)
        result.extend(len(protected_headers_bytes).to_bytes(2, "big"))
    result.extend(protected_headers_bytes)

    # external_aad: empty bstr
    result.append(0x40)  # bstr(0)

    # payload: bstr
    if len(payload) < 24:
        result.append(0x40 | len(payload))
    elif len(payload) < 256:
        result.append(0x58)
        result.append(len(payload))
    elif len(payload) < 65536:
        result.append(0x59)
        result.extend(len(payload).to_bytes(2, "big"))
    else:
        result.append(0x5A)
        result.extend(len(payload).to_bytes(4, "big"))
    result.extend(payload)

    return bytes(result)


def _encode_cose_sign1_message(
    cose_sign1: Dict[str, Any], clear_unprotected: bool = False
) -> bytes:
    """Re-encode a COSE_Sign1 message to bytes.

    :param cose_sign1: The decoded COSE_Sign1 structure.
    :param clear_unprotected: If True, clear the unprotected headers.
    :return: The CBOR-encoded COSE_Sign1 message (without tag).
    """
    protected_headers = cose_sign1.get("protected_headers", {})
    unprotected_headers = (
        {} if clear_unprotected else cose_sign1.get("unprotected_headers", {})
    )
    payload = cose_sign1.get("payload", b"")
    signature = cose_sign1.get("signature", b"")

    # Encode protected headers as CBOR map
    protected_bytes = _encode_cbor_map(protected_headers)

    result = bytearray()

    # CBOR tag 18 for COSE_Sign1 (optional, but let's include for compatibility)
    result.append(0xD8)  # tag
    result.append(18)  # COSE_Sign1

    # CBOR array header for 4 elements
    result.append(0x84)  # array(4)

    # protected: bstr containing CBOR-encoded map
    _append_cbor_bstr(result, protected_bytes)

    # unprotected: map
    _append_cbor_map(result, unprotected_headers)

    # payload: bstr or nil
    if payload is None:
        result.append(0xF6)  # null
    else:
        _append_cbor_bstr(result, payload)

    # signature: bstr
    _append_cbor_bstr(result, signature)

    return bytes(result)


def _encode_cbor_map(data: Dict[Any, Any]) -> bytes:
    """Encode a dictionary as a CBOR map."""
    result = bytearray()
    length = len(data)

    if length < 24:
        result.append(0xA0 | length)
    elif length < 256:
        result.append(0xB8)
        result.append(length)
    else:
        result.append(0xB9)
        result.extend(length.to_bytes(2, "big"))

    for key, value in data.items():
        _append_cbor_value(result, key)
        _append_cbor_value(result, value)

    return bytes(result)


def _append_cbor_map(result: bytearray, data: Dict[Any, Any]) -> None:
    """Append a CBOR map to the result."""
    result.extend(_encode_cbor_map(data))


def _append_cbor_bstr(result: bytearray, data: bytes) -> None:
    """Append a CBOR byte string to the result."""
    length = len(data)
    if length < 24:
        result.append(0x40 | length)
    elif length < 256:
        result.append(0x58)
        result.append(length)
    elif length < 65536:
        result.append(0x59)
        result.extend(length.to_bytes(2, "big"))
    else:
        result.append(0x5A)
        result.extend(length.to_bytes(4, "big"))
    result.extend(data)


def _append_cbor_value(result: bytearray, value: Any) -> None:
    """Append a CBOR value to the result."""
    if isinstance(value, int):
        if value >= 0:
            if value < 24:
                result.append(value)
            elif value < 256:
                result.append(0x18)
                result.append(value)
            elif value < 65536:
                result.append(0x19)
                result.extend(value.to_bytes(2, "big"))
            elif value < 4294967296:
                result.append(0x1A)
                result.extend(value.to_bytes(4, "big"))
            else:
                result.append(0x1B)
                result.extend(value.to_bytes(8, "big"))
        else:
            neg = -1 - value
            if neg < 24:
                result.append(0x20 | neg)
            elif neg < 256:
                result.append(0x38)
                result.append(neg)
            elif neg < 65536:
                result.append(0x39)
                result.extend(neg.to_bytes(2, "big"))
            elif neg < 4294967296:
                result.append(0x3A)
                result.extend(neg.to_bytes(4, "big"))
            else:
                result.append(0x3B)
                result.extend(neg.to_bytes(8, "big"))
    elif isinstance(value, bytes):
        _append_cbor_bstr(result, value)
    elif isinstance(value, str):
        encoded = value.encode("utf-8")
        length = len(encoded)
        if length < 24:
            result.append(0x60 | length)
        elif length < 256:
            result.append(0x78)
            result.append(length)
        elif length < 65536:
            result.append(0x79)
            result.extend(length.to_bytes(2, "big"))
        else:
            result.append(0x7A)
            result.extend(length.to_bytes(4, "big"))
        result.extend(encoded)
    elif isinstance(value, list):
        length = len(value)
        if length < 24:
            result.append(0x80 | length)
        elif length < 256:
            result.append(0x98)
            result.append(length)
        else:
            result.append(0x99)
            result.extend(length.to_bytes(2, "big"))
        for item in value:
            _append_cbor_value(result, item)
    elif isinstance(value, dict):
        _append_cbor_map(result, value)
    elif value is None:
        result.append(0xF6)
    elif value is True:
        result.append(0xF5)
    elif value is False:
        result.append(0xF4)
    else:
        raise ValueError(f"Unsupported CBOR value type: {type(value)}")


def _get_protected_headers_bytes_from_cose(data: bytes) -> bytes:
    """Extract the raw protected headers bytes from a COSE_Sign1 message.

    :param data: The COSE_Sign1 bytes.
    :return: The raw protected headers bytes.
    """
    decoder = CBORDecoder(data)
    cose_structure = decoder.decode()

    # Handle COSE_Sign1 structure (tag 18)
    if isinstance(cose_structure, dict) and cose_structure.get("tag") == 18:
        cose_structure = cose_structure["value"]

    if not isinstance(cose_structure, list) or len(cose_structure) != 4:
        raise ValueError("Invalid COSE_Sign1 structure")

    return cose_structure[0]  # protected headers bytes


def _verify_receipt(
    jwk: Dict[str, Any],
    receipt_bytes: bytes,
    signed_statement_bytes: bytes,
) -> None:
    """Verify a CCF SCITT receipt.

    :param jwk: The service certificate key (JWK).
    :param receipt_bytes: Receipt in COSE_Sign1 CBOR bytes.
    :param signed_statement_bytes: The input signed statement bytes.
    :raises ValueError: If the verification fails.
    """
    claims_digest = sha256(signed_statement_bytes).digest()

    # Extract expected KID from the JWK
    expected_kid = jwk.get("kid", "").encode("utf-8")

    # Decode the receipt
    receipt = _decode_cose_sign1(receipt_bytes)
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

    crypto_client = CryptographyClient.from_jwk(jwk)
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
                f"Claim digest mismatch: {leaf.data_digest.hex()} != {claims_digest.hex()}"
            )


def _fetch_jwks_document(issuer: str) -> Dict[str, Any]:
    """Fetch the JWKS document from the issuer's endpoint.

    :param issuer: The issuer domain.
    :return: The JWKS document.
    :raises ValueError: If the JWKS document cannot be fetched.
    """
    import json
    from azure.core.pipeline import Pipeline
    from azure.core.pipeline.transport import RequestsTransport
    from azure.core.pipeline.policies import RetryPolicy, UserAgentPolicy
    from azure.core.rest import HttpRequest

    endpoint = f"https://{issuer}/jwks"

    try:
        # Create a simple pipeline with retry and user agent policies
        policies_list = [
            UserAgentPolicy("azure-codetransparency"),
            RetryPolicy(),
        ]
        transport = RequestsTransport()
        pipeline = Pipeline(transport=transport, policies=policies_list)

        request = HttpRequest(
            method="GET", url=endpoint, headers={"Accept": "application/json"}
        )

        response = pipeline.run(request)
        http_response = response.http_response

        if http_response.status_code != 200:
            raise ValueError(
                f"Failed to fetch JWKS document from {issuer}: "
                f"HTTP {http_response.status_code}"
            )

        body = http_response.body()
        if isinstance(body, bytes):
            return json.loads(body.decode("utf-8"))
        else:
            return json.loads(body)

    except Exception as exc:
        raise ValueError(f"Failed to fetch JWKS document from {issuer}: {exc}") from exc


def _get_service_certificate_key(
    receipt_bytes: bytes,
    issuer: str,
    offline_keys: Optional[CodeTransparencyOfflineKeys],
    allow_network_fallback: bool,
) -> Dict[str, Any]:
    """Get the service certificate key for verifying a receipt.

    :param receipt_bytes: The receipt COSE_Sign1 bytes.
    :param issuer: The issuer domain.
    :param offline_keys: Optional offline keys store.
    :param allow_network_fallback: Whether to allow network fallback if offline keys are not found.
    :return: The JWK for verification.
    :raises ValueError: If no matching key is found.
    """
    jwks_document: Optional[Dict[str, Any]] = None

    # Check offline keys first
    if offline_keys is not None and issuer in offline_keys.by_issuer:
        jwks_document = offline_keys.by_issuer[issuer]
    elif allow_network_fallback:
        jwks_document = _fetch_jwks_document(issuer)

    if jwks_document is None:
        raise ValueError(
            f"No keys available for issuer '{issuer}'. "
            "Either offline keys are not configured or network fallback is disabled."
        )

    keys = jwks_document.get("keys", [])
    if not keys:
        raise ValueError("No keys found in JWKS document.")

    # Build keys dictionary
    keys_dict: Dict[str, Dict[str, Any]] = {}
    for key in keys:
        kid = key.get("kid")
        if kid:
            keys_dict[kid] = key

    # Get KID from receipt
    receipt = _decode_cose_sign1(receipt_bytes)
    protected_headers = receipt.get("protected_headers", {})

    kid = protected_headers.get(COSE_HEADER_KID)
    if kid is None:
        raise ValueError("KID not found in receipt.")

    if isinstance(kid, bytes):
        kid_str = kid.decode("utf-8")
    else:
        kid_str = str(kid)

    if kid_str not in keys_dict:
        raise ValueError(f"Key with ID '{kid_str}' not found.")

    return keys_dict[kid_str]


def _prepare_signed_statement_for_verification(
    transparent_statement_bytes: bytes,
) -> bytes:
    """Prepare the signed statement for verification by clearing unprotected headers.

    :param transparent_statement_bytes: The transparent statement COSE_Sign1 bytes.
    :return: The encoded signed statement with cleared unprotected headers.
    """
    cose_sign1 = _decode_cose_sign1(transparent_statement_bytes)
    return _encode_cose_sign1_message(cose_sign1, clear_unprotected=True)


def verify_transparent_statement(
    transparent_statement_bytes: bytes,
    verification_options: Optional[VerificationOptions] = None,
) -> None:
    """Verify the receipt integrity against the COSE_Sign1 envelope and enforce issuer domain rules.

    This function verifies that a transparent statement contains valid receipts from
    authorized code transparency service instances.

    :param transparent_statement_bytes: The transparent statement COSE_Sign1 bytes.
    :param verification_options: Optional verification options. If None, default options are used.
    :raises ValueError: If verification fails.
    :raises AggregateError: If multiple verification failures occur.

    Example usage::

        try:
            verification_options = VerificationOptions(
                authorized_domains=["myservice.confidential-ledger.azure.com"],
                authorized_receipt_behavior=AuthorizedReceiptBehavior.REQUIRE_ALL,
                unauthorized_receipt_behavior=UnauthorizedReceiptBehavior.FAIL_IF_PRESENT,
            )
            verify_transparent_statement(transparent_statement_bytes, verification_options)
            print("Verification succeeded: The statement was registered in the immutable ledger.")
        except Exception as e:
            print(f"Verification failed: {e}")
    """
    if verification_options is None:
        verification_options = VerificationOptions()

    authorized_failures: List[Exception] = []
    unauthorized_failures: List[Exception] = []

    # Extract receipts from transparent statement
    receipt_list = _get_receipts_from_transparent_statement(transparent_statement_bytes)
    if len(receipt_list) == 0:
        raise ValueError("No receipts found in the transparent statement.")

    # Normalize authorized domains
    configured_authorized_list = verification_options.authorized_domains or []
    authorized_list_normalized: set[str] = set()
    for domain in configured_authorized_list:
        if domain and not domain.startswith(UNKNOWN_ISSUER_PREFIX):
            authorized_list_normalized.add(domain.strip().lower())

    # Check if no receipts would be verified
    if (
        len(authorized_list_normalized) == 0
        and verification_options.unauthorized_receipt_behavior
        == UnauthorizedReceiptBehavior.IGNORE_ALL
    ):
        raise ValueError(
            "No receipts would be verified as no authorized domains were provided "
            "and the unauthorized receipt behavior is set to ignore all."
        )

    # Tracking for behaviors
    valid_authorized_domains_encountered: set[str] = set()
    authorized_domains_with_receipt: set[str] = set()

    # Early failure if we must fail on presence of unauthorized receipts
    if (
        verification_options.unauthorized_receipt_behavior
        == UnauthorizedReceiptBehavior.FAIL_IF_PRESENT
    ):
        for issuer, _ in receipt_list:
            if issuer.lower() not in authorized_list_normalized:
                raise ValueError(
                    f"Receipt issuer '{issuer}' is not in the authorized domain list."
                )

    # Prepare signed statement for verification (with cleared unprotected headers)
    signed_statement_bytes = _prepare_signed_statement_for_verification(
        transparent_statement_bytes
    )

    # Determine offline keys settings
    offline_keys = verification_options.offline_keys
    allow_network_fallback = (
        verification_options.offline_keys_behavior
        == OfflineKeysBehavior.FALLBACK_TO_NETWORK
    )

    for issuer, receipt_bytes in receipt_list:
        issuer_lower = issuer.lower()
        is_authorized = issuer_lower in authorized_list_normalized

        if is_authorized:
            authorized_domains_with_receipt.add(issuer_lower)

        # Determine if this receipt should be verified
        should_verify: bool
        if is_authorized:
            should_verify = True
        else:
            if (
                verification_options.unauthorized_receipt_behavior
                == UnauthorizedReceiptBehavior.VERIFY_ALL
            ):
                should_verify = True
            elif (
                verification_options.unauthorized_receipt_behavior
                == UnauthorizedReceiptBehavior.IGNORE_ALL
            ):
                should_verify = False
            else:  # FAIL_IF_PRESENT - already handled above
                should_verify = False

        if not should_verify:
            continue

        if issuer.startswith(UNKNOWN_ISSUER_PREFIX):
            unauthorized_failures.append(
                ValueError(f"Cannot verify receipt with unknown issuer '{issuer}'.")
            )
            continue

        try:
            jwk = _get_service_certificate_key(
                receipt_bytes,
                issuer,
                offline_keys,
                allow_network_fallback,
            )
            _verify_receipt(jwk, receipt_bytes, signed_statement_bytes)

            # Verification succeeded
            if is_authorized:
                valid_authorized_domains_encountered.add(issuer_lower)

        except Exception as exc:
            if is_authorized:
                authorized_failures.append(exc)
            else:
                unauthorized_failures.append(exc)

    # Post-processing based on authorized domain verification behavior
    if (
        verification_options.authorized_receipt_behavior
        == AuthorizedReceiptBehavior.VERIFY_ANY_MATCHING
    ):
        if (
            len(authorized_list_normalized) > 0
            and len(valid_authorized_domains_encountered) == 0
        ):
            authorized_failures.append(
                ValueError("No valid receipts found for any authorized issuer domain.")
            )
        else:
            # If at least one authorized receipt is valid, clear authorized failures
            authorized_failures.clear()

    elif (
        verification_options.authorized_receipt_behavior
        == AuthorizedReceiptBehavior.VERIFY_ALL_MATCHING
    ):
        if (
            len(authorized_list_normalized) > 0
            and len(authorized_domains_with_receipt) == 0
        ):
            authorized_failures.append(
                ValueError("No valid receipts found for any authorized issuer domain.")
            )
        for domain in authorized_domains_with_receipt:
            if domain not in valid_authorized_domains_encountered:
                authorized_failures.append(
                    ValueError(
                        f"A receipt from the required domain '{domain}' failed verification."
                    )
                )

    elif (
        verification_options.authorized_receipt_behavior
        == AuthorizedReceiptBehavior.REQUIRE_ALL
    ):
        for domain in authorized_list_normalized:
            if domain not in valid_authorized_domains_encountered:
                authorized_failures.append(
                    ValueError(
                        f"No valid receipt found for a required domain '{domain}'."
                    )
                )

    # Combine failures
    all_failures = authorized_failures + unauthorized_failures

    if len(all_failures) > 0:
        if len(all_failures) == 1:
            raise all_failures[0]
        else:
            # Create an aggregate exception
            raise AggregateError(all_failures)


class AggregateError(Exception):
    """An exception that contains multiple inner exceptions."""

    def __init__(self, exceptions: List[Exception]):
        self.exceptions = exceptions
        messages = [str(exc) for exc in exceptions]
        super().__init__(f"Multiple verification failures: {'; '.join(messages)}")
