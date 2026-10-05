# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Unit tests for the _SessionBrowser sentinel value, page size, and
management response handling.

These tests verify the default-listing sentinel matches the value the service
expects, and that the list_sessions_op handler covers all response branches,
without requiring Azure credentials or a live Service Bus namespace.
"""

from unittest.mock import MagicMock
import asyncio
import threading
from datetime import datetime, timezone

import pytest

from azure.servicebus._session_browser import (
    _MAX_DATETIME_MS,
    _PAGE_SIZE,
    _SessionBrowser,
    _page_request_body,
    _to_last_updated_ms,
)
from azure.servicebus.aio._session_browser_async import _SessionBrowserAsync
from azure.servicebus._pyamqp.types import AMQPTypes, TYPE, VALUE
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.exceptions import OperationTimeoutError
from azure.servicebus._common.mgmt_handlers import list_sessions_op
from azure.servicebus._common.constants import (
    ERROR_CODE_MESSAGE_NOT_FOUND,
    MGMT_RESPONSE_MESSAGE_ERROR_CONDITION,
)


class TestSessionBrowserSentinel:
    """Verify the default-listing sentinel value is correct.

    The service checks `lastUpdatedTime != DateTime.MaxValue` (exact equality)
    to switch between default listing mode and updated-since mode. The default
    listing mode returns sessions with active messages or stored session state. The .NET
    AMQP library (TimeStampEncoding.cs) encodes DateTime.MaxValue as
    253402300800000 ms (10000-01-01T00:00:00Z) due to double-to-long rounding
    in TimeSpan.TotalMilliseconds, and its decoder clamps values exceeding
    DateTime.MaxValue.Ticks back to DateTime.MaxValue.

    Sending 253402300799999 (1 ms less) decodes to a DateTime that is NOT
    DateTime.MaxValue, causing the service to use "updated-since" mode with
    a far-future timestamp, which returns empty results instead of sessions
    with active messages or stored session state.
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

    def test_200_decodes_session_ids_from_utf8_bytes(self):
        """200 decodes each `sessions-ids` byte value from UTF-8 to str.

        The live tests carry `live_test_only` and skip in playback CI, so this
        mocked case guards the branch that reads
        `get_message_value(message)[b"sessions-ids"]` and decodes UTF-8 - a byte
        key and encoding that are easy to break silently.
        """
        msg = self._make_message(
            {}, value={b"sessions-ids": [b"session-a", "se\u00f1or".encode("utf-8")]}
        )
        transport = self._make_transport()
        result = list_sessions_op(200, msg, None, transport)
        assert result == ["session-a", "se\u00f1or"]
        transport.handle_amqp_mgmt_error.assert_not_called()

    def test_200_empty_sessions_ids_returns_empty_list(self):
        """200 with an empty `sessions-ids` list returns an empty list."""
        msg = self._make_message({}, value={b"sessions-ids": []})
        transport = self._make_transport()
        result = list_sessions_op(200, msg, None, transport)
        assert result == []
        transport.handle_amqp_mgmt_error.assert_not_called()

    def test_202_204_return_empty_list(self):
        """202/204 (no sessions match the query) returns an empty list."""
        transport = self._make_transport()
        for status_code in (202, 204):
            msg = self._make_message({})
            result = list_sessions_op(status_code, msg, None, transport)
            assert result == []
        transport.handle_amqp_mgmt_error.assert_not_called()


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
    browser stub it out. It also builds each page body through the transport
    value factories and closes the browser on the terminal page, so a real
    `PyamqpTransport` is attached and `close` is stubbed. Shutdown behavior is
    covered separately.
    """
    browser = object.__new__(cls)
    browser._check_live = lambda: None
    browser._amqp_transport = PyamqpTransport
    if "Async" in cls.__name__:

        async def _noop_close():
            return None

        browser.close = _noop_close
    else:
        browser.close = lambda: None
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
        page2 = [
            f"session-{i}" for i in range(_PAGE_SIZE, _PAGE_SIZE + 30)
        ]  # partial -> stop
        skips = []
        serve = _paged_mgmt_stub({0: page1, _PAGE_SIZE: page2}, skips)

        browser = _live_browser(_SessionBrowser)
        browser._mgmt_request_response_with_retry = (
            lambda operation, message, callback, **kwargs: serve(message["skip"][VALUE])
        )

        result = list(browser.list_sessions())

        assert result == page1 + page2  # every ID from both pages, in order
        assert skips == [
            0,
            _PAGE_SIZE,
        ]  # skip advanced by len(page1)=100, stopped after the partial page


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
        # The deadline is established on the first page fetch, then shared.
        # monotonic() is called twice on the first page (set deadline, then
        # remaining), and once per subsequent page. base 1000 -> deadline 1010;
        # page 1 at 1000 -> 10 left; page 2 at 1003 -> 7 left.
        clock = iter([1000.0, 1000.0, 1003.0])
        list(browser.list_sessions(timeout=10, _now=lambda: next(clock)))

        # A per-page timeout would record [10, 10]; a shared budget shrinks.
        assert seen == [10.0, 7.0]

    def test_exhausted_budget_raises_before_next_page(self):
        browser = _live_browser(_SessionBrowser)

        def _should_not_run(*args, **kwargs):
            raise AssertionError(
                "management request should not be issued after the budget is spent"
            )

        browser._mgmt_request_response_with_retry = _should_not_run
        # base 1000 -> deadline 1005; first page check at 1006 -> -1 remaining -> raise.
        clock = iter([1000.0, 1006.0])
        with pytest.raises(OperationTimeoutError):
            list(browser.list_sessions(timeout=5, _now=lambda: next(clock)))


class TestListSessionsTimeoutBudgetAsync:
    """Async mirror of the total-budget timeout coverage above.

    `aio/_session_browser_async.py` carries its own copy of the deadline
    arithmetic, so it needs its own coverage.
    """

    @pytest.mark.asyncio
    async def test_timeout_shrinks_across_pages(self):
        page1 = [f"session-{i}" for i in range(_PAGE_SIZE)]
        page2 = [f"session-{i}" for i in range(_PAGE_SIZE, _PAGE_SIZE + 5)]
        pages = {0: page1, _PAGE_SIZE: page2}
        seen = []

        async def serve(operation, message, callback, **kwargs):
            seen.append(kwargs.get("timeout"))
            return pages.get(message["skip"][VALUE], [])

        browser = _live_browser(_SessionBrowserAsync)
        browser._mgmt_request_response_with_retry = serve
        clock = iter([1000.0, 1000.0, 1003.0])
        _ = [
            sid
            async for sid in browser.list_sessions(timeout=10, _now=lambda: next(clock))
        ]

        assert seen == [10.0, 7.0]

    @pytest.mark.asyncio
    async def test_exhausted_budget_raises_before_next_page(self):
        browser = _live_browser(_SessionBrowserAsync)

        async def _should_not_run(*args, **kwargs):
            raise AssertionError(
                "management request should not be issued after the budget is spent"
            )

        browser._mgmt_request_response_with_retry = _should_not_run
        clock = iter([1000.0, 1006.0])
        with pytest.raises(OperationTimeoutError):
            _ = [
                sid
                async for sid in browser.list_sessions(
                    timeout=5, _now=lambda: next(clock)
                )
            ]


def _capture_last_updated_ms(browser):
    """Run one page and return the `last-updated-time` ms value sent on the wire."""
    captured = {}

    def _serve(operation, message, callback, **kwargs):
        captured["ms"] = message["last-updated-time"][VALUE]
        return []

    browser._mgmt_request_response_with_retry = _serve
    return captured


class TestUpdatedAfterSentinelBoundary:
    """An explicit filter timestamp must never collide with the default-listing sentinel.

    `datetime.max` in UTC is 1 ms below `_MAX_DATETIME_MS`. Float `timestamp() * 1000`
    rounds it up onto the sentinel, which would silently switch the request into
    default listing mode. Integer arithmetic must keep it at `_MAX_DATETIME_MS - 1`.
    """

    def test_datetime_max_stays_below_sentinel(self):
        browser = _live_browser(_SessionBrowser)
        captured = _capture_last_updated_ms(browser)
        list(
            browser.list_sessions(
                state_updated_after=datetime.max.replace(tzinfo=timezone.utc)
            )
        )
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
        _ = [
            sid
            async for sid in browser.list_sessions(
                state_updated_after=datetime.max.replace(tzinfo=timezone.utc)
            )
        ]
        assert captured["ms"] == _MAX_DATETIME_MS - 1
        assert captured["ms"] != _MAX_DATETIME_MS


class TestPageRequestBody:
    """The request body is built with transport-neutral value factories, so both
    the pyamqp and uamqp encoders tag each field with its AMQP type.

    A hand-built pyamqp typed dict is passed through untouched by uamqp and
    encoded as a nested map, so the service would receive a map where it expects
    a timestamp and two ints. These tests pin the pyamqp shape; the uamqp shape
    is validated against the real uamqp encoder out of band.
    """

    def test_body_tags_each_field_with_its_amqp_type(self):
        body = _page_request_body(PyamqpTransport, _MAX_DATETIME_MS, skip=42)
        assert body["last-updated-time"][TYPE] == AMQPTypes.timestamp
        assert body["last-updated-time"][VALUE] == _MAX_DATETIME_MS
        assert body["skip"][TYPE] == AMQPTypes.int
        assert body["skip"][VALUE] == 42
        assert body["top"][TYPE] == AMQPTypes.int
        assert body["top"][VALUE] == _PAGE_SIZE

    def test_wire_body_is_typed_on_every_page(self):
        """Each page issued by `list_sessions` carries the typed body, not a
        plain dict."""
        page1 = [f"session-{i}" for i in range(_PAGE_SIZE)]
        page2 = [f"session-{i}" for i in range(_PAGE_SIZE, _PAGE_SIZE + 3)]
        pages = {0: page1, _PAGE_SIZE: page2}
        bodies = []

        def serve(operation, message, callback, **kwargs):
            bodies.append(message)
            return pages.get(message["skip"][VALUE], [])

        browser = _live_browser(_SessionBrowser)
        browser._mgmt_request_response_with_retry = serve
        list(browser.list_sessions())

        assert len(bodies) == 2
        for body in bodies:
            assert body["last-updated-time"][TYPE] == AMQPTypes.timestamp
            assert body["skip"][TYPE] == AMQPTypes.int
            assert body["top"][TYPE] == AMQPTypes.int


class TestToLastUpdatedMs:
    """The shared `_to_last_updated_ms` helper is used by both the sync and async
    browsers, so a drift between the two copies cannot change the query mode."""

    def test_none_returns_default_listing_sentinel(self):
        assert _to_last_updated_ms(None) == _MAX_DATETIME_MS

    def test_naive_datetime_is_treated_as_utc(self):
        naive = datetime(2026, 1, 1, 0, 0, 0)
        aware = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert _to_last_updated_ms(naive) == _to_last_updated_ms(aware)

    def test_epoch_is_zero(self):
        assert _to_last_updated_ms(datetime(1970, 1, 1, tzinfo=timezone.utc)) == 0


class TestListSessionsPaged:
    """`list_sessions` returns an `ItemPaged`, so `by_page()` and the
    continuation token are available per the Python paging guideline."""

    def test_by_page_yields_each_page_and_continuation_token(self):
        page1 = [f"session-{i}" for i in range(_PAGE_SIZE)]
        page2 = [f"session-{i}" for i in range(_PAGE_SIZE, _PAGE_SIZE + 4)]
        pages = {0: page1, _PAGE_SIZE: page2}

        def serve(operation, message, callback, **kwargs):
            return pages.get(message["skip"][VALUE], [])

        browser = _live_browser(_SessionBrowser)
        browser._mgmt_request_response_with_retry = serve

        pager = browser.list_sessions().by_page()
        first_page = list(next(pager))
        assert first_page == page1
        second_page = list(next(pager))
        assert second_page == page2
        with pytest.raises(StopIteration):
            next(pager)


class TestBrowserEagerClose:
    """The connection is released eagerly on the terminal page, and not before.

    Without this coverage, dropping the terminal-page `self.close()` from
    `_extract_data` (a connection leak) would pass the whole suite.
    """

    def test_close_called_once_on_terminal_page_only(self):
        page1 = [f"session-{i}" for i in range(_PAGE_SIZE)]  # full -> continue
        page2 = [
            f"session-{i}" for i in range(_PAGE_SIZE, _PAGE_SIZE + 3)
        ]  # partial -> close
        pages = {0: page1, _PAGE_SIZE: page2}
        close_calls = []

        browser = object.__new__(_SessionBrowser)
        browser._check_live = lambda: None
        browser._amqp_transport = PyamqpTransport
        browser.close = lambda: close_calls.append(1)
        browser._mgmt_request_response_with_retry = (
            lambda operation, message, callback, **kwargs: pages.get(
                message["skip"][VALUE], []
            )
        )

        pager = browser.list_sessions().by_page()
        list(next(pager))  # full first page
        assert close_calls == []  # not closed mid-enumeration
        list(next(pager))  # terminal partial page
        assert close_calls == [1]  # closed exactly once, eagerly
        with pytest.raises(StopIteration):
            next(pager)
        assert close_calls == [1]  # not closed again

    def test_close_not_called_when_pager_abandoned_early(self):
        """A caller that stops after the first full page does not trigger the
        eager terminal-page close (cleanup then falls to the client / GC)."""
        page1 = [f"session-{i}" for i in range(_PAGE_SIZE)]  # full -> would continue
        page2 = [f"session-{i}" for i in range(_PAGE_SIZE, _PAGE_SIZE + 3)]
        pages = {0: page1, _PAGE_SIZE: page2}
        close_calls = []

        browser = object.__new__(_SessionBrowser)
        browser._check_live = lambda: None
        browser._amqp_transport = PyamqpTransport
        browser.close = lambda: close_calls.append(1)
        browser._mgmt_request_response_with_retry = (
            lambda operation, message, callback, **kwargs: pages.get(
                message["skip"][VALUE], []
            )
        )

        pager = browser.list_sessions().by_page()
        list(next(pager))  # consume only the first full page, then abandon
        assert close_calls == []

    @pytest.mark.asyncio
    async def test_close_called_once_on_terminal_page_only_async(self):
        page1 = [f"session-{i}" for i in range(_PAGE_SIZE)]
        page2 = [f"session-{i}" for i in range(_PAGE_SIZE, _PAGE_SIZE + 3)]
        pages = {0: page1, _PAGE_SIZE: page2}
        close_calls = []

        browser = object.__new__(_SessionBrowserAsync)
        browser._check_live = lambda: None
        browser._amqp_transport = PyamqpTransport

        async def _close():
            close_calls.append(1)

        browser.close = _close

        async def _mgmt(operation, message, callback, **kwargs):
            return pages.get(message["skip"][VALUE], [])

        browser._mgmt_request_response_with_retry = _mgmt

        pager = browser.list_sessions().by_page()
        [x async for x in await pager.__anext__()]  # full first page
        assert close_calls == []
        [x async for x in await pager.__anext__()]  # terminal partial page
        assert close_calls == [1]
        with pytest.raises(StopAsyncIteration):
            await pager.__anext__()
        assert close_calls == [1]


class TestBrowserShutdownGuard:
    """A paused iterator must not reopen a connection after the client is closed."""

    def test_shutdown_browser_does_not_request_pages(self):
        browser = object.__new__(_SessionBrowser)
        browser._shutdown = threading.Event()
        browser._shutdown.set()
        requested = []
        browser._mgmt_request_response_with_retry = (
            lambda *a, **k: requested.append(1) or []
        )

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
