# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""ContentRange value type for specifying content ranges on AnalysisInput."""

from datetime import timedelta
from typing import Optional


class ContentRange:
    """Represents a range of content to analyze.

    For documents, ranges use 1-based page numbers (e.g., ``"1-3"``, ``"5"``, ``"9-"``).
    For audio/video, ranges use integer milliseconds (e.g., ``"0-5000"``, ``"5000-"``).
    Multiple ranges can be combined with commas (e.g., ``"1-3,5,9-"``).

    Example usage::

        # Document pages
        range = ContentRange.page(5)                    # "5"
        range = ContentRange.pages(1, 3)                # "1-3"
        range = ContentRange.pages_from(9)              # "9-"

        # Audio/video time ranges
        range = ContentRange.time_range(
            timedelta(0), timedelta(seconds=5))         # "0-5000"
        range = ContentRange.time_range_from(
            timedelta(seconds=5))                       # "5000-"

        # Combine multiple ranges
        range = ContentRange.combine(
            ContentRange.pages(1, 3),
            ContentRange.page(5),
            ContentRange.pages_from(9))                 # "1-3,5,9-"

        # Or construct from a raw string
        range = ContentRange("1-3,5,9-")
    """

    def __init__(self, value: str) -> None:
        """Initialize a new ContentRange.

        :param value: The range string value.
        :type value: str
        :raises ValueError: If value is None or empty.
        """
        if value is None:
            raise ValueError("value cannot be None.")
        self._value = value

    @classmethod
    def page(cls, page_number: int) -> "ContentRange":
        """Create a ContentRange for a single document page (1-based).

        :param page_number: The 1-based page number.
        :type page_number: int
        :return: A ContentRange representing a single page, e.g. ``"5"``.
        :rtype: ~azure.ai.contentunderstanding.models.ContentRange
        :raises ValueError: If page_number is less than 1.
        """
        if page_number < 1:
            raise ValueError("Page number must be >= 1.")
        return cls(str(page_number))

    @classmethod
    def pages(cls, start: int, end: int) -> "ContentRange":
        """Create a ContentRange for a contiguous range of document pages (1-based, inclusive).

        :param start: The 1-based start page number (inclusive).
        :type start: int
        :param end: The 1-based end page number (inclusive).
        :type end: int
        :return: A ContentRange representing the page range, e.g. ``"1-3"``.
        :rtype: ~azure.ai.contentunderstanding.models.ContentRange
        :raises ValueError: If start is less than 1, or end is less than start.
        """
        if start < 1:
            raise ValueError("Start page must be >= 1.")
        if end < start:
            raise ValueError("End page must be >= start page.")
        return cls(f"{start}-{end}")

    @classmethod
    def pages_from(cls, start_page: int) -> "ContentRange":
        """Create a ContentRange for all pages from a starting page to the end (1-based).

        :param start_page: The 1-based start page number (inclusive).
        :type start_page: int
        :return: A ContentRange representing the open-ended range, e.g. ``"9-"``.
        :rtype: ~azure.ai.contentunderstanding.models.ContentRange
        :raises ValueError: If start_page is less than 1.
        """
        if start_page < 1:
            raise ValueError("Start page must be >= 1.")
        return cls(f"{start_page}-")

    @classmethod
    def _time_range_ms(cls, start_ms: int, end_ms: int) -> "ContentRange":
        """Create a ContentRange for a time range in milliseconds (for audio/video).

        :param start_ms: The start time in milliseconds (inclusive).
        :type start_ms: int
        :param end_ms: The end time in milliseconds (inclusive).
        :type end_ms: int
        :return: A ContentRange representing the time range.
        :rtype: ~azure.ai.contentunderstanding.models.ContentRange
        :raises ValueError: If start_ms is negative or end_ms is less than start_ms.
        """
        if start_ms < 0:
            raise ValueError("Start time must be >= 0.")
        if end_ms < start_ms:
            raise ValueError("End time must be >= start time.")
        return cls(f"{start_ms}-{end_ms}")

    @classmethod
    def _time_range_from_ms(cls, start_ms: int) -> "ContentRange":
        """Create a ContentRange from a starting time to the end in milliseconds.

        :param start_ms: The start time in milliseconds (inclusive).
        :type start_ms: int
        :return: A ContentRange representing the open-ended time range.
        :rtype: ~azure.ai.contentunderstanding.models.ContentRange
        :raises ValueError: If start_ms is negative.
        """
        if start_ms < 0:
            raise ValueError("Start time must be >= 0.")
        return cls(f"{start_ms}-")

    @classmethod
    def time_range(cls, start: timedelta, end: timedelta) -> "ContentRange":
        """Create a ContentRange for a time range (for audio/video content).

        :param start: The start time (inclusive).
        :type start: ~datetime.timedelta
        :param end: The end time (inclusive).
        :type end: ~datetime.timedelta
        :return: A ContentRange representing the time range, e.g. ``"0-5000"``.
        :rtype: ~azure.ai.contentunderstanding.models.ContentRange
        :raises ValueError: If start is negative, or end is less than start.
        """
        if start < timedelta(0):
            raise ValueError("Start time must be non-negative.")
        if end < start:
            raise ValueError("End time must be >= start time.")
        return cls._time_range_ms(
            int(start.total_seconds() * 1000), int(end.total_seconds() * 1000)
        )

    @classmethod
    def time_range_from(cls, start: timedelta) -> "ContentRange":
        """Create a ContentRange from a starting time to the end (for audio/video content).

        :param start: The start time (inclusive).
        :type start: ~datetime.timedelta
        :return: A ContentRange representing the open-ended time range, e.g. ``"5000-"``.
        :rtype: ~azure.ai.contentunderstanding.models.ContentRange
        :raises ValueError: If start is negative.
        """
        if start < timedelta(0):
            raise ValueError("Start time must be non-negative.")
        return cls._time_range_from_ms(int(start.total_seconds() * 1000))

    @classmethod
    def combine(cls, *ranges: "ContentRange") -> "ContentRange":
        """Combine multiple ContentRange values into a single comma-separated range.

        :param ranges: The ranges to combine.
        :type ranges: ~azure.ai.contentunderstanding.models.ContentRange
        :return: A ContentRange representing the combined ranges, e.g. ``"1-3,5,9-"``.
        :rtype: ~azure.ai.contentunderstanding.models.ContentRange
        :raises ValueError: If no ranges are provided.
        """
        if not ranges:
            raise ValueError("At least one range must be provided.")
        return cls(",".join(r._value for r in ranges))

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"ContentRange({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ContentRange):
            return self._value == other._value
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, ContentRange):
            return self._value != other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)
