# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.appconfiguration.provider._models import SettingSelector
from azure.appconfiguration.provider._constants import NULL_CHAR


class TestSettingSelector:
    """Tests for the SettingSelector class."""

    def test_setting_selector_init(self):
        """Test the initialization of SettingSelector with valid parameters."""
        # Basic initialization with key_filter only
        selector = SettingSelector(key_filter="*")
        assert selector.key_filter == "*"
        assert selector.label_filter == NULL_CHAR
        assert selector.tag_filters is None

        # Initialization with all parameters
        selector = SettingSelector(
            key_filter="my-key*", label_filter="my-label", tag_filters=["tag1=value1", "tag2=value2"]
        )
        assert selector.key_filter == "my-key*"
        assert selector.label_filter == "my-label"
        assert selector.tag_filters == ["tag1=value1", "tag2=value2"]

    def test_setting_selector_tag_filters_validation(self):
        """Test the validation of tag_filters in SettingSelector."""
        # Valid tag filters
        selector = SettingSelector(key_filter="*", tag_filters=["tag=value"])
        assert selector.tag_filters == ["tag=value"]

        selector = SettingSelector(key_filter="*", tag_filters=["tag=value", "another=one"])
        assert selector.tag_filters == ["tag=value", "another=one"]

        selector = SettingSelector(key_filter="*", tag_filters=["tag="])
        assert selector.tag_filters == ["tag="]

        # Special characters in tag names and values
        selector = SettingSelector(key_filter="*", tag_filters=["special@tag=special:value"])
        assert selector.tag_filters == ["special@tag=special:value"]

    def test_setting_selector_invalid_tag_filters(self):
        """Test that appropriate exceptions are raised for invalid tag filters."""
        # Non-list tag filters
        with pytest.raises(TypeError, match="tag_filters must be a list of strings."):
            SettingSelector(key_filter="*", tag_filters="tag=value")  # type:ignore

        with pytest.raises(TypeError, match="tag_filters must be a list of strings."):
            SettingSelector(key_filter="*", tag_filters={"tag": "value"})  # type:ignore

        # Empty tag filter
        with pytest.raises(ValueError, match="Tag filter cannot be an empty string or None."):
            SettingSelector(key_filter="*", tag_filters=[""])

        # No equals sign in tag filter
        with pytest.raises(ValueError, match=r"Tag filter tag does not follow the format \"tagName=tagValue\"."):
            SettingSelector(key_filter="*", tag_filters=["tag"])

        # Equals sign at start in tag filter
        with pytest.raises(ValueError, match=r"Tag filter =value does not follow the format \"tagName=tagValue\"."):
            SettingSelector(key_filter="*", tag_filters=["=value"])

    def test_setting_selector_with_multiple_tag_filters(self):
        """Test SettingSelector with multiple tag filters."""
        selector = SettingSelector(key_filter="*", tag_filters=["tag1=value1", "tag2=value2", "tag3=value3"])
        assert selector.tag_filters == ["tag1=value1", "tag2=value2", "tag3=value3"]

    def test_setting_selector_different_key_filters(self):
        """Test SettingSelector with different key filters."""
        selector = SettingSelector(key_filter="*", tag_filters=["tag=value"])
        assert selector.key_filter == "*"

        selector = SettingSelector(key_filter="prefix-*", tag_filters=["tag=value"])
        assert selector.key_filter == "prefix-*"

        selector = SettingSelector(key_filter="exact-key", tag_filters=["tag=value"])
        assert selector.key_filter == "exact-key"

    def test_setting_selector_different_label_filters(self):
        """Test SettingSelector with different label filters."""
        selector = SettingSelector(key_filter="*", label_filter="prod", tag_filters=["tag=value"])
        assert selector.label_filter == "prod"

        selector = SettingSelector(key_filter="*", label_filter="", tag_filters=["tag=value"])
        assert selector.label_filter == ""

        selector = SettingSelector(key_filter="*", tag_filters=["tag=value"])
        assert selector.label_filter == NULL_CHAR
