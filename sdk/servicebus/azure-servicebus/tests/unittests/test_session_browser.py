# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Unit tests for the _SessionBrowser sentinel value and page size.

These tests verify the active-messages sentinel matches the value the service
expects, without requiring Azure credentials or a live Service Bus namespace.
"""

from azure.servicebus._session_browser import _MAX_DATETIME_MS, _PAGE_SIZE


class TestSessionBrowserSentinel:
    """Verify the active-messages sentinel value is correct.

    The service checks `lastUpdatedTime != DateTime.MaxValue` (exact equality)
    to switch between "active messages" mode and "updated since" mode. The .NET
    AMQP library (TimeStampEncoding.cs) encodes DateTime.MaxValue as
    253402300800000 ms (10000-01-01T00:00:00Z) due to double-to-long rounding
    in TimeSpan.TotalMilliseconds, and its decoder clamps values exceeding
    DateTime.MaxValue.Ticks back to DateTime.MaxValue.

    Sending 253402300799999 (1 ms less) decodes to a DateTime that is NOT
    DateTime.MaxValue, causing the service to use "updated-since" mode with
    a far-future timestamp, which returns empty results instead of sessions
    with active messages.
    """

    def test_sentinel_value_matches_dotnet_amqp_encoding_of_datetime_maxvalue(self):
        """The sentinel must be 253402300800000 — the exact ms value the .NET
        AMQP library produces for DateTime.MaxValue. Track 1 Java's
        SessionBrowser.MAXDATE = new Date(253402300800000L) uses the same
        value.
        """
        assert _MAX_DATETIME_MS == 253402300800000

    def test_sentinel_is_exactly_1ms_past_last_ms_of_year_9999(self):
        """253402300800000 is exactly 1 ms past 9999-12-31T23:59:59.999Z.

        Python's datetime can't represent year 10000, so we verify
        arithmetically that the sentinel is 253402300799999 + 1. The value
        253402300799999 would decode on the service side to a DateTime that
        is NOT DateTime.MaxValue, failing the exact-equality check.
        """
        last_ms_of_year_9999 = 253402300799999  # 9999-12-31T23:59:59.999Z
        assert _MAX_DATETIME_MS == last_ms_of_year_9999 + 1

    def test_page_size_is_100(self):
        """Default page size for get-message-sessions pagination."""
        assert _PAGE_SIZE == 100
