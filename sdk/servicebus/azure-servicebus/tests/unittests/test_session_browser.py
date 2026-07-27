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

from unittest.mock import MagicMock, patch
import asyncio
import threading
from datetime import datetime, timezone

import pytest

from azure.servicebus._session_browser import _MAX_DATETIME_MS, _PAGE_SIZE, _SessionBrowser
from azure.servicebus.aio._session_browser_async import _SessionBrowserAsync
from azure.servicebus._pyamqp.types import VALUE
from azure.servicebus.exceptions import OperationTimeoutError
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


def _paged_mgmt_stub(pages, skips):
    """Return a fake `_mgmt_request_response_with_retry` that serves `pages`
    keyed by the requested `skip`, recording each requested skip in `skips`.
    """

    def _serve(skip):
        skips.append(skip)
        return pages.get(skip, [])

    return _serve


def _live_browser(cls):
    """A browser instance whose liveness check is a no-op (not shut down).

    `list_sessions` calls `self._check_live()` before every page; bypassing
    `__init__` leaves no `_shutdown` event, so tests that exercise a live
    browser stub it out. Shutdown behavior is covered separately.
    """
    browser = object.__new__(cls)
    browser._check_live = lambda: None
    return browser


class TestListSessionsPagination:
    """Verify skip-based pagination yields every page and advances `skip`.

    Without this, a regression that truncates after the first page (e.g.
    dropping the `skip += len(result)` advance or the full-page continue) would
    still pass CI, because every live test creates at most three sessions and
    never fills a 100-item page.
    """

    def test_paginates_full_first_page_then_partial_second(self):
        page1 = [f"session-{i}" for i in range(_PAGE_SIZE)]  # full page -> fetch next
        page2 = [f"session-{i}" for i in range(_PAGE_SIZE, _PAGE_SIZE + 30)]  # partial -> stop
        skips = []
        serve = _paged_mgmt_stub({0: page1, _PAGE_SIZE: page2}, skips)

        browser = _live_browser(_SessionBrowser)
        browser._mgmt_request_response_with_retry = lambda operation, message, callback, **kwargs: serve(
            message["skip"][VALUE]
        )

        result = list(browser.list_sessions())

        assert result == page1 + page2  # every ID from both pages, in order
        assert skips == [0, _PAGE_SIZE]  # skip advanced by len(page1)=100, stopped after the partial page


class TestListSessionsPaginationAsync:
    """Async mirror of the pagination coverage above."""

    @pytest.mark.asyncio
    async def test_paginates_full_first_page_then_partial_second(self):
        page1 = [f"session-{i}" for i in range(_PAGE_SIZE)]
        page2 = [f"session-{i}" for i in range(_PAGE_SIZE, _PAGE_SIZE + 30)]
        skips = []
        serve = _paged_mgmt_stub({0: page1, _PAGE_SIZE: page2}, skips)

        async def _mgmt(operation, message, callback, **kwargs):
            return serve(message["skip"][VALUE])

        browser = _live_browser(_SessionBrowserAsync)
        browser._mgmt_request_response_with_retry = _mgmt

        result = [sid async for sid in browser.list_sessions()]

        assert result == page1 + page2
        assert skips == [0, _PAGE_SIZE]


