# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Unit tests for the _SessionBrowser sentinel value, page size, and
management response handling.

These tests verify the active-messages sentinel matches the value the service
expects, and that the list_sessions_op handler covers all response branches,
without requiring Azure credentials or a live Service Bus namespace.
"""

from unittest.mock import MagicMock

from azure.servicebus._session_browser import _MAX_DATETIME_MS, _PAGE_SIZE
from azure.servicebus._common.mgmt_handlers import list_sessions_op
from azure.servicebus._common.constants import (
    ERROR_CODE_MESSAGE_NOT_FOUND,
    MGMT_RESPONSE_MESSAGE_ERROR_CONDITION,
)


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


class TestListSessionsOpHandler:
    """Verify the list_sessions_op management-response handler covers all branches.

    The handler recognises three success-like status codes:
      - 200: sessions found (parse and return).
      - 202/204: no sessions match (return empty list).
      - 404 + com.microsoft:message-not-found: cross-SDK safety net (return empty list).

    The 404 branch is not currently emitted by the service for get-message-sessions,
    but .NET carries the same guard. This test ensures the branch is exercised so
    it doesn't silently rot.
    """

    @staticmethod
    def _make_message(application_properties, value=None):
        msg = MagicMock()
        msg.application_properties = application_properties
        msg.value = value
        return msg

    @staticmethod
    def _make_transport():
        transport = MagicMock()
        transport.get_message_value = lambda m: m.value
        transport.handle_amqp_mgmt_error = MagicMock()
        return transport

    def test_404_message_not_found_returns_empty_list(self):
        """404 + message-not-found returns an empty list (cross-SDK safety net)."""
        msg = self._make_message(
            {MGMT_RESPONSE_MESSAGE_ERROR_CONDITION: ERROR_CODE_MESSAGE_NOT_FOUND}
        )
        transport = self._make_transport()
        result = list_sessions_op(404, msg, "Not found", transport)
        assert result == []
        transport.handle_amqp_mgmt_error.assert_not_called()

    def test_404_other_condition_raises(self):
        """404 with a different condition code falls through to the error handler."""
        msg = self._make_message(
            {MGMT_RESPONSE_MESSAGE_ERROR_CONDITION: b"com.microsoft:other-error"}
        )
        transport = self._make_transport()
        list_sessions_op(404, msg, "Not found", transport)
        transport.handle_amqp_mgmt_error.assert_called_once()
