# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Algorithm implementation for verifying service issued transparent statements."""

import json
from typing import Dict, List, Any, Optional, Tuple

from azure.codetransparency.cbor import CBORDecoder
from azure.codetransparency import CodeTransparencyClient
from azure.codetransparency.receipt._transparent_statement_verifier_options import (
    AuthorizedReceiptBehavior,
    UnauthorizedReceiptBehavior,
    OfflineKeysBehavior,
    CodeTransparencyOfflineKeys,
    VerificationOptions,
)
from azure.codetransparency.receipt._receipt import (
    get_receipt_kid,
    verify_receipt,
    get_receipt_issuer_host,
    _trim_unprotected_headers,
)

# Prefix for unknown issuers
UNKNOWN_ISSUER_PREFIX = "__unknown-issuer::"

COSE_HEADER_EMBEDDED_RECEIPTS = 394


class AggregateError(Exception):
    """An exception that contains multiple inner exceptions.

    :param exceptions: The list of exceptions that occurred.
    :type exceptions: List[Exception]
    :ivar exceptions: The list of inner exceptions.
    :vartype exceptions: List[Exception]
    """

    def __init__(self, exceptions: List[Exception]):
        """Initialize an AggregateError with a list of exceptions.

        :param exceptions: The list of exceptions that occurred.
        :type exceptions: List[Exception]
        """
        self.exceptions = exceptions
        messages = [str(exc) for exc in exceptions]
        super().__init__(f"Multiple verification failures: {'; '.join(messages)}")


def _get_receipts_from_transparent_statement(
    transparent_statement_bytes: bytes,
) -> List[Tuple[str, bytes]]:
    """Extract receipts from a transparent statement COSE_Sign1 envelope.

    :param transparent_statement_bytes: The COSE_Sign1 bytes containing the transparent statement.
    :type transparent_statement_bytes: bytes
    :return: A list of tuples containing (issuer_host, receipt_bytes).
    :rtype: List[Tuple[str, bytes]]
    :raises ValueError: If embedded receipts are not found or are malformed.
    """
    cose_sign1 = CBORDecoder(transparent_statement_bytes).decode_cose_sign1()
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

        issuer = get_receipt_issuer_host(receipt)
        if issuer is None:
            issuer = f"{UNKNOWN_ISSUER_PREFIX}{idx}"

        receipt_list.append((issuer, receipt))

    return receipt_list


def _get_service_certificate_key(
    receipt_bytes: bytes,
    issuer: str,
    offline_keys: Optional[CodeTransparencyOfflineKeys],
    allow_network_fallback: bool,
    client: Optional[CodeTransparencyClient] = None,
) -> Dict[str, Any]:
    """Get the service certificate key for verifying a receipt.

    :param receipt_bytes: The receipt COSE_Sign1 bytes.
    :type receipt_bytes: bytes
    :param issuer: The issuer domain.
    :type issuer: str
    :param offline_keys: Optional offline keys store.
    :type offline_keys: Optional[CodeTransparencyOfflineKeys]
    :param allow_network_fallback: Whether to allow network fallback if offline keys are not found.
    :type allow_network_fallback: bool
    :param client: Optional CodeTransparencyClient instance (or compatible object with
        get_public_keys method) to use for fetching public keys. It is expected to be
        provided if network fallback is allowed.
    :type client: Optional[CodeTransparencyClient]
    :return: The JWK for verification.
    :rtype: Dict[str, Any]
    :raises ValueError: If no matching key is found or if fetching keys fails.
    """
    jwks_document: Optional[Dict[str, Any]] = None

    # Check offline keys first
    if offline_keys is not None and issuer in offline_keys.by_issuer:
        jwks_document = offline_keys.by_issuer[issuer]
    elif allow_network_fallback and client is not None:
        try:
            response_iter = client.get_public_keys()
            response_bytes = b"".join(response_iter)
            if isinstance(response_bytes, bytes):
                jwks_document = json.loads(response_bytes.decode("utf-8"))
            else:
                jwks_document = json.loads(response_bytes)
        except Exception as exc:
            raise ValueError(
                f"Failed to fetch JWKS document from {issuer} using client: {exc}"
            ) from exc

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

    kid_str = get_receipt_kid(receipt_bytes)
    if kid_str is None:
        raise ValueError("KID not found in receipt.")
    if kid_str not in keys_dict:
        raise ValueError(f"Key with ID '{kid_str}' not found.")

    # Return the matching public key
    return keys_dict[kid_str]


def verify_transparent_statement(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    transparent_statement_bytes: bytes,
    verification_options: Optional[VerificationOptions] = None,
    **kwargs: Any,
) -> None:
    """Verify the receipt integrity against the COSE_Sign1 envelope and enforce issuer domain rules.

    This function verifies that a transparent statement contains valid receipts from
    authorized code transparency service instances.

    :param transparent_statement_bytes: The transparent statement COSE_Sign1 bytes.
    :type transparent_statement_bytes: bytes
    :param verification_options: Optional verification options. If None, default options are used.
    :type verification_options: Optional[VerificationOptions]
    :keyword credential: Optional credential for authenticating with code transparency services
        when network fallback is enabled.
    :paramtype credential: Optional[TokenCredential]
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
    signed_statement_bytes = _trim_unprotected_headers(transparent_statement_bytes)

    # Determine offline keys settings
    offline_keys = verification_options.offline_keys
    allow_network_fallback = (
        verification_options.offline_keys_behavior
        == OfflineKeysBehavior.FALLBACK_TO_NETWORK
    )

    # Cache for client instances per issuer domain
    # This would deal with multiple receipts from the same issuer
    client_instances: Dict[str, CodeTransparencyClient] = {}

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
            if issuer not in client_instances and allow_network_fallback:
                endpoint = f"https://{issuer}"
                client_credential = kwargs.get("credential", None)
                client_instances[issuer] = CodeTransparencyClient(
                    endpoint, client_credential, **kwargs  # type: ignore[arg-type]
                )
            client = client_instances.get(issuer, None)
            jwk = _get_service_certificate_key(
                receipt_bytes,
                issuer,
                offline_keys,
                allow_network_fallback,
                client=client,
            )
            verify_receipt(
                jwk,
                receipt_bytes,
                signed_statement_bytes,
                trim_unprotected_headers=False,  # already trimmed above
            )

            # Verification succeeded
            if is_authorized:
                valid_authorized_domains_encountered.add(issuer_lower)

        except Exception as exc:  # pylint: disable=broad-exception-caught
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

    if len(all_failures) == 1:
        raise all_failures[0]

    if len(all_failures) > 0:
        # Create an aggregate exception
        raise AggregateError(all_failures)
