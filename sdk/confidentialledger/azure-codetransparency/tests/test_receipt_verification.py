# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for CCF SCITT receipt verification."""

import json
import os
import responses
import pytest

from azure.codetransparency.receipt import (
    verify_transparent_statement,
    VerificationOptions,
    AuthorizedReceiptBehavior,
    UnauthorizedReceiptBehavior,
    CodeTransparencyOfflineKeys,
    OfflineKeysBehavior,
    AggregateError,
)
from azure.codetransparency.cbor import CBORDecoder, CBOREncoder
from azure.codetransparency.receipt._receipt_verification import (
    _verify_receipt,
    _get_receipt_issuer_host,
    _get_receipts_from_transparent_statement,
    _get_service_certificate_key,
)


# Get the directory containing test files
TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files")


def read_file_bytes(name: str) -> bytes:
    """Read a test file and return its bytes."""
    file_path = os.path.join(TEST_FILES_DIR, name)
    with open(file_path, "rb") as f:
        return f.read()


class TestReceiptVerification:
    """Tests for receipt verification functionality."""

    def test_verify_receipt_kid_mismatch_throws_value_error(self):
        """Test that verification fails with KID mismatch error when using wrong key."""
        # JWK with wrong KID (different from what's in the receipt)
        wrong_kid_jwk = {
            "crv": "P-384",
            "kid": "fb29ce6d6b37e7a0b03a5fc94205490e1c37de1f41f68b92e3620021e9981d01",
            "kty": "EC",
            "x": "Tv_tP9eJIb5oJY9YB6iAzMfds4v3N84f8pgcPYLaxd_Nj3Nb_dBm6Fc8ViDZQhGR",
            "y": "xJ7fI2kA8gs11XDc9h2zodU-fZYRrE0UJHpzPfDVJrOpTvPcDoC5EWOBx9Fks0bZ",
        }

        receipt_bytes = read_file_bytes("receipt.cose")
        input_signed_payload_bytes = read_file_bytes("statement.cose")

        with pytest.raises(ValueError) as exc_info:
            _verify_receipt(wrong_kid_jwk, receipt_bytes, input_signed_payload_bytes)

        assert "KID mismatch" in str(exc_info.value)

    def test_verify_valid_receipt_statement_digest_mismatch_throws_value_error(self):
        """Test that verification fails with statement digest mismatch when using correct key and receipt."""

        # JWK with correct KID but we'll verify against wrong/modified payload
        # This KID matches what's in the receipt
        correct_kid_jwk = {
            "crv": "P-384",
            "kid": "87d64669f1c5988e28f22da4f3526334de860ad2395a71a735de59f9ec3aa662",
            "kty": "EC",
            "x": "9y7Zs09nKjYQHdJ7oAsxftOvSK9RfGWJM3p0_5XXyBuvkUs-kN-YB-EQCCuB_Hsw",
            "y": "teV4Jkd2zphYJa2gPSm5HEjuvEM9MNu3e5E7z1L_0s0GWKaEqmHpAiXBtLGHC5-A",
        }

        receipt_bytes = read_file_bytes("receipt.cose")
        input_signed_payload_bytes = read_file_bytes("statement.cose")

        with pytest.raises(ValueError) as exc_info:
            _verify_receipt(correct_kid_jwk, receipt_bytes, input_signed_payload_bytes)

        error_message = str(exc_info.value)
        assert "statement digest does not match the leaf digest in the receipt" in error_message.lower()

    def test_decode_receipt_cose_structure(self):
        """Test that we can decode the receipt COSE_Sign1 structure."""
        receipt_bytes = read_file_bytes("receipt.cose")

        cose_sign1 = CBORDecoder(receipt_bytes).decode_cose_sign1()

        assert "protected_headers" in cose_sign1
        assert "unprotected_headers" in cose_sign1
        assert "signature" in cose_sign1
        assert isinstance(cose_sign1["signature"], bytes)

    def test_decode_transparent_statement_cose_structure(self):
        """Test that we can decode the transparent statement COSE_Sign1 structure."""
        transparent_statement_bytes = read_file_bytes("transparent_statement.cose")

        decoded = CBORDecoder(transparent_statement_bytes).decode_cose_sign1()

        assert "protected_headers" in decoded
        assert "unprotected_headers" in decoded
        assert "payload" in decoded
        assert "signature" in decoded

        reencoded = CBOREncoder().encode_cose_sign1(
            protected_headers=decoded.get("protected_headers", {}),
            unprotected_headers=decoded.get("unprotected_headers", {}),
            payload=decoded.get("payload", b""),
            signature=decoded.get("signature", b""),
            include_tag=decoded.get("was_tagged", True),
        )
        assert reencoded.hex() == transparent_statement_bytes.hex()

    def test_get_receipts_from_transparent_statement(self):
        """Test that we can extract receipts from a transparent statement."""
        transparent_statement_bytes = read_file_bytes("transparent_statement.cose")

        receipts = _get_receipts_from_transparent_statement(transparent_statement_bytes)

        # Should have at least one receipt
        assert len(receipts) == 1
        assert receipts[0][0] == "foo.bar.com"
        assert isinstance(receipts[0][1], bytes)

    def test_verify_transparent_statement_no_receipts_raises_error(self):
        """Test that verification fails when no receipts are found."""
        # Create a minimal valid COSE_Sign1 without embedded receipts
        # Tag 18 (COSE_Sign1) + array of 4 elements: protected, unprotected (empty map), payload, signature
        # This structure has no header 394 (embedded receipts)

        # Build a properly formed COSE_Sign1 structure manually
        # D2 18 = tag(18) for COSE_Sign1
        # 84 = array(4)
        # 43 A1 01 26 = bstr(3) containing {1: -7} (ES256 algorithm)
        # A0 = empty map (unprotected headers - no receipts!)
        # 44 74 65 73 74 = bstr(4) "test" (payload)
        # 58 20 + 32 zeros = bstr(32) signature placeholder
        minimal_cose = bytes(
            [
                0xD8,
                0x12,  # tag(18) COSE_Sign1
                0x84,  # array(4)
                0x43,
                0xA1,
                0x01,
                0x26,  # bstr(3) with {1: -7}
                0xA0,  # empty map (no receipts)
                0x44,
                0x74,
                0x65,
                0x73,
                0x74,  # bstr(4) "test"
                0x58,
                0x20,  # bstr(32)
            ]
            + [0x00] * 32
        )  # 32 bytes of zeros for signature

        with pytest.raises(ValueError) as exc_info:
            verify_transparent_statement(minimal_cose)

        error_msg = str(exc_info.value).lower()
        assert (
            "receipts" in error_msg
            or "not found" in error_msg
            or "embedded" in error_msg
        )

    def test_verify_transparent_statement_with_unauthorized_domain_fails(self):
        """Test that verification fails when receipt issuer is not in authorized domains."""
        transparent_statement_bytes = read_file_bytes("transparent_statement.cose")

        # Get the actual issuer from the receipts
        receipts = _get_receipts_from_transparent_statement(transparent_statement_bytes)
        actual_issuer = receipts[0][0]
        assert actual_issuer == "foo.bar.com"

        # Use a different domain than the actual issuer
        verification_options = VerificationOptions(
            authorized_domains=["some-other-domain.confidential-ledger.azure.com"],
            unauthorized_receipt_behavior=UnauthorizedReceiptBehavior.FAIL_IF_PRESENT,
        )

        with pytest.raises(ValueError) as exc_info:
            verify_transparent_statement(
                transparent_statement_bytes, verification_options
            )

        assert "not in the authorized domain list" in str(exc_info.value)

    def test_verify_transparent_statement_with_offline_keys_no_fallback_fails_when_key_missing(
        self,
    ):
        """Test that verification fails when offline keys don't have the required issuer."""
        transparent_statement_bytes = read_file_bytes("transparent_statement.cose")

        # Create offline keys that don't include the actual issuer
        offline_keys = CodeTransparencyOfflineKeys(
            by_issuer={"wrong-issuer.confidential-ledger.azure.com": {"keys": []}}
        )

        verification_options = VerificationOptions(
            authorized_domains=[],  # Allow any domain
            unauthorized_receipt_behavior=UnauthorizedReceiptBehavior.VERIFY_ALL,
            offline_keys=offline_keys,
            offline_keys_behavior=OfflineKeysBehavior.NO_FALLBACK_TO_NETWORK,
        )

        with pytest.raises(ValueError) as exc_info:
            verify_transparent_statement(
                transparent_statement_bytes, verification_options
            )

        assert (
            "No keys available" in str(exc_info.value)
            or "not found" in str(exc_info.value).lower()
        )

    def test_verification_options_defaults(self):
        """Test that VerificationOptions has correct default values."""
        options = VerificationOptions()

        assert options.authorized_domains == []
        assert (
            options.unauthorized_receipt_behavior
            == UnauthorizedReceiptBehavior.FAIL_IF_PRESENT
        )
        assert (
            options.authorized_receipt_behavior
            == AuthorizedReceiptBehavior.VERIFY_ALL_MATCHING
        )
        assert options.offline_keys is None
        assert options.offline_keys_behavior == OfflineKeysBehavior.FALLBACK_TO_NETWORK

    def test_verification_options_custom_values(self):
        """Test that VerificationOptions accepts custom values."""
        offline_keys = CodeTransparencyOfflineKeys(by_issuer={"test.com": {"keys": []}})

        options = VerificationOptions(
            authorized_domains=["domain1.com", "domain2.com"],
            unauthorized_receipt_behavior=UnauthorizedReceiptBehavior.IGNORE_ALL,
            authorized_receipt_behavior=AuthorizedReceiptBehavior.REQUIRE_ALL,
            offline_keys=offline_keys,
            offline_keys_behavior=OfflineKeysBehavior.NO_FALLBACK_TO_NETWORK,
        )

        assert options.authorized_domains == ["domain1.com", "domain2.com"]
        assert (
            options.unauthorized_receipt_behavior
            == UnauthorizedReceiptBehavior.IGNORE_ALL
        )
        assert (
            options.authorized_receipt_behavior == AuthorizedReceiptBehavior.REQUIRE_ALL
        )
        assert options.offline_keys is offline_keys
        assert (
            options.offline_keys_behavior == OfflineKeysBehavior.NO_FALLBACK_TO_NETWORK
        )


