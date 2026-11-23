# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for AGENTSERVER_FLUSH_MODE dispatch on the response hot path."""

from unittest import mock

import pytest

from azure.ai.agentserver.responses.hosting import _endpoint_handler as eh


_MODE_TO_HELPER = {
    "flush_spans": "sync flush",
    "schedule_flush_spans": "background flush",
    "flush_spans_async": "async flush",
}


@pytest.fixture(autouse=True)
def _clear_invalid_flush_modes() -> None:
    with eh._flush_mode_lock:
        eh._invalid_flush_modes_warned.clear()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode, expected_helper",
    [
        # sync
        ("sync", "flush_spans"),
        ("SYNC", "flush_spans"),
        ("  sync  ", "flush_spans"),
        # background
        ("background", "schedule_flush_spans"),
        ("Background", "schedule_flush_spans"),
        # async (explicit opt-in)
        ("async", "flush_spans_async"),
        ("ASYNC", "flush_spans_async"),
        # fallback to the background default for empty / unknown values
        ("", "schedule_flush_spans"),
        ("   ", "schedule_flush_spans"),
        ("bogus", "schedule_flush_spans"),
        ("background-disabled", "schedule_flush_spans"),
    ],
)
async def test_flush_mode_dispatch(mode: str, expected_helper: str) -> None:
    """Each mode routes to exactly one helper; case/whitespace-insensitive."""
    with mock.patch.object(eh, "flush_spans") as m_sync, mock.patch.object(
        eh, "schedule_flush_spans"
    ) as m_bg, mock.patch.object(
        eh, "flush_spans_async", new_callable=mock.AsyncMock
    ) as m_async:
        await eh._flush_spans_for_mode(mode)

    called = {
        "flush_spans": m_sync.called,
        "schedule_flush_spans": m_bg.called,
        "flush_spans_async": m_async.called,
    }
    assert called[expected_helper] is True, f"{expected_helper} not called for {mode!r}"
    for helper, was_called in called.items():
        if helper != expected_helper:
            assert was_called is False, f"{helper} unexpectedly called for {mode!r}"


@pytest.mark.asyncio
async def test_flush_mode_dispatch_awaits_async_helper() -> None:
    """The explicit async path is actually awaited (not fire-and-forget)."""
    with mock.patch.object(eh, "flush_spans"), mock.patch.object(
        eh, "schedule_flush_spans"
    ), mock.patch.object(
        eh, "flush_spans_async", new_callable=mock.AsyncMock
    ) as m_async:
        await eh._flush_spans_for_mode("async")
    m_async.assert_awaited_once()


@pytest.mark.asyncio
async def test_invalid_flush_mode_warns_once(caplog: pytest.LogCaptureFixture) -> None:
    """Repeated requests with the same invalid mode emit one warning."""
    with mock.patch.object(eh, "schedule_flush_spans"):
        await eh._flush_spans_for_mode("invalid-mode")
        await eh._flush_spans_for_mode(" INVALID-MODE ")

    warnings = [record for record in caplog.records if record.levelname == "WARNING"]
    assert len(warnings) == 1
    assert "falling back to 'background' flush mode" in warnings[0].getMessage()
