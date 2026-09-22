# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from __future__ import annotations

import logging
import re

import pytest

from azure.ai.finetuningsessions import _patch as _patch_mod
from azure.ai.finetuningsessions._patch import (
    _POLL_LOG_DEDUP_SEC,
    _clear_poll_log_state,
    _maybe_log_poll_progress,
)

_LOGGER_NAME = "azure.ai.finetuningsessions._patch"
_RESUMING = {"status": "pending", "phase": "resuming_session"}
_GENERIC_PENDING = {"status": "pending"}


@pytest.fixture(autouse=True)
def _reset_dedup_state():
    _patch_mod._poll_log_last.clear()
    _patch_mod._request_active_since.clear()
    _patch_mod._poll_warn_last.clear()
    yield
    _patch_mod._poll_log_last.clear()
    _patch_mod._request_active_since.clear()
    _patch_mod._poll_warn_last.clear()


@pytest.fixture
def clock(monkeypatch):
    class _Clock:
        now: float = 1000.0

    c = _Clock()
    monkeypatch.setattr(_patch_mod._time, "monotonic", lambda: c.now)
    return c


def _call(envelope=_GENERIC_PENDING, *, op_type="sample", elapsed=None):
    if elapsed is None:
        elapsed = _POLL_LOG_DEDUP_SEC + 1.0
    _maybe_log_poll_progress(
        envelope,
        session_id="sess-1",
        request_id="req-1",
        op_type=op_type,
        elapsed=elapsed,
    )


def _records(caplog):
    return [r for r in caplog.records if r.name == _LOGGER_NAME]


def test_logs_queued_message_on_resuming_session(caplog, clock):
    elapsed = _POLL_LOG_DEDUP_SEC + 1.0
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _call(_RESUMING, elapsed=elapsed)
    [rec] = _records(caplog)
    msg = rec.getMessage()
    assert "sess-1" in msg and "req-1" in msg and "sample" in msg
    assert "[poller]" in msg
    assert "queued" in msg.lower() and "capacity" in msg.lower()
    m = re.search(r"(\d+)s elapsed", msg)
    assert m is not None and int(m.group(1)) == int(elapsed)


def test_logs_generic_message_on_other_pending(caplog, clock):
    _patch_mod._request_active_since[("sess-1", "req-1")] = clock.now - (
        _POLL_LOG_DEDUP_SEC + 1.0
    )
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _call(_GENERIC_PENDING)
    [rec] = _records(caplog)
    msg = rec.getMessage()
    assert "sess-1" in msg and "req-1" in msg and "sample" in msg
    assert "[poller]" in msg
    assert "in progress" in msg.lower()


def test_silent_when_elapsed_below_threshold(caplog, clock):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _call(_RESUMING, elapsed=_POLL_LOG_DEDUP_SEC - 0.001)
        _call(_GENERIC_PENDING, elapsed=_POLL_LOG_DEDUP_SEC - 0.001)
    assert _records(caplog) == []


def test_dedups_within_window(caplog, clock):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _call(_RESUMING)
        clock.now += _POLL_LOG_DEDUP_SEC / 2
        _call(_RESUMING)
    assert len(_records(caplog)) == 1


def test_logs_again_after_window_expires(caplog, clock):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _call(_RESUMING)
        clock.now += _POLL_LOG_DEDUP_SEC + 0.001
        _call(_RESUMING)
    assert len(_records(caplog)) == 2


def test_dedup_keyed_by_op_type(caplog, clock):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _call(_RESUMING, op_type="sample")
        _call(_RESUMING, op_type="forward_backward")
    assert len(_records(caplog)) == 2


def test_dedup_keyed_by_session_id(caplog, clock):
    elapsed = _POLL_LOG_DEDUP_SEC + 1.0
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _maybe_log_poll_progress(
            _RESUMING, session_id="sess-A", request_id="req-A",
            op_type="sample", elapsed=elapsed,
        )
        _maybe_log_poll_progress(
            _RESUMING, session_id="sess-B", request_id="req-B",
            op_type="sample", elapsed=elapsed,
        )
    assert len(_records(caplog)) == 2


