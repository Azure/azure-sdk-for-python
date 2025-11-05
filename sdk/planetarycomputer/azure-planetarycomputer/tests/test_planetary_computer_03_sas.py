# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Unit tests for Shared Access Signature (SAS) operations.
"""
import logging
import pytest
from pathlib import Path
from urllib.request import urlopen
from datetime import datetime, timedelta, timezone
import re
from devtools_testutils import recorded_by_proxy, is_live
from testpreparer import PlanetaryComputerProClientTestBase, PlanetaryComputerPreparer
from azure.planetarycomputer.models import (
    SharedAccessSignatureToken,
    SharedAccessSignatureSignedLink,
)

# Set up test logger
test_logger = logging.getLogger("test_sas")
test_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# File handler for test logs
log_file = log_dir / "sas_test_results.log"
file_handler = logging.FileHandler(log_file, mode="w")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
test_logger.addHandler(file_handler)


class TestPlanetaryComputerSas(PlanetaryComputerProClientTestBase):
    """Test suite for Shared Access Signature (SAS) operations."""

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_01_get_token_with_default_duration(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test generating a SAS token with default duration."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_01_get_token_with_default_duration")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_token(collection_id={planetarycomputer_collection_id})"
        )
        response = client.shared_access_signature.get_token(
            collection_id=planetarycomputer_collection_id
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")
        if hasattr(response, "as_dict"):
            test_logger.info(f"Response as_dict: {response.as_dict()}")

        # Assert response is correct type
        assert response is not None, "Response should not be None"
        assert isinstance(
            response, SharedAccessSignatureToken
        ), f"Response should be SharedAccessSignatureToken, got {type(response)}"

        # Verify token format - in playback mode, entire token is sanitized to "Sanitized"
        if is_live():
            # In live mode, verify SAS token format with regex
            sas_token_pattern = (
                r"st=[^&]+&se=[^&]+&sp=[^&]+&sv=[^&]+&sr=[^&]+&.*sig=[^&]+"
            )
            assert re.search(
                sas_token_pattern, response.token
            ), "Token should match SAS token format (st, se, sp, sv, sr, sig)"
        else:
            # In playback mode, just verify token exists as a non-empty string
            assert isinstance(response.token, str), "Token should be a string"
            assert len(response.token) > 0, "Token should not be empty"

        # Verify expires_on is a datetime in the future
        assert isinstance(
            response.expires_on, datetime
        ), "expires_on should be a datetime object"

        if is_live():
            assert response.expires_on > datetime.now(
                timezone.utc
            ), "Token expiry should be in the future"

        # Verify default duration is approximately 24 hours (allow 5 minute tolerance for clock skew)
        if is_live():
            now = datetime.now(timezone.utc)
            expected_expiry = now + timedelta(hours=24)
            time_diff = abs((response.expires_on - expected_expiry).total_seconds())
            assert (
                time_diff < 300
            ), f"Expiry should be ~24 hours from now (diff: {time_diff}s)"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_02_get_token_with_custom_duration(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test generating a SAS token with custom duration."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_02_get_token_with_custom_duration")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        test_logger.info("Input - duration_in_minutes: 60")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_token(collection_id={planetarycomputer_collection_id}, duration_in_minutes=60)"
        )
        response = client.shared_access_signature.get_token(
            collection_id=planetarycomputer_collection_id, duration_in_minutes=60
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")
        if hasattr(response, "as_dict"):
            test_logger.info(f"Response as_dict: {response.as_dict()}")

        # Assert response is correct type
        assert response is not None, "Response should not be None"
        assert isinstance(
            response, SharedAccessSignatureToken
        ), f"Response should be SharedAccessSignatureToken, got {type(response)}"

        # Verify token format - in playback mode, entire token is sanitized to "Sanitized"
        if is_live():
            # In live mode, verify SAS token format with regex
            sas_token_pattern = (
                r"st=[^&]+&se=[^&]+&sp=[^&]+&sv=[^&]+&sr=[^&]+&.*sig=[^&]+"
            )
            assert re.search(
                sas_token_pattern, response.token
            ), "Token should match SAS token format (st, se, sp, sv, sr, sig)"
        else:
            # In playback mode, just verify token exists as a non-empty string
            assert isinstance(response.token, str), "Token should be a string"
            assert len(response.token) > 0, "Token should not be empty"

        # Verify expires_on is a datetime in the future
        assert isinstance(
            response.expires_on, datetime
        ), "expires_on should be a datetime object"

        if is_live():
            assert response.expires_on > datetime.now(
                timezone.utc
            ), "Token expiry should be in the future"

        # Verify custom duration is approximately 60 minutes (allow 5 minute tolerance for clock skew)
        if is_live():
            now = datetime.now(timezone.utc)
            expected_expiry = now + timedelta(minutes=60)
            time_diff = abs((response.expires_on - expected_expiry).total_seconds())
            assert (
                time_diff < 300
            ), f"Expiry should be ~60 minutes from now (diff: {time_diff}s)"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_03_get_sign_with_collection_thumbnail(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test signing an asset HREF using collection thumbnail."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_03_get_sign_with_collection_thumbnail")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info("Getting collection...")
        collection = client.stac.get_collection(
            collection_id=planetarycomputer_collection_id
        )

        assert collection is not None
        assert collection.assets is not None
        assert "thumbnail" in collection.assets

        original_href = collection.assets["thumbnail"].href
        test_logger.info(f"Original HREF: {original_href}")
        assert original_href is not None

        test_logger.info(f"Calling: get_sign(href={original_href})")
        response = client.shared_access_signature.get_sign(href=original_href)

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")
        if hasattr(response, "as_dict"):
            test_logger.info(f"Response as_dict: {response.as_dict()}")

        # Assert response is correct type
        assert response is not None, "Response should not be None"
        assert isinstance(
            response, SharedAccessSignatureSignedLink
        ), f"Response should be SharedAccessSignatureSignedLink, got {type(response)}"

        signed_href = response.href
        test_logger.info(f"Signed HREF: {signed_href}")
        test_logger.info(f"HREF changed: {signed_href != original_href}")
        test_logger.info(f"Has query params: {'?' in signed_href}")
        test_logger.info(f"Has sig param: {'sig=' in signed_href.lower()}")

        # Verify signed HREF is different and contains SAS parameters
        assert (
            signed_href != original_href
        ), "Signed HREF should differ from original HREF"

        # Verify SAS parameters in HREF - skip regex in playback due to sanitization variations
        if is_live():
            # In live mode, verify SAS HREF format with regex
            sas_href_pattern = (
                r"\?.*st=[^&]+&se=[^&]+&sp=[^&]+&sv=[^&]+&sr=[^&]+&.*sig=[^&]+"
            )
            assert re.search(
                sas_href_pattern, signed_href
            ), "Signed HREF should contain SAS parameters (st, se, sp, sv, sr, sig)"
        else:
            # In playback mode, just verify basic SAS structure exists
            assert "?" in signed_href, "Signed HREF should have query parameters"
            assert (
                "sig=" in signed_href.lower()
            ), "Signed HREF should contain signature parameter"

        # Verify expires_on is a datetime in the future (if present)
        if response.expires_on is not None:
            assert isinstance(
                response.expires_on, datetime
            ), "expires_on should be a datetime object"

            if is_live():
                assert response.expires_on > datetime.now(
                    timezone.utc
                ), "Token expiry should be in the future"

        # Verify the signed HREF starts with the original base URL (strip query params first)
        original_base = original_href.split("?")[0]
        signed_base = signed_href.split("?")[0]
        assert (
            signed_base == original_base
        ), "Signed HREF should have the same base URL as original"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_04_signed_href_can_download_asset(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test that a signed HREF can be used to download an asset.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_04_signed_href_can_download_asset")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info("Getting collection...")
        collection = client.stac.get_collection(
            collection_id=planetarycomputer_collection_id
        )
        thumbnail_href = collection.assets["thumbnail"].href
        test_logger.info(f"Thumbnail HREF: {thumbnail_href}")

        test_logger.info(f"Calling: get_sign(href={thumbnail_href})")
        sign_response = client.shared_access_signature.get_sign(href=thumbnail_href)
        signed_href = sign_response.href
        test_logger.info(f"Signed HREF: {signed_href}")

        if is_live():
            test_logger.info("Attempting to download asset (live mode)...")
            with urlopen(signed_href) as download_response:
                content = download_response.read()

                test_logger.info(f"Download status code: {download_response.status}")
                test_logger.info(f"Content length: {len(content)} bytes")
                content_type = download_response.headers.get("content-type", "").lower()
                test_logger.info(f"Content-Type: {content_type}")

                # Verify successful download
                assert (
                    download_response.status == 200
                ), f"Expected 200, got {download_response.status}"
                assert len(content) > 0, "Downloaded content should not be empty"

                # Verify content is binary data (image file)
                # Note: Azure Storage may return 'application/octet-stream' instead of 'image/*'
                assert len(content) > 1000, "Downloaded file should be larger than 1KB"
                # Verify it's actually binary image data by checking PNG magic bytes
                assert (
                    content[:4] == b"\x89PNG"
                ), "Downloaded content should be a PNG image"
        else:
            test_logger.info("Skipping download test (playback mode)")

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_05_revoke_token(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """Test revoking a SAS token. This test runs LAST to avoid breaking other tests."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_05_revoke_token")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Generate a SAS token first
        test_logger.info("Step 1: Generating SAS token...")
        token_response = client.shared_access_signature.get_token(
            collection_id=planetarycomputer_collection_id, duration_in_minutes=60
        )

        test_logger.info(f"Token generated: {token_response.token[:50]}...")
        assert token_response is not None, "Token response should not be None"
        assert isinstance(
            token_response, SharedAccessSignatureToken
        ), f"Response should be SharedAccessSignatureToken, got {type(token_response)}"

        # Revoke the token
        test_logger.info("Step 2: Revoking token...")
        client.shared_access_signature.revoke_token()
        test_logger.info("Token revoked successfully (no exception thrown)")

        test_logger.info("Test PASSED\n")
