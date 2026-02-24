# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import recorded_by_proxy
from preparers import app_config_decorator
from test_constants import FEATURE_MANAGEMENT_KEY
from testcase import (
    AppConfigTestCase,
    has_feature_flag,
)
from azure.appconfiguration.provider import SettingSelector
from azure.appconfiguration.provider._constants import NULL_CHAR


class TestTagFilters(AppConfigTestCase):
    """Tests for tag filter functionality in Azure App Configuration provider."""

    @recorded_by_proxy
    @app_config_decorator
    def test_tag_filter_exact_match(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        """Test filtering by exact tag name and value match."""
        selects = {SettingSelector(key_filter="*", tag_filters=["a=b"])}
        config_client = self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )

        # Should include settings with tag "a=b"
        assert "tagged_config" in config_client
        assert "multi_tagged" in config_client

        # Should not include settings without tag "a=b"
        assert "different_tag" not in config_client
        assert "no_tags" not in config_client
        assert "wildcard_tag" not in config_client

    @recorded_by_proxy
    @app_config_decorator
    def test_multiple_tag_filters(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        """Test filtering with multiple tag filters (AND condition)."""
        selects = {SettingSelector(key_filter="*", tag_filters=["a=b", "c=d"])}
        config_client = self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )

        # Should only include settings with both tags "a=b" AND "c=d"
        assert "multi_tagged" in config_client

        # Should not include settings with only one of the tags
        assert "tagged_config" not in config_client
        assert "different_tag" not in config_client
        assert "no_tags" not in config_client

    @recorded_by_proxy
    @app_config_decorator
    def test_tag_filter_empty_value(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        """Test filtering by tag with empty value."""
        selects = {SettingSelector(key_filter="*", tag_filters=["a="])}
        config_client = self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )

        # Should include settings with tag "a" having empty value
        assert "tag_no_value" in config_client

        # Should not include settings with tag "a" having non-empty value
        assert "tagged_config" not in config_client
        assert "multi_tagged" not in config_client
        assert "wildcard_tag" not in config_client
        assert "different_tag" not in config_client
        assert "no_tags" not in config_client

    @recorded_by_proxy
    @app_config_decorator
    def test_tag_filter_special_characters(
        self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url
    ):
        selects = {SettingSelector(key_filter="*", tag_filters=["special@tag=special:value"])}
        config_client = self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )

        # Should include settings with the special tag
        assert "special_chars" in config_client

        # Should not include other settings
        assert "tagged_config" not in config_client
        assert "multi_tagged" not in config_client
        assert "no_tags" not in config_client

    @recorded_by_proxy
    @app_config_decorator
    def test_feature_flag_tag_filters(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        """Test tag filters with feature flags."""
        # Only apply tag filters to feature flags
        config_client = self.create_client(
            connection_string=appconfiguration_connection_string,
            feature_flag_enabled=True,
            feature_flag_selectors={SettingSelector(key_filter="*", tag_filters=["a=b"])},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )

        # Should include all regular settings (no filter)
        assert "tagged_config" in config_client
        assert "multi_tagged" in config_client
        assert "different_tag" in config_client
        assert "no_tags" in config_client

        # Should include only feature flags with tag "a=b"
        assert FEATURE_MANAGEMENT_KEY in config_client
        assert has_feature_flag(config_client, "TaggedFeatureFlag")
        assert not has_feature_flag(config_client, "DifferentTaggedFeatureFlag")
        assert not has_feature_flag(config_client, "NoTagsFeatureFlag")

    @recorded_by_proxy
    @app_config_decorator
    def test_nonexistent_tag_filter(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        """Test filtering by non-existent tag."""
        selects = {SettingSelector(key_filter="*", tag_filters=["nonexistent=tag"])}
        config_client = self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )

        # Should not include any settings
        assert "tagged_config" not in config_client
        assert "multi_tagged" not in config_client
        assert "different_tag" not in config_client
        assert "no_tags" not in config_client

        # Check that feature flags are also filtered properly
        config_client = self.create_client(
            connection_string=appconfiguration_connection_string,
            feature_flag_enabled=True,
            feature_flag_selectors={SettingSelector(key_filter="*", tag_filters=["nonexistent=tag"])},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )

        # Feature flags shouldn't be available with non-existent tag filter
        assert len(config_client[FEATURE_MANAGEMENT_KEY]["feature_flags"]) == 0

    @recorded_by_proxy
    @app_config_decorator
    def test_tag_filter_with_null_value(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        """Test filtering by tag with null value."""
        selects = {SettingSelector(key_filter="*", tag_filters=["tag=" + NULL_CHAR])}
        config_client = self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )

        # Should include settings with tag "null_tag" having null value
        assert "null_tag" in config_client