def test_wording_follows_current_phase(caplog, clock):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _call(_RESUMING)
        _call(_GENERIC_PENDING)
        clock.now += _POLL_LOG_DEDUP_SEC + 0.001
        _call(_GENERIC_PENDING)
    msgs = [r.getMessage().lower() for r in _records(caplog)]
    assert len(msgs) == 2
    assert "queued" in msgs[0] and "capacity" in msgs[0]
    assert "in progress" in msgs[1]


def test_in_progress_elapsed_is_since_active_not_since_submission(caplog, clock):
    long_submission_elapsed = 600.0
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _call(_RESUMING, elapsed=long_submission_elapsed)
        clock.now += 0.5
        _call(_GENERIC_PENDING, elapsed=long_submission_elapsed + 0.5)
        clock.now += 0.5
        _call(_GENERIC_PENDING, elapsed=long_submission_elapsed + 1.0)
        clock.now += _POLL_LOG_DEDUP_SEC + 1.0
        _call(_GENERIC_PENDING, elapsed=long_submission_elapsed + _POLL_LOG_DEDUP_SEC + 2.0)
    msgs = [r.getMessage() for r in _records(caplog)]
    assert len(msgs) == 2
    assert "queued" in msgs[0].lower()
    assert "in progress" in msgs[1].lower()
    m = re.search(r"(\d+)s elapsed", msgs[1])
    assert m is not None, msgs[1]
    active_elapsed = int(m.group(1))
    assert active_elapsed < 60, (
        f"in-progress elapsed should reflect active time, got {active_elapsed}s"
    )


def test_active_since_resets_when_request_re_queues(caplog, clock):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _call(_GENERIC_PENDING)
        clock.now += 10.0
        _call(_RESUMING, elapsed=10.0)
        clock.now += 5.0
        _call(_GENERIC_PENDING)
        clock.now += _POLL_LOG_DEDUP_SEC + 0.1
        _call(_GENERIC_PENDING)
    msgs = [r.getMessage() for r in _records(caplog)]
    assert any("in progress" in m.lower() for m in msgs)


def test_clear_poll_log_state_removes_entries(clock):
    _patch_mod._request_active_since[("sess-1", "req-1")] = clock.now
    _patch_mod._poll_log_last[("sess-1", "sample")] = clock.now
    _clear_poll_log_state("sess-1", "req-1", "sample")
    assert ("sess-1", "req-1") not in _patch_mod._request_active_since
    assert ("sess-1", "sample") not in _patch_mod._poll_log_last


def test_clear_poll_log_state_is_idempotent():
    _clear_poll_log_state("sess-unknown", "req-unknown", "sample")


# ---------------------------------------------------------------------------
# WARNING escalation + per-request dedup
#
# A request still pending past _POLL_WARN_SEC escalates from INFO to WARNING.
# The warn dedup is keyed per (session, op, request) -- NOT per (session, op) --
# so each genuinely-stuck request stays individually visible and a sibling
# request of the same op completing cannot reset another request's window.
# ---------------------------------------------------------------------------


def _warn_call(
    clock,
    *,
    session_id="sess-1",
    request_id="req-1",
    op_type="sample",
    pending_for=None,
):
    """Drive _maybe_log_poll_progress for an in-progress request that has been
    active for ``pending_for`` seconds (default: just over the warn threshold)."""
    if pending_for is None:
        pending_for = _patch_mod._POLL_WARN_SEC + 1.0
    # Seed active-since so display_elapsed >= the warn threshold this call.
    _patch_mod._request_active_since[(session_id, request_id)] = clock.now - pending_for
    _maybe_log_poll_progress(
        _GENERIC_PENDING,
        session_id=session_id,
        request_id=request_id,
        op_type=op_type,
        elapsed=pending_for,
    )


def _warns(caplog):
    return [r for r in _records(caplog) if r.levelno == logging.WARNING]


def test_escalates_to_warning_when_pending_past_threshold(caplog, clock):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _warn_call(clock)
    warns = _warns(caplog)
    assert len(warns) == 1
    msg = warns[0].getMessage()
    assert "sess-1" in msg and "req-1" in msg and "sample" in msg
    assert "still pending" in msg.lower()


def test_no_warning_below_threshold(caplog, clock):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _warn_call(clock, pending_for=_patch_mod._POLL_WARN_SEC - 1.0)
    assert _warns(caplog) == []