class TestGetServiceCertificateKey:
    """Tests for _get_service_certificate_key functionality."""

    def test_get_key_from_offline_keys_success(self):
        """Test successfully retrieving a key from offline keys."""
        receipt_bytes = read_file_bytes("receipt.cose")

        # The receipt has KID: 87d64669f1c5988e28f22da4f3526334de860ad2395a71a735de59f9ec3aa662
        valid_jwk = {
            "crv": "P-384",
            "kid": "87d64669f1c5988e28f22da4f3526334de860ad2395a71a735de59f9ec3aa662",
            "kty": "EC",
            "x": "9y7Zs09nKjYQHdJ7oAsxftOvSK9RfGWJM3p0_5XXyBuvkUs-kN-YB-EQCCuB_Hsw",
            "y": "teV4Jkd2zphYJa2gPSm5HEjuvEM9MNu3e5E7z1L_0s0GWKaEqmHpAiXBtLGHC5-A",
        }

        offline_keys = CodeTransparencyOfflineKeys(
            by_issuer={"foo.bar.com": {"keys": [valid_jwk]}}
        )

        result = _get_service_certificate_key(
            receipt_bytes=receipt_bytes,
            issuer="foo.bar.com",
            offline_keys=offline_keys,
            allow_network_fallback=False,
        )

        assert result["kid"] == valid_jwk["kid"]
        assert result["crv"] == "P-384"
        assert result["kty"] == "EC"

    def test_get_key_no_offline_keys_no_fallback_raises_error(self):
        """Test that error is raised when no offline keys and network fallback is disabled."""
        receipt_bytes = read_file_bytes("receipt.cose")

        with pytest.raises(ValueError) as exc_info:
            _get_service_certificate_key(
                receipt_bytes=receipt_bytes,
                issuer="foo.bar.com",
                offline_keys=None,
                allow_network_fallback=False,
            )

        assert "No keys available" in str(exc_info.value)

    def test_get_key_issuer_not_in_offline_keys_no_fallback_raises_error(self):
        """Test that error is raised when issuer is not in offline keys and fallback is disabled."""
        receipt_bytes = read_file_bytes("receipt.cose")

        # Offline keys for a different issuer
        offline_keys = CodeTransparencyOfflineKeys(
            by_issuer={"different-issuer.com": {"keys": []}}
        )

        with pytest.raises(ValueError) as exc_info:
            _get_service_certificate_key(
                receipt_bytes=receipt_bytes,
                issuer="foo.bar.com",
                offline_keys=offline_keys,
                allow_network_fallback=False,
            )

        assert "No keys available" in str(exc_info.value)

    def test_get_key_empty_keys_in_jwks_raises_error(self):
        """Test that error is raised when JWKS document has empty keys array."""
        receipt_bytes = read_file_bytes("receipt.cose")

        # Offline keys with empty keys array
        offline_keys = CodeTransparencyOfflineKeys(
            by_issuer={"foo.bar.com": {"keys": []}}
        )

        with pytest.raises(ValueError) as exc_info:
            _get_service_certificate_key(
                receipt_bytes=receipt_bytes,
                issuer="foo.bar.com",
                offline_keys=offline_keys,
                allow_network_fallback=False,
            )

        assert "No keys found in JWKS document" in str(exc_info.value)

    def test_get_key_kid_not_found_in_jwks_raises_error(self):
        """Test that error is raised when KID from receipt is not found in JWKS."""
        receipt_bytes = read_file_bytes("receipt.cose")

        # JWK with different KID than what's in the receipt
        wrong_kid_jwk = {
            "crv": "P-384",
            "kid": "wrong_kid_that_does_not_match",
            "kty": "EC",
            "x": "9y7Zs09nKjYQHdJ7oAsxftOvSK9RfGWJM3p0_5XXyBuvkUs-kN-YB-EQCCuB_Hsw",
            "y": "teV4Jkd2zphYJa2gPSm5HEjuvEM9MNu3e5E7z1L_0s0GWKaEqmHpAiXBtLGHC5-A",
        }

        offline_keys = CodeTransparencyOfflineKeys(
            by_issuer={"foo.bar.com": {"keys": [wrong_kid_jwk]}}
        )

        with pytest.raises(ValueError) as exc_info:
            _get_service_certificate_key(
                receipt_bytes=receipt_bytes,
                issuer="foo.bar.com",
                offline_keys=offline_keys,
                allow_network_fallback=False,
            )

        assert "not found" in str(exc_info.value).lower()

    def test_get_key_selects_correct_key_from_multiple_keys(self):
        """Test that the correct key is selected when JWKS contains multiple keys."""
        receipt_bytes = read_file_bytes("receipt.cose")

        # The receipt has KID: 87d64669f1c5988e28f22da4f3526334de860ad2395a71a735de59f9ec3aa662
        correct_jwk = {
            "crv": "P-384",
            "kid": "87d64669f1c5988e28f22da4f3526334de860ad2395a71a735de59f9ec3aa662",
            "kty": "EC",
            "x": "9y7Zs09nKjYQHdJ7oAsxftOvSK9RfGWJM3p0_5XXyBuvkUs-kN-YB-EQCCuB_Hsw",
            "y": "teV4Jkd2zphYJa2gPSm5HEjuvEM9MNu3e5E7z1L_0s0GWKaEqmHpAiXBtLGHC5-A",
        }

        other_jwk = {
            "crv": "P-384",
            "kid": "another_kid_value",
            "kty": "EC",
            "x": "Tv_tP9eJIb5oJY9YB6iAzMfds4v3N84f8pgcPYLaxd_Nj3Nb_dBm6Fc8ViDZQhGR",
            "y": "xJ7fI2kA8gs11XDc9h2zodU-fZYRrE0UJHpzPfDVJrOpTvPcDoC5EWOBx9Fks0bZ",
        }

        # Include multiple keys, the correct one should be selected
        offline_keys = CodeTransparencyOfflineKeys(
            by_issuer={"foo.bar.com": {"keys": [other_jwk, correct_jwk]}}
        )

        result = _get_service_certificate_key(
            receipt_bytes=receipt_bytes,
            issuer="foo.bar.com",
            offline_keys=offline_keys,
            allow_network_fallback=False,
        )

        assert result["kid"] == correct_jwk["kid"]

    def test_get_key_with_network_fallback_no_client_raises_error(self):
        """Test that error is raised when network fallback is allowed but no client is provided."""
        receipt_bytes = read_file_bytes("receipt.cose")

        # No offline keys, network fallback allowed but no client
        with pytest.raises(ValueError) as exc_info:
            _get_service_certificate_key(
                receipt_bytes=receipt_bytes,
                issuer="foo.bar.com",
                offline_keys=None,
                allow_network_fallback=True,
                client=None,
            )

        assert "No keys available" in str(exc_info.value)


