# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.appconfiguration._audience import get_audience

# Expected scope constants
_EXPECTED_PUBLIC_CLOUD_AUDIENCE = "https://appconfig.azure.com/"
_EXPECTED_US_GOVERNMENT_AUDIENCE = "https://appconfig.azure.us/"
_EXPECTED_CHINA_AUDIENCE = "https://appconfig.azure.cn/"


class TestGetDefaultScope:
    """Tests for the get_default_scope utility function."""

    def test_get_default_scope_public_cloud_legacy(self):
        """Test default scope for Azure public cloud with legacy endpoint."""
        endpoint = "https://example1.azconfig.azure.com"  # cspell:disable-line
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_PUBLIC_CLOUD_AUDIENCE

    def test_get_default_scope_public_cloud(self):
        """Test default scope for Azure public cloud with regular endpoint."""
        endpoint = "https://example1.appconfig.azure.com"
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_PUBLIC_CLOUD_AUDIENCE

    def test_get_default_scope_china_legacy(self):
        """Test default scope for Azure China cloud with legacy endpoint."""
        endpoint = "https://example1.azconfig.azure.cn"  # cspell:disable-line
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_CHINA_AUDIENCE

    def test_get_default_scope_china(self):
        """Test default scope for Azure China cloud with regular endpoint."""
        endpoint = "https://example1.appconfig.azure.cn"
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_CHINA_AUDIENCE

    def test_get_default_scope_us_government_legacy(self):
        """Test default scope for Azure US Government cloud with legacy endpoint."""
        endpoint = "https://example1.azconfig.azure.us"  # cspell:disable-line
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_US_GOVERNMENT_AUDIENCE

    def test_get_default_scope_us_government(self):
        """Test default scope for Azure US Government cloud with regular endpoint."""
        endpoint = "https://example1.appconfig.azure.us"
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_US_GOVERNMENT_AUDIENCE

    def test_default_scope_with_different_subdomain(self):
        """Test that different subdomains still resolve to correct scope."""
        endpoint = "https://my-store-123.appconfig.azure.com"
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_PUBLIC_CLOUD_AUDIENCE

    def test_get_default_scope_public_cloud_with_trailing_slash(self):
        """Test default scope for Azure public cloud with trailing slash."""
        endpoint = "https://example1.appconfig.azure.com/"
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_PUBLIC_CLOUD_AUDIENCE

    def test_get_default_scope_china_with_trailing_slash(self):
        """Test default scope for Azure China cloud with trailing slash."""
        endpoint = "https://example1.appconfig.azure.cn/"
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_CHINA_AUDIENCE

    def test_get_default_scope_us_government_with_trailing_slash(self):
        """Test default scope for Azure US Government cloud with trailing slash."""
        endpoint = "https://example1.appconfig.azure.us/"
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_US_GOVERNMENT_AUDIENCE

    def test_get_default_scope_legacy_with_trailing_slash(self):
        """Test default scope for legacy endpoint with trailing slash."""
        endpoint = "https://example1.azconfig.azure.us/"  # cspell:disable-line
        actual_scope = get_audience(endpoint)
        assert actual_scope == _EXPECTED_US_GOVERNMENT_AUDIENCE
