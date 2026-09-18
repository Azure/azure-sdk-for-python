# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Tests for the error-budget polling semantics in ``_post_and_poll``.

The poll loop uses an *error budget* rather than a flat wall-clock deadline:

  * Healthy ``pending`` 200s (queued for capacity / in progress) clear the
    budget, so an operation can wait in the queue indefinitely.
  * A sustained streak of 5xx / 408 / 429 / transient network errors is bounded
    by ``_DEFAULT_OPERATION_TIMEOUT_SEC`` and raises ``TimeoutError``.
  * Any healthy 200 in between disarms the budget, so intermittent blips never
    trip it.
"""

from __future__ import annotations

import itertools
import logging

import pytest

from azure.core.exceptions import ServiceResponseError

from azure.ai.finetuningsessions import _patch as _patch_mod
from azure.ai.finetuningsessions._patch import FineTuningSession, _ErrorBudget

_SUBPATH = "/fine_tuning_sessions/session_deadbeef/optim_step"
_COMPLETED = {"status": "completed", "result": {}}
_PENDING = {"status": "pending"}


class _FakeResponse:
    def __init__(self, status_code: int, body: dict | None = None, retry_after: str | None = None):
        self.status_code = status_code
        self._body = body or {}
        self.headers = {} if retry_after is None else {"Retry-After": retry_after}

    def json(self) -> dict:
        return self._body

    def raise_for_status(self) -> None:  # pragma: no cover - not hit in these tests
        raise AssertionError(f"unexpected raise_for_status on {self.status_code}")


class _FakeClient:
    """Returns a fixed POST response, then yields scripted GET responses.

    A scripted GET entry may be a ``_FakeResponse`` (returned) or an
    ``Exception`` instance (raised, to simulate a transport error).
    """

    def __init__(self, get_responses):
        self._get = iter(get_responses)
        self.post_count = 0
        self.get_urls: list[str] = []

    def send_request(self, req):
        if req.method == "POST":
            self.post_count += 1
            return _FakeResponse(
                200,
                {"request_id": f"req-{self.post_count}", "session_id": "session_deadbeef"},
            )
        self.get_urls.append(req.url)
        item = next(self._get)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture
def clock(monkeypatch):
    """Deterministic monotonic clock; ``sleep`` advances it by its argument."""

    class _Clock:
        now: float = 1000.0

    c = _Clock()
    monkeypatch.setattr(_patch_mod._time, "monotonic", lambda: c.now)
    monkeypatch.setattr(_patch_mod._time, "sleep", lambda dt: setattr(c, "now", c.now + dt))
    return c


@pytest.fixture(autouse=True)
def _reset_poll_state():
    _patch_mod._poll_log_last.clear()
    _patch_mod._request_active_since.clear()
    yield
    _patch_mod._poll_log_last.clear()
    _patch_mod._request_active_since.clear()


@pytest.fixture
def small_budget(monkeypatch):
    monkeypatch.setattr(_patch_mod, "_DEFAULT_OPERATION_TIMEOUT_SEC", 5.0)
    return 5.0


def _make_session(get_responses) -> FineTuningSession:
    # Bypass __init__ so we don't start the background heartbeat thread.
    sess = FineTuningSession.__new__(FineTuningSession)
    sess._client = _FakeClient(get_responses)
    sess.session_id = "session_deadbeef"
    return sess


def test_long_queue_wait_then_complete_does_not_time_out(clock, small_budget):
    # 20 healthy pending polls (clock advances well past the 5s budget via
    # backoff sleeps) followed by completion — must NOT raise.
    responses = [_FakeResponse(200, _PENDING) for _ in range(20)] + [_FakeResponse(200, _COMPLETED)]
    sess = _make_session(responses)

    result = sess._post_and_poll(_SUBPATH, {})

    assert result is not None
    # Sanity: we really did spend more wall-clock than the budget while healthy.
    assert clock.now >= 1000.0 + small_budget


def test_sustained_5xx_raises_timeout(clock, small_budget):
    sess = _make_session(itertools.repeat(_FakeResponse(503)))

    with pytest.raises(TimeoutError):
        sess._post_and_poll(_SUBPATH, {})

    # The streak must have lasted at least the budget before failing.
    assert clock.now >= 1000.0 + small_budget


def test_sustained_network_error_raises_timeout(clock, small_budget):
    sess = _make_session(itertools.repeat(ServiceResponseError("boom")))

    with pytest.raises(TimeoutError):
        sess._post_and_poll(_SUBPATH, {})


def test_healthy_poll_resets_error_budget(clock, small_budget):
    # 503s that never run long enough *consecutively* to exceed the budget
    # because a healthy pending poll disarms it in between -> must complete.
    responses = [
        _FakeResponse(503),
        _FakeResponse(503),
        _FakeResponse(503),
        _FakeResponse(200, _PENDING),  # disarms the budget
        _FakeResponse(503),
        _FakeResponse(503),
        _FakeResponse(503),
        _FakeResponse(200, _COMPLETED),
    ]
    sess = _make_session(responses)

    result = sess._post_and_poll(_SUBPATH, {})

    assert result is not None


def test_fresh_request_not_found_retries_then_completes(clock, caplog):
    sess = _make_session(
        [
            _FakeResponse(404, {"detail": "Request not found"}),
            _FakeResponse(200, _COMPLETED),
        ]
    )

    with caplog.at_level(logging.WARNING, logger=_patch_mod.__name__):
        result = sess._post_and_poll(_SUBPATH, {})

    assert result is not None
    assert len(sess._client.get_urls) == 2
    assert clock.now == 1001.0
    assert (
        "transient request-store 404 for session_deadbeef/req-1 " "(op=optim_step, 0.0s/120.0s grace); retrying in 1.0s"
    ) in caplog.text


def test_request_not_found_stops_retrying_after_grace(clock):
    sess = _make_session(itertools.repeat(_FakeResponse(404, {"detail": "Request not found"})))

    with pytest.raises(AssertionError, match="unexpected raise_for_status on 404"):
        sess._post_and_poll(_SUBPATH, {})

    assert len(sess._client.get_urls) == 16
    assert clock.now == 1120.0


def test_other_404_is_retried(clock):
    sess = _make_session(
        [
            _FakeResponse(404, {"detail": "Model not found"}),
            _FakeResponse(200, _COMPLETED),
        ]
    )

    result = sess._post_and_poll(_SUBPATH, {})

    assert result is not None
    assert len(sess._client.get_urls) == 2
    assert clock.now == 1001.0


@pytest.mark.parametrize(
    "body",
    [
        {"detail": "request not found"},
        {"detail": " Request not found "},
        {"detail": "Request not found", "code": "missing"},
    ],
)
def test_404_body_variants_are_retried(clock, body):
    sess = _make_session([_FakeResponse(404, body), _FakeResponse(200, _COMPLETED)])

    result = sess._post_and_poll(_SUBPATH, {})

    assert result is not None
    assert len(sess._client.get_urls) == 2
    assert clock.now == 1001.0


def test_request_not_found_does_not_clear_armed_error_budget(clock, small_budget):
    responses = [
        _FakeResponse(503),
        _FakeResponse(404, {"detail": "Request not found"}),
        *[_FakeResponse(503) for _ in range(10)],
    ]
    sess = _make_session(responses)

    with pytest.raises(TimeoutError):
        sess._post_and_poll(_SUBPATH, {})

    assert clock.now >= 1000.0 + small_budget


def test_request_not_found_retry_delay_is_exponential_then_capped(clock):
    retry_state = _patch_mod._BoundedRetryState(
        limit_sec=120.0,
        base_delay_sec=1.0,
        max_delay_sec=10.0,
    )
    assert [retry_state.next_delay() for _ in range(7)] == [1.0, 2.0, 4.0, 8.0, 10.0, 10.0, 10.0]


def test_disabled_budget_retries_through_errors(clock, monkeypatch):
    # With the budget disabled (env var <= 0 -> None) a finite error streak
    # followed by completion must still succeed (no TimeoutError).
    monkeypatch.setattr(_patch_mod, "_DEFAULT_OPERATION_TIMEOUT_SEC", None)
    responses = [_FakeResponse(503) for _ in range(50)] + [_FakeResponse(200, _COMPLETED)]
    sess = _make_session(responses)

    result = sess._post_and_poll(_SUBPATH, {})

    assert result is not None


# ---------------------------------------------------------------------------
# Retryable resubmit: a failed sampling envelope with should_retry -> new POST
# ---------------------------------------------------------------------------

_FAILED_RETRYABLE = {
    "status": "failed",
    "should_retry": True,
    "retry_after_sec": 5,
}


def test_retryable_failure_resubmits_then_completes(clock):
    # First attempt fails retryably; the wrapper resubmits (new POST) and the
    # second attempt completes -> a single successful result, no exception.
    responses = [
        _FakeResponse(200, _FAILED_RETRYABLE),
        _FakeResponse(200, _COMPLETED),
    ]
    sess = _make_session(responses)

    result = sess._post_and_poll(_SUBPATH, {})

    assert result is not None
    assert sess._client.post_count == 2
    assert "req-1" in sess._client.get_urls[0]
    assert "req-2" in sess._client.get_urls[1]
    # Retry-After is a minimum; positive jitter spreads simultaneous retries.
    assert 1005.0 <= clock.now <= 1006.25


def test_happy_path_operation_timeline_has_stable_fields(clock, caplog):
    sess = _make_session([_FakeResponse(200, _COMPLETED)])

    with caplog.at_level(logging.INFO, logger=_patch_mod.__name__):
        result = sess._post_and_poll(_SUBPATH, {})

    assert result is not None
    assert (
        "submit_started session_id=session_deadbeef op=optim_step "
        "path=/fine_tuning_sessions/session_deadbeef/optim_step"
    ) in caplog.text
    assert (
        "submit_completed session_id=session_deadbeef request_id=req-1 " "op=optim_step elapsed_ms=0.0"
    ) in caplog.text
    assert (
        "result_consumed session_id=session_deadbeef request_id=req-1 op=optim_step "
        "poll_attempts=1 elapsed_ms=0.0 poll_elapsed_ms=0.0"
    ) in caplog.text


def test_retryable_resubmit_preserves_operation_timeline(clock, caplog, monkeypatch):
    responses = [
        _FakeResponse(200, _FAILED_RETRYABLE),
        _FakeResponse(200, _COMPLETED),
    ]
    sess = _make_session(responses)
    monkeypatch.setattr(_patch_mod, "_retryable_resubmit_wait", lambda _: 2.0)

    with caplog.at_level(logging.INFO, logger=_patch_mod.__name__):
        result = sess._post_and_poll(_SUBPATH, {})

    assert result is not None
    assert "submit_started session_id=session_deadbeef op=optim_step" in caplog.text
    assert (
        "submit_completed session_id=session_deadbeef request_id=req-2 " "op=optim_step elapsed_ms=0.0"
    ) in caplog.text
    assert (
        "result_consumed session_id=session_deadbeef request_id=req-2 op=optim_step "
        "poll_attempts=1 elapsed_ms=2000.0 poll_elapsed_ms=2000.0"
    ) in caplog.text


def test_retryable_failure_exhausts_and_raises(clock):
    from azure.ai.finetuningsessions import RequestRetryableError

    sess = _make_session(itertools.repeat(_FakeResponse(200, _FAILED_RETRYABLE)))

    with pytest.raises(RequestRetryableError):
        sess._post_and_poll(_SUBPATH, {})
    assert sess._client.post_count == 3


def test_non_retryable_failure_is_not_resubmitted(clock):
    # A failed envelope WITHOUT should_retry must surface immediately (the
    # generic RuntimeError path), never resubmit.
    responses = [_FakeResponse(200, {"status": "failed", "error": "boom"})]
    sess = _make_session(responses)

    with pytest.raises(RuntimeError):
        sess._post_and_poll(_SUBPATH, {})
    assert sess._client.post_count == 1


def test_completed_result_unavailable_is_not_resubmitted(clock):
    from azure.ai.finetuningsessions import OperationResultUnavailableError

    responses = [
        _FakeResponse(
            200,
            {
                "status": "failed",
                "error": "Operation completed, but its result is unavailable.",
                "error_code": "operation_completed_result_unavailable",
                # Defensive coverage: the error code remains non-retryable even
                # if a server response accidentally includes this flag.
                "should_retry": True,
            },
        )
    ]
    sess = _make_session(responses)

    with pytest.raises(OperationResultUnavailableError) as exc_info:
        sess._post_and_poll(_SUBPATH, {})

    assert exc_info.value.operation_completed is True
    assert sess._client.post_count == 1


def test_classify_poll_failure_flags_should_retry():
    # Retry is driven purely by should_retry; retry_after_sec is passed through.
    from azure.ai.finetuningsessions._exceptions import (
        _classify_poll_failure,
        RequestRetryableError,
    )

    typed = _classify_poll_failure(
        {"status": "failed", "should_retry": True, "retry_after_sec": 45, "error": "timed out"}
    )
    assert isinstance(typed, RequestRetryableError)
    assert typed.retry_after_sec == 45.0


def test_classify_no_retry_without_flag():
    # Decoupled from any code allow-list: even a code that historically implied
    # retry does NOT trigger a retry unless the server sets should_retry.
    from azure.ai.finetuningsessions._exceptions import (
        _classify_poll_failure,
        RequestRetryableError,
    )

    typed = _classify_poll_failure({"status": "failed", "code": "request_orphaned", "error": "gone"})
    assert not isinstance(typed, RequestRetryableError)


class TestErrorBudget:
    """Direct unit tests for the shared ``_ErrorBudget`` helper.

    These exercise the arm/clear/exhaust state machine in isolation so the
    behavior is locked in independent of the two poll loops that consume it.
    """

    @staticmethod
    def _budget(budget_sec, exc=TimeoutError):
        return _ErrorBudget(
            budget_sec,
            on_exhausted=lambda reason, b: exc(f"{reason}:{b}"),
        )

    def test_first_error_does_not_raise(self, clock):
        b = self._budget(5.0)
        b.consume("HTTP 503")  # arms only; no raise on the first error

    def test_sustained_streak_past_deadline_raises(self, clock):
        b = self._budget(5.0)
        b.consume("HTTP 503")  # arm at t=1000 -> deadline 1005
        clock.now += 6.0  # advance past the deadline
        with pytest.raises(TimeoutError, match="HTTP 503:5.0"):
            b.consume("HTTP 503")

    def test_clear_resets_the_streak(self, clock):
        b = self._budget(5.0)
        b.consume("err")  # arm at 1000 -> deadline 1005
        clock.now += 6.0  # would be past the deadline...
        b.clear()  # ...but a healthy poll disarms it
        b.consume("err")  # re-arms fresh; must not raise
        clock.now += 1.0
        b.consume("err")  # still within the new budget

    def test_none_budget_is_disabled(self, clock):
        b = self._budget(None)
        b.consume("err")
        clock.now += 10_000.0
        b.consume("err")  # never raises when disabled

    def test_exception_factory_controls_type(self, clock):
        b = self._budget(5.0, exc=RuntimeError)
        b.consume("boom")
        clock.now += 6.0
        with pytest.raises(RuntimeError, match="boom:5.0"):
            b.consume("boom")
