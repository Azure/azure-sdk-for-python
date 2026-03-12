# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""Unit tests for ContentRange."""

import pytest
from datetime import timedelta
from azure.ai.contentunderstanding.models import ContentRange, AnalysisInput


class TestContentRangeConstructor:
    """Tests for ContentRange constructor."""

    def test_constructor_with_value_stores_value(self):
        cr = ContentRange("1-3")
        assert str(cr) == "1-3"

    def test_constructor_none_value_raises(self):
        with pytest.raises(ValueError):
            ContentRange(None)  # type: ignore


class TestContentRangePageMethods:
    """Tests for page-related factory methods."""

    def test_page_valid_page_number(self):
        cr = ContentRange.page(5)
        assert str(cr) == "5"

    def test_page_page_one(self):
        cr = ContentRange.page(1)
        assert str(cr) == "1"

    def test_page_zero_raises(self):
        with pytest.raises(ValueError):
            ContentRange.page(0)

    def test_page_negative_raises(self):
        with pytest.raises(ValueError):
            ContentRange.page(-1)

    def test_pages_valid_range(self):
        cr = ContentRange.pages(1, 3)
        assert str(cr) == "1-3"

    def test_pages_same_start_and_end(self):
        cr = ContentRange.pages(5, 5)
        assert str(cr) == "5-5"

    def test_pages_zero_start_raises(self):
        with pytest.raises(ValueError):
            ContentRange.pages(0, 3)

    def test_pages_end_before_start_raises(self):
        with pytest.raises(ValueError):
            ContentRange.pages(5, 3)

    def test_pages_from_valid(self):
        cr = ContentRange.pages_from(9)
        assert str(cr) == "9-"

    def test_pages_from_zero_raises(self):
        with pytest.raises(ValueError):
            ContentRange.pages_from(0)


class TestContentRangeTimeMethods:
    """Tests for time-related factory methods."""

    def test_time_range_valid(self):
        cr = ContentRange.time_range(timedelta(0), timedelta(milliseconds=5000))
        assert str(cr) == "0-5000"

    def test_time_range_same_start_and_end(self):
        cr = ContentRange.time_range(
            timedelta(milliseconds=1000), timedelta(milliseconds=1000)
        )
        assert str(cr) == "1000-1000"

    def test_time_range_negative_start_raises(self):
        with pytest.raises(ValueError):
            ContentRange.time_range(
                timedelta(milliseconds=-1), timedelta(milliseconds=5000)
            )

    def test_time_range_end_before_start_raises(self):
        with pytest.raises(ValueError):
            ContentRange.time_range(
                timedelta(milliseconds=5000), timedelta(milliseconds=1000)
            )

    def test_time_range_from_valid(self):
        cr = ContentRange.time_range_from(timedelta(milliseconds=5000))
        assert str(cr) == "5000-"

    def test_time_range_from_zero(self):
        cr = ContentRange.time_range_from(timedelta(0))
        assert str(cr) == "0-"

    def test_time_range_from_negative_raises(self):
        with pytest.raises(ValueError):
            ContentRange.time_range_from(timedelta(milliseconds=-1))

    def test_time_range_seconds(self):
        cr = ContentRange.time_range(timedelta(0), timedelta(seconds=5))
        assert str(cr) == "0-5000"

    def test_time_range_minutes(self):
        cr = ContentRange.time_range(timedelta(0), timedelta(minutes=1))
        assert str(cr) == "0-60000"


class TestContentRangeCombine:
    """Tests for combine factory method."""

    def test_combine_multiple_ranges(self):
        combined = ContentRange.combine(
            ContentRange.pages(1, 3), ContentRange.page(5), ContentRange.pages_from(9)
        )
        assert str(combined) == "1-3,5,9-"

    def test_combine_single_range(self):
        combined = ContentRange.combine(ContentRange.page(1))
        assert str(combined) == "1"

    def test_combine_empty_raises(self):
        with pytest.raises(ValueError):
            ContentRange.combine()


class TestContentRangeEquality:
    """Tests for equality operations."""

    def test_equals_same_value(self):
        r1 = ContentRange.pages(1, 3)
        r2 = ContentRange("1-3")
        assert r1 == r2

    def test_equals_different_value(self):
        r1 = ContentRange.pages(1, 3)
        r2 = ContentRange.pages(1, 5)
        assert r1 != r2

    def test_hash_equal_for_same_values(self):
        r1 = ContentRange.pages(1, 3)
        r2 = ContentRange("1-3")
        assert hash(r1) == hash(r2)

    def test_hash_different_for_different_values(self):
        r1 = ContentRange.pages(1, 3)
        r2 = ContentRange.pages(1, 5)
        assert hash(r1) != hash(r2)

    def test_equals_non_content_range_returns_not_implemented(self):
        r1 = ContentRange.pages(1, 3)
        assert r1 != "1-3"  # Different type


class TestContentRangeStr:
    """Tests for string conversion."""

    def test_str(self):
        cr = ContentRange.pages(1, 3)
        assert str(cr) == "1-3"

    def test_repr(self):
        cr = ContentRange.pages(1, 3)
        assert repr(cr) == "ContentRange('1-3')"


class TestAnalysisInputContentRange:
    """Tests for ContentRange integration with AnalysisInput."""

    def test_analysis_input_accepts_content_range_string(self):
        ai = AnalysisInput(content_range="1-3")
        assert ai.content_range == "1-3"

    def test_analysis_input_content_range_none_by_default(self):
        ai = AnalysisInput()
        assert ai.content_range is None
