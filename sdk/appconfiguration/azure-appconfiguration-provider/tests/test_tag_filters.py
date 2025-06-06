# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from preparers import app_config_decorator
from azure.appconfiguration.provider import SettingSelector
from test_constants import FEATURE_MANAGEMENT_KEY, FEATURE_FLAG_KEY
from testcase import (
    AppConfigTestCase,
    setup_configs,
    get_configs,
    get_feature_flag,
    has_feature_flag,
    create_config_setting,
)


class TestTagFilters(AppConfigTestCase):
    """Tests for tag filter functionality in Azure App Configuration provider."""

    @staticmethod
    def create_test_configs(client, keyvault_secret_url):
        """Create additional configuration settings with various tag combinations for testing."""
        configs = []
        # Configuration with single tag
        configs.append(create_config_setting("tagged_config", "\0", "tagged value", tags={"a": "b"}))

        # Configuration with multiple tags
        configs.append(create_config_setting("multi_tagged", "\0", "multi tagged value", tags={"a": "b", "c": "d"}))

        # Configuration with tag that has wildcard matchable value
        configs.append(create_config_setting("wildcard_tag", "\0", "wildcard value", tags={"a": "begins_with_b"}))

        # Configuration with tag that has no value
        configs.append(create_config_setting("tag_no_value", "\0", "no value", tags={"a": ""}))

        # Configuration with tag that has special characters
        configs.append(create_config_setting("special_chars", "\0", "special", tags={"special@tag": "special:value"}))

        # Configuration with different tag
        configs.append(create_config_setting("different_tag", "\0", "different", tags={"different": "tag"}))

        # Configuration with no tags
        configs.append(create_config_setting("no_tags", "\0", "no tags"))

        # Add feature flag with tags
        configs.append(
            create_config_setting(
                ".appconfig.featureflag/TaggedFeatureFlag",
                "\0",
                '{	"id": "TaggedFeatureFlag", "description": "", "enabled": true, "conditions": {	"client_filters": []	}}',
                "application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
                tags={"a": "b"},
            )
        )

        # Add feature flag with different tags
        configs.append(
            create_config_setting(
                ".appconfig.featureflag/DifferentTaggedFeatureFlag",
                "\0",
                '{	"id": "DifferentTaggedFeatureFlag", "description": "", "enabled": true, "conditions": {	"client_filters": []	}}',
                "application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
                tags={"different": "tag"},
            )
        )

        # Add feature flag with no tags
        configs.append(
            create_config_setting(
                ".appconfig.featureflag/NoTagsFeatureFlag",
                "\0",
                '{	"id": "NoTagsFeatureFlag", "description": "", "enabled": true, "conditions": {	"client_filters": []	}}',
                "application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
            )
        )

        for config in configs:
            client.set_configuration_setting(config)

    @recorded_by_proxy
    @app_config_decorator
    def test_tag_filter_exact_match(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        """Test filtering by exact tag name and value match."""
        client = self.create_sdk_client(appconfiguration_connection_string)
        self.create_test_configs(client, appconfiguration_keyvault_secret_url)

        selects = {SettingSelector(key_filter="*", tag_filters=["a=b"])}
        config_client = self.create_client(
            appconfiguration_connection_string,
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
        client = self.create_sdk_client(appconfiguration_connection_string)
        self.create_test_configs(client, appconfiguration_keyvault_secret_url)

        selects = {SettingSelector(key_filter="*", tag_filters=["a=b", "c=d"])}
        config_client = self.create_client(
            appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )

        # Should only include settings with both tags "a=b" AND "c=d"
        assert "multi_tagged" in config_client

        # Should not include settings with only one of the tags
        assert "tagged_config" not in config_client
        assert "different_tag" not in config_client
        assert "no_tags" not in config_client

    def test_tag_filter_wildcard(self):
        """Test that unescaped reserved characters are not allowed in tag filters."""
        # Test wildcard character '*' should raise ValueError
        with pytest.raises(ValueError, match=r"contains unescaped reserved character '\*'"):
            SettingSelector(key_filter="*", tag_filters=["a=b*"])

        # Test backslash at end should raise ValueError for incomplete escape sequence
        with pytest.raises(ValueError, match=r"ends with incomplete escape sequence"):
            SettingSelector(key_filter="*", tag_filters=["a=b\\"])

        # Test comma character ',' should raise ValueError
        with pytest.raises(ValueError, match=r"contains unescaped reserved character ','"):
            SettingSelector(key_filter="*", tag_filters=["a=b,c"])

    @recorded_by_proxy
    @app_config_decorator
    def test_tag_filter_empty_value(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        """Test filtering by tag with empty value."""
        client = self.create_sdk_client(appconfiguration_connection_string)
        self.create_test_configs(client, appconfiguration_keyvault_secret_url)

        selects = {SettingSelector(key_filter="*", tag_filters=["a="])}
        config_client = self.create_client(
            appconfiguration_connection_string,
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
        """Test filtering by tag with special characters."""
        client = self.create_sdk_client(appconfiguration_connection_string)
        self.create_test_configs(client, appconfiguration_keyvault_secret_url)

        selects = {SettingSelector(key_filter="*", tag_filters=["special@tag=special:value"])}
        config_client = self.create_client(
            appconfiguration_connection_string,
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
        client = self.create_sdk_client(appconfiguration_connection_string)
        self.create_test_configs(client, appconfiguration_keyvault_secret_url)

        # Only apply tag filters to feature flags
        config_client = self.create_client(
            appconfiguration_connection_string,
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
        client = self.create_sdk_client(appconfiguration_connection_string)
        self.create_test_configs(client, appconfiguration_keyvault_secret_url)

        selects = {SettingSelector(key_filter="*", tag_filters=["nonexistent=tag"])}
        config_client = self.create_client(
            appconfiguration_connection_string,
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
            appconfiguration_connection_string,
            feature_flag_enabled=True,
            feature_flag_selectors={SettingSelector(key_filter="*", tag_filters=["nonexistent=tag"])},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )

        # Feature flags shouldn't be available with non-existent tag filter
        assert len(config_client[FEATURE_MANAGEMENT_KEY]["feature_flags"]) == 0

    def test_tag_filter_max_limit(self):
        """Test that more than 5 tag filters raises ValueError."""
        # Create 6 valid tag filters to test the limit
        six_tag_filters = ["tag1=value1", "tag2=value2", "tag3=value3", "tag4=value4", "tag5=value5", "tag6=value6"]

        # Should raise ValueError for more than 5 tag filters
        with pytest.raises(ValueError, match=r"tag_filters cannot be longer than 5 items\."):
            SettingSelector(key_filter="*", tag_filters=six_tag_filters)
        # Test that exactly 5 tag filters is allowed
        five_tag_filters = six_tag_filters[:5]
        selector = SettingSelector(key_filter="*", tag_filters=five_tag_filters)
        assert selector.tag_filters == five_tag_filters

    def test_escaped_reserved_characters_valid(self):
        """Test that properly escaped reserved characters are accepted."""
        valid_escaped_tags = [
            "tag=value\\*with\\*asterisks",  # Escaped asterisks
            "tag=value\\,with\\,commas",  # Escaped commas
            "tag=value\\\\with\\\\backslashes",  # Escaped backslashes
            "tag=value\\*\\,\\\\mixed",  # Mixed escaped characters
            "normal=\\*escaped\\*normal",  # Normal char with escaped asterisk
            "tag=\\\\\\*\\,all\\*\\,\\\\",  # All reserved chars escaped
            "tag=\\a\\b\\c",  # Non-reserved chars can be escaped
        ]

        for tag in valid_escaped_tags:
            try:
                # Should not raise an exception
                SettingSelector(key_filter="*", tag_filters=[tag])
            except ValueError as e:
                pytest.fail(f"Valid escaped tag '{tag}' should not raise ValueError: {e}")

    def test_unescaped_reserved_characters_invalid(self):
        """Test that unescaped reserved characters are rejected."""
        invalid_tags = [
            "tag=value*with*asterisk",  # Unescaped asterisk
            "tag=value,with,comma",  # Unescaped comma
            "tag=value\\with\\backslash",  # Unescaped backslash (this is actually escaped!)
            "tag=*unescaped",  # Asterisk at start
            "tag=unescaped*",  # Asterisk at end
            "tag=,unescaped",  # Comma at start
            "tag=unescaped,",  # Comma at end
            "tag=mix*ed,values",  # Mixed unescaped
        ]

        # Note: "tag=value\\with\\backslash" is actually valid because \\ is an escaped backslash
        # Let's correct the test cases
        invalid_tags = [
            "tag=value*with*asterisk",  # Unescaped asterisk            "tag=value,with,comma",  # Unescaped comma
            "tag=*unescaped",  # Asterisk at start
            "tag=unescaped*",  # Asterisk at end
            "tag=,unescaped",  # Comma at start
            "tag=unescaped,",  # Comma at end
            "tag=mix*ed,values",  # Mixed unescaped
        ]

        for tag in invalid_tags:
            with pytest.raises(ValueError, match="contains unescaped reserved character"):
                SettingSelector(key_filter="*", tag_filters=[tag])

    def test_incomplete_escape_sequences(self):
        """Test that incomplete escape sequences are rejected."""
        invalid_tags = [
            "tag=value\\",  # Trailing backslash
            "tag=incomplete\\",  # Trailing backslash at end
        ]

        for tag in invalid_tags:
            with pytest.raises(ValueError, match="ends with incomplete escape sequence"):
                SettingSelector(key_filter="*", tag_filters=[tag])

    def test_double_escaped_characters(self):
        """Test handling of double-escaped characters."""
        valid_tags = [
            "tag=value\\\\\\*escaped",  # Escaped backslash followed by escaped asterisk
            "tag=\\\\\\*value",  # Escaped backslash, then escaped asterisk
            "tag=\\\\\\\\value",  # Double escaped backslash
        ]

        for tag in valid_tags:
            try:
                # Should not raise an exception
                SettingSelector(key_filter="*", tag_filters=[tag])
            except ValueError as e:
                pytest.fail(f"Valid double-escaped tag '{tag}' should not raise ValueError: {e}")

    def test_escaped_non_reserved_characters(self):
        """Test that non-reserved characters can be escaped without error."""
        valid_tags = [
            "tag=\\a\\b\\c",  # Escaped normal letters
            "tag=\\1\\2\\3",  # Escaped numbers
            "tag=\\@\\#\\$",  # Escaped special symbols
            "tag=\\n\\t\\r",  # Escaped whitespace chars (as literals)
        ]

        for tag in valid_tags:
            try:
                # Should not raise an exception
                SettingSelector(key_filter="*", tag_filters=[tag])
            except ValueError as e:
                pytest.fail(f"Valid escaped non-reserved tag '{tag}' should not raise ValueError: {e}")

    def test_edge_cases_escaping(self):
        """Test edge cases for escaping logic."""
        # Empty tag name or value with escapes
        valid_edge_cases = [
            "\\*=value",  # Escaped asterisk in tag name
            "tag=\\*",  # Just escaped asterisk as value
            "\\,=\\,",  # Escaped comma in both name and value
        ]

        for tag in valid_edge_cases:
            try:
                SettingSelector(key_filter="*", tag_filters=[tag])
            except ValueError as e:
                # Only check if it's an escaping error, not other validation errors
                if "unescaped reserved character" in str(e) or "incomplete escape sequence" in str(e):
                    pytest.fail(f"Edge case tag '{tag}' should not raise escaping ValueError: {e}")