class TestListSessionsTimeoutBudget:
    """`timeout` is a single total budget spent across all pages, not reset per page."""

    def test_timeout_shrinks_across_pages(self):
        page1 = [f"session-{i}" for i in range(_PAGE_SIZE)]
        page2 = [f"session-{i}" for i in range(_PAGE_SIZE, _PAGE_SIZE + 5)]
        pages = {0: page1, _PAGE_SIZE: page2}
        seen = []

        def serve(operation, message, callback, **kwargs):
            seen.append(kwargs.get("timeout"))
            return pages.get(message["skip"][VALUE], [])

        browser = _live_browser(_SessionBrowser)
        browser._mgmt_request_response_with_retry = serve
        # monotonic() is called once for the deadline, then once per page.
        # base 1000 -> deadline 1010; page 1 at 1000 -> 10 left; page 2 at 1003 -> 7 left.
        clock = iter([1000.0, 1000.0, 1003.0])
        with patch("azure.servicebus._session_browser.time.monotonic", lambda: next(clock)):
            list(browser.list_sessions(timeout=10))

        # A per-page timeout would record [10, 10]; a shared budget shrinks.
        assert seen == [10.0, 7.0]

    def test_exhausted_budget_raises_before_next_page(self):
        browser = _live_browser(_SessionBrowser)

        def _should_not_run(*args, **kwargs):
            raise AssertionError("management request should not be issued after the budget is spent")

        browser._mgmt_request_response_with_retry = _should_not_run
        # base 1000 -> deadline 1005; first page check at 1006 -> -1 remaining -> raise.
        clock = iter([1000.0, 1006.0])
        with patch("azure.servicebus._session_browser.time.monotonic", lambda: next(clock)):
            with pytest.raises(OperationTimeoutError):
                list(browser.list_sessions(timeout=5))


def _capture_last_updated_ms(browser):
    """Run one page and return the `last-updated-time` ms value sent on the wire."""
    captured = {}

    def _serve(operation, message, callback, **kwargs):
        captured["ms"] = message["last-updated-time"][VALUE]
        return []

    browser._mgmt_request_response_with_retry = _serve
    return captured


class TestUpdatedAfterSentinelBoundary:
    """An explicit filter timestamp must never collide with the active-messages sentinel.

    `datetime.max` in UTC is 1 ms below `_MAX_DATETIME_MS`. Float `timestamp() * 1000`
    rounds it up onto the sentinel, which would silently switch the request into
    active-messages mode. Integer arithmetic must keep it at `_MAX_DATETIME_MS - 1`.
    """

    def test_datetime_max_stays_below_sentinel(self):
        browser = _live_browser(_SessionBrowser)
        captured = _capture_last_updated_ms(browser)
        list(browser.list_sessions(state_updated_after=datetime.max.replace(tzinfo=timezone.utc)))
        assert captured["ms"] == _MAX_DATETIME_MS - 1
        assert captured["ms"] != _MAX_DATETIME_MS

    @pytest.mark.asyncio
    async def test_datetime_max_stays_below_sentinel_async(self):
        browser = _live_browser(_SessionBrowserAsync)
        captured = {}

        async def _serve(operation, message, callback, **kwargs):
            captured["ms"] = message["last-updated-time"][VALUE]
            return []

        browser._mgmt_request_response_with_retry = _serve
        _ = [sid async for sid in browser.list_sessions(
            state_updated_after=datetime.max.replace(tzinfo=timezone.utc))]
        assert captured["ms"] == _MAX_DATETIME_MS - 1
        assert captured["ms"] != _MAX_DATETIME_MS


class TestBrowserShutdownGuard:
    """A paused iterator must not reopen a connection after the client is closed."""

    def test_shutdown_browser_does_not_request_pages(self):
        browser = object.__new__(_SessionBrowser)
        browser._shutdown = threading.Event()
        browser._shutdown.set()
        requested = []
        browser._mgmt_request_response_with_retry = lambda *a, **k: requested.append(1) or []

        with pytest.raises(ValueError, match="already been shutdown"):
            list(browser.list_sessions())
        assert requested == []  # no page request issued after shutdown

    @pytest.mark.asyncio
    async def test_shutdown_browser_does_not_request_pages_async(self):
        browser = object.__new__(_SessionBrowserAsync)
        browser._shutdown = asyncio.Event()
        browser._shutdown.set()
        requested = []

        async def _mgmt(*a, **k):
            requested.append(1)
            return []

        browser._mgmt_request_response_with_retry = _mgmt
        with pytest.raises(ValueError, match="already been shutdown"):
            _ = [sid async for sid in browser.list_sessions()]
        assert requested == []