def test_warn_dedup_independent_per_request(caplog, clock):
    # Two distinct requests of the SAME op, both stuck past the threshold:
    # each must warn. Under the old (session, op) key the second would have
    # been suppressed.
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _warn_call(clock, request_id="req-A", op_type="sample")
        _warn_call(clock, request_id="req-B", op_type="sample")
    warns = _warns(caplog)
    assert len(warns) == 2
    warned_requests = {
        rid for rid in ("req-A", "req-B")
        if any(rid in w.getMessage() for w in warns)
    }
    assert warned_requests == {"req-A", "req-B"}


def test_warn_dedups_same_request_within_window(caplog, clock):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _warn_call(clock, request_id="req-1")
        clock.now += _patch_mod._POLL_WARN_DEDUP_SEC / 2
        _warn_call(clock, request_id="req-1")
    assert len(_warns(caplog)) == 1


def test_warn_refires_after_dedup_window(caplog, clock):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _warn_call(clock, request_id="req-1")
        clock.now += _patch_mod._POLL_WARN_DEDUP_SEC + 0.001
        _warn_call(clock, request_id="req-1")
    assert len(_warns(caplog)) == 2


def test_sibling_completion_does_not_reset_other_request_warn_window(caplog, clock):
    # req-A and req-B are both stuck on the same op; both warn once. A short
    # sibling (req-B) then completes and clears ITS state. req-A is still within
    # its dedup window, so it must NOT warn again -- the clear is request-scoped.
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        _warn_call(clock, request_id="req-A", op_type="sample")
        _warn_call(clock, request_id="req-B", op_type="sample")
        assert len(_warns(caplog)) == 2
        _clear_poll_log_state("sess-1", "req-B", "sample")
        clock.now += 1.0  # still well within _POLL_WARN_DEDUP_SEC
        _warn_call(clock, request_id="req-A", op_type="sample")
    assert len(_warns(caplog)) == 2


def test_clear_poll_log_state_removes_per_request_warn_entry(clock):
    _patch_mod._poll_warn_last[("sess-1", "sample", "req-1")] = clock.now
    _patch_mod._poll_warn_last[("sess-1", "sample", "req-2")] = clock.now
    _clear_poll_log_state("sess-1", "req-1", "sample")
    # Only req-1's warn state is dropped; req-2's survives.
    assert ("sess-1", "sample", "req-1") not in _patch_mod._poll_warn_last
    assert ("sess-1", "sample", "req-2") in _patch_mod._poll_warn_last


def test_warn_dedup_per_request_contract(caplog, clock):
    # End-to-end check of the full per-request warn contract in ONE timeline:
    # two same-session/same-op requests with different request_ids each warn,
    # a repeat for one of them inside the dedup window stays throttled, and
    # clearing one request drops ONLY that request's _poll_warn_last entry.
    # Splitting these into separate tests proves each property in isolation;
    # exercising them together guards against interaction bugs (e.g. one
    # request firing or clearing resetting another request's window).
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        # 1. Two distinct requests of the same op both escalate to WARNING.
        _warn_call(clock, request_id="req-A", op_type="sample")
        _warn_call(clock, request_id="req-B", op_type="sample")
        assert len(_warns(caplog)) == 2
        assert {
            rid for rid in ("req-A", "req-B")
            if any(rid in w.getMessage() for w in _warns(caplog))
        } == {"req-A", "req-B"}

        # 2. A repeat warning for req-A inside its dedup window is throttled,
        #    even though req-B warned in between (no shared-state reset).
        clock.now += _patch_mod._POLL_WARN_DEDUP_SEC / 2
        _warn_call(clock, request_id="req-A", op_type="sample")
        assert len(_warns(caplog)) == 2

    # 3. Clearing req-A removes only req-A's per-request warn entry; req-B's
    #    independent dedup window is untouched.
    assert ("sess-1", "sample", "req-A") in _patch_mod._poll_warn_last
    assert ("sess-1", "sample", "req-B") in _patch_mod._poll_warn_last
    _clear_poll_log_state("sess-1", "req-A", "sample")
    assert ("sess-1", "sample", "req-A") not in _patch_mod._poll_warn_last
    assert ("sess-1", "sample", "req-B") in _patch_mod._poll_warn_last