class TestTransparentStatementWithFiles:
    """Tests using the actual test files for transparent statement verification."""

    def test_extract_issuer_from_transparent_statement_receipts(self):
        """Test extracting issuer information from transparent statement receipts."""
        transparent_statement_bytes = read_file_bytes("transparent_statement.cose")

        receipts = _get_receipts_from_transparent_statement(transparent_statement_bytes)

        assert len(receipts) == 1
        issuer, receipt_bytes = receipts[0]
        assert issuer == "foo.bar.com"

        # The receipt bytes should be valid COSE
        receipt_cose = CBORDecoder(receipt_bytes).decode_cose_sign1()
        assert "protected_headers" in receipt_cose

        receipt_issuer = _get_receipt_issuer_host(receipt_bytes)
        assert receipt_issuer == issuer

    def test_verify_transparent_statement_requires_all_domains_fails_when_domain_missing(
        self,
    ):
        """Test REQUIRE_ALL behavior fails when a required domain has no valid receipt."""
        transparent_statement_bytes = read_file_bytes("transparent_statement.cose")

        # Get actual issuer - we know it's "foo.bar.com" from the transparent_statement.cose
        receipts = _get_receipts_from_transparent_statement(transparent_statement_bytes)
        actual_issuer = receipts[0][0] if receipts else "unknown"
        assert actual_issuer == "foo.bar.com"

        # Require both the actual issuer AND another domain that doesn't exist
        # This should fail because we can't verify against nonexistent-domain
        verification_options = VerificationOptions(
            authorized_domains=[actual_issuer, "nonexistent-domain.azure.com"],
            authorized_receipt_behavior=AuthorizedReceiptBehavior.REQUIRE_ALL,
            unauthorized_receipt_behavior=UnauthorizedReceiptBehavior.IGNORE_ALL,  # Ignore unauthorized
            offline_keys=CodeTransparencyOfflineKeys(
                by_issuer={}
            ),  # Empty offline keys
            offline_keys_behavior=OfflineKeysBehavior.NO_FALLBACK_TO_NETWORK,  # Don't try network
        )

        with pytest.raises((ValueError, AggregateError)) as exc_info:
            verify_transparent_statement(
                transparent_statement_bytes, verification_options
            )

        # Should fail because nonexistent-domain has no receipt OR because foo.bar.com key is not available
        error_message = str(exc_info.value).lower()
        assert (
            "nonexistent-domain" in error_message
            or "no valid receipt" in error_message
            or "no keys available" in error_message
        )

    def test_verify_transparent_statement_with_offline_jwks(self):
        """Test verifying transparent statement with mocked offline JWKS for the issuer."""
        transparent_statement_bytes = read_file_bytes("transparent_statement.cose")

        # Valid JWKS for the issuer foo.bar.com (taken from C# test)
        valid_jwk = {
            "crv": "P-384",
            "kid": "fb29ce6d6b37e7a0b03a5fc94205490e1c37de1f41f68b92e3620021e9981d01",
            "kty": "EC",
            "x": "Tv_tP9eJIb5oJY9YB6iAzMfds4v3N84f8pgcPYLaxd_Nj3Nb_dBm6Fc8ViDZQhGR",
            "y": "xJ7fI2kA8gs11XDc9h2zodU-fZYRrE0UJHpzPfDVJrOpTvPcDoC5EWOBx9Fks0bZ",
        }

        # Create offline keys with the valid JWKS for foo.bar.com
        offline_keys = CodeTransparencyOfflineKeys(
            by_issuer={"foo.bar.com": {"keys": [valid_jwk]}}
        )

        verification_options = VerificationOptions(
            authorized_domains=["foo.bar.com"],
            authorized_receipt_behavior=AuthorizedReceiptBehavior.VERIFY_ALL_MATCHING,
            unauthorized_receipt_behavior=UnauthorizedReceiptBehavior.FAIL_IF_PRESENT,
            offline_keys=offline_keys,
            offline_keys_behavior=OfflineKeysBehavior.NO_FALLBACK_TO_NETWORK,
        )

        # This should succeed - verifying the transparent statement with valid offline keys
        verify_transparent_statement(transparent_statement_bytes, verification_options)

    @responses.activate
    def test_verify_transparent_statement_with_online_keys_mocked(self, tmp_path):
        """Test verifying transparent statement with mocked network calls for online key retrieval."""
        transparent_statement_bytes = read_file_bytes("transparent_statement.cose")

        # Valid JWKS for the issuer foo.bar.com (taken from C# test)
        valid_jwk = {
            "crv": "P-384",
            "kid": "fb29ce6d6b37e7a0b03a5fc94205490e1c37de1f41f68b92e3620021e9981d01",
            "kty": "EC",
            "x": "Tv_tP9eJIb5oJY9YB6iAzMfds4v3N84f8pgcPYLaxd_Nj3Nb_dBm6Fc8ViDZQhGR",
            "y": "xJ7fI2kA8gs11XDc9h2zodU-fZYRrE0UJHpzPfDVJrOpTvPcDoC5EWOBx9Fks0bZ",
        }

        # Create JWKS document that would be returned from the network
        jwks_document = {"keys": [valid_jwk]}

        # Mock the ledger identity endpoint
        responses.add(
            responses.GET,
            "https://identity.confidential-ledger.core.azure.com/ledgerIdentity/foo",
            body=json.dumps(
                {
                    "ledgerTlsCertificate": "-----BEGIN CERTIFICATE-----\nMIIB...IDAQAB\n-----END CERTIFICATE-----\n"  # cSpell:disable-line
                }
            ),
            status=200,
            content_type="application/json",
        )

        # Mock the JWKS endpoint
        responses.add(
            responses.GET,
            "https://foo.bar.com/jwks",
            body=json.dumps(jwks_document),
            status=200,
            content_type="application/json",
        )

        # Use FALLBACK_TO_NETWORK to trigger network key retrieval
        # No offline keys configured for the issuer
        verification_options = VerificationOptions(
            authorized_domains=["foo.bar.com"],
            authorized_receipt_behavior=AuthorizedReceiptBehavior.VERIFY_ALL_MATCHING,
            unauthorized_receipt_behavior=UnauthorizedReceiptBehavior.FAIL_IF_PRESENT,
            offline_keys=None,  # No offline keys - force network fallback
            offline_keys_behavior=OfflineKeysBehavior.FALLBACK_TO_NETWORK,
        )

        # This should succeed - verifying the transparent statement with mocked online keys
        verify_transparent_statement(
            transparent_statement_bytes,
            verification_options,
        )

        # Verify that the JWKS endpoint was called
        assert responses.calls[0].request.url is not None
        assert responses.calls[0].request.url.startswith("https://identity.confidential-ledger.core.azure.com/ledgerIdentity/foo")
        assert responses.calls[1].request.url is not None
        assert responses.calls[1].request.url.startswith("https://foo.bar.com/jwks")
        assert len(responses.calls) == 2  # 1 identity + 1 JWKS request

